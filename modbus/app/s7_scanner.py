"""
S7 Protocol Scanner for Siemens LOGO! v7/0BA7 Detection
Based on S7comm protocol specification from Wireshark Wiki

Protocol Details:
- Port: 102 (TCP)
- Layer 4: ISO-on-TCP (RFC 1006 - TPKT)
- Layer 7: S7 Communication (COTP + S7comm)
- First byte of S7comm payload: 0x32 (protocol identifier)

Connection Establishment (3 steps):
1. TCP Connect to port 102
2. ISO/COTP Connect Request
3. S7comm Setup Communication (func=0xf0)

TSAP Structure (2 bytes):
- Byte 1: Communication Type (1=PG/Programming, 2=OP/Operator)
- Byte 2: Rack (bits 5-7) + Slot (bits 0-4)
"""

import socket
import struct
import logging
from typing import Optional, Dict, Tuple

logger = logging.getLogger(__name__)


class S7Scanner:
    """Scanner for S7 protocol devices (LOGO! v7, S7-300, S7-400, etc.)"""

    # TPKT Header (RFC 1006)
    TPKT_VERSION = 0x03
    TPKT_RESERVED = 0x00

    # COTP (ISO 8073) PDU Types
    COTP_CONNECT_REQUEST = 0xE0
    COTP_CONNECT_CONFIRM = 0xD0
    COTP_DATA = 0xF0

    # S7comm Protocol ID
    S7COMM_PROTOCOL_ID = 0x32

    # Default TSAPs for LOGO!
    # Local TSAP: 0x0100 (PG communication, Rack 0, Slot 0)
    # Remote TSAP: 0x2000 (OP communication, Rack 0, Slot 0)
    DEFAULT_LOCAL_TSAP = 0x0100
    DEFAULT_REMOTE_TSAP = 0x2000

    def __init__(self, host: str, port: int = 102, timeout: int = 5):
        """
        Initialize S7 Scanner

        Args:
            host: IP address of target device
            port: TCP port (default 102 for S7)
            timeout: Connection timeout in seconds
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock = None

    def _create_tpkt_header(self, length: int) -> bytes:
        """
        Create TPKT header (RFC 1006)

        Format:
        - Version: 1 byte (0x03)
        - Reserved: 1 byte (0x00)
        - Length: 2 bytes (big-endian, includes TPKT header)

        Args:
            length: Total packet length including TPKT header

        Returns:
            bytes: TPKT header (4 bytes)
        """
        return struct.pack('!BBH', self.TPKT_VERSION, self.TPKT_RESERVED, length)

    def _create_cotp_connect_request(self, src_tsap: int, dst_tsap: int) -> bytes:
        """
        Create COTP Connection Request (ISO 8073)

        Format:
        - Length Indicator: 1 byte (length of COTP header without this byte)
        - PDU Type: 1 byte (0xE0 = CR - Connect Request)
        - Destination Reference: 2 bytes (0x0000)
        - Source Reference: 2 bytes (0x0001)
        - Class/Option: 1 byte (0x00)
        - Parameter Code: 1 byte (0xC1 = src-tsap)
        - Parameter Length: 1 byte
        - Parameter Value: n bytes (src-tsap)
        - Parameter Code: 1 byte (0xC2 = dst-tsap)
        - Parameter Length: 1 byte
        - Parameter Value: n bytes (dst-tsap)
        - Parameter Code: 1 byte (0xC0 = tpdu-size)
        - Parameter Length: 1 byte (0x01)
        - Parameter Value: 1 byte (0x0A = 1024 bytes)

        Args:
            src_tsap: Source TSAP (2 bytes, e.g., 0x0100)
            dst_tsap: Destination TSAP (2 bytes, e.g., 0x2000)

        Returns:
            bytes: COTP Connection Request
        """
        # Convert TSAPs to bytes
        src_tsap_bytes = struct.pack('!H', src_tsap)
        dst_tsap_bytes = struct.pack('!H', dst_tsap)

        # Build COTP CR packet
        cotp_cr = bytearray()

        # PDU Type
        cotp_cr.append(self.COTP_CONNECT_REQUEST)

        # Destination Reference (0x0000)
        cotp_cr.extend(b'\x00\x00')

        # Source Reference (0x0001)
        cotp_cr.extend(b'\x00\x01')

        # Class/Option (0x00)
        cotp_cr.append(0x00)

        # Parameter: src-tsap (0xC1)
        cotp_cr.append(0xC1)
        cotp_cr.append(len(src_tsap_bytes))
        cotp_cr.extend(src_tsap_bytes)

        # Parameter: dst-tsap (0xC2)
        cotp_cr.append(0xC2)
        cotp_cr.append(len(dst_tsap_bytes))
        cotp_cr.extend(dst_tsap_bytes)

        # Parameter: tpdu-size (0xC0) - 1024 bytes (0x0A)
        cotp_cr.extend(b'\xC0\x01\x0A')

        # Prepend length indicator (length without this byte)
        length_indicator = len(cotp_cr)
        cotp_packet = bytes([length_indicator]) + bytes(cotp_cr)

        return cotp_packet

    def _create_s7comm_setup(self, max_amq_calling: int = 1, max_amq_called: int = 1, pdu_length: int = 480) -> bytes:
        """
        Create S7comm Setup Communication request

        Format:
        - Protocol ID: 1 byte (0x32)
        - ROSCTR (Remote Operating Service Control): 1 byte (0x01 = Job)
        - Reserved: 2 bytes (0x0000)
        - PDU Reference: 2 bytes (0x0000)
        - Parameter Length: 2 bytes
        - Data Length: 2 bytes (0x0000)
        - Function: 1 byte (0xF0 = Setup communication)
        - Reserved: 1 byte (0x00)
        - Max AMQ (calling): 2 bytes
        - Max AMQ (called): 2 bytes
        - PDU Length: 2 bytes

        Args:
            max_amq_calling: Maximum parallel jobs calling (default 1)
            max_amq_called: Maximum parallel jobs called (default 1)
            pdu_length: Negotiated PDU length (default 480)

        Returns:
            bytes: S7comm Setup Communication request
        """
        # Build parameter
        parameter = bytearray()
        parameter.append(0xF0)  # Function: Setup communication
        parameter.append(0x00)  # Reserved
        parameter.extend(struct.pack('!H', max_amq_calling))
        parameter.extend(struct.pack('!H', max_amq_called))
        parameter.extend(struct.pack('!H', pdu_length))

        # Build S7comm header
        s7comm = bytearray()
        s7comm.append(self.S7COMM_PROTOCOL_ID)  # Protocol ID
        s7comm.append(0x01)  # ROSCTR: Job
        s7comm.extend(b'\x00\x00')  # Reserved
        s7comm.extend(b'\x00\x00')  # PDU Reference
        s7comm.extend(struct.pack('!H', len(parameter)))  # Parameter Length
        s7comm.extend(b'\x00\x00')  # Data Length
        s7comm.extend(parameter)

        return bytes(s7comm)

    def _send_receive(self, data: bytes) -> Optional[bytes]:
        """
        Send data and receive response

        Args:
            data: Data to send

        Returns:
            Optional[bytes]: Response data or None on error
        """
        try:
            self.sock.sendall(data)
            response = self.sock.recv(4096)
            return response
        except socket.timeout:
            logger.debug(f"Timeout receiving from {self.host}:{self.port}")
            return None
        except Exception as e:
            logger.debug(f"Error communicating with {self.host}:{self.port}: {e}")
            return None

    def detect_s7_device(self, src_tsap: Optional[int] = None, dst_tsap: Optional[int] = None) -> Dict:
        """
        Detect S7-compatible device using 3-step connection

        Args:
            src_tsap: Source TSAP (default: 0x0100)
            dst_tsap: Destination TSAP (default: 0x2000)

        Returns:
            dict: Detection results with keys:
                - success: bool
                - device_type: str (e.g., "LOGO! v7", "S7-300", "S7-400", "Unknown S7")
                - port: int
                - tsap_src: int
                - tsap_dst: int
                - pdu_size: int (negotiated PDU size)
                - error: str (if failed)
        """
        if src_tsap is None:
            src_tsap = self.DEFAULT_LOCAL_TSAP
        if dst_tsap is None:
            dst_tsap = self.DEFAULT_REMOTE_TSAP

        result = {
            'success': False,
            'device_type': None,
            'port': self.port,
            'tsap_src': src_tsap,
            'tsap_dst': dst_tsap,
            'pdu_size': None,
            'error': None
        }

        try:
            # Step 1: TCP Connect
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.timeout)
            self.sock.connect((self.host, self.port))
            logger.debug(f"TCP connected to {self.host}:{self.port}")

            # Step 2: COTP Connect Request
            cotp_cr = self._create_cotp_connect_request(src_tsap, dst_tsap)
            tpkt_length = 4 + len(cotp_cr)  # TPKT header + COTP CR
            tpkt_header = self._create_tpkt_header(tpkt_length)
            cotp_request = tpkt_header + cotp_cr

            cotp_response = self._send_receive(cotp_request)
            if not cotp_response or len(cotp_response) < 7:
                result['error'] = 'No COTP response or response too short'
                return result

            # Check COTP Connect Confirm (0xD0)
            cotp_pdu_type = cotp_response[5]  # After TPKT header (4 bytes) + length indicator (1 byte)
            if cotp_pdu_type != self.COTP_CONNECT_CONFIRM:
                result['error'] = f'COTP connection rejected (PDU type: 0x{cotp_pdu_type:02X})'
                return result

            logger.debug(f"COTP connection confirmed to {self.host}:{self.port}")

            # Step 3: S7comm Setup Communication
            s7_setup = self._create_s7comm_setup()

            # Wrap in COTP Data packet
            cotp_data = bytes([2, 0xF0, 0x80])  # Length=2, DT Data, EOT
            s7_packet = cotp_data + s7_setup

            tpkt_length = 4 + len(s7_packet)
            tpkt_header = self._create_tpkt_header(tpkt_length)
            s7_request = tpkt_header + s7_packet

            s7_response = self._send_receive(s7_request)
            if not s7_response or len(s7_response) < 20:
                result['error'] = 'No S7comm response or response too short'
                return result

            # Parse S7comm response
            # Skip TPKT (4 bytes) + COTP (3 bytes) = 7 bytes
            s7_data = s7_response[7:]

            # Check S7comm Protocol ID
            if s7_data[0] != self.S7COMM_PROTOCOL_ID:
                result['error'] = f'Invalid S7comm protocol ID: 0x{s7_data[0]:02X}'
                return result

            # Check ROSCTR (should be 0x03 = Ack_Data)
            rosctr = s7_data[1]
            if rosctr != 0x03:
                result['error'] = f'Unexpected ROSCTR: 0x{rosctr:02X}'
                return result

            # Extract PDU size from response (bytes 18-19 after TPKT+COTP)
            if len(s7_data) >= 20:
                pdu_size = struct.unpack('!H', s7_data[18:20])[0]
                result['pdu_size'] = pdu_size

            logger.info(f"S7comm connection established to {self.host}:{self.port} (PDU: {result['pdu_size']})")

            # Device type detection based on TSAP and response
            result['success'] = True
            result['device_type'] = self._identify_device_type(dst_tsap, s7_response)

            return result

        except socket.timeout:
            result['error'] = 'Connection timeout'
            return result
        except ConnectionRefusedError:
            result['error'] = 'Connection refused'
            return result
        except Exception as e:
            result['error'] = str(e)
            logger.debug(f"S7 detection error for {self.host}:{self.port}: {e}")
            return result
        finally:
            if self.sock:
                try:
                    self.sock.close()
                except Exception:
                    pass

    def _identify_device_type(self, tsap: int, response: bytes) -> str:
        """
        Identify device type based on TSAP and response characteristics

        Args:
            tsap: Destination TSAP used
            response: S7comm response

        Returns:
            str: Device type identifier
        """
        # LOGO! v7/0BA7 typically uses TSAP 0x2000
        # PDU size for LOGO! is typically 480 bytes
        if tsap == 0x2000:
            # Parse PDU size from response
            if len(response) >= 27:
                s7_data = response[7:]
                if len(s7_data) >= 20:
                    pdu_size = struct.unpack('!H', s7_data[18:20])[0]
                    if pdu_size == 480:
                        return "LOGO! v7 (0BA7)"
                    elif pdu_size <= 512:
                        return "LOGO! v7/v8 (uncertain)"

        # S7-300 series (rack/slot based TSAP)
        rack = (tsap >> 8) & 0x07
        slot = tsap & 0x1F
        if rack == 0 and slot > 0:
            return f"S7-300 (Rack {rack}, Slot {slot})"

        # S7-400 series
        if rack > 0:
            return f"S7-400 (Rack {rack}, Slot {slot})"

        return "Unknown S7 Device"

    @staticmethod
    def scan_network_for_s7(network: str, timeout: int = 2) -> list:
        """
        Scan network for S7 devices on port 102

        Args:
            network: Network range (e.g., "192.168.1.0/24")
            timeout: Timeout per host in seconds

        Returns:
            list: List of dicts with detected S7 devices
        """
        import ipaddress

        devices = []
        network_obj = ipaddress.IPv4Network(network, strict=False)

        logger.info(f"Scanning network {network} for S7 devices...")

        for ip in network_obj.hosts():
            ip_str = str(ip)
            logger.debug(f"Checking {ip_str}:102 for S7...")

            scanner = S7Scanner(ip_str, port=102, timeout=timeout)
            result = scanner.detect_s7_device()

            if result['success']:
                devices.append({
                    'host': ip_str,
                    'port': 102,
                    'device_type': result['device_type'],
                    'pdu_size': result['pdu_size'],
                    'tsap_src': result['tsap_src'],
                    'tsap_dst': result['tsap_dst']
                })
                logger.info(f"Found S7 device: {ip_str} - {result['device_type']}")

        logger.info(f"S7 scan complete. Found {len(devices)} device(s).")
        return devices

    @staticmethod
    def create_tsap(comm_type: int, rack: int, slot: int) -> int:
        """
        Create TSAP value from communication type, rack, and slot

        Args:
            comm_type: Communication type (1=PG, 2=OP, 3=S7 Basic Communication)
            rack: Rack number (0-7, 3 bits)
            slot: Slot number (0-31, 5 bits)

        Returns:
            int: TSAP value (2 bytes)

        Examples:
            >>> S7Scanner.create_tsap(1, 0, 0)
            256  # 0x0100 - PG, Rack 0, Slot 0
            >>> S7Scanner.create_tsap(2, 0, 0)
            512  # 0x0200 - OP, Rack 0, Slot 0
            >>> S7Scanner.create_tsap(1, 0, 2)
            258  # 0x0102 - PG, Rack 0, Slot 2
        """
        if not (1 <= comm_type <= 3):
            raise ValueError("comm_type must be 1 (PG), 2 (OP), or 3 (S7 Basic)")
        if not (0 <= rack <= 7):
            raise ValueError("rack must be 0-7")
        if not (0 <= slot <= 31):
            raise ValueError("slot must be 0-31")

        # First byte: communication type
        # Second byte: rack (bits 5-7) + slot (bits 0-4)
        byte1 = comm_type
        byte2 = (rack << 5) | slot

        return (byte1 << 8) | byte2

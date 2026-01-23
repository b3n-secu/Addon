"""
Multi-Protocol Scanner for Industrial Communication Protocols
Detects: Modbus TCP/UDP, S7comm, KNX, CANbus, CANopen, PROFINET, PROFIBUS

Based on standard ports and protocol signatures
"""

import socket
import struct
import logging
from typing import List, Dict, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class ProtocolType(Enum):
    """Supported industrial protocols"""
    MODBUS_TCP = "modbus_tcp"
    MODBUS_UDP = "modbus_udp"
    S7COMM = "s7comm"
    KNX_IP = "knx_ip"
    CANBUS = "canbus"
    CANOPEN = "canopen"
    PROFINET = "profinet"
    PROFIBUS = "profibus"
    BACNET = "bacnet"
    UNKNOWN = "unknown"


# Standard ports for industrial protocols
PROTOCOL_PORTS = {
    ProtocolType.MODBUS_TCP: [502],
    ProtocolType.S7COMM: [102],
    ProtocolType.KNX_IP: [3671],  # KNXnet/IP
    ProtocolType.PROFINET: [34962, 34963, 34964],  # PROFINET RT
    ProtocolType.BACNET: [47808],  # BAC/IP (UDP)
}


class ProtocolScanner:
    """Scanner for multiple industrial protocols"""

    def __init__(self, timeout: int = 2):
        self.timeout = timeout

    def scan_host(self, host: str, ports: Optional[List[int]] = None) -> List[Dict]:
        """
        Scan a single host for all supported protocols

        Args:
            host: IP address to scan
            ports: Optional list of ports to scan (defaults to all known ports)

        Returns:
            List of detected protocols with details
        """
        if ports is None:
            ports = self._get_all_ports()

        detected = []

        for port in ports:
            result = self._probe_port(host, port)
            if result:
                detected.append(result)

        return detected

    def scan_network(self, network: str, protocols: Optional[List[ProtocolType]] = None) -> List[Dict]:
        """
        Scan network for devices supporting specified protocols

        Args:
            network: Network range (e.g., "192.168.1.0/24")
            protocols: Optional list of protocols to scan for

        Returns:
            List of detected devices
        """
        import ipaddress

        if protocols is None:
            protocols = [
                ProtocolType.MODBUS_TCP,
                ProtocolType.S7COMM,
                ProtocolType.KNX_IP
            ]

        devices = []
        network_obj = ipaddress.IPv4Network(network, strict=False)

        ports = []
        for protocol in protocols:
            if protocol in PROTOCOL_PORTS:
                ports.extend(PROTOCOL_PORTS[protocol])

        ports = list(set(ports))  # Remove duplicates

        logger.info(f"Scanning {network} for protocols: {[p.value for p in protocols]}")
        logger.info(f"Ports to scan: {ports}")

        for ip in network_obj.hosts():
            ip_str = str(ip)
            for port in ports:
                result = self._probe_port(ip_str, port)
                if result:
                    devices.append(result)
                    logger.info(f"Found device: {ip_str}:{port} - {result['protocol']}")

        return devices

    def _probe_port(self, host: str, port: int) -> Optional[Dict]:
        """
        Probe a specific port and identify protocol

        Returns:
            Dict with protocol info or None if no response
        """
        # Try TCP first
        result = self._probe_tcp(host, port)
        if result:
            return result

        # Try UDP for UDP-based protocols
        if port in [502, 47808]:  # Modbus UDP, BACnet
            result = self._probe_udp(host, port)
            if result:
                return result

        return None

    def _probe_tcp(self, host: str, port: int) -> Optional[Dict]:
        """Probe TCP port"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((host, port))
            sock.close()

            if result == 0:
                # Port is open, identify protocol
                protocol = self._identify_tcp_protocol(host, port)
                return {
                    'host': host,
                    'port': port,
                    'protocol': protocol.value,
                    'transport': 'tcp'
                }

        except Exception as e:
            logger.debug(f"TCP probe error {host}:{port}: {e}")

        return None

    def _probe_udp(self, host: str, port: int) -> Optional[Dict]:
        """Probe UDP port"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.timeout)

            # Send protocol-specific probe
            if port == 502:
                # Modbus UDP probe
                probe = self._create_modbus_probe()
            elif port == 47808:
                # BACnet probe
                probe = self._create_bacnet_probe()
            else:
                return None

            sock.sendto(probe, (host, port))

            try:
                data, addr = sock.recvfrom(1024)
                sock.close()

                if data:
                    protocol = self._identify_udp_protocol(port, data)
                    return {
                        'host': host,
                        'port': port,
                        'protocol': protocol.value,
                        'transport': 'udp'
                    }
            except socket.timeout:
                pass

            sock.close()

        except Exception as e:
            logger.debug(f"UDP probe error {host}:{port}: {e}")

        return None

    def _identify_tcp_protocol(self, host: str, port: int) -> ProtocolType:
        """Identify protocol based on port and connection test"""

        # Modbus TCP (port 502)
        if port == 502:
            if self._test_modbus_tcp(host, port):
                return ProtocolType.MODBUS_TCP

        # S7comm (port 102)
        elif port == 102:
            if self._test_s7comm(host, port):
                return ProtocolType.S7COMM

        # KNX/IP (port 3671)
        elif port == 3671:
            if self._test_knx_ip(host, port):
                return ProtocolType.KNX_IP

        # PROFINET (ports 34962-34964)
        elif port in [34962, 34963, 34964]:
            return ProtocolType.PROFINET

        return ProtocolType.UNKNOWN

    def _identify_udp_protocol(self, port: int, data: bytes) -> ProtocolType:
        """Identify protocol based on UDP response"""

        if port == 502:
            # Check for Modbus response
            if len(data) >= 7 and data[2:4] == b'\x00\x00':  # Modbus MBAP header
                return ProtocolType.MODBUS_UDP

        elif port == 47808:
            # Check for BACnet response
            if len(data) >= 4 and data[0] == 0x81:  # BACnet BVLC type
                return ProtocolType.BACNET

        return ProtocolType.UNKNOWN

    def _test_modbus_tcp(self, host: str, port: int) -> bool:
        """Test if port responds to Modbus TCP"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((host, port))

            # Send Modbus Read Coils request (Function 01)
            # MBAP Header + PDU
            request = struct.pack(
                '>HHHBB',
                0x0001,  # Transaction ID
                0x0000,  # Protocol ID (Modbus)
                0x0006,  # Length
                0x01,    # Unit ID
                0x01     # Function Code: Read Coils
            )
            request += struct.pack('>HH', 0x0000, 0x0001)  # Start address, count

            sock.sendall(request)
            response = sock.recv(1024)
            sock.close()

            # Check for Modbus response (protocol ID should be 0x0000)
            if len(response) >= 7:
                protocol_id = struct.unpack('>H', response[2:4])[0]
                return protocol_id == 0x0000

        except Exception as e:
            logger.debug(f"Modbus TCP test error: {e}")

        return False

    def _test_s7comm(self, host: str, port: int) -> bool:
        """Test if port responds to S7comm"""
        try:
            # Use simplified S7 detection
            from s7_scanner import S7Scanner
            scanner = S7Scanner(host, port=port, timeout=self.timeout)
            result = scanner.detect_s7_device()
            return result.get('success', False)
        except Exception as e:
            logger.debug(f"S7comm test error: {e}")
            return False

    def _test_knx_ip(self, host: str, port: int) -> bool:
        """Test if port responds to KNX/IP"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((host, port))

            # Send KNX SEARCH_REQUEST (simplified)
            # KNX/IP header: header length, protocol version, service type, total length
            request = struct.pack(
                '>BBHH',
                0x06,    # Header length
                0x10,    # Protocol version 1.0
                0x0201,  # SEARCH_REQUEST
                0x000E   # Total length
            )
            # HPAI (Host Protocol Address Information)
            request += struct.pack('>BB', 0x08, 0x01)  # Structure length, protocol code
            request += socket.inet_aton(host)
            request += struct.pack('>H', 0)  # Port

            sock.sendall(request)
            response = sock.recv(1024)
            sock.close()

            # Check for KNX response
            if len(response) >= 6:
                return response[1] == 0x10  # Protocol version

        except Exception as e:
            logger.debug(f"KNX/IP test error: {e}")

        return False

    def _create_modbus_probe(self) -> bytes:
        """Create Modbus UDP probe packet"""
        # Simple Modbus read coils request
        return struct.pack(
            '>HHHBBHH',
            0x0001,  # Transaction ID
            0x0000,  # Protocol ID
            0x0006,  # Length
            0x01,    # Unit ID
            0x01,    # Function Code
            0x0000,  # Start address
            0x0001   # Quantity
        )

    def _create_bacnet_probe(self) -> bytes:
        """Create BACnet probe packet"""
        # BACnet Who-Is request (simplified)
        return bytes([
            0x81,  # BVLC Type: BACnet/IP
            0x0A,  # Function: Original-Unicast-NPDU
            0x00, 0x11,  # Length
            0x01,  # Version
            0x20,  # Control flags
            0xFF, 0xFF,  # DNET
            0x00,  # DLEN
            0x08,  # Who-Is
            0x00, 0x00,  # Range (all)
        ])

    def _get_all_ports(self) -> List[int]:
        """Get all known protocol ports"""
        all_ports = []
        for ports in PROTOCOL_PORTS.values():
            all_ports.extend(ports)
        return list(set(all_ports))

    @staticmethod
    def get_protocol_info(protocol: ProtocolType) -> Dict:
        """Get information about a protocol"""
        info = {
            ProtocolType.MODBUS_TCP: {
                'name': 'Modbus TCP',
                'description': 'Modbus protocol over TCP/IP',
                'default_port': 502,
                'requires_gateway': False,
                'supported': True
            },
            ProtocolType.MODBUS_UDP: {
                'name': 'Modbus UDP',
                'description': 'Modbus protocol over UDP/IP',
                'default_port': 502,
                'requires_gateway': False,
                'supported': True
            },
            ProtocolType.S7COMM: {
                'name': 'S7 Communication',
                'description': 'Siemens S7 protocol for PLCs',
                'default_port': 102,
                'requires_gateway': False,
                'supported': True
            },
            ProtocolType.KNX_IP: {
                'name': 'KNX/IP',
                'description': 'KNX Building Automation over IP',
                'default_port': 3671,
                'requires_gateway': True,
                'gateway_type': 'KNX/IP Gateway',
                'supported': True
            },
            ProtocolType.PROFINET: {
                'name': 'PROFINET',
                'description': 'PROFINET Industrial Ethernet',
                'default_port': 34962,
                'requires_gateway': True,
                'gateway_type': 'PROFINET Gateway',
                'supported': False
            },
            ProtocolType.PROFIBUS: {
                'name': 'PROFIBUS',
                'description': 'PROFIBUS DP/PA fieldbus',
                'default_port': None,
                'requires_gateway': True,
                'gateway_type': 'PROFIBUS Gateway',
                'supported': False
            },
            ProtocolType.CANBUS: {
                'name': 'CANbus',
                'description': 'Controller Area Network bus',
                'default_port': None,
                'requires_gateway': True,
                'gateway_type': 'CAN Gateway',
                'supported': False
            },
            ProtocolType.CANOPEN: {
                'name': 'CANopen',
                'description': 'CANopen application layer protocol',
                'default_port': None,
                'requires_gateway': True,
                'gateway_type': 'CANopen Gateway',
                'supported': False
            },
            ProtocolType.BACNET: {
                'name': 'BACnet',
                'description': 'Building Automation and Control Networks',
                'default_port': 47808,
                'requires_gateway': False,
                'supported': True
            },
        }

        return info.get(protocol, {
            'name': 'Unknown',
            'description': 'Unknown protocol',
            'default_port': None,
            'requires_gateway': False,
            'supported': False
        })

"""
Modbus Scanner for automatic device discovery
"""
import logging
import socket
import ipaddress
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

logger = logging.getLogger(__name__)


class ModbusScanner:
    """Scanner for Modbus devices"""

    def __init__(self, host, port=502, timeout=3):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.client = None

    def connect(self):
        """Connect to Modbus device"""
        try:
            self.client = ModbusTcpClient(
                host=self.host,
                port=self.port,
                timeout=self.timeout
            )
            connected = self.client.connect()
            if connected:
                logger.info(f"Connected to {self.host}:{self.port}")
                return True
            else:
                logger.error(f"Failed to connect to {self.host}:{self.port}")
                return False
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False

    def disconnect(self):
        """Disconnect from Modbus device"""
        if self.client:
            try:
                self.client.close()
                logger.info(f"Disconnected from {self.host}:{self.port}")
            except:
                pass

    def scan_coils(self, start_address=0, count=100, slave=1):
        """Scan coils (digital outputs)"""
        available = []
        try:
            result = self.client.read_coils(start_address, count, unit=slave)
            if not result.isError() and hasattr(result, 'bits'):
                for i, bit in enumerate(result.bits[:count]):
                    available.append({
                        'address': start_address + i,
                        'value': bit,
                        'type': 'coil'
                    })
                logger.info(f"Found {len(available)} coils starting at {start_address}")
        except Exception as e:
            logger.debug(f"Error scanning coils: {e}")
        return available

    def scan_discrete_inputs(self, start_address=0, count=100, slave=1):
        """Scan discrete inputs (digital inputs)"""
        available = []
        try:
            result = self.client.read_discrete_inputs(start_address, count, unit=slave)
            if not result.isError() and hasattr(result, 'bits'):
                for i, bit in enumerate(result.bits[:count]):
                    available.append({
                        'address': start_address + i,
                        'value': bit,
                        'type': 'discrete_input'
                    })
                logger.info(f"Found {len(available)} discrete inputs starting at {start_address}")
        except Exception as e:
            logger.debug(f"Error scanning discrete inputs: {e}")
        return available

    def scan_holding_registers(self, start_address=0, count=100, slave=1):
        """Scan holding registers"""
        available = []
        try:
            result = self.client.read_holding_registers(start_address, count, unit=slave)
            if not result.isError() and hasattr(result, 'registers'):
                for i, value in enumerate(result.registers):
                    available.append({
                        'address': start_address + i,
                        'value': value,
                        'type': 'holding_register'
                    })
                logger.info(f"Found {len(available)} holding registers starting at {start_address}")
        except Exception as e:
            logger.debug(f"Error scanning holding registers: {e}")
        return available

    def scan_input_registers(self, start_address=0, count=100, slave=1):
        """Scan input registers"""
        available = []
        try:
            result = self.client.read_input_registers(start_address, count, unit=slave)
            if not result.isError() and hasattr(result, 'registers'):
                for i, value in enumerate(result.registers):
                    available.append({
                        'address': start_address + i,
                        'value': value,
                        'type': 'input_register'
                    })
                logger.info(f"Found {len(available)} input registers starting at {start_address}")
        except Exception as e:
            logger.debug(f"Error scanning input registers: {e}")
        return available

    def scan_device(self, profile=None, slave=1):
        """Scan device based on profile or generic scan"""
        results = {
            'coils': [],
            'discrete_inputs': [],
            'holding_registers': [],
            'input_registers': []
        }

        if not self.connect():
            return results

        try:
            if profile and 'registers' in profile:
                # Scan based on profile
                registers = profile['registers']

                if 'digital_outputs' in registers:
                    reg = registers['digital_outputs']
                    results['coils'] = self.scan_coils(
                        reg.get('start_address', 0),
                        reg.get('count', 20),
                        slave
                    )

                if 'digital_inputs' in registers:
                    reg = registers['digital_inputs']
                    results['discrete_inputs'] = self.scan_discrete_inputs(
                        reg.get('start_address', 0),
                        reg.get('count', 24),
                        slave
                    )

                if 'analog_outputs' in registers or 'holding_registers' in registers:
                    reg_key = 'analog_outputs' if 'analog_outputs' in registers else 'holding_registers'
                    reg = registers[reg_key]
                    results['holding_registers'] = self.scan_holding_registers(
                        reg.get('start_address', 0),
                        reg.get('count', 10),
                        slave
                    )

                if 'analog_inputs' in registers or 'input_registers' in registers:
                    reg_key = 'analog_inputs' if 'analog_inputs' in registers else 'input_registers'
                    reg = registers[reg_key]
                    results['input_registers'] = self.scan_input_registers(
                        reg.get('start_address', 0),
                        reg.get('count', 10),
                        slave
                    )
            else:
                # Generic scan - try common ranges
                results['coils'] = self.scan_coils(0, 100, slave)
                results['discrete_inputs'] = self.scan_discrete_inputs(0, 100, slave)
                results['holding_registers'] = self.scan_holding_registers(0, 100, slave)
                results['input_registers'] = self.scan_input_registers(0, 100, slave)

                # Try Siemens LOGO! specific addresses if nothing found
                if not any(results.values()):
                    logger.info("Trying Siemens LOGO! specific addresses...")
                    results['discrete_inputs'] = self.scan_discrete_inputs(1, 24, slave)
                    results['input_registers'] = self.scan_input_registers(1, 8, slave)
                    results['coils'] = self.scan_coils(8193, 20, slave)  # 0x2001

        finally:
            self.disconnect()

        return results

    def test_connection(self):
        """Test connection to device"""
        if self.connect():
            self.disconnect()
            return True
        return False


class NetworkScanner:
    """Network scanner for Modbus TCP devices"""

    @staticmethod
    def get_local_network():
        """Get local network CIDR"""
        try:
            # Get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()

            # Assume /24 network
            network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
            return str(network)
        except:
            return "192.168.1.0/24"

    @staticmethod
    def scan_network(network=None, ports=[502, 510], timeout=1):
        """Scan network for Modbus devices"""
        if network is None:
            network = NetworkScanner.get_local_network()

        logger.info(f"Scanning network {network} for Modbus devices...")
        devices = []

        try:
            net = ipaddress.IPv4Network(network, strict=False)

            for ip in net.hosts():
                ip_str = str(ip)

                for port in ports:
                    try:
                        # Quick TCP port check
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(timeout)
                        result = sock.connect_ex((ip_str, port))
                        sock.close()

                        if result == 0:
                            # Port is open, try Modbus connection
                            scanner = ModbusScanner(ip_str, port, timeout=2)
                            if scanner.test_connection():
                                devices.append({
                                    'ip': ip_str,
                                    'port': port,
                                    'status': 'online'
                                })
                                logger.info(f"Found Modbus device at {ip_str}:{port}")
                    except:
                        pass

        except Exception as e:
            logger.error(f"Network scan error: {e}")

        logger.info(f"Network scan complete. Found {len(devices)} devices.")
        return devices

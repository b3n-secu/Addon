"""
Nmap-based Modbus Scanner for efficient device discovery
Uses nmap's modbus-discover NSE script for professional scanning
"""
import logging
import nmap
import ipaddress
import socket
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class NmapModbusScanner:
    """
    Efficient Modbus scanner using nmap with modbus-discover script
    Based on DefCon 16 research on Modbus security
    """

    def __init__(self):
        self.nm = nmap.PortScanner()

    @staticmethod
    def get_local_network(cidr=24):
        """
        Automatically detect local network with specified CIDR

        Args:
            cidr: Network mask (default: 24 for /24)

        Returns:
            Network in CIDR notation (e.g., '192.168.1.0/24')
        """
        try:
            # Get hostname and resolve to IP
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)

            # If localhost, try alternative method
            if local_ip.startswith('127.'):
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()

            # Create network from IP with specified CIDR
            interface = ipaddress.IPv4Interface(f"{local_ip}/{cidr}")
            network = interface.network

            logger.info(f"Auto-detected network: {network}")
            return str(network)
        except Exception as e:
            logger.error(f"Failed to auto-detect network: {e}")
            return "192.168.1.0/24"  # Fallback

    def scan_network_nmap(
        self,
        network: Optional[str] = None,
        port_range: str = "502,510,20000-20100",
        timeout: int = 300,
        use_modbus_discover: bool = True
    ) -> List[Dict]:
        """
        Scan network using nmap for Modbus devices

        Args:
            network: Network in CIDR notation (e.g., '192.168.1.0/24')
            port_range: Port range to scan (e.g., '502,510,20000-20100')
            timeout: Scan timeout in seconds
            use_modbus_discover: Use nmap's modbus-discover NSE script

        Returns:
            List of discovered devices with details
        """
        if network is None:
            network = self.get_local_network()

        logger.info(f"Starting nmap scan on {network}, ports: {port_range}")

        devices = []

        try:
            # Build nmap arguments
            nmap_args = f"-p {port_range} --open"

            if use_modbus_discover:
                # Use modbus-discover NSE script for advanced detection
                nmap_args += " --script modbus-discover"

            # Add timing and performance options
            nmap_args += " -T4 --max-retries 2"

            logger.info(f"Nmap command: nmap {nmap_args} {network}")

            # Execute nmap scan
            self.nm.scan(hosts=network, arguments=nmap_args, timeout=timeout)

            # Parse results
            for host in self.nm.all_hosts():
                if self.nm[host].state() == 'up':
                    logger.info(f"Found host: {host}")

                    # Check each port
                    for proto in self.nm[host].all_protocols():
                        ports = self.nm[host][proto].keys()

                        for port in ports:
                            port_info = self.nm[host][proto][port]

                            # Only process open ports
                            if port_info['state'] == 'open':
                                device = {
                                    'ip': host,
                                    'port': port,
                                    'status': 'online',
                                    'protocol': proto,
                                    'service': port_info.get('name', 'unknown'),
                                    'product': port_info.get('product', ''),
                                    'version': port_info.get('version', ''),
                                    'scan_method': 'nmap'
                                }

                                # Parse modbus-discover script output
                                if 'script' in port_info and 'modbus-discover' in port_info['script']:
                                    modbus_info = port_info['script']['modbus-discover']
                                    device['modbus_info'] = modbus_info
                                    device['device_type'] = self._parse_modbus_device_type(modbus_info)
                                    device['manufacturer'] = self._parse_manufacturer(modbus_info)
                                    device['model'] = self._parse_model(modbus_info)
                                else:
                                    # Fallback: try to detect via port number
                                    if port == 102:
                                        # Port 102 is typically used by Siemens S7 PLCs
                                        device['device_type'] = 'SIEMENS_S7'
                                        device['manufacturer'] = 'Siemens'
                                        device['model'] = 'S7 PLC'
                                    elif port in [502, 510]:
                                        device['device_type'] = 'MODBUS_TCP'
                                        device['manufacturer'] = 'Generic'
                                        device['model'] = 'Modbus TCP'
                                    elif port >= 20000 and port <= 20100:
                                        # Common range for Modbus TCP gateways
                                        device['device_type'] = 'MODBUS_TCP'
                                        device['manufacturer'] = 'Generic'
                                        device['model'] = 'Modbus Gateway'
                                    else:
                                        # Unknown port, but likely Modbus if nmap found it
                                        device['device_type'] = 'MODBUS_DEVICE'
                                        device['manufacturer'] = 'Unknown'
                                        device['model'] = 'Modbus Device'

                                # Auto-generate device name
                                device['name'] = self._generate_device_name(device)

                                devices.append(device)
                                logger.info(f"Discovered Modbus device: {device['name']} at {host}:{port}")

            logger.info(f"Nmap scan complete. Found {len(devices)} Modbus device(s).")

        except nmap.PortScannerError as e:
            logger.error(f"Nmap scan error: {e}")
            raise Exception(f"Nmap not available or error during scan: {e}")
        except Exception as e:
            logger.error(f"Error during nmap scan: {e}", exc_info=True)
            raise

        return devices

    def _parse_modbus_device_type(self, modbus_info: str) -> str:
        """
        Parse device type from modbus-discover script output

        Args:
            modbus_info: Output from modbus-discover script

        Returns:
            Device type identifier
        """
        modbus_lower = modbus_info.lower()

        # Check for known device types
        if 'logo!' in modbus_lower or 'logo 8' in modbus_lower:
            return 'LOGO_8'
        elif 'logo' in modbus_lower and '0ba7' in modbus_lower:
            return 'LOGO_0BA7'
        elif 'siemens' in modbus_lower:
            return 'SIEMENS_PLC'
        elif 'schneider' in modbus_lower or 'modicon' in modbus_lower:
            return 'SCHNEIDER_PLC'
        elif 'allen bradley' in modbus_lower or 'rockwell' in modbus_lower:
            return 'AB_PLC'
        elif 'wago' in modbus_lower:
            return 'WAGO_PLC'
        else:
            return 'GENERIC_MODBUS'

    def _parse_manufacturer(self, modbus_info: str) -> str:
        """Parse manufacturer from modbus info"""
        modbus_lower = modbus_info.lower()

        if 'siemens' in modbus_lower or 'logo' in modbus_lower:
            return 'Siemens'
        elif 'schneider' in modbus_lower or 'modicon' in modbus_lower:
            return 'Schneider Electric'
        elif 'allen bradley' in modbus_lower or 'rockwell' in modbus_lower:
            return 'Allen Bradley'
        elif 'wago' in modbus_lower:
            return 'Wago'
        elif 'abb' in modbus_lower:
            return 'ABB'
        else:
            return 'Generic'

    def _parse_model(self, modbus_info: str) -> str:
        """Parse model from modbus info"""
        modbus_lower = modbus_info.lower()

        if 'logo! 8' in modbus_lower or 'logo 8' in modbus_lower:
            return 'LOGO! 8'
        elif 'logo' in modbus_lower and '0ba7' in modbus_lower:
            return 'LOGO! 0BA7'
        elif 'logo' in modbus_lower:
            return 'LOGO!'
        elif 'modicon' in modbus_lower:
            return 'Modicon M221'
        else:
            return 'Modbus TCP'

    def _generate_device_name(self, device: Dict) -> str:
        """
        Generate a descriptive device name

        Args:
            device: Device information dictionary

        Returns:
            Generated device name
        """
        ip_last_octet = device['ip'].split('.')[-1]

        manufacturer = device.get('manufacturer', 'Device')
        model = device.get('model', '')

        if manufacturer == 'Siemens' and 'LOGO' in model:
            return f"LOGO_{ip_last_octet}"
        elif manufacturer != 'Generic':
            return f"{manufacturer}_{ip_last_octet}"
        else:
            return f"Modbus_{ip_last_octet}"

    def quick_port_scan(self, ip: str, port_range: str = "1-65535") -> List[int]:
        """
        Quick TCP port scan to find open ports

        Args:
            ip: IP address to scan
            port_range: Port range (e.g., '1-1000' or '502,510')

        Returns:
            List of open ports
        """
        logger.info(f"Quick port scan on {ip}, range: {port_range}")

        open_ports = []

        try:
            self.nm.scan(hosts=ip, arguments=f"-p {port_range} --open -T4")

            if ip in self.nm.all_hosts():
                for proto in self.nm[ip].all_protocols():
                    ports = self.nm[ip][proto].keys()
                    for port in ports:
                        if self.nm[ip][proto][port]['state'] == 'open':
                            open_ports.append(port)

            logger.info(f"Found {len(open_ports)} open port(s) on {ip}")

        except Exception as e:
            logger.error(f"Error during quick port scan: {e}")

        return sorted(open_ports)

    def detect_modbus_ports(self, ip: str) -> List[int]:
        """
        Detect common and uncommon Modbus ports on a specific IP

        Args:
            ip: IP address to scan

        Returns:
            List of detected Modbus ports
        """
        # Common Modbus ports and extended range
        common_ports = "502,510,2222,20000-20100,44818,47808,502"

        logger.info(f"Detecting Modbus ports on {ip}")

        modbus_ports = []

        try:
            # Scan for open ports
            open_ports = self.quick_port_scan(ip, common_ports)

            # Test each open port for Modbus capability
            from modbus_scanner import ModbusScanner

            for port in open_ports:
                try:
                    scanner = ModbusScanner(ip, port, timeout=2)
                    if scanner.test_connection():
                        modbus_ports.append(port)
                        logger.info(f"Confirmed Modbus on {ip}:{port}")
                except Exception as e:
                    logger.debug(f"Port {port} is not Modbus: {e}")

        except Exception as e:
            logger.error(f"Error detecting Modbus ports: {e}")

        return modbus_ports

"""
Network Detection Module
Automatically detects local network information (IP, DNS, Netmask, Gateway)
"""

import socket
import struct
import subprocess
import logging
import ipaddress
import os
import requests

logger = logging.getLogger(__name__)


class NetworkDetector:
    """Detects local network configuration"""

    def __init__(self):
        self.network_info = None

    def get_network_info(self):
        """
        Get comprehensive network information
        Returns dict with: ip, netmask, gateway, dns, network_range
        """
        try:
            # Try Home Assistant Supervisor API first (for Add-on environment)
            supervisor_info = self._get_supervisor_network_info()
            if supervisor_info:
                logger.info("Using network info from Supervisor API")
                return supervisor_info

            # Fallback to local detection
            network_info = {
                'ip': self._get_local_ip(),
                'netmask': self._get_netmask(),
                'gateway': self._get_default_gateway(),
                'dns': self._get_dns_servers(),
                'network_range': None,
                'scan_range': None
            }

            # Calculate network range for scanning
            if network_info['ip'] and network_info['netmask']:
                network_range = self._calculate_network_range(
                    network_info['ip'],
                    network_info['netmask']
                )
                network_info['network_range'] = network_range
                network_info['scan_range'] = network_range  # e.g., "192.168.178.0/24"

            logger.info(f"Network detected: {network_info}")
            self.network_info = network_info
            return network_info

        except Exception as e:
            logger.error(f"Error detecting network: {e}")
            return {
                'ip': 'Unknown',
                'netmask': 'Unknown',
                'gateway': 'Unknown',
                'dns': 'Unknown',
                'network_range': None,
                'scan_range': None,
                'error': str(e)
            }

    def _get_supervisor_network_info(self):
        """
        Get network info from Home Assistant Supervisor API
        This works when running as a Home Assistant Add-on
        """
        try:
            supervisor_token = os.environ.get('SUPERVISOR_TOKEN')
            if not supervisor_token:
                logger.debug("No SUPERVISOR_TOKEN found, skipping Supervisor API")
                return None

            # Query Supervisor API for network info
            headers = {
                'Authorization': f'Bearer {supervisor_token}',
                'Content-Type': 'application/json'
            }

            # Get network interface info from Supervisor
            response = requests.get(
                'http://supervisor/network/info',
                headers=headers,
                timeout=5
            )

            if response.status_code != 200:
                logger.warning(f"Supervisor API returned status {response.status_code}")
                return None

            data = response.json()

            # Find primary interface (usually eth0 or similar)
            interfaces = data.get('data', {}).get('interfaces', [])
            primary_interface = None

            for iface in interfaces:
                # Skip docker/loopback interfaces
                if iface.get('interface', '').startswith(('docker', 'veth', 'lo')):
                    continue

                # Find interface with IPv4
                if iface.get('ipv4') and iface['ipv4'].get('address'):
                    primary_interface = iface
                    break

            if not primary_interface:
                logger.warning("No suitable network interface found in Supervisor API")
                return None

            # Extract network info
            ipv4 = primary_interface.get('ipv4', {})
            ip = ipv4.get('address', [])[0] if ipv4.get('address') else None
            gateway = ipv4.get('gateway')
            prefix = ipv4.get('prefix', 24)  # CIDR prefix (e.g., 24 for /24)

            # Get DNS from nameservers
            dns_servers = data.get('data', {}).get('nameservers', [])
            dns = ', '.join(dns_servers[:2]) if dns_servers else 'Unknown'

            if not ip:
                return None

            # Calculate netmask from CIDR prefix
            netmask = self._cidr_to_netmask(prefix)

            # Calculate network range
            network_range = self._calculate_network_range(ip, netmask)

            network_info = {
                'ip': ip,
                'netmask': netmask,
                'gateway': gateway or 'Unknown',
                'dns': dns,
                'network_range': network_range,
                'scan_range': network_range
            }

            logger.info(f"Network info from Supervisor: {network_info}")
            self.network_info = network_info
            return network_info

        except Exception as e:
            logger.warning(f"Could not get network info from Supervisor API: {e}")
            return None

    def _get_local_ip(self):
        """Get local IP address"""
        try:
            # Try to get IP by connecting to external host (doesn't actually send data)
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception as e:
            logger.warning(f"Could not detect IP via socket: {e}")

            # Fallback: Try to read from ip command
            try:
                result = subprocess.run(
                    ['ip', 'route', 'get', '1'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    # Parse output: "1.0.0.0 via 192.168.1.1 dev eth0 src 192.168.1.100"
                    for line in result.stdout.split('\n'):
                        if 'src' in line:
                            parts = line.split('src')
                            if len(parts) > 1:
                                ip = parts[1].strip().split()[0]
                                return ip
            except Exception as e2:
                logger.warning(f"Could not detect IP via ip command: {e2}")

            return 'Unknown'

    def _get_netmask(self):
        """Get network mask"""
        try:
            # Try using ip command
            result = subprocess.run(
                ['ip', 'addr', 'show'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                local_ip = self._get_local_ip()
                if local_ip and local_ip != 'Unknown':
                    # Find the line with our IP
                    for line in result.stdout.split('\n'):
                        if local_ip in line and 'inet ' in line:
                            # Format: "inet 192.168.178.50/24 brd ..."
                            parts = line.strip().split()
                            for part in parts:
                                if '/' in part and local_ip in part:
                                    cidr = part.split('/')[1]
                                    # Convert CIDR to netmask
                                    return self._cidr_to_netmask(int(cidr))

            # Default fallback
            return '255.255.255.0'

        except Exception as e:
            logger.warning(f"Could not detect netmask: {e}")
            return '255.255.255.0'

    def _get_default_gateway(self):
        """Get default gateway"""
        try:
            result = subprocess.run(
                ['ip', 'route', 'show', 'default'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                # Parse: "default via 192.168.178.1 dev eth0"
                for line in result.stdout.split('\n'):
                    if 'default via' in line:
                        parts = line.split('via')
                        if len(parts) > 1:
                            gateway = parts[1].strip().split()[0]
                            return gateway

            return 'Unknown'

        except Exception as e:
            logger.warning(f"Could not detect gateway: {e}")
            return 'Unknown'

    def _get_dns_servers(self):
        """Get DNS servers"""
        try:
            with open('/etc/resolv.conf', 'r') as f:
                dns_servers = []
                for line in f:
                    if line.startswith('nameserver'):
                        dns = line.split()[1]
                        dns_servers.append(dns)

                if dns_servers:
                    return ', '.join(dns_servers[:2])  # Return first 2

            return 'Unknown'

        except Exception as e:
            logger.warning(f"Could not detect DNS: {e}")
            return 'Unknown'

    def _cidr_to_netmask(self, cidr):
        """Convert CIDR notation to netmask (e.g., 24 -> 255.255.255.0)"""
        mask = (0xffffffff >> (32 - cidr)) << (32 - cidr)
        return socket.inet_ntoa(struct.pack('>I', mask))

    def _calculate_network_range(self, ip, netmask):
        """
        Calculate network range from IP and netmask
        Returns CIDR notation (e.g., "192.168.178.0/24")
        """
        try:
            # Convert netmask to CIDR
            cidr = sum([bin(int(x)).count('1') for x in netmask.split('.')])

            # Create network object
            network = ipaddress.IPv4Network(f"{ip}/{cidr}", strict=False)

            return str(network)

        except Exception as e:
            logger.error(f"Error calculating network range: {e}")
            return None

    def get_scan_targets(self, custom_target=None):
        """
        Get scan targets (either custom or auto-detected network range)

        Args:
            custom_target: Optional custom IP/range to scan

        Returns:
            String with IP/range to scan (e.g., "192.168.178.0/24" or "192.168.1.100")
        """
        if custom_target:
            return custom_target

        # Use auto-detected range
        if not self.network_info:
            self.get_network_info()

        return self.network_info.get('scan_range', '192.168.1.0/24')

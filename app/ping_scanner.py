"""
Ping Scanner for Network Device Discovery
Performs fast ICMP ping scan and retrieves MAC addresses
"""
import logging
import subprocess
import ipaddress
import re
import socket
import concurrent.futures
from typing import List, Dict, Optional, Callable

logger = logging.getLogger(__name__)

# MAC Vendor Database (OUI - first 3 bytes)
# Source: IEEE OUI database - common industrial vendors
MAC_VENDORS = {
    # Siemens
    "00:1B:1B": "Siemens",
    "00:0E:8C": "Siemens",
    "00:1C:06": "Siemens",
    "00:1F:F8": "Siemens",
    "64:00:6A": "Siemens",
    "98:4B:E1": "Siemens",
    "B0:00:B4": "Siemens",
    "00:30:DE": "Siemens",
    "08:00:06": "Siemens",
    "00:60:65": "Siemens",

    # Schneider Electric
    "00:00:54": "Schneider Electric",
    "00:80:F4": "Schneider Electric",
    "00:0D:5D": "Schneider Electric",

    # ABB
    "00:21:99": "ABB",
    "00:24:7D": "ABB",

    # Wago
    "00:30:DE": "Wago",
    "00:A0:45": "Wago",

    # Beckhoff
    "00:01:05": "Beckhoff",

    # Phoenix Contact
    "00:A0:57": "Phoenix Contact",

    # Moxa
    "00:90:E8": "Moxa",

    # Advantech
    "00:0B:AB": "Advantech",
    "00:D0:C9": "Advantech",

    # B&R Automation
    "00:60:65": "B&R",

    # Pilz
    "00:03:A0": "Pilz",

    # Rockwell/Allen-Bradley
    "00:00:BC": "Rockwell",
    "00:1D:9C": "Rockwell",

    # Omron
    "00:00:62": "Omron",

    # Mitsubishi
    "00:06:FA": "Mitsubishi",

    # Common Network Equipment
    "00:1A:79": "Cisco",
    "00:1B:0D": "Cisco",
    "00:1E:49": "Cisco",
    "00:50:56": "VMware",
    "08:00:27": "VirtualBox",
    "52:54:00": "QEMU",
    "00:1C:C0": "Intel",
    "00:1E:67": "Intel",
    "3C:D9:2B": "HP",
    "00:1A:4B": "HP",
    "00:23:24": "Dell",
    "F4:8E:38": "Dell",
    "00:1E:58": "D-Link",
    "00:1D:7E": "Linksys",
    "00:1F:33": "Netgear",
    "C8:3A:35": "AVM",
    "24:65:11": "AVM",
    "B0:48:7A": "AVM",
    "00:04:0E": "AVM",
    "3C:A6:2F": "AVM",
    "88:71:B1": "AVM",

    # Raspberry Pi
    "B8:27:EB": "Raspberry Pi",
    "DC:A6:32": "Raspberry Pi",
    "E4:5F:01": "Raspberry Pi",

    # ESP/Arduino
    "24:6F:28": "Espressif",
    "30:AE:A4": "Espressif",
    "84:CC:A8": "Espressif",
    "A4:CF:12": "Espressif",
    "5C:CF:7F": "Espressif",
}


def get_vendor_from_mac(mac: str) -> str:
    """
    Get vendor name from MAC address using OUI lookup

    Args:
        mac: MAC address in format XX:XX:XX:XX:XX:XX or XX-XX-XX-XX-XX-XX

    Returns:
        Vendor name or "Unknown"
    """
    if not mac:
        return "Unknown"

    # Normalize MAC address
    mac = mac.upper().replace("-", ":")

    # Get OUI (first 3 bytes)
    oui = mac[:8]

    return MAC_VENDORS.get(oui, "Unknown")


def ping_host(ip: str, timeout: float = 0.5) -> bool:
    """
    Ping a single host

    Args:
        ip: IP address to ping
        timeout: Timeout in seconds

    Returns:
        True if host responds, False otherwise
    """
    try:
        # Use ping command with timeout
        result = subprocess.run(
            ["ping", "-c", "1", "-W", str(int(timeout * 1000)), ip],
            capture_output=True,
            timeout=timeout + 1
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False


def get_mac_from_ip(ip: str) -> Optional[str]:
    """
    Get MAC address for an IP from ARP cache

    Args:
        ip: IP address

    Returns:
        MAC address or None
    """
    try:
        # Try to read from ARP cache
        result = subprocess.run(
            ["ip", "neighbor", "show", ip],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            # Parse output: "192.168.1.1 dev eth0 lladdr aa:bb:cc:dd:ee:ff REACHABLE"
            match = re.search(r'lladdr\s+([0-9a-fA-F:]+)', result.stdout)
            if match:
                return match.group(1).upper()

        # Fallback: Try arp command
        result = subprocess.run(
            ["arp", "-n", ip],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            # Parse output
            match = re.search(r'([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}', result.stdout)
            if match:
                return match.group(0).upper().replace("-", ":")

    except Exception as e:
        logger.debug(f"Could not get MAC for {ip}: {e}")

    return None


def get_hostname(ip: str) -> Optional[str]:
    """
    Try to resolve hostname for IP

    Args:
        ip: IP address

    Returns:
        Hostname or None
    """
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        return hostname
    except Exception:
        return None


class PingScanner:
    """Fast network scanner using ICMP ping"""

    def __init__(self, timeout: float = 0.5, max_workers: int = 50):
        """
        Initialize ping scanner

        Args:
            timeout: Ping timeout per host in seconds
            max_workers: Maximum concurrent ping threads
        """
        self.timeout = timeout
        self.max_workers = max_workers

    def scan_network(
        self,
        network: str,
        progress_callback: Optional[Callable[[str, int, int, Optional[Dict]], None]] = None
    ) -> List[Dict]:
        """
        Scan network for active hosts using ping

        Args:
            network: Network in CIDR notation (e.g., "192.168.1.0/24")
            progress_callback: Optional callback(current_ip, scanned, total, found_device)

        Returns:
            List of discovered devices with IP, MAC, vendor
        """
        devices = []

        try:
            net = ipaddress.IPv4Network(network, strict=False)
            hosts = list(net.hosts())
            total = len(hosts)

            logger.info(f"Starting ping scan on {network} ({total} hosts)")

            scanned = 0

            def scan_host(ip_str: str) -> Optional[Dict]:
                """Scan a single host"""
                if ping_host(ip_str, self.timeout):
                    # Host is alive, get MAC address
                    mac = get_mac_from_ip(ip_str)
                    vendor = get_vendor_from_mac(mac) if mac else "Unknown"
                    hostname = get_hostname(ip_str)

                    return {
                        "ip": ip_str,
                        "mac": mac or "Unknown",
                        "vendor": vendor,
                        "hostname": hostname,
                        "status": "online"
                    }
                return None

            # Use thread pool for parallel scanning
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all ping tasks
                future_to_ip = {
                    executor.submit(scan_host, str(ip)): str(ip)
                    for ip in hosts
                }

                # Process results as they complete
                for future in concurrent.futures.as_completed(future_to_ip):
                    ip_str = future_to_ip[future]
                    scanned += 1

                    try:
                        result = future.result()
                        if result:
                            devices.append(result)
                            logger.info(f"Found device: {result['ip']} ({result['vendor']})")

                            if progress_callback:
                                progress_callback(ip_str, scanned, total, result)
                        else:
                            if progress_callback:
                                progress_callback(ip_str, scanned, total, None)
                    except Exception as e:
                        logger.debug(f"Error scanning {ip_str}: {e}")
                        if progress_callback:
                            progress_callback(ip_str, scanned, total, None)

            logger.info(f"Ping scan complete: {len(devices)} devices found")

        except Exception as e:
            logger.error(f"Ping scan error: {e}", exc_info=True)

        return devices

    def scan_host_detailed(self, ip: str) -> Optional[Dict]:
        """
        Get detailed information about a single host

        Args:
            ip: IP address to scan

        Returns:
            Device info dict or None if host is offline
        """
        if not ping_host(ip, self.timeout):
            return None

        mac = get_mac_from_ip(ip)
        vendor = get_vendor_from_mac(mac) if mac else "Unknown"
        hostname = get_hostname(ip)

        return {
            "ip": ip,
            "mac": mac or "Unknown",
            "vendor": vendor,
            "hostname": hostname,
            "status": "online"
        }


# Convenience function for quick network scan
def quick_ping_scan(
    network: str,
    progress_callback: Optional[Callable] = None
) -> List[Dict]:
    """
    Perform a quick ping scan on the network

    Args:
        network: Network in CIDR notation
        progress_callback: Optional progress callback

    Returns:
        List of discovered devices
    """
    scanner = PingScanner(timeout=0.5, max_workers=100)
    return scanner.scan_network(network, progress_callback)

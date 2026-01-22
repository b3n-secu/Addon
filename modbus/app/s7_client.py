"""
S7 Protocol Client for Siemens LOGO! v7/0BA7
Uses python-snap7 library for S7 communication
"""

try:
    from snap7.logo import Logo
    from snap7.exceptions import Snap7Exception
    SNAP7_AVAILABLE = True
except ImportError:
    SNAP7_AVAILABLE = False
    Logo = None
    Snap7Exception = Exception

import logging

logger = logging.getLogger(__name__)


class S7Client:
    """S7 Protocol client for LOGO! v7/0BA7"""

    def __init__(self, host, port=102, local_tsap=0x0100, remote_tsap=0x2000):
        """
        Initialize S7 client

        Args:
            host: IP address of LOGO! device
            port: TCP port (default 102 for S7)
            local_tsap: Local TSAP (default 0x0100 = 01.00)
            remote_tsap: Remote TSAP (default 0x2000 = 20.00)
        """
        if not SNAP7_AVAILABLE:
            raise ImportError(
                "python-snap7 library not installed. "
                "Install with: pip install python-snap7"
            )

        self.host = host
        self.port = port
        self.local_tsap = local_tsap
        self.remote_tsap = remote_tsap
        self.client = None
        self.connected = False

    def connect(self):
        """Connect to LOGO! device via S7 protocol"""
        try:
            self.client = Logo()
            self.client.connect(
                self.host,
                self.local_tsap,
                self.remote_tsap,
                self.port
            )
            self.connected = True
            logger.info(f"S7 connection established to {self.host}:{self.port}")
            return True
        except Snap7Exception as e:
            logger.error(f"S7 connection failed: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """Disconnect from LOGO! device"""
        if self.client:
            try:
                self.client.disconnect()
                logger.info(f"S7 disconnected from {self.host}")
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
            finally:
                self.connected = False

    def read_vm(self, address):
        """
        Read value from VM address

        Args:
            address: VM address string (e.g., "V10", "VW12", "V10.3")

        Returns:
            int: Value read from address, or None if error
        """
        if not self.connected:
            logger.error("Not connected to LOGO! device")
            return None

        try:
            value = self.client.read(address)
            logger.debug(f"Read {address}: {value}")
            return value
        except Snap7Exception as e:
            logger.error(f"Error reading {address}: {e}")
            return None

    def write_vm(self, address, value):
        """
        Write value to VM address

        Args:
            address: VM address string (e.g., "V10", "VW12", "V10.3")
            value: Integer value to write

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.connected:
            logger.error("Not connected to LOGO! device")
            return False

        try:
            self.client.write(address, value)
            logger.debug(f"Wrote {address}: {value}")
            return True
        except Snap7Exception as e:
            logger.error(f"Error writing {address}: {e}")
            return False

    def read_multiple(self, addresses):
        """
        Read multiple VM addresses

        Args:
            addresses: List of VM address strings

        Returns:
            dict: Dictionary mapping addresses to values
        """
        results = {}
        for addr in addresses:
            value = self.read_vm(addr)
            if value is not None:
                results[addr] = value
        return results

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


def create_home_assistant_s7_config(device_name, host, variables):
    """
    Create Home Assistant configuration for S7 LOGO! v7

    Args:
        device_name: Name of the LOGO! device
        host: IP address
        variables: List of dicts with 'name', 'address', 'type' keys

    Returns:
        dict: Home Assistant configuration
    """
    config = {
        "s7": {
            "host": host,
            "port": 102,
            "tsap_client": "0x0100",
            "tsap_server": "0x2000",
            "variables": []
        }
    }

    for var in variables:
        var_config = {
            "name": f"{device_name}_{var['name']}",
            "address": var["address"],
            "type": var.get("type", "sensor")
        }
        config["s7"]["variables"].append(var_config)

    return config

"""
Device Database Module
Provides structured device information based on ports, manufacturers, and detection patterns
"""
import json
import logging
import os
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class DeviceDatabase:
    """
    Manages device database for Modbus device identification
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize device database

        Args:
            db_path: Path to device_database.json (optional)
        """
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), 'device_database.json')

        self.db_path = db_path
        self.db = self._load_database()

    def _load_database(self) -> Dict:
        """Load device database from JSON file"""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                db = json.load(f)
                logger.info(f"Loaded device database version {db.get('version', 'unknown')}")
                return db
        except FileNotFoundError:
            logger.error(f"Device database not found at {self.db_path}")
            return self._get_fallback_database()
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing device database: {e}")
            return self._get_fallback_database()

    def _get_fallback_database(self) -> Dict:
        """Return minimal fallback database if main database is unavailable"""
        return {
            "version": "0.0.0-fallback",
            "port_mappings": {},
            "manufacturers": {},
            "detection_rules": {}
        }

    def get_device_by_port(self, port: int) -> Optional[Dict]:
        """
        Get device information based on port number

        Args:
            port: Port number

        Returns:
            Device information dict or None
        """
        port_str = str(port)

        # Direct port lookup
        if port_str in self.db.get('port_mappings', {}):
            port_info = self.db['port_mappings'][port_str]
            if port_info.get('common_devices'):
                # Return first device as default
                device = port_info['common_devices'][0].copy()
                device['port'] = port
                device['protocol'] = port_info.get('protocol', 'Unknown')
                return device

        # Range lookup (e.g., 20000-20100)
        for port_range, port_info in self.db.get('port_mappings', {}).items():
            if '-' in port_range:
                try:
                    start, end = port_range.split('-')
                    if int(start) <= port <= int(end):
                        if port_info.get('common_devices'):
                            device = port_info['common_devices'][0].copy()
                            device['port'] = port
                            device['protocol'] = port_info.get('protocol', 'Unknown')
                            return device
                except (ValueError, AttributeError):
                    continue

        return None

    def identify_device(
        self,
        port: int,
        banner: Optional[str] = None,
        modbus_info: Optional[str] = None,
        vendor_id: Optional[int] = None
    ) -> Tuple[str, str, str]:
        """
        Identify device based on multiple detection criteria

        Args:
            port: Port number
            banner: Banner string from service detection
            modbus_info: Modbus-discover script output
            vendor_id: Modbus vendor ID

        Returns:
            Tuple of (manufacturer, model, device_type)
        """
        manufacturer = "Unknown"
        model = "Unknown Device"
        device_type = "MODBUS_DEVICE"

        # Priority 1: Vendor ID
        if vendor_id is not None:
            vendor_ids = self.db.get('detection_rules', {}).get('vendor_ids', {})
            if str(vendor_id) in vendor_ids:
                manufacturer = vendor_ids[str(vendor_id)]

        # Priority 2: Banner/Modbus Info patterns
        if banner or modbus_info:
            detected = self._detect_from_banner(banner or modbus_info or "")
            if detected:
                manufacturer, model, device_type = detected
                return manufacturer, model, device_type

        # Priority 3: Port-based detection
        device_info = self.get_device_by_port(port)
        if device_info:
            manufacturer = device_info.get('manufacturer', 'Generic')
            model = device_info.get('default_model', 'Modbus Device')
            device_type = device_info.get('device_type', 'MODBUS_DEVICE')

        return manufacturer, model, device_type

    def _detect_from_banner(self, text: str) -> Optional[Tuple[str, str, str]]:
        """
        Detect device from banner text using pattern matching

        Args:
            text: Banner or modbus-discover output

        Returns:
            Tuple of (manufacturer, model, device_type) or None
        """
        text_lower = text.lower()

        patterns = self.db.get('detection_rules', {}).get('banner_patterns', {})

        # Check Siemens LOGO!
        if any(p.lower() in text_lower for p in patterns.get('siemens_logo', [])):
            if '0ba7' in text_lower:
                return 'Siemens', 'LOGO! 0BA7', 'LOGO_0BA7'
            else:
                return 'Siemens', 'LOGO! 8', 'LOGO_8'

        # Check Siemens S7
        if any(p.lower() in text_lower for p in patterns.get('siemens_s7', [])):
            if 's7-1200' in text_lower:
                return 'Siemens', 'S7-1200', 'SIEMENS_S7'
            elif 's7-1500' in text_lower:
                return 'Siemens', 'S7-1500', 'SIEMENS_S7'
            elif 's7-300' in text_lower:
                return 'Siemens', 'S7-300', 'SIEMENS_S7'
            elif 's7-400' in text_lower:
                return 'Siemens', 'S7-400', 'SIEMENS_S7'
            else:
                return 'Siemens', 'S7 PLC', 'SIEMENS_S7'

        # Check Schneider
        if any(p.lower() in text_lower for p in patterns.get('schneider', [])):
            return 'Schneider Electric', 'Modicon PLC', 'SCHNEIDER_PLC'

        # Check ABB
        if any(p.lower() in text_lower for p in patterns.get('abb', [])):
            return 'ABB', 'AC500 PLC', 'ABB_PLC'

        # Check Wago
        if any(p.lower() in text_lower for p in patterns.get('wago', [])):
            return 'Wago', 'PFC Controller', 'WAGO_PLC'

        # Check Allen-Bradley
        if any(p.lower() in text_lower for p in patterns.get('allen_bradley', [])):
            return 'Allen-Bradley', 'ControlLogix', 'AB_PLC'

        return None

    def get_manufacturer_info(self, manufacturer_key: str) -> Optional[Dict]:
        """
        Get detailed manufacturer information

        Args:
            manufacturer_key: Manufacturer key (e.g., 'siemens', 'schneider')

        Returns:
            Manufacturer info dict or None
        """
        return self.db.get('manufacturers', {}).get(manufacturer_key.lower())

    def get_device_profile(self, manufacturer: str, model: str) -> Optional[Dict]:
        """
        Get detailed device profile with register ranges and features

        Args:
            manufacturer: Manufacturer name
            model: Model name

        Returns:
            Device profile dict or None
        """
        manufacturer_key = manufacturer.lower().replace(' ', '_').replace('-', '_')
        manufacturer_info = self.get_manufacturer_info(manufacturer_key)

        if not manufacturer_info:
            return None

        # Search through product lines for matching model
        for product_line_name, product_line in manufacturer_info.get('product_lines', {}).items():
            for model_key, model_info in product_line.get('models', {}).items():
                if model_key.lower() in model.lower() or model.lower() in model_key.lower():
                    return model_info

        return None

    def get_all_supported_ports(self) -> List[int]:
        """
        Get list of all supported ports

        Returns:
            List of port numbers
        """
        ports = []

        for port_str in self.db.get('port_mappings', {}).keys():
            if '-' in port_str:
                # Range
                try:
                    start, end = map(int, port_str.split('-'))
                    ports.extend(range(start, end + 1))
                except ValueError:
                    continue
            else:
                # Single port
                try:
                    ports.append(int(port_str))
                except ValueError:
                    continue

        return sorted(set(ports))

    def get_recommended_port_range(self) -> str:
        """
        Get recommended port range for scanning

        Returns:
            Port range string (e.g., '102,502,510,20000-20100')
        """
        # Get all port mappings
        port_mappings = self.db.get('port_mappings', {})

        single_ports = []
        ranges = []

        for port_str in port_mappings.keys():
            if '-' in port_str:
                ranges.append(port_str)
            else:
                try:
                    single_ports.append(int(port_str))
                except ValueError:
                    continue

        # Build port range string
        single_ports_str = ','.join(map(str, sorted(single_ports)))
        ranges_str = ','.join(ranges)

        if single_ports_str and ranges_str:
            return f"{single_ports_str},{ranges_str}"
        elif single_ports_str:
            return single_ports_str
        else:
            return ranges_str or "502"


# Global instance
_db_instance = None

def get_device_database() -> DeviceDatabase:
    """Get global DeviceDatabase instance (singleton)"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DeviceDatabase()
    return _db_instance

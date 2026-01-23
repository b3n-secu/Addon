"""
Device Manager for Universal Modbus Configurator
Manages both Modbus and S7comm devices with automatic register detection
"""

import logging
from typing import Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class DeviceProtocol(Enum):
    """Device protocol types"""
    MODBUS = "modbus"
    S7COMM = "s7comm"
    UNKNOWN = "unknown"


class RegisterStatus(Enum):
    """Register availability status"""
    AVAILABLE = "available"  # Yellow dot - register exists
    ERROR = "error"  # Black dot - register doesn't exist or error
    UNTESTED = "untested"  # Gray dot - not yet tested


class IOType(Enum):
    """Input/Output types"""
    DIGITAL_INPUT = "digital_input"  # DI - Discrete Inputs
    DIGITAL_OUTPUT = "digital_output"  # DO - Coils
    ANALOG_INPUT = "analog_input"  # AI - Input Registers
    ANALOG_OUTPUT = "analog_output"  # AO - Holding Registers


class Device:
    """Represents a discovered or configured device"""

    def __init__(
        self,
        name: str,
        host: str,
        port: int,
        protocol: DeviceProtocol,
        manufacturer: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ):
        self.name = name
        self.host = host
        self.port = port
        self.protocol = protocol
        self.manufacturer = manufacturer or "Unknown"
        self.model = model or "Unknown"

        # S7-specific attributes
        self.tsap_src = kwargs.get('tsap_src')
        self.tsap_dst = kwargs.get('tsap_dst')
        self.pdu_size = kwargs.get('pdu_size')

        # Modbus-specific attributes
        self.slave_id = kwargs.get('slave_id', 1)

        # Register information
        self.registers = {
            IOType.DIGITAL_INPUT: {},  # address -> RegisterStatus
            IOType.DIGITAL_OUTPUT: {},
            IOType.ANALOG_INPUT: {},
            IOType.ANALOG_OUTPUT: {}
        }

        # I/O Configuration
        self.io_config = {
            IOType.DIGITAL_INPUT: [],  # List of configured I/O points
            IOType.DIGITAL_OUTPUT: [],
            IOType.ANALOG_INPUT: [],
            IOType.ANALOG_OUTPUT: []
        }

        # Device metadata
        self.detected_at = None
        self.last_scan = None
        self.connection_status = "unknown"  # unknown, connected, error

    def to_dict(self) -> dict:
        """Convert device to dictionary for JSON serialization"""
        return {
            'name': self.name,
            'host': self.host,
            'port': self.port,
            'protocol': self.protocol.value,
            'manufacturer': self.manufacturer,
            'model': self.model,
            'slave_id': self.slave_id,
            'tsap_src': self.tsap_src,
            'tsap_dst': self.tsap_dst,
            'pdu_size': self.pdu_size,
            'registers': {
                io_type.value: {
                    str(addr): status.value
                    for addr, status in registers.items()
                }
                for io_type, registers in self.registers.items()
            },
            'io_config': {
                io_type.value: config
                for io_type, config in self.io_config.items()
            },
            'detected_at': self.detected_at,
            'last_scan': self.last_scan,
            'connection_status': self.connection_status
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Device':
        """Create device from dictionary"""
        protocol = DeviceProtocol(data.get('protocol', 'unknown'))

        device = cls(
            name=data['name'],
            host=data['host'],
            port=data['port'],
            protocol=protocol,
            manufacturer=data.get('manufacturer'),
            model=data.get('model'),
            slave_id=data.get('slave_id', 1),
            tsap_src=data.get('tsap_src'),
            tsap_dst=data.get('tsap_dst'),
            pdu_size=data.get('pdu_size')
        )

        # Restore registers
        if 'registers' in data:
            for io_type_str, registers in data['registers'].items():
                try:
                    io_type = IOType(io_type_str)
                    device.registers[io_type] = {
                        int(addr): RegisterStatus(status)
                        for addr, status in registers.items()
                    }
                except (ValueError, KeyError):
                    pass

        # Restore I/O config
        if 'io_config' in data:
            for io_type_str, config in data['io_config'].items():
                try:
                    io_type = IOType(io_type_str)
                    device.io_config[io_type] = config
                except (ValueError, KeyError):
                    pass

        device.detected_at = data.get('detected_at')
        device.last_scan = data.get('last_scan')
        device.connection_status = data.get('connection_status', 'unknown')

        return device


class DeviceManager:
    """Manages all discovered and configured devices"""

    def __init__(self):
        self.devices: Dict[str, Device] = {}  # device_id -> Device

    def add_device(self, device: Device) -> str:
        """
        Add or update device

        Returns:
            str: Device ID
        """
        device_id = self._generate_device_id(device)
        self.devices[device_id] = device
        logger.info(f"Added device: {device.name} ({device.protocol.value}) at {device.host}:{device.port}")
        return device_id

    def remove_device(self, device_id: str) -> bool:
        """Remove device by ID"""
        if device_id in self.devices:
            device = self.devices[device_id]
            del self.devices[device_id]
            logger.info(f"Removed device: {device.name}")
            return True
        return False

    def get_device(self, device_id: str) -> Optional[Device]:
        """Get device by ID"""
        return self.devices.get(device_id)

    def get_all_devices(self) -> List[Device]:
        """Get all devices"""
        return list(self.devices.values())

    def get_devices_by_protocol(self, protocol: DeviceProtocol) -> List[Device]:
        """Get devices by protocol type"""
        return [
            device for device in self.devices.values()
            if device.protocol == protocol
        ]

    def get_modbus_devices(self) -> List[Device]:
        """Get all Modbus devices"""
        return self.get_devices_by_protocol(DeviceProtocol.MODBUS)

    def get_s7_devices(self) -> List[Device]:
        """Get all S7comm devices"""
        return self.get_devices_by_protocol(DeviceProtocol.S7COMM)

    def update_register_status(
        self,
        device_id: str,
        io_type: IOType,
        address: int,
        status: RegisterStatus
    ) -> bool:
        """Update register status for a device"""
        device = self.get_device(device_id)
        if device:
            device.registers[io_type][address] = status
            logger.debug(f"Updated register status: {device.name} {io_type.value}@{address} = {status.value}")
            return True
        return False

    def add_io_point(
        self,
        device_id: str,
        io_type: IOType,
        config: dict
    ) -> bool:
        """
        Add I/O point configuration

        Args:
            device_id: Device ID
            io_type: I/O type
            config: Configuration dict with keys:
                - name: I/O point name
                - address: Register address
                - unit: Unit of measurement (optional)
                - scale: Scaling factor (optional)
                - offset: Offset (optional)
        """
        device = self.get_device(device_id)
        if device:
            device.io_config[io_type].append(config)
            logger.info(f"Added I/O point: {config.get('name')} to {device.name}")
            return True
        return False

    def remove_io_point(
        self,
        device_id: str,
        io_type: IOType,
        index: int
    ) -> bool:
        """Remove I/O point configuration by index"""
        device = self.get_device(device_id)
        if device and 0 <= index < len(device.io_config[io_type]):
            removed = device.io_config[io_type].pop(index)
            logger.info(f"Removed I/O point: {removed.get('name')} from {device.name}")
            return True
        return False

    def get_device_summary(self) -> dict:
        """
        Get summary of all devices

        Returns:
            dict with keys:
                - total: Total number of devices
                - modbus: Number of Modbus devices
                - s7comm: Number of S7comm devices
                - by_status: Count by connection status
        """
        devices = self.get_all_devices()

        summary = {
            'total': len(devices),
            'modbus': len(self.get_modbus_devices()),
            's7comm': len(self.get_s7_devices()),
            'by_status': {
                'connected': 0,
                'error': 0,
                'unknown': 0
            },
            'by_manufacturer': {}
        }

        for device in devices:
            # Count by status
            status = device.connection_status
            if status in summary['by_status']:
                summary['by_status'][status] += 1

            # Count by manufacturer
            mfg = device.manufacturer
            if mfg not in summary['by_manufacturer']:
                summary['by_manufacturer'][mfg] = 0
            summary['by_manufacturer'][mfg] += 1

        return summary

    def to_dict(self) -> dict:
        """Convert all devices to dictionary"""
        return {
            device_id: device.to_dict()
            for device_id, device in self.devices.items()
        }

    def from_dict(self, data: dict):
        """Load devices from dictionary"""
        self.devices.clear()
        for device_id, device_data in data.items():
            try:
                device = Device.from_dict(device_data)
                self.devices[device_id] = device
            except Exception as e:
                logger.error(f"Error loading device {device_id}: {e}")

    @staticmethod
    def _generate_device_id(device: Device) -> str:
        """Generate unique device ID"""
        return f"{device.protocol.value}_{device.host}_{device.port}"

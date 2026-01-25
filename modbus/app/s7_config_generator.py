"""
S7 Configuration Generator
Generates configuration for Home Assistant S7 PLC integration
Based on patterns from ha-s7plc integration
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# S7 Data Types mapping
S7_DATA_TYPES = {
    'bit': {'prefix': 'X', 'size': 1, 'description': 'Boolean bit'},
    'byte': {'prefix': 'B', 'size': 1, 'description': '8-bit unsigned integer (0-255)'},
    'word': {'prefix': 'W', 'size': 2, 'description': '16-bit signed integer'},
    'dword': {'prefix': 'DW', 'size': 4, 'description': '32-bit signed integer'},
    'real': {'prefix': 'R', 'size': 4, 'description': 'IEEE 754 float'},
    'string': {'prefix': 'S', 'size': 0, 'description': 'S7 STRING type'}
}

# LOGO! 8 specific address mappings
LOGO8_ADDRESS_MAP = {
    'digital_inputs': {
        'start': 1024,  # I1-I24
        'count': 24,
        'type': 'bit',
        'db': 1,
        'description': 'Digital Inputs I1-I24'
    },
    'digital_outputs': {
        'start': 1064,  # Q1-Q20
        'count': 20,
        'type': 'bit',
        'db': 1,
        'description': 'Digital Outputs Q1-Q20'
    },
    'flags': {
        'start': 1104,  # M1-M64
        'count': 64,
        'type': 'bit',
        'db': 1,
        'description': 'Flags/Markers M1-M64'
    },
    'analog_inputs': {
        'start': 1032,  # AI1-AI8
        'count': 8,
        'type': 'word',
        'db': 1,
        'description': 'Analog Inputs AI1-AI8'
    },
    'analog_outputs': {
        'start': 1072,  # AQ1-AQ8
        'count': 8,
        'type': 'word',
        'db': 1,
        'description': 'Analog Outputs AQ1-AQ8'
    },
    'variable_memory': {
        'start': 0,  # VB0-VB849
        'count': 850,
        'type': 'byte',
        'db': 1,
        'description': 'Variable Memory VB0-VB849'
    }
}

# Default rack/slot configurations
S7_DEVICE_CONFIGS = {
    'S7-1200': {'rack': 0, 'slot': 1},
    'S7-1500': {'rack': 0, 'slot': 1},
    'S7-300': {'rack': 0, 'slot': 2},
    'S7-400': {'rack': 0, 'slot': 2},
    'LOGO! 8': {'rack': 0, 'slot': 2},
    'LOGO! 0BA7': {'rack': 0, 'slot': 2}
}


class S7ConfigGenerator:
    """
    Generates S7 PLC configuration for Home Assistant
    """

    def __init__(self):
        self.devices: List[Dict] = []
        self.entities: List[Dict] = []

    def add_device(self, device: Dict):
        """Add a S7 device configuration"""
        device_type = device.get('device_type', 'S7-1200')
        config = S7_DEVICE_CONFIGS.get(device_type, {'rack': 0, 'slot': 1})

        self.devices.append({
            'name': device.get('name', f"S7 PLC {device.get('host')}"),
            'host': device.get('host'),
            'port': device.get('port', 102),
            'rack': device.get('rack', config['rack']),
            'slot': device.get('slot', config['slot']),
            'device_type': device_type,
            'scan_interval': device.get('scan_interval', 1)
        })

    def add_entity(self, entity: Dict):
        """Add an entity configuration"""
        self.entities.append(entity)

    def generate_binary_sensor(self, name: str, address: str, device_class: Optional[str] = None) -> Dict:
        """Generate binary sensor entity config"""
        return {
            'platform': 's7plc',
            'entity_type': 'binary_sensor',
            'name': name,
            'address': address,
            'device_class': device_class
        }

    def generate_sensor(self, name: str, address: str, data_type: str = 'word',
                       multiplier: float = 1.0, unit: Optional[str] = None) -> Dict:
        """Generate sensor entity config"""
        return {
            'platform': 's7plc',
            'entity_type': 'sensor',
            'name': name,
            'address': address,
            'data_type': data_type,
            'multiplier': multiplier,
            'unit_of_measurement': unit
        }

    def generate_switch(self, name: str, address: str) -> Dict:
        """Generate switch entity config"""
        return {
            'platform': 's7plc',
            'entity_type': 'switch',
            'name': name,
            'address': address
        }

    def generate_light(self, name: str, address: str, brightness_address: Optional[str] = None) -> Dict:
        """Generate light entity config"""
        config = {
            'platform': 's7plc',
            'entity_type': 'light',
            'name': name,
            'address': address
        }
        if brightness_address:
            config['brightness_address'] = brightness_address
        return config

    def generate_number(self, name: str, address: str, data_type: str = 'word',
                       min_value: float = 0, max_value: float = 100,
                       multiplier: float = 1.0) -> Dict:
        """Generate number entity config"""
        return {
            'platform': 's7plc',
            'entity_type': 'number',
            'name': name,
            'address': address,
            'data_type': data_type,
            'min': min_value,
            'max': max_value,
            'multiplier': multiplier
        }

    def generate_logo8_config(self, device: Dict) -> Dict:
        """Generate complete LOGO! 8 configuration with standard entities"""
        host = device.get('host')
        name_prefix = device.get('name', 'LOGO8')

        config = {
            'device': {
                'name': name_prefix,
                'host': host,
                'port': 102,
                'rack': 0,
                'slot': 2,
                'type': 'LOGO! 8'
            },
            'binary_sensors': [],
            'sensors': [],
            'switches': [],
            'lights': []
        }

        # Generate Digital Inputs (I1-I24)
        for i in range(1, 25):
            byte_addr = (i - 1) // 8
            bit_addr = (i - 1) % 8
            config['binary_sensors'].append({
                'name': f'{name_prefix} Input I{i}',
                'address': f'DB1,X{1024 + byte_addr}.{bit_addr}',
                'device_class': 'opening'
            })

        # Generate Digital Outputs (Q1-Q20)
        for i in range(1, 21):
            byte_addr = (i - 1) // 8
            bit_addr = (i - 1) % 8
            config['switches'].append({
                'name': f'{name_prefix} Output Q{i}',
                'address': f'DB1,X{1064 + byte_addr}.{bit_addr}'
            })

        # Generate Analog Inputs (AI1-AI8)
        for i in range(1, 9):
            config['sensors'].append({
                'name': f'{name_prefix} Analog Input AI{i}',
                'address': f'DB1,W{1032 + (i-1) * 2}',
                'data_type': 'word',
                'multiplier': 0.1,
                'unit': 'V'
            })

        # Generate Analog Outputs (AQ1-AQ8)
        for i in range(1, 9):
            config['sensors'].append({
                'name': f'{name_prefix} Analog Output AQ{i}',
                'address': f'DB1,W{1072 + (i-1) * 2}',
                'data_type': 'word',
                'multiplier': 0.1,
                'unit': 'V'
            })

        return config

    def generate_ha_automation_yaml(self, device_config: Dict) -> str:
        """Generate Home Assistant automation YAML for S7 entities"""
        yaml_lines = ['# S7 PLC Configuration for Home Assistant']
        yaml_lines.append(f'# Device: {device_config["device"]["name"]}')
        yaml_lines.append(f'# Host: {device_config["device"]["host"]}')
        yaml_lines.append('')

        # Binary sensors
        if device_config.get('binary_sensors'):
            yaml_lines.append('# Binary Sensors (Digital Inputs)')
            yaml_lines.append('binary_sensor:')
            for sensor in device_config['binary_sensors']:
                yaml_lines.append(f'  - platform: s7plc')
                yaml_lines.append(f'    name: "{sensor["name"]}"')
                yaml_lines.append(f'    address: "{sensor["address"]}"')
                if sensor.get('device_class'):
                    yaml_lines.append(f'    device_class: {sensor["device_class"]}')
                yaml_lines.append('')

        # Sensors (Analog)
        if device_config.get('sensors'):
            yaml_lines.append('# Sensors (Analog Inputs/Outputs)')
            yaml_lines.append('sensor:')
            for sensor in device_config['sensors']:
                yaml_lines.append(f'  - platform: s7plc')
                yaml_lines.append(f'    name: "{sensor["name"]}"')
                yaml_lines.append(f'    address: "{sensor["address"]}"')
                yaml_lines.append(f'    data_type: {sensor.get("data_type", "word")}')
                if sensor.get('multiplier', 1) != 1:
                    yaml_lines.append(f'    multiplier: {sensor["multiplier"]}')
                if sensor.get('unit'):
                    yaml_lines.append(f'    unit_of_measurement: "{sensor["unit"]}"')
                yaml_lines.append('')

        # Switches (Digital Outputs)
        if device_config.get('switches'):
            yaml_lines.append('# Switches (Digital Outputs)')
            yaml_lines.append('switch:')
            for switch in device_config['switches']:
                yaml_lines.append(f'  - platform: s7plc')
                yaml_lines.append(f'    name: "{switch["name"]}"')
                yaml_lines.append(f'    address: "{switch["address"]}"')
                yaml_lines.append('')

        # Lights
        if device_config.get('lights'):
            yaml_lines.append('# Lights')
            yaml_lines.append('light:')
            for light in device_config['lights']:
                yaml_lines.append(f'  - platform: s7plc')
                yaml_lines.append(f'    name: "{light["name"]}"')
                yaml_lines.append(f'    address: "{light["address"]}"')
                if light.get('brightness_address'):
                    yaml_lines.append(f'    brightness_address: "{light["brightness_address"]}"')
                yaml_lines.append('')

        return '\n'.join(yaml_lines)

    def clear(self):
        """Clear all configurations"""
        self.devices.clear()
        self.entities.clear()


# Global S7 config generator instance
s7_config_generator = S7ConfigGenerator()

"""
Configuration generator for Home Assistant Modbus integration
Based on official Home Assistant Modbus Integration documentation
"""
import yaml
import logging
from device_profiles import get_device_profile

logger = logging.getLogger(__name__)


class ModbusConfigGenerator:
    """Generator for Modbus YAML configuration following HA standards"""

    def __init__(self):
        self.config = []

    def add_device(self, device_config, scan_results=None):
        """
        Add a device to the configuration

        Args:
            device_config: dict with name, manufacturer, model, host, port, etc.
            scan_results: optional scan results from ModbusScanner

        Returns:
            bool: True if device was added successfully
        """
        manufacturer = device_config.get('manufacturer')
        model = device_config.get('model')
        profile = get_device_profile(manufacturer, model)

        if not profile:
            logger.error(f"No profile found for {manufacturer} {model}")
            return False

        # Create modbus hub configuration following HA documentation
        device = {
            'name': device_config.get('name', f"{manufacturer}_{model}").lower().replace(' ', '_'),
            'type': 'tcp',  # Default to TCP
            'host': device_config['host'],
            'port': device_config.get('port', profile.get('port', 502)),
            'timeout': profile.get('timeout', 5),
        }

        # Add optional delay parameter if needed
        if profile.get('delay'):
            device['delay'] = profile['delay']

        # Add message_wait_milliseconds if needed
        if profile.get('message_wait_milliseconds'):
            device['message_wait_milliseconds'] = profile['message_wait_milliseconds']

        # Generate entities based on profile
        self._add_entities(device, profile, device_config, scan_results)

        # Only add device if it has at least one entity
        if self._has_entities(device):
            self.config.append(device)
            logger.info(f"Added device: {device['name']} with {self._count_entities(device)} entities")
            return True
        else:
            logger.warning(f"Device {device['name']} has no entities, skipping")
            return False

    def _has_entities(self, device):
        """Check if device has at least one entity"""
        entity_types = ['sensors', 'binary_sensors', 'switches', 'climates', 'covers', 'fans', 'lights']
        return any(device.get(entity_type) for entity_type in entity_types)

    def _count_entities(self, device):
        """Count total number of entities in device"""
        entity_types = ['sensors', 'binary_sensors', 'switches', 'climates', 'covers', 'fans', 'lights']
        return sum(len(device.get(entity_type, [])) for entity_type in entity_types)

    def _add_entities(self, device, profile, device_config, scan_results):
        """Add entities (sensors, switches, etc.) to device following HA Modbus documentation"""
        registers = profile.get('registers', {})
        slave_id = device_config.get('slave_id', 1)

        # Initialize entity lists
        sensors = []
        binary_sensors = []
        switches = []

        # Generate entities from profile
        for register_name, register_config in registers.items():
            entity_type = register_config.get('type')

            if entity_type == 'sensor':
                sensor = self._create_sensor(register_name, register_config, slave_id)
                if sensor:
                    sensors.append(sensor)

            elif entity_type == 'binary_sensor':
                binary_sensor = self._create_binary_sensor(register_name, register_config, slave_id)
                if binary_sensor:
                    binary_sensors.append(binary_sensor)

            elif entity_type == 'switch':
                switch = self._create_switch(register_name, register_config, slave_id)
                if switch:
                    switches.append(switch)

        # Add entity lists to device if not empty
        if sensors:
            device['sensors'] = sensors
        if binary_sensors:
            device['binary_sensors'] = binary_sensors
        if switches:
            device['switches'] = switches

    def _create_sensor(self, register_name, register_config, slave_id):
        """
        Create sensor configuration following HA Modbus documentation

        HA Documentation:
        - name: sensor_name (Required)
        - address: register address (Required)
        - input_type: holding (default) or input
        - data_type: int16 (default), uint16, int32, uint32, float32, etc.
        - scale: scale factor
        - offset: offset value
        - precision: number of decimals
        - unit_of_measurement: unit
        - device_class: sensor device class
        - state_class: measurement, total, total_increasing
        - scan_interval: update interval in seconds
        - slave: slave address (default 1)
        """
        address = register_config.get('start_address')
        if address is None:
            logger.warning(f"Sensor {register_name} has no start_address")
            return None

        sensor = {
            'name': register_name.replace('_', ' ').title(),
            'address': address,
            'slave': slave_id,
        }

        # Input type (holding or input register)
        input_type = register_config.get('input_type', 'holding')
        if input_type in ['holding', 'input']:
            sensor['input_type'] = input_type

        # Data type
        data_type = register_config.get('data_type', 'int16')
        sensor['data_type'] = data_type

        # Scale and offset
        if 'scale' in register_config:
            sensor['scale'] = register_config['scale']
        if 'offset' in register_config:
            sensor['offset'] = register_config['offset']

        # Precision
        if 'precision' in register_config:
            sensor['precision'] = register_config['precision']

        # Unit of measurement
        if 'unit_of_measurement' in register_config:
            sensor['unit_of_measurement'] = register_config['unit_of_measurement']

        # Device class
        if 'device_class' in register_config:
            sensor['device_class'] = register_config['device_class']

        # State class
        if 'state_class' in register_config:
            sensor['state_class'] = register_config['state_class']

        # Scan interval
        if 'scan_interval' in register_config:
            sensor['scan_interval'] = register_config['scan_interval']

        # Count (number of registers)
        if 'count' in register_config and register_config['count'] > 1:
            sensor['count'] = register_config['count']

        return sensor

    def _create_binary_sensor(self, register_name, register_config, slave_id):
        """
        Create binary sensor configuration following HA Modbus documentation

        HA Documentation:
        - name: sensor_name (Required)
        - address: coil/discrete input address (Required)
        - input_type: coil (default) or discrete_input
        - device_class: binary sensor device class
        - scan_interval: update interval in seconds
        - slave: slave address (default 1)
        """
        address = register_config.get('start_address')
        if address is None:
            logger.warning(f"Binary sensor {register_name} has no start_address")
            return None

        binary_sensor = {
            'name': register_name.replace('_', ' ').title(),
            'address': address,
            'slave': slave_id,
        }

        # Input type (coil or discrete_input)
        input_type = register_config.get('input_type', 'discrete_input')
        if input_type in ['coil', 'discrete_input']:
            binary_sensor['input_type'] = input_type

        # Device class
        if 'device_class' in register_config:
            binary_sensor['device_class'] = register_config['device_class']

        # Scan interval
        if 'scan_interval' in register_config:
            binary_sensor['scan_interval'] = register_config['scan_interval']

        return binary_sensor

    def _create_switch(self, register_name, register_config, slave_id):
        """
        Create switch configuration following HA Modbus documentation

        HA Documentation:
        - name: switch_name (Required)
        - address: coil/register address (Required)
        - write_type: coil (default), holding, coils, holdings
        - command_on: value to write to turn on (default 1)
        - command_off: value to write to turn off (default 0)
        - verify: optional verification configuration
        - slave: slave address (default 1)
        """
        address = register_config.get('start_address')
        if address is None:
            logger.warning(f"Switch {register_name} has no start_address")
            return None

        switch = {
            'name': register_name.replace('_', ' ').title(),
            'address': address,
            'slave': slave_id,
        }

        # Write type
        write_type = register_config.get('write_type', 'coil')
        if write_type in ['coil', 'holding', 'coils', 'holdings']:
            switch['write_type'] = write_type

        # Command values
        if 'command_on' in register_config:
            switch['command_on'] = register_config['command_on']
        if 'command_off' in register_config:
            switch['command_off'] = register_config['command_off']

        # Scan interval
        if 'scan_interval' in register_config:
            switch['scan_interval'] = register_config['scan_interval']

        # Add verification if needed
        if register_config.get('verify', False):
            switch['verify'] = {}

        return switch

    def generate_yaml(self):
        """
        Generate YAML configuration string for Home Assistant

        Returns:
            str: YAML configuration following HA Modbus documentation format
        """
        if not self.config:
            logger.warning("No devices configured")
            return None

        # Create modbus configuration with proper structure
        modbus_config = {
            'modbus': self.config
        }

        # Generate YAML with custom formatting
        yaml_str = yaml.dump(
            modbus_config,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            indent=2
        )

        # Add header comment
        header = """# Home Assistant Modbus Configuration
# Generated by Universal Modbus Configurator
# Based on official Home Assistant Modbus Integration documentation
# https://www.home-assistant.io/integrations/modbus/
#
# To use this configuration:
# 1. This file is automatically saved as 'modbus.yaml' in your Home Assistant config directory
# 2. Add the following line to your configuration.yaml:
#    modbus: !include modbus.yaml
# 3. Restart Home Assistant or reload the Modbus integration
#
"""

        return header + yaml_str

    def save_to_file(self, file_path):
        """
        Save configuration to YAML file

        Args:
            file_path: Path where to save the configuration

        Returns:
            bool: True if successful, False otherwise
        """
        yaml_content = self.generate_yaml()

        if not yaml_content:
            logger.error("No configuration to save")
            return False

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(yaml_content)
            logger.info(f"Configuration saved to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {e}", exc_info=True)
            return False

    def clear(self):
        """Clear all configuration"""
        self.config = []

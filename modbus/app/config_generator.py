"""
Configuration generator for Home Assistant Modbus integration
Based on official Home Assistant Modbus Integration documentation
"""
import yaml
import logging
import os
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
        device_model = device_config.get('model', '')

        # Get I/O configuration from device_config (user-defined counts)
        io_config = device_config.get('io_config', {})
        digital_inputs_count = io_config.get('digital_inputs', 0)
        digital_outputs_count = io_config.get('digital_outputs', 0)
        analog_inputs_count = io_config.get('analog_inputs', 0)
        analog_outputs_count = io_config.get('analog_outputs', 0)
        network_inputs_count = io_config.get('network_inputs', 0)
        network_outputs_count = io_config.get('network_outputs', 0)

        # Initialize entity lists
        sensors = []
        binary_sensors = []
        switches = []

        # Generate digital inputs (binary_sensors) based on user-defined count
        if digital_inputs_count > 0:
            for i in range(1, digital_inputs_count + 1):
                binary_sensor = {
                    'name': f"{device['name']}_I{i}",
                    'unique_id': f"ID_{device['name']}_I{i}",
                    'address': i,
                    'input_type': 'discrete_input',
                    'slave': slave_id,
                    'scan_interval': 1
                }
                binary_sensors.append(binary_sensor)

        # Generate digital outputs (switches) based on user-defined count
        if digital_outputs_count > 0:
            # LOGO! 8 addressing scheme (based on reference modbus.yaml)
            # Write address: 1-N (direct output number)
            # Verify address: 8198 + output_number (for state verification)
            # Sync flag: Forces state synchronization (prevents desync)
            enable_sync = io_config.get('enable_sync', False)
            for i in range(1, digital_outputs_count + 1):
                switch = {
                    'name': f"{device['name']}_Q{i}",
                    'unique_id': f"ID_{device['name']}_Q{i}",
                    'address': i,  # Write to output 1-N
                    'write_type': 'coil',
                    'slave': slave_id,
                    'command_on': 1,
                    'command_off': 0,
                    'verify': {
                        'input_type': 'coil',
                        'address': 8198 + i,  # Verify at 8199, 8200, 8201, etc.
                        'state_on': 1,
                        'state_off': 0
                    }
                }
                # Add sync flag if enabled (prevents desynchronization)
                if enable_sync:
                    switch['verify']['sync'] = True
                switches.append(switch)

        # Generate analog inputs (sensors) based on user-defined count
        if analog_inputs_count > 0:
            for i in range(1, analog_inputs_count + 1):
                sensor = {
                    'name': f"{device['name']}_AI{i}",
                    'unique_id': f"ID_{device['name']}_AI{i}",
                    'address': i,
                    'input_type': 'input',
                    'data_type': 'uint16',
                    'slave': slave_id,
                    'scan_interval': 5
                }
                sensors.append(sensor)

        # Generate analog outputs (sensors with write capability) based on user-defined count
        if analog_outputs_count > 0:
            # LOGO! uses base address 528 (0x0210) for analog outputs
            base_address = 528
            for i in range(1, analog_outputs_count + 1):
                sensor = {
                    'name': f"{device['name']}_AQ{i}",
                    'unique_id': f"ID_{device['name']}_AQ{i}",
                    'address': base_address + (i - 1),
                    'input_type': 'holding',
                    'data_type': 'uint16',
                    'slave': slave_id,
                    'scan_interval': 5
                }
                sensors.append(sensor)

        # Generate network inputs (NI) - LOGO-to-LOGO communication (binary_sensors)
        # IMPORTANT: Network I/O (NI/NQ) is ONLY available in LOGO! 8, NOT in LOGO! v7 (0BA7)
        if network_inputs_count > 0 and device_model in ["LOGO! 8", "LOGO! 8 (0BA8)"]:
            # Network inputs start at address 0 (NI1-NI64)
            for i in range(1, network_inputs_count + 1):
                binary_sensor = {
                    'name': f"{device['name']}_NI{i}",
                    'unique_id': f"ID_{device['name']}_NI{i}",
                    'address': i - 1,  # NI1 starts at address 0
                    'input_type': 'discrete_input',
                    'slave': slave_id,
                    'scan_interval': 2
                }
                binary_sensors.append(binary_sensor)

        # Generate network outputs (NQ) - LOGO-to-LOGO communication (switches)
        # IMPORTANT: Network I/O (NI/NQ) is ONLY available in LOGO! 8, NOT in LOGO! v7 (0BA7)
        if network_outputs_count > 0 and device_model in ["LOGO! 8", "LOGO! 8 (0BA8)"]:
            # Network outputs start at address 0 (NQ1-NQ64)
            enable_sync = io_config.get('enable_sync', False)
            for i in range(1, network_outputs_count + 1):
                switch = {
                    'name': f"{device['name']}_NQ{i}",
                    'unique_id': f"ID_{device['name']}_NQ{i}",
                    'address': i - 1,  # NQ1 starts at address 0
                    'write_type': 'coil',
                    'slave': slave_id,
                    'command_on': 1,
                    'command_off': 0,
                    'verify': {
                        'input_type': 'coil',
                        'address': i - 1,
                        'state_on': 1,
                        'state_off': 0
                    }
                }
                # Add sync flag if enabled (prevents desynchronization)
                if enable_sync:
                    switch['verify']['sync'] = True
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

        # Count (number of registers) - ONLY if data_type is NOT specified
        # Note: count and data_type are mutually exclusive in HA Modbus
        # When data_type is specified, HA automatically determines register count
        if 'count' in register_config and register_config['count'] > 1 and 'data_type' not in sensor:
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

        # Generate YAML directly from config list (no 'modbus:' wrapper)
        # The 'modbus:' key is already in configuration.yaml via !include
        yaml_str = yaml.dump(
            self.config,
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
# IMPORTANT: This file should NOT contain 'modbus:' as root key since it's
# already defined in configuration.yaml via the !include directive.
#
"""

        return header + yaml_str

    def _merge_with_existing(self, file_path):
        """
        Merge new configuration with existing manual changes

        This function loads the existing modbus.yaml, compares it with the new
        configuration, and preserves any manual changes made by the user.

        Args:
            file_path: Path to existing configuration file

        Returns:
            None (modifies self.config in place)
        """
        if not os.path.exists(file_path):
            logger.info("No existing configuration file to merge with")
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Load existing config (skip comment lines)
            existing_config = yaml.safe_load(content)

            if not existing_config or not isinstance(existing_config, list):
                logger.warning("Existing configuration is empty or invalid")
                return

            # Create a mapping of existing devices by name
            existing_devices = {dev.get('name'): dev for dev in existing_config if dev.get('name')}

            # Merge each new device with existing one if found
            for new_device in self.config:
                device_name = new_device.get('name')

                if device_name in existing_devices:
                    logger.info(f"Merging device: {device_name}")
                    existing_device = existing_devices[device_name]

                    # Merge each entity type
                    for entity_type in ['sensors', 'binary_sensors', 'switches']:
                        if entity_type in new_device:
                            new_device[entity_type] = self._merge_entities(
                                new_device[entity_type],
                                existing_device.get(entity_type, []),
                                entity_type
                            )

            logger.info("Configuration merge completed")

        except Exception as e:
            logger.error(f"Error merging configurations: {e}", exc_info=True)
            # Continue with new config if merge fails

    def _merge_entities(self, new_entities, existing_entities, entity_type):
        """
        Merge new entities with existing ones, preserving manual changes

        Args:
            new_entities: List of newly generated entities
            existing_entities: List of entities from existing config
            entity_type: Type of entity (sensors, binary_sensors, switches)

        Returns:
            List of merged entities
        """
        # Create mapping of existing entities by address
        existing_by_address = {}
        for entity in existing_entities:
            address = entity.get('address')
            if address is not None:
                existing_by_address[address] = entity

        merged_entities = []

        for new_entity in new_entities:
            address = new_entity.get('address')

            # If entity exists at this address, merge with existing
            if address in existing_by_address:
                existing_entity = existing_by_address[address]
                merged_entity = new_entity.copy()

                # Preserve user-customized fields
                preserve_fields = [
                    'name',              # Custom names
                    'scale',             # Custom scale factors
                    'offset',            # Custom offset values
                    'unit_of_measurement',  # Custom units
                    'device_class',      # Custom device classes
                    'precision',         # Custom precision
                    'scan_interval',     # Custom scan intervals
                    'state_class',       # Custom state classes
                    'command_on',        # Custom on command
                    'command_off',       # Custom off command
                    'verify',            # Custom verify configuration (for switches)
                ]

                for field in preserve_fields:
                    if field in existing_entity:
                        # Check if value was actually customized (different from default)
                        existing_value = existing_entity[field]
                        new_value = merged_entity.get(field)

                        # If values differ, preserve the existing (manually changed) value
                        if existing_value != new_value:
                            merged_entity[field] = existing_value
                            logger.debug(f"Preserved '{field}' for {merged_entity.get('name')}: {existing_value}")

                merged_entities.append(merged_entity)
            else:
                # New entity, add as is
                merged_entities.append(new_entity)

        return merged_entities

    def save_to_file(self, file_path, merge_existing=True):
        """
        Save configuration to YAML file

        Args:
            file_path: Path where to save the configuration
            merge_existing: If True, merge with existing configuration to preserve manual changes

        Returns:
            bool: True if successful, False otherwise
        """
        # Merge with existing configuration if requested
        if merge_existing:
            self._merge_with_existing(file_path)

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

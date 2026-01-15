"""
Configuration generator for Home Assistant Modbus integration
"""
import os
import yaml
import logging
from device_profiles import get_device_profile

logger = logging.getLogger(__name__)


class ModbusConfigGenerator:
    """Generator for Modbus YAML configuration"""

    def __init__(self):
        self.config = []

    def add_device(self, device_config, scan_results=None):
        """
        Add a device to the configuration

        Args:
            device_config: dict with name, manufacturer, model, host, port, etc.
            scan_results: optional scan results from ModbusScanner
        """
        manufacturer = device_config.get('manufacturer')
        model = device_config.get('model')
        profile = get_device_profile(manufacturer, model)

        if not profile:
            logger.error(f"No profile found for {manufacturer} {model}")
            return False

        device = {
            'name': device_config.get('name', f"{manufacturer}_{model}"),
            'type': 'tcp',
            'host': device_config['host'],
            'port': device_config.get('port', profile.get('port', 502)),
            'timeout': profile.get('timeout', 5)
        }

        # Add slave ID if provided
        if 'slave_id' in device_config and device_config['slave_id']:
            device['slave'] = device_config['slave_id']

        # Generate entities based on profile
        self._add_entities(device, profile, device_config, scan_results)

        self.config.append(device)
        logger.info(f"Added device: {device['name']}")
        return True

    def _add_entities(self, device, profile, device_config, scan_results):
        """Add entities (sensors, switches, etc.) to device"""
        registers = profile.get('registers', {})
        custom_entities = device_config.get('entities', [])

        # Initialize entity lists
        sensors = []
        binary_sensors = []
        switches = []
        numbers = []

        # Add custom entities if provided
        if custom_entities:
            for entity in custom_entities:
                entity_type = entity.get('type')
                if entity_type == 'sensor':
                    sensors.append(self._create_sensor(entity, profile))
                elif entity_type == 'binary_sensor':
                    binary_sensors.append(self._create_binary_sensor(entity))
                elif entity_type == 'switch':
                    switches.append(self._create_switch(entity))
                elif entity_type == 'number':
                    numbers.append(self._create_number(entity))
        else:
            # Auto-generate entities based on profile and scan results
            if scan_results:
                sensors, binary_sensors, switches, numbers = self._generate_from_scan(
                    scan_results, profile, device_config
                )
            else:
                sensors, binary_sensors, switches, numbers = self._generate_from_profile(
                    registers, profile, device_config
                )

        # Add entity lists to device if not empty
        if sensors:
            device['sensors'] = sensors
        if binary_sensors:
            device['binary_sensors'] = binary_sensors
        if switches:
            device['switches'] = switches
        if numbers:
            device['numbers'] = numbers

    def _generate_from_scan(self, scan_results, profile, device_config):
        """Generate entities from scan results"""
        sensors = []
        binary_sensors = []
        switches = []
        numbers = []

        device_name = device_config.get('name', 'Device')

        # Input registers -> sensors
        for reg in scan_results.get('input_registers', []):
            sensors.append({
                'name': f"{device_name} Input {reg['address']}",
                'address': reg['address'],
                'input_type': 'input',
                'data_type': 'uint16',
                'scan_interval': 5
            })

        # Holding registers -> sensors
        for reg in scan_results.get('holding_registers', []):
            sensors.append({
                'name': f"{device_name} Holding {reg['address']}",
                'address': reg['address'],
                'input_type': 'holding',
                'data_type': 'uint16',
                'scan_interval': 5
            })

        # Discrete inputs -> binary sensors
        for reg in scan_results.get('discrete_inputs', []):
            binary_sensors.append({
                'name': f"{device_name} Input {reg['address']}",
                'address': reg['address'],
                'input_type': 'discrete_input',
                'scan_interval': 1
            })

        # Coils -> switches
        for reg in scan_results.get('coils', []):
            switches.append({
                'name': f"{device_name} Output {reg['address']}",
                'address': reg['address'],
                'write_type': 'coil',
                'scan_interval': 1
            })

        return sensors, binary_sensors, switches, numbers

    def _generate_from_profile(self, registers, profile, device_config):
        """Generate entities from device profile"""
        sensors = []
        binary_sensors = []
        switches = []
        numbers = []

        device_name = device_config.get('name', 'Device')
        count = device_config.get('register_count', 'auto')

        # Generate based on register types in profile
        for reg_name, reg_config in registers.items():
            entity_type = reg_config.get('type')
            start_addr = reg_config.get('start_address', 0)
            reg_count = reg_config.get('count', 10) if count == 'auto' else count

            if entity_type == 'sensor':
                for i in range(reg_count):
                    sensors.append(self._create_sensor({
                        'name': f"{device_name} {reg_name} {i+1}",
                        'address': start_addr + i,
                        'input_type': reg_config.get('input_type', 'input'),
                        'data_type': reg_config.get('data_type', 'uint16'),
                        'scan_interval': reg_config.get('scan_interval', 5)
                    }, profile))

            elif entity_type == 'binary_sensor':
                for i in range(reg_count):
                    binary_sensors.append(self._create_binary_sensor({
                        'name': f"{device_name} {reg_name} {i+1}",
                        'address': start_addr + i,
                        'input_type': reg_config.get('input_type', 'discrete_input'),
                        'scan_interval': reg_config.get('scan_interval', 1)
                    }))

            elif entity_type == 'switch':
                for i in range(reg_count):
                    switches.append(self._create_switch({
                        'name': f"{device_name} {reg_name} {i+1}",
                        'address': start_addr + i,
                        'write_type': reg_config.get('write_type', 'coil'),
                        'scan_interval': reg_config.get('scan_interval', 1)
                    }))

            elif entity_type == 'number':
                for i in range(reg_count):
                    numbers.append(self._create_number({
                        'name': f"{device_name} {reg_name} {i+1}",
                        'address': start_addr + i,
                        'input_type': reg_config.get('input_type', 'holding'),
                        'data_type': reg_config.get('data_type', 'uint16'),
                        'scan_interval': reg_config.get('scan_interval', 5)
                    }))

        return sensors, binary_sensors, switches, numbers

    def _create_sensor(self, entity, profile=None):
        """Create sensor entity"""
        sensor = {
            'name': entity['name'],
            'address': entity['address'],
            'input_type': entity.get('input_type', 'input'),
            'data_type': entity.get('data_type', 'uint16'),
            'scan_interval': entity.get('scan_interval', 5)
        }

        # Add optional parameters
        if 'unit_of_measurement' in entity:
            sensor['unit_of_measurement'] = entity['unit_of_measurement']
        if 'scale' in entity:
            sensor['scale'] = entity['scale']
        if 'offset' in entity:
            sensor['offset'] = entity['offset']
        if 'device_class' in entity:
            sensor['device_class'] = entity['device_class']
        if 'precision' in entity:
            sensor['precision'] = entity['precision']
        if 'state_class' in entity:
            sensor['state_class'] = entity['state_class']

        return sensor

    def _create_binary_sensor(self, entity):
        """Create binary sensor entity"""
        return {
            'name': entity['name'],
            'address': entity['address'],
            'input_type': entity.get('input_type', 'discrete_input'),
            'scan_interval': entity.get('scan_interval', 1)
        }

    def _create_switch(self, entity):
        """Create switch entity"""
        return {
            'name': entity['name'],
            'address': entity['address'],
            'write_type': entity.get('write_type', 'coil'),
            'scan_interval': entity.get('scan_interval', 1)
        }

    def _create_number(self, entity):
        """Create number entity"""
        number = {
            'name': entity['name'],
            'address': entity['address'],
            'input_type': entity.get('input_type', 'holding'),
            'data_type': entity.get('data_type', 'uint16'),
            'scan_interval': entity.get('scan_interval', 5)
        }

        # Add optional parameters
        if 'min' in entity:
            number['min'] = entity['min']
        if 'max' in entity:
            number['max'] = entity['max']
        if 'step' in entity:
            number['step'] = entity['step']

        return number

    def generate_yaml(self, output_path=None):
        """Generate YAML configuration file"""
        if not self.config:
            logger.warning("No devices configured")
            return ""

        # Create YAML structure
        yaml_config = self.config

        # Convert to YAML string
        yaml_str = yaml.dump(
            yaml_config,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True
        )

        # Add header comment
        header = """# ==========================================
# Auto-generated Modbus Configuration
# Generated by Universal Modbus Configurator
# ==========================================
#
"""
        yaml_str = header + yaml_str

        # Write to file if path provided
        if output_path:
            try:
                # Ensure directory exists
                output_dir = os.path.dirname(output_path)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
                    logger.info(f"Created directory: {output_dir}")

                with open(output_path, 'w') as f:
                    f.write(yaml_str)
                logger.info(f"Configuration written to {output_path}")
            except Exception as e:
                logger.error(f"Error writing configuration: {e}")
                raise

        return yaml_str

    def clear(self):
        """Clear configuration"""
        self.config = []

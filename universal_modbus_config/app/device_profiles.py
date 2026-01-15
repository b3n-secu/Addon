"""
Device profiles for different manufacturers and models
"""

DEVICE_PROFILES = {
    "Siemens": {
        "LOGO! 8": {
            "port": 510,
            "timeout": 5,
            "registers": {
                "analog_inputs": {
                    "type": "sensor",
                    "start_address": 1,
                    "count": 8,
                    "input_type": "input",
                    "data_type": "uint16",
                    "scan_interval": 5
                },
                "digital_inputs": {
                    "type": "binary_sensor",
                    "start_address": 1,
                    "count": 24,
                    "input_type": "discrete_input",
                    "scan_interval": 1
                },
                "digital_outputs": {
                    "type": "switch",
                    "start_address": 8193,  # 0x2001
                    "count": 20,
                    "write_type": "coil",
                    "scan_interval": 1
                },
                "analog_outputs": {
                    "type": "number",
                    "start_address": 528,  # 0x0210
                    "count": 8,
                    "input_type": "holding",
                    "data_type": "uint16",
                    "scan_interval": 5
                }
            },
            "presets": {
                "temperature_sensor": {
                    "unit_of_measurement": "°C",
                    "scale": 0.081,
                    "offset": -20.0,
                    "device_class": "temperature",
                    "precision": 1,
                    "state_class": "measurement"
                },
                "humidity_sensor": {
                    "unit_of_measurement": "%",
                    "scale": 0.125,
                    "device_class": "humidity",
                    "precision": 1,
                    "state_class": "measurement"
                },
                "power_sensor": {
                    "unit_of_measurement": "kW",
                    "scale": 1,
                    "device_class": "power",
                    "precision": 1,
                    "state_class": "measurement"
                }
            }
        },
        "LOGO! 7": {
            "port": 510,
            "timeout": 5,
            "registers": {
                "analog_inputs": {
                    "type": "sensor",
                    "start_address": 1,
                    "count": 8,
                    "input_type": "input",
                    "data_type": "uint16",
                    "scan_interval": 5
                },
                "digital_inputs": {
                    "type": "binary_sensor",
                    "start_address": 1,
                    "count": 24,
                    "input_type": "discrete_input",
                    "scan_interval": 1
                },
                "digital_outputs": {
                    "type": "switch",
                    "start_address": 8193,
                    "count": 16,
                    "write_type": "coil",
                    "scan_interval": 1
                }
            }
        }
    },
    "Schneider Electric": {
        "Modicon M221": {
            "port": 502,
            "timeout": 5,
            "registers": {
                "analog_inputs": {
                    "type": "sensor",
                    "start_address": 0,
                    "count": 8,
                    "input_type": "input",
                    "data_type": "int16",
                    "scan_interval": 5
                },
                "digital_inputs": {
                    "type": "binary_sensor",
                    "start_address": 0,
                    "count": 16,
                    "input_type": "discrete_input",
                    "scan_interval": 1
                },
                "holding_registers": {
                    "type": "sensor",
                    "start_address": 0,
                    "count": 100,
                    "input_type": "holding",
                    "data_type": "int16",
                    "scan_interval": 5
                }
            }
        }
    },
    "Generic": {
        "Modbus TCP": {
            "port": 502,
            "timeout": 5,
            "registers": {
                "holding_registers": {
                    "type": "sensor",
                    "start_address": 0,
                    "count": 100,
                    "input_type": "holding",
                    "data_type": "int16",
                    "scan_interval": 5
                },
                "input_registers": {
                    "type": "sensor",
                    "start_address": 0,
                    "count": 100,
                    "input_type": "input",
                    "data_type": "int16",
                    "scan_interval": 5
                },
                "coils": {
                    "type": "switch",
                    "start_address": 0,
                    "count": 100,
                    "write_type": "coil",
                    "scan_interval": 1
                },
                "discrete_inputs": {
                    "type": "binary_sensor",
                    "start_address": 0,
                    "count": 100,
                    "input_type": "discrete_input",
                    "scan_interval": 1
                }
            }
        }
    },
    "ABB": {
        "AC500": {
            "port": 502,
            "timeout": 5,
            "registers": {
                "analog_inputs": {
                    "type": "sensor",
                    "start_address": 0,
                    "count": 16,
                    "input_type": "input",
                    "data_type": "int16",
                    "scan_interval": 5
                },
                "digital_inputs": {
                    "type": "binary_sensor",
                    "start_address": 0,
                    "count": 32,
                    "input_type": "discrete_input",
                    "scan_interval": 1
                },
                "digital_outputs": {
                    "type": "switch",
                    "start_address": 0,
                    "count": 32,
                    "write_type": "coil",
                    "scan_interval": 1
                }
            }
        }
    },
    "Wago": {
        "750 Series": {
            "port": 502,
            "timeout": 5,
            "registers": {
                "inputs": {
                    "type": "binary_sensor",
                    "start_address": 0,
                    "count": 64,
                    "input_type": "discrete_input",
                    "scan_interval": 1
                },
                "outputs": {
                    "type": "switch",
                    "start_address": 512,
                    "count": 64,
                    "write_type": "coil",
                    "scan_interval": 1
                },
                "analog_inputs": {
                    "type": "sensor",
                    "start_address": 0,
                    "count": 32,
                    "input_type": "input",
                    "data_type": "int16",
                    "scan_interval": 5
                }
            }
        }
    }
}


def get_manufacturers():
    """Get list of available manufacturers"""
    return list(DEVICE_PROFILES.keys())


def get_models(manufacturer):
    """Get list of models for a manufacturer"""
    if manufacturer in DEVICE_PROFILES:
        return list(DEVICE_PROFILES[manufacturer].keys())
    return []


def get_device_profile(manufacturer, model):
    """Get device profile for manufacturer and model"""
    if manufacturer in DEVICE_PROFILES:
        if model in DEVICE_PROFILES[manufacturer]:
            return DEVICE_PROFILES[manufacturer][model]
    return None

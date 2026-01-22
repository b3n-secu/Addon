"""
Device profiles for different manufacturers and models
"""

DEVICE_PROFILES = {
    "Siemens": {
        "LOGO! 8 (0BA8)": {
            "port": 510,
            "timeout": 5,
            "note": "LOGO! 8 with native Modbus TCP support. IMPORTANT: LOGO! v7/0BA7 does NOT support Modbus - see LOGO_COMPATIBILITY.md",
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
                },
                "network_inputs": {
                    "type": "binary_sensor",
                    "start_address": 0,  # NI1-NI64
                    "count": 64,
                    "input_type": "discrete_input",
                    "scan_interval": 2,
                    "note": "Network Inputs for LOGO-to-LOGO communication (LOGO! 8 only)"
                },
                "network_outputs": {
                    "type": "switch",
                    "start_address": 0,  # NQ1-NQ64
                    "count": 64,
                    "write_type": "coil",
                    "scan_interval": 2,
                    "note": "Network Outputs for LOGO-to-LOGO communication (LOGO! 8 only)"
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
        "S7 PLC": {
            "port": 502,
            "timeout": 5,
            "note": "S7 PLCs require MB_SERVER configuration. Default generic Modbus mapping.",
            "registers": {
                "holding_registers": {
                    "type": "sensor",
                    "start_address": 0,
                    "count": 100,
                    "input_type": "holding",
                    "data_type": "int16",
                    "scan_interval": 5,
                    "note": "Maps to DB words via MB_SERVER"
                },
                "input_registers": {
                    "type": "sensor",
                    "start_address": 0,
                    "count": 100,
                    "input_type": "input",
                    "data_type": "int16",
                    "scan_interval": 5,
                    "note": "Read-only registers"
                },
                "coils": {
                    "type": "switch",
                    "start_address": 0,
                    "count": 100,
                    "write_type": "coil",
                    "scan_interval": 1,
                    "note": "Maps to Q outputs"
                },
                "discrete_inputs": {
                    "type": "binary_sensor",
                    "start_address": 0,
                    "count": 100,
                    "input_type": "discrete_input",
                    "scan_interval": 1,
                    "note": "Read-only inputs"
                }
            },
            "presets": {
                "generic_sensor": {
                    "unit_of_measurement": "",
                    "data_type": "int16",
                    "precision": 2,
                    "state_class": "measurement"
                }
            }
        },
        "S7-300": {
            "port": 102,
            "timeout": 5,
            "note": "S7-300 uses ISO-TSAP protocol on Port 102. Requires CP module for Modbus.",
            "registers": {
                "holding_registers": {
                    "type": "sensor",
                    "start_address": 0,
                    "count": 100,
                    "input_type": "holding",
                    "data_type": "int16",
                    "scan_interval": 5
                },
                "coils": {
                    "type": "switch",
                    "start_address": 0,
                    "count": 100,
                    "write_type": "coil",
                    "scan_interval": 1
                }
            }
        },
        "S7-400": {
            "port": 102,
            "timeout": 5,
            "note": "S7-400 uses ISO-TSAP protocol on Port 102. Requires CP module for Modbus.",
            "registers": {
                "holding_registers": {
                    "type": "sensor",
                    "start_address": 0,
                    "count": 100,
                    "input_type": "holding",
                    "data_type": "int16",
                    "scan_interval": 5
                },
                "coils": {
                    "type": "switch",
                    "start_address": 0,
                    "count": 100,
                    "write_type": "coil",
                    "scan_interval": 1
                }
            }
        },
        "S7-1200": {
            "port": 502,
            "timeout": 5,
            "note": "S7-1200 with built-in Modbus TCP server (MB_SERVER). Configure via TIA Portal.",
            "registers": {
                "holding_registers": {
                    "type": "sensor",
                    "start_address": 0,
                    "count": 100,
                    "input_type": "holding",
                    "data_type": "int16",
                    "scan_interval": 5,
                    "note": "DB data blocks"
                },
                "coils": {
                    "type": "switch",
                    "start_address": 0,
                    "count": 1024,
                    "write_type": "coil",
                    "scan_interval": 1,
                    "note": "Q0.0 to Q1023.7"
                },
                "discrete_inputs": {
                    "type": "binary_sensor",
                    "start_address": 0,
                    "count": 1024,
                    "input_type": "discrete_input",
                    "scan_interval": 1,
                    "note": "I0.0 to I1023.7"
                }
            }
        },
        "S7-1500": {
            "port": 502,
            "timeout": 5,
            "note": "S7-1500 with built-in Modbus TCP server (MB_SERVER). Configure via TIA Portal.",
            "registers": {
                "holding_registers": {
                    "type": "sensor",
                    "start_address": 0,
                    "count": 100,
                    "input_type": "holding",
                    "data_type": "int16",
                    "scan_interval": 5,
                    "note": "DB data blocks"
                },
                "coils": {
                    "type": "switch",
                    "start_address": 0,
                    "count": 1024,
                    "write_type": "coil",
                    "scan_interval": 1,
                    "note": "Q0.0 to Q1023.7"
                },
                "discrete_inputs": {
                    "type": "binary_sensor",
                    "start_address": 0,
                    "count": 1024,
                    "input_type": "discrete_input",
                    "scan_interval": 1,
                    "note": "I0.0 to I1023.7"
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

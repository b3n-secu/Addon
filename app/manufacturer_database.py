"""
Manufacturer Database - Port and Protocol Information
Contains default ports, protocols, and device-specific information for industrial automation manufacturers
"""

# Manufacturer port database
MANUFACTURER_PORTS = {
    'Siemens': {
        'name': 'Siemens',
        'devices': {
            'LOGO! 8': {
                'protocols': ['Modbus TCP', 'S7comm'],
                'ports': {
                    'modbus_tcp': 510,  # LOGO! 8 uses 510 by default
                    's7comm': 102
                },
                'slave_id_range': (1, 247),
                'notes': 'LOGO! 8 verwendet Port 510 für Modbus TCP. S7comm über Port 102.'
            },
            'LOGO! 0BA7': {
                'protocols': ['S7comm'],
                'ports': {
                    's7comm': 102
                },
                'slave_id_range': (1, 1),
                'notes': 'LOGO! 0BA7 unterstützt nur S7comm, kein Modbus TCP.'
            },
            'S7-1200': {
                'protocols': ['Modbus TCP', 'S7comm', 'PROFINET'],
                'ports': {
                    'modbus_tcp': 502,
                    's7comm': 102,
                    'profinet': [34962, 34963, 34964]
                },
                'slave_id_range': (1, 247),
                'notes': 'PUT/GET-Kommunikation muss in der Projektierung aktiviert sein.'
            },
            'S7-1500': {
                'protocols': ['Modbus TCP', 'S7comm', 'PROFINET'],
                'ports': {
                    'modbus_tcp': 502,
                    's7comm': 102,
                    'profinet': [34962, 34963, 34964]
                },
                'slave_id_range': (1, 247),
                'notes': 'PUT/GET-Kommunikation muss in der Projektierung aktiviert sein.'
            },
            'S7-300': {
                'protocols': ['S7comm', 'PROFINET'],
                'ports': {
                    's7comm': 102,
                    'profinet': [34962, 34963, 34964]
                },
                'notes': 'Ältere Serie, meist nur S7comm.'
            },
            'S7-400': {
                'protocols': ['S7comm', 'PROFINET'],
                'ports': {
                    's7comm': 102,
                    'profinet': [34962, 34963, 34964]
                },
                'notes': 'Ältere Serie, meist nur S7comm.'
            }
        }
    },
    'Schneider Electric': {
        'name': 'Schneider Electric',
        'devices': {
            'Modicon M340': {
                'protocols': ['Modbus TCP', 'EtherNet/IP'],
                'ports': {
                    'modbus_tcp': 502,
                    'ethernet_ip': 44818
                },
                'slave_id_range': (1, 247),
                'notes': 'Standard Modbus TCP auf Port 502.'
            },
            'Modicon M580': {
                'protocols': ['Modbus TCP', 'EtherNet/IP'],
                'ports': {
                    'modbus_tcp': 502,
                    'ethernet_ip': 44818
                },
                'slave_id_range': (1, 247),
                'notes': 'Standard Modbus TCP auf Port 502.'
            },
            'Modicon Premium': {
                'protocols': ['Modbus TCP'],
                'ports': {
                    'modbus_tcp': 502
                },
                'slave_id_range': (1, 247),
                'notes': 'Standard Modbus TCP.'
            },
            'Modicon Quantum': {
                'protocols': ['Modbus TCP'],
                'ports': {
                    'modbus_tcp': 502
                },
                'slave_id_range': (1, 247),
                'notes': 'Standard Modbus TCP.'
            }
        }
    },
    'ABB': {
        'name': 'ABB',
        'devices': {
            'AC500': {
                'protocols': ['Modbus TCP', 'PROFINET'],
                'ports': {
                    'modbus_tcp': 502,
                    'profinet': [34962, 34963, 34964]
                },
                'slave_id_range': (1, 247),
                'notes': 'Standard Modbus TCP auf Port 502.'
            },
            'AC800M': {
                'protocols': ['Modbus TCP'],
                'ports': {
                    'modbus_tcp': 502
                },
                'slave_id_range': (1, 247),
                'notes': 'Standard Modbus TCP.'
            }
        }
    },
    'Wago': {
        'name': 'Wago',
        'devices': {
            'PFC100': {
                'protocols': ['Modbus TCP', 'EtherNet/IP'],
                'ports': {
                    'modbus_tcp': 502,
                    'ethernet_ip': 44818
                },
                'slave_id_range': (1, 247),
                'notes': 'Standard Modbus TCP auf Port 502.'
            },
            'PFC200': {
                'protocols': ['Modbus TCP', 'EtherNet/IP', 'PROFINET'],
                'ports': {
                    'modbus_tcp': 502,
                    'ethernet_ip': 44818,
                    'profinet': [34962, 34963, 34964]
                },
                'slave_id_range': (1, 247),
                'notes': 'Unterstützt mehrere Protokolle.'
            },
            '750 Series': {
                'protocols': ['Modbus TCP'],
                'ports': {
                    'modbus_tcp': 502
                },
                'slave_id_range': (1, 247),
                'notes': 'Feldbus-Koppler mit Modbus TCP.'
            }
        }
    },
    'Beckhoff': {
        'name': 'Beckhoff',
        'devices': {
            'CX Series': {
                'protocols': ['Modbus TCP', 'TwinCAT ADS', 'EtherCAT'],
                'ports': {
                    'modbus_tcp': 502,
                    'twincat_ads': [1010, 1020],
                    'twincat_ads_secure': 8016,
                    'ads_discovery': 48899
                },
                'notes': 'TwinCAT ADS ist das native Protokoll.'
            },
            'EK Series': {
                'protocols': ['Modbus TCP', 'EtherCAT'],
                'ports': {
                    'modbus_tcp': 502
                },
                'notes': 'EtherCAT-Koppler mit Modbus TCP Option.'
            }
        }
    },
    'Phoenix Contact': {
        'name': 'Phoenix Contact',
        'devices': {
            'ILC Series': {
                'protocols': ['Modbus TCP', 'PROFINET'],
                'ports': {
                    'modbus_tcp': 502,
                    'profinet': [34962, 34963, 34964]
                },
                'slave_id_range': (1, 247),
                'notes': 'Standard Modbus TCP.'
            },
            'AXC Series': {
                'protocols': ['Modbus TCP', 'PROFINET', 'EtherNet/IP'],
                'ports': {
                    'modbus_tcp': 502,
                    'profinet': [34962, 34963, 34964],
                    'ethernet_ip': 44818
                },
                'slave_id_range': (1, 247),
                'notes': 'Multi-Protokoll-Controller.'
            }
        }
    },
    'Allen-Bradley': {
        'name': 'Allen-Bradley/Rockwell',
        'devices': {
            'ControlLogix': {
                'protocols': ['EtherNet/IP', 'Modbus TCP'],
                'ports': {
                    'ethernet_ip': 44818,
                    'modbus_tcp': 502
                },
                'notes': 'EtherNet/IP ist das native Protokoll.'
            },
            'CompactLogix': {
                'protocols': ['EtherNet/IP', 'Modbus TCP'],
                'ports': {
                    'ethernet_ip': 44818,
                    'modbus_tcp': 502
                },
                'notes': 'EtherNet/IP ist das native Protokoll.'
            },
            'MicroLogix': {
                'protocols': ['EtherNet/IP'],
                'ports': {
                    'ethernet_ip': 44818,
                    'ethernet_ip_legacy': 2222
                },
                'notes': 'Ältere Modelle verwenden Port 2222.'
            }
        }
    },
    'Generic': {
        'name': 'Generic Modbus',
        'devices': {
            'Modbus TCP Device': {
                'protocols': ['Modbus TCP'],
                'ports': {
                    'modbus_tcp': 502
                },
                'slave_id_range': (1, 247),
                'notes': 'Standard Modbus TCP Gerät.'
            }
        }
    }
}

# Protocol port reference
PROTOCOL_PORTS = {
    'modbus_tcp': {
        'name': 'Modbus TCP',
        'default_port': 502,
        'alternative_ports': [510, 5020, 20000],
        'type': 'TCP',
        'description': 'Standard Industrial Protocol for device communication'
    },
    's7comm': {
        'name': 'S7comm (ISO-on-TCP)',
        'default_port': 102,
        'alternative_ports': [],
        'type': 'TCP',
        'description': 'Siemens proprietary protocol for S7 PLCs'
    },
    'profinet': {
        'name': 'PROFINET',
        'default_port': 34962,
        'alternative_ports': [34963, 34964, 53247],
        'type': 'UDP',
        'description': 'Real-time Ethernet for industrial automation'
    },
    'ethernet_ip': {
        'name': 'EtherNet/IP',
        'default_port': 44818,
        'alternative_ports': [2222],
        'type': 'TCP/UDP',
        'description': 'Rockwell/Allen-Bradley industrial Ethernet protocol'
    },
    'twincat_ads': {
        'name': 'TwinCAT ADS',
        'default_port': 48898,
        'alternative_ports': [1010, 1020, 8016],
        'type': 'TCP',
        'description': 'Beckhoff automation protocol'
    }
}

# Common scan port ranges by use case
SCAN_PORT_RANGES = {
    'quick': {
        'name': 'Quick Scan',
        'ports': [102, 502, 510],
        'description': 'Schneller Scan für gängige Protokolle'
    },
    'standard': {
        'name': 'Standard Scan',
        'ports': [102, 502, 510, 2222, 44818],
        'description': 'Standard-Scan für die meisten Geräte'
    },
    'extended': {
        'name': 'Extended Scan',
        'ports': [102, 502, 510, 2222, 44818, 34962, 34963, 34964, 1010, 1020],
        'description': 'Erweiterter Scan inkl. PROFINET und TwinCAT'
    },
    'full': {
        'name': 'Full Scan',
        'port_range': '102,502,510,2222,5020,20000-20100,34962-34964,44818,48898-48899',
        'description': 'Vollständiger Scan aller bekannten Ports'
    }
}


def get_manufacturer_info(manufacturer_name):
    """Get manufacturer information by name"""
    for key, data in MANUFACTURER_PORTS.items():
        if key.lower() == manufacturer_name.lower() or data['name'].lower() == manufacturer_name.lower():
            return data
    return None


def get_device_info(manufacturer_name, device_name):
    """Get device information by manufacturer and device name"""
    manufacturer = get_manufacturer_info(manufacturer_name)
    if manufacturer:
        for key, device in manufacturer.get('devices', {}).items():
            if key.lower() == device_name.lower():
                return device
    return None


def get_ports_for_protocol(protocol):
    """Get port information for a protocol"""
    return PROTOCOL_PORTS.get(protocol.lower().replace(' ', '_').replace('-', '_'))


def detect_manufacturer_by_port(port):
    """Detect possible manufacturers by open port"""
    possible_manufacturers = []

    for mfr_key, mfr_data in MANUFACTURER_PORTS.items():
        for device_name, device_info in mfr_data.get('devices', {}).items():
            ports = device_info.get('ports', {})
            for protocol, port_value in ports.items():
                if isinstance(port_value, list):
                    if port in port_value:
                        possible_manufacturers.append({
                            'manufacturer': mfr_data['name'],
                            'device': device_name,
                            'protocol': protocol
                        })
                elif port_value == port:
                    possible_manufacturers.append({
                        'manufacturer': mfr_data['name'],
                        'device': device_name,
                        'protocol': protocol
                    })

    return possible_manufacturers


def get_recommended_ports_for_scan():
    """Get recommended ports for network scanning"""
    ports = set()
    for protocol_info in PROTOCOL_PORTS.values():
        ports.add(protocol_info['default_port'])
        ports.update(protocol_info.get('alternative_ports', []))
    return sorted(list(ports))


def get_all_manufacturers():
    """Get list of all manufacturers"""
    return [data['name'] for data in MANUFACTURER_PORTS.values()]


def get_devices_for_manufacturer(manufacturer_name):
    """Get all devices for a manufacturer"""
    manufacturer = get_manufacturer_info(manufacturer_name)
    if manufacturer:
        return list(manufacturer.get('devices', {}).keys())
    return []

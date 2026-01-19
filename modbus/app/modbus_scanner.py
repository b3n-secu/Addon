"""
Modbus Scanner for automatic device discovery
"""
import logging
import socket
import ipaddress
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

logger = logging.getLogger(__name__)


class ModbusScanner:
    """Scanner for Modbus devices"""

    def __init__(self, host, port=502, timeout=3):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.client = None

    @staticmethod
    def lg8add(logo_modbustcp_address: int) -> int:
        """
        Logo8 uses modbusTCP +1 address offset
        to stay conform with their documentation, subtract 1 from each given address
        """
        return logo_modbustcp_address - 1

    def connect(self):
        """Connect to Modbus device"""
        try:
            self.client = ModbusTcpClient(
                host=self.host,
                port=self.port,
                timeout=self.timeout
            )
            connected = self.client.connect()
            if connected:
                logger.info(f"Connected to {self.host}:{self.port}")
                return True
            else:
                logger.error(f"Failed to connect to {self.host}:{self.port}")
                return False
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False

    def disconnect(self):
        """Disconnect from Modbus device"""
        if self.client:
            try:
                self.client.close()
                logger.info(f"Disconnected from {self.host}:{self.port}")
            except:
                pass

    def scan_coils(self, start_address=0, count=100, slave=1):
        """Scan coils (digital outputs)"""
        available = []
        try:
            result = self.client.read_coils(start_address, count, unit=slave)
            if not result.isError() and hasattr(result, 'bits'):
                for i, bit in enumerate(result.bits[:count]):
                    available.append({
                        'address': start_address + i,
                        'value': bit,
                        'type': 'coil'
                    })
                logger.info(f"Found {len(available)} coils starting at {start_address}")
        except Exception as e:
            logger.debug(f"Error scanning coils: {e}")
        return available

    def scan_discrete_inputs(self, start_address=0, count=100, slave=1):
        """Scan discrete inputs (digital inputs)"""
        available = []
        try:
            result = self.client.read_discrete_inputs(start_address, count, unit=slave)
            if not result.isError() and hasattr(result, 'bits'):
                for i, bit in enumerate(result.bits[:count]):
                    available.append({
                        'address': start_address + i,
                        'value': bit,
                        'type': 'discrete_input'
                    })
                logger.info(f"Found {len(available)} discrete inputs starting at {start_address}")
        except Exception as e:
            logger.debug(f"Error scanning discrete inputs: {e}")
        return available

    def scan_holding_registers(self, start_address=0, count=100, slave=1):
        """Scan holding registers"""
        available = []
        try:
            result = self.client.read_holding_registers(start_address, count, unit=slave)
            if not result.isError() and hasattr(result, 'registers'):
                for i, value in enumerate(result.registers):
                    available.append({
                        'address': start_address + i,
                        'value': value,
                        'type': 'holding_register'
                    })
                logger.info(f"Found {len(available)} holding registers starting at {start_address}")
        except Exception as e:
            logger.debug(f"Error scanning holding registers: {e}")
        return available

    def scan_input_registers(self, start_address=0, count=100, slave=1):
        """Scan input registers"""
        available = []
        try:
            result = self.client.read_input_registers(start_address, count, unit=slave)
            if not result.isError() and hasattr(result, 'registers'):
                for i, value in enumerate(result.registers):
                    available.append({
                        'address': start_address + i,
                        'value': value,
                        'type': 'input_register'
                    })
                logger.info(f"Found {len(available)} input registers starting at {start_address}")
        except Exception as e:
            logger.debug(f"Error scanning input registers: {e}")
        return available

    def scan_device(self, profile=None, slave=1):
        """Scan device based on profile or generic scan"""
        results = {
            'coils': [],
            'discrete_inputs': [],
            'holding_registers': [],
            'input_registers': []
        }

        if not self.connect():
            return results

        try:
            if profile and 'registers' in profile:
                # Scan based on profile
                registers = profile['registers']

                if 'digital_outputs' in registers:
                    reg = registers['digital_outputs']
                    results['coils'] = self.scan_coils(
                        reg.get('start_address', 0),
                        reg.get('count', 20),
                        slave
                    )

                if 'digital_inputs' in registers:
                    reg = registers['digital_inputs']
                    results['discrete_inputs'] = self.scan_discrete_inputs(
                        reg.get('start_address', 0),
                        reg.get('count', 24),
                        slave
                    )

                if 'analog_outputs' in registers or 'holding_registers' in registers:
                    reg_key = 'analog_outputs' if 'analog_outputs' in registers else 'holding_registers'
                    reg = registers[reg_key]
                    results['holding_registers'] = self.scan_holding_registers(
                        reg.get('start_address', 0),
                        reg.get('count', 10),
                        slave
                    )

                if 'analog_inputs' in registers or 'input_registers' in registers:
                    reg_key = 'analog_inputs' if 'analog_inputs' in registers else 'input_registers'
                    reg = registers[reg_key]
                    results['input_registers'] = self.scan_input_registers(
                        reg.get('start_address', 0),
                        reg.get('count', 10),
                        slave
                    )
            else:
                # Generic scan - try common ranges
                results['coils'] = self.scan_coils(0, 100, slave)
                results['discrete_inputs'] = self.scan_discrete_inputs(0, 100, slave)
                results['holding_registers'] = self.scan_holding_registers(0, 100, slave)
                results['input_registers'] = self.scan_input_registers(0, 100, slave)

                # Try Siemens LOGO! specific addresses if nothing found
                if not any(results.values()):
                    logger.info("Trying Siemens LOGO! specific addresses...")
                    results['discrete_inputs'] = self.scan_discrete_inputs(1, 24, slave)
                    results['input_registers'] = self.scan_input_registers(1, 8, slave)
                    results['coils'] = self.scan_coils(8193, 20, slave)  # 0x2001

        finally:
            self.disconnect()

        return results

    def detect_device_type(self, slave=1):
        """
        Automatically detect device type by testing specific addresses
        Returns: 'LOGO_8', 'LOGO_0BA7', or 'GENERIC'
        """
        if not self.connect():
            return 'UNKNOWN'

        try:
            # Test for LOGO! specific addresses
            # LOGO! uses address offset of -1

            # Try LOGO! 8 signature: Digital output at 8193 (0x2001)
            try:
                result = self.client.read_coils(self.lg8add(8193), 1, unit=slave)
                if not result.isError():
                    # Check for VM memory at typical LOGO! addresses
                    vm_test = self.client.read_holding_registers(self.lg8add(1), 1, unit=slave)
                    if not vm_test.isError():
                        # Test for LOGO! 8 specific: Try AM registers (528+)
                        am_test = self.client.read_holding_registers(self.lg8add(529), 1, unit=slave)
                        if not am_test.isError():
                            logger.info("Device detected as: LOGO! 8")
                            return 'LOGO_8'

                        # Test for 0BA7: Marker bits at 8255
                        marker_test = self.client.read_coils(self.lg8add(8255), 1, unit=slave)
                        if not marker_test.isError():
                            # Check if only 16 outputs (0BA7 specific)
                            q16_test = self.client.read_coils(self.lg8add(8209), 1, unit=slave)
                            if not q16_test.isError():
                                logger.info("Device detected as: LOGO! 0BA7")
                                return 'LOGO_0BA7'
            except:
                pass

            # Generic Modbus device
            # Test standard Modbus registers
            try:
                result = self.client.read_holding_registers(0, 1, unit=slave)
                if not result.isError():
                    logger.info("Device detected as: Generic Modbus")
                    return 'GENERIC'
            except:
                pass

        except Exception as e:
            logger.debug(f"Error during device detection: {e}")
        finally:
            self.disconnect()

        return 'UNKNOWN'

    def discover_register_map(self, slave=1):
        """
        Comprehensive register discovery to determine device capabilities.
        Tests common Modbus register ranges and LOGO!-specific addresses.

        Returns:
            dict: Detailed report of supported register types and ranges
        """
        if not self.connect():
            return {
                'success': False,
                'error': 'Could not connect to device'
            }

        discovery = {
            'success': True,
            'slave_id': slave,
            'supported_functions': [],
            'register_ranges': {
                'discrete_inputs': [],
                'coils': [],
                'input_registers': [],
                'holding_registers': []
            },
            'detected_device': 'UNKNOWN',
            'recommendations': []
        }

        try:
            # Test ranges to check
            test_ranges = {
                'discrete_inputs': [
                    {'start': 0, 'count': 100, 'name': 'Standard (0-99)'},
                    {'start': 1, 'count': 24, 'name': 'LOGO! Digital Inputs (I1-I24)'},
                    {'start': 10000, 'count': 100, 'name': 'Modicon 1x Range (10001-10100)'}
                ],
                'coils': [
                    {'start': 0, 'count': 100, 'name': 'Standard (0-99)'},
                    {'start': 1, 'count': 100, 'name': 'LOGO! Direct Write (Q1-Q100)'},
                    {'start': 8193, 'count': 100, 'name': 'LOGO! VM Outputs (8193-8292)'},
                    {'start': 8198, 'count': 100, 'name': 'LOGO! Verify Range (8199-8298)'}
                ],
                'input_registers': [
                    {'start': 0, 'count': 100, 'name': 'Standard (0-99)'},
                    {'start': 1, 'count': 8, 'name': 'LOGO! Analog Inputs (AI1-AI8)'},
                    {'start': 30000, 'count': 100, 'name': 'Modicon 3x Range (30001-30100)'}
                ],
                'holding_registers': [
                    {'start': 0, 'count': 100, 'name': 'Standard (0-99)'},
                    {'start': 1, 'count': 100, 'name': 'LOGO! VM Memory (V0.0-V99.0)'},
                    {'start': 528, 'count': 8, 'name': 'LOGO! Analog Outputs (AQ1-AQ8)'},
                    {'start': 40000, 'count': 100, 'name': 'Modicon 4x Range (40001-40100)'}
                ]
            }

            logger.info(f"Starting comprehensive register discovery on {self.host}:{self.port} slave {slave}")

            # Test discrete inputs (Function Code 2)
            for test_range in test_ranges['discrete_inputs']:
                try:
                    result = self.client.read_discrete_inputs(
                        test_range['start'],
                        test_range['count'],
                        unit=slave
                    )
                    if not result.isError() and hasattr(result, 'bits'):
                        # Count how many are responding (not all zeros or ones)
                        active_count = sum(1 for bit in result.bits[:test_range['count']])
                        discovery['register_ranges']['discrete_inputs'].append({
                            'range': test_range['name'],
                            'start': test_range['start'],
                            'count': test_range['count'],
                            'supported': True,
                            'active_registers': active_count,
                            'note': f"{active_count}/{test_range['count']} inputs are HIGH"
                        })
                        logger.info(f"✓ Discrete Inputs: {test_range['name']} - {active_count} active")
                    else:
                        discovery['register_ranges']['discrete_inputs'].append({
                            'range': test_range['name'],
                            'start': test_range['start'],
                            'count': test_range['count'],
                            'supported': False,
                            'error': str(result) if hasattr(result, '__str__') else 'No response'
                        })
                        logger.debug(f"✗ Discrete Inputs: {test_range['name']} - Not supported")
                except Exception as e:
                    logger.debug(f"✗ Discrete Inputs: {test_range['name']} - Error: {e}")
                    discovery['register_ranges']['discrete_inputs'].append({
                        'range': test_range['name'],
                        'start': test_range['start'],
                        'count': test_range['count'],
                        'supported': False,
                        'error': str(e)
                    })

            # Test coils (Function Code 1)
            for test_range in test_ranges['coils']:
                try:
                    result = self.client.read_coils(
                        test_range['start'],
                        test_range['count'],
                        unit=slave
                    )
                    if not result.isError() and hasattr(result, 'bits'):
                        active_count = sum(1 for bit in result.bits[:test_range['count']])
                        discovery['register_ranges']['coils'].append({
                            'range': test_range['name'],
                            'start': test_range['start'],
                            'count': test_range['count'],
                            'supported': True,
                            'active_registers': active_count,
                            'note': f"{active_count}/{test_range['count']} outputs are ON"
                        })
                        logger.info(f"✓ Coils: {test_range['name']} - {active_count} active")
                    else:
                        discovery['register_ranges']['coils'].append({
                            'range': test_range['name'],
                            'start': test_range['start'],
                            'count': test_range['count'],
                            'supported': False,
                            'error': str(result) if hasattr(result, '__str__') else 'No response'
                        })
                        logger.debug(f"✗ Coils: {test_range['name']} - Not supported")
                except Exception as e:
                    logger.debug(f"✗ Coils: {test_range['name']} - Error: {e}")
                    discovery['register_ranges']['coils'].append({
                        'range': test_range['name'],
                        'start': test_range['start'],
                        'count': test_range['count'],
                        'supported': False,
                        'error': str(e)
                    })

            # Test input registers (Function Code 4)
            for test_range in test_ranges['input_registers']:
                try:
                    result = self.client.read_input_registers(
                        test_range['start'],
                        test_range['count'],
                        unit=slave
                    )
                    if not result.isError() and hasattr(result, 'registers'):
                        non_zero = sum(1 for val in result.registers if val != 0)
                        # Show first 5 values as sample
                        sample_values = result.registers[:min(5, len(result.registers))]
                        discovery['register_ranges']['input_registers'].append({
                            'range': test_range['name'],
                            'start': test_range['start'],
                            'count': test_range['count'],
                            'supported': True,
                            'non_zero_registers': non_zero,
                            'sample_values': sample_values,
                            'note': f"{non_zero} non-zero values, Sample: {sample_values}"
                        })
                        logger.info(f"✓ Input Registers: {test_range['name']} - {non_zero} non-zero")
                    else:
                        discovery['register_ranges']['input_registers'].append({
                            'range': test_range['name'],
                            'start': test_range['start'],
                            'count': test_range['count'],
                            'supported': False,
                            'error': str(result) if hasattr(result, '__str__') else 'No response'
                        })
                        logger.debug(f"✗ Input Registers: {test_range['name']} - Not supported")
                except Exception as e:
                    logger.debug(f"✗ Input Registers: {test_range['name']} - Error: {e}")
                    discovery['register_ranges']['input_registers'].append({
                        'range': test_range['name'],
                        'start': test_range['start'],
                        'count': test_range['count'],
                        'supported': False,
                        'error': str(e)
                    })

            # Test holding registers (Function Code 3)
            for test_range in test_ranges['holding_registers']:
                try:
                    result = self.client.read_holding_registers(
                        test_range['start'],
                        test_range['count'],
                        unit=slave
                    )
                    if not result.isError() and hasattr(result, 'registers'):
                        non_zero = sum(1 for val in result.registers if val != 0)
                        sample_values = result.registers[:min(5, len(result.registers))]
                        discovery['register_ranges']['holding_registers'].append({
                            'range': test_range['name'],
                            'start': test_range['start'],
                            'count': test_range['count'],
                            'supported': True,
                            'non_zero_registers': non_zero,
                            'sample_values': sample_values,
                            'note': f"{non_zero} non-zero values, Sample: {sample_values}"
                        })
                        logger.info(f"✓ Holding Registers: {test_range['name']} - {non_zero} non-zero")
                    else:
                        discovery['register_ranges']['holding_registers'].append({
                            'range': test_range['name'],
                            'start': test_range['start'],
                            'count': test_range['count'],
                            'supported': False,
                            'error': str(result) if hasattr(result, '__str__') else 'No response'
                        })
                        logger.debug(f"✗ Holding Registers: {test_range['name']} - Not supported")
                except Exception as e:
                    logger.debug(f"✗ Holding Registers: {test_range['name']} - Error: {e}")
                    discovery['register_ranges']['holding_registers'].append({
                        'range': test_range['name'],
                        'start': test_range['start'],
                        'count': test_range['count'],
                        'supported': False,
                        'error': str(e)
                    })

            # Determine supported function codes
            for reg_type, ranges in discovery['register_ranges'].items():
                if any(r['supported'] for r in ranges):
                    discovery['supported_functions'].append(reg_type)

            # Device detection and recommendations
            has_logo_di = any(
                r['supported'] and 'LOGO!' in r['range']
                for r in discovery['register_ranges']['discrete_inputs']
            )
            has_logo_coils = any(
                r['supported'] and 'LOGO!' in r['range']
                for r in discovery['register_ranges']['coils']
            )
            has_logo_ai = any(
                r['supported'] and 'LOGO!' in r['range']
                for r in discovery['register_ranges']['input_registers']
            )

            if has_logo_di and has_logo_coils and has_logo_ai:
                discovery['detected_device'] = 'SIEMENS LOGO! 8'
                discovery['recommendations'] = [
                    'Device detected as Siemens LOGO! 8',
                    'Use manufacturer: Siemens, model: LOGO! 8',
                    'Digital Inputs: Configure I1-I24 in device settings',
                    'Digital Outputs: Configure Q1-Q20 in device settings',
                    'Analog Inputs: Configure AI1-AI8 if used',
                    'Port: 510 (LOGO! standard)',
                    'Write to outputs: Address 1-N',
                    'Verify outputs: Address 8199+ (8198 + N)'
                ]
            elif any('Modicon' in r.get('range', '') and r.get('supported')
                    for ranges in discovery['register_ranges'].values() for r in ranges):
                discovery['detected_device'] = 'Generic Modbus (Modicon addressing)'
                discovery['recommendations'] = [
                    'Device uses Modicon address convention',
                    'Discrete Inputs: 10001-1xxxx',
                    'Coils (Outputs): 00001-0xxxx',
                    'Input Registers: 30001-3xxxx',
                    'Holding Registers: 40001-4xxxx'
                ]
            else:
                discovery['detected_device'] = 'Generic Modbus Device'
                discovery['recommendations'] = [
                    'Standard Modbus device detected',
                    'Use supported register ranges shown above',
                    'Configure I/O counts based on actual device specifications'
                ]

            logger.info(f"Register discovery completed. Device: {discovery['detected_device']}")

        except Exception as e:
            logger.error(f"Error during register discovery: {e}", exc_info=True)
            discovery['success'] = False
            discovery['error'] = str(e)
        finally:
            self.disconnect()

        return discovery

    def auto_scan_device(self, slave=1):
        """
        Automatically scan device and return all found data with device type
        """
        device_type = self.detect_device_type(slave)

        results = {
            'device_type': device_type,
            'registers': {}
        }

        if device_type == 'LOGO_8':
            results['registers'] = self.scan_logo8_addresses(slave)
        elif device_type == 'LOGO_0BA7':
            results['registers'] = self.scan_logo0ba7_addresses(slave)
        elif device_type == 'GENERIC':
            results['registers'] = self.scan_device(None, slave)

        return results

    def test_connection(self):
        """Test connection to device"""
        if self.connect():
            self.disconnect()
            return True
        return False

    def scan_logo8_addresses(self, slave=1):
        """
        Detailed scan for Siemens LOGO! 8 specific addresses
        Based on LOGO! 8 Modbus TCP addressing
        """
        results = {
            'digital_inputs': [],
            'digital_outputs': [],
            'analog_inputs': [],
            'analog_outputs': [],
            'vm_memory': []
        }

        if not self.connect():
            return results

        try:
            # Digital Inputs (DI1-DI24): Address 1-24
            logger.info("Scanning LOGO! 8 Digital Inputs (DI1-DI24)...")
            for addr in range(1, 25):
                try:
                    result = self.client.read_discrete_inputs(self.lg8add(addr), 1, unit=slave)
                    if not result.isError() and hasattr(result, 'bits'):
                        results['digital_inputs'].append({
                            'address': addr,
                            'modbus_address': self.lg8add(addr),
                            'name': f'DI{addr}',
                            'value': result.bits[0],
                            'type': 'discrete_input'
                        })
                except:
                    pass

            # Digital Outputs (Q1-Q20): Address 8193-8212 (0x2001-0x2014)
            logger.info("Scanning LOGO! 8 Digital Outputs (Q1-Q20)...")
            for i in range(20):
                addr = 8193 + i
                try:
                    result = self.client.read_coils(self.lg8add(addr), 1, unit=slave)
                    if not result.isError() and hasattr(result, 'bits'):
                        results['digital_outputs'].append({
                            'address': addr,
                            'modbus_address': self.lg8add(addr),
                            'name': f'Q{i+1}',
                            'value': result.bits[0],
                            'type': 'coil'
                        })
                except:
                    pass

            # Analog Inputs (AI1-AI8): Multiple access methods
            logger.info("Scanning LOGO! 8 Analog Inputs (AI1-AI8)...")
            for i in range(1, 9):
                try:
                    # Direct read via input registers
                    result = self.client.read_input_registers(self.lg8add(i), 1, unit=slave)
                    if not result.isError() and hasattr(result, 'registers'):
                        results['analog_inputs'].append({
                            'address': i,
                            'modbus_address': self.lg8add(i),
                            'name': f'AI{i}',
                            'value': result.registers[0],
                            'type': 'input_register',
                            'method': 'direct'
                        })

                    # VM mapping read via holding registers
                    vm_addr = (i - 1) * 2 + 1  # VW0, VW2, VW4, etc.
                    result_vm = self.client.read_holding_registers(self.lg8add(vm_addr), 1, unit=slave)
                    if not result_vm.isError() and hasattr(result_vm, 'registers'):
                        results['analog_inputs'].append({
                            'address': vm_addr,
                            'modbus_address': self.lg8add(vm_addr),
                            'name': f'AI{i}_VM',
                            'value': result_vm.registers[0],
                            'type': 'holding_register',
                            'method': 'vm_mapping'
                        })

                    # AM mapping (AM1-AM8): Address 529-536
                    am_addr = 528 + i
                    result_am = self.client.read_holding_registers(self.lg8add(am_addr), 1, unit=slave)
                    if not result_am.isError() and hasattr(result_am, 'registers'):
                        results['analog_inputs'].append({
                            'address': am_addr,
                            'modbus_address': self.lg8add(am_addr),
                            'name': f'AM{i}',
                            'value': result_am.registers[0],
                            'type': 'holding_register',
                            'method': 'am_mapping'
                        })
                except:
                    pass

            # Analog Outputs (AQ1-AQ8): Address 528.1 onwards or via VM
            logger.info("Scanning LOGO! 8 Analog Outputs (AQ1-AQ8)...")
            for i in range(1, 9):
                try:
                    # Try common analog output addresses
                    aq_addr = 1024 + i  # Common AQ range
                    result = self.client.read_holding_registers(self.lg8add(aq_addr), 1, unit=slave)
                    if not result.isError() and hasattr(result, 'registers'):
                        results['analog_outputs'].append({
                            'address': aq_addr,
                            'modbus_address': self.lg8add(aq_addr),
                            'name': f'AQ{i}',
                            'value': result.registers[0],
                            'type': 'holding_register'
                        })
                except:
                    pass

            # VM Memory (VW0-VW850): Sample key addresses
            logger.info("Scanning LOGO! 8 VM Memory (sample addresses)...")
            vm_addresses = [0, 2, 4, 6, 8, 10, 100, 200, 300, 400, 500, 600, 700, 800, 850]
            for vm_addr in vm_addresses:
                try:
                    result = self.client.read_holding_registers(self.lg8add(vm_addr + 1), 1, unit=slave)
                    if not result.isError() and hasattr(result, 'registers'):
                        results['vm_memory'].append({
                            'address': vm_addr + 1,
                            'modbus_address': self.lg8add(vm_addr + 1),
                            'name': f'VW{vm_addr}',
                            'value': result.registers[0],
                            'type': 'holding_register'
                        })
                except:
                    pass

        finally:
            self.disconnect()

        # Count total found addresses
        total = sum(len(v) for v in results.values())
        logger.info(f"LOGO! 8 scan complete: {total} addresses found")

        return results

    def scan_logo0ba7_addresses(self, slave=1):
        """
        Detailed scan for Siemens LOGO! 0BA7 specific addresses
        Based on LOGO! 0BA7 Modbus TCP addressing
        """
        results = {
            'digital_inputs': [],
            'digital_outputs': [],
            'analog_inputs': [],
            'analog_outputs': [],
            'vm_memory': [],
            'marker_bits': []
        }

        if not self.connect():
            return results

        try:
            # Digital Inputs (I1-I24): Address 1-24
            logger.info("Scanning LOGO! 0BA7 Digital Inputs (I1-I24)...")
            for addr in range(1, 25):
                try:
                    result = self.client.read_discrete_inputs(self.lg8add(addr), 1, unit=slave)
                    if not result.isError() and hasattr(result, 'bits'):
                        results['digital_inputs'].append({
                            'address': addr,
                            'modbus_address': self.lg8add(addr),
                            'name': f'I{addr}',
                            'value': result.bits[0],
                            'type': 'discrete_input'
                        })
                except:
                    pass

            # Digital Outputs (Q1-Q16): Address 8193-8208 (0x2001-0x2010)
            logger.info("Scanning LOGO! 0BA7 Digital Outputs (Q1-Q16)...")
            for i in range(16):
                addr = 8193 + i
                try:
                    result = self.client.read_coils(self.lg8add(addr), 1, unit=slave)
                    if not result.isError() and hasattr(result, 'bits'):
                        results['digital_outputs'].append({
                            'address': addr,
                            'modbus_address': self.lg8add(addr),
                            'name': f'Q{i+1}',
                            'value': result.bits[0],
                            'type': 'coil'
                        })
                except:
                    pass

            # Marker Bits (M1-M24): Address 8255-8278 (0x203F-0x2056)
            logger.info("Scanning LOGO! 0BA7 Marker Bits (M1-M24)...")
            for i in range(24):
                addr = 8255 + i
                try:
                    result = self.client.read_coils(self.lg8add(addr), 1, unit=slave)
                    if not result.isError() and hasattr(result, 'bits'):
                        results['marker_bits'].append({
                            'address': addr,
                            'modbus_address': self.lg8add(addr),
                            'name': f'M{i+1}',
                            'value': result.bits[0],
                            'type': 'coil'
                        })
                except:
                    pass

            # Analog Inputs (AI1-AI8): Multiple access methods
            logger.info("Scanning LOGO! 0BA7 Analog Inputs (AI1-AI8)...")
            for i in range(1, 9):
                try:
                    # Direct read via input registers
                    result = self.client.read_input_registers(self.lg8add(i), 1, unit=slave)
                    if not result.isError() and hasattr(result, 'registers'):
                        results['analog_inputs'].append({
                            'address': i,
                            'modbus_address': self.lg8add(i),
                            'name': f'AI{i}',
                            'value': result.registers[0],
                            'type': 'input_register',
                            'method': 'direct'
                        })

                    # VM mapping read via holding registers (VW0-VW14 for AI1-AI8)
                    vm_addr = (i - 1) * 2 + 1  # VW0, VW2, VW4, etc.
                    result_vm = self.client.read_holding_registers(self.lg8add(vm_addr), 1, unit=slave)
                    if not result_vm.isError() and hasattr(result_vm, 'registers'):
                        results['analog_inputs'].append({
                            'address': vm_addr,
                            'modbus_address': self.lg8add(vm_addr),
                            'name': f'AI{i}_VM',
                            'value': result_vm.registers[0],
                            'type': 'holding_register',
                            'method': 'vm_mapping'
                        })
                except:
                    pass

            # Analog Outputs (AQ1-AQ2): 0BA7 typically has fewer analog outputs
            logger.info("Scanning LOGO! 0BA7 Analog Outputs (AQ1-AQ2)...")
            for i in range(1, 3):
                try:
                    # Try common analog output addresses
                    aq_addr = 1024 + i
                    result = self.client.read_holding_registers(self.lg8add(aq_addr), 1, unit=slave)
                    if not result.isError() and hasattr(result, 'registers'):
                        results['analog_outputs'].append({
                            'address': aq_addr,
                            'modbus_address': self.lg8add(aq_addr),
                            'name': f'AQ{i}',
                            'value': result.registers[0],
                            'type': 'holding_register'
                        })
                except:
                    pass

            # VM Memory (VW0-VW850): Sample key addresses
            logger.info("Scanning LOGO! 0BA7 VM Memory (sample addresses)...")
            vm_addresses = [0, 2, 4, 6, 8, 10, 20, 40, 60, 80, 100, 200, 300, 400, 500, 600, 700, 800, 850]
            for vm_addr in vm_addresses:
                try:
                    result = self.client.read_holding_registers(self.lg8add(vm_addr + 1), 1, unit=slave)
                    if not result.isError() and hasattr(result, 'registers'):
                        results['vm_memory'].append({
                            'address': vm_addr + 1,
                            'modbus_address': self.lg8add(vm_addr + 1),
                            'name': f'VW{vm_addr}',
                            'value': result.registers[0],
                            'type': 'holding_register'
                        })
                except:
                    pass

        finally:
            self.disconnect()

        # Count total found addresses
        total = sum(len(v) for v in results.values())
        logger.info(f"LOGO! 0BA7 scan complete: {total} addresses found")

        return results

    def scan_detailed_addresses(self, address_list, slave=1):
        """
        Scan specific addresses provided by user
        address_list format: [{'type': 'coil', 'address': 8193}, ...]
        """
        results = []

        if not self.connect():
            return results

        try:
            for item in address_list:
                addr_type = item.get('type', 'holding_register')
                address = item.get('address', 0)
                count = item.get('count', 1)

                try:
                    if addr_type == 'coil':
                        result = self.client.read_coils(address, count, unit=slave)
                        if not result.isError() and hasattr(result, 'bits'):
                            for i, bit in enumerate(result.bits[:count]):
                                results.append({
                                    'address': address + i,
                                    'value': bit,
                                    'type': 'coil'
                                })
                    elif addr_type == 'discrete_input':
                        result = self.client.read_discrete_inputs(address, count, unit=slave)
                        if not result.isError() and hasattr(result, 'bits'):
                            for i, bit in enumerate(result.bits[:count]):
                                results.append({
                                    'address': address + i,
                                    'value': bit,
                                    'type': 'discrete_input'
                                })
                    elif addr_type == 'input_register':
                        result = self.client.read_input_registers(address, count, unit=slave)
                        if not result.isError() and hasattr(result, 'registers'):
                            for i, value in enumerate(result.registers):
                                results.append({
                                    'address': address + i,
                                    'value': value,
                                    'type': 'input_register'
                                })
                    elif addr_type == 'holding_register':
                        result = self.client.read_holding_registers(address, count, unit=slave)
                        if not result.isError() and hasattr(result, 'registers'):
                            for i, value in enumerate(result.registers):
                                results.append({
                                    'address': address + i,
                                    'value': value,
                                    'type': 'holding_register'
                                })
                except Exception as e:
                    logger.debug(f"Error reading {addr_type} at {address}: {e}")

        finally:
            self.disconnect()

        return results


class NetworkScanner:
    """Network scanner for Modbus TCP devices"""

    @staticmethod
    def get_local_network():
        """Get local network CIDR"""
        try:
            # Get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()

            # Assume /24 network
            network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
            return str(network)
        except:
            return "192.168.1.0/24"

    @staticmethod
    def scan_network(network=None, ports=[502, 510], timeout=1, auto_detect=True):
        """
        Scan network for Modbus devices with automatic device type detection

        Args:
            network: Network CIDR (e.g. '192.168.1.0/24'), auto-detected if None
            ports: List of ports to scan (default: [502, 510])
            timeout: Connection timeout in seconds
            auto_detect: Automatically detect device type and scan registers
        """
        if network is None:
            network = NetworkScanner.get_local_network()

        logger.info(f"Scanning network {network} for Modbus devices...")
        devices = []

        try:
            net = ipaddress.IPv4Network(network, strict=False)

            for ip in net.hosts():
                ip_str = str(ip)

                for port in ports:
                    try:
                        # Quick TCP port check
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(timeout)
                        result = sock.connect_ex((ip_str, port))
                        sock.close()

                        if result == 0:
                            # Port is open, try Modbus connection
                            scanner = ModbusScanner(ip_str, port, timeout=3)
                            if scanner.test_connection():
                                device_info = {
                                    'ip': ip_str,
                                    'port': port,
                                    'status': 'online'
                                }

                                if auto_detect:
                                    # Automatically detect device type
                                    logger.info(f"Auto-detecting device type at {ip_str}:{port}...")
                                    device_type = scanner.detect_device_type(slave=1)
                                    device_info['device_type'] = device_type

                                    # Auto-generate device name
                                    if device_type in ['LOGO_8', 'LOGO_0BA7']:
                                        device_info['name'] = f"LOGO_{ip_str.split('.')[-1]}"
                                        device_info['manufacturer'] = 'Siemens'
                                        device_info['model'] = 'LOGO! 8' if device_type == 'LOGO_8' else 'LOGO! 0BA7'
                                    else:
                                        device_info['name'] = f"Modbus_{ip_str.split('.')[-1]}"
                                        device_info['manufacturer'] = 'Generic'
                                        device_info['model'] = 'Modbus TCP'

                                devices.append(device_info)
                                logger.info(f"Found {device_info.get('device_type', 'unknown')} device at {ip_str}:{port}")
                    except Exception as e:
                        logger.debug(f"Error scanning {ip_str}:{port}: {e}")

        except Exception as e:
            logger.error(f"Network scan error: {e}")

        logger.info(f"Network scan complete. Found {len(devices)} devices.")
        return devices

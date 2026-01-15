"""
Modbus Scanner for automatic device discovery
"""
import logging
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

logger = logging.getLogger(__name__)


class ModbusScanner:
    """Scanner for Modbus devices"""

    def __init__(self, host, port=502, timeout=5):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.client = None

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
            self.client.close()
            logger.info(f"Disconnected from {self.host}:{self.port}")

    def scan_coils(self, start_address=0, count=100, slave=1):
        """Scan coils (digital outputs)"""
        available = []
        try:
            result = self.client.read_coils(start_address, count, slave=slave)
            if not result.isError():
                for i, bit in enumerate(result.bits[:count]):
                    available.append({
                        'address': start_address + i,
                        'value': bit,
                        'type': 'coil'
                    })
                logger.info(f"Found {len(available)} coils starting at {start_address}")
        except Exception as e:
            logger.error(f"Error scanning coils: {e}")
        return available

    def scan_discrete_inputs(self, start_address=0, count=100, slave=1):
        """Scan discrete inputs (digital inputs)"""
        available = []
        try:
            result = self.client.read_discrete_inputs(start_address, count, slave=slave)
            if not result.isError():
                for i, bit in enumerate(result.bits[:count]):
                    available.append({
                        'address': start_address + i,
                        'value': bit,
                        'type': 'discrete_input'
                    })
                logger.info(f"Found {len(available)} discrete inputs starting at {start_address}")
        except Exception as e:
            logger.error(f"Error scanning discrete inputs: {e}")
        return available

    def scan_holding_registers(self, start_address=0, count=100, slave=1):
        """Scan holding registers"""
        available = []
        try:
            result = self.client.read_holding_registers(start_address, count, slave=slave)
            if not result.isError():
                for i, value in enumerate(result.registers):
                    available.append({
                        'address': start_address + i,
                        'value': value,
                        'type': 'holding_register'
                    })
                logger.info(f"Found {len(available)} holding registers starting at {start_address}")
        except Exception as e:
            logger.error(f"Error scanning holding registers: {e}")
        return available

    def scan_input_registers(self, start_address=0, count=100, slave=1):
        """Scan input registers"""
        available = []
        try:
            result = self.client.read_input_registers(start_address, count, slave=slave)
            if not result.isError():
                for i, value in enumerate(result.registers):
                    available.append({
                        'address': start_address + i,
                        'value': value,
                        'type': 'input_register'
                    })
                logger.info(f"Found {len(available)} input registers starting at {start_address}")
        except Exception as e:
            logger.error(f"Error scanning input registers: {e}")
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
                        reg.get('count', 100),
                        slave
                    )

                if 'digital_inputs' in registers:
                    reg = registers['digital_inputs']
                    results['discrete_inputs'] = self.scan_discrete_inputs(
                        reg.get('start_address', 0),
                        reg.get('count', 100),
                        slave
                    )

                if 'analog_outputs' in registers or 'holding_registers' in registers:
                    reg_key = 'analog_outputs' if 'analog_outputs' in registers else 'holding_registers'
                    reg = registers[reg_key]
                    results['holding_registers'] = self.scan_holding_registers(
                        reg.get('start_address', 0),
                        reg.get('count', 100),
                        slave
                    )

                if 'analog_inputs' in registers or 'input_registers' in registers:
                    reg_key = 'analog_inputs' if 'analog_inputs' in registers else 'input_registers'
                    reg = registers[reg_key]
                    results['input_registers'] = self.scan_input_registers(
                        reg.get('start_address', 0),
                        reg.get('count', 100),
                        slave
                    )
            else:
                # Generic scan
                results['coils'] = self.scan_coils(0, 100, slave)
                results['discrete_inputs'] = self.scan_discrete_inputs(0, 100, slave)
                results['holding_registers'] = self.scan_holding_registers(0, 100, slave)
                results['input_registers'] = self.scan_input_registers(0, 100, slave)

        finally:
            self.disconnect()

        return results

    def test_connection(self):
        """Test connection to device"""
        if self.connect():
            self.disconnect()
            return True
        return False

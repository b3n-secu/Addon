"""
Automatic Register Scanner for Modbus and S7 Devices
Scans available registers and reports status
"""

import logging
from typing import Dict, List, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class RegisterStatus(Enum):
    """Register availability status"""
    AVAILABLE = "available"  # Yellow dot - register exists and readable
    ERROR = "error"  # Black dot - register doesn't exist or read error
    UNTESTED = "untested"  # Gray dot - not yet tested


class RegisterType(Enum):
    """Modbus register types"""
    COIL = "coil"  # Digital outputs (FC01, FC05, FC15)
    DISCRETE_INPUT = "discrete_input"  # Digital inputs (FC02)
    INPUT_REGISTER = "input_register"  # Analog inputs (FC04)
    HOLDING_REGISTER = "holding_register"  # Analog outputs (FC03, FC06, FC16)


class RegisterScanner:
    """Automatic register scanner for Modbus devices"""

    def __init__(self, host: str, port: int = 502, slave_id: int = 1, timeout: int = 2):
        self.host = host
        self.port = port
        self.slave_id = slave_id
        self.timeout = timeout

    def scan_all_registers(
        self,
        coil_range: Tuple[int, int] = (0, 100),
        discrete_range: Tuple[int, int] = (0, 100),
        input_range: Tuple[int, int] = (0, 100),
        holding_range: Tuple[int, int] = (0, 100),
        batch_size: int = 10
    ) -> Dict[RegisterType, Dict[int, RegisterStatus]]:
        """
        Scan all register types

        Args:
            coil_range: (start, end) for coils
            discrete_range: (start, end) for discrete inputs
            input_range: (start, end) for input registers
            holding_range: (start, end) for holding registers
            batch_size: Number of registers to read in one request

        Returns:
            Dict mapping RegisterType to {address: status}
        """
        results = {
            RegisterType.COIL: {},
            RegisterType.DISCRETE_INPUT: {},
            RegisterType.INPUT_REGISTER: {},
            RegisterType.HOLDING_REGISTER: {}
        }

        logger.info(f"Starting register scan for {self.host}:{self.port}")

        # Scan coils
        logger.info("Scanning coils...")
        results[RegisterType.COIL] = self._scan_coils(coil_range[0], coil_range[1], batch_size)

        # Scan discrete inputs
        logger.info("Scanning discrete inputs...")
        results[RegisterType.DISCRETE_INPUT] = self._scan_discrete_inputs(
            discrete_range[0], discrete_range[1], batch_size
        )

        # Scan input registers
        logger.info("Scanning input registers...")
        results[RegisterType.INPUT_REGISTER] = self._scan_input_registers(
            input_range[0], input_range[1], batch_size
        )

        # Scan holding registers
        logger.info("Scanning holding registers...")
        results[RegisterType.HOLDING_REGISTER] = self._scan_holding_registers(
            holding_range[0], holding_range[1], batch_size
        )

        # Log summary
        total_available = sum(
            sum(1 for status in regs.values() if status == RegisterStatus.AVAILABLE)
            for regs in results.values()
        )
        logger.info(f"Register scan complete. Found {total_available} available registers.")

        return results

    def _scan_coils(self, start: int, end: int, batch_size: int) -> Dict[int, RegisterStatus]:
        """Scan coils (FC01)"""
        try:
            from pymodbus.client import ModbusTcpClient

            client = ModbusTcpClient(self.host, port=self.port, timeout=self.timeout)
            if not client.connect():
                logger.error(f"Failed to connect to {self.host}:{self.port}")
                return {}

            results = {}

            for addr in range(start, end, batch_size):
                count = min(batch_size, end - addr)
                try:
                    response = client.read_coils(addr, count, slave=self.slave_id)
                    if not response.isError():
                        # All registers in this batch are available
                        for i in range(count):
                            results[addr + i] = RegisterStatus.AVAILABLE
                    else:
                        # Mark all as error
                        for i in range(count):
                            results[addr + i] = RegisterStatus.ERROR
                except Exception as e:
                    logger.debug(f"Error reading coils at {addr}: {e}")
                    for i in range(count):
                        results[addr + i] = RegisterStatus.ERROR

            client.close()
            return results

        except ImportError:
            logger.error("pymodbus not available")
            return {}
        except Exception as e:
            logger.error(f"Error scanning coils: {e}")
            return {}

    def _scan_discrete_inputs(self, start: int, end: int, batch_size: int) -> Dict[int, RegisterStatus]:
        """Scan discrete inputs (FC02)"""
        try:
            from pymodbus.client import ModbusTcpClient

            client = ModbusTcpClient(self.host, port=self.port, timeout=self.timeout)
            if not client.connect():
                return {}

            results = {}

            for addr in range(start, end, batch_size):
                count = min(batch_size, end - addr)
                try:
                    response = client.read_discrete_inputs(addr, count, slave=self.slave_id)
                    if not response.isError():
                        for i in range(count):
                            results[addr + i] = RegisterStatus.AVAILABLE
                    else:
                        for i in range(count):
                            results[addr + i] = RegisterStatus.ERROR
                except Exception as e:
                    logger.debug(f"Error reading discrete inputs at {addr}: {e}")
                    for i in range(count):
                        results[addr + i] = RegisterStatus.ERROR

            client.close()
            return results

        except Exception as e:
            logger.error(f"Error scanning discrete inputs: {e}")
            return {}

    def _scan_input_registers(self, start: int, end: int, batch_size: int) -> Dict[int, RegisterStatus]:
        """Scan input registers (FC04)"""
        try:
            from pymodbus.client import ModbusTcpClient

            client = ModbusTcpClient(self.host, port=self.port, timeout=self.timeout)
            if not client.connect():
                return {}

            results = {}

            for addr in range(start, end, batch_size):
                count = min(batch_size, end - addr)
                try:
                    response = client.read_input_registers(addr, count, slave=self.slave_id)
                    if not response.isError():
                        for i in range(count):
                            results[addr + i] = RegisterStatus.AVAILABLE
                    else:
                        for i in range(count):
                            results[addr + i] = RegisterStatus.ERROR
                except Exception as e:
                    logger.debug(f"Error reading input registers at {addr}: {e}")
                    for i in range(count):
                        results[addr + i] = RegisterStatus.ERROR

            client.close()
            return results

        except Exception as e:
            logger.error(f"Error scanning input registers: {e}")
            return {}

    def _scan_holding_registers(self, start: int, end: int, batch_size: int) -> Dict[int, RegisterStatus]:
        """Scan holding registers (FC03)"""
        try:
            from pymodbus.client import ModbusTcpClient

            client = ModbusTcpClient(self.host, port=self.port, timeout=self.timeout)
            if not client.connect():
                return {}

            results = {}

            for addr in range(start, end, batch_size):
                count = min(batch_size, end - addr)
                try:
                    response = client.read_holding_registers(addr, count, slave=self.slave_id)
                    if not response.isError():
                        for i in range(count):
                            results[addr + i] = RegisterStatus.AVAILABLE
                    else:
                        for i in range(count):
                            results[addr + i] = RegisterStatus.ERROR
                except Exception as e:
                    logger.debug(f"Error reading holding registers at {addr}: {e}")
                    for i in range(count):
                        results[addr + i] = RegisterStatus.ERROR

            client.close()
            return results

        except Exception as e:
            logger.error(f"Error scanning holding registers: {e}")
            return {}


class S7RegisterScanner:
    """Automatic register scanner for S7 devices"""

    def __init__(self, host: str, port: int = 102, tsap_src: int = 0x0100, tsap_dst: int = 0x2000):
        self.host = host
        self.port = port
        self.tsap_src = tsap_src
        self.tsap_dst = tsap_dst

    def scan_registers(self) -> Dict[str, Dict[str, RegisterStatus]]:
        """
        Scan S7 memory areas

        Returns:
            Dict mapping memory area to {address: status}
        """
        results = {
            'inputs': {},  # I (Digital Inputs)
            'outputs': {},  # Q (Digital Outputs)
            'markers': {},  # M (Merkers)
            'data_blocks': {},  # DB (Data Blocks)
            'analog_inputs': {},  # AI
            'analog_outputs': {}  # AQ
        }

        try:
            from s7_client import S7Client, SNAP7_AVAILABLE

            if not SNAP7_AVAILABLE:
                logger.warning("S7 client not available")
                return results

            with S7Client(self.host, self.port, self.tsap_src, self.tsap_dst) as client:
                if not client.connect():
                    logger.error(f"Failed to connect to S7 device at {self.host}:{self.port}")
                    return results

                # Scan digital inputs (typical LOGO! range: I1-I24)
                for i in range(1, 25):
                    addr = f"V{i}"
                    try:
                        value = client.read_vm(addr)
                        if value is not None:
                            results['inputs'][addr] = RegisterStatus.AVAILABLE
                        else:
                            results['inputs'][addr] = RegisterStatus.ERROR
                    except Exception:
                        results['inputs'][addr] = RegisterStatus.ERROR

                logger.info(f"S7 register scan complete for {self.host}")

        except ImportError:
            logger.warning("S7 client not available for scanning")
        except Exception as e:
            logger.error(f"Error scanning S7 registers: {e}")

        return results


def format_register_map(results: Dict, show_errors: bool = False) -> str:
    """
    Format register scan results as human-readable string

    Args:
        results: Results from scan_all_registers()
        show_errors: Include error registers in output

    Returns:
        Formatted string
    """
    output = []

    for reg_type, registers in results.items():
        available = [addr for addr, status in registers.items() if status == RegisterStatus.AVAILABLE]
        errors = [addr for addr, status in registers.items() if status == RegisterStatus.ERROR]

        output.append(f"\n{reg_type.value}:")
        output.append(f"  Available: {len(available)} registers")

        if available:
            # Group consecutive addresses
            groups = []
            start = available[0]
            end = available[0]

            for addr in available[1:]:
                if addr == end + 1:
                    end = addr
                else:
                    groups.append((start, end))
                    start = addr
                    end = addr

            groups.append((start, end))

            output.append("  Ranges:")
            for start, end in groups:
                if start == end:
                    output.append(f"    {start}")
                else:
                    output.append(f"    {start}-{end}")

        if show_errors and errors:
            output.append(f"  Errors: {len(errors)} registers")

    return '\n'.join(output)

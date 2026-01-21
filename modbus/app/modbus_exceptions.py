"""
Custom exceptions for Modbus operations
Based on best practices from integration_blueprint
"""


class ModbusError(Exception):
    """Base exception for all Modbus-related errors"""
    def __init__(self, message, details=None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_dict(self):
        """Convert exception to API-friendly dictionary"""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'details': self.details
        }


class ModbusConnectionError(ModbusError):
    """Raised when connection to Modbus device fails"""
    pass


class ModbusTimeoutError(ModbusConnectionError):
    """Raised when Modbus operation times out"""
    pass


class ModbusInvalidAddressError(ModbusError):
    """Raised when attempting to access invalid register address"""
    pass


class ModbusReadError(ModbusError):
    """Raised when read operation fails"""
    pass


class ModbusWriteError(ModbusError):
    """Raised when write operation fails"""
    pass


class DeviceProfileNotFoundError(ModbusError):
    """Raised when device profile is not found"""
    pass


class ConfigurationError(ModbusError):
    """Raised when configuration is invalid"""
    pass


class DeviceNotFoundError(ModbusError):
    """Raised when device is not found in configuration"""
    pass


class InvalidSlaveIdError(ModbusError):
    """Raised when slave ID is invalid (must be 1-247)"""
    pass


class RegisterCountError(ModbusError):
    """Raised when register count exceeds device limits"""
    pass


# Error code mapping for API responses
ERROR_CODES = {
    ModbusConnectionError: 'CONNECTION_FAILED',
    ModbusTimeoutError: 'TIMEOUT',
    ModbusInvalidAddressError: 'INVALID_ADDRESS',
    ModbusReadError: 'READ_FAILED',
    ModbusWriteError: 'WRITE_FAILED',
    DeviceProfileNotFoundError: 'PROFILE_NOT_FOUND',
    ConfigurationError: 'INVALID_CONFIG',
    DeviceNotFoundError: 'DEVICE_NOT_FOUND',
    InvalidSlaveIdError: 'INVALID_SLAVE_ID',
    RegisterCountError: 'INVALID_REGISTER_COUNT'
}


def get_error_code(exception):
    """Get error code for exception"""
    return ERROR_CODES.get(type(exception), 'UNKNOWN_ERROR')


def create_error_response(exception):
    """Create standardized error response from exception"""
    if isinstance(exception, ModbusError):
        return {
            'success': False,
            'error_type': exception.__class__.__name__,
            'error_code': get_error_code(exception),
            'message': exception.message,
            'details': exception.details
        }
    else:
        # Generic exception
        return {
            'success': False,
            'error_type': 'UnknownError',
            'error_code': 'UNKNOWN_ERROR',
            'message': str(exception),
            'details': {}
        }

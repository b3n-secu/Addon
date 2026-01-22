# Changelog

## Version 1.6.1 (2026-01-22)

### Critical Bug Fixes

- 🐛 **FINAL FIX: JSON parse error in web interface** - Completely resolved "unexpected non-whitespace character after JSON data at line 1 column 4"
  - **Root cause identified**: Logging output was mixing with HTTP responses (stdout contamination)
  - **Solution**: Redirected ALL logs to stderr instead of stdout
  - Configured Python logging to use `sys.stderr` stream
  - Reconfigured Flask/Werkzeug loggers to prevent stdout contamination
  - Enhanced `/api/devices` endpoint with robust validation and error handling
  - Fixed logging initialization order (BEFORE any module imports)

### Technical Changes

- 🔧 **Logging Configuration**:
  - Moved `logging.basicConfig()` to the top of both `app/app.py` and `modbus/app/app.py`
  - Added `stream=sys.stderr` to all logging configurations
  - Configured Werkzeug logger to explicitly use stderr
  - Prevents log messages from mixing with JSON responses

- 🛡️ **Enhanced API Validation**:
  - Added type checking in `/api/devices` GET endpoint
  - Validates `devices` is always a proper list
  - Filters out invalid device entries
  - Returns empty array instead of errors for better UX

- 📊 **Import Order Fix**:
  - Logging configuration now runs BEFORE optional module imports
  - Changed `logging.warning()` to `logger.warning()` after logger initialization

### Impact

This fix resolves the persistent JSON parse error that was preventing the web interface from loading device lists. The issue was caused by logging output mixing with HTTP response data when logs were written to stdout. By redirecting all logging to stderr, JSON responses remain clean and parseable.

---

## Version 1.6.0a (2026-01-22)

### Critical Bug Fixes

- 🐛 **FIXED: JSON parse error in web interface** - Resolved "unexpected non-whitespace character after JSON data at line 1 column 4"
  - Added missing `save_config()` call in `/api/scan-network` endpoint
  - Enhanced data validation in `/api/devices` endpoint
  - Improved error handling in `load_config()` function
  - Added proper type checking for device list integrity

### Improvements

- 🔧 **Enhanced data integrity**: Added validation to ensure devices list is always properly structured
- 🛡️ **Better error handling**: Graceful handling of corrupted config files
- 📊 **Improved logging**: More detailed error messages for troubleshooting
- ✅ **Config persistence**: Automatic save after network scan device addition

### Technical Changes

- Added JSON validation for device data structures
- Enhanced exception handling in API endpoints
- Improved config file validation on load
- Better error recovery from malformed data

---

## Version 1.5.0c (2026-01-22)

### Bug Fixes

- 🐛 Fixed JSON parse error in web interface ("unexpected non-whitespace character")
- 🔧 Synchronized device_profiles.py between app/ and modbus/app/
- ✅ Corrected device profile structure (LOGO! 8 (0BA8), S7 PLC)
- 📝 Improved device profile documentation and notes

### Technical Changes

- 🔄 Unified device profiles across all modules
- 🏗️ Added S7-300, S7-400, S7-1200, S7-1500 PLC profiles
- 📊 Enhanced Siemens PLC support with comprehensive register mappings

---

## Version 1.5.0b (2026-01-22)

### Major Features

**LOGO! 8 Enhanced Support:**
- ✅ Added missing Siemens LOGO! 8 registers:
  - **Merker (M)**: M1-M64 → Modbus Coil 8257-8320
  - **Variable Words (VW)**: VW0-VW848 → Holding Registers 1-425
  - **Analog Merker (AM)**: AM1-AM64 → Holding Registers 529-592
  - **Network Inputs (NI)**: NI1-NI64 → Discrete Inputs 0-63
  - **Network Outputs (NQ)**: NQ1-NQ64 → Coils 0-63
- 📊 Complete LOGO! 8 Modbus register mapping based on official specifications

**LOGO! v7 S7 Protocol Support:**
- 🔧 Added S7 protocol support for LOGO! v7/0BA7 devices
- 📦 Integrated python-snap7 library for S7 communication
- 🔌 S7Client class with VM address support (V, VW, VB, M, MB, IB, QB)
- ⚠️ Warning messages for LOGO! v7 users about S7-only protocol
- 📖 Comprehensive S7 integration guide (LOGO_V7_S7_INTEGRATION.md)
- 🎯 LOGO! Soft Comfort export configuration examples
- 🔍 TSAP configuration (Client 01.00 + Server 20.00)

**Technical Improvements:**
- 🐳 Fixed Docker base image (switched from base-python:3.11 to base:3.19)
- 📦 Added python-snap7==1.3 to dependencies
- 🔧 Updated Dockerfile for improved build reliability
- 📝 Enhanced device profiles with protocol warnings

### Documentation

- 📚 New: LOGO_V7_S7_INTEGRATION.md - Complete S7 integration guide
- 📖 Updated: LOGO_COMPATIBILITY.md - LOGO! v7 vs v8 comparison
- 📝 VM address mapping tables and examples
- 🔍 Troubleshooting guide for S7 connections
- 💡 Best practices for address planning

### Bug Fixes

- 🐛 Fixed version number in config.yaml (was 1.1.0, now 1.5.0b)
- 🐛 Fixed Docker build error with missing base image
- 🐛 Removed image field from config.yaml to enable local builds

### Breaking Changes

- ⚠️ LOGO! v7/0BA7 now correctly marked as S7-only (Port 102)
- ⚠️ Base image changed from base-python to base (Alpine 3.19)

---

## Version 1.0.0 (2026-01-14)

### Initial Release

**Features:**
- 🎯 Universeller Modbus Konfigurator für Home Assistant
- 🏭 Unterstützung für mehrere Hersteller:
  - Siemens (LOGO! 7, LOGO! 8)
  - Schneider Electric (Modicon M221)
  - ABB (AC500)
  - Wago (750 Series)
  - Generic Modbus TCP
- 🖥️ Benutzerfreundliches Web-Interface
- 🔍 Automatische Geräteerkennung (Device Scanner)
- 📝 Automatische YAML-Konfigurationsgenerierung
- ✅ Verbindungstest für Geräte
- 🎨 Modernes, responsives UI-Design
- 📊 Mehrere Geräte gleichzeitig konfigurierbar
- 🔧 Anpassbare Register-Konfiguration

**Supported Device Types:**
- Analog Inputs (Input Registers)
- Analog Outputs (Holding Registers)
- Digital Inputs (Discrete Inputs)
- Digital Outputs (Coils)

**Technical:**
- Python 3.11 Backend
- Flask Web Framework
- PyModbus für Modbus-Kommunikation
- Responsive HTML/CSS/JavaScript Frontend
- RESTful API
- Docker Container

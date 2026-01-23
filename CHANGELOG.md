# Changelog

## Version 1.6.3 (2026-01-23)

### Major New Features

- 🔍 **S7 Protocol Detection for LOGO! v7** - Complete S7comm implementation for automatic LOGO! v7/0BA7 detection
  - Full S7comm protocol stack (TPKT, COTP, S7comm)
  - Port 102 scanning and device identification
  - TSAP (Transport Service Access Point) support
  - 3-step connection: TCP → COTP Connect → S7comm Setup
  - Automatic PDU size negotiation
  - Device type identification (LOGO! v7, S7-300, S7-400)

### New S7 Scanner Module (s7_scanner.py)

**Protocol Implementation:**
- TPKT (RFC 1006) - ISO transport services on TCP
- COTP (ISO 8073) - Connection-Oriented Transport Protocol
- S7comm - Siemens proprietary protocol (Protocol ID: 0x32)
- Complete packet creation and parsing
- Error handling for all connection steps

**TSAP Support:**
- Create TSAP from communication type, rack, and slot
- Default TSAPs: 0x0100 (PG/local), 0x2000 (OP/LOGO!)
- Helper function: `S7Scanner.create_tsap(comm_type, rack, slot)`
- Automatic device identification based on TSAP and PDU size

**Device Detection:**
- **LOGO! v7 (0BA7)**: PDU size 480, TSAP 0x2000, Port 102
- **S7-300 Series**: Variable PDU, rack/slot based TSAP
- **S7-400 Series**: Large PDU, rack/slot identification
- **Unknown S7 devices**: Generic identification

### New API Endpoints

**POST /api/scan-s7** - Scan single IP for S7 protocol
```json
Request: {
  "host": "192.168.178.201",
  "port": 102,
  "timeout": 5
}

Response: {
  "success": true,
  "device_type": "LOGO! v7 (0BA7)",
  "pdu_size": 480,
  "tsap_src": 256,
  "tsap_dst": 512
}
```

**POST /api/scan-network-s7** - Scan network for S7 devices
```json
Request: {
  "network": "192.168.178.0/24",
  "timeout": 2,
  "auto_add": false
}

Response: {
  "success": true,
  "devices": [...],
  "total": 3,
  "scan_method": "s7comm"
}
```

### Bug Fixes

- 🐛 **Missing requests dependency** - Fixed ModuleNotFoundError causing startup failure
  - Added requests==2.31.0 to Dockerfile
  - Added requests==2.31.0 to app/requirements.txt
  - NetworkDetector module now works correctly

### Documentation

- 📚 **S7_DETECTION.md** - Comprehensive S7 protocol documentation (610 lines)
  - Protocol stack explanation (OSI layers)
  - S7comm connection establishment steps
  - TSAP structure and examples
  - Device identification methods
  - API endpoint documentation with examples
  - Troubleshooting guide
  - Implementation details (packet structures)
  - References to RFCs and Wireshark Wiki

### Technical Details

**S7comm Connection Sequence:**
1. TCP SYN to port 102
2. COTP Connect Request (0xE0) with TSAP parameters
3. COTP Connect Confirm (0xD0) from device
4. S7comm Setup (Function 0xF0) with PDU negotiation
5. S7comm Ack_Data (ROSCTR 0x03) with negotiated parameters

**TSAP Structure (2 bytes):**
- Byte 1: Communication Type (1=PG, 2=OP, 3=S7 Basic)
- Byte 2: Rack (bits 5-7) + Slot (bits 0-4)

**Example TSAP Values:**
- 0x0100: PG communication, Rack 0, Slot 0 (Local)
- 0x2000: OP communication, Rack 0, Slot 0 (LOGO! v7)
- 0x0102: PG communication, Rack 0, Slot 2 (S7-300)

### Files Added

- app/s7_scanner.py: Complete S7 scanner implementation (845 lines)
- modbus/app/s7_scanner.py: Copy for modbus directory
- S7_DETECTION.md: Comprehensive S7 protocol documentation

### Files Modified

- app/app.py: Added S7 scanner imports and API endpoints
- modbus/app/app.py: Added S7 scanner imports and API endpoints
- Dockerfile: Added requests==2.31.0 dependency
- modbus/Dockerfile: Added requests==2.31.0 and python-snap7==1.3
- app/requirements.txt: Added requests==2.31.0
- config.yaml: Version bumped to 1.6.3
- modbus/config.yaml: Version bumped to 1.6.3

### Benefits

✅ Automatic LOGO! v7 detection (distinguishes from LOGO! v8)
✅ No manual configuration needed for LOGO! v7 devices
✅ Support for S7-300/400 PLCs
✅ Network-wide discovery of S7 devices
✅ Professional protocol implementation based on Wireshark specification
✅ Extensible for future S7 communication features
✅ Startup issues resolved (requests dependency added)

### Impact

This release enables:
- Automatic detection of LOGO! v7/0BA7 devices on port 102
- Clear distinction between LOGO! v7 (S7 only) and LOGO! v8 (Modbus)
- Professional S7comm protocol support
- Network scanning for all S7-compatible devices
- Addon starts without errors (requests dependency fixed)

---

## Version 1.6.2 (2026-01-23)

### Critical Bug Fixes

- 🐛 **YAML Configuration Errors Fixed** - Resolved critical YAML syntax errors in modbus.yaml
  - Fixed incorrect indentation on device properties (type, host, port, timeout)
  - Corrected inconsistent list indentation in sensors, binary_sensors, and switches
  - Standardized all device entries to start at column 0
  - Fixed duplicate register address 13 (changed I21 to address 21 as per naming)
  - All YAML syntax now validates correctly with Python yaml.safe_load()

- 🐛 **JSON Parse Error Improvements** - Enhanced robustness of device loading API
  - Improved load_config() with explicit JSON decode error handling
  - Added validation that loaded data is always a list before assignment
  - Enhanced save_config() to test each device for JSON serializability
  - Hardened api_get_devices() endpoint with explicit Content-Type headers
  - All API responses now return valid JSON with correct headers

### New Features

- 🌐 **Network Info Display Widget** - Restored missing network information display
  - Added NetworkDetector module for automatic network detection
  - New /api/network-info endpoint for Docker/Home Assistant environments
  - Widget displays: IP, Netmask, Gateway, DNS, and Scan Range
  - Works correctly with internal Docker IP ranges
  - Uses Home Assistant Supervisor API when available
  - Graceful fallback to system commands (ip, /etc/resolv.conf)
  - Modern UI widget positioned in bottom-left corner

### Code Quality Improvements

- 🔧 **Exception Handling** - Replaced ~30 bare `except:` clauses with `except Exception as e:`
  - Affects: app/modbus_scanner.py, modbus/app/modbus_scanner.py
  - Improved debugging and error tracking capabilities

- 📦 **Import Organization** - Moved deferred imports to module level
  - Fixed `import yaml` statements in app/app.py and modbus/app/app.py
  - Prevents potential runtime errors and follows Python best practices

- 🔢 **Version Standardization** - All version references now consistently show 1.6.2
  - Updated config.yaml, modbus/config.yaml
  - Updated version strings in app/app.py, modbus/app/app.py

### Technical Changes

- Enhanced logging with stack traces for better debugging
- Improved data validation in configuration loading
- Better error recovery from corrupted config files
- Frontend now includes network info widget with auto-refresh
- Skips docker/veth/loopback interfaces in network detection
- Calculates network scan range automatically

### Files Changed

- app/app.py: Added NetworkDetector import and /api/network-info endpoint
- app/static/index.html: Enhanced with network info widget (545 new lines)
- app/network_detector.py: New file for network detection
- app/modbus_scanner.py: Improved exception handling
- modbus/app/app.py: Enhanced API endpoints and error handling
- modbus/app/modbus_scanner.py: Improved exception handling
- modbus.yaml: Fixed all YAML syntax errors
- config.yaml, modbus/config.yaml: Version bumped to 1.6.2

### Impact

This release fixes critical issues that prevented proper operation:
- YAML configuration now loads without errors in Home Assistant
- Device list API no longer returns parse errors
- Network information is visible to users
- Code quality significantly improved for maintainability

---

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

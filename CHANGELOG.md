# Changelog

## Version 1.7.7 (2026-01-23)

### Critical Bug Fixes

- 🐛 **Auto-Add All Devices Fixed** - Found devices now automatically added regardless of detection status
  - **Problem**: Devices without detected manufacturer/model (e.g., "Device_45") were not automatically added to configuration despite checkbox being checked
  - **Root cause**: Backend required 'manufacturer' and 'model' fields to be present for auto-add
  - **Solution**:
    - Remove manufacturer/model requirement for auto-add
    - Use default values: manufacturer='Generic', model='Modbus TCP'
    - Add duplicate detection to prevent adding same device twice (checks host:port)
    - Use `.get()` for safe field access with defaults

### Technical Changes

- Modified `api_scan_network()` and `api_scan_network_nmap()` in both `app/app.py` and `modbus/app/app.py`
- Changed from: `if 'manufacturer' in device and 'model' in device:`
- Changed to: Always add device, use `device.get('manufacturer', 'Generic')`
- Added duplicate detection: Check if host:port combination already exists
- Better error handling with safe `.get()` access

### Impact

All found devices are now automatically added to configuration when auto-add checkbox is enabled, regardless of whether manufacturer/model could be detected. This fixes the workflow where scanned devices appeared in "Gefundene Geräte" but not in "Konfigurierte Geräte".

---

## Version 1.7.6 (2026-01-23)

### UI/UX Improvements

- 🎨 **Optimized Layout - Sidebar & Inline Inputs**
  - **Button Sidebar (Left)**: All action buttons now arranged vertically in a compact sidebar
    - Cleaner, more compact button layout
    - Easy access to all main functions
    - Fixed width sidebar (250px)
  - **Inline Input Fields**: All input parameters now displayed in a single horizontal row
    - Network, Port-Range, IP-Address, Port, Slave ID all in one line
    - More space-efficient layout
    - Shorter, clearer labels
    - Tooltips removed for cleaner appearance
  - **Responsive Design**: Automatically adjusts to stacked layout on smaller screens

### Technical Changes

- Added `.main-layout` CSS class for sidebar + content grid layout
- Added `.button-sidebar` for vertical button arrangement
- Added `.input-inline-area` for inline input field layout
- Added `.inline-inputs` with 5-column grid layout
- Optimized `.checkbox-row` for compact checkbox display
- Reduced label font size to 0.8em for better fit
- Hidden small hints on desktop, shown only on mobile

### Benefits

- 💨 More compact interface with better space utilization
- 🎯 Clearer visual hierarchy with sidebar navigation
- 📱 Better responsive behavior on different screen sizes
- ✨ Cleaner, more professional appearance

### Files Changed

- `app/static/index.html`: Sidebar layout with inline inputs
- `modbus/app/static/index.html`: Same layout changes

---

## Version 1.7.5 (2026-01-23)

### UI/UX Improvements

- 🎨 **Completely Redesigned Web Interface Layout**
  - **Button Bar at Top**: All action buttons now grouped in a prominent button bar for quick access
    - Nmap Scan, Quick Scan, Register Analysis, Generate Config, View Config all in one place
  - **Input Area Below Buttons**: All input fields grouped together in a dedicated input area
    - Network range, port range, IP address, port, slave ID all in one organized section
    - Clear labels with icons for better visual guidance
  - **Three-Column Results Layout**: Results now displayed in three organized columns
    - Column 1: 🔍 Found Devices (network scan results)
    - Column 2: ⚙️ Configured Devices (device list)
    - Column 3: 📊 Register Analysis (analysis results)
  - **Responsive Design**: Automatically adjusts to single column on smaller screens (<1200px)

### Technical Changes

- Added new CSS classes: `.button-bar`, `.input-area`, `.three-column-layout`, `.column`
- Removed duplicate sections from old layout
- Enhanced visibility toggling for empty state placeholders
- Improved visual hierarchy with icons and consistent spacing
- Better mobile responsiveness

### Benefits

- ⚡ Faster workflow: All actions accessible from top button bar
- 👁️ Better overview: See found devices, configured devices, and analysis results at a glance
- 📱 Responsive: Works well on different screen sizes
- 🎯 Cleaner interface: Logical grouping of inputs and results
- ✨ Modern look: Enhanced visual design with icons and improved spacing

### Files Changed

- `app/static/index.html`: Complete layout restructure
- `modbus/app/static/index.html`: Same layout restructure

---

## Version 1.7.4 (2026-01-23)

### Bug Fixes

- 🐛 **Auto-Add Default Fixed** - Network scan now automatically adds found devices by default
  - **Problem**: Found devices were not automatically added to configuration despite checkbox being checked
  - **Root cause**: `auto_add` parameter defaulted to `False` in `/api/scan-network` and `/api/scan-network-nmap` endpoints
  - **Solution**: Changed default to `True` to match UI checkbox behavior
  - Fixed in `app/app.py` for both `/api/scan-network` and `/api/scan-network-nmap` endpoints

### Technical Changes

- `/api/scan-network`: Changed `auto_add = data.get('auto_add', False)` → `auto_add = data.get('auto_add', True)`
- `/api/scan-network-nmap`: Changed `auto_add = data.get('auto_add', False)` → `auto_add = data.get('auto_add', True)`
- `modbus/app/app.py` already had correct defaults

### Impact

When users perform a network scan with the "Gefundene Geräte automatisch zur Konfiguration hinzufügen" checkbox enabled (default), found devices are now correctly added to the "Konfigurierte Geräte" list automatically.

---

## Version 1.7.3 (2026-01-23)

### Release Update

- 🔄 **Version bump to ensure addon rebuild**
  - Forces Home Assistant to recognize and apply all changes from 1.7.2
  - Ensures `/data/devices.json` persistence is properly activated
  - Guarantees clean deployment of device configuration fixes

### Notes

This version contains no code changes from 1.7.2, but ensures the addon is properly rebuilt and all persistence fixes are applied.

---

## Version 1.7.2 (2026-01-23)

### Critical Bug Fixes

- 🐛 **Device Configuration Persistence Fixed** - Devices now properly saved across addon restarts
  - **Problem**: Devices added in Web UI were not saved persistently
  - **Root cause**: App was writing to `/data/options.json` which is managed by Home Assistant Supervisor and gets overwritten on restart
  - **Solution**: Use separate `/data/devices.json` file for persistent device storage
  - Automatic migration from `options.json` to `devices.json` on first run
  - Both `app/app.py` and `modbus/app/app.py` now use unified persistence approach

### Technical Changes

- Added `DEVICES_PATH = '/data/devices.json'` constant for device storage
- Updated `load_config()` to load from `devices.json` with fallback migration
- Updated `save_config()` to save directly to `devices.json`
- Device configuration now survives addon rebuilds and restarts
- Migration logic ensures existing configurations are preserved

### Impact

Users can now add devices through the Web UI and they will remain configured after addon restarts, updates, or rebuilds. This resolves the major workflow issue where device configuration was lost on every restart.

---

## Version 1.7.1 (2026-01-23)

### Bug Fixes

- 🐛 **S7 Device Auto-Add Fixed** - LOGO! v7 devices now automatically added to device list
  - Changed default `auto_add` parameter from False to True in S7 scan endpoints
  - Fixed "Keine Geräte konfiguriert" error when detecting LOGO! v7 on port 102
  - Detected S7 devices are now automatically saved to configuration
  - Single IP scan (`/api/scan-s7`) now includes auto-add functionality
  - Network scan (`/api/scan-network-s7`) also defaults to auto-add

### Technical Changes

- Modified `api_scan_s7()` function in app/app.py and modbus/app/app.py
- Auto-add logic creates device entry with protocol='s7' marker
- Device includes all S7 parameters (tsap_src, tsap_dst, pdu_size)
- Prevents duplicate device entries (checks host:port combination)
- Configuration automatically persisted with `save_config()`

### Impact

Users can now scan for LOGO! v7 devices and they will be immediately available in the device list without manual addition. This resolves the workflow issue where detected devices were not usable until manually added.

---

## Version 1.7.0 (2026-01-23)

### Major New Features - Multi-Protocol Support & Device Management

This release introduces comprehensive multi-protocol support, automatic register detection, and advanced device management capabilities.

### 🌐 Multi-Protocol Scanner (protocol_scanner.py)

**Supported Protocols:**
- ✅ **Modbus TCP** (Port 502) - Fully supported with auto-detection
- ✅ **Modbus UDP** (Port 502) - Fully supported with auto-detection
- ✅ **S7comm** (Port 102) - Siemens S7 PLCs and LOGO! v7
- ✅ **KNX/IP** (Port 3671) - Building automation (requires KNX/IP Gateway)
- ✅ **BACnet/IP** (Port 47808) - Building automation
- 🔶 **PROFINET** (Ports 34962-34964) - Detection only (requires Gateway)
- 🔶 **PROFIBUS** - Detection only (requires PROFIBUS Gateway)
- 🔶 **CANbus** - Detection only (requires CAN Gateway)
- 🔶 **CANopen** - Detection only (requires CANopen Gateway)

**Features:**
- Automatic protocol detection on network scan
- Single host or full network scanning
- Gateway detection and identification
- Protocol-specific probing and verification
- Transport protocol detection (TCP/UDP)

### 📊 Device Manager (device_manager.py)

**Device Categorization:**
- Separate management for **Modbus devices** and **S7comm devices**
- Automatic protocol detection and classification
- Device metadata tracking (manufacturer, model, connection status)
- Persistent device storage

**Device Properties:**
- Protocol type (Modbus, S7comm, etc.)
- Connection parameters (host, port, slave_id, TSAP)
- Register availability maps
- I/O configuration storage
- Last scan timestamp and status

### 🔍 Automatic Register Detection (register_scanner.py)

**Register Status Indicators:**
- 🟡 **Yellow dot (AVAILABLE)** - Register exists and is readable
- ⚫ **Black dot (ERROR)** - Register doesn't exist or read error
- ⚪ **Gray dot (UNTESTED)** - Not yet tested

**Modbus Register Scanning:**
- **Coils** (Digital Outputs) - FC01, FC05, FC15
- **Discrete Inputs** (Digital Inputs) - FC02
- **Input Registers** (Analog Inputs) - FC04
- **Holding Registers** (Analog Outputs) - FC03, FC06, FC16

**S7 Register Scanning:**
- Digital Inputs (I/Q memory areas)
- Digital Outputs (Q memory areas)
- Markers (M memory areas)
- Data Blocks (DB)
- Analog Inputs and Outputs

**Features:**
- Batch register reading for efficiency
- Configurable scan ranges
- Automatic register grouping
- Status reporting per register

### 🔧 I/O Configuration Management

**Configurable I/O Points:**
- Digital Inputs (Discrete Inputs)
- Digital Outputs (Coils)
- Analog Inputs (Input Registers)
- Analog Outputs (Holding Registers)

**Configuration Options:**
- Name/Label for each I/O point
- Register address
- Unit of measurement
- Scaling factor
- Offset value
- Device class (for Home Assistant integration)

### 📋 Device Management Features

**Device Discovery:**
1. Network-wide protocol scanning
2. Automatic device detection (Modbus, S7comm, KNX, etc.)
3. Protocol-specific device identification
4. Gateway detection for serial-based protocols

**Device Organization:**
1. **Modbus devices** → Modbus configuration category
2. **S7comm devices** → Separate S7 configuration category
3. Other protocols → Respective protocol categories

**Automatic Configuration:**
- Register scanning on device addition
- Automatic I/O point discovery
- Configuration templates based on device type
- Export to Home Assistant YAML format

### 🚀 New Capabilities

**Network Discovery:**
- Scan entire network for control devices
- Detect all protocol types simultaneously
- Identify gateway requirements
- Report connection status

**Register Management:**
- Automatic register availability testing
- Visual status indicators (yellow/black/gray dots)
- Register range optimization
- Error detection and reporting

**Configuration Export:**
- Modbus devices → `modbus.yaml`
- S7 devices → Separate S7 configuration
- Protocol-specific configuration generation

### 📁 New Files

1. **app/protocol_scanner.py** (420 lines)
   - Multi-protocol detection engine
   - Support for 9+ industrial protocols
   - Gateway identification

2. **app/device_manager.py** (330 lines)
   - Device lifecycle management
   - Protocol categorization
   - I/O configuration storage

3. **app/register_scanner.py** (380 lines)
   - Automatic register detection
   - Modbus and S7 support
   - Status indicator system

4. **modbus/app/protocol_scanner.py** (copy)
5. **modbus/app/device_manager.py** (copy)
6. **modbus/app/register_scanner.py** (copy)

### 🔄 Modified Files

- config.yaml: Version 1.6.3 → 1.7.0
- modbus/config.yaml: Version 1.6.3 → 1.7.0
- app/app.py: API version 1.6.3 → 1.7.0
- modbus/app/app.py: API version 1.6.3 → 1.7.0

### 🎯 Technical Implementation

**Protocol Detection Process:**
1. Port scanning on target network
2. TCP/UDP probing for each protocol
3. Protocol-specific handshake verification
4. Device type identification
5. Register availability scanning
6. Configuration generation

**Register Scanning Process:**
1. Connect to device (Modbus/S7)
2. Batch-read registers in groups
3. Mark each register as AVAILABLE or ERROR
4. Generate register availability map
5. Store results in device configuration

**Gateway Detection:**
- PROFINET → Requires PROFINET Gateway
- PROFIBUS → Requires PROFIBUS Gateway
- CANbus → Requires CAN Gateway
- CANopen → Requires CANopen Gateway
- KNX → Requires KNX/IP Gateway

### 📊 Protocol Support Matrix

| Protocol | Detection | Auto-Config | Register Scan | Gateway Required |
|----------|-----------|-------------|---------------|------------------|
| Modbus TCP | ✅ Full | ✅ Full | ✅ Full | ❌ No |
| Modbus UDP | ✅ Full | ✅ Full | ✅ Full | ❌ No |
| S7comm | ✅ Full | ✅ Full | ✅ Full | ❌ No |
| KNX/IP | ✅ Full | 🔶 Partial | ❌ No | ✅ Yes |
| BACnet/IP | ✅ Full | 🔶 Partial | ❌ No | ❌ No |
| PROFINET | 🔶 Detection | ❌ No | ❌ No | ✅ Yes |
| PROFIBUS | 🔶 Detection | ❌ No | ❌ No | ✅ Yes |
| CANbus | 🔶 Detection | ❌ No | ❌ No | ✅ Yes |
| CANopen | 🔶 Detection | ❌ No | ❌ No | ✅ Yes |

### ✅ Benefits

- **Universal Protocol Support**: Detect and identify multiple industrial protocols
- **Intelligent Categorization**: Automatic device organization by protocol type
- **Visual Feedback**: Register status indicators (yellow/black/gray dots)
- **Gateway Awareness**: Identifies when gateways are required
- **Modbus ↔ S7 Separation**: Clear distinction between Modbus and S7 devices
- **Auto-Configuration**: Reduces manual configuration effort
- **Extensible Architecture**: Easy to add new protocols

### 🔮 Future Enhancements

- Web UI for device management
- Interactive register configuration
- Protocol-specific configuration wizards
- Real-time register monitoring
- Multi-device batch operations
- Advanced gateway configuration

### 📝 Notes

This release focuses on backend infrastructure for multi-protocol support. Full UI integration will be added in future versions.

---

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

# Changelog

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

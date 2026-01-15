# 🔧 Universal Modbus Configurator

Ein Home Assistant Addon zur einfachen Konfiguration von Modbus-Geräten für Siemens LOGO! und andere Hersteller.

## Features

- 🏭 Unterstützung für mehrere Hersteller (Siemens, Schneider, ABB, Wago, Generic)
- 🖥️ Benutzerfreundliches Web-Interface
- 🔍 Automatische Geräteerkennung
- 📝 Automatische YAML-Konfigurationsgenerierung
- ✅ Verbindungstest
- 📊 Mehrere Geräte gleichzeitig verwalten

## Quick Start

1. Installieren Sie das Addon
2. Starten Sie das Addon
3. Öffnen Sie das Web-UI
4. Fügen Sie Ihre Geräte hinzu
5. Generieren Sie die Konfiguration
6. Integrieren Sie in Home Assistant

## Dokumentation

Siehe [README_ADDON.md](README_ADDON.md) für vollständige Dokumentation.

## Unterstützte Geräte

- **Siemens**: LOGO! 7, LOGO! 8
- **Schneider Electric**: Modicon M221
- **ABB**: AC500
- **Wago**: 750 Series
- **Generic**: Standard Modbus TCP

## Installation

```yaml
# In configuration.yaml
modbus: !include modbus_generated.yaml
```

## Version

1.0.0 - Initial Release

## Lizenz

MIT
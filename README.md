# 🔧 Universal Modbus Configurator (HAMCA)

Ein professionelles Home Assistant Addon zur einfachen Konfiguration von Modbus-Geräten mit automatischer Geräteerkennung.

## ✨ Features

### Automatische Geräteerkennung
- 🚀 **Professioneller Nmap-Scanner** mit modbus-discover NSE Script
- ⚡ **Quick Scan** für schnelle Ergebnisse
- 🎯 **Anpassbare Port-Ranges** (502, 510, 20000-20100, etc.)
- 🔍 **Automatische Gerätetyp-Erkennung**

### Unterstützte Hersteller
- 🟦 **Siemens**: LOGO! 8, LOGO! 0BA7
- 🟢 **Schneider Electric**: Modicon PLCs
- 🔵 **ABB**: Industrial Controllers
- 🟡 **Wago**: 750 Series
- 🔴 **Allen Bradley / Rockwell**: PLCs
- 🌐 **Generic**: Standard Modbus TCP

### Weitere Features
- 🖥️ Modernes, benutzerfreundliches Web-Interface
- 📝 Automatische YAML-Konfigurationsgenerierung
- ✅ Verbindungstest und Geräte-Validierung
- 📊 Mehrere Geräte gleichzeitig verwalten
- 🎨 Visuelle Gerätetyp-Kennzeichnung

## 🚀 Quick Start

1. **Installieren** Sie das Addon über den Add-on Store
2. **Starten** Sie das Addon
3. **Öffnen** Sie das Web-UI (wird automatisch geöffnet)
4. **Scannen** Sie Ihr Netzwerk mit einem Klick
5. **Wählen** Sie die gefundenen Geräte aus (oder Auto-Add aktivieren)
6. **Generieren** Sie die Konfiguration
7. **Integrieren** Sie in Home Assistant

## 📡 Scan-Modi

### 🚀 Nmap Scan (Empfohlen)
- Verwendet professionelles Nmap mit modbus-discover NSE Script
- Erkennt erweiterte Geräteinformationen
- Anpassbare Port-Ranges
- Basiert auf DefCon 16 Modbus Security Research

**Beispiel Port-Ranges:**
- Standard: `502,510` (schnell)
- Erweitert: `502,510,20000-20100` (empfohlen)
- Custom: `502,510,2222,44818,47808`

### ⚡ Quick Scan
- Schneller Python-basierter Scan
- Scannt Standard-Ports 502 und 510
- Ideal für bekannte Netzwerke

## 🔧 Konfiguration

### Addon-Optionen

```yaml
devices: []  # Wird automatisch gefüllt
modbus_config_path: "/config/modbus_generated.yaml"
scan_timeout: 300  # Nmap Scan Timeout in Sekunden
default_port_range: "502,510,20000-20100"  # Standard Port-Range
```

### Home Assistant Integration

```yaml
# In configuration.yaml
modbus: !include modbus_generated.yaml
```

Nach der Konfigurationsgenerierung einfach Home Assistant neu laden.

## 📖 Dokumentation

- [Vollständige Addon-Dokumentation](README_ADDON.md)
- [Build-Anleitung](BUILD.md)
- [Quick Start Guide](QUICKSTART.md)
- [Beispiele & Use Cases](EXAMPLES.md)
- [FAQ](FAQ.md)

## 🛠️ Entwicklung

### Container lokal bauen und testen

```bash
# Einfaches Build & Test
./build-and-test.sh

# Oder manuell
docker build -t universal-modbus-configurator:latest .
docker run -d -p 8099:8099 -v $(pwd)/test-config:/config universal-modbus-configurator:latest
```

Siehe [BUILD.md](BUILD.md) für Details.

## 📝 Changelog

### Version 1.1.0 (Aktuell)
- ✨ **NEU:** Professioneller Nmap-Scanner mit modbus-discover NSE Script
- ✨ **NEU:** Anpassbare Port-Ranges
- ✨ **NEU:** Erweiterte Geräteerkennung (Siemens, Schneider, ABB, Wago, Allen Bradley)
- ✨ **NEU:** Automatische Gerätetyp-Erkennung
- ✨ **NEU:** Zwei Scan-Modi (Nmap & Quick Scan)
- 🔧 Verbesserte UI mit visuellen Gerätetyp-Indikatoren
- 🔧 Graceful Fallback wenn nmap nicht verfügbar
- 🐛 Bugfixes und Performance-Verbesserungen

### Version 1.0.0
- 🎉 Initial Release
- ✅ Grundlegende Geräteerkennung
- ✅ YAML-Konfigurationsgenerierung

## 🤝 Contributing

Beiträge sind willkommen! Bitte erstellen Sie einen Pull Request.

## 📄 Lizenz

MIT License - Siehe [LICENSE](LICENSE) für Details.

## 🙏 Credits

- Basiert auf DefCon 16 Modbus Security Research
- Nmap modbus-discover NSE Script: https://nmap.org/nsedoc/scripts/modbus-discover.html
- Home Assistant Community
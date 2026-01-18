# Universal Modbus Configurator

![Logo](logo.png)

Professionelles Home Assistant Add-on für Modbus-Gerätekonfiguration mit automatischer Netzwerkerkennung.

## Über dieses Add-on

Der Universal Modbus Configurator (HAMCA) vereinfacht die Konfiguration von Modbus-Geräten in Home Assistant erheblich. Mit automatischer Geräteerkennung via Nmap und intuitiver Web-Oberfläche können Sie Modbus-Geräte binnen Minuten einrichten.

## Features

- 🚀 **Professioneller Nmap-Scanner** mit modbus-discover NSE Script
- ⚡ **Quick Scan** für schnelle Ergebnisse
- 🎯 **Anpassbare Port-Ranges** (502, 510, 20000-20100, etc.)
- 🔍 **Automatische Gerätetyp-Erkennung**
- 🌐 **Netzwerk-Scan** mit /24 CIDR-Unterstützung
- 📝 **Automatische YAML-Generierung** für Home Assistant
- 🖥️ **Modernes Web-Interface** mit Echtzeit-Feedback

## Unterstützte Geräte

- 🟦 **Siemens**: LOGO! 8, LOGO! 0BA7
- 🟢 **Schneider Electric**: Modicon PLCs
- 🔵 **ABB**: Industrial Controllers
- 🟡 **Wago**: 750 Series
- 🔴 **Allen Bradley**: Rockwell PLCs
- 🌐 **Generic**: Standard Modbus TCP

## Installation

1. Fügen Sie dieses Repository zu Ihren Add-on Repositories hinzu:
   ```
   https://github.com/b3n-secu/Addon
   ```

2. Installieren Sie "Universal Modbus Configurator"

3. Starten Sie das Add-on

4. Öffnen Sie die Web-UI

## Verwendung

### Schnellstart

1. **Netzwerk scannen**: Klicken Sie auf "🚀 Nmap Scan starten"
2. **Geräte auswählen**: Aktivieren Sie "Automatisch hinzufügen"
3. **Konfiguration generieren**: Klicken Sie auf "Konfiguration generieren"
4. **Home Assistant Integration**: Fügen Sie in `configuration.yaml` hinzu:
   ```yaml
   modbus: !include modbus_generated.yaml
   ```
5. **Neu laden**: Starten Sie Home Assistant neu oder laden Sie die Konfiguration neu

### Scan-Modi

#### 🚀 Nmap Scan (Empfohlen)
- Verwendet nmap mit modbus-discover NSE Script
- Erkennt Gerätetyp und Hersteller automatisch
- Anpassbare Port-Ranges
- Basiert auf DefCon 16 Modbus Security Research

**Port-Range Beispiele:**
- Standard: `502,510`
- Erweitert: `502,510,20000-20100`
- Custom: `502,510,2222,44818,47808`

#### ⚡ Quick Scan
- Schneller Python-basierter Scan
- Scannt Ports 502 und 510
- Ideal für bekannte Netzwerke

## Konfiguration

### Add-on Optionen

```yaml
devices: []  # Wird automatisch gefüllt
modbus_config_path: "/config/modbus_generated.yaml"
scan_timeout: 300  # Nmap Timeout in Sekunden
default_port_range: "102,502,510,20000-20100"
```

### Netzwerk-Einstellungen

Das Add-on erkennt automatisch Ihr lokales /24 Netzwerk. Sie können aber auch manuell ein Netzwerk angeben:
- `192.168.1.0/24`
- `10.0.0.0/24`
- `172.16.0.0/24`

## Generierte Konfiguration

Die generierte `modbus_generated.yaml` enthält:
- Modbus-Verbindungsparameter
- Automatisch erkannte Geräteentities
- Optimierte Scan-Intervalle
- Gerätespezifische Konfigurationen

Beispiel:
```yaml
- name: LOGO_100
  type: tcp
  host: 192.168.1.100
  port: 510
  sensors:
    - name: "LOGO AI1"
      address: 1
      input_type: input
      data_type: uint16
      scan_interval: 5
  binary_sensors:
    - name: "LOGO Q1"
      address: 8193
      input_type: coil
      scan_interval: 1
```

## Troubleshooting

### "Nmap ist nicht verfügbar"
- Das Add-on enthält nmap bereits
- Starten Sie das Add-on neu
- Prüfen Sie die Logs

### JSON Parse Fehler
- Leeren Sie Ihren Browser-Cache (Ctrl+Shift+R)
- Öffnen Sie die UI im Inkognito-Modus
- Prüfen Sie die Add-on Logs

### Keine Geräte gefunden
- Überprüfen Sie Ihre Netzwerkverbindung
- Stellen Sie sicher, dass Modbus-Geräte erreichbar sind
- Testen Sie eine andere Port-Range
- Verwenden Sie den Quick Scan für Standard-Ports

### Logs anzeigen
```bash
# In Home Assistant
Supervisor → Universal Modbus Configurator → Logs
```

## Support & Dokumentation

- [GitHub Repository](https://github.com/b3n-secu/Addon)
- [Vollständige Dokumentation](https://github.com/b3n-secu/Addon/blob/main/README.md)
- [Build-Anleitung](https://github.com/b3n-secu/Addon/blob/main/BUILD.md)
- [FAQ](https://github.com/b3n-secu/Addon/blob/main/FAQ.md)
- [Issues](https://github.com/b3n-secu/Addon/issues)

## Changelog

### Version 1.1.0
- ✨ Professioneller Nmap-Scanner
- ✨ Automatische Gerätetyp-Erkennung
- ✨ Anpassbare Port-Ranges
- ✨ Zwei Scan-Modi (Nmap & Quick Scan)
- 🔧 Verbesserte Fehlerbehandlung
- 🐛 Diverse Bugfixes

### Version 1.0.0
- 🎉 Initial Release

## Lizenz

MIT License

## Credits

- DefCon 16 Modbus Security Research
- Nmap modbus-discover NSE Script
- Home Assistant Community

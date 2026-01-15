# Universal Modbus Configurator

Home Assistant Add-on für einfache Modbus-Konfiguration.

## Über dieses Add-on

Dieses Add-on vereinfacht die Konfiguration von Modbus TCP-Geräten in Home Assistant erheblich. Anstatt YAML-Dateien manuell zu erstellen, bietet es eine benutzerfreundliche Web-Oberfläche.

## Installation

1. Fügen Sie dieses Repository zu Home Assistant hinzu
2. Installieren Sie "Universal Modbus Configurator"
3. Starten Sie das Add-on
4. Öffnen Sie das Web-UI

## Konfiguration

```yaml
devices: []
modbus_config_path: "/config/modbus_generated.yaml"
```

## Verwendung

1. Öffnen Sie das Web-UI (Port 8099)
2. Fügen Sie Ihre Modbus-Geräte hinzu
3. Generieren Sie die Konfiguration
4. Fügen Sie in `configuration.yaml` hinzu: `modbus: !include modbus_generated.yaml`
5. Starten Sie Home Assistant neu

## Support

Weitere Dokumentation im Haupt-Repository: https://github.com/b3n-secu/only_claude

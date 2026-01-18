# Device Database Documentation

## Übersicht

Die Device Database ist eine strukturierte JSON-Datenbank zur intelligenten Identifikation von Modbus-Geräten. Sie enthält Informationen über Hersteller, Gerätetypen, Port-Mappings und gerätespezifische Konfigurationen.

## Dateistruktur

```
modbus/app/
├── device_database.json     # Haupt-Datenbank (JSON)
└── device_database.py       # Python-Modul für Datenbankzugriff
```

## Features

### 1. Port-basierte Erkennung
- **Port 102**: Siemens S7 PLCs (ISO-TSAP/RFC1006)
- **Port 502**: Standard Modbus TCP
- **Port 510**: Alternativer Modbus TCP Port
- **Ports 20000-20100**: Modbus TCP/RTU Gateways
- **Port 44818**: Allen-Bradley EtherNet/IP

### 2. Hersteller-Informationen
Unterstützte Hersteller:
- **Siemens** (Deutschland): LOGO!, S7-300, S7-400, S7-1200, S7-1500
- **Schneider Electric** (Frankreich): Modicon M340, M580, Quantum
- **ABB** (Schweiz): AC500 Serie
- **Wago** (Deutschland): PFC Controller
- **Allen-Bradley** (USA): ControlLogix
- **Moxa** (Taiwan): MGate Gateways

### 3. Gerätespezifische Profile
Für bekannte Geräte werden Profile mit folgenden Informationen bereitgestellt:
- Unterstützte Modbus-Funktionscodes
- Register-Bereiche (Digital I/O, Analog I/O, Marker)
- Adressierungs-Offsets (z.B. LOGO! lg8add)
- Typische Features und Einschränkungen

### 4. Multi-Kriterien-Erkennung
Erkennungspriorität:
1. Modbus Vendor ID
2. Banner-Patterns (modbus-discover output)
3. Port-Nummer
4. Service-Banner
5. Verhaltensbasierte Erkennung

## Verwendung

### Python API

```python
from device_database import get_device_database

# Singleton-Instanz abrufen
db = get_device_database()

# Gerät anhand der Port-Nummer identifizieren
device_info = db.get_device_by_port(102)
print(f"Port 102: {device_info['manufacturer']} {device_info['default_model']}")

# Intelligente Identifikation mit mehreren Kriterien
manufacturer, model, device_type = db.identify_device(
    port=502,
    banner="LOGO! 8.3",
    modbus_info="Siemens LOGO! 8"
)
print(f"Identified: {manufacturer} {model}")

# Geräteprofil abrufen
profile = db.get_device_profile("Siemens", "LOGO! 8")
if profile:
    print(f"Modbus Support: {profile['modbus_tcp']}")
    print(f"Addressing: {profile['addressing']['type']}")

# Hersteller-Informationen
siemens_info = db.get_manufacturer_info("siemens")
print(f"Country: {siemens_info['country']}")
print(f"Website: {siemens_info['website']}")

# Empfohlene Port-Range für Scans
port_range = db.get_recommended_port_range()
print(f"Scan ports: {port_range}")  # "102,502,510,20000-20100"
```

## Neue Geräte hinzufügen

### 1. Neuen Port hinzufügen

In `device_database.json` unter `port_mappings`:

```json
{
  "port_mappings": {
    "YOUR_PORT": {
      "protocol": "Protocol Name",
      "description": "Description of what uses this port",
      "common_devices": [
        {
          "manufacturer": "Manufacturer Name",
          "device_type": "Device Type",
          "default_model": "Default Model Name",
          "modbus_support": "native|gateway|via module"
        }
      ]
    }
  }
}
```

### 2. Neuen Hersteller hinzufügen

In `device_database.json` unter `manufacturers`:

```json
{
  "manufacturers": {
    "manufacturer_key": {
      "name": "Full Manufacturer Name",
      "country": "Country",
      "website": "https://www.example.com",
      "product_lines": {
        "Product Line Name": {
          "description": "Product line description",
          "models": {
            "Model Key": {
              "full_name": "Full Model Name",
              "modbus_tcp": true,
              "default_port": 502,
              "typical_ports": [502],
              "register_ranges": {
                "digital_inputs": "Description",
                "digital_outputs": "Description"
              }
            }
          }
        }
      }
    }
  }
}
```

### 3. Banner-Patterns hinzufügen

In `device_database.json` unter `detection_rules.banner_patterns`:

```json
{
  "detection_rules": {
    "banner_patterns": {
      "your_pattern_key": ["pattern1", "pattern2", "PATTERN3"]
    }
  }
}
```

## Beispiel: Siemens LOGO! 8

```json
{
  "manufacturers": {
    "siemens": {
      "name": "Siemens",
      "product_lines": {
        "LOGO!": {
          "models": {
            "LOGO! 8": {
              "full_name": "LOGO! 8.x (e.g., 8.3, 8.4)",
              "modbus_tcp": true,
              "default_port": 502,
              "addressing": {
                "type": "offset-based",
                "offset_function": "lg8add",
                "vm_offset": 8192,
                "am_offset": 528
              },
              "register_ranges": {
                "digital_inputs": "I1-I24",
                "digital_outputs": "Q1-Q20",
                "network_inputs": "NI1-NI64",
                "network_outputs": "NQ1-NQ64",
                "analog_inputs": "AI1-AI8",
                "analog_outputs": "AQ1-AQ8",
                "markers": "M1-M64",
                "analog_markers": "AM1-AM64"
              }
            }
          }
        }
      }
    }
  }
}
```

## Testing

Nach Änderungen an der Datenbank:

```bash
# Validate JSON syntax
python3 -m json.tool modbus/app/device_database.json > /dev/null

# Test database loading
cd modbus/app
python3 -c "from device_database import get_device_database; db = get_device_database(); print(f'Database version: {db.db.get(\"version\")}')"
```

## Best Practices

1. **Port-Nummern**: Immer Strings verwenden (`"102"`, nicht `102`)
2. **Hersteller-Keys**: Kleinbuchstaben mit Unterstrichen (`siemens`, `allen_bradley`)
3. **Banner-Patterns**: Mehrere Varianten für robuste Erkennung
4. **Dokumentation**: Beschreibungen und Referenzen hinzufügen
5. **Versionierung**: `version` in `device_database.json` erhöhen bei Änderungen

## Referenzen

### Siemens
- LOGO! Modbus Server Dokumentation
- S7-1200/1500 System Manual
- CP343-1/CP443-1 Modbus TCP Manuals

### Schneider Electric
- Modbus Protocol Specification (original inventor)
- Modicon M340/M580 Programming Guide

### Standards
- Modbus-IDA Vendor ID Registry
- IANA Port Number Registry
- Industrial Protocol Specifications

## Erweiterungsmöglichkeiten

Zukünftige Features:
- [ ] OPC UA Port-Mapping
- [ ] BACnet/IP Integration
- [ ] PROFINET Device Detection
- [ ] EtherCAT Device Profiles
- [ ] Automatic Profile Updates via GitHub
- [ ] Community Device Database
- [ ] Device Firmware Vulnerability Database
- [ ] Performance Benchmarks per Device Type

## Lizenz

Die Geräteinformationen basieren auf öffentlich zugänglichen Herstellerdokumentationen und Industriestandards. Marken und Produktnamen sind Eigentum ihrer jeweiligen Inhaber.

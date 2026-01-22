# LOGO! v7 S7-Protokoll Integration

## ⚠️ Wichtiger Hinweis

**LOGO! v7 / 0BA7 unterstützt KEIN Modbus TCP!**

LOGO! v7 verwendet ausschließlich das **S7-Protokoll** über Port 102. Diese Anleitung zeigt, wie Sie LOGO! v7 Geräte mit Home Assistant über S7 integrieren können.

## Voraussetzungen

### Software
- **python-snap7** Library (bereits im Add-on enthalten)
- **LOGO! Soft Comfort** V7.x oder V8.x (für Konfiguration)
- **Home Assistant** mit diesem Add-on

### Hardware
- Siemens LOGO! v7 / 0BA7 Gerät
- Ethernet-Verbindung zum LOGO!
- Konfigurierter Netzwerk-Zugang

## Schritt 1: LOGO! Soft Comfort Konfiguration

### 1.1 S7-Verbindung einrichten

1. Öffnen Sie **LOGO! Soft Comfort**
2. Öffnen Sie Ihr LOGO! Projekt
3. Gehen Sie zu **Extras → Übertragen → Geräteigenschaften [S7_1]**
4. Konfigurieren Sie folgende Parameter:

```
Gerätename: Logo7_1 (oder Ihr bevorzugter Name)
IP-Adresse: 192.168.0.2 (Ihre LOGO! IP)
Subnetzmaske: 255.255.255.0
Standard-Gateway: 192.168.0.1
TSAP: 20.00 (Standard für LOGO!)
```

### 1.2 Datenbereiche (VM-Adressen)

LOGO! v7 unterstützt folgende Datenbereiche über S7:

| Bereich | Typ | Adressbereich | Beschreibung |
|---------|-----|---------------|--------------|
| **VB** | Byte | V0-V850 | Variable Memory Bytes |
| **VW** | Word | VW0-VW848 | Variable Memory Words (16-bit) |
| **M** | Bit | V0.0-V850.7 | Merker (einzelne Bits) |
| **MB** | Byte | V0-V850 | Merker als Bytes |
| **IB** | Byte | - | Input Bytes (physikalische Eingänge) |
| **QB** | Byte | - | Output Bytes (physikalische Ausgänge) |

### 1.3 Export-Konfiguration für Home Assistant

Erstellen Sie eine Datei `logo_v7_variables.yaml` mit Ihren VM-Adressen:

```yaml
logo_v7:
  name: "LOGO! v7 Gerät"
  host: "192.168.0.2"
  port: 102
  tsap_client: "0x0100"  # 01.00
  tsap_server: "0x2000"  # 20.00

  variables:
    # Beispiel: Digitale Eingänge
    - name: "input_1"
      address: "V0.0"
      type: "binary_sensor"

    - name: "input_2"
      address: "V0.1"
      type: "binary_sensor"

    # Beispiel: Digitale Ausgänge
    - name: "output_1"
      address: "V10.0"
      type: "switch"

    - name: "output_2"
      address: "V10.1"
      type: "switch"

    # Beispiel: Analoge Werte (Words)
    - name: "temperature"
      address: "VW12"
      type: "sensor"
      unit: "°C"
      scale: 0.1

    - name: "setpoint"
      address: "VW14"
      type: "number"
      min: 0
      max: 1000
```

## Schritt 2: Python S7 Client verwenden

### 2.1 Basis-Verwendung

```python
from app.s7_client import S7Client

# Verbindung herstellen
client = S7Client(
    host="192.168.0.2",
    port=102,
    local_tsap=0x0100,   # Client TSAP (01.00)
    remote_tsap=0x2000   # LOGO! Server TSAP (20.00)
)

client.connect()

# Einzelne VM-Adresse lesen
value = client.read_vm("VW12")  # Liest Word aus VW12
print(f"Temperature: {value}")

# Einzelnes Bit lesen
bit_value = client.read_vm("V0.0")  # Liest Bit 0 von V0
print(f"Input 1: {bit_value}")

# Wert schreiben
client.write_vm("V10.0", 1)  # Setzt Output 1 auf HIGH
client.write_vm("VW14", 250)  # Schreibt 250 in VW14

# Mehrere Adressen lesen
addresses = ["V0.0", "V0.1", "VW12", "VW14"]
values = client.read_multiple(addresses)
print(values)

client.disconnect()
```

### 2.2 Context Manager

```python
from app.s7_client import S7Client

with S7Client("192.168.0.2") as client:
    temp = client.read_vm("VW12")
    client.write_vm("V10.0", 1)
    # Verbindung wird automatisch geschlossen
```

## Schritt 3: Home Assistant Integration

### 3.1 Installation von python-snap7

Das Add-on enthält bereits python-snap7. Falls Sie es separat installieren möchten:

```bash
pip install python-snap7
```

**Hinweis**: Auf manchen Systemen benötigen Sie zusätzlich die snap7-Library:

```bash
# Debian/Ubuntu
sudo apt-get install libsnap7-1 libsnap7-dev

# Fedora/RHEL
sudo dnf install snap7
```

### 3.2 Home Assistant Konfiguration

Fügen Sie in Ihrer `configuration.yaml` hinzu:

```yaml
# LOGO! v7 S7 Integration (benutzerdefiniert)
sensor:
  - platform: template
    sensors:
      logo_temperature:
        friendly_name: "LOGO! Temperatur"
        unit_of_measurement: "°C"
        value_template: "{{ states('sensor.logo_vw12') | float * 0.1 }}"

binary_sensor:
  - platform: template
    sensors:
      logo_input_1:
        friendly_name: "LOGO! Eingang 1"
        value_template: "{{ is_state('sensor.logo_v0_0', '1') }}"

switch:
  - platform: template
    switches:
      logo_output_1:
        friendly_name: "LOGO! Ausgang 1"
        value_template: "{{ is_state('sensor.logo_v10_0', '1') }}"
        turn_on:
          service: script.logo_write_output_1_on
        turn_off:
          service: script.logo_write_output_1_off
```

## Schritt 4: VM-Adress-Mapping (LOGO! Soft Comfort)

### 4.1 Typische VM-Zuordnungen

In LOGO! Soft Comfort können Sie VM-Adressen für verschiedene Zwecke zuweisen:

| Funktion | LOGO! Element | VM-Adresse | S7 Adresse |
|----------|---------------|------------|------------|
| Digitaler Eingang I1 | Input | - | V0.0 |
| Digitaler Eingang I2 | Input | - | V0.1 |
| Digitaler Ausgang Q1 | Output | - | V10.0 |
| Digitaler Ausgang Q2 | Output | - | V10.1 |
| Merker M1 | Memory | M1 | V20.0 |
| Analoger Eingang AI1 | Analog In | AI1 | VW100 |
| Analogwert | Variable | VW12 | VW12 |

### 4.2 Adress-Berechnung

**Byte zu Bit:**
- V10 = V10.0 bis V10.7 (8 Bits)
- V11 = V11.0 bis V11.7 (8 Bits)

**Word Adressen:**
- VW12 = V12 (High-Byte) + V13 (Low-Byte)
- VW14 = V14 (High-Byte) + V15 (Low-Byte)

## Schritt 5: LOGO! Soft Comfort Export

### 5.1 Projekt-Export für Dokumentation

1. Öffnen Sie Ihr LOGO! Projekt
2. Gehen Sie zu **Datei → Drucken → Parameterliste**
3. Exportieren Sie die Liste als PDF/Excel
4. Dokumentieren Sie alle verwendeten VM-Adressen

### 5.2 Beispiel-Parameterliste

```
Parameterliste - Logo7_1
============================

Eingänge:
- I1: Taster Start (V0.0)
- I2: Taster Stop (V0.1)
- I3: Temperatursensor (AI1 → VW100)

Ausgänge:
- Q1: Motor (V10.0)
- Q2: Heizung (V10.1)

Merker:
- M1: Betrieb aktiv (V20.0)
- M2: Alarm aktiv (V20.1)

Variable Words:
- VW12: Temperatur (×0.1°C)
- VW14: Sollwert (×0.1°C)
- VW16: Timer-Wert (Sekunden)
```

## Schritt 6: Fehlerbehebung

### 6.1 Häufige Probleme

**Problem: Connection refused (Port 102)**
```
Lösung: Stellen Sie sicher, dass:
- LOGO! per Ethernet erreichbar ist (ping 192.168.0.2)
- Port 102 nicht durch Firewall blockiert ist
- S7-Verbindung in LOGO! aktiviert ist
```

**Problem: TSAP Error**
```
Lösung: Überprüfen Sie die TSAP-Werte:
- Client TSAP: 0x0100 (01.00)
- Server TSAP: 0x2000 (20.00)
- Diese Werte sind Standard für LOGO!
```

**Problem: VM Address not found**
```
Lösung: Überprüfen Sie:
- VM-Adresse existiert in LOGO! Programm
- Richtige Syntax: "V10.0", "VW12" (nicht "V10:0" oder "VW-12")
- Adressbereich stimmt (V0-V850)
```

### 6.2 Test-Verbindung

Testen Sie die S7-Verbindung mit diesem Script:

```python
from app.s7_client import S7Client
import sys

def test_connection(host):
    print(f"Testing S7 connection to {host}...")

    try:
        client = S7Client(host)
        if client.connect():
            print("✓ Connection successful!")

            # Test read
            test_addr = "V0"
            value = client.read_vm(test_addr)
            if value is not None:
                print(f"✓ Read test successful: {test_addr} = {value}")
            else:
                print(f"✗ Read test failed")

            client.disconnect()
            return True
        else:
            print("✗ Connection failed")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "192.168.0.2"
    test_connection(host)
```

## Schritt 7: Best Practices

### 7.1 Adress-Planung

- **V0-V9**: Reserviert für Eingänge (I1-I24)
- **V10-V19**: Reserviert für Ausgänge (Q1-Q20)
- **V20-V49**: Merker (M1-M64)
- **VW100-VW200**: Analoge Werte
- **VW300-VW400**: Benutzer-Parameter

### 7.2 Polling-Intervall

```python
# Empfohlene Scan-Intervalle
DIGITAL_IO_SCAN = 1      # Sekunde (schnell)
ANALOG_SCAN = 5          # Sekunden (mittel)
STATUS_SCAN = 10         # Sekunden (langsam)
```

### 7.3 Fehlerbehandlung

```python
def safe_read(client, address, default=0):
    """Sichere Lesefunktion mit Fallback"""
    try:
        value = client.read_vm(address)
        return value if value is not None else default
    except Exception as e:
        logger.error(f"Error reading {address}: {e}")
        return default
```

## Zusammenfassung

**LOGO! v7 mit Home Assistant:**
1. ✅ S7-Protokoll über python-snap7
2. ✅ VM-Adressen aus LOGO! Soft Comfort
3. ✅ Port 102 (nicht 502/510 wie Modbus!)
4. ✅ TSAP: 01.00 (Client) + 20.00 (Server)

**Wichtig:**
- LOGO! v7 ≠ Modbus (nur S7!)
- LOGO! v8 = Modbus TCP + S7

## Quellen und Referenzen

- [python-snap7 auf PyPI](https://pypi.org/project/python-snap7/)
- [python-snap7 GitHub Repository](https://github.com/gijzelaerr/python-snap7)
- [LOGO! Documentation](https://python-snap7.readthedocs.io/en/1.0/logo.html)
- [Snap7 LOGO Integration Guide](https://www.solisplc.com/tutorials/introduction-to-snap7-integration-into-siemens-tia-portal)

---

**Stand**: 2026-01-22
**Version**: 1.5.0b
**Kompatibilität**: LOGO! v7 / 0BA7

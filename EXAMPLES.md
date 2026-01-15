# Konfigurationsbeispiele

## Siemens LOGO! 8 - Vollständige Konfiguration

### Szenario: Hausautomatisierung mit 4 LOGO!-Steuerungen

#### LOGO! 1 - Haupthaus Obergeschoss (192.168.178.201)

**Gerät konfigurieren:**
- **Name**: `logo_1_haupthaus`
- **Hersteller**: Siemens
- **Modell**: LOGO! 8
- **IP-Adresse**: 192.168.178.201
- **Port**: 510

**Automatisch generierte Entitäten:**

**Analoge Eingänge (Temperatursensoren):**
```yaml
- name: "Logo1 AI 1 Temp Wohnzimmer"
  address: 1
  input_type: input
  data_type: uint16
  unit_of_measurement: "°C"
  scale: 0.081
  offset: -20.0
  device_class: temperature
  precision: 1
  scan_interval: 5
  state_class: measurement
```

**Digitale Eingänge (Schalter/Taster):**
```yaml
- name: "Logo1 I3 Kind 1 Licht Schalter"
  address: 3
  input_type: discrete_input
  scan_interval: 1
```

**Digitale Ausgänge (Relais/Aktoren):**
```yaml
- name: "Logo1 Q1 Kind 1 Licht"
  address: 8193  # 0x2001
  write_type: coil
  scan_interval: 1
```

---

## Schneider Electric Modicon M221

### Szenario: Industrielle Steuerung

**Gerät konfigurieren:**
- **Name**: `modicon_produktion`
- **Hersteller**: Schneider Electric
- **Modell**: Modicon M221
- **IP-Adresse**: 192.168.1.50
- **Port**: 502

**Beispiel-Entitäten:**

```yaml
sensors:
  - name: "Produktion Druck Sensor 1"
    address: 0
    input_type: input
    data_type: int16
    unit_of_measurement: "bar"
    scale: 0.01
    device_class: pressure
    precision: 2
    scan_interval: 2

binary_sensors:
  - name: "Produktion Notaus Status"
    address: 0
    input_type: discrete_input
    scan_interval: 1
```

---

## ABB AC500

### Szenario: Gebäudeautomation

**Gerät konfigurieren:**
- **Name**: `abb_gebaeude1`
- **Hersteller**: ABB
- **Modell**: AC500
- **IP-Adresse**: 192.168.10.100
- **Port**: 502

---

## Wago 750 Series

### Szenario: Heizungssteuerung

**Gerät konfigurieren:**
- **Name**: `wago_heizung`
- **Hersteller**: Wago
- **Modell**: 750 Series
- **IP-Adresse**: 192.168.2.10
- **Port**: 502

**Beispiel-Konfiguration:**

```yaml
sensors:
  - name: "Heizung Vorlauftemperatur"
    address: 0
    input_type: input
    data_type: int16
    unit_of_measurement: "°C"
    scale: 0.1
    device_class: temperature
    precision: 1
    scan_interval: 10

switches:
  - name: "Heizung Pumpe 1"
    address: 512
    write_type: coil
    scan_interval: 1
```

---

## Generic Modbus TCP

### Szenario: Energie-Monitoring

**Gerät konfigurieren:**
- **Name**: `powermeter_haupteingang`
- **Hersteller**: Generic
- **Modell**: Modbus TCP
- **IP-Adresse**: 192.168.1.200
- **Port**: 502
- **Slave ID**: 1

**Beispiel für Energie-Zähler:**

```yaml
sensors:
  # Spannung L1
  - name: "Powermeter Spannung L1"
    address: 0
    input_type: input
    data_type: uint16
    unit_of_measurement: "V"
    scale: 0.1
    device_class: voltage
    precision: 1
    scan_interval: 5
    state_class: measurement

  # Strom L1
  - name: "Powermeter Strom L1"
    address: 6
    input_type: input
    data_type: uint16
    unit_of_measurement: "A"
    scale: 0.01
    device_class: current
    precision: 2
    scan_interval: 5
    state_class: measurement

  # Leistung Gesamt
  - name: "Powermeter Leistung Total"
    address: 12
    input_type: input
    data_type: uint32
    unit_of_measurement: "W"
    device_class: power
    precision: 0
    scan_interval: 2
    state_class: measurement

  # Energie Gesamt
  - name: "Powermeter Energie Total"
    address: 342
    input_type: input
    data_type: uint32
    unit_of_measurement: "kWh"
    scale: 0.01
    device_class: energy
    precision: 2
    scan_interval: 30
    state_class: total_increasing
```

---

## Multi-Gerät Szenario

### Szenario: Komplette Hausautomatisierung

**4 LOGO! Steuerungen:**

1. **LOGO! 1** (192.168.178.201) - Obergeschoss Beleuchtung + Temperatur
2. **LOGO! 2** (192.168.178.202) - Untergeschoss Bad
3. **LOGO! 3** (192.168.178.203) - Garage + Pool
4. **LOGO! 4** (192.168.178.204) - Keller + Energiemonitoring

**Workflow:**

1. **Alle Geräte im Web-UI hinzufügen**
   - Jeweils Hersteller "Siemens", Modell "LOGO! 8" wählen
   - IP-Adressen und Namen konfigurieren
   - Verbindung testen

2. **Optional: Geräte scannen**
   - Verfügbare Register automatisch erkennen
   - Anzahl der Inputs/Outputs sehen

3. **Konfiguration generieren**
   - Alle 4 Geräte werden in einer YAML-Datei zusammengefasst
   - Automatisch korrekte Register-Adressen

4. **In Home Assistant einbinden**
   ```yaml
   # configuration.yaml
   modbus: !include modbus_generated.yaml
   ```

5. **Home Assistant neu starten**

6. **Entitäten verfügbar:**
   - `sensor.logo1_ai_1_temp_wz`
   - `binary_sensor.logo1_i3_kind_1_licht_schalter`
   - `switch.logo1_q1_kind_1_licht`
   - ... und viele mehr!

---

## Erweiterte Konfiguration

### Temperatursensoren mit Kalibrierung

Wenn Ihre Temperatursensoren kalibriert werden müssen:

```yaml
sensors:
  - name: "Kalibrierter Temperatursensor"
    address: 1
    input_type: input
    data_type: uint16
    unit_of_measurement: "°C"
    scale: 0.081        # Skalierungsfaktor
    offset: -20.194     # Offset zur Kalibrierung
    device_class: temperature
    precision: 1
    scan_interval: 5
    state_class: measurement
```

**Kalibrierung berechnen:**
```
Gemessener Wert = (Rohwert * scale) + offset

Beispiel:
Rohwert = 250
scale = 0.081
offset = -20.194

Temperatur = (250 * 0.081) + (-20.194) = 20.25 - 20.194 = 0.056°C
```

### Leistungsmessung mit mehreren Phasen

```yaml
sensors:
  # Phase 1
  - name: "Haus Leistung L1"
    address: 1
    input_type: input
    data_type: uint16
    unit_of_measurement: "kW"
    scale: 1
    device_class: power
    precision: 1
    scan_interval: 5
    state_class: measurement

  # Phase 2
  - name: "Haus Leistung L2"
    address: 2
    input_type: input
    data_type: uint16
    unit_of_measurement: "kW"
    scale: 1
    device_class: power
    precision: 1
    scan_interval: 5
    state_class: measurement

  # Phase 3
  - name: "Haus Leistung L3"
    address: 3
    input_type: input
    data_type: uint16
    unit_of_measurement: "kW"
    scale: 1
    device_class: power
    precision: 1
    scan_interval: 5
    state_class: measurement
```

### Template für Gesamtleistung in configuration.yaml

```yaml
template:
  - sensor:
      - name: "Haus Gesamtleistung"
        unit_of_measurement: "kW"
        state: >
          {{ states('sensor.haus_leistung_l1')|float(0) +
             states('sensor.haus_leistung_l2')|float(0) +
             states('sensor.haus_leistung_l3')|float(0) }}
        device_class: power
        state_class: measurement
```

---

## Tipps & Tricks

### 1. Scan vor der Konfiguration

Nutzen Sie immer die Scan-Funktion, um zu sehen, welche Register wirklich verfügbar sind.

### 2. Verbindungstest

Testen Sie die Verbindung, bevor Sie das Gerät hinzufügen.

### 3. Sinnvolle Namen

Verwenden Sie beschreibende Namen wie:
- ✅ `logo1_schlafzimmer_temperatur`
- ❌ `sensor_1`

### 4. Scan-Intervalle anpassen

- Temperatur: 5-10 Sekunden
- Schalter: 1 Sekunde
- Energie-Zähler: 10-30 Sekunden

### 5. Slave ID beachten

Manche Geräte benötigen eine spezifische Slave ID (meist 1 oder 255).

### 6. Register-Adressen dokumentieren

Notieren Sie sich die Zuordnung der Adressen zu physischen Ein-/Ausgängen.

---

## Fehlersuche

### Gerät nicht erreichbar

```yaml
# Erhöhen Sie den Timeout
timeout: 10
```

### Falsche Werte

```yaml
# Passen Sie scale und offset an
scale: 0.081
offset: -20.0
```

### Zu viele Anfragen

```yaml
# Erhöhen Sie scan_interval
scan_interval: 10
```

---

## Integration mit Home Assistant

### Automation Beispiel

```yaml
automation:
  - alias: "Licht einschalten bei Bewegung"
    trigger:
      - platform: state
        entity_id: binary_sensor.logo1_i3_bewegungsmelder
        to: "on"
    action:
      - service: switch.turn_on
        entity_id: switch.logo1_q1_flur_licht
```

### Lovelace Dashboard Beispiel

```yaml
type: entities
title: Siemens LOGO! Status
entities:
  - entity: sensor.logo1_ai_1_temp_wz
  - entity: switch.logo1_q1_licht_wz
  - entity: binary_sensor.logo1_i3_taster_wz
```

---

**Weitere Fragen?** Siehe [README_ADDON.md](README_ADDON.md) für vollständige Dokumentation.

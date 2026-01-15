# 🔧 Universal Modbus Configurator für Home Assistant

Ein umfassendes Home Assistant Addon zur einfachen Konfiguration von Modbus TCP-Geräten verschiedener Hersteller.

## 📋 Übersicht

Der Universal Modbus Configurator vereinfacht die Erstellung von Modbus-Konfigurationen für Home Assistant erheblich. Anstatt YAML-Dateien manuell zu erstellen, bietet dieses Addon eine benutzerfreundliche Web-Oberfläche zur Konfiguration von Modbus-Geräten.

### Hauptfunktionen

✨ **Unterstützte Hersteller:**
- **Siemens** - LOGO! 7, LOGO! 8
- **Schneider Electric** - Modicon M221
- **ABB** - AC500
- **Wago** - 750 Series
- **Generic** - Standard Modbus TCP

🎯 **Features:**
- Benutzerfreundliches Web-Interface
- Automatische Geräteerkennung
- Verbindungstest
- Mehrere Geräte gleichzeitig verwalten
- Automatische YAML-Generierung
- Register-Scanner für verfügbare Modbus-Adressen

## 🚀 Installation

### Methode 1: Über Home Assistant Add-on Store (empfohlen)

1. Navigieren Sie zu **Einstellungen** → **Add-ons** → **Add-on Store**
2. Klicken Sie auf die drei Punkte (⋮) oben rechts
3. Wählen Sie **Repositories**
4. Fügen Sie diese Repository-URL hinzu:
   ```
   https://github.com/IHR_USERNAME/only_claude
   ```
5. Suchen Sie nach "Universal Modbus Configurator"
6. Klicken Sie auf **Installieren**

### Methode 2: Manuelle Installation

1. Kopieren Sie den gesamten Addon-Ordner nach `/addons/universal_modbus_config/`
2. Starten Sie Home Assistant neu
3. Das Addon erscheint im Add-on Store unter "Local add-ons"

## ⚙️ Konfiguration

### Addon-Optionen

```yaml
devices: []
modbus_config_path: "/config/modbus_generated.yaml"
```

- **devices**: Liste der konfigurierten Geräte (wird über Web-UI verwaltet)
- **modbus_config_path**: Pfad zur generierten Modbus-Konfiguration

## 📖 Verwendung

### 1. Addon starten

1. Navigieren Sie zu **Einstellungen** → **Add-ons** → **Universal Modbus Configurator**
2. Klicken Sie auf **Start**
3. Aktivieren Sie **Show in Sidebar** für schnellen Zugriff
4. Klicken Sie auf **Web UI öffnen**

### 2. Gerät hinzufügen

1. **Hersteller wählen**: Wählen Sie den Hersteller Ihres Geräts aus
2. **Modell wählen**: Wählen Sie das spezifische Modell
3. **Gerätename**: Vergeben Sie einen eindeutigen Namen (z.B. "Logo1_Haupthaus")
4. **IP-Adresse**: Geben Sie die IP-Adresse des Geräts ein
5. **Port**: Standard ist 502 (LOGO! nutzt 510)
6. **Slave ID**: Optional, falls erforderlich

### 3. Verbindung testen

Klicken Sie auf **Verbindung testen**, um zu überprüfen, ob das Gerät erreichbar ist.

### 4. Gerät scannen (optional)

Klicken Sie auf **Gerät scannen**, um automatisch alle verfügbaren Register zu erkennen. Dies zeigt:
- Anzahl der Input Register
- Anzahl der Holding Register
- Anzahl der Discrete Inputs
- Anzahl der Coils

### 5. Gerät hinzufügen

Klicken Sie auf **Gerät hinzufügen**, um das Gerät zur Konfiguration hinzuzufügen.

### 6. Konfiguration generieren

Wenn alle Geräte hinzugefügt wurden:
1. Klicken Sie auf **Konfiguration generieren**
2. Die `modbus_generated.yaml` wird erstellt
3. Integrieren Sie diese in Ihre Home Assistant Konfiguration

## 🔗 Integration in Home Assistant

### Variante 1: Direct Include

Fügen Sie in Ihrer `configuration.yaml` hinzu:

```yaml
modbus: !include modbus_generated.yaml
```

### Variante 2: Packages

Erstellen Sie ein Package in `/config/packages/modbus.yaml`:

```yaml
modbus: !include ../modbus_generated.yaml
```

Aktivieren Sie Packages in `configuration.yaml`:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

### Nach der Integration

1. Überprüfen Sie die Konfiguration: **Entwicklerwerkzeuge** → **YAML** → **Check configuration**
2. Starten Sie Home Assistant neu
3. Ihre Modbus-Entitäten sind nun verfügbar!

## 🎨 Beispiel: Siemens LOGO! 8 Konfiguration

### Durch das Addon generiert:

Das Addon erstellt automatisch Entitäten basierend auf den LOGO!-Profilen:

- **Analoge Eingänge (AI)**: Werden als `sensor` erstellt
  - AI1-AI8 (Adresse 1-8)
  - Konfigurierbar für Temperatur, Feuchtigkeit, etc.

- **Digitale Eingänge (I)**: Werden als `binary_sensor` erstellt
  - I1-I24 (Adresse 1-24)

- **Digitale Ausgänge (Q)**: Werden als `switch` erstellt
  - Q1-Q20 (Adresse 8193-8212, 0x2001-0x2014)

### Beispiel-Entität:

```yaml
- name: logo_1_haupthaus
  type: tcp
  host: 192.168.178.201
  port: 510
  timeout: 5

  sensors:
    - name: "Logo1 AI 1 Temp WZ"
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

## 🛠️ Erweiterte Konfiguration

### Eigene Geräteprofile hinzufügen

Geräteprofile befinden sich in `app/device_profiles.py`. Sie können neue Hersteller oder Modelle hinzufügen:

```python
"Ihr_Hersteller": {
    "Ihr_Modell": {
        "port": 502,
        "timeout": 5,
        "registers": {
            "analog_inputs": {
                "type": "sensor",
                "start_address": 0,
                "count": 10,
                "input_type": "input",
                "data_type": "uint16",
                "scan_interval": 5
            }
        }
    }
}
```

### Register-Adressen

**Siemens LOGO! 8 Register-Mapping:**
- Analoge Eingänge: 1-8
- Digitale Eingänge: 1-24
- Digitale Ausgänge: 8193-8212 (0x2001-0x2014)
- Analoge Ausgänge: 528-535 (0x0210-0x0217)

**Standard Modbus:**
- Coils: 0-65535
- Discrete Inputs: 0-65535
- Input Registers: 0-65535
- Holding Registers: 0-65535

## 🔍 Troubleshooting

### Verbindung fehlgeschlagen

**Problem**: "Connection failed" beim Testen

**Lösungen**:
1. Überprüfen Sie die IP-Adresse
2. Prüfen Sie, ob das Gerät erreichbar ist (ping)
3. Stellen Sie sicher, dass Modbus TCP aktiviert ist
4. Überprüfen Sie Firewall-Einstellungen
5. Vergewissern Sie sich, dass der Port korrekt ist (LOGO! = 510, Standard = 502)

### Keine Register gefunden beim Scannen

**Problem**: Scan findet 0 Register

**Lösungen**:
1. Überprüfen Sie die Slave ID (oft 1 oder 255)
2. Wählen Sie das korrekte Geräteprofil
3. Manche Geräte benötigen spezielle Start-Adressen
4. Überprüfen Sie die Gerätedokumentation

### Entitäten erscheinen nicht in Home Assistant

**Problem**: Nach Neustart keine Entitäten sichtbar

**Lösungen**:
1. Überprüfen Sie die Configuration: **Entwicklerwerkzeuge** → **YAML**
2. Prüfen Sie das Home Assistant Log auf Fehler
3. Stellen Sie sicher, dass `modbus:` in `configuration.yaml` korrekt eingebunden ist
4. Vergewissern Sie sich, dass die IP-Adressen erreichbar sind

### YAML-Syntax-Fehler

**Problem**: "Invalid config" nach Neustart

**Lösungen**:
1. Überprüfen Sie die Einrückung in der generierten YAML
2. Stellen Sie sicher, dass keine Tab-Zeichen verwendet werden
3. Validieren Sie die YAML-Syntax online
4. Überprüfen Sie das Configuration Check Tool

## 📊 API-Dokumenten

Das Addon bietet eine RESTful API:

### GET /api/manufacturers
Gibt Liste aller unterstützten Hersteller zurück.

### GET /api/models/{manufacturer}
Gibt Modelle für einen Hersteller zurück.

### GET /api/devices
Gibt alle konfigurierten Geräte zurück.

### POST /api/devices
Fügt ein neues Gerät hinzu.

### POST /api/scan
Scannt ein Gerät nach verfügbaren Registern.

### POST /api/generate
Generiert die Modbus-YAML-Konfiguration.

## 🤝 Beitragen

Contributions sind willkommen! Öffnen Sie gerne Issues oder Pull Requests.

### Neue Geräteprofile hinzufügen

1. Forken Sie das Repository
2. Fügen Sie Ihr Profil zu `app/device_profiles.py` hinzu
3. Testen Sie das Profil
4. Erstellen Sie einen Pull Request

## 📄 Lizenz

MIT License - Siehe LICENSE Datei für Details

## 🙏 Danksagungen

- Home Assistant Community
- PyModbus Contributors
- Alle Beta-Tester

## 📞 Support

- GitHub Issues: [Repository Issues](https://github.com/IHR_USERNAME/only_claude/issues)
- Home Assistant Forum: [Link zum Thread]
- Discord: [Link zum Server]

## 🗺️ Roadmap

**Geplante Features:**
- [ ] Automatische Entitäten-Benennung basierend auf Funktion
- [ ] Import bestehender Modbus-Konfigurationen
- [ ] Backup/Restore Funktionalität
- [ ] Templates für häufige Szenarien
- [ ] Erweiterte Register-Konfiguration im UI
- [ ] Multi-Language Support (EN, DE, FR)
- [ ] Export als CSV
- [ ] Bulk-Import von Geräten

---

**Version**: 1.0.0
**Erstellt mit**: ❤️ für die Home Assistant Community
**Letzte Aktualisierung**: 2026-01-14

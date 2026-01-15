# 🔧 Universal Modbus Configurator

**Home Assistant Add-on Repository für einfache Modbus-Konfiguration**

Ein umfassendes Home Assistant Add-on zur mühelosen Konfiguration von Modbus TCP-Geräten verschiedener Hersteller, speziell optimiert für Siemens LOGO! und andere SPS-Systeme.

---

## 📦 Add-on Installation

### Schritt 1: Repository zu Home Assistant hinzufügen

1. Öffnen Sie **Home Assistant**
2. Navigieren Sie zu **Einstellungen** → **Add-ons** → **Add-on Store**
3. Klicken Sie auf die **drei Punkte (⋮)** oben rechts
4. Wählen Sie **Repositories**
5. Fügen Sie diese URL hinzu:

```
https://github.com/b3n-secu/only_claude
```

6. Klicken Sie auf **Hinzufügen**
7. Schließen Sie den Dialog

### Schritt 2: Add-on installieren

1. Suchen Sie im Add-on Store nach **"Universal Modbus Configurator"**
2. Klicken Sie auf das Add-on
3. Klicken Sie auf **Installieren**
4. Warten Sie, bis die Installation abgeschlossen ist
5. Klicken Sie auf **Starten**
6. Optional: Aktivieren Sie **Show in Sidebar** für schnellen Zugriff

### Schritt 3: Web-UI öffnen

1. Klicken Sie auf **Web UI öffnen**
2. Oder öffnen Sie manuell: `http://homeassistant.local:8099`

---

## 🎯 Features

### ✨ Unterstützte Hersteller

- **Siemens** - LOGO! 7, LOGO! 8 (Port 510)
- **Schneider Electric** - Modicon M221
- **ABB** - AC500
- **Wago** - 750 Series
- **Generic** - Standard Modbus TCP (Port 502)

### 🔧 Hauptfunktionen

- 🌐 **Web-basiertes UI** - Intuitive Konfiguration über Browser (Port 8099)
- 🔍 **Automatischer Scanner** - Erkennt verfügbare Modbus-Register
- ✅ **Verbindungstest** - Prüft Geräte vor der Konfiguration
- 📝 **YAML-Generator** - Erstellt automatisch Home Assistant Konfiguration
- 📊 **Multi-Gerät Support** - Unbegrenzte Anzahl von Geräten
- 🔌 **RESTful API** - Programmierbare Schnittstelle
- 🌍 **Mehrsprachig** - Deutsch & Englisch
- 📱 **Responsive Design** - Funktioniert auf allen Geräten

### 📋 Unterstützte Register-Typen

- **Analog Inputs** (Input Registers) → Sensoren (Temperatur, Druck, etc.)
- **Analog Outputs** (Holding Registers) → Stellgrößen
- **Digital Inputs** (Discrete Inputs) → Binary Sensoren (Schalter, Taster)
- **Digital Outputs** (Coils) → Switches (Relais, Lichter)

---

## 🚀 Schnellstart (5 Minuten)

### 1. Repository hinzufügen & installieren
```
Einstellungen → Add-ons → Add-on Store → ⋮ → Repositories
→ https://github.com/b3n-secu/only_claude
→ Universal Modbus Configurator → Installieren → Starten
```

### 2. Web-UI öffnen
```
http://homeassistant.local:8099
```

### 3. Gerät konfigurieren (Beispiel: Siemens LOGO! 8)

```yaml
Hersteller: Siemens
Modell: LOGO! 8
Name: logo_haupthaus
IP-Adresse: 192.168.178.201
Port: 510
```

→ **Verbindung testen** ✓
→ **Gerät scannen** (optional)
→ **Gerät hinzufügen**

### 4. Konfiguration generieren

Klicken Sie auf **"Konfiguration generieren"**

→ Datei wird erstellt: `/config/modbus_generated.yaml`

### 5. In Home Assistant einbinden

Öffnen Sie `/config/configuration.yaml` und fügen Sie hinzu:

```yaml
modbus: !include modbus_generated.yaml
```

### 6. Neustart & Fertig! 🎉

```
Einstellungen → System → Neu starten
```

Nach dem Neustart sind Ihre Modbus-Entitäten verfügbar!

---

## 📖 Dokumentation

### Vollständige Anleitungen

- 📚 **[README_ADDON.md](README_ADDON.md)** - Vollständige Dokumentation (8.5 KB)
- 🚀 **[QUICKSTART.md](QUICKSTART.md)** - 5-Minuten Setup-Guide
- 💡 **[EXAMPLES.md](EXAMPLES.md)** - Konfigurationsbeispiele für alle Hersteller
- ❓ **[FAQ.md](FAQ.md)** - 40+ häufige Fragen & Antworten
- 📝 **[INSTALL.md](INSTALL.md)** - Detaillierte Installationsanleitung
- 🤝 **[CONTRIBUTING.md](CONTRIBUTING.md)** - Beitragen & neue Geräteprofile

### Hilfreiche Ressourcen

- 📋 **[CHANGELOG.md](CHANGELOG.md)** - Versionshistorie
- 📄 **[LICENSE](LICENSE)** - MIT License
- 📊 **[modbus.yaml](modbus.yaml)** - Beispiel-Konfiguration (4 LOGO! Geräte)

---

## 🎯 Verwendungsbeispiel

### Siemens LOGO! 8 - Automatisch generierte Konfiguration

```yaml
- name: logo_1_haupthaus
  type: tcp
  host: 192.168.178.201
  port: 510
  timeout: 5

  # Temperatursensoren (Analog Inputs)
  sensors:
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

  # Schalter/Taster (Digital Inputs)
  binary_sensors:
    - name: "Logo1 I3 Bewegungsmelder"
      address: 3
      input_type: discrete_input
      scan_interval: 1

  # Relais/Lichter (Digital Outputs)
  switches:
    - name: "Logo1 Q1 Wohnzimmer Licht"
      address: 8193  # 0x2001
      write_type: coil
      scan_interval: 1
```

---

## 🔍 Troubleshooting

### ❌ "Not a valid add-on repository"

**Lösung**: Stellen Sie sicher, dass Sie die korrekte URL verwenden:
```
https://github.com/b3n-secu/only_claude
```

### ❌ Verbindungstest fehlgeschlagen

**Checkliste**:
- [ ] IP-Adresse korrekt?
- [ ] Port korrekt? (LOGO! = 510, andere = 502)
- [ ] Gerät eingeschaltet?
- [ ] Im gleichen Netzwerk?
- [ ] Modbus TCP am Gerät aktiviert?
- [ ] Firewall-Blockierung?

### ❌ Keine Entitäten nach Neustart

**Prüfen**:
1. Ist `modbus: !include modbus_generated.yaml` in `configuration.yaml`?
2. Configuration Check grün?
3. Geräte online und erreichbar?
4. Home Assistant Log auf Fehler prüfen

Weitere Hilfe: Siehe [FAQ.md](FAQ.md)

---

## 🤝 Beitragen

Contributions sind willkommen!

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/b3n-secu/only_claude/issues)
- 💡 **Feature Requests**: [GitHub Issues](https://github.com/b3n-secu/only_claude/issues)
- 🔧 **Pull Requests**: Siehe [CONTRIBUTING.md](CONTRIBUTING.md)
- 📝 **Neue Geräteprofile**: Siehe [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📄 Lizenz

MIT License - Siehe [LICENSE](LICENSE) für Details

---

**Version**: 1.0.0
**Repository**: https://github.com/b3n-secu/only_claude

🎉 **Viel Erfolg mit Ihrem Modbus-Setup!**

# Häufig gestellte Fragen (FAQ)

## Installation & Setup

### F: Wie installiere ich das Addon?

**A:** Es gibt mehrere Methoden:

1. **Über Repository (empfohlen):**
   - Gehen Sie zu Einstellungen → Add-ons → Add-on Store
   - Fügen Sie das Repository hinzu
   - Installieren Sie "Universal Modbus Configurator"

2. **Lokal:**
   - Kopieren Sie alle Dateien nach `/addons/universal_modbus_config/`
   - Starten Sie Home Assistant neu

Siehe [INSTALL.md](INSTALL.md) für Details.

### F: Auf welchem Port läuft das Web-UI?

**A:** Das Web-UI läuft standardmäßig auf Port **8099**.

Zugriff über: `http://homeassistant.local:8099`

### F: Muss ich das Addon immer laufen lassen?

**A:** Nein! Das Addon wird nur zum Konfigurieren benötigt. Nach der Generierung der YAML-Datei können Sie es stoppen. Die Modbus-Integration von Home Assistant läuft unabhängig.

---

## Geräte & Verbindung

### F: Welche Hersteller werden unterstützt?

**A:** Aktuell unterstützt:
- **Siemens** - LOGO! 7, LOGO! 8
- **Schneider Electric** - Modicon M221
- **ABB** - AC500
- **Wago** - 750 Series
- **Generic** - Standard Modbus TCP

### F: Mein Gerät ist nicht in der Liste. Was tun?

**A:** Sie haben mehrere Optionen:

1. Wählen Sie "Generic" → "Modbus TCP"
2. Fügen Sie ein eigenes Profil hinzu (siehe [CONTRIBUTING.md](CONTRIBUTING.md))
3. Öffnen Sie ein Feature Request auf GitHub

### F: Wie finde ich die IP-Adresse meines Geräts?

**A:** Methoden:

1. **Gerätedisplay:** Viele Geräte zeigen die IP im Display
2. **Router:** Checken Sie die verbundenen Geräte in Ihrem Router
3. **Network Scanner:** Nutzen Sie Tools wie `nmap` oder "Fing"
4. **Herstellersoftware:** LOGO! Soft Comfort, TIA Portal, etc.

### F: Welchen Port verwendet mein Gerät?

**A:** Standard-Ports:
- **Siemens LOGO!**: Port **510**
- **Meiste andere**: Port **502** (Standard Modbus TCP)

Das Addon setzt automatisch den richtigen Port basierend auf dem Geräteprofil.

### F: Was ist die Slave ID?

**A:** Die Slave ID (Unit ID) identifiziert ein Gerät auf dem Modbus-Bus.

- Meist: **1**
- Bei manchen Geräten: **255**
- Überprüfen Sie die Gerätedokumentation

Lassen Sie das Feld leer, wenn Sie unsicher sind - das Addon verwendet dann den Standard.

### F: Verbindungstest schlägt fehl. Was tun?

**A:** Überprüfen Sie:

1. ✅ **IP-Adresse korrekt?**
2. ✅ **Gerät eingeschaltet?**
3. ✅ **Im gleichen Netzwerk?**
4. ✅ **Port korrekt?** (LOGO! = 510, andere = 502)
5. ✅ **Modbus TCP aktiviert?** (am Gerät)
6. ✅ **Firewall-Blockierung?**
7. ✅ **Ping erfolgreich?** (`ping 192.168.x.x`)

---

## Konfiguration

### F: Wie viele Geräte kann ich hinzufügen?

**A:** Unbegrenzt! Sie können beliebig viele Modbus-Geräte konfigurieren.

### F: Kann ich Geräte verschiedener Hersteller mischen?

**A:** Ja! Sie können LOGO!, Schneider, ABB, Wago und Generic Geräte gleichzeitig konfigurieren.

### F: Was macht die Scan-Funktion?

**A:** Die Scan-Funktion:
- Liest alle verfügbaren Register aus
- Zeigt, wie viele Inputs/Outputs vorhanden sind
- Hilft bei der Fehlersuche

**Hinweis:** Der Scan ist optional. Sie können auch ohne Scan Geräte hinzufügen.

### F: Wie funktioniert die automatische Generierung?

**A:** Das Addon:
1. Verwendet das Geräteprofil (Hersteller + Modell)
2. Erstellt Entitäten basierend auf den Register-Typen
3. Setzt sinnvolle Defaults (scan_interval, data_type, etc.)
4. Generiert eine valide YAML-Datei

### F: Kann ich die generierte Konfiguration anpassen?

**A:** Ja! Nach der Generierung können Sie:
1. Die YAML-Datei öffnen
2. Entitäten umbenennen
3. Parameter anpassen (scale, offset, scan_interval)
4. Ungenutzte Entitäten entfernen

### F: Wo wird die Konfiguration gespeichert?

**A:** Standardmäßig hier: `/config/modbus_generated.yaml`

Sie können den Pfad in den Addon-Optionen ändern.

---

## Integration in Home Assistant

### F: Wie integriere ich die generierte Konfiguration?

**A:** Fügen Sie in Ihrer `configuration.yaml` hinzu:

```yaml
modbus: !include modbus_generated.yaml
```

Dann Home Assistant neu starten.

### F: Meine Entitäten erscheinen nicht. Warum?

**A:** Mögliche Gründe:

1. **Konfiguration nicht eingebunden:** Fehlt `modbus: !include ...` in `configuration.yaml`?
2. **YAML-Fehler:** Prüfen Sie die Konfiguration unter Entwicklerwerkzeuge → YAML
3. **Gerät nicht erreichbar:** Sind die Geräte online und erreichbar?
4. **Home Assistant nicht neu gestartet:** Haben Sie nach der Änderung neu gestartet?

### F: Wie benenne ich Entitäten um?

**A:** In der YAML-Datei:

```yaml
# Vorher
- name: "Logo1 Q1"

# Nachher
- name: "Wohnzimmer Licht"
```

Die Entity ID wird beim nächsten Neustart aktualisiert.

### F: Kann ich die Konfiguration in Packages auslagern?

**A:** Ja! Erstellen Sie `/config/packages/modbus.yaml`:

```yaml
modbus: !include ../modbus_generated.yaml
```

Und in `configuration.yaml`:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

---

## Siemens LOGO! spezifisch

### F: Welche Register-Adressen hat die LOGO!?

**A:** LOGO! 8 Register-Mapping:

| Typ | Register | Adressen |
|-----|----------|----------|
| Analoge Eingänge (AI) | Input Registers | 1-8 |
| Digitale Eingänge (I) | Discrete Inputs | 1-24 |
| Digitale Ausgänge (Q) | Coils | 8193-8212 (0x2001-0x2014) |
| Analoge Ausgänge (AQ) | Holding Registers | 528-535 (0x0210-0x0217) |

### F: Warum sind meine Temperaturwerte falsch?

**A:** LOGO! Temperatursensoren benötigen Kalibrierung:

```yaml
scale: 0.081        # Skalierungsfaktor
offset: -20.0       # Offset zur Kalibrierung
```

Passen Sie den `offset` an Ihre Sensoren an (Bereich: -19.0 bis -21.0).

### F: Wie finde ich heraus, welche Eingänge/Ausgänge belegt sind?

**A:**
1. Nutzen Sie die Scan-Funktion im Addon
2. Oder öffnen Sie Ihr Programm in LOGO! Soft Comfort
3. Schauen Sie in die Netzwerkkonfiguration der LOGO!

### F: Muss die LOGO! speziell konfiguriert werden?

**A:** Ja! In LOGO! Soft Comfort:

1. **Ethernet-Verbindung aktivieren**
2. **IP-Adresse festlegen**
3. **Modbus TCP-Server aktivieren**
4. **Port 510 einstellen**
5. **Programm übertragen und starten**

---

## Fehlersuche

### F: "Connection refused" Fehler

**A:** Mögliche Ursachen:
- Modbus TCP nicht aktiviert am Gerät
- Falscher Port
- Firewall blockiert
- Gerät im falschen Netzwerk

### F: "Timeout" Fehler

**A:** Lösungen:
- Erhöhen Sie den Timeout in `config.yaml`
- Überprüfen Sie die Netzwerkverbindung
- Reduzieren Sie `scan_interval`

### F: Werte sind immer 0 oder NULL

**A:** Überprüfen Sie:
- Slave ID korrekt?
- Register-Adresse korrekt?
- Datentyp korrekt? (uint16 vs int16)
- Scale/Offset korrekt?

### F: "Invalid config" nach Neustart

**A:**
1. Gehen Sie zu Entwicklerwerkzeuge → YAML
2. Klicken Sie auf "Check Configuration"
3. Sehen Sie sich die Fehler an
4. Häufige Probleme:
   - Falsche Einrückung (2 Spaces!)
   - Tab-Zeichen statt Spaces
   - Fehlende Anführungszeichen bei Sonderzeichen

### F: Addon startet nicht

**A:**
1. Überprüfen Sie die Addon-Logs
2. Port 8099 bereits belegt?
3. Docker-Problem? Neustart versuchen
4. Neuinstallation

### F: Web-UI lädt nicht

**A:**
- Überprüfen Sie, ob Addon läuft (Status: Started)
- Versuchen Sie: `http://homeassistant.local:8099`
- Versuchen Sie: `http://IP-ADRESSE:8099`
- Browser-Cache leeren
- Anderen Browser testen

---

## Performance & Optimierung

### F: Wie oft sollte ich Sensoren abfragen?

**A:** Empfohlene Intervalle:

- **Temperaturen:** 5-10 Sekunden
- **Schalter/Status:** 1 Sekunde
- **Energiezähler:** 10-30 Sekunden
- **Langsame Prozesse:** 60+ Sekunden

Zu häufige Abfragen belasten das Gerät!

### F: Kann ich die Netzwerklast reduzieren?

**A:** Ja:
1. Erhöhen Sie `scan_interval` für unwichtige Sensoren
2. Entfernen Sie ungenutzte Entitäten
3. Nutzen Sie `timeout` Werte moderat (3-5 Sekunden)

### F: Wie viele Geräte verträgt Home Assistant?

**A:** Home Assistant kann Dutzende von Modbus-Geräten verwalten. Die Grenze liegt meist am Netzwerk oder den Geräten selbst, nicht an Home Assistant.

---

## Erweiterte Nutzung

### F: Kann ich das Addon ohne Home Assistant nutzen?

**A:** Ja! Sie können es als Docker-Container standalone betreiben:

```bash
docker run -d -p 8099:8099 -v /pfad:/config universal-modbus-config
```

### F: Gibt es eine API?

**A:** Ja! Das Addon bietet eine RESTful API:

- `GET /api/manufacturers` - Hersteller abrufen
- `GET /api/models/{manufacturer}` - Modelle abrufen
- `POST /api/devices` - Gerät hinzufügen
- `POST /api/scan` - Gerät scannen
- `POST /api/generate` - Konfiguration generieren

Siehe [README_ADDON.md](README_ADDON.md#api-dokumenten) für Details.

### F: Kann ich eigene Geräteprofile erstellen?

**A:** Ja! Siehe [CONTRIBUTING.md](CONTRIBUTING.md#1-neue-geräteprofile-hinzufügen)

---

## Weitere Fragen?

- 📖 Lesen Sie die [vollständige Dokumentation](README_ADDON.md)
- 💡 Sehen Sie sich [Beispiele](EXAMPLES.md) an
- 🐛 Öffnen Sie ein [GitHub Issue](https://github.com/IHR_USERNAME/only_claude/issues)
- 💬 Fragen Sie in der [Home Assistant Community](https://community.home-assistant.io/)

---

**Ihre Frage ist nicht dabei?** Öffnen Sie ein Issue auf GitHub!

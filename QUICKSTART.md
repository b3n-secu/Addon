# 🚀 Schnellstart-Anleitung

Erhalten Sie Ihre Modbus-Geräte in 5 Minuten in Home Assistant!

## Schritt 1: Installation (2 Minuten)

### Option A: Über Repository (Empfohlen)

1. Öffnen Sie Home Assistant
2. **Einstellungen** → **Add-ons** → **Add-on Store**
3. Klicken Sie auf **⋮** (drei Punkte) → **Repositories**
4. Fügen Sie hinzu: `https://github.com/IHR_USERNAME/only_claude`
5. Suchen Sie "Universal Modbus Configurator"
6. Klicken Sie **Installieren**
7. Nach Installation: **Starten**
8. Optional: **Show in Sidebar** aktivieren

### Option B: Schnelltest (Standalone)

```bash
docker run -d \
  --name modbus-config \
  -p 8099:8099 \
  -v $(pwd)/config:/config \
  universal-modbus-config
```

## Schritt 2: Web-UI öffnen (30 Sekunden)

1. Öffnen Sie: `http://homeassistant.local:8099`
2. Sie sehen das Universal Modbus Configurator Interface

## Schritt 3: Erstes Gerät hinzufügen (2 Minuten)

### Beispiel: Siemens LOGO! 8

1. **Hersteller:** `Siemens` auswählen
2. **Modell:** `LOGO! 8` auswählen
3. **Gerätename:** z.B. `logo_haupthaus` eingeben
4. **IP-Adresse:** z.B. `192.168.178.201` eingeben
5. **Port:** Automatisch `510` (für LOGO!)
6. *Optional:* **Slave ID** leer lassen (Standard: 1)

### 📱 Verbindung testen

Klicken Sie auf **Verbindung testen**

✅ **Erfolgreich?** → Weiter zu Schritt 4
❌ **Fehlgeschlagen?** → Siehe [Troubleshooting](#troubleshooting)

### 🔍 Optional: Gerät scannen

Klicken Sie auf **Gerät scannen**

Das zeigt Ihnen:
- Anzahl verfügbarer Input Register
- Anzahl verfügbarer Holding Register
- Anzahl Discrete Inputs
- Anzahl Coils

### ➕ Gerät hinzufügen

Klicken Sie auf **Gerät hinzufügen**

Das Gerät erscheint nun in der Liste "Konfigurierte Geräte"

## Schritt 4: Weitere Geräte (optional)

Wiederholen Sie Schritt 3 für jedes weitere Gerät.

**Beispiel: 4 LOGO! Steuerungen**

| Name | IP-Adresse | Funktion |
|------|------------|----------|
| logo_1_obergeschoss | 192.168.178.201 | Beleuchtung OG |
| logo_2_untergeschoss | 192.168.178.202 | Bad UG |
| logo_3_garage | 192.168.178.203 | Garage + Pool |
| logo_4_keller | 192.168.178.204 | Energie-Monitoring |

## Schritt 5: Konfiguration generieren (30 Sekunden)

1. Scrollen Sie nach unten zu **"Konfiguration generieren"**
2. Klicken Sie **📄 Konfiguration generieren**
3. Warten Sie kurz...
4. ✅ **Erfolgreich!** Die Datei wurde erstellt

**Datei-Pfad:** `/config/modbus_generated.yaml`

### Optional: Konfiguration ansehen

Klicken Sie **👁️ Aktuelle Konfiguration anzeigen**

## Schritt 6: In Home Assistant einbinden (1 Minute)

### 6.1 configuration.yaml bearbeiten

1. Öffnen Sie **File Editor** oder **Studio Code Server**
2. Öffnen Sie `/config/configuration.yaml`
3. Fügen Sie hinzu:

```yaml
modbus: !include modbus_generated.yaml
```

4. **Speichern**

### 6.2 Konfiguration prüfen

1. **Entwicklerwerkzeuge** → **YAML**
2. Klicken Sie **Check Configuration**
3. Warten Sie...
4. ✅ **Configuration valid!**

### 6.3 Home Assistant neu starten

1. **Einstellungen** → **System**
2. Klicken Sie **Neu starten**
3. Bestätigen Sie
4. Warten Sie ~1-2 Minuten

## Schritt 7: Entitäten nutzen (Fertig! 🎉)

Nach dem Neustart sind Ihre Modbus-Entitäten verfügbar!

### Entitäten finden

1. **Einstellungen** → **Geräte & Dienste**
2. Suchen Sie nach "Modbus"
3. Oder suchen Sie direkt nach Ihrem Gerätenamen

### Beispiel-Entitäten (LOGO!):

**Sensoren (Temperaturen, Analogwerte):**
- `sensor.logo1_ai_1`
- `sensor.logo1_ai_2`
- ...

**Binary Sensoren (Digitale Eingänge):**
- `binary_sensor.logo1_i3`
- `binary_sensor.logo1_i4`
- ...

**Switches (Digitale Ausgänge):**
- `switch.logo1_q1`
- `switch.logo1_q2`
- ...

### Im Dashboard verwenden

Fügen Sie eine Karte hinzu:

```yaml
type: entities
title: Meine Modbus Geräte
entities:
  - entity: sensor.logo1_ai_1
    name: Wohnzimmer Temperatur
  - entity: switch.logo1_q1
    name: Wohnzimmer Licht
  - entity: binary_sensor.logo1_i3
    name: Bewegungsmelder
```

---

## ⚡ Express-Methode (Für Profis)

Wenn Sie die Parameter kennen:

```bash
# 1. Addon installieren & starten
# 2. Web-UI öffnen: http://homeassistant.local:8099
# 3. Geräte hinzufügen (Name, IP, Port)
# 4. Konfiguration generieren
# 5. configuration.yaml: modbus: !include modbus_generated.yaml
# 6. Config Check → Neustart
# 7. Fertig!
```

**Zeit:** ~3 Minuten für ein Gerät

---

## 🔧 Troubleshooting

### ❌ Verbindungstest fehlgeschlagen

**Checkliste:**
- [ ] IP-Adresse korrekt? (z.B. `192.168.178.201`)
- [ ] Port korrekt? (LOGO! = `510`, andere = `502`)
- [ ] Gerät eingeschaltet?
- [ ] Im gleichen Netzwerk?
- [ ] Modbus TCP am Gerät aktiviert?
- [ ] Firewall-Problem?

**Test:**
```bash
ping 192.168.178.201
```

### ❌ Keine Entitäten nach Neustart

**Prüfen:**
1. `modbus: !include modbus_generated.yaml` in `configuration.yaml`?
2. Configuration Check grün?
3. Home Assistant Log auf Fehler prüfen
4. Geräte online und erreichbar?

**Log öffnen:**
**Einstellungen** → **System** → **Protokolle**

Suchen nach: `modbus`

### ❌ "Invalid config" Fehler

**Häufige Ursachen:**
- Falsche Einrückung (verwenden Sie 2 Leerzeichen!)
- Tab-Zeichen statt Leerzeichen
- Fehlende Anführungszeichen

**YAML-Syntax prüfen:**
1. **Entwicklerwerkzeuge** → **YAML**
2. **Check Configuration**
3. Fehler werden angezeigt

### ❌ Addon startet nicht

1. Überprüfen Sie Addon-Logs
2. Port 8099 belegt? → Anderen Port verwenden
3. Docker-Neustart: **Addon stoppen** → **Starten**
4. Neuinstallation

### ❌ Werte sind falsch/0/NULL

**Für Temperaturen (LOGO!):**
```yaml
scale: 0.081
offset: -20.0    # Passen Sie an (zwischen -19.0 und -21.0)
```

**Für andere Sensoren:**
- Prüfen Sie `data_type` (uint16 vs int16)
- Prüfen Sie Register-Adresse
- Prüfen Sie Slave ID

---

## 📚 Nächste Schritte

### Konfiguration anpassen

1. Öffnen Sie `/config/modbus_generated.yaml`
2. Benennen Sie Entitäten um:
   ```yaml
   - name: "Logo1 Q1"  # Vorher
   - name: "Wohnzimmer Licht"  # Nachher
   ```
3. Passen Sie Parameter an (scale, offset, scan_interval)
4. Speichern & Neustart

### Automationen erstellen

```yaml
automation:
  - alias: "Licht bei Bewegung"
    trigger:
      platform: state
      entity_id: binary_sensor.logo1_i3
      to: 'on'
    action:
      service: switch.turn_on
      entity_id: switch.logo1_q1
```

### Dashboard gestalten

- Fügen Sie Entity Cards hinzu
- Erstellen Sie Gruppen
- Nutzen Sie Custom Cards (Button Card, Mini Graph Card)

### Weitere Geräte

- Schneider Electric PLC
- Energiezähler
- Wago Steuerungen
- Generische Modbus-Geräte

---

## 💡 Tipps für den Start

1. **Klein anfangen:** Beginnen Sie mit einem Gerät
2. **Testen:** Nutzen Sie Verbindungstest & Scan
3. **Dokumentieren:** Notieren Sie Register-Zuordnungen
4. **Sichern:** Backup Ihrer `modbus_generated.yaml`
5. **Community:** Fragen Sie bei Problemen

---

## 📖 Weitere Dokumentation

- **Vollständige Anleitung:** [README_ADDON.md](README_ADDON.md)
- **Beispiele:** [EXAMPLES.md](EXAMPLES.md)
- **FAQ:** [FAQ.md](FAQ.md)
- **Installation:** [INSTALL.md](INSTALL.md)

---

## 🆘 Hilfe benötigt?

- 💬 [GitHub Issues](https://github.com/IHR_USERNAME/only_claude/issues)
- 🏠 [Home Assistant Forum](https://community.home-assistant.io/)
- 📚 [Dokumentation](README_ADDON.md)

---

**Viel Erfolg mit Ihrem Modbus-Setup!** 🎉

**Geschätzte Zeit gesamt:** 5-10 Minuten

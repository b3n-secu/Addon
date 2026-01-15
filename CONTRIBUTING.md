# Beitragen zum Universal Modbus Configurator

Vielen Dank für Ihr Interesse, zum Universal Modbus Configurator beizutragen!

## Wie Sie beitragen können

### 1. Neue Geräteprofile hinzufügen

Wenn Sie ein Modbus-Gerät verwenden, das noch nicht unterstützt wird:

1. Forken Sie das Repository
2. Fügen Sie Ihr Geräteprofil zu `app/device_profiles.py` hinzu
3. Testen Sie das Profil gründlich
4. Dokumentieren Sie die Register-Adressen
5. Erstellen Sie einen Pull Request

**Beispiel für ein neues Profil:**

```python
"Ihr_Hersteller": {
    "Ihr_Modell": {
        "port": 502,
        "timeout": 5,
        "registers": {
            "analog_inputs": {
                "type": "sensor",
                "start_address": 0,
                "count": 16,
                "input_type": "input",
                "data_type": "uint16",
                "scan_interval": 5
            },
            "digital_outputs": {
                "type": "switch",
                "start_address": 0,
                "count": 32,
                "write_type": "coil",
                "scan_interval": 1
            }
        },
        "presets": {
            "temperature_sensor": {
                "unit_of_measurement": "°C",
                "scale": 0.1,
                "offset": 0,
                "device_class": "temperature",
                "precision": 1,
                "state_class": "measurement"
            }
        }
    }
}
```

### 2. Bugs melden

Wenn Sie einen Bug gefunden haben:

1. Überprüfen Sie, ob der Bug bereits gemeldet wurde
2. Öffnen Sie ein neues Issue auf GitHub
3. Beschreiben Sie das Problem detailliert:
   - Schritte zur Reproduktion
   - Erwartetes Verhalten
   - Tatsächliches Verhalten
   - Screenshots (falls relevant)
   - Home Assistant Version
   - Addon Version
   - Gerätetyp und Hersteller

### 3. Features vorschlagen

Haben Sie eine Idee für ein neues Feature?

1. Öffnen Sie ein Issue mit dem Label "feature request"
2. Beschreiben Sie:
   - Was soll das Feature tun?
   - Warum ist es nützlich?
   - Wie soll es funktionieren?

### 4. Dokumentation verbessern

Dokumentation kann immer besser werden:

- Rechtschreibfehler korrigieren
- Unklare Abschnitte verbessern
- Neue Beispiele hinzufügen
- Übersetzungen hinzufügen

### 5. Code-Beiträge

#### Entwicklungsumgebung einrichten

```bash
# Repository klonen
git clone https://github.com/IHR_USERNAME/only_claude.git
cd only_claude

# Python Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate

# Abhängigkeiten installieren
pip install -r app/requirements.txt

# Entwicklungsserver starten
cd app
python app.py
```

#### Code-Style

- Verwenden Sie Python 3.11+ Syntax
- Befolgen Sie PEP 8
- Fügen Sie Docstrings zu Funktionen hinzu
- Kommentieren Sie komplexen Code

#### Testing

Testen Sie Ihre Änderungen gründlich:

1. Testen Sie mit verschiedenen Gerätetypen
2. Testen Sie Edge Cases
3. Überprüfen Sie die generierte YAML-Syntax
4. Testen Sie im echten Home Assistant

#### Pull Request erstellen

1. Forken Sie das Repository
2. Erstellen Sie einen neuen Branch (`git checkout -b feature/mein-feature`)
3. Committen Sie Ihre Änderungen (`git commit -am 'Add: Mein neues Feature'`)
4. Pushen Sie den Branch (`git push origin feature/mein-feature`)
5. Öffnen Sie einen Pull Request

**Pull Request Checkliste:**
- [ ] Code folgt dem Style-Guide
- [ ] Dokumentation wurde aktualisiert
- [ ] CHANGELOG.md wurde aktualisiert
- [ ] Alle Tests bestehen
- [ ] Keine Merge-Konflikte

## Commit-Nachricht Konvention

Verwenden Sie aussagekräftige Commit-Nachrichten:

- `Feat: Neue Funktion hinzugefügt`
- `Fix: Bug in Scanner behoben`
- `Docs: Dokumentation verbessert`
- `Style: Code formatiert`
- `Refactor: Code umstrukturiert`
- `Test: Tests hinzugefügt`
- `Chore: Build-Prozess aktualisiert`

## Verhaltenskodex

- Seien Sie respektvoll und konstruktiv
- Helfen Sie anderen Benutzern
- Akzeptieren Sie konstruktive Kritik
- Konzentrieren Sie sich auf das Projekt

## Lizenz

Durch Beiträge stimmen Sie zu, dass Ihre Beiträge unter der MIT-Lizenz lizenziert werden.

## Fragen?

Bei Fragen können Sie:
- Ein Issue öffnen
- Eine Diskussion starten
- Die Community im Forum fragen

**Vielen Dank für Ihre Unterstützung!** 🙏

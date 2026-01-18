# Home Assistant Add-ons Repository

Dieses Repository enthält Home Assistant Add-ons für industrielle Automatisierung und Heimsteuerung.

## Verfügbare Add-ons

### 🔧 Modbus Configurator
Professionelles Add-on zur automatischen Konfiguration von Modbus-Geräten mit Nmap-basierter Geräteerkennung.

**Ordner:** `modbus/`
**Version:** 1.1.0
**Beschreibung:** Universeller Modbus Konfigurator mit professionellem Nmap-Scanner für Home Assistant - Unterstützt Siemens LOGO!, Schneider, ABB, Wago und weitere Hersteller

[Zur Dokumentation](modbus/README.md)

---

## Installation

### Repository hinzufügen

1. Öffnen Sie Home Assistant
2. Gehen Sie zu: **Supervisor → Add-on Store → ⋮ (Menü) → Repositories**
3. Fügen Sie diese URL hinzu:
   ```
   https://github.com/b3n-secu/Addon
   ```
4. Klicken Sie auf **Hinzufügen**

### Add-on installieren

Nach dem Hinzufügen des Repositories:

1. Finden Sie das gewünschte Add-on im Add-on Store
2. Klicken Sie darauf
3. Klicken Sie auf **Installieren**
4. Warten Sie, bis die Installation abgeschlossen ist
5. Konfigurieren Sie das Add-on nach Bedarf
6. Klicken Sie auf **Starten**

## Repository-Struktur

```
repository.json              # Repository-Metadaten
modbus/                      # Modbus Configurator Add-on
├── config.yaml             # Add-on Konfiguration
├── Dockerfile              # Container Build
├── README.md               # Add-on Dokumentation
├── build.yaml              # Multi-Arch Build
├── icon.png                # Add-on Icon
├── logo.png                # Add-on Logo
├── run.sh                  # Startup Script
├── app/                    # Anwendungscode
│   ├── app.py
│   ├── modbus_scanner.py
│   ├── nmap_scanner.py
│   ├── config_generator.py
│   ├── device_profiles.py
│   ├── requirements.txt
│   └── static/
│       └── index.html
└── translations/           # Übersetzungen
    ├── en.yaml
    └── de.yaml

# Zukünftige Add-ons können hier hinzugefügt werden:
# another-addon/
# ├── config.yaml
# ├── Dockerfile
# └── ...
```

## Weitere Add-ons hinzufügen

Um weitere Add-ons zu diesem Repository hinzuzufügen:

1. Erstellen Sie einen neuen Ordner mit einem beschreibenden Namen (z.B. `mqtt-bridge/`)
2. Fügen Sie die erforderlichen Dateien hinzu:
   - `config.yaml` (erforderlich)
   - `Dockerfile` (erforderlich)
   - `README.md` (empfohlen)
   - `icon.png` (empfohlen)
   - `logo.png` (optional)
   - `build.yaml` (für Multi-Arch Builds)
3. Committen und pushen Sie die Änderungen
4. Das neue Add-on erscheint automatisch im Home Assistant Add-on Store

## Support & Beiträge

- **Issues:** [GitHub Issues](https://github.com/b3n-secu/Addon/issues)
- **Discussions:** [GitHub Discussions](https://github.com/b3n-secu/Addon/discussions)
- **Pull Requests:** Beiträge sind willkommen!

## Lizenz

MIT License - Siehe [LICENSE](LICENSE) für Details.

## Credits

- Home Assistant Community
- Alle Add-on-spezifischen Credits finden Sie in den jeweiligen README-Dateien

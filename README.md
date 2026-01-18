# 🏠 Home Assistant Add-ons Repository

Professionelle Home Assistant Add-ons für industrielle Automatisierung und Smart Home Integration.

## 📦 Verfügbare Add-ons

### 🔧 [Modbus Configurator](modbus/)

Professioneller Modbus Konfigurator mit automatischer Geräteerkennung via Nmap.

**Features:**
- 🚀 Nmap-basierte Geräteerkennung mit modbus-discover NSE Script
- ⚡ Quick Scan für schnelle Ergebnisse
- 🎯 Anpassbare Port-Ranges
- 🌐 Unterstützt Siemens LOGO!, Schneider, ABB, Wago, Allen Bradley und mehr
- 📝 Automatische YAML-Konfigurationsgenerierung

**Version:** 1.1.0
**[Zur Dokumentation →](modbus/README.md)**

---

## 🚀 Installation

### 1. Repository hinzufügen

1. Öffnen Sie **Home Assistant**
2. Navigieren Sie zu: **Supervisor → Add-on Store**
3. Klicken Sie auf **⋮ (Menü)** oben rechts
4. Wählen Sie **Repositories**
5. Fügen Sie diese URL hinzu:
   ```
   https://github.com/b3n-secu/Addon
   ```
6. Klicken Sie auf **Hinzufügen**

### 2. Add-on installieren

Nach dem Hinzufügen des Repositories finden Sie die Add-ons im Add-on Store:

1. Suchen Sie nach dem gewünschten Add-on
2. Klicken Sie auf **Installieren**
3. Konfigurieren Sie das Add-on
4. Starten Sie das Add-on

## 📖 Dokumentation

- **[Repository-Struktur](README_REPO.md)** - Technische Details zum Repository
- **[Modbus Configurator](modbus/README.md)** - Vollständige Add-on Dokumentation
- **[Build-Anleitung](BUILD.md)** - Für Entwickler
- **[FAQ](FAQ.md)** - Häufig gestellte Fragen
- **[Troubleshooting](TROUBLESHOOTING.md)** - Problemlösungen

## 🛠️ Für Entwickler

### Lokales Testen

```bash
# Modbus Add-on lokal bauen und testen
./build-and-test.sh

# Oder manuell
docker build -t modbus-configurator:latest ./modbus
docker run -d -p 8099:8099 -v $(pwd)/test-config:/config modbus-configurator:latest
```

### Neues Add-on hinzufügen

Um ein neues Add-on zu diesem Repository hinzuzufügen:

1. Erstellen Sie einen neuen Ordner (z.B. `my-addon/`)
2. Fügen Sie die erforderlichen Dateien hinzu:
   - `config.yaml` ✅ Erforderlich
   - `Dockerfile` ✅ Erforderlich
   - `README.md` 📝 Empfohlen
   - `icon.png` 🖼️ Empfohlen
   - `build.yaml` 🏗️ Für Multi-Arch
3. Committen und pushen Sie die Änderungen

```bash
git add my-addon/
git commit -m "Add: New add-on 'My Addon'"
git push
```

## 🤝 Beiträge

Beiträge sind herzlich willkommen!

- **Bug-Report:** [Issue erstellen](https://github.com/b3n-secu/Addon/issues/new)
- **Feature-Request:** [Discussion starten](https://github.com/b3n-secu/Addon/discussions)
- **Pull Request:** [PR erstellen](https://github.com/b3n-secu/Addon/pulls)

## 📝 Changelog

### Repository
- **2024-01:** Multi-Add-on Repository-Struktur implementiert
- **2024-01:** Modbus Configurator v1.1.0 hinzugefügt

### Modbus Configurator v1.1.0
- ✨ Professioneller Nmap-Scanner
- ✨ Automatische Gerätetyp-Erkennung
- ✨ Anpassbare Port-Ranges
- 🔧 Verbesserte UI
- 🐛 Diverse Bugfixes

[Vollständiges Changelog](modbus/README.md#changelog)

## 📄 Lizenz

MIT License - Siehe [LICENSE](LICENSE) für Details.

## 🙏 Credits

- **Home Assistant** Community
- **DefCon 16** Modbus Security Research
- **Nmap** Project und modbus-discover NSE Script
- Alle Mitwirkenden

---

**Maintained by:** [@b3n-secu](https://github.com/b3n-secu)
**Repository:** [github.com/b3n-secu/Addon](https://github.com/b3n-secu/Addon)

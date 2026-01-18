# Beitragen zu Home Assistant Add-ons

Vielen Dank für Ihr Interesse, zu diesem Repository beizutragen!

## 🚀 Neues Add-on hinzufügen

### Struktur

Erstellen Sie einen neuen Ordner mit einem beschreibenden Namen:

```
my-addon/
├── config.yaml          # ✅ Erforderlich - Add-on Konfiguration
├── Dockerfile           # ✅ Erforderlich - Container Build
├── README.md            # 📝 Empfohlen - Dokumentation
├── icon.png             # 🖼️ Empfohlen - Add-on Icon (256x256px)
├── logo.png             # 🖼️ Optional - Add-on Logo
├── build.yaml           # 🏗️ Für Multi-Arch Builds
├── run.sh               # 🚀 Startup Script
└── translations/        # 🌍 i18n Übersetzungen
    ├── en.yaml
    └── de.yaml
```

### config.yaml Beispiel

```yaml
name: "Mein Add-on"
version: "1.0.0"
slug: my_addon
description: "Kurze Beschreibung"
arch:
  - armhf
  - armv7
  - aarch64
  - amd64
  - i386
init: false
ports:
  8080/tcp: 8080
options:
  option1: "default"
schema:
  option1: str
```

### Schritte

1. **Fork** erstellen
2. **Branch** erstellen: `git checkout -b feature/my-addon`
3. **Add-on Ordner** erstellen
4. **Dateien** hinzufügen (siehe Struktur oben)
5. **Lokal testen**:
   ```bash
   docker build -t my-addon:test ./my-addon
   docker run -d -p 8080:8080 my-addon:test
   ```
6. **Committen**:
   ```bash
   git add my-addon/
   git commit -m "Add: Mein Add-on v1.0.0"
   ```
7. **Push**: `git push origin feature/my-addon`
8. **Pull Request** erstellen

## 🐛 Bugfix

1. **Issue** erstellen oder referenzieren
2. **Branch** erstellen: `git checkout -b fix/issue-123`
3. **Fix** implementieren
4. **Testen**
5. **Committen**: `git commit -m "Fix: Beschreibung (#123)"`
6. **Pull Request** erstellen

## ✨ Feature

1. **Discussion** starten für größere Features
2. **Branch** erstellen: `git checkout -b feature/feature-name`
3. **Feature** implementieren
4. **Dokumentation** aktualisieren
5. **Testen**
6. **Pull Request** erstellen

## 📝 Dokumentation

Dokumentationsverbesserungen sind immer willkommen:

- README.md Verbesserungen
- Neue Beispiele
- Tutorials
- FAQ Ergänzungen

## ✅ Code-Qualität

### Python
- Verwenden Sie Type Hints
- Folgen Sie PEP 8
- Fügen Sie Docstrings hinzu
- Schreiben Sie Tests (wenn möglich)

### Docker
- Verwenden Sie Alpine Linux als Basis
- Minimieren Sie Image-Größe
- Multi-Stage Builds für Kompilation

### Commit Messages

Verwenden Sie konventionelle Commit-Nachrichten:

- `Add: Neue Funktion`
- `Fix: Bugfix`
- `Docs: Dokumentation`
- `Refactor: Code-Refactoring`
- `Test: Tests`
- `Chore: Wartung`

Beispiele:
```
Add: MQTT Bridge Add-on v1.0.0
Fix: Network scan timeout issue (#45)
Docs: Improve installation instructions
```

## 🧪 Testing

Testen Sie Ihr Add-on vor dem PR:

1. **Build** lokal:
   ```bash
   docker build -t test:latest ./my-addon
   ```

2. **Run** Container:
   ```bash
   docker run -d --name test -p 8080:8080 test:latest
   ```

3. **Logs** prüfen:
   ```bash
   docker logs -f test
   ```

4. **Funktionalität** testen

5. **Cleanup**:
   ```bash
   docker stop test && docker rm test
   ```

## 📦 Multi-Architektur Builds

Für Multi-Arch Builds erstellen Sie eine `build.yaml`:

```yaml
build_from:
  aarch64: ghcr.io/home-assistant/aarch64-base:latest
  amd64: ghcr.io/home-assistant/amd64-base:latest
  armhf: ghcr.io/home-assistant/armhf-base:latest
  armv7: ghcr.io/home-assistant/armv7-base:latest
  i386: ghcr.io/home-assistant/i386-base:latest
args:
  PYTHON_VERSION: "3.11"
```

## 🔒 Sicherheit

- Keine Secrets in Code committen
- Verwenden Sie offizielle Base Images
- Minimieren Sie Dependencies
- Regelmäßige Sicherheitsupdates

## 📄 Lizenz

Alle Beiträge unterliegen der MIT-Lizenz dieses Repositories.

## 💬 Fragen?

- **Issues:** [GitHub Issues](https://github.com/b3n-secu/Addon/issues)
- **Discussions:** [GitHub Discussions](https://github.com/b3n-secu/Addon/discussions)

Vielen Dank für Ihre Unterstützung! 🎉

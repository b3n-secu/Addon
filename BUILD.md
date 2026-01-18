# Build-Anleitung - Universal Modbus Configurator

## Docker Container lokal bauen

### Voraussetzungen
- Docker installiert
- Git installiert

### Build-Prozess

1. **Repository klonen:**
```bash
git clone <repository-url>
cd only_claude
```

2. **Docker Image bauen:**
```bash
docker build -t universal-modbus-configurator:latest .
```

3. **Container testen:**
```bash
docker run -d \
  --name modbus-config-test \
  -p 8099:8099 \
  -v $(pwd)/test-config:/config \
  universal-modbus-configurator:latest
```

4. **Logs anzeigen:**
```bash
docker logs -f modbus-config-test
```

5. **Im Browser öffnen:**
```
http://localhost:8099
```

6. **Container stoppen:**
```bash
docker stop modbus-config-test
docker rm modbus-config-test
```

## Nmap-Funktionalität testen

Nach dem Start des Containers:

1. Öffnen Sie `http://localhost:8099`
2. Sie sollten **keine** Warnung über fehlendes nmap sehen
3. Beide Scan-Buttons sollten aktiviert sein:
   - 🚀 Nmap Scan starten
   - ⚡ Quick Scan (Python)

### Nmap im Container überprüfen

```bash
# Shell im Container öffnen
docker exec -it modbus-config-test sh

# Nmap-Version prüfen
nmap --version

# NSE Scripts prüfen
ls -la /usr/share/nmap/scripts/modbus*

# Python-nmap testen
python3 -c "import nmap; print('✓ python-nmap erfolgreich importiert')"

# Exit
exit
```

## Multi-Architektur Build (Home Assistant Add-on)

Für das offizielle Home Assistant Add-on Repository:

```bash
# Build für alle Architekturen
docker buildx build \
  --platform linux/amd64,linux/arm64,linux/arm/v7 \
  -t ghcr.io/homeassistant/amd64-addon-universal-modbus-config:latest \
  --push \
  .
```

## Troubleshooting

### Problem: python-nmap Installation schlägt fehl

**Lösung:** Der Dockerfile verwendet jetzt Build-Dependencies und `--no-build-isolation`:
```dockerfile
RUN apk add --no-cache gcc musl-dev python3-dev \
    && pip3 install --no-cache-dir --no-build-isolation python-nmap \
    && apk del gcc musl-dev python3-dev
```

### Problem: "Nmap ist nicht verfügbar" Warnung in UI

**Ursachen:**
1. Container wurde nicht mit aktuellem Dockerfile gebaut
2. Nmap-Installation im Container fehlgeschlagen

**Lösung:**
```bash
# Container neu bauen
docker build --no-cache -t universal-modbus-configurator:latest .

# Container starten und testen
docker run -it --rm universal-modbus-configurator:latest sh
nmap --version
python3 -c "import nmap"
```

### Problem: Modbus-Geräte werden nicht gefunden

**Netzwerk-Modus prüfen:**
```bash
# Container mit Host-Netzwerk starten (für besseren Netzwerk-Zugriff)
docker run -d \
  --name modbus-config-test \
  --network host \
  -v $(pwd)/test-config:/config \
  universal-modbus-configurator:latest
```

## Performance-Optimierung

### Image-Größe reduzieren

Der Dockerfile entfernt automatisch Build-Dependencies nach der Installation:
```dockerfile
&& apk del gcc musl-dev python3-dev
```

### Scan-Performance

- **Quick Scan:** ~10-30 Sekunden für /24 Netzwerk
- **Nmap Scan:** ~2-5 Minuten für /24 Netzwerk (abhängig von Port-Range)

**Port-Range optimieren:**
- Standard: `502,510,20000-20100` (schnell)
- Erweitert: `1-65535` (sehr langsam, nicht empfohlen)
- Empfohlen: Nur bekannte Modbus-Ports scannen

## Entwicklung

### Lokale Entwicklung ohne Docker

```bash
cd app

# Virtuelle Umgebung erstellen
python3 -m venv venv
source venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt

# Flask-App starten
python3 app.py
```

**Hinweis:** Nmap muss auf dem Host-System installiert sein:
```bash
# Debian/Ubuntu
sudo apt-get install nmap

# macOS
brew install nmap

# Alpine Linux
apk add nmap nmap-scripts
```

## Home Assistant Add-on Installation

1. Navigieren Sie zu **Supervisor → Add-on Store → ⋮ → Repositories**
2. Fügen Sie hinzu: `https://github.com/ihr-username/ha-addons`
3. Installieren Sie "Universal Modbus Configurator"
4. Starten Sie das Add-on
5. Öffnen Sie die Web UI über **Supervisor → Universal Modbus Configurator → Web UI**

## Lizenz

[Siehe LICENSE]

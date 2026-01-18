# Installation Guide

## Home Assistant Addon Installation

### Option 1: Repository hinzufügen (Empfohlen)

1. Öffnen Sie Home Assistant
2. Gehen Sie zu **Einstellungen** → **Add-ons** → **Add-on Store**
3. Klicken Sie auf die **drei Punkte** (⋮) oben rechts
4. Wählen Sie **Repositories**
5. Fügen Sie diese URL hinzu:
   ```
   https://github.com/IHR_USERNAME/only_claude
   ```
6. Klicken Sie auf **Hinzufügen**
7. Schließen Sie den Dialog
8. Suchen Sie nach "Universal Modbus Configurator"
9. Klicken Sie auf das Addon
10. Klicken Sie auf **Installieren**
11. Warten Sie, bis die Installation abgeschlossen ist
12. Klicken Sie auf **Starten**
13. Optional: Aktivieren Sie **Show in Sidebar**
14. Klicken Sie auf **Web UI öffnen**

### Option 2: Lokale Installation

1. Verbinden Sie sich per SSH mit Ihrem Home Assistant System
2. Navigieren Sie zum Addons-Verzeichnis:
   ```bash
   cd /addons
   ```
3. Erstellen Sie einen Ordner für das Addon:
   ```bash
   mkdir universal_modbus_config
   ```
4. Kopieren Sie alle Dateien in diesen Ordner
5. Starten Sie Home Assistant neu
6. Das Addon erscheint unter "Local add-ons"

### Option 3: Docker Standalone

Falls Sie das Addon ohne Home Assistant nutzen möchten:

```bash
# Repository klonen
git clone https://github.com/IHR_USERNAME/only_claude.git
cd Addon

# Docker Image bauen
docker build -t universal-modbus-config .

# Container starten
docker run -d \
  --name modbus-config \
  -p 8099:8099 \
  -v /path/to/config:/config \
  universal-modbus-config
```

Öffnen Sie dann http://localhost:8099 im Browser.

## Nach der Installation

### 1. Erstkonfiguration

1. Öffnen Sie das Web UI
2. Konfigurieren Sie Ihr erstes Gerät
3. Testen Sie die Verbindung
4. Generieren Sie die Konfiguration

### 2. Integration in Home Assistant

Öffnen Sie Ihre `configuration.yaml` und fügen Sie hinzu:

```yaml
modbus: !include modbus_generated.yaml
```

### 3. Konfiguration prüfen

1. Gehen Sie zu **Entwicklerwerkzeuge**
2. Klicken Sie auf **YAML**
3. Klicken Sie auf **Check Configuration**
4. Überprüfen Sie, ob Fehler angezeigt werden

### 4. Home Assistant neu starten

1. Gehen Sie zu **Einstellungen** → **System**
2. Klicken Sie auf **Neu starten**
3. Bestätigen Sie den Neustart

### 5. Entitäten überprüfen

Nach dem Neustart:
1. Gehen Sie zu **Einstellungen** → **Geräte & Dienste**
2. Suchen Sie nach "Modbus"
3. Ihre Geräte und Entitäten sollten erscheinen

## Troubleshooting

### Addon startet nicht

**Mögliche Ursachen:**
- Port 8099 ist bereits belegt
- Nicht genügend Ressourcen
- Docker-Problem

**Lösungen:**
1. Überprüfen Sie die Addon-Logs
2. Starten Sie Home Assistant neu
3. Deinstallieren und neu installieren

### Keine Verbindung zum Web UI

**Lösungen:**
1. Überprüfen Sie, ob das Addon läuft
2. Prüfen Sie die Port-Konfiguration
3. Versuchen Sie http://homeassistant.local:8099
4. Deaktivieren Sie temporär Firewall/VPN

### Konfiguration wird nicht generiert

**Lösungen:**
1. Überprüfen Sie die Schreibrechte auf `/config`
2. Prüfen Sie die Addon-Logs
3. Stellen Sie sicher, dass Geräte hinzugefügt wurden

## Update

### Addon Update

1. Gehen Sie zu **Einstellungen** → **Add-ons**
2. Klicken Sie auf "Universal Modbus Configurator"
3. Wenn ein Update verfügbar ist, erscheint ein **Update**-Button
4. Klicken Sie auf **Update**
5. Warten Sie, bis das Update abgeschlossen ist
6. Starten Sie das Addon neu

### Manuelle Updates

```bash
cd /addons/universal_modbus_config
git pull origin main
# Dann Addon in Home Assistant neu starten
```

## Deinstallation

1. Stoppen Sie das Addon
2. Klicken Sie auf **Deinstallieren**
3. Bestätigen Sie die Deinstallation
4. Optional: Löschen Sie die generierte `modbus_generated.yaml`

## Support

Bei Problemen:
- Überprüfen Sie die Addon-Logs
- Lesen Sie die [Troubleshooting-Sektion](README_ADDON.md#troubleshooting)
- Öffnen Sie ein Issue auf GitHub
- Fragen Sie in der Home Assistant Community

---

**Viel Erfolg mit Ihrem Universal Modbus Configurator!** 🎉

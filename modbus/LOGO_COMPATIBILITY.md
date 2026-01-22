# LOGO! Kompatibilität - Wichtige Hinweise

## ⚠️ KRITISCH: LOGO! v7 und v8 Unterschiede

### LOGO! v8 (0BA8) ✅
- **Modbus TCP**: Voll unterstützt
- **Port**: 502 oder 510
- **Kompatibilität**: 100% mit diesem Add-on
- **Features**: DI, DO, AI, AO, NI, NQ (Network I/O)

### LOGO! v7 / 0BA7 ❌
- **Modbus TCP**: NICHT unterstützt
- **Protokoll**: Nur S7-Protokoll
- **Port**: 102 (S7-Protokoll)
- **Kompatibilität**: NICHT mit diesem Add-on nutzbar
- **Alternative**: Verwenden Sie ein S7-basiertes Tool (z.B. snap7, python-snap7)

## 🔍 Wie erkennen Sie Ihre LOGO! Version?

### Auf dem Gerät:
- **LOGO! 8**: Display zeigt "0BA8" in der Typbezeichnung
- **LOGO! v7**: Display zeigt "0BA7" in der Typbezeichnung

### Modbus-Test:
```bash
# LOGO! 8 antwortet auf Port 510:
nc -zv <LOGO-IP> 510

# LOGO! v7 antwortet NICHT auf Port 510
# Aber auf Port 102 (S7):
nc -zv <LOGO-IP> 102
```

## 💡 Empfehlung

**Wenn Sie LOGO! v7 haben:**
- Dieses Add-on funktioniert NICHT
- Verwenden Sie stattdessen:
  - Home Assistant S7 Integration (falls verfügbar)
  - Custom Component mit snap7
  - Upgrade auf LOGO! 8 (Hardware-Update)

**Wenn Sie LOGO! 8 haben:**
- Perfekt! Dieses Add-on ist genau richtig für Sie
- Volle Modbus-Unterstützung inkl. Network I/O

## 🔧 Technische Details

### LOGO! v8 Modbus TCP Spezifikationen:
- **Supported Ports**: 502 (Standard) oder 510 (LOGO! Standard)
- **Slave ID**: 1 (Standard)
- **Digital Inputs (DI)**: Discrete Inputs, Address 1-24
- **Digital Outputs (DO)**: Coils, Write Address 1-20, Verify Address 8193+
- **Analog Inputs (AI)**: Input Registers, Address 1-8
- **Analog Outputs (AO)**: Holding Registers, Address 528+
- **Network Inputs (NI)**: Discrete Inputs, Address 0-63 (NI1-NI64)
- **Network Outputs (NQ)**: Coils, Address 0-63 (NQ1-NQ64)

### LOGO! v7 Protokoll-Einschränkungen:
- **Nur S7-Kommunikation**: Port 102 (ISO-TSAP)
- **Kein Modbus**: Keine Modbus TCP Unterstützung
- **Keine Network I/O**: NI/NQ nicht verfügbar
- **Alternative Protokolle**: Nur proprietäres S7-Protokoll

## 📚 Quellen

- Siemens LOGO! Manual (Version 8.3)
- LOGO! 0BA7 Technical Specifications: S7-Kommunikation über Port 102
- LOGO! 0BA8 Technical Specifications: Nativer Modbus TCP Server (Port 502/510)
- Siemens Industry Support: LOGO! v7 vs v8 Protokollvergleich

## ❓ Häufige Fragen (FAQ)

**Q: Kann ich LOGO! v7 mit einem Modbus-Gateway verwenden?**
A: Theoretisch ja, aber es ist nicht empfohlen. Ein S7-zu-Modbus Gateway würde funktionieren, aber die Komplexität und Kosten rechtfertigen meist ein Upgrade auf LOGO! v8.

**Q: Wie erkenne ich, ob mein LOGO! Modbus TCP unterstützt?**
A: Führen Sie einen Port-Scan durch: `nc -zv <LOGO-IP> 510`. Wenn Port 510 antwortet, haben Sie LOGO! v8. Wenn Port 102 antwortet, haben Sie LOGO! v7.

**Q: Funktioniert Network I/O (NI/NQ) mit LOGO! v7?**
A: Nein. Network I/O ist eine LOGO! v8 exklusive Funktion und erfordert Modbus TCP.

---

**Hinweis**: Wenn Sie eine LOGO! v7 über Modbus ansprechen möchten, benötigen Sie ein externes Modbus-Gateway oder ein Upgrade auf LOGO! v8. Die empfohlene Lösung ist ein Hardware-Upgrade auf LOGO! 8 für native Modbus TCP Unterstützung.

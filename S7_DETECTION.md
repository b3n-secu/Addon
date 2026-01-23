# S7 Protocol Detection for LOGO! v7 and S7 PLCs

This document describes the S7 protocol detection system implemented in the Universal Modbus Configurator addon.

## Overview

The S7 scanner module (`s7_scanner.py`) implements automatic detection of Siemens S7-compatible devices, including:

- **LOGO! v7 (0BA7)** - Small automation devices (Port 102, S7 protocol only)
- **S7-300 Series** - Mid-range PLCs
- **S7-400 Series** - High-end PLCs
- **Other S7-compatible devices**

## S7comm Protocol

S7comm (S7 Communication) is a Siemens proprietary protocol based on the Wireshark S7comm specification.

### Protocol Stack

| OSI Layer | Protocol |
|-----------|----------|
| 7 - Application | S7 Communication |
| 6 - Presentation | S7 Communication |
| 5 - Session | S7 Communication |
| 4 - Transport | ISO-on-TCP (RFC 1006 - TPKT) |
| 3 - Network | IP |
| 2 - Data Link | Ethernet |
| 1 - Physical | Ethernet |

### Connection Parameters

- **Port**: 102 (TCP)
- **Protocol Identifier**: 0x32 (first byte of S7comm payload)
- **TPKT**: RFC 1006 - ISO transport services on top of TCP
- **COTP**: ISO 8073 Connection-Oriented Transport Protocol

### 3-Step Connection Establishment

1. **TCP Connect**
   - Connect to PLC on TCP port 102

2. **ISO/COTP Connect Request**
   - Send COTP Connection Request with TSAP parameters
   - Receive COTP Connection Confirm (PDU type 0xD0)

3. **S7comm Setup Communication**
   - Send S7comm Setup (Function 0xF0)
   - Negotiate PDU size and communication parameters
   - Receive Ack_Data response (ROSCTR 0x03)

## TSAP (Transport Service Access Point)

TSAP is a 2-byte identifier used to address specific communication endpoints.

### TSAP Structure

```
Byte 1: Communication Type
- 0x01 = PG (Programming Device)
- 0x02 = OP (Operator Panel)
- 0x03 = S7 Basic Communication

Byte 2: Rack and Slot
- Bits 5-7: Rack Number (0-7)
- Bits 0-4: Slot Number (0-31)
```

### Common TSAP Values

| Device | TSAP | Meaning |
|--------|------|---------|
| LOGO! v7 | 0x2000 | OP communication, Rack 0, Slot 0 |
| S7-300 CPU Slot 2 | 0x0102 | PG communication, Rack 0, Slot 2 |
| S7-400 CPU Slot 3 | 0x0103 | PG communication, Rack 0, Slot 3 |

### Creating TSAP Values

Use the helper function:

```python
from s7_scanner import S7Scanner

# LOGO! v7: OP communication, Rack 0, Slot 0
tsap = S7Scanner.create_tsap(comm_type=2, rack=0, slot=0)  # Returns 0x0200 (512)

# S7-300: PG communication, Rack 0, Slot 2
tsap = S7Scanner.create_tsap(comm_type=1, rack=0, slot=2)  # Returns 0x0102 (258)
```

## Device Detection

### Single Device Scan

```python
from s7_scanner import S7Scanner

scanner = S7Scanner('192.168.1.100', port=102, timeout=5)
result = scanner.detect_s7_device(
    src_tsap=0x0100,  # Local TSAP (PG)
    dst_tsap=0x2000   # Remote TSAP (OP for LOGO!)
)

if result['success']:
    print(f"Device Type: {result['device_type']}")
    print(f"PDU Size: {result['pdu_size']}")
else:
    print(f"Error: {result['error']}")
```

### Network Scan

```python
from s7_scanner import S7Scanner

devices = S7Scanner.scan_network_for_s7(
    network='192.168.1.0/24',
    timeout=2  # seconds per host
)

for device in devices:
    print(f"Found: {device['host']} - {device['device_type']}")
```

## API Endpoints

### POST /api/scan-s7

Scan a single IP address for S7 protocol.

**Request:**
```json
{
  "host": "192.168.1.100",
  "port": 102,
  "src_tsap": 256,
  "dst_tsap": 512,
  "timeout": 5
}
```

**Response (Success):**
```json
{
  "success": true,
  "device_type": "LOGO! v7 (0BA7)",
  "port": 102,
  "tsap_src": 256,
  "tsap_dst": 512,
  "pdu_size": 480
}
```

**Response (Failure):**
```json
{
  "success": false,
  "device_type": null,
  "port": 102,
  "tsap_src": 256,
  "tsap_dst": 512,
  "pdu_size": null,
  "error": "Connection refused"
}
```

### POST /api/scan-network-s7

Scan entire network for S7 devices.

**Request:**
```json
{
  "network": "192.168.1.0/24",
  "timeout": 2,
  "auto_add": false
}
```

**Response:**
```json
{
  "success": true,
  "devices": [
    {
      "host": "192.168.1.100",
      "port": 102,
      "device_type": "LOGO! v7 (0BA7)",
      "pdu_size": 480,
      "tsap_src": 256,
      "tsap_dst": 512
    }
  ],
  "total": 1,
  "added_count": 0,
  "scan_method": "s7comm",
  "network": "192.168.1.0/24"
}
```

## Device Identification

### LOGO! v7 (0BA7)

- **TSAP**: 0x2000 (OP communication, Rack 0, Slot 0)
- **PDU Size**: 480 bytes (typical)
- **Port**: 102 only (no Modbus support)
- **Protocol**: S7comm only

### S7-300 Series

- **TSAP**: 0x01XX (PG communication, where XX = slot number)
- **PDU Size**: Variable (typically 240-480 bytes)
- **Port**: 102
- **Protocol**: S7comm

### S7-400 Series

- **TSAP**: 0x01XX (where rack/slot encoded)
- **PDU Size**: Variable (up to 960 bytes)
- **Port**: 102
- **Protocol**: S7comm

## Implementation Details

### TPKT Header (RFC 1006)

```
Offset  Length  Description
0       1       Version (0x03)
1       1       Reserved (0x00)
2       2       Packet Length (big-endian, includes TPKT header)
```

### COTP Connection Request

```
Offset  Length  Description
0       1       Length Indicator (length without this byte)
1       1       PDU Type (0xE0 = CR - Connect Request)
2       2       Destination Reference (0x0000)
4       2       Source Reference (0x0001)
6       1       Class/Option (0x00)
7       1       Parameter Code 0xC1 (src-tsap)
8       1       Parameter Length
9       n       Parameter Value (src-tsap)
...     ...     More parameters (dst-tsap, tpdu-size)
```

### S7comm Setup Communication

```
Offset  Length  Description
0       1       Protocol ID (0x32)
1       1       ROSCTR (0x01 = Job)
2       2       Reserved (0x0000)
4       2       PDU Reference (0x0000)
6       2       Parameter Length
8       2       Data Length (0x0000)
10      1       Function (0xF0 = Setup communication)
11      1       Reserved (0x00)
12      2       Max AMQ (calling)
14      2       Max AMQ (called)
16      2       PDU Length
```

## Troubleshooting

### Connection Refused

- **Cause**: Port 102 is not open or device doesn't support S7
- **Solution**: Check if device is LOGO! v7 or S7 PLC. LOGO! v8 uses Modbus (port 502/510), not S7.

### COTP Connection Rejected

- **Cause**: Incorrect TSAP values
- **Solution**: Try different TSAP combinations:
  - LOGO! v7: src=0x0100, dst=0x2000
  - S7-300: src=0x0100, dst=0x0102 (or slot number)

### No S7comm Response

- **Cause**: Device doesn't support S7comm protocol
- **Solution**: Device may be Modbus-only (LOGO! v8). Try Modbus scan instead.

### Timeout

- **Cause**: Device is slow to respond or network latency
- **Solution**: Increase timeout value (default is 5 seconds)

## References

- **Wireshark S7comm Wiki**: https://wiki.wireshark.org/S7comm
- **RFC 1006**: ISO transport services on top of TCP
- **RFC 905**: ISO 8073 COTP
- **Siemens Documentation**: Support Industry Siemens (view/26483647)

## Related Documentation

- [LOGO_COMPATIBILITY.md](LOGO_COMPATIBILITY.md) - LOGO! v7 vs v8 comparison
- [LOGO_V7_S7_INTEGRATION.md](LOGO_V7_S7_INTEGRATION.md) - Complete S7 integration guide
- [README.md](README.md) - Main addon documentation

## License

This implementation is based on publicly available protocol specifications and is intended for legitimate automation and integration purposes.

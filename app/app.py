"""
busbot - Universal Modbus Configurator
"""
import os
import json
import logging
import sys
import yaml
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from device_profiles import get_manufacturers, get_models, get_device_profile
from modbus_scanner import ModbusScanner, NetworkScanner
from config_generator import ModbusConfigGenerator
from network_detector import NetworkDetector
from manufacturer_database import (
    MANUFACTURER_PORTS, PROTOCOL_PORTS, SCAN_PORT_RANGES,
    get_manufacturer_info, get_device_info, detect_manufacturer_by_port,
    get_recommended_ports_for_scan, get_all_manufacturers, get_devices_for_manufacturer
)
from auto_scanner import auto_scanner
from scan_progress import scan_progress
from ping_scanner import PingScanner, get_vendor_from_mac, quick_ping_scan

# Configure logging FIRST - ensure logs go to stderr, not stdout (prevents mixing with HTTP responses)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr  # Critical: prevents logs from mixing with HTTP response
)
logger = logging.getLogger(__name__)

# Try to import nmap scanner (optional dependency)
try:
    from nmap_scanner import NmapModbusScanner
    NMAP_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Nmap scanner not available: {e}. Install 'nmap' and 'python-nmap' for advanced scanning.")
    NMAP_AVAILABLE = False

# Try to import S7 scanner (for LOGO! v7 detection)
try:
    from s7_scanner import S7Scanner
    from s7_client import S7Client, SNAP7_AVAILABLE
    S7_SCANNER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"S7 scanner not available: {e}")
    S7_SCANNER_AVAILABLE = False
    S7Scanner = None
    S7Client = None
    SNAP7_AVAILABLE = False

app = Flask(__name__)
CORS(app)

# Configure Flask/Werkzeug loggers to use stderr
werkzeug_logger = logging.getLogger('werkzeug')
for handler in werkzeug_logger.handlers[:]:
    werkzeug_logger.removeHandler(handler)
werkzeug_handler = logging.StreamHandler(sys.stderr)
werkzeug_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
werkzeug_logger.addHandler(werkzeug_handler)
werkzeug_logger.setLevel(logging.INFO)

# Configuration
CONFIG_PATH = os.environ.get('CONFIG_PATH', '/data/options.json')
# Use separate file for device storage (not managed by Supervisor)
DEVICES_PATH = os.environ.get('DEVICES_PATH', '/data/devices.json')
# Use different default paths depending on environment
if os.path.exists('/config'):
    # Running in Home Assistant addon
    DEFAULT_MODBUS_PATH = '/config/modbus.yaml'
else:
    # Running locally or in development - use absolute path in app directory
    DEFAULT_MODBUS_PATH = os.path.abspath('./modbus.yaml')

MODBUS_CONFIG_PATH = os.environ.get('MODBUS_CONFIG_PATH', DEFAULT_MODBUS_PATH)
logger.info(f"Modbus config will be saved to: {MODBUS_CONFIG_PATH}")
logger.info(f"Device storage path: {DEVICES_PATH}")

# Global state
devices = []
config_generator = ModbusConfigGenerator()


def load_config():
    """Load device configuration from persistent storage"""
    global devices

    # Initialize devices as empty list
    devices = []

    try:
        # First, try to load from persistent devices.json file
        if os.path.exists(DEVICES_PATH):
            with open(DEVICES_PATH, 'r') as f:
                loaded_devices = json.load(f)

                # Validate that devices is a list
                if not isinstance(loaded_devices, list):
                    logger.error(f"Devices file contains invalid data: {type(loaded_devices)}")
                    devices = []
                    return

                # Validate each device is a dict
                devices = []
                for i, device in enumerate(loaded_devices):
                    if isinstance(device, dict):
                        devices.append(device)
                    else:
                        logger.warning(f"Skipping invalid device at index {i}: {type(device)}")

                logger.info(f"Loaded {len(devices)} devices from {DEVICES_PATH}")

        # Migration: If devices.json doesn't exist, try to migrate from options.json
        elif os.path.exists(CONFIG_PATH):
            logger.info(f"Migrating devices from {CONFIG_PATH} to {DEVICES_PATH}")
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)

                # Ensure config is a dict
                if isinstance(config, dict):
                    loaded_devices = config.get('devices', [])

                    # Validate that devices is a list
                    if isinstance(loaded_devices, list):
                        # Validate each device is a dict
                        for device in loaded_devices:
                            if isinstance(device, dict):
                                devices.append(device)

                        # Save to new location
                        if devices:
                            save_config()
                            logger.info(f"Migrated {len(devices)} devices to {DEVICES_PATH}")

        else:
            logger.info(f"No existing device configuration found")
            devices = []

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error loading devices: {e}")
        devices = []
    except Exception as e:
        logger.error(f"Error loading devices: {e}", exc_info=True)
        devices = []


def save_config():
    """Save device configuration to persistent storage"""
    global devices

    # Ensure devices is always a list
    if not isinstance(devices, list):
        logger.error(f"Cannot save devices: devices is not a list! Type: {type(devices)}")
        devices = []

    # Validate all devices are JSON-serializable
    valid_devices = []
    for i, device in enumerate(devices):
        if isinstance(device, dict):
            try:
                json.dumps(device)  # Test if device is JSON-serializable
                valid_devices.append(device)
            except (TypeError, ValueError) as e:
                logger.warning(f"Skipping non-serializable device at index {i}: {e}")
        else:
            logger.warning(f"Skipping invalid device at index {i}: {type(device)}")

    devices = valid_devices

    try:
        # Ensure /data directory exists
        os.makedirs(os.path.dirname(DEVICES_PATH), exist_ok=True)

        # Save directly as list (not wrapped in {'devices': ...})
        with open(DEVICES_PATH, 'w') as f:
            json.dump(devices, f, indent=2)
        logger.info(f"Devices saved to {DEVICES_PATH} ({len(devices)} devices)")
    except Exception as e:
        logger.error(f"Error saving devices: {e}", exc_info=True)


@app.route('/')
def index():
    """Serve main page"""
    return send_from_directory('static', 'index.html')


@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('static', path)


@app.route('/api/status', methods=['GET'])
def api_status():
    """Get system status and capabilities"""
    return jsonify({
        'success': True,
        'nmap_available': NMAP_AVAILABLE,
        'version': '2.0.2'
    })


@app.route('/api/manufacturers', methods=['GET'])
def api_manufacturers():
    """Get list of manufacturers"""
    return jsonify(get_manufacturers())


@app.route('/api/models/<manufacturer>', methods=['GET'])
def api_models(manufacturer):
    """Get list of models for manufacturer"""
    return jsonify(get_models(manufacturer))


@app.route('/api/profile/<manufacturer>/<model>', methods=['GET'])
def api_profile(manufacturer, model):
    """Get device profile"""
    profile = get_device_profile(manufacturer, model)
    if profile:
        return jsonify(profile)
    return jsonify({'error': 'Profile not found'}), 404


@app.route('/api/devices', methods=['GET'])
def api_get_devices():
    """Get all configured devices"""
    try:
        # Ensure devices is a proper list
        if not isinstance(devices, list):
            logger.error(f"Devices is not a list: {type(devices)}")
            response = jsonify([])
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
            return response

        # Validate each device is a dict and is JSON-serializable
        valid_devices = []
        for i, device in enumerate(devices):
            if isinstance(device, dict):
                # Test if device is JSON-serializable
                try:
                    json.dumps(device)
                    valid_devices.append(device)
                except (TypeError, ValueError) as e:
                    logger.warning(f"Device at index {i} is not JSON-serializable: {e}")
            else:
                logger.warning(f"Device at index {i} is not a dict: {type(device)}")

        # Create response with explicit content type
        response = jsonify(valid_devices)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
    except Exception as e:
        logger.error(f"Error getting devices: {e}", exc_info=True)
        # Return empty array as fallback
        response = jsonify([])
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 200


@app.route('/api/devices', methods=['POST'])
def api_add_device():
    """Add a new device"""
    try:
        device = request.json

        # Validate required fields
        required = ['name', 'host']
        for field in required:
            if field not in device:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Set defaults for optional fields
        if 'manufacturer' not in device or not device['manufacturer']:
            device['manufacturer'] = 'Generic'
        if 'model' not in device or not device['model']:
            device['model'] = 'Modbus TCP'

        # Try to get profile, but allow custom devices without profile
        profile = get_device_profile(device['manufacturer'], device['model'])

        # Set default port based on profile or model type
        if 'port' not in device:
            if profile:
                device['port'] = profile.get('port', 502)
            elif 's7' in device['model'].lower():
                device['port'] = 102
            else:
                device['port'] = 502

        # Set default slave_id if not present
        if 'slave_id' not in device:
            device['slave_id'] = 1

        devices.append(device)
        save_config()

        logger.info(f"Added device: {device['name']}")
        return jsonify({'success': True, 'device': device})

    except Exception as e:
        logger.error(f"Error adding device: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/devices/<int:index>', methods=['PUT'])
def api_update_device(index):
    """Update a device"""
    try:
        if index < 0 or index >= len(devices):
            return jsonify({'error': 'Device not found'}), 404

        device = request.json
        devices[index] = device
        save_config()

        logger.info(f"Updated device: {device.get('name', index)}")
        return jsonify({'success': True, 'device': device})

    except Exception as e:
        logger.error(f"Error updating device: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/devices/<int:index>', methods=['DELETE'])
def api_delete_device(index):
    """Delete a device"""
    try:
        if index < 0 or index >= len(devices):
            return jsonify({'error': 'Device not found'}), 404

        device = devices.pop(index)
        save_config()

        logger.info(f"Deleted device: {device.get('name', index)}")
        return jsonify({'success': True})

    except Exception as e:
        logger.error(f"Error deleting device: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/scan', methods=['POST'])
def api_scan_device():
    """Scan a device for available registers"""
    try:
        data = request.json
        host = data.get('host')
        port = data.get('port', 502)
        manufacturer = data.get('manufacturer')
        model = data.get('model')
        slave_id = data.get('slave_id', 1)

        if not host:
            return jsonify({'error': 'Host is required'}), 400

        # Get device profile
        profile = None
        if manufacturer and model:
            profile = get_device_profile(manufacturer, model)

        # Scan device
        scanner = ModbusScanner(host, port)
        results = scanner.scan_device(profile, slave_id)

        # Count available registers
        total = sum(len(v) for v in results.values())

        logger.info(f"Scanned {host}:{port} - found {total} registers")
        return jsonify({
            'success': True,
            'results': results,
            'total': total
        })

    except Exception as e:
        logger.error(f"Error scanning device: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/network-info', methods=['GET'])
def api_get_network_info():
    """Get local network information (IP, DNS, Netmask, Gateway)"""
    try:
        detector = NetworkDetector()
        network_info = detector.get_network_info()

        # Set explicit content type
        response = jsonify(network_info)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response

    except Exception as e:
        logger.error(f"Error getting network info: {e}", exc_info=True)
        # Return fallback info
        response = jsonify({
            'ip': 'Unknown',
            'netmask': 'Unknown',
            'gateway': 'Unknown',
            'dns': 'Unknown',
            'network_range': None,
            'scan_range': None,
            'error': str(e)
        })
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 200


@app.route('/api/scan-network', methods=['POST'])
def api_scan_network():
    """Scan network for Modbus devices with automatic device detection"""
    try:
        data = request.json or {}
        network = data.get('network')  # Optional, e.g. "192.168.1.0/24"
        ports = data.get('ports', [502, 510])
        auto_detect = data.get('auto_detect', True)  # Auto-detect device type
        auto_add = data.get('auto_add', True)  # Automatically add to device list

        # Auto-detect network if not provided
        if not network:
            detector = NetworkDetector()
            network_info = detector.get_network_info()
            network = network_info.get('scan_range', '192.168.1.0/24')
            logger.info(f"Auto-detected network: {network}")

        # Start progress tracking
        scan_progress.start_scan(network, 'python')

        logger.info(f"Starting network scan on {network}...")

        # Progress callback for live updates
        def progress_callback(current_ip, scanned_count, found_device=None):
            scan_progress.update_progress(current_ip, scanned_count)
            if found_device:
                scan_progress.add_found_device(found_device)

        found_devices = NetworkScanner.scan_network(network, ports, timeout=1, auto_detect=auto_detect, progress_callback=progress_callback)

        # Automatically add detected devices if requested
        added_count = 0
        if auto_add:
            for device in found_devices:
                # Check if device is already in list to avoid duplicates
                host = device.get('ip')
                port = device.get('port', 502)
                if any(d.get('host') == host and d.get('port') == port for d in devices):
                    logger.info(f"Device {host}:{port} already in list, skipping")
                    continue

                # Add device even if manufacturer/model not detected
                new_device = {
                    'name': device.get('name', f"Device at {host}:{port}"),
                    'manufacturer': device.get('manufacturer', 'Generic'),
                    'model': device.get('model', 'Modbus TCP'),
                    'host': host,
                    'port': port,
                    'slave_id': device.get('slave_id', 1)
                }
                devices.append(new_device)
                added_count += 1
                logger.info(f"Auto-added device: {new_device['name']} at {host}:{port}")

            # Save configuration if devices were added
            if added_count > 0:
                save_config()

        # Mark scan as complete
        scan_progress.finish_scan()

        logger.info(f"Network scan complete: found {len(found_devices)} devices, added {added_count}")
        return jsonify({
            'success': True,
            'devices': found_devices,
            'total': len(found_devices),
            'added_count': added_count,
            'network': network
        })

    except Exception as e:
        scan_progress.set_error(str(e))
        logger.error(f"Error scanning network: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/scan-progress', methods=['GET'])
def api_scan_progress():
    """Get current scan progress"""
    return jsonify(scan_progress.get_status())


# ============================================================================
# Two-Phase Scan API Endpoints (New Workflow)
# ============================================================================

# Global storage for scan results between phases
_network_devices = []  # Phase 1 results (ping scan)
_bus_devices = []      # Phase 2 results (port scan)


@app.route('/api/scan/phase1-ping', methods=['POST'])
def api_scan_phase1_ping():
    """
    Phase 1: Quick ping scan to discover all network devices
    Returns devices with IP, MAC address, and vendor information
    """
    global _network_devices

    try:
        data = request.json or {}
        network = data.get('network')

        # Auto-detect network if not provided
        if not network:
            detector = NetworkDetector()
            network_info = detector.get_network_info()
            network = network_info.get('scan_range', '192.168.1.0/24')
            logger.info(f"Auto-detected network for ping scan: {network}")

        # Start progress tracking for phase 1
        scan_progress.start_scan(network, 'ping')
        scan_progress.set_phase('phase1_ping')

        logger.info(f"Starting Phase 1: Ping scan on {network}")

        # Progress callback
        def progress_callback(current_ip, scanned, total, found_device):
            scan_progress.update_progress(current_ip, scanned)
            scan_progress._total_hosts = total
            if found_device:
                scan_progress.add_found_device(found_device)

        # Perform ping scan
        scanner = PingScanner(timeout=0.5, max_workers=100)
        _network_devices = scanner.scan_network(network, progress_callback)

        scan_progress.set_phase('phase1_complete')
        scan_progress.finish_scan()

        logger.info(f"Phase 1 complete: {len(_network_devices)} devices found")

        return jsonify({
            'success': True,
            'phase': 'phase1_ping',
            'devices': _network_devices,
            'total': len(_network_devices),
            'network': network
        })

    except Exception as e:
        scan_progress.set_error(str(e))
        logger.error(f"Phase 1 ping scan error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/scan/phase2-ports', methods=['POST'])
def api_scan_phase2_ports():
    """
    Phase 2: Port scan on discovered devices for industrial protocols
    Scans ports: 102 (S7comm), 502, 510 (Modbus), 20000-20100 (custom Modbus)
    """
    global _bus_devices

    try:
        data = request.json or {}
        target_ips = data.get('ips', [])  # Optional: specific IPs to scan
        port_range = data.get('port_range', '102,502,510,20000-20100')

        # If no specific IPs provided, use Phase 1 results
        if not target_ips and _network_devices:
            target_ips = [d['ip'] for d in _network_devices]

        if not target_ips:
            return jsonify({
                'success': False,
                'error': 'Keine Geräte zum Scannen. Bitte zuerst Phase 1 (Ping-Scan) ausführen.'
            }), 400

        # Start progress tracking for phase 2
        scan_progress.start_scan(f"{len(target_ips)} hosts", 'ports')
        scan_progress.set_phase('phase2_ports')
        scan_progress._total_hosts = len(target_ips)

        logger.info(f"Starting Phase 2: Port scan on {len(target_ips)} hosts, ports: {port_range}")

        _bus_devices = []
        scanned_count = 0

        # Parse port range
        ports_to_scan = []
        for part in port_range.split(','):
            if '-' in part:
                start, end = part.split('-')
                ports_to_scan.extend(range(int(start), int(end) + 1))
            else:
                ports_to_scan.append(int(part))

        # Scan each host for open ports
        import socket
        for ip in target_ips:
            scanned_count += 1
            scan_progress.update_progress(ip, scanned_count)

            # Find corresponding network device for MAC info
            net_device = next((d for d in _network_devices if d['ip'] == ip), None)
            mac = net_device.get('mac', 'Unknown') if net_device else 'Unknown'
            vendor = net_device.get('vendor', 'Unknown') if net_device else 'Unknown'

            for port in ports_to_scan:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex((ip, port))
                    sock.close()

                    if result == 0:
                        # Determine protocol based on port
                        if port == 102:
                            protocol = 'S7comm'
                        elif port in [502, 510]:
                            protocol = 'Modbus TCP'
                        elif 20000 <= port <= 20100:
                            protocol = 'Modbus (Custom)'
                        else:
                            protocol = 'TCP'

                        bus_device = {
                            'ip': ip,
                            'port': port,
                            'protocol': protocol,
                            'mac': mac,
                            'vendor': vendor,
                            'status': 'open'
                        }
                        _bus_devices.append(bus_device)
                        scan_progress.add_found_device(bus_device)
                        logger.info(f"Found open port: {ip}:{port} ({protocol})")

                except Exception as e:
                    logger.debug(f"Error scanning {ip}:{port}: {e}")

        scan_progress.set_phase('phase2_complete')
        scan_progress.finish_scan()

        logger.info(f"Phase 2 complete: {len(_bus_devices)} bus devices found")

        return jsonify({
            'success': True,
            'phase': 'phase2_ports',
            'devices': _bus_devices,
            'total': len(_bus_devices)
        })

    except Exception as e:
        scan_progress.set_error(str(e))
        logger.error(f"Phase 2 port scan error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/scan/full', methods=['POST'])
def api_scan_full():
    """
    Full two-phase scan:
    1. Ping scan to find all devices
    2. Port scan to find industrial protocols
    """
    global _network_devices, _bus_devices

    try:
        data = request.json or {}
        network = data.get('network')
        port_range = data.get('port_range', '102,502,510,20000-20100')
        auto_add = data.get('auto_add', False)

        # Auto-detect network if not provided
        if not network:
            detector = NetworkDetector()
            network_info = detector.get_network_info()
            network = network_info.get('scan_range', '192.168.1.0/24')

        logger.info(f"Starting full two-phase scan on {network}")

        # Phase 1: Ping scan
        scan_progress.start_scan(network, 'ping')
        scan_progress.set_phase('phase1_ping')

        def ping_progress(current_ip, scanned, total, found_device):
            scan_progress.update_progress(current_ip, scanned)
            scan_progress._total_hosts = total
            if found_device:
                scan_progress.add_found_device(found_device)

        scanner = PingScanner(timeout=0.5, max_workers=100)
        _network_devices = scanner.scan_network(network, ping_progress)

        logger.info(f"Phase 1 complete: {len(_network_devices)} devices")

        # Phase 2: Port scan
        scan_progress.set_phase('phase2_ports')
        scan_progress._found_devices = []  # Reset for phase 2
        target_ips = [d['ip'] for d in _network_devices]

        _bus_devices = []
        scanned_count = 0

        # Parse port range
        ports_to_scan = []
        for part in port_range.split(','):
            if '-' in part:
                start, end = part.split('-')
                ports_to_scan.extend(range(int(start), int(end) + 1))
            else:
                ports_to_scan.append(int(part))

        scan_progress._total_hosts = len(target_ips)

        import socket
        for ip in target_ips:
            scanned_count += 1
            scan_progress.update_progress(ip, scanned_count)

            net_device = next((d for d in _network_devices if d['ip'] == ip), None)
            mac = net_device.get('mac', 'Unknown') if net_device else 'Unknown'
            vendor = net_device.get('vendor', 'Unknown') if net_device else 'Unknown'

            for port in ports_to_scan:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex((ip, port))
                    sock.close()

                    if result == 0:
                        if port == 102:
                            protocol = 'S7comm'
                        elif port in [502, 510]:
                            protocol = 'Modbus TCP'
                        elif 20000 <= port <= 20100:
                            protocol = 'Modbus (Custom)'
                        else:
                            protocol = 'TCP'

                        bus_device = {
                            'ip': ip,
                            'port': port,
                            'protocol': protocol,
                            'mac': mac,
                            'vendor': vendor,
                            'status': 'open'
                        }
                        _bus_devices.append(bus_device)
                        scan_progress.add_found_device(bus_device)

                except Exception:
                    pass

        # Auto-add to device list if requested
        added_count = 0
        if auto_add:
            for bus_dev in _bus_devices:
                host = bus_dev['ip']
                port = bus_dev['port']
                if not any(d.get('host') == host and d.get('port') == port for d in devices):
                    new_device = {
                        'name': f"{bus_dev['vendor']}_{host.split('.')[-1]}",
                        'manufacturer': bus_dev['vendor'],
                        'model': bus_dev['protocol'],
                        'host': host,
                        'port': port,
                        'mac': bus_dev['mac'],
                        'protocol': bus_dev['protocol'],
                        'slave_id': 1
                    }
                    devices.append(new_device)
                    added_count += 1

            if added_count > 0:
                save_config()

        scan_progress.set_phase('complete')
        scan_progress.finish_scan()

        logger.info(f"Full scan complete: {len(_network_devices)} network, {len(_bus_devices)} bus devices")

        return jsonify({
            'success': True,
            'network_devices': _network_devices,
            'bus_devices': _bus_devices,
            'network_total': len(_network_devices),
            'bus_total': len(_bus_devices),
            'added_count': added_count,
            'network': network
        })

    except Exception as e:
        scan_progress.set_error(str(e))
        logger.error(f"Full scan error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/scan/network-devices', methods=['GET'])
def api_get_network_devices():
    """Get current network devices from last ping scan"""
    return jsonify({
        'success': True,
        'devices': _network_devices,
        'total': len(_network_devices)
    })


@app.route('/api/scan/bus-devices', methods=['GET'])
def api_get_bus_devices():
    """Get current bus devices from last port scan"""
    return jsonify({
        'success': True,
        'devices': _bus_devices,
        'total': len(_bus_devices)
    })


@app.route('/api/scan-network-nmap', methods=['POST'])
def api_scan_network_nmap():
    """
    Advanced network scan using nmap with modbus-discover script
    Supports custom port ranges and efficient scanning
    """
    if not NMAP_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Nmap is not available. Please install nmap and python-nmap packages.',
            'fallback': 'Use the Quick Scan (Python) instead for basic functionality.'
        }), 503

    try:
        data = request.json or {}
        network = data.get('network')  # Optional, e.g. "192.168.1.0/24"
        port_range = data.get('port_range', '502,510,20000-20100')  # Configurable port range
        auto_add = data.get('auto_add', True)  # Automatically add to device list
        use_modbus_discover = data.get('use_modbus_discover', True)  # Use nmap NSE script
        timeout = data.get('timeout', 300)  # Scan timeout in seconds

        # Auto-detect network if not provided
        if not network:
            detector = NetworkDetector()
            network_info = detector.get_network_info()
            network = network_info.get('scan_range', '192.168.1.0/24')
            logger.info(f"Auto-detected network: {network}")

        # Start progress tracking
        scan_progress.start_scan(network, 'nmap')

        logger.info(f"Starting nmap network scan on {network}...")
        logger.info(f"Port range: {port_range}, timeout: {timeout}s")

        # Initialize nmap scanner
        nmap_scanner = NmapModbusScanner()

        # Perform nmap scan with progress callback
        def progress_callback(current_ip, scanned_count, found_device=None):
            scan_progress.update_progress(current_ip, scanned_count)
            if found_device:
                scan_progress.add_found_device(found_device)

        found_devices = nmap_scanner.scan_network_nmap(
            network=network,
            port_range=port_range,
            timeout=timeout,
            use_modbus_discover=use_modbus_discover,
            progress_callback=progress_callback
        )

        # Automatically add detected devices if requested
        added_count = 0
        if auto_add:
            for device in found_devices:
                # Check if device is already in list to avoid duplicates
                host = device.get('ip')
                port = device.get('port', 502)
                if any(d.get('host') == host and d.get('port') == port for d in devices):
                    logger.info(f"Device {host}:{port} already in list, skipping")
                    continue

                # Add device even if manufacturer/model not detected
                new_device = {
                    'name': device.get('name', f"Device at {host}:{port}"),
                    'manufacturer': device.get('manufacturer', 'Generic'),
                    'model': device.get('model', 'Modbus TCP'),
                    'host': host,
                    'port': port,
                    'slave_id': device.get('slave_id', 1)
                }
                devices.append(new_device)
                added_count += 1
                logger.info(f"Auto-added device: {new_device['name']} at {host}:{port}")

            # Save configuration if devices were added
            if added_count > 0:
                save_config()

        # Mark scan as complete
        scan_progress.finish_scan()

        logger.info(f"Nmap scan complete: found {len(found_devices)} devices, added {added_count}")
        return jsonify({
            'success': True,
            'devices': found_devices,
            'total': len(found_devices),
            'added_count': added_count,
            'scan_method': 'nmap',
            'network': network
        })

    except Exception as e:
        scan_progress.set_error(str(e))
        logger.error(f"Error during nmap scan: {e}", exc_info=True)
        return jsonify({'error': str(e), 'scan_method': 'nmap'}), 500


@app.route('/api/scan-s7', methods=['POST'])
def api_scan_s7():
    """
    Scan single IP for S7 protocol (LOGO! v7, S7-300, S7-400)
    Uses S7comm protocol detection on port 102
    """
    if not S7_SCANNER_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'S7 scanner not available. Missing s7_scanner module.',
            'info': 'S7 scanner is used for LOGO! v7/0BA7 detection on port 102'
        }), 503

    try:
        data = request.json
        host = data.get('host')
        port = data.get('port', 102)
        src_tsap = data.get('src_tsap')  # Optional, e.g., 0x0100
        dst_tsap = data.get('dst_tsap')  # Optional, e.g., 0x2000
        timeout = data.get('timeout', 5)
        auto_add = data.get('auto_add', True)  # Automatically add to device list (default: True)

        if not host:
            return jsonify({'error': 'Host is required'}), 400

        logger.info(f"Scanning {host}:{port} for S7 protocol...")

        scanner = S7Scanner(host, port=port, timeout=timeout)
        result = scanner.detect_s7_device(src_tsap=src_tsap, dst_tsap=dst_tsap)

        if result['success']:
            logger.info(f"S7 device detected: {host} - {result['device_type']}")

            # Automatically add device if requested
            if auto_add:
                new_device = {
                    'name': f"{result['device_type']} at {host}",
                    'manufacturer': 'Siemens',
                    'model': result['device_type'],
                    'host': host,
                    'port': port,
                    'protocol': 's7',  # Mark as S7 protocol
                    'tsap_src': result['tsap_src'],
                    'tsap_dst': result['tsap_dst'],
                    'pdu_size': result['pdu_size']
                }

                # Only add if not already in list
                if not any(d.get('host') == host and d.get('port') == port for d in devices):
                    devices.append(new_device)
                    save_config()
                    logger.info(f"Auto-added S7 device: {new_device['name']}")
                    result['added'] = True
                else:
                    logger.info(f"S7 device already in list: {host}:{port}")
                    result['added'] = False
            else:
                result['added'] = False
        else:
            logger.info(f"No S7 device found at {host}:{port} - {result.get('error', 'Unknown error')}")

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error during S7 scan: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/scan-network-s7', methods=['POST'])
def api_scan_network_s7():
    """
    Scan network for S7 devices (LOGO! v7, S7-300, S7-400)
    Scans port 102 for S7comm protocol
    """
    if not S7_SCANNER_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'S7 scanner not available. Missing s7_scanner module.',
            'info': 'S7 scanner is used for LOGO! v7/0BA7 detection on port 102'
        }), 503

    try:
        data = request.json or {}
        network = data.get('network')  # Optional, e.g. "192.168.1.0/24"
        timeout = data.get('timeout', 2)  # Timeout per host
        auto_add = data.get('auto_add', True)  # Automatically add to device list (default: True)

        # Auto-detect network if not provided
        if not network:
            detector = NetworkDetector()
            network_info = detector.get_network_info()
            network = network_info.get('scan_range', '192.168.1.0/24')
            logger.info(f"Auto-detected network: {network}")

        logger.info(f"Starting S7 network scan on {network} (timeout: {timeout}s per host)...")

        # Perform S7 network scan
        found_devices = S7Scanner.scan_network_for_s7(network, timeout=timeout)

        # Automatically add detected devices if requested
        added_count = 0
        if auto_add:
            for device in found_devices:
                # Add S7 device to list (will need S7 client, not Modbus)
                new_device = {
                    'name': f"{device['device_type']} at {device['host']}",
                    'manufacturer': 'Siemens',
                    'model': device['device_type'],
                    'host': device['host'],
                    'port': device['port'],
                    'protocol': 's7',  # Mark as S7 protocol
                    'tsap_src': device['tsap_src'],
                    'tsap_dst': device['tsap_dst'],
                    'pdu_size': device['pdu_size']
                }

                # Only add if not already in list
                if not any(d.get('host') == new_device['host'] and d.get('port') == new_device['port'] for d in devices):
                    devices.append(new_device)
                    added_count += 1
                    logger.info(f"Auto-added S7 device: {new_device['name']}")

            # Save configuration if devices were added
            if added_count > 0:
                save_config()

        logger.info(f"S7 scan complete. Found {len(found_devices)} device(s), added {added_count}.")

        return jsonify({
            'success': True,
            'devices': found_devices,
            'total': len(found_devices),
            'added_count': added_count,
            'scan_method': 's7comm',
            'network': network
        })

    except Exception as e:
        logger.error(f"Error during S7 network scan: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'scan_method': 's7comm'
        }), 500


@app.route('/api/detect-modbus-ports', methods=['POST'])
def api_detect_modbus_ports():
    """
    Detect all Modbus ports on a specific IP address
    Useful for finding non-standard Modbus ports
    """
    if not NMAP_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Nmap is not available. Please install nmap and python-nmap packages.'
        }), 503

    try:
        data = request.json
        ip = data.get('ip')

        if not ip:
            return jsonify({'error': 'IP address is required'}), 400

        logger.info(f"Detecting Modbus ports on {ip}...")

        # Initialize nmap scanner
        nmap_scanner = NmapModbusScanner()

        # Detect Modbus ports
        modbus_ports = nmap_scanner.detect_modbus_ports(ip)

        logger.info(f"Found {len(modbus_ports)} Modbus port(s) on {ip}: {modbus_ports}")
        return jsonify({
            'success': True,
            'ip': ip,
            'modbus_ports': modbus_ports,
            'total': len(modbus_ports)
        })

    except Exception as e:
        logger.error(f"Error detecting Modbus ports: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/scan-logo8', methods=['POST'])
def api_scan_logo8():
    """Detailed scan for Siemens LOGO! 8 devices"""
    try:
        data = request.json
        host = data.get('host')
        port = data.get('port', 502)
        slave_id = data.get('slave_id', 1)

        if not host:
            return jsonify({'error': 'Host is required'}), 400

        logger.info(f"Starting LOGO! 8 detailed scan on {host}:{port}...")
        scanner = ModbusScanner(host, port)
        results = scanner.scan_logo8_addresses(slave_id)

        # Count total found addresses
        total = sum(len(v) for v in results.values())

        logger.info(f"LOGO! 8 scan complete: {host}:{port} - found {total} addresses")
        return jsonify({
            'success': True,
            'results': results,
            'total': total
        })

    except Exception as e:
        logger.error(f"Error scanning LOGO! 8 device: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/scan-logo0ba7', methods=['POST'])
def api_scan_logo0ba7():
    """Detailed scan for Siemens LOGO! 0BA7 devices"""
    try:
        data = request.json
        host = data.get('host')
        port = data.get('port', 502)
        slave_id = data.get('slave_id', 1)

        if not host:
            return jsonify({'error': 'Host is required'}), 400

        logger.info(f"Starting LOGO! 0BA7 detailed scan on {host}:{port}...")
        scanner = ModbusScanner(host, port)
        results = scanner.scan_logo0ba7_addresses(slave_id)

        # Count total found addresses
        total = sum(len(v) for v in results.values())

        logger.info(f"LOGO! 0BA7 scan complete: {host}:{port} - found {total} addresses")
        return jsonify({
            'success': True,
            'results': results,
            'total': total
        })

    except Exception as e:
        logger.error(f"Error scanning LOGO! 0BA7 device: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/scan-addresses', methods=['POST'])
def api_scan_addresses():
    """Scan specific addresses"""
    try:
        data = request.json
        host = data.get('host')
        port = data.get('port', 502)
        slave_id = data.get('slave_id', 1)
        address_list = data.get('addresses', [])

        if not host:
            return jsonify({'error': 'Host is required'}), 400

        if not address_list:
            return jsonify({'error': 'Address list is required'}), 400

        logger.info(f"Scanning specific addresses on {host}:{port}...")
        scanner = ModbusScanner(host, port)
        results = scanner.scan_detailed_addresses(address_list, slave_id)

        logger.info(f"Address scan complete: {host}:{port} - found {len(results)} values")
        return jsonify({
            'success': True,
            'results': results,
            'total': len(results)
        })

    except Exception as e:
        logger.error(f"Error scanning addresses: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/test-connection', methods=['POST'])
def api_test_connection():
    """Test connection to a device"""
    try:
        data = request.json
        host = data.get('host')
        port = data.get('port', 502)

        if not host:
            return jsonify({'error': 'Host is required'}), 400

        scanner = ModbusScanner(host, port)
        success = scanner.test_connection()

        if success:
            logger.info(f"Connection test successful: {host}:{port}")
            return jsonify({'success': True, 'message': 'Connection successful'})
        else:
            logger.warning(f"Connection test failed: {host}:{port}")
            return jsonify({'success': False, 'message': 'Connection failed'}), 400

    except Exception as e:
        logger.error(f"Error testing connection: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/discover-registers', methods=['POST'])
def api_discover_registers():
    """
    Discover and analyze registers on a Modbus device
    Returns device type and all readable registers in frontend-expected format
    """
    try:
        data = request.json or {}
        host = data.get('host')
        port = data.get('port', 502)
        slave_id = data.get('slave_id', 1)

        if not host:
            return jsonify({'success': False, 'error': 'Host is required'}), 400

        logger.info(f"Starting register discovery on {host}:{port} (slave {slave_id})")

        scanner = ModbusScanner(host, port)

        if not scanner.connect():
            return jsonify({
                'success': False,
                'error': f'Verbindung zu {host}:{port} fehlgeschlagen'
            }), 400

        try:
            # Detect device type
            device_type = scanner.detect_device_type(slave_id)
            detected_device = {
                'LOGO_8': 'Siemens LOGO! 8',
                'LOGO_0BA7': 'Siemens LOGO! 0BA7',
                'GENERIC': 'Generic Modbus TCP'
            }.get(device_type, 'Generic Modbus TCP')

            # Test supported functions
            supported_functions = []
            register_ranges = {
                'discrete_inputs': [],
                'coils': [],
                'input_registers': [],
                'holding_registers': []
            }
            recommendations = []

            # Define test ranges based on device type
            if device_type == 'LOGO_8':
                test_ranges = {
                    'discrete_inputs': [(8192, 64, 'DI 1-64 (LOGO! 8)')],
                    'coils': [(8256, 64, 'DO 1-64 (LOGO! 8)')],
                    'input_registers': [(0, 50, 'AI 1-8 + AM (LOGO! 8)'), (528, 32, 'NAI/NAO (LOGO! 8)')],
                    'holding_registers': [(0, 50, 'AQ + VM (LOGO! 8)'), (528, 32, 'NAQ (LOGO! 8)')]
                }
                recommendations.append('LOGO! 8 erkannt - Verwenden Sie Port 510 für Modbus TCP')
                recommendations.append('Digital I/O: Register ab 8192 (DI) und 8256 (DO)')
            elif device_type == 'LOGO_0BA7':
                test_ranges = {
                    'discrete_inputs': [(0, 24, 'I1-I24 (LOGO! 0BA7)')],
                    'coils': [(0, 16, 'Q1-Q16 (LOGO! 0BA7)'), (16, 8, 'M1-M8 (LOGO! 0BA7)')],
                    'input_registers': [(0, 8, 'AI1-AI8 (LOGO! 0BA7)')],
                    'holding_registers': [(0, 8, 'AQ1-AQ2 + AM (LOGO! 0BA7)')]
                }
                recommendations.append('LOGO! 0BA7 erkannt - Nur über S7comm unterstützt')
            else:
                test_ranges = {
                    'discrete_inputs': [(0, 100, 'Standard DI 0-99'), (1000, 100, 'Extended DI 1000-1099')],
                    'coils': [(0, 100, 'Standard Coils 0-99'), (1000, 100, 'Extended Coils 1000-1099')],
                    'input_registers': [(0, 100, 'Standard IR 0-99'), (1000, 100, 'Extended IR 1000-1099')],
                    'holding_registers': [(0, 100, 'Standard HR 0-99'), (1000, 100, 'Extended HR 1000-1099')]
                }
                recommendations.append('Standard Modbus-Gerät - Prüfen Sie die Dokumentation für Register-Adressen')

            # Test Discrete Inputs (Function Code 2)
            for start, count, note in test_ranges['discrete_inputs']:
                try:
                    result = scanner.scan_discrete_inputs(start, min(count, 100), slave_id)
                    supported = result is not None and len(result) > 0
                    if supported and 'Read Discrete Inputs (FC2)' not in supported_functions:
                        supported_functions.append('Read Discrete Inputs (FC2)')
                    register_ranges['discrete_inputs'].append({
                        'range': f'{start}-{start+count-1}',
                        'start': start,
                        'count': count,
                        'supported': supported,
                        'note': note if supported else 'Nicht lesbar',
                        'error': None
                    })
                except Exception as e:
                    register_ranges['discrete_inputs'].append({
                        'range': f'{start}-{start+count-1}',
                        'start': start,
                        'count': count,
                        'supported': False,
                        'note': note,
                        'error': str(e)
                    })

            # Test Coils (Function Code 1)
            for start, count, note in test_ranges['coils']:
                try:
                    result = scanner.scan_coils(start, min(count, 100), slave_id)
                    supported = result is not None and len(result) > 0
                    if supported and 'Read Coils (FC1)' not in supported_functions:
                        supported_functions.append('Read Coils (FC1)')
                    register_ranges['coils'].append({
                        'range': f'{start}-{start+count-1}',
                        'start': start,
                        'count': count,
                        'supported': supported,
                        'note': note if supported else 'Nicht lesbar',
                        'error': None
                    })
                except Exception as e:
                    register_ranges['coils'].append({
                        'range': f'{start}-{start+count-1}',
                        'start': start,
                        'count': count,
                        'supported': False,
                        'note': note,
                        'error': str(e)
                    })

            # Test Input Registers (Function Code 4)
            for start, count, note in test_ranges['input_registers']:
                try:
                    result = scanner.scan_input_registers(start, min(count, 100), slave_id)
                    supported = result is not None and len(result) > 0
                    if supported and 'Read Input Registers (FC4)' not in supported_functions:
                        supported_functions.append('Read Input Registers (FC4)')
                    register_ranges['input_registers'].append({
                        'range': f'{start}-{start+count-1}',
                        'start': start,
                        'count': count,
                        'supported': supported,
                        'note': note if supported else 'Nicht lesbar',
                        'error': None
                    })
                except Exception as e:
                    register_ranges['input_registers'].append({
                        'range': f'{start}-{start+count-1}',
                        'start': start,
                        'count': count,
                        'supported': False,
                        'note': note,
                        'error': str(e)
                    })

            # Test Holding Registers (Function Code 3)
            for start, count, note in test_ranges['holding_registers']:
                try:
                    result = scanner.scan_holding_registers(start, min(count, 100), slave_id)
                    supported = result is not None and len(result) > 0
                    if supported and 'Read Holding Registers (FC3)' not in supported_functions:
                        supported_functions.append('Read Holding Registers (FC3)')
                    register_ranges['holding_registers'].append({
                        'range': f'{start}-{start+count-1}',
                        'start': start,
                        'count': count,
                        'supported': supported,
                        'note': note if supported else 'Nicht lesbar',
                        'error': None
                    })
                except Exception as e:
                    register_ranges['holding_registers'].append({
                        'range': f'{start}-{start+count-1}',
                        'start': start,
                        'count': count,
                        'supported': False,
                        'note': note,
                        'error': str(e)
                    })

            logger.info(f"Register discovery complete: {detected_device}, functions: {supported_functions}")

            return jsonify({
                'success': True,
                'host': host,
                'port': port,
                'slave_id': slave_id,
                'detected_device': detected_device,
                'supported_functions': supported_functions,
                'register_ranges': register_ranges,
                'recommendations': recommendations
            })

        finally:
            scanner.disconnect()

    except Exception as e:
        logger.error(f"Error during register discovery: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/generate', methods=['POST'])
def api_generate_config():
    """Generate Modbus configuration"""
    try:
        data = request.json or {}
        output_path = data.get('output_path', MODBUS_CONFIG_PATH)
        include_scan = data.get('include_scan', False)

        # Check if there are any devices
        if not devices:
            logger.warning("No devices configured")
            return jsonify({
                'success': False,
                'error': 'Keine Geräte konfiguriert. Bitte fügen Sie zuerst ein Gerät hinzu.'
            }), 400

        # Clear previous configuration
        config_generator.clear()

        # Add all devices
        added_count = 0
        for device in devices:
            scan_results = None

            # Optionally scan device
            if include_scan:
                try:
                    manufacturer = device.get('manufacturer')
                    model = device.get('model')
                    profile = get_device_profile(manufacturer, model)

                    scanner = ModbusScanner(
                        device['host'],
                        device.get('port', 502)
                    )
                    scan_results = scanner.scan_device(
                        profile,
                        device.get('slave_id', 1)
                    )
                except Exception as e:
                    logger.warning(f"Scan failed for {device['name']}: {e}")

            if config_generator.add_device(device, scan_results):
                added_count += 1

        if added_count == 0:
            return jsonify({
                'success': False,
                'error': 'Keine Geräte konnten zur Konfiguration hinzugefügt werden.'
            }), 400

        # Generate YAML
        yaml_config = config_generator.generate_yaml(output_path)

        # Get absolute path for display
        abs_path = os.path.abspath(output_path)

        # Verify file was created
        file_exists = os.path.exists(abs_path)
        file_size = os.path.getsize(abs_path) if file_exists else 0

        logger.info(f"Generated configuration with {added_count} devices at {abs_path}")
        logger.info(f"File exists: {file_exists}, Size: {file_size} bytes")

        if not file_exists:
            return jsonify({
                'success': False,
                'error': f'Konfiguration konnte nicht gespeichert werden nach {abs_path}. Bitte Berechtigungen prüfen.'
            }), 500

        return jsonify({
            'success': True,
            'config': yaml_config,
            'path': abs_path,
            'absolute_path': abs_path,
            'devices_count': added_count,
            'file_size': file_size,
            'message': f'Konfiguration erfolgreich gespeichert: {abs_path} ({file_size} Bytes)'
        })

    except Exception as e:
        logger.error(f"Error generating config: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Fehler beim Generieren der Konfiguration: {str(e)}'
        }), 500


@app.route('/api/config', methods=['GET'])
def api_get_config():
    """Get current configuration"""
    try:
        if os.path.exists(MODBUS_CONFIG_PATH):
            with open(MODBUS_CONFIG_PATH, 'r') as f:
                config = f.read()
            return jsonify({'success': True, 'config': config})
        else:
            return jsonify({'success': False, 'message': 'No configuration found'})
    except Exception as e:
        logger.error(f"Error reading config: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/check-devices-in-config', methods=['GET'])
def api_check_devices_in_config():
    """Check which devices are present in the generated configuration"""
    try:
        if not os.path.exists(MODBUS_CONFIG_PATH):
            return jsonify({
                'success': True,
                'devices_in_config': {},
                'config_exists': False
            })

        # Read the generated YAML config
        with open(MODBUS_CONFIG_PATH, 'r') as f:
            config_content = f.read()

        # Parse YAML to get device names
        config_data = yaml.safe_load(config_content)

        if not config_data:
            return jsonify({
                'success': True,
                'devices_in_config': {},
                'config_exists': True
            })

        # Extract device names from config
        config_device_names = set()
        if isinstance(config_data, list):
            for device in config_data:
                if isinstance(device, dict) and 'name' in device:
                    config_device_names.add(device['name'])

        # Check each device
        devices_status = {}
        for i, device in enumerate(devices):
            device_name = device.get('name', f"{device.get('manufacturer', '')}_{device.get('model', '')}")
            devices_status[i] = {
                'name': device_name,
                'in_config': device_name in config_device_names
            }

        return jsonify({
            'success': True,
            'devices_in_config': devices_status,
            'config_exists': True,
            'total_in_config': sum(1 for d in devices_status.values() if d['in_config'])
        })

    except Exception as e:
        logger.error(f"Error checking devices in config: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# Auto-Scanner API Endpoints
# ============================================================================

@app.route('/api/auto-scanner/status', methods=['GET'])
def api_auto_scanner_status():
    """Get auto-scanner status"""
    status = auto_scanner.get_status()
    status['nmap_available'] = NMAP_AVAILABLE
    return jsonify({'success': True, **status})


@app.route('/api/auto-scanner/configure', methods=['POST'])
def api_auto_scanner_configure():
    """Configure auto-scanner settings"""
    try:
        data = request.json or {}
        auto_scanner.configure(data)
        return jsonify({
            'success': True,
            'message': 'Auto-scanner configured',
            'config': auto_scanner.get_status()
        })
    except Exception as e:
        logger.error(f"Error configuring auto-scanner: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


def detect_device_type_for_host(host, port, slave_id=1):
    """Detect device type for a specific host using ModbusScanner"""
    try:
        scanner = ModbusScanner(host, port, timeout=3)
        if scanner.connect():
            device_type = scanner.detect_device_type(slave_id)
            scanner.disconnect()

            # Map device type to manufacturer/model
            type_map = {
                'LOGO_8': ('Siemens', 'LOGO! 8'),
                'LOGO_0BA7': ('Siemens', 'LOGO! 0BA7'),
                'S7': ('Siemens', 'S7 PLC'),
            }

            if device_type in type_map:
                return {
                    'device_type': device_type,
                    'manufacturer': type_map[device_type][0],
                    'model': type_map[device_type][1]
                }
    except Exception as e:
        logger.debug(f"Device detection failed for {host}:{port}: {e}")

    return {
        'device_type': 'GENERIC',
        'manufacturer': 'Generic',
        'model': 'Modbus TCP'
    }


def perform_network_scan(network=None, port_range='502,510', use_nmap=False, auto_add=True):
    """
    Unified scan function for auto-scanner with device detection.
    Used by both auto-scanner start and manual trigger endpoints.
    """
    found_devices = []

    # Auto-detect network if not provided
    if not network:
        detector = NetworkDetector()
        network_info = detector.get_network_info()
        network = network_info.get('scan_range', '192.168.1.0/24')

    logger.info(f"Network scan starting on {network} with ports {port_range}")

    # Start progress tracking
    scan_progress.start_scan(network, 'nmap' if use_nmap else 'python')

    if use_nmap and NMAP_AVAILABLE:
        nmap_scanner = NmapModbusScanner()

        def progress_callback(current_ip, scanned_count, found_device=None):
            scan_progress.update_progress(current_ip, scanned_count)
            if found_device:
                scan_progress.add_found_device(found_device)

        found_devices = nmap_scanner.scan_network_nmap(
            network=network,
            port_range=port_range,
            timeout=300,
            progress_callback=progress_callback
        )
    else:
        ports = [int(p) for p in port_range.split(',') if p.isdigit()][:5]
        found_devices = NetworkScanner.scan_network(network, ports, timeout=1)

    # Detect device types for all found devices
    for device in found_devices:
        host = device.get('ip')
        port = device.get('port', 502)
        slave_id = device.get('slave_id', 1)

        # Try to detect device type
        detection = detect_device_type_for_host(host, port, slave_id)
        device['device_type'] = detection['device_type']
        device['manufacturer'] = detection['manufacturer']
        device['model'] = detection['model']

        # Update name based on detected type
        if detection['device_type'] != 'GENERIC':
            device['name'] = f"{detection['model']} at {host}"

        logger.info(f"Detected: {host}:{port} -> {detection['model']}")

    # Auto-add devices if enabled
    added_count = 0
    if auto_add:
        for device in found_devices:
            host = device.get('ip')
            port = device.get('port', 502)
            if not any(d.get('host') == host and d.get('port') == port for d in devices):
                new_device = {
                    'name': device.get('name', f"Device at {host}:{port}"),
                    'manufacturer': device.get('manufacturer', 'Generic'),
                    'model': device.get('model', 'Modbus TCP'),
                    'host': host,
                    'port': port,
                    'slave_id': device.get('slave_id', 1)
                }
                devices.append(new_device)
                added_count += 1
                logger.info(f"Auto-added: {new_device['name']}")

        if added_count > 0:
            save_config()

    # Finish progress tracking
    scan_progress.finish_scan()

    logger.info(f"Network scan complete: {len(found_devices)} found, {added_count} added")
    return {'success': True, 'devices': found_devices, 'added_count': added_count}


@app.route('/api/auto-scanner/start', methods=['POST'])
def api_auto_scanner_start():
    """Start automatic scanning"""
    try:
        success = auto_scanner.start(perform_network_scan, NMAP_AVAILABLE)
        return jsonify({
            'success': success,
            'message': 'Auto-scanner started' if success else 'Auto-scanner already running'
        })
    except Exception as e:
        logger.error(f"Error starting auto-scanner: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/auto-scanner/stop', methods=['POST'])
def api_auto_scanner_stop():
    """Stop automatic scanning"""
    success = auto_scanner.stop()
    return jsonify({
        'success': success,
        'message': 'Auto-scanner stopped' if success else 'Auto-scanner not running'
    })


@app.route('/api/auto-scanner/trigger', methods=['POST'])
def api_auto_scanner_trigger():
    """Trigger a manual scan"""
    try:
        result = auto_scanner.trigger_manual_scan(perform_network_scan, NMAP_AVAILABLE)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error triggering manual scan: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# Manufacturer Database API Endpoints
# ============================================================================

@app.route('/api/manufacturer-database', methods=['GET'])
def api_get_manufacturer_database():
    """Get full manufacturer database"""
    return jsonify({
        'success': True,
        'manufacturers': MANUFACTURER_PORTS,
        'protocols': PROTOCOL_PORTS,
        'scan_ranges': SCAN_PORT_RANGES
    })


@app.route('/api/manufacturer-database/manufacturers', methods=['GET'])
def api_get_all_manufacturers():
    """Get list of all manufacturers"""
    return jsonify({
        'success': True,
        'manufacturers': get_all_manufacturers()
    })


@app.route('/api/manufacturer-database/manufacturer/<name>', methods=['GET'])
def api_get_manufacturer(name):
    """Get manufacturer information"""
    info = get_manufacturer_info(name)
    if info:
        return jsonify({'success': True, 'manufacturer': info})
    return jsonify({'success': False, 'error': 'Manufacturer not found'}), 404


@app.route('/api/manufacturer-database/detect-by-port/<int:port>', methods=['GET'])
def api_detect_by_port(port):
    """Detect possible manufacturers by port"""
    matches = detect_manufacturer_by_port(port)
    return jsonify({
        'success': True,
        'port': port,
        'possible_manufacturers': matches
    })


@app.route('/api/manufacturer-database/recommended-ports', methods=['GET'])
def api_get_recommended_ports():
    """Get recommended ports for scanning"""
    return jsonify({
        'success': True,
        'ports': get_recommended_ports_for_scan(),
        'scan_ranges': SCAN_PORT_RANGES
    })


# ============================================================================
# Auto Config Generation API Endpoints
# ============================================================================

@app.route('/api/auto-generate-all', methods=['POST'])
def api_auto_generate_all():
    """
    Automatically scan all devices and generate configurations
    This combines: scan -> register analysis -> config generation
    """
    try:
        data = request.json or {}
        generate_modbus = data.get('generate_modbus', True)
        generate_s7 = data.get('generate_s7', True)

        results = {
            'scanned_devices': [],
            'register_analysis': [],
            'generated_configs': [],
            'errors': []
        }

        # Process each configured device
        for device in devices:
            device_result = {
                'name': device.get('name'),
                'host': device.get('host'),
                'port': device.get('port', 502)
            }

            try:
                # Test connection and analyze registers
                scanner = ModbusScanner(device['host'], device.get('port', 502))
                if scanner.connect():
                    try:
                        device_type = scanner.detect_device_type(device.get('slave_id', 1))
                        device_result['device_type'] = device_type
                        device_result['connection'] = 'success'
                        results['scanned_devices'].append(device_result)
                    finally:
                        scanner.disconnect()
                else:
                    device_result['connection'] = 'failed'
                    results['errors'].append(f"Could not connect to {device['host']}")

            except Exception as e:
                device_result['error'] = str(e)
                results['errors'].append(f"Error scanning {device['host']}: {e}")

        # Generate Modbus config if devices exist and option enabled
        if generate_modbus and devices:
            try:
                config_generator.clear()
                for device in devices:
                    config_generator.add_device(device)
                yaml_config = config_generator.generate_yaml()
                with open(MODBUS_CONFIG_PATH, 'w') as f:
                    f.write(yaml_config)
                results['generated_configs'].append({
                    'type': 'modbus',
                    'path': MODBUS_CONFIG_PATH,
                    'success': True
                })
            except Exception as e:
                results['errors'].append(f"Error generating Modbus config: {e}")

        # Generate S7 config for S7-compatible devices
        if generate_s7 and S7_SCANNER_AVAILABLE:
            s7_devices = [d for d in results['scanned_devices']
                        if d.get('device_type') in ['LOGO_8', 'LOGO_0BA7', 'S7']]
            if s7_devices:
                results['generated_configs'].append({
                    'type': 's7comm',
                    'devices': len(s7_devices),
                    'note': 'S7 devices found - use S7 integration for these'
                })

        return jsonify({
            'success': True,
            'results': results
        })

    except Exception as e:
        logger.error(f"Error in auto-generate-all: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    logger.info("Starting busbot - Universal Modbus Configurator")
    logger.info(f"Config path: {CONFIG_PATH}")
    logger.info(f"Modbus config path: {MODBUS_CONFIG_PATH}")

    # Load existing configuration
    load_config()

    # Start web server
    app.run(host='0.0.0.0', port=8099, debug=False)

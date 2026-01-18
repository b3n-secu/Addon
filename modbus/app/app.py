"""
Universal Modbus Configurator - Main Application
"""
import os
import json
import logging
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from device_profiles import get_manufacturers, get_models, get_device_profile
from modbus_scanner import ModbusScanner, NetworkScanner
from config_generator import ModbusConfigGenerator

# Try to import nmap scanner (optional dependency)
try:
    from nmap_scanner import NmapModbusScanner
    NMAP_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Nmap scanner not available: {e}. Install 'nmap' and 'python-nmap' for advanced scanning.")
    NMAP_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
CONFIG_PATH = os.environ.get('CONFIG_PATH', '/data/options.json')
# Use different default paths depending on environment
if os.path.exists('/config'):
    # Running in Home Assistant addon
    DEFAULT_MODBUS_PATH = '/config/modbus_generated.yaml'
else:
    # Running locally or in development - use absolute path in app directory
    DEFAULT_MODBUS_PATH = os.path.abspath('./modbus_generated.yaml')

MODBUS_CONFIG_PATH = os.environ.get('MODBUS_CONFIG_PATH', DEFAULT_MODBUS_PATH)
logger.info(f"Modbus config will be saved to: {MODBUS_CONFIG_PATH}")

# Global state
devices = []
config_generator = ModbusConfigGenerator()


def load_config():
    """Load configuration from Home Assistant"""
    global devices
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
                devices = config.get('devices', [])
                logger.info(f"Loaded {len(devices)} devices from config")
    except Exception as e:
        logger.error(f"Error loading config: {e}")


def save_config():
    """Save configuration to Home Assistant"""
    try:
        config = {'devices': devices}
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info("Configuration saved")
    except Exception as e:
        logger.error(f"Error saving config: {e}")


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
        'version': '1.0.0'
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
    return jsonify(devices)


@app.route('/api/devices', methods=['POST'])
def api_add_device():
    """Add a new device"""
    try:
        device = request.json

        # Validate required fields
        required = ['manufacturer', 'model', 'name', 'host']
        for field in required:
            if field not in device:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Get profile and set default port
        profile = get_device_profile(device['manufacturer'], device['model'])
        if not profile:
            return jsonify({'error': 'Invalid manufacturer or model'}), 400

        if 'port' not in device:
            device['port'] = profile.get('port', 502)

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


@app.route('/api/scan-network', methods=['POST'])
def api_scan_network():
    """Scan network for Modbus devices with automatic device detection"""
    try:
        data = request.json or {}
        network = data.get('network')  # Optional, e.g. "192.168.1.0/24"
        ports = data.get('ports', [502, 510])
        auto_detect = data.get('auto_detect', True)  # Auto-detect device type
        auto_add = data.get('auto_add', False)  # Automatically add to device list

        logger.info(f"Starting network scan on {network or 'auto-detected network'}...")
        found_devices = NetworkScanner.scan_network(network, ports, timeout=1, auto_detect=auto_detect)

        # Automatically add detected devices if requested
        added_count = 0
        if auto_add:
            for device in found_devices:
                if 'manufacturer' in device and 'model' in device:
                    new_device = {
                        'name': device['name'],
                        'manufacturer': device['manufacturer'],
                        'model': device['model'],
                        'host': device['ip'],
                        'port': device['port'],
                        'slave_id': 1
                    }
                    devices.append(new_device)
                    added_count += 1
                    logger.info(f"Auto-added device: {device['name']} at {device['ip']}:{device['port']}")

        logger.info(f"Network scan complete: found {len(found_devices)} devices, added {added_count}")
        return jsonify({
            'success': True,
            'devices': found_devices,
            'total': len(found_devices),
            'added_count': added_count
        })

    except Exception as e:
        logger.error(f"Error scanning network: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


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
        port_range = data.get('port_range', '102,502,510,20000-20100')  # Configurable port range
        auto_add = data.get('auto_add', False)  # Automatically add to device list
        use_modbus_discover = data.get('use_modbus_discover', True)  # Use nmap NSE script
        timeout = data.get('timeout', 300)  # Scan timeout in seconds

        logger.info(f"Starting nmap network scan on {network or 'auto-detected network'}...")
        logger.info(f"Port range: {port_range}, timeout: {timeout}s")

        # Initialize nmap scanner
        nmap_scanner = NmapModbusScanner()

        # Perform nmap scan
        found_devices = nmap_scanner.scan_network_nmap(
            network=network,
            port_range=port_range,
            timeout=timeout,
            use_modbus_discover=use_modbus_discover
        )

        # Automatically add detected devices if requested
        added_count = 0
        if auto_add:
            for device in found_devices:
                if 'manufacturer' in device and 'model' in device:
                    new_device = {
                        'name': device['name'],
                        'manufacturer': device['manufacturer'],
                        'model': device['model'],
                        'host': device['ip'],
                        'port': device['port'],
                        'slave_id': 1
                    }
                    devices.append(new_device)
                    added_count += 1
                    logger.info(f"Auto-added device: {device['name']} at {device['ip']}:{device['port']}")

            # Save configuration if devices were added
            if added_count > 0:
                save_config()

        logger.info(f"Nmap scan complete: found {len(found_devices)} devices, added {added_count}")
        return jsonify({
            'success': True,
            'devices': found_devices,
            'total': len(found_devices),
            'added_count': added_count,
            'scan_method': 'nmap'
        })

    except Exception as e:
        logger.error(f"Error during nmap scan: {e}", exc_info=True)
        return jsonify({'error': str(e), 'scan_method': 'nmap'}), 500


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

        logger.info(f"Generated configuration with {added_count} devices at {abs_path}")
        return jsonify({
            'success': True,
            'config': yaml_config,
            'path': abs_path,
            'absolute_path': abs_path,
            'devices_count': added_count
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
        import yaml
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


if __name__ == '__main__':
    logger.info("Starting Universal Modbus Configurator")
    logger.info(f"Config path: {CONFIG_PATH}")
    logger.info(f"Modbus config path: {MODBUS_CONFIG_PATH}")

    # Load existing configuration
    load_config()

    # Start web server
    app.run(host='0.0.0.0', port=8099, debug=False)

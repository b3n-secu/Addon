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
MODBUS_CONFIG_PATH = os.environ.get('MODBUS_CONFIG_PATH', '/config/modbus_generated.yaml')

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
    """Scan network for Modbus devices"""
    try:
        data = request.json or {}
        network = data.get('network')  # Optional, e.g. "192.168.1.0/24"
        ports = data.get('ports', [502, 510])

        logger.info(f"Starting network scan on {network or 'auto-detected network'}...")
        devices = NetworkScanner.scan_network(network, ports, timeout=1)

        logger.info(f"Network scan complete: found {len(devices)} devices")
        return jsonify({
            'success': True,
            'devices': devices,
            'total': len(devices)
        })

    except Exception as e:
        logger.error(f"Error scanning network: {e}")
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
        data = request.json
        output_path = data.get('output_path', MODBUS_CONFIG_PATH)
        include_scan = data.get('include_scan', False)

        # Clear previous configuration
        config_generator.clear()

        # Add all devices
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

            config_generator.add_device(device, scan_results)

        # Generate YAML
        yaml_config = config_generator.generate_yaml(output_path)

        logger.info(f"Generated configuration with {len(devices)} devices")
        return jsonify({
            'success': True,
            'config': yaml_config,
            'path': output_path
        })

    except Exception as e:
        logger.error(f"Error generating config: {e}")
        return jsonify({'error': str(e)}), 500


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


if __name__ == '__main__':
    logger.info("Starting Universal Modbus Configurator")
    logger.info(f"Config path: {CONFIG_PATH}")
    logger.info(f"Modbus config path: {MODBUS_CONFIG_PATH}")

    # Load existing configuration
    load_config()

    # Start web server
    app.run(host='0.0.0.0', port=8099, debug=False)

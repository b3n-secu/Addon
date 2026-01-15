#!/bin/bash
set -e

echo "Starting Universal Modbus Configurator..."

# Set default config path
export MODBUS_CONFIG_PATH="/config/modbus_generated.yaml"
export CONFIG_PATH="/data/options.json"

# Read config path from options if available
if [ -f "/data/options.json" ]; then
    CUSTOM_PATH=$(jq -r '.modbus_config_path // empty' /data/options.json)
    if [ -n "$CUSTOM_PATH" ]; then
        export MODBUS_CONFIG_PATH="$CUSTOM_PATH"
    fi
fi

echo "Modbus config will be written to: ${MODBUS_CONFIG_PATH}"

# Start the web application
echo "Starting web interface on port 8099..."
cd /app
exec python3 app.py

#!/usr/bin/with-contenv bashio

bashio::log.info "Starting Universal Modbus Configurator..."

# Get config path from options
CONFIG_PATH=$(bashio::config 'modbus_config_path')
bashio::log.info "Modbus config will be written to: ${CONFIG_PATH}"

# Export config path for Python app
export MODBUS_CONFIG_PATH="${CONFIG_PATH}"
export CONFIG_PATH="/data/options.json"

# Start the web application
bashio::log.info "Starting web interface on port 8099..."
cd /app
python3 app.py

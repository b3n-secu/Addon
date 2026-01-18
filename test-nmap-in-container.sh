#!/bin/bash
#
# Quick test script to verify nmap is working in the container
#

IMAGE_NAME="universal-modbus-configurator:latest"

echo "🧪 Testing nmap in Docker container..."
echo ""

# Build image
echo "📦 Building Docker image..."
docker build -t $IMAGE_NAME . > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✓ Build successful"
else
    echo "✗ Build failed"
    exit 1
fi

echo ""
echo "🔍 Testing nmap installation..."
echo ""

# Test 1: Nmap binary
echo -n "1. Nmap binary: "
NMAP_VERSION=$(docker run --rm $IMAGE_NAME nmap --version 2>/dev/null | head -n1)
if [ -n "$NMAP_VERSION" ]; then
    echo "✓ $NMAP_VERSION"
else
    echo "✗ FAILED"
    exit 1
fi

# Test 2: NSE scripts
echo -n "2. modbus-discover NSE script: "
NSE_SCRIPT=$(docker run --rm $IMAGE_NAME ls /usr/share/nmap/scripts/modbus-discover.nse 2>/dev/null)
if [ -n "$NSE_SCRIPT" ]; then
    echo "✓ Found"
else
    echo "✗ NOT FOUND"
    exit 1
fi

# Test 3: Python nmap module
echo -n "3. python-nmap module: "
PYTHON_NMAP=$(docker run --rm $IMAGE_NAME python3 -c "import nmap; print('OK')" 2>/dev/null)
if [ "$PYTHON_NMAP" = "OK" ]; then
    echo "✓ Imported successfully"
else
    echo "✗ IMPORT FAILED"
    exit 1
fi

# Test 4: Flask app can import nmap_scanner
echo -n "4. nmap_scanner module: "
NMAP_SCANNER=$(docker run --rm $IMAGE_NAME python3 -c "import sys; sys.path.insert(0, '/app'); from nmap_scanner import NmapModbusScanner; print('OK')" 2>/dev/null)
if [ "$NMAP_SCANNER" = "OK" ]; then
    echo "✓ Imported successfully"
else
    echo "✗ IMPORT FAILED"
    exit 1
fi

echo ""
echo "✅ All tests passed! Nmap is fully integrated in the container."
echo ""
echo "You can now run:"
echo "  ./build-and-test.sh"
echo ""

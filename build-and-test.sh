#!/bin/bash
#
# Build and Test Script for Universal Modbus Configurator
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="universal-modbus-configurator"
CONTAINER_NAME="modbus-config-test"
PORT=8099

echo -e "${BLUE}=== Universal Modbus Configurator - Build & Test ===${NC}\n"

# Step 1: Stop and remove existing container
echo -e "${YELLOW}[1/6] Stopping existing container (if any)...${NC}"
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true
echo -e "${GREEN}✓ Cleanup complete${NC}\n"

# Step 2: Build Docker image
echo -e "${YELLOW}[2/6] Building Docker image...${NC}"
docker build -t $IMAGE_NAME:latest .
echo -e "${GREEN}✓ Build complete${NC}\n"

# Step 3: Create test config directory
echo -e "${YELLOW}[3/6] Creating test configuration directory...${NC}"
mkdir -p ./test-config
echo -e "${GREEN}✓ Test directory created${NC}\n"

# Step 4: Start container
echo -e "${YELLOW}[4/6] Starting container...${NC}"
docker run -d \
  --name $CONTAINER_NAME \
  -p $PORT:8099 \
  -v $(pwd)/test-config:/config \
  $IMAGE_NAME:latest

# Wait for container to start
sleep 3
echo -e "${GREEN}✓ Container started${NC}\n"

# Step 5: Verify nmap installation
echo -e "${YELLOW}[5/6] Verifying nmap installation in container...${NC}"

# Check nmap binary
echo -n "  → Checking nmap binary: "
if docker exec $CONTAINER_NAME nmap --version > /dev/null 2>&1; then
    NMAP_VERSION=$(docker exec $CONTAINER_NAME nmap --version | head -n1)
    echo -e "${GREEN}✓${NC} $NMAP_VERSION"
else
    echo -e "${RED}✗ FAILED${NC}"
    exit 1
fi

# Check nmap NSE scripts
echo -n "  → Checking modbus-discover NSE script: "
if docker exec $CONTAINER_NAME ls /usr/share/nmap/scripts/modbus-discover.nse > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Found${NC}"
else
    echo -e "${RED}✗ NOT FOUND${NC}"
    exit 1
fi

# Check python-nmap module
echo -n "  → Checking python-nmap module: "
if docker exec $CONTAINER_NAME python3 -c "import nmap; print('OK')" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Imported successfully${NC}"
else
    echo -e "${RED}✗ IMPORT FAILED${NC}"
    exit 1
fi

echo ""

# Step 6: Test API endpoints
echo -e "${YELLOW}[6/6] Testing API endpoints...${NC}"

# Wait for Flask to start
sleep 2

# Test /api/status endpoint
echo -n "  → Testing /api/status: "
STATUS_RESPONSE=$(curl -s http://localhost:$PORT/api/status)
NMAP_AVAILABLE=$(echo $STATUS_RESPONSE | grep -o '"nmap_available":[^,}]*' | cut -d':' -f2 | tr -d ' ')

if [ "$NMAP_AVAILABLE" = "true" ]; then
    echo -e "${GREEN}✓ Nmap available${NC}"
else
    echo -e "${RED}✗ Nmap NOT available (API reports: $NMAP_AVAILABLE)${NC}"
    echo "Response: $STATUS_RESPONSE"
    exit 1
fi

# Test manufacturers endpoint
echo -n "  → Testing /api/manufacturers: "
MANUFACTURERS=$(curl -s http://localhost:$PORT/api/manufacturers)
if echo $MANUFACTURERS | grep -q "Siemens"; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
    exit 1
fi

echo ""

# Show container logs
echo -e "${YELLOW}Recent container logs:${NC}"
docker logs --tail 20 $CONTAINER_NAME
echo ""

# Success message
echo -e "${GREEN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                    ║${NC}"
echo -e "${GREEN}║  ✓ Build and tests completed successfully!        ║${NC}"
echo -e "${GREEN}║                                                    ║${NC}"
echo -e "${GREEN}║  Access the web interface at:                     ║${NC}"
echo -e "${GREEN}║  ${BLUE}http://localhost:$PORT${GREEN}                            ║${NC}"
echo -e "${GREEN}║                                                    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}"
echo ""

# Show available commands
echo -e "${BLUE}Available commands:${NC}"
echo "  • View logs:       docker logs -f $CONTAINER_NAME"
echo "  • Shell access:    docker exec -it $CONTAINER_NAME sh"
echo "  • Stop container:  docker stop $CONTAINER_NAME"
echo "  • Remove:          docker rm $CONTAINER_NAME"
echo ""
echo -e "${YELLOW}Container is running in background. Press Ctrl+C to exit this script.${NC}"
echo -e "${YELLOW}(Container will continue running)${NC}"
echo ""

# Option to follow logs
read -p "Follow container logs? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker logs -f $CONTAINER_NAME
fi

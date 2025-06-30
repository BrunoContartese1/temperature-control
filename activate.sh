#!/bin/bash
# Activate virtual environment for ESP32 Temperature Control Project

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== ESP32 Temperature Control Project ===${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run setup first:"
    echo "  ./setup.sh"
    exit 1
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

echo ""
echo -e "${GREEN}Virtual environment activated!${NC}"
echo ""
echo "Available commands:"
echo "  ./src/tools/esp32_upload.sh --all    # Upload to ESP32"
echo "  python src/tools/check_esp32_status.py  # Check ESP32 status"
echo "  python src/tests/test_web_server.py     # Test web server"
echo ""
echo "To deactivate, run: deactivate"
echo "" 
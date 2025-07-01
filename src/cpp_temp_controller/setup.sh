#!/bin/bash

# ESP32 Temperature Controller Setup Script
# This script helps set up the development environment

set -e

echo "🚀 ESP32 Professional Temperature Controller Setup"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "esp32_temperature_controller.ino" ]; then
    print_error "Please run this script from the cpp_temp_controller directory"
    exit 1
fi

print_status "Checking system requirements..."

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python3 found: $PYTHON_VERSION"
else
    print_error "Python3 is required but not installed"
    exit 1
fi

# Check pip
if command -v pip3 &> /dev/null; then
    print_success "pip3 found"
else
    print_error "pip3 is required but not installed"
    exit 1
fi

# Check if esptool is installed
if python3 -c "import esptool" &> /dev/null; then
    print_success "esptool is already installed"
else
    print_status "Installing esptool..."
    pip3 install esptool
    print_success "esptool installed"
fi

# Check for mkspiffs
if command -v mkspiffs &> /dev/null; then
    print_success "mkspiffs found"
else
    print_warning "mkspiffs not found"
    echo "Please install mkspiffs:"
    echo "  - Download from: https://github.com/igrr/mkspiffs/releases"
    echo "  - Or build from source: https://github.com/igrr/mkspiffs"
    echo ""
fi

# Check data directory
if [ -d "data" ]; then
    print_success "Data directory found"
    
    # Check for required files
    required_files=("index.html" "style.css" "script.js")
    missing_files=()
    
    for file in "${required_files[@]}"; do
        if [ ! -f "data/$file" ]; then
            missing_files+=("$file")
        fi
    done
    
    if [ ${#missing_files[@]} -eq 0 ]; then
        print_success "All web interface files present"
    else
        print_warning "Missing web interface files: ${missing_files[*]}"
    fi
else
    print_error "Data directory not found"
    exit 1
fi

# Make upload script executable
if [ -f "upload_data.py" ]; then
    chmod +x upload_data.py
    print_success "Upload script made executable"
else
    print_error "Upload script not found"
    exit 1
fi

# Check for ESP32 device
print_status "Checking for ESP32 device..."
if ls /dev/ttyACM* 2>/dev/null | grep -q .; then
    ESP32_PORTS=$(ls /dev/ttyACM*)
    print_success "ESP32 device(s) found: $ESP32_PORTS"
else
    print_warning "No ESP32 device detected"
    echo "Please connect your ESP32 via USB"
fi

echo ""
print_status "Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Open esp32_temperature_controller.ino in Arduino IDE"
echo "2. Install required libraries (see README.md)"
echo "3. Configure board settings (see README.md)"
echo "4. Upload the firmware"
echo "5. Run: python3 upload_data.py --port /dev/ttyUSB0"
echo ""
echo "📖 For detailed instructions, see README.md"
echo "🔧 For troubleshooting, see the Troubleshooting section in README.md" 
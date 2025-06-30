#!/bin/bash
# Setup script for ESP32 Temperature Control Project
# This script creates a virtual environment and installs dependencies

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

echo "=== ESP32 Temperature Control Project Setup ==="
echo ""

# Remove existing venv if it exists
if [ -d "venv" ]; then
    print_status "Removing existing virtual environment..."
    rm -rf venv
fi

# Try to create virtual environment
print_status "Creating virtual environment..."
if python3 -m venv venv; then
    print_success "Virtual environment created successfully"
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip
    
    # Install dependencies
    print_status "Installing dependencies..."
    pip install -r requirements.txt
    
    print_success "Setup completed successfully!"
    echo ""
    print_status "To activate the virtual environment, run:"
    echo "  source venv/bin/activate"
    echo "  # or use the convenience script:"
    echo "  ./activate.sh"
    echo ""
    print_status "To deactivate, run:"
    echo "  deactivate"
    echo ""
    print_status "Next steps:"
    echo "  1. Activate the virtual environment"
    echo "  2. Run the ESP32 upload script:"
    echo "     ./src/tools/esp32_upload.sh --all"
else
    print_warning "Failed to create virtual environment. Installing packages globally..."
    print_warning "This is not recommended but will work for development."
    echo ""
    
    # Install packages globally as fallback
    print_status "Installing dependencies globally..."
    pip3 install -r requirements.txt
    
    print_success "Setup completed (global installation)!"
    echo ""
    print_warning "Note: Packages are installed globally. Consider fixing virtual environment issues."
    echo ""
    print_status "Next steps:"
    echo "  1. Run the ESP32 upload script:"
    echo "     ./src/tools/esp32_upload.sh --all"
fi 
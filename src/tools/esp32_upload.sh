#!/bin/bash
# ESP32 Upload Script
# This script helps upload the temperature controller to ESP32

set -e

# Configuration
PORT="/dev/ttyACM0"
BAUD_RATE="115200"
FIRMWARE_URL="https://micropython.org/resources/firmware/esp32-20230426-v1.20.0.bin"
FIRMWARE_FILE="../../firmware/ESP32_GENERIC-20250415-v1.25.0.bin"

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if ESP32 is connected
check_esp32_connection() {
    if [ ! -e "$PORT" ]; then
        print_error "ESP32 not found on $PORT"
        print_status "Please check:"
        echo "  1. ESP32 is connected via USB"
        echo "  2. USB cable supports data transfer"
        echo "  3. Correct port (try: ls /dev/tty*)"
        exit 1
    fi
    print_success "ESP32 found on $PORT"
}

# Function to install required tools
install_tools() {
    print_status "Checking required tools..."
    
    if ! command_exists esptool; then
        print_warning "esptool not found. Installing..."
        pip install esptool
    else
        print_success "esptool found"
    fi
    
    if ! command_exists ampy; then
        print_warning "ampy not found. Installing..."
        pip install adafruit-ampy
    else
        print_success "ampy found"
    fi
}

# Function to flash MicroPython firmware
flash_firmware() {
    print_status "Flashing MicroPython firmware..."
    
    if [ ! -f "$FIRMWARE_FILE" ]; then
        print_status "Downloading MicroPython firmware..."
        wget -O "$FIRMWARE_FILE" "$FIRMWARE_URL"
    fi
    
    print_status "Erasing flash..."
    esptool.py --chip esp32 --port "$PORT" erase_flash
    
    print_status "Writing firmware..."
    esptool.py --chip esp32 --port "$PORT" write_flash -z 0x1000 "$FIRMWARE_FILE"
    
    print_success "Firmware flashed successfully"
}

# Function to upload application files
upload_files() {
    print_status "Uploading application files..."
    
    # Upload main application
    print_status "Uploading main application..."
    ampy --port "$PORT" put ../esp32/esp32_temperature_control.py main.py
    
    # Upload boot script
    print_status "Uploading boot script..."
    ampy --port "$PORT" put ../esp32/esp32_boot.py boot.py
    
    # Upload test script
    print_status "Uploading test script..."
    ampy --port "$PORT" put ../esp32/esp32_test_sensor.py test_sensor.py
    
    print_success "All files uploaded successfully"
}

# Function to test connection
test_connection() {
    print_status "Testing ESP32 connection..."
    
    # Wait a moment for ESP32 to boot
    sleep 3
    
    # Try to get file list
    if ampy --port "$PORT" ls >/dev/null 2>&1; then
        print_success "ESP32 connection test passed"
        return 0
    else
        print_error "ESP32 connection test failed"
        return 1
    fi
}

# Function to show usage
show_usage() {
    echo "ESP32 Temperature Controller Upload Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -p, --port PORT     Serial port (default: /dev/ttyUSB0)"
    echo "  -f, --flash         Flash MicroPython firmware"
    echo "  -u, --upload        Upload application files"
    echo "  -t, --test          Test ESP32 connection"
    echo "  -a, --all           Do everything (flash + upload + test)"
    echo "  -h, --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --all                    # Complete setup"
    echo "  $0 --flash                  # Only flash firmware"
    echo "  $0 --upload --port /dev/ttyUSB1  # Upload to different port"
}

# Main script
main() {
    echo "=== ESP32 Temperature Controller Upload Script ==="
    echo ""
    
    # Parse command line arguments
    FLASH=false
    UPLOAD=false
    TEST=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -p|--port)
                PORT="$2"
                shift 2
                ;;
            -f|--flash)
                FLASH=true
                shift
                ;;
            -u|--upload)
                UPLOAD=true
                shift
                ;;
            -t|--test)
                TEST=true
                shift
                ;;
            -a|--all)
                FLASH=true
                UPLOAD=true
                TEST=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # If no options specified, show usage
    if [ "$FLASH" = false ] && [ "$UPLOAD" = false ] && [ "$TEST" = false ]; then
        show_usage
        exit 0
    fi
    
    # Check ESP32 connection
    check_esp32_connection
    
    # Install required tools
    install_tools
    
    # Flash firmware if requested
    if [ "$FLASH" = true ]; then
        flash_firmware
    fi
    
    # Upload files if requested
    if [ "$UPLOAD" = true ]; then
        upload_files
    fi
    
    # Test connection if requested
    if [ "$TEST" = true ]; then
        test_connection
    fi
    
    print_success "Setup completed successfully!"
    echo ""
    print_status "Next steps:"
    echo "  1. Connect to WiFi network 'TempController' (password: temp123456)"
    echo "  2. Open web browser and go to http://192.168.4.1"
    echo "  3. Configure your temperature settings"
    echo ""
    print_status "To monitor ESP32 output, use:"
    echo "  screen $PORT $BAUD_RATE"
}

# Run main function
main "$@" 
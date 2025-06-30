# ESP32 Temperature Controller

A complete temperature control system using ESP32 and DS18B20 temperature sensors with a web interface.

## Project Structure

```
temperature-control/
├── src/
│   ├── esp32/                 # ESP32 MicroPython code
│   │   ├── esp32_temperature_control.py  # Main application
│   │   ├── esp32_boot.py      # Boot script
│   │   ├── esp32_test_sensor.py  # Sensor test script
│   │   └── esp32_simple_test.py  # Simple test script
│   ├── tools/                 # Development and deployment tools
│   │   ├── esp32_upload.sh    # Upload script
│   │   └── check_esp32_status.py  # Status checker
│   └── tests/                 # Test scripts
│       ├── test_web_server.py # Web server test
│       ├── test_sensor.py     # Sensor test
│       └── temperature.py     # Temperature monitoring
├── docs/                      # Documentation
│   ├── README.md             # Original README
│   └── esp32_setup.md        # Setup guide
├── firmware/                  # Firmware files
│   └── esp32-firmware.bin    # MicroPython firmware
├── venv/                     # Virtual environment (created by setup)
├── requirements.txt          # Python dependencies
├── setup.sh                  # Setup script
└── config.py                 # Configuration file
```

## Quick Start

### 1. Setup Environment

```bash
# Run the setup script to create virtual environment and install dependencies
./setup.sh

# Activate the virtual environment
source venv/bin/activate
```

### 2. Upload to ESP32

```bash
# Upload everything (firmware + application)
./src/tools/esp32_upload.sh --all

# Or step by step:
./src/tools/esp32_upload.sh --flash    # Flash MicroPython firmware
./src/tools/esp32_upload.sh --upload   # Upload application files
./src/tools/esp32_upload.sh --test     # Test connection
```

### 3. Connect and Use

1. Connect to WiFi network `TempController` (password: `temp123456`)
2. Open web browser and go to `http://192.168.4.1`
3. Configure temperature settings

## Development

### Virtual Environment

The project uses a virtual environment to manage Python dependencies. Always activate it before working:

```bash
source venv/bin/activate
```

### Dependencies

Main dependencies (installed automatically by setup.sh):
- `esptool` - ESP32 flashing tool
- `adafruit-ampy` - MicroPython file transfer
- `requests` - Web testing

### Testing

```bash
# Test web server
python src/tests/test_web_server.py

# Test sensor
python src/tests/test_sensor.py

# Check ESP32 status
python src/tools/check_esp32_status.py
```

## Troubleshooting

### Common Issues

1. **ESP32 not found**: Check USB connection and port
2. **Upload fails**: Try different port (e.g., `/dev/ttyUSB1`)
3. **Web interface not working**: Check WiFi connection and IP address

### Useful Commands

```bash
# List available ports
ls /dev/tty*

# Monitor ESP32 output
screen /dev/ttyACM0 115200

# Check ESP32 status
python src/tools/check_esp32_status.py
```

## Documentation

- [Setup Guide](docs/esp32_setup.md) - Detailed setup instructions
- [Original README](docs/README.md) - Original project documentation

## License

This project is open source. See LICENSE file for details. 
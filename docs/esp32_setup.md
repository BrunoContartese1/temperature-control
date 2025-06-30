# ESP32 Temperature Controller Setup Guide

## Hardware Requirements

### Components
- ESP32 development board
- DS18B20 temperature sensor
- 4.7kΩ resistor (pull-up for DS18B20)
- 5V relay module
- Power supply for ESP32 (USB or external)
- Breadboard and jumper wires

### Wiring Diagram

```
ESP32 Pin Connections:
- GPIO4  → DS18B20 Data Pin (with 4.7kΩ pull-up to 3.3V)
- GPIO5  → Relay Module Signal Pin
- 3.3V   → DS18B20 VCC + 4.7kΩ resistor
- GND    → DS18B20 GND + Relay GND

DS18B20 Sensor:
- VCC    → 3.3V (with 4.7kΩ pull-up resistor)
- Data   → GPIO4
- GND    → GND

Relay Module:
- VCC    → 5V (from external power supply)
- GND    → GND
- Signal → GPIO5
```

## Software Setup

### 1. Install MicroPython on ESP32

1. Download the latest MicroPython firmware for ESP32 from:
   https://micropython.org/download/esp32/

2. Install `esptool` to flash the firmware:
   ```bash
   pip install esptool
   ```

3. Flash MicroPython to ESP32:
   ```bash
   esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
   esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 esp32-firmware.bin
   ```

### 2. Upload the Application

1. Install `ampy` for file transfer:
   ```bash
   pip install adafruit-ampy
   ```

2. Upload the main application:
   ```bash
   ampy --port /dev/ttyUSB0 put esp32_temperature_control.py main.py
   ```

3. Reset the ESP32 to start the application

### 3. Connect to WiFi Access Point

1. The ESP32 will create a WiFi access point named "TempController"
2. Connect to this network using password "temp123456"
3. The ESP32's IP address will be displayed in the serial console (usually 192.168.4.1)

### 4. Access Web Interface

1. Open a web browser on your device
2. Navigate to `http://192.168.4.1`
3. You'll see the temperature controller web interface

## Configuration

### Default Settings
- **Temperature Low**: 20.0°C (activates relay)
- **Temperature High**: 25.0°C (deactivates relay)
- **Check Interval**: 5 seconds
- **WiFi SSID**: TempController
- **WiFi Password**: temp123456

### Customizing Settings

You can modify the default settings in the `esp32_temperature_control.py` file:

```python
# WiFi Configuration
WIFI_SSID = "YourNetworkName"
WIFI_PASSWORD = "YourPassword"

# Hardware pins (if different)
DS18B20_PIN = 4
RELAY_PIN = 5

# Default temperature settings
DEFAULT_TEMP_LOW = 20.0
DEFAULT_TEMP_HIGH = 25.0
DEFAULT_CHECK_INTERVAL = 5
```

## Features

### Web Interface
- Real-time temperature display
- Current relay status
- Configuration form for temperature settings
- Auto-refresh every 5 seconds

### Temperature Control
- Automatic relay control based on temperature thresholds
- Configurable temperature ranges
- Safety limits to prevent erroneous readings

### WiFi Access Point
- No router required
- Standalone operation
- Multiple device connections supported

## Troubleshooting

### Common Issues

1. **DS18B20 not found**
   - Check wiring connections
   - Verify 4.7kΩ pull-up resistor is connected
   - Ensure sensor is powered with 3.3V

2. **Relay not working**
   - Check relay module connections
   - Verify relay module power supply (5V)
   - Test relay with simple GPIO toggle

3. **WiFi access point not visible**
   - Check serial console for error messages
   - Verify ESP32 has enough power
   - Try resetting the ESP32

4. **Web interface not accessible**
   - Ensure you're connected to the "TempController" network
   - Check the IP address in serial console
   - Try accessing http://192.168.4.1

### Serial Console Access

Connect to the ESP32 serial console to see debug messages:

```bash
screen /dev/ttyUSB0 115200
```

Or use any serial terminal application with these settings:
- Baud rate: 115200
- Data bits: 8
- Parity: None
- Stop bits: 1
- Flow control: None

## API Endpoints

The web server provides these API endpoints:

- `GET /` - Main web interface
- `GET /api/status` - JSON status data
- `GET /api/config` - JSON configuration data
- `POST /` - Update configuration

## Power Considerations

- ESP32 can be powered via USB or external 5V supply
- Relay module typically requires 5V power supply
- Consider using a power supply that can handle both ESP32 and relay current
- For continuous operation, use a stable power supply

## Security Notes

- The default WiFi password is simple for easy setup
- Change the password in production environments
- The web interface has no authentication
- Consider adding authentication for production use 
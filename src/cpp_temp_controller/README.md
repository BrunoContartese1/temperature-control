# ESP32 Professional Temperature Controller (C++)

A high-performance, professional-grade temperature monitoring and control system built with C++ for the ESP32 microcontroller. Features a modern web dashboard with real-time charts, automatic temperature control, and comprehensive system monitoring.

## 🌟 Features

### Core Functionality
- **High-Temperature Monitoring**: Designed for 0-120°C range with precision control
- **Automatic Relay Control**: Activates at 60°C, deactivates at 70°C (configurable)
- **Real-Time Data Logging**: Stores up to 100 data points in memory
- **2-Second Reading Interval**: Fast response time for critical applications
- **Emergency Shutdown**: Automatic safety shutdown at 120°C

### Web Interface (Now Inline)
- **Modern Dashboard**: Professional, responsive design
- **No SPIFFS/Web Files Needed**: The entire web interface is served inline from the firmware (no upload or mkspiffs required)
- **Live Status Monitoring**: Relay, sensor, and controller status indicators
- **Configuration Panel**: Easy temperature and interval adjustment
- **Manual Controls**: Direct relay and controller control
- **System Information**: Uptime, readings count, error tracking

### Technical Features
- **WiFi Access Point**: No router required - ESP32 creates its own network
- **REST API**: JSON endpoints for external integration
- **Configuration Persistence**: Settings are saved in SPIFFS as JSON (no web files)
- **Error Handling**: Comprehensive error detection and reporting
- **Memory Management**: Efficient data structures and garbage collection

## 🛠️ Hardware Requirements

### Required Components
- **ESP32 Development Board** (ESP32-WROOM-32 or similar)
- **DS18B20 Temperature Sensor** (waterproof version recommended)
- **4.7kΩ Pull-up Resistor** (for DS18B20)
- **5V Relay Module** (for controlling heating/cooling system)
- **Breadboard and Jumper Wires**
- **USB Cable** (for programming)

### Wiring Diagram
```
ESP32 Pin Connections:
├── GPIO4  → DS18B20 Data Pin (with 4.7kΩ pull-up to 3.3V)
├── GPIO5  → Relay Module Signal Pin
├── 3.3V   → DS18B20 VCC + Pull-up Resistor
└── GND    → DS18B20 GND + Relay Module GND
```

## 📋 Software Requirements

### Arduino IDE Setup
1. **Install Arduino IDE** (version 1.8.19 or later)
2. **Add ESP32 Board Manager**:
   - Open Arduino IDE → Preferences
   - Add to Additional Board Manager URLs:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
3. **Install ESP32 Board Package**:
   - Tools → Board → Boards Manager
   - Search "ESP32" and install "ESP32 by Espressif Systems"

### Required Libraries
Install these libraries via Arduino IDE Library Manager:
- **OneWire** by Paul Stoffregen
- **DallasTemperature** by Miles Burton
- **ArduinoJson** by Benoit Blanchon
- **ESPAsyncWebServer** by lacamera
- **AsyncTCP** by dvarrel

### Tools Installation
- **esptool**: `pip install esptool`
- **mkspiffs**: Download from [GitHub releases](https://github.com/igrr/mkspiffs/releases)

## 🚀 Installation & Setup

### 1. Clone and Prepare
```bash
# Navigate to the project directory
cd src/cpp_temp_controller

# Verify file structure
ls -la
# Should show: esp32_temperature_controller.ino, README.md, (no data/ or web files needed)
```

### 2. Configure Arduino IDE
1. **Select Board**: Tools → Board → ESP32 Arduino → ESP32 Dev Module
2. **Configure Settings**:
   - Upload Speed: 115200
   - CPU Frequency: 240MHz
   - Flash Frequency: 80MHz
   - Flash Mode: QIO
   - Flash Size: 4MB (32Mb)
   - Partition Scheme: Default 4MB with spiffs (1.2MB APP/1.5MB SPIFFS)

### 3. Upload Firmware
1. **Connect ESP32** via USB
2. **Select Port**: Tools → Port → (your ESP32 port)
3. **Upload**: Click Upload button or press Ctrl+U
4. **Monitor**: Open Serial Monitor (115200 baud) to see startup messages

> **Note:** You no longer need to upload any web interface files or use mkspiffs. The web dashboard is now fully embedded in the firmware.

## 📱 Usage

### Initial Setup
1. **Power on ESP32** - it will create WiFi access point
2. **Connect to WiFi**:
   - SSID: `TempController`
   - Password: `temp123456`
3. **Open Browser**: Navigate to `http://192.168.4.1`
4. **Configure Settings**: Set your desired temperature ranges

### Web Dashboard Features

#### Real-Time Monitoring
- **Temperature Display**: Large, color-coded temperature reading
- **Range Indicator**: Visual temperature range with control points
- **Status Indicators**: Relay, controller, and sensor status
- **System Uptime**: Continuous operation tracking

#### Configuration Panel
- **Temperature Low**: Relay activation temperature (default: 60°C)
- **Temperature High**: Relay deactivation temperature (default: 70°C)
- **Check Interval**: Reading frequency in seconds (default: 2s)
- **Validation**: Automatic range and logic validation

#### Manual Controls
- **Start/Stop Controller**: Enable/disable automatic control
- **Relay ON/OFF**: Direct relay control for testing
- **Chart Controls**: Refresh or clear temperature history

#### Data Visualization
- **Temperature Chart**: Real-time line chart with time axis
- **Relay State**: Overlay showing relay activation periods
- **Data Points**: Up to 100 historical readings
- **Interactive**: Hover for detailed information

### API Endpoints
The system provides REST API for external integration:

```bash
# Get system status
GET /api/status

# Get current configuration
GET /api/config

# Update configuration
POST /api/config
  temp_low=60.0&temp_high=70.0&check_interval=2

# Get temperature data
GET /api/data

# Control commands
POST /api/control
  action=start|stop|relay_on|relay_off
```

## ⚙️ Configuration

### Default Settings
- **Temperature Range**: 60-70°C (relay control)
- **Maximum Temperature**: 120°C (safety limit)
- **Reading Interval**: 2 seconds
- **Data Points**: 100 historical readings
- **WiFi**: Access point mode, no router required

### Customization
Edit `esp32_temperature_controller.ino` to modify:
- WiFi credentials (SSID/password)
- Hardware pin assignments
- Temperature limits and intervals
- Data logging parameters

### Safety Features
- **Emergency Shutdown**: Automatic at 120°C
- **Sensor Validation**: Range checking and error detection
- **Relay Protection**: Automatic deactivation on errors
- **Configuration Validation**: Prevents invalid settings

## 🔧 Troubleshooting

### Common Issues

#### ESP32 Not Detected
```bash
# Check USB connection
ls /dev/ttyUSB*

# Install drivers if needed
# Windows: Install CP210x or CH340 drivers
# Linux: Add user to dialout group
sudo usermod -a -G dialout $USER
```

#### Upload Failures
```bash
# Try different upload speeds
# Hold BOOT button during upload
# Check USB cable quality
# Verify board selection in Arduino IDE
```

#### Web Interface Not Loading
```bash
# Check SPIFFS upload
python3 upload_data.py --skip-upload

# Verify file structure
ls -la data/
# Should show: index.html, style.css, script.js

# Check serial monitor for errors
```

#### Temperature Reading Issues
- **Check Wiring**: Verify DS18B20 connections
- **Pull-up Resistor**: Ensure 4.7kΩ resistor is connected
- **Power Supply**: Use stable 3.3V power
- **Sensor Distance**: Keep wires short for better reliability

#### WiFi Connection Problems
- **Reset ESP32**: Power cycle the device
- **Check Credentials**: Verify SSID/password
- **Signal Strength**: Ensure device is within range
- **Interference**: Avoid 2.4GHz interference sources

### Debug Information
Enable debug output by uncommenting debug lines in the code:
```cpp
#define DEBUG_MODE 1
```

Monitor serial output for detailed system information:
```bash
# Serial monitor settings
# Baud rate: 115200
# Line ending: Both NL & CR
```

## 📊 Performance Specifications

### Temperature Control
- **Range**: 0-120°C
- **Accuracy**: ±0.5°C (DS18B20 specification)
- **Response Time**: 2 seconds
- **Control Precision**: 0.1°C

### System Performance
- **Memory Usage**: ~200KB (firmware) + ~50KB (web interface)
- **Data Storage**: 100 data points in RAM
- **Web Response**: <100ms for API calls
- **Uptime**: Continuous operation supported

### Network Performance
- **WiFi Range**: ~30 meters (open space)
- **Max Clients**: 4 simultaneous connections
- **Data Transfer**: ~1KB per status update
- **Power Consumption**: ~150mA (active), ~10mA (sleep)

## 🔒 Security Considerations

### Network Security
- **Access Point**: WPA2 encryption
- **Default Password**: Change from `temp123456`
- **Local Network**: No internet access required
- **Firewall**: Consider network isolation for critical systems

### System Security
- **Configuration Validation**: Prevents invalid settings
- **Error Handling**: Graceful failure modes
- **Memory Protection**: Bounds checking on all operations
- **Watchdog Timer**: Automatic reset on system hang

## 🤝 Contributing

### Development Setup
1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-feature`
3. **Make changes** and test thoroughly
4. **Submit pull request** with detailed description

### Code Style
- **C++**: Follow Arduino/ESP32 conventions
- **JavaScript**: ES6+ with modern practices
- **CSS**: BEM methodology with CSS custom properties
- **Documentation**: Inline comments and README updates

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **ESP32 Community**: For excellent documentation and examples
- **Arduino Libraries**: OneWire, DallasTemperature, ArduinoJson
- **Chart.js**: For beautiful data visualization
- **Open Source Community**: For inspiration and best practices

## 📞 Support

### Getting Help
1. **Check Documentation**: This README and code comments
2. **Review Issues**: Search existing GitHub issues
3. **Create Issue**: Provide detailed problem description
4. **Community Forums**: ESP32 and Arduino communities

### Contact Information
- **GitHub Issues**: For bug reports and feature requests
- **Documentation**: Check inline code comments
- **Examples**: Review code structure and patterns

---

**Happy Temperature Controlling! 🌡️** 
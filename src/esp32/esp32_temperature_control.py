#!/usr/bin/env python3
"""
ESP32 Temperature Controller with DS18B20 sensor and relay
Web interface for configuration and monitoring

Hardware Setup:
- DS18B20 sensor connected to GPIO4 (with 4.7kΩ pull-up resistor)
- Relay connected to GPIO5
- ESP32 creates WiFi access point for configuration

Features:
- Web interface to view/set TEMP_LOW and TEMP_HIGH
- Real-time temperature monitoring
- Automatic temperature control
- WiFi access point mode (no router needed)
"""

import network
import socket
import time
import json
import gc
from machine import Pin
import onewire
import ds18x20
import _thread

# Configuration
WIFI_SSID = "TempController"
WIFI_PASSWORD = "temp123456"
WIFI_CHANNEL = 1

# Hardware pins
DS18B20_PIN = 4
RELAY_PIN = 5

# Default temperature settings
DEFAULT_TEMP_LOW = 20.0
DEFAULT_TEMP_HIGH = 25.0
DEFAULT_CHECK_INTERVAL = 5

# Temperature limits
MAX_TEMP = 50.0
MIN_TEMP = -10.0

# Configuration file
CONFIG_FILE = "config.json"

class ESP32TemperatureController:
    def __init__(self):
        self.temp_low = DEFAULT_TEMP_LOW
        self.temp_high = DEFAULT_TEMP_HIGH
        self.check_interval = DEFAULT_CHECK_INTERVAL
        self.relay_active = False
        self.running = False
        self.current_temp = None
        self.last_reading_time = 0
        
        # Load configuration
        self.load_config()
        
        # Setup hardware
        self.setup_hardware()
        
        # Setup WiFi access point
        self.setup_wifi()
        
        print("ESP32 Temperature Controller initialized")
        print(f"  - Temperature Low (activate): {self.temp_low}°C")
        print(f"  - Temperature High (deactivate): {self.temp_high}°C")
        print(f"  - Check interval: {self.check_interval} seconds")
        print(f"  - WiFi SSID: {WIFI_SSID}")
        print(f"  - WiFi Password: {WIFI_PASSWORD}")
    
    def load_config(self):
        """Load configuration from file"""
        try:
            with open(CONFIG_FILE, 'r') as f:
                config_str = f.read()
                config = json.loads(config_str)
                self.temp_low = config.get('temp_low', DEFAULT_TEMP_LOW)
                self.temp_high = config.get('temp_high', DEFAULT_TEMP_HIGH)
                self.check_interval = config.get('check_interval', DEFAULT_CHECK_INTERVAL)
                print("Configuration loaded from file")
        except:
            print("Using default configuration")
            self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        try:
            config = {
                'temp_low': self.temp_low,
                'temp_high': self.temp_high,
                'check_interval': self.check_interval
            }
            # Use json.dumps() instead of json.dump() for MicroPython compatibility
            config_str = json.dumps(config)
            with open(CONFIG_FILE, 'w') as f:
                f.write(config_str)
            print("Configuration saved")
        except Exception as e:
            print(f"Error saving configuration: {e}")
    
    def setup_hardware(self):
        """Setup DS18B20 sensor and relay"""
        # Setup DS18B20 sensor
        self.ow = onewire.OneWire(Pin(DS18B20_PIN))
        self.ds = ds18x20.DS18X20(self.ow)
        
        # Find DS18B20 devices
        self.roms = self.ds.scan()
        if not self.roms:
            raise RuntimeError("No DS18B20 sensor found")
        print(f"DS18B20 sensor found: {self.roms[0]}")
        
        # Setup relay
        self.relay = Pin(RELAY_PIN, Pin.OUT)
        self.relay.value(0)  # Start with relay off
        print("Relay initialized")
    
    def setup_wifi(self):
        """Setup WiFi access point"""
        try:
            self.ap = network.WLAN(network.AP_IF)
            self.ap.active(True)
            
            # Configure access point (simplified for compatibility)
            self.ap.config(
                essid=WIFI_SSID,
                password=WIFI_PASSWORD,
                channel=WIFI_CHANNEL
            )
            
            # Wait for access point to be active
            while not self.ap.active():
                time.sleep(0.1)
            
            print(f"WiFi Access Point started")
            print(f"  SSID: {WIFI_SSID}")
            print(f"  Password: {WIFI_PASSWORD}")
            print(f"  IP Address: {self.ap.ifconfig()[0]}")
            
        except Exception as e:
            print(f"Error setting up WiFi: {e}")
            raise
    
    def read_temperature(self):
        """Read temperature from DS18B20 sensor"""
        try:
            self.ds.convert_temp()
            try:
                time.sleep_ms(750)  # Wait for conversion
            except Exception as e:
                print(f"Error in sleep_ms: {e}")
                time.sleep(0.75)  # Fallback to regular sleep
            
            temp = self.ds.read_temp(self.roms[0])
            
            if temp is not None and MIN_TEMP <= temp <= MAX_TEMP:
                self.current_temp = temp
                try:
                    self.last_reading_time = time.time()
                except Exception as e:
                    print(f"Error in time.time(): {e}")
                    self.last_reading_time = 0
                return temp
            else:
                print(f"Temperature reading out of range: {temp}°C")
                return None
                
        except Exception as e:
            print(f"Error reading temperature: {e}")
            return None
    
    def set_relay(self, active):
        """Control relay"""
        try:
            self.relay.value(1 if active else 0)
            self.relay_active = active
            status = "ON" if active else "OFF"
            print(f"Relay: {status}")
        except Exception as e:
            print(f"Error controlling relay: {e}")
    
    def control_logic(self, temperature):
        """Temperature control logic"""
        if temperature <= self.temp_low and not self.relay_active:
            print(f"Temperature {temperature:.1f}°C <= {self.temp_low}°C - Activating relay")
            self.set_relay(True)
        elif temperature >= self.temp_high and self.relay_active:
            print(f"Temperature {temperature:.1f}°C >= {self.temp_high}°C - Deactivating relay")
            self.set_relay(False)
    
    def start_control_loop(self):
        """Start the temperature control loop in a separate thread"""
        def control_thread():
            while self.running:
                temp = self.read_temperature()
                if temp is not None:
                    print(f"Current temperature: {temp:.1f}°C")
                    self.control_logic(temp)
                else:
                    print("Failed to read temperature")
                
                time.sleep(self.check_interval)
        
        self.running = True
        _thread.start_new_thread(control_thread, ())
        print("Temperature control loop started")
    
    def stop_control_loop(self):
        """Stop the temperature control loop"""
        self.running = False
        self.set_relay(False)
        print("Temperature control loop stopped")
    
    def get_status(self):
        """Get current status"""
        try:
            return {
                'temperature': self.current_temp,
                'relay_active': self.relay_active,
                'temp_low': self.temp_low,
                'temp_high': self.temp_high,
                'check_interval': self.check_interval,
                'running': self.running,
                'last_reading': self.last_reading_time
            }
        except Exception as e:
            print(f"Error in get_status: {e}")
            # Return a basic status without problematic fields
            return {
                'temperature': self.current_temp,
                'relay_active': self.relay_active,
                'temp_low': self.temp_low,
                'temp_high': self.temp_high,
                'check_interval': self.check_interval,
                'running': self.running,
                'last_reading': 0
            }
    
    def update_config(self, temp_low=None, temp_high=None, check_interval=None):
        """Update configuration"""
        if temp_low is not None:
            self.temp_low = float(temp_low)
        if temp_high is not None:
            self.temp_high = float(temp_high)
        if check_interval is not None:
            self.check_interval = int(check_interval)
        
        # Validate configuration
        if self.temp_low >= self.temp_high:
            raise ValueError("TEMP_LOW must be less than TEMP_HIGH")
        if self.check_interval < 1:
            raise ValueError("CHECK_INTERVAL must be at least 1 second")
        
        self.save_config()
        print("Configuration updated")

class WebServer:
    def __init__(self, controller):
        self.controller = controller
        self.socket = None
    
    def start(self, port=80):
        """Start web server"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('', port))
        self.socket.listen(5)
        print(f"Web server started on port {port}")
        
        while True:
            try:
                client, addr = self.socket.accept()
                print(f"Client connected from {addr}")
                self.handle_client(client)
                client.close()
            except Exception as e:
                print(f"Web server error: {e}")
                gc.collect()
    
    def handle_client(self, client):
        """Handle client request"""
        try:
            try:
                request = client.recv(1024).decode('utf-8')
            except Exception as e:
                print(f"Error in decode: {e}")
                try:
                    # Fallback without encoding specification
                    request = client.recv(1024).decode()
                except Exception as e2:
                    print(f"Error in fallback decode: {e2}")
                    return
            
            if not request:
                return
            
            print(f"Received request: {request[:200]}...")
            
            # Parse request
            lines = request.split('\n')
            if not lines:
                return
                
            first_line = lines[0].strip()
            print(f"First line: {first_line}")
            
            if first_line.startswith('GET'):
                print("Handling GET request...")
                try:
                    self.handle_get(client, first_line)
                except Exception as e:
                    print(f"Error in handle_get: {e}")
                    self.send_response(client, "500 Internal Server Error", "text/plain", f"GET Error: {e}")
            elif first_line.startswith('POST'):
                print("Handling POST request...")
                try:
                    self.handle_post(client, request)
                except Exception as e:
                    print(f"Error in handle_post: {e}")
                    self.send_response(client, "500 Internal Server Error", "text/plain", f"POST Error: {e}")
            else:
                print(f"Unsupported method: {first_line}")
                self.send_response(client, "405 Method Not Allowed", "text/plain", "Method not allowed")
                
        except Exception as e:
            print(f"Error handling client: {e}")
            try:
                self.send_response(client, "500 Internal Server Error", "text/plain", f"Server error: {e}")
            except:
                pass
    
    def handle_get(self, client, first_line):
        """Handle GET request"""
        print(f"GET request: {first_line}")
        
        if '/test' in first_line:
            print("Serving /test - simple test page")
            # Return a very simple test page
            test_html = """<!DOCTYPE html>
<html>
<head>
    <title>Test</title>
</head>
<body>
    <h1>ESP32 Test Page</h1>
    <p>If you can see this, the web server is working!</p>
</body>
</html>"""
            self.send_response(client, "200 OK", "text/html", test_html)
        elif '/api/status' in first_line:
            print("Serving /api/status")
            # Return JSON status
            status = self.controller.get_status()
            self.send_json_response(client, status)
        elif '/api/config' in first_line:
            print("Serving /api/config")
            # Return current configuration
            config = {
                'temp_low': self.controller.temp_low,
                'temp_high': self.controller.temp_high,
                'check_interval': self.controller.check_interval
            }
            self.send_json_response(client, config)
        else:
            print("Serving main HTML page")
            # Return HTML interface
            self.send_html_response(client)
    
    def handle_post(self, client, request):
        """Handle POST request"""
        try:
            # Extract POST data
            body_start = request.find('\r\n\r\n') + 4
            body = request[body_start:]
            
            # Parse form data
            data = {}
            for item in body.split('&'):
                if '=' in item:
                    key, value = item.split('=', 1)
                    data[key] = value.replace('+', ' ')
            
            # Update configuration
            temp_low = float(data.get('temp_low', self.controller.temp_low))
            temp_high = float(data.get('temp_high', self.controller.temp_high))
            check_interval = int(data.get('check_interval', self.controller.check_interval))
            
            self.controller.update_config(temp_low, temp_high, check_interval)
            
            # Redirect to main page
            self.send_redirect(client, '/')
            
        except Exception as e:
            print(f"Error processing POST: {e}")
            self.send_response(client, "400 Bad Request", "text/plain", "Invalid data")
    
    def send_response(self, client, status, content_type, body):
        """Send HTTP response"""
        try:
            print(f"Sending response: {status}, Content-Type: {content_type}")
            
            # Ensure body is properly encoded
            if isinstance(body, str):
                try:
                    body_bytes = body.encode('utf-8')
                except Exception as e:
                    print(f"Error encoding body: {e}")
                    body_bytes = body.encode()
            else:
                body_bytes = body
            
            print(f"Body length: {len(body_bytes)} bytes")
            
            # Build response with simpler format
            response_lines = [
                f"HTTP/1.1 {status}",
                f"Content-Type: {content_type}",
                f"Content-Length: {len(body_bytes)}",
                "Connection: close",
                "",
                ""
            ]
            
            response = "\r\n".join(response_lines)
            print(f"Response headers: {response}")
            
            # Send headers
            try:
                client.send(response.encode('utf-8'))
            except Exception as e:
                print(f"Error encoding/sending headers: {e}")
                client.send(response.encode())
            
            # Send body
            client.send(body_bytes)
            
            print("Response sent successfully")
            
        except Exception as e:
            print(f"Error sending response: {e}")
    
    def send_json_response(self, client, data):
        """Send JSON response"""
        try:
            print("Sending JSON response...")
            json_data = json.dumps(data)
            print(f"JSON data: {json_data}")
            self.send_response(client, "200 OK", "application/json", json_data)
        except Exception as e:
            print(f"Error sending JSON response: {e}")
            self.send_response(client, "500 Internal Server Error", "text/plain", "Error generating response")
    
    def send_redirect(self, client, location):
        """Send redirect response"""
        try:
            print(f"Sending redirect to: {location}")
            response_lines = [
                "HTTP/1.1 302 Found",
                f"Location: {location}",
                "Connection: close",
                "",
                ""
            ]
            response = "\r\n".join(response_lines)
            client.send(response.encode('utf-8'))
            print("Redirect sent successfully")
        except Exception as e:
            print(f"Error sending redirect: {e}")
    
    def send_html_response(self, client):
        """Send HTML interface"""
        try:
            print("Sending HTML response...")
            try:
                html = self.get_html_interface()
                print(f"HTML length: {len(html)} characters")
                self.send_response(client, "200 OK", "text/html", html)
            except Exception as e:
                print(f"Error in get_html_interface: {e}")
                # Send a simple error page
                error_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Error - ESP32 Temperature Controller</title>
</head>
<body>
    <h1>Error</h1>
    <p>Unable to load the temperature controller interface.</p>
    <p>Error: {e}</p>
    <p>Please try refreshing the page.</p>
</body>
</html>"""
                self.send_response(client, "500 Internal Server Error", "text/html", error_html)
        except Exception as e:
            print(f"Error sending HTML response: {e}")
            # Send a simple error page
            error_html = """<!DOCTYPE html>
<html>
<head>
    <title>Error - ESP32 Temperature Controller</title>
</head>
<body>
    <h1>Error</h1>
    <p>Unable to load the temperature controller interface.</p>
    <p>Please try refreshing the page.</p>
</body>
</html>"""
            self.send_response(client, "500 Internal Server Error", "text/html", error_html)
    
    def get_html_interface(self):
        """Get HTML interface"""
        try:
            status = self.controller.get_status()
            
            # Handle potential None values
            temp_display = f"{status['temperature']:.1f}°C" if status['temperature'] is not None else "N/A"
            relay_status = "ON" if status['relay_active'] else "OFF"
            relay_class = "on" if status['relay_active'] else "off"
            controller_status = "Running" if status['running'] else "Stopped"
            
            # Pre-format values to avoid complex f-string expressions
            temp_low_val = str(status['temp_low'])
            temp_high_val = str(status['temp_high'])
            check_interval_val = str(status['check_interval'])
            
            # Very simple HTML without complex formatting
            html = f"""<!DOCTYPE html>
<html>
<head>
    <title>ESP32 Temperature Controller</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 20px; }}
        .status {{ background: #e8f5e8; padding: 15px; margin-bottom: 20px; }}
        .form-group {{ margin-bottom: 15px; }}
        label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
        input[type="number"] {{ width: 100%; padding: 8px; border: 1px solid #ddd; }}
        button {{ background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }}
        .temp {{ font-size: 2em; font-weight: bold; color: #007bff; }}
        .relay {{ font-size: 1.2em; font-weight: bold; }}
        .relay.on {{ color: #28a745; }}
        .relay.off {{ color: #dc3545; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>ESP32 Temperature Controller</h1>
        
        <div class="status">
            <h2>Current Status</h2>
            <p><strong>Temperature:</strong> <span class="temp">{temp_display}</span></p>
            <p><strong>Relay:</strong> <span class="relay {relay_class}">{relay_status}</span></p>
            <p><strong>Controller:</strong> {controller_status}</p>
        </div>
        
        <form method="POST">
            <h2>Configuration</h2>
            
            <div class="form-group">
                <label for="temp_low">Temperature Low (activate relay):</label>
                <input type="number" id="temp_low" name="temp_low" step="0.1" value="{temp_low_val}" required>
            </div>

            <div class="form-group">
                <label for="temp_high">Temperature High (deactivate relay):</label>
                <input type="number" id="temp_high" name="temp_high" step="0.1" value="{temp_high_val}" required>
            </div>

            <div class="form-group">
                <label for="check_interval">Check Interval (seconds):</label>
                <input type="number" id="check_interval" name="check_interval" min="1" value="{check_interval_val}" required>
            </div>
            
            <button type="submit">Save Configuration</button>
        </form>
        
        <div style="margin-top: 20px; text-align: center;">
            <button onclick="location.reload()">Refresh Status</button>
        </div>
    </div>
    
    <script>
        setTimeout(function() {{
            location.reload();
        }}, 30000);
    </script>
</body>
</html>"""
            
            print(f"Generated HTML successfully, length: {len(html)}")
            return html
        except Exception as e:
            print(f"Error generating HTML: {e}")
            # Return a very simple fallback HTML
            return """<!DOCTYPE html>
<html>
<head>
    <title>ESP32 Temperature Controller</title>
</head>
<body>
    <h1>ESP32 Temperature Controller</h1>
    <p>Unable to load status. Please refresh the page.</p>
</body>
</html>"""

def main():
    """Main function"""
    print("=== ESP32 Temperature Controller ===")
    print("Starting up...")
    
    try:
        # Create controller
        controller = ESP32TemperatureController()
        
        # Start control loop
        controller.start_control_loop()
        
        # Start web server
        server = WebServer(controller)
        server.start()
        
    except Exception as e:
        print(f"Fatal error: {e}")
        import sys
        sys.exit(1)

if __name__ == "__main__":
    main() 
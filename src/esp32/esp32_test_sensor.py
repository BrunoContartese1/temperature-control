#!/usr/bin/env python3
"""
ESP32 DS18B20 Sensor Test Script
Use this to test if your DS18B20 sensor is working correctly

Hardware:
- DS18B20 sensor connected to GPIO4
- 4.7kΩ pull-up resistor between VCC and Data pin
"""

import time
from machine import Pin
import onewire
import ds18x20

# Configuration
DS18B20_PIN = 4
READ_INTERVAL = 2  # seconds

def test_ds18b20():
    """Test DS18B20 sensor functionality"""
    print("=== DS18B20 Sensor Test ===")
    
    try:
        # Setup OneWire bus
        print("Setting up OneWire bus on GPIO4...")
        ow = onewire.OneWire(Pin(DS18B20_PIN))
        ds = ds18x20.DS18X20(ow)
        
        # Scan for devices
        print("Scanning for DS18B20 devices...")
        roms = ds.scan()
        
        if not roms:
            print("ERROR: No DS18B20 devices found!")
            print("Check your wiring:")
            print("  - VCC → 3.3V")
            print("  - Data → GPIO4 (with 4.7kΩ pull-up resistor)")
            print("  - GND → GND")
            return False
        
        print(f"Found {len(roms)} DS18B20 device(s):")
        for i, rom in enumerate(roms):
            print(f"  Device {i+1}: {rom}")
        
        # Test temperature readings
        print("\nStarting temperature readings...")
        print("Press Ctrl+C to stop")
        
        while True:
            try:
                # Start temperature conversion
                ds.convert_temp()
                
                # Wait for conversion (750ms minimum)
                time.sleep_ms(750)
                
                # Read temperature
                temp = ds.read_temp(roms[0])
                
                if temp is not None:
                    print(f"Temperature: {temp:.2f}°C")
                else:
                    print("ERROR: Failed to read temperature")
                
                time.sleep(READ_INTERVAL)
                
            except KeyboardInterrupt:
                print("\nTest stopped by user")
                break
            except Exception as e:
                print(f"Error reading temperature: {e}")
                time.sleep(READ_INTERVAL)
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_relay():
    """Test relay functionality"""
    print("\n=== Relay Test ===")
    
    try:
        # Setup relay pin
        relay_pin = Pin(5, Pin.OUT)
        
        print("Testing relay on GPIO5...")
        print("Relay will turn ON for 2 seconds, then OFF for 2 seconds")
        print("Press Ctrl+C to stop")
        
        while True:
            try:
                # Turn relay ON
                print("Relay: ON")
                relay_pin.value(1)
                time.sleep(2)
                
                # Turn relay OFF
                print("Relay: OFF")
                relay_pin.value(0)
                time.sleep(2)
                
            except KeyboardInterrupt:
                print("\nRelay test stopped by user")
                relay_pin.value(0)  # Ensure relay is OFF
                break
            except Exception as e:
                print(f"Error controlling relay: {e}")
                break
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    """Main test function"""
    print("ESP32 Hardware Test")
    print("===================")
    
    # Test sensor
    sensor_ok = test_ds18b20()
    
    if sensor_ok:
        print("\n✅ DS18B20 sensor test PASSED")
    else:
        print("\n❌ DS18B20 sensor test FAILED")
    
    # Ask if user wants to test relay
    try:
        response = input("\nTest relay? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            relay_ok = test_relay()
            if relay_ok:
                print("\n✅ Relay test PASSED")
            else:
                print("\n❌ Relay test FAILED")
    except:
        print("Skipping relay test")

if __name__ == "__main__":
    main() 
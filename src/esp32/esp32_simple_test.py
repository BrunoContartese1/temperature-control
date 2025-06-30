#!/usr/bin/env python3
"""
Simple ESP32 Test Script
Tests basic functionality and WiFi access point
"""

import network
import time

print("=== ESP32 Simple Test ===")

# Test WiFi Access Point
print("Setting up WiFi Access Point...")

try:
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    
    # Configure access point
    ap.config(
        essid="TempController",
        password="temp123456",
        channel=1
    )
    
    # Wait for access point to be active
    while not ap.active():
        time.sleep(0.1)
    
    print("WiFi Access Point started successfully!")
    print(f"SSID: TempController")
    print(f"Password: temp123456")
    print(f"IP Address: {ap.ifconfig()[0]}")
    
    # Keep running
    while True:
        print("Access point is running...")
        time.sleep(5)
        
except Exception as e:
    print(f"Error: {e}")
    import sys
    sys.exit(1) 
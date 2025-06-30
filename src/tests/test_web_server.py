#!/usr/bin/env python3
"""
Test script for ESP32 Temperature Controller Web Interface
This script can be used to test if the web server is responding correctly
"""

import requests
import json
import time

def test_esp32_web_interface():
    """Test the ESP32 web interface"""
    base_url = "http://192.168.4.1"
    
    print("=== Testing ESP32 Temperature Controller Web Interface ===")
    print(f"Testing URL: {base_url}")
    print()
    
    try:
        # Test 1: Basic HTML page
        print("1. Testing main page...")
        response = requests.get(base_url, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
        print(f"   Content Length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            print("   ✓ Main page loaded successfully")
        else:
            print("   ✗ Main page failed to load")
        
        print()
        
        # Test 2: API status endpoint
        print("2. Testing API status endpoint...")
        response = requests.get(f"{base_url}/api/status", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("   ✓ Status API working")
                print(f"   Temperature: {data.get('temperature', 'N/A')}")
                print(f"   Relay: {data.get('relay_active', 'N/A')}")
                print(f"   Controller Running: {data.get('running', 'N/A')}")
            except json.JSONDecodeError:
                print("   ✗ Status API returned invalid JSON")
        else:
            print("   ✗ Status API failed")
        
        print()
        
        # Test 3: API config endpoint
        print("3. Testing API config endpoint...")
        response = requests.get(f"{base_url}/api/config", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("   ✓ Config API working")
                print(f"   Temp Low: {data.get('temp_low', 'N/A')}")
                print(f"   Temp High: {data.get('temp_high', 'N/A')}")
                print(f"   Check Interval: {data.get('check_interval', 'N/A')}")
            except json.JSONDecodeError:
                print("   ✗ Config API returned invalid JSON")
        else:
            print("   ✗ Config API failed")
        
        print()
        print("=== Test completed ===")
        
    except requests.exceptions.ConnectionError:
        print("✗ Connection failed - ESP32 not reachable")
        print("Please check:")
        print("  1. ESP32 is powered on")
        print("  2. You're connected to WiFi network 'TempController'")
        print("  3. ESP32 IP address is 192.168.4.1")
    except requests.exceptions.Timeout:
        print("✗ Request timeout - ESP32 not responding")
    except Exception as e:
        print(f"✗ Test failed with error: {e}")

if __name__ == "__main__":
    test_esp32_web_interface() 
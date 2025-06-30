#!/usr/bin/env python3
"""
Check ESP32 Temperature Controller Status
This script checks if the ESP32 is running and accessible
"""

import ampy.files
import ampy.pyboard
import time
import sys

def check_esp32_status(port="/dev/ttyACM0", baud=115200):
    """Check if ESP32 temperature controller is running"""
    print("=== Checking ESP32 Temperature Controller Status ===")
    print(f"Port: {port}")
    print(f"Baud: {baud}")
    print()
    
    try:
        # Connect to ESP32
        print("1. Connecting to ESP32...")
        board = ampy.pyboard.Pyboard(port, baud)
        print("   ✓ Connected to ESP32")
        
        # Check if main.py exists
        print("2. Checking if main.py exists...")
        files = ampy.files.Files(board)
        file_list = files.ls()
        
        if 'main.py' in file_list:
            print("   ✓ main.py found")
        else:
            print("   ✗ main.py not found - application not uploaded")
            return False
        
        if 'boot.py' in file_list:
            print("   ✓ boot.py found")
        else:
            print("   ✗ boot.py not found")
        
        print()
        
        # Check if application is running
        print("3. Checking if application is running...")
        try:
            # Try to get a simple response
            result = board.exec_raw("print('ESP32 Temperature Controller is running')")
            if result:
                print("   ✓ Application appears to be running")
            else:
                print("   ⚠ Application may not be fully started")
        except Exception as e:
            print(f"   ✗ Error checking application status: {e}")
        
        print()
        
        # Check WiFi status
        print("4. Checking WiFi status...")
        try:
            result = board.exec_raw("""
import network
ap = network.WLAN(network.AP_IF)
if ap.active():
    print(f"WiFi AP active: {ap.config('essid')}")
    print(f"IP Address: {ap.ifconfig()[0]}")
else:
    print("WiFi AP not active")
""")
            if result:
                print("   ✓ WiFi status checked")
        except Exception as e:
            print(f"   ✗ Error checking WiFi: {e}")
        
        print()
        print("=== Status check completed ===")
        return True
        
    except Exception as e:
        print(f"✗ Failed to connect to ESP32: {e}")
        print("Please check:")
        print("  1. ESP32 is connected via USB")
        print("  2. Correct port is specified")
        print("  3. ESP32 is powered on")
        return False

def main():
    """Main function"""
    port = "/dev/ttyACM0"
    
    # Check command line arguments
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    success = check_esp32_status(port)
    
    if success:
        print("\nNext steps:")
        print("  1. Connect to WiFi network 'TempController' (password: temp123456)")
        print("  2. Open web browser and go to http://192.168.4.1")
        print("  3. If web interface doesn't work, try the test script:")
        print("     python3 test_web_server.py")
    else:
        print("\nTroubleshooting:")
        print("  1. Check USB connection")
        print("  2. Try different port (e.g., /dev/ttyUSB1)")
        print("  3. Re-upload the application:")
        print("     ./esp32_upload.sh --upload")

if __name__ == "__main__":
    main() 
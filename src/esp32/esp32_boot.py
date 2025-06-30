# ESP32 Boot Script
# This file runs automatically when the ESP32 starts up

import gc
import sys
import time

# Enable garbage collection
gc.enable()

# Print startup information
print("=== ESP32 Temperature Controller Boot ===")
print(f"MicroPython version: {sys.version}")
print("Starting temperature controller...")

# Wait a moment for system to stabilize
time.sleep(2)

# Import and run the main application
try:
    import main
    print("Temperature controller started successfully")
except Exception as e:
    print(f"Error starting temperature controller: {e}")
    print("Please check the hardware connections and try again") 
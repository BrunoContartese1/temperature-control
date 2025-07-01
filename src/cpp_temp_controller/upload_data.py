#!/usr/bin/env python3
"""
Upload script for ESP32 Temperature Controller web interface
Uploads HTML, CSS, and JavaScript files to ESP32's SPIFFS filesystem
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def find_esptool():
    """Find esptool installation"""
    # Try to find esptool in the current environment
    try:
        # First try to use the virtual environment's Python
        if os.path.exists('.venv/bin/python'):
            result = subprocess.run(['.venv/bin/python', '-m', 'esptool', 'version'], 
                                  capture_output=True, text=True, check=True)
            return '.venv/bin/python -m esptool'
        elif os.path.exists('venv/bin/python'):
            result = subprocess.run(['venv/bin/python', '-m', 'esptool', 'version'], 
                                  capture_output=True, text=True, check=True)
            return 'venv/bin/python -m esptool'
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Try system esptool
    try:
        result = subprocess.run(['esptool', 'version'], capture_output=True, text=True, check=True)
        return 'esptool'
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Try esptool.py
    try:
        result = subprocess.run(['esptool.py', 'version'], capture_output=True, text=True, check=True)
        return 'esptool.py'
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    return None

def find_mkspiffs():
    """Find mkspiffs tool"""
    # Try common locations
    mkspiffs_paths = [
        'mkspiffs',
        'mkspiffs.exe',
        '/usr/local/bin/mkspiffs',
        '/usr/bin/mkspiffs',
        'tools/mkspiffs',
        'tools/mkspiffs.exe'
    ]
    
    for path in mkspiffs_paths:
        try:
            result = subprocess.run([path, '--version'], capture_output=True, text=True, check=True)
            return path
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    return None

def parse_size(size_str):
    """Convert human-readable size to bytes"""
    size_str = size_str.upper().strip()
    
    # Handle different size units
    if size_str.endswith('KB'):
        return int(size_str[:-2]) * 1024
    elif size_str.endswith('MB'):
        return int(size_str[:-2]) * 1024 * 1024
    elif size_str.endswith('GB'):
        return int(size_str[:-2]) * 1024 * 1024 * 1024
    else:
        # Assume bytes if no unit specified
        return int(size_str)

def create_spiffs_image(data_dir, output_file, partition_size="1MB"):
    """Create SPIFFS image from data directory"""
    mkspiffs = find_mkspiffs()
    if not mkspiffs:
        print("❌ mkspiffs tool not found!")
        print("Please install mkspiffs:")
        print("  - Download from: https://github.com/igrr/mkspiffs/releases")
        print("  - Or build from source: https://github.com/igrr/mkspiffs")
        return False
    
    # Convert partition size to bytes
    try:
        size_bytes = parse_size(partition_size)
    except ValueError:
        print(f"❌ Invalid partition size format: {partition_size}")
        print("Supported formats: 1MB, 512KB, 2MB, etc.")
        return False
    
    print(f"📦 Creating SPIFFS image: {output_file}")
    print(f"   Source: {data_dir}")
    print(f"   Size: {partition_size} ({size_bytes:,} bytes)")
    
    try:
        cmd = [
            mkspiffs,
            '-c', data_dir,
            '-s', str(size_bytes),
            '-p', '256',
            output_file
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ SPIFFS image created successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating SPIFFS image: {e}")
        print(f"Command output: {e.stdout}")
        print(f"Error output: {e.stderr}")
        return False

def upload_spiffs_image(image_file, port, baud_rate=115200):
    """Upload SPIFFS image to ESP32"""
    esptool = find_esptool()
    if not esptool:
        print("❌ esptool not found!")
        print("Please install esptool:")
        print("  pip install esptool")
        return False
    
    print(f"📤 Uploading SPIFFS image to ESP32")
    print(f"   Port: {port}")
    print(f"   Baud rate: {baud_rate}")
    print(f"   Image: {image_file}")
    
    try:
        cmd = esptool.split() + [
            '--chip', 'esp32',
            '--port', port,
            '--baud', str(baud_rate),
            'write_flash',
            '--no-compress',  # Disable compression
            '0x290000',  # SPIFFS partition offset
            image_file
        ]
        
        result = subprocess.run(cmd, check=True)
        print("✅ SPIFFS image uploaded successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error uploading SPIFFS image: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Upload web interface to ESP32')
    parser.add_argument('--port', '-p', default='/dev/ttyACM0', 
                       help='Serial port (default: /dev/ttyACM0)')
    parser.add_argument('--baud', '-b', type=int, default=115200,
                       help='Baud rate (default: 115200)')
    parser.add_argument('--partition-size', default='1441792',
                       help='SPIFFS partition size in bytes (default: 1441792)')
    parser.add_argument('--data-dir', default='data',
                       help='Data directory (default: data)')
    parser.add_argument('--image-file', default='spiffs.bin',
                       help='Output image file (default: spiffs.bin)')
    parser.add_argument('--skip-upload', action='store_true',
                       help='Skip upload, only create image')
    
    args = parser.parse_args()
    
    # Check if data directory exists
    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        print(f"❌ Data directory not found: {data_dir}")
        return 1
    
    print("🚀 ESP32 Temperature Controller - Web Interface Upload")
    print("=" * 60)
    
    # Create SPIFFS image
    if not create_spiffs_image(str(data_dir), args.image_file, args.partition_size):
        return 1
    
    # Upload if not skipped
    if not args.skip_upload:
        if not upload_spiffs_image(args.image_file, args.port, args.baud):
            return 1
    
    print("\n🎉 Upload completed successfully!")
    print(f"📱 Connect to WiFi: TempController (password: temp123456)")
    print(f"🌐 Open browser: http://192.168.4.1")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
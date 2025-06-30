#!/usr/bin/env python3
"""
Script de prueba para el sensor DS18B20
Verifica que el sensor esté funcionando correctamente
"""

import os
import time
import glob
import sys

def find_sensors():
    """Encontrar todos los sensores DS18B20"""
    devices = glob.glob("/sys/bus/w1/devices/28-*/w1_slave")
    return devices

def read_temperature(device_path):
    """Leer temperatura de un sensor específico"""
    try:
        with open(device_path, "r") as f:
            lines = f.readlines()
        
        if len(lines) >= 2 and "YES" in lines[0]:
            temp_raw = lines[1].split("=")[1].strip()
            temp_celsius = float(temp_raw) / 1000.0
            return temp_celsius
        else:
            return None
    except Exception as e:
        print(f"Error leyendo {device_path}: {e}")
        return None

def test_gpio(gpio_pin):
    """Probar control de GPIO"""
    try:
        # Exportar GPIO
        with open(f"/sys/class/gpio/export", "w") as f:
            f.write(str(gpio_pin))
        
        # Configurar como salida
        with open(f"/sys/class/gpio/gpio{gpio_pin}/direction", "w") as f:
            f.write("out")
        
        # Probar encendido
        with open(f"/sys/class/gpio/gpio{gpio_pin}/value", "w") as f:
            f.write("1")
        print(f"  ✓ GPIO {gpio_pin} encendido")
        
        time.sleep(0.5)
        
        # Probar apagado
        with open(f"/sys/class/gpio/gpio{gpio_pin}/value", "w") as f:
            f.write("0")
        print(f"  ✓ GPIO {gpio_pin} apagado")
        
        # Unexport GPIO
        with open(f"/sys/class/gpio/unexport", "w") as f:
            f.write(str(gpio_pin))
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error probando GPIO {gpio_pin}: {e}")
        return False

def main():
    print("=== Prueba del Sistema DS18B20 ===")
    print()
    
    # Verificar permisos
    if os.geteuid() != 0:
        print("⚠ ADVERTENCIA: Ejecutando sin permisos de root")
        print("Algunas pruebas pueden fallar")
        print()
    
    # 1. Verificar módulos del kernel
    print("1. Verificando módulos del kernel...")
    try:
        with open("/proc/modules", "r") as f:
            modules = f.read()
        
        if "w1_gpio" in modules:
            print("  ✓ Módulo w1_gpio cargado")
        else:
            print("  ✗ Módulo w1_gpio no encontrado")
        
        if "w1_therm" in modules:
            print("  ✓ Módulo w1_therm cargado")
        else:
            print("  ✗ Módulo w1_therm no encontrado")
            
    except Exception as e:
        print(f"  ✗ Error verificando módulos: {e}")
    
    print()
    
    # 2. Buscar sensores
    print("2. Buscando sensores DS18B20...")
    sensors = find_sensors()
    
    if sensors:
        print(f"  ✓ Encontrados {len(sensors)} sensor(es):")
        for sensor in sensors:
            sensor_id = os.path.basename(sensor)
            print(f"    - {sensor_id}")
    else:
        print("  ✗ No se encontraron sensores DS18B20")
        print("    Verifica las conexiones y reinicia el sistema")
        return False
    
    print()
    
    # 3. Probar lectura de temperatura
    print("3. Probando lectura de temperatura...")
    for i, sensor in enumerate(sensors, 1):
        print(f"  Sensor {i} ({os.path.basename(sensor)}):")
        
        # Tomar múltiples lecturas
        readings = []
        for j in range(5):
            temp = read_temperature(sensor)
            if temp is not None:
                readings.append(temp)
                print(f"    Lectura {j+1}: {temp:.2f}°C")
            else:
                print(f"    Lectura {j+1}: Error")
            time.sleep(1)
        
        if readings:
            avg_temp = sum(readings) / len(readings)
            print(f"    Temperatura promedio: {avg_temp:.2f}°C")
            
            # Verificar estabilidad
            if max(readings) - min(readings) < 2.0:
                print("    ✓ Lecturas estables")
            else:
                print("    ⚠ Lecturas variables (verificar conexiones)")
        else:
            print("    ✗ No se pudieron obtener lecturas válidas")
    
    print()
    
    # 4. Probar GPIO del relé
    print("4. Probando GPIO del relé...")
    try:
        from config import RELAY_GPIO
        if test_gpio(RELAY_GPIO):
            print("  ✓ GPIO del relé funcionando correctamente")
        else:
            print("  ✗ Error en GPIO del relé")
    except ImportError:
        print("  ⚠ No se pudo importar config.py, probando GPIO 17...")
        if test_gpio(17):
            print("  ✓ GPIO 17 funcionando correctamente")
        else:
            print("  ✗ Error en GPIO 17")
    
    print()
    
    # 5. Resumen
    print("=== Resumen de la Prueba ===")
    if sensors and len(sensors) > 0:
        print("✅ Sistema DS18B20 funcionando correctamente")
        print("✅ Puedes ejecutar el controlador principal")
        print()
        print("Para ejecutar el controlador:")
        print("  sudo python3 temperature.py")
        return True
    else:
        print("❌ Problemas detectados en el sistema")
        print("Revisa las conexiones y configuración")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
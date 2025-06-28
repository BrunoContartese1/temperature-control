#!/usr/bin/env python3
"""
Controlador de temperatura con sensor DS18B20 y relé
Raspberry Pi - Control de temperatura automático

Configuración:
- Sensor DS18B20 conectado en GPIO1 (modo 1-wire)
- Relé de 5V conectado en GPIO17
- Temperaturas configurables para activar/desactivar el relé
- Monitoreo continuo con intervalo configurable
"""

import os
import time
import signal
import sys
from typing import Optional
import logging

# Importar configuración
try:
    from config import *
except ImportError:
    print("Error: No se pudo importar config.py")
    print("Asegúrate de que el archivo config.py esté en el mismo directorio")
    sys.exit(1)

# Configuración de logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TemperatureController:
    def __init__(self, 
                 temp_low: float = TEMP_LOW,
                 temp_high: float = TEMP_HIGH,
                 check_interval: int = CHECK_INTERVAL,
                 relay_gpio: int = RELAY_GPIO,
                 sensor_path: str = SENSOR_PATH,
                 relay_active_low: bool = RELAY_ACTIVE_LOW,
                 max_temp: float = MAX_TEMP,
                 min_temp: float = MIN_TEMP):
        
        self.temp_low = temp_low
        self.temp_high = temp_high
        self.check_interval = check_interval
        self.relay_gpio = relay_gpio
        self.sensor_path = sensor_path
        self.relay_active_low = relay_active_low
        self.max_temp = max_temp
        self.min_temp = min_temp
        self.running = False
        self.relay_active = False
        
        # Validar configuración
        self._validate_config()
        
        # Configurar GPIO para el relé
        self._setup_gpio()
        
        # Encontrar el sensor DS18B20
        self.sensor_device = self._find_sensor()
        if not self.sensor_device:
            raise RuntimeError("No se pudo encontrar el sensor DS18B20")
        
        logger.info(f"Controlador inicializado:")
        logger.info(f"  - Temperatura baja (activar): {self.temp_low}°C")
        logger.info(f"  - Temperatura alta (desactivar): {self.temp_high}°C")
        logger.info(f"  - Intervalo de verificación: {self.check_interval} segundos")
        logger.info(f"  - GPIO del relé: {self.relay_gpio}")
        logger.info(f"  - Relé activo en bajo: {self.relay_active_low}")
        logger.info(f"  - Sensor encontrado: {self.sensor_device}")
    
    def _validate_config(self):
        """Validar la configuración"""
        if self.temp_low >= self.temp_high:
            raise ValueError("TEMP_LOW debe ser menor que TEMP_HIGH")
        
        if self.check_interval < 1:
            raise ValueError("CHECK_INTERVAL debe ser al menos 1 segundo")
        
        if self.relay_gpio not in range(1, 28):  # GPIO válidos en Raspberry Pi
            raise ValueError("RELAY_GPIO debe estar entre 1 y 27")
        
        if self.max_temp <= self.min_temp:
            raise ValueError("MAX_TEMP debe ser mayor que MIN_TEMP")
    
    def _setup_gpio(self):
        """Configurar GPIO para el relé"""
        try:
            # Exportar el GPIO
            with open(f"/sys/class/gpio/export", "w") as f:
                f.write(str(self.relay_gpio))
            
            # Configurar como salida
            with open(f"/sys/class/gpio/gpio{self.relay_gpio}/direction", "w") as f:
                f.write("out")
            
            # Inicializar en estado apagado
            self._set_relay(False)
            
            logger.info(f"GPIO {self.relay_gpio} configurado correctamente")
            
        except Exception as e:
            logger.error(f"Error configurando GPIO {self.relay_gpio}: {e}")
            raise
    
    def _find_sensor(self) -> Optional[str]:
        """Encontrar el dispositivo del sensor DS18B20"""
        try:
            import glob
            devices = glob.glob(self.sensor_path)
            if devices:
                return devices[0]
            else:
                logger.error("No se encontraron dispositivos DS18B20")
                return None
        except Exception as e:
            logger.error(f"Error buscando sensor DS18B20: {e}")
            return None
    
    def _read_temperature(self) -> Optional[float]:
        """Leer temperatura del sensor DS18B20"""
        try:
            with open(self.sensor_device, "r") as f:
                lines = f.readlines()
            
            if len(lines) >= 2:
                # Verificar que la lectura sea válida
                if "YES" in lines[0]:
                    # Extraer temperatura (está en milicelsius)
                    temp_line = lines[1]
                    temp_raw = temp_line.split("=")[1].strip()
                    temp_celsius = float(temp_raw) / 1000.0
                    
                    # Validar rango de temperatura
                    if self.min_temp <= temp_celsius <= self.max_temp:
                        return temp_celsius
                    else:
                        logger.warning(f"Temperatura fuera de rango: {temp_celsius:.1f}°C (rango: {self.min_temp}°C - {self.max_temp}°C)")
                        return None
                else:
                    logger.warning("Lectura del sensor no válida")
                    return None
            else:
                logger.warning("Formato de lectura del sensor incorrecto")
                return None
                
        except Exception as e:
            logger.error(f"Error leyendo temperatura: {e}")
            return None
    
    def _set_relay(self, active: bool):
        """Activar o desactivar el relé"""
        try:
            # Aplicar lógica del relé (activo en bajo o alto)
            if self.relay_active_low:
                value = "0" if active else "1"
            else:
                value = "1" if active else "0"
            
            with open(f"/sys/class/gpio/gpio{self.relay_gpio}/value", "w") as f:
                f.write(value)
            
            self.relay_active = active
            status = "ACTIVADO" if active else "DESACTIVADO"
            logger.info(f"Relé {status}")
            
        except Exception as e:
            logger.error(f"Error controlando relé: {e}")
    
    def _control_logic(self, temperature: float):
        """Lógica de control basada en la temperatura"""
        if temperature <= self.temp_low and not self.relay_active:
            # Temperatura baja, activar relé (calefacción)
            logger.info(f"Temperatura {temperature:.1f}°C <= {self.temp_low}°C - Activando relé")
            self._set_relay(True)
            
        elif temperature >= self.temp_high and self.relay_active:
            # Temperatura alta, desactivar relé (calefacción)
            logger.info(f"Temperatura {temperature:.1f}°C >= {self.temp_high}°C - Desactivando relé")
            self._set_relay(False)
    
    def start(self):
        """Iniciar el controlador de temperatura"""
        self.running = True
        logger.info("Iniciando controlador de temperatura...")
        
        # Configurar manejo de señales para parada elegante
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            while self.running:
                # Leer temperatura
                temperature = self._read_temperature()
                
                if temperature is not None:
                    logger.info(f"Temperatura actual: {temperature:.1f}°C")
                    self._control_logic(temperature)
                else:
                    logger.warning("No se pudo leer la temperatura")
                
                # Esperar antes de la siguiente verificación
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logger.info("Interrupción recibida, deteniendo...")
        except Exception as e:
            logger.error(f"Error en el bucle principal: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Detener el controlador"""
        self.running = False
        # Desactivar relé al salir
        self._set_relay(False)
        logger.info("Controlador detenido")
    
    def _signal_handler(self, signum, frame):
        """Manejador de señales para parada elegante"""
        logger.info(f"Señal {signum} recibida, deteniendo...")
        self.stop()
        sys.exit(0)

def main():
    """Función principal"""
    print("=== Controlador de Temperatura DS18B20 ===")
    print("Configuración actual:")
    print(f"  - Temperatura baja (activar): {TEMP_LOW}°C")
    print(f"  - Temperatura alta (desactivar): {TEMP_HIGH}°C")
    print(f"  - Intervalo de verificación: {CHECK_INTERVAL} segundos")
    print(f"  - GPIO del relé: {RELAY_GPIO}")
    print(f"  - Relé activo en bajo: {RELAY_ACTIVE_LOW}")
    print(f"  - Rango de temperatura válido: {MIN_TEMP}°C - {MAX_TEMP}°C")
    print()
    
    # Verificar que se ejecute como root (necesario para GPIO)
    if os.geteuid() != 0:
        print("ERROR: Este script debe ejecutarse como root (sudo)")
        print("Ejecuta: sudo python3 temperature.py")
        sys.exit(1)
    
    try:
        # Crear y ejecutar el controlador
        controller = TemperatureController()
        controller.start()
        
    except Exception as e:
        logger.error(f"Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

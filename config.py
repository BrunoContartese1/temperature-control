#!/usr/bin/env python3
"""
Archivo de configuración para el controlador de temperatura DS18B20
Modifica estos valores según tus necesidades
"""

# Configuración de temperaturas
TEMP_LOW = 20.0      # Temperatura para activar relé (encender calefacción) en °C
TEMP_HIGH = 25.0     # Temperatura para desactivar relé (apagar calefacción) en °C

# Configuración de hardware
RELAY_GPIO = 17      # GPIO donde está conectado el relé
CHECK_INTERVAL = 5   # Intervalo de verificación en segundos

# Configuración del sensor DS18B20
SENSOR_PATH = "/sys/bus/w1/devices/28-*/w1_slave"  # Ruta del sensor (normalmente no cambiar)

# Configuración de logging
LOG_LEVEL = "INFO"   # Nivel de logging: DEBUG, INFO, WARNING, ERROR
LOG_FILE = "temperature_control.log"  # Archivo de log

# Configuración del relé (si tu relé funciona diferente)
RELAY_ACTIVE_LOW = True  # True si el relé se activa con señal baja (0), False si se activa con señal alta (1)

# Configuración de seguridad
MAX_TEMP = 50.0      # Temperatura máxima permitida (para evitar lecturas erróneas)
MIN_TEMP = -10.0     # Temperatura mínima permitida (para evitar lecturas erróneas) 
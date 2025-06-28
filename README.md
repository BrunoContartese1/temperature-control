# Controlador de Temperatura DS18B20 para Raspberry Pi

Este proyecto implementa un controlador automático de temperatura usando un sensor DS18B20 y un relé para controlar un sistema de calefacción o refrigeración.

## Características

- ✅ Monitoreo continuo de temperatura con sensor DS18B20
- ✅ Control automático de relé basado en umbrales configurables
- ✅ Logging completo con archivo de registro
- ✅ Parada elegante con manejo de señales
- ✅ Validación de rangos de temperatura para seguridad
- ✅ Configuración flexible mediante archivo separado
- ✅ Servicio systemd para ejecución automática
- ✅ Compatible con Raspberry Pi (testeado en Raspberry Pi 4)

## Hardware Requerido

### Componentes
- **Raspberry Pi** (cualquier modelo con GPIO)
- **Sensor DS18B20** (sensor de temperatura digital)
- **Relé de 5V** (para controlar el sistema de calefacción/refrigeración)
- **Resistencia de 4.7kΩ** (pull-up para el bus 1-wire)
- **Cables de conexión**

### Conexiones

#### Sensor DS18B20
```
DS18B20    Raspberry Pi
VDD    →   3.3V (Pin 1)
GND    →   GND (Pin 6)
DQ     →   GPIO1 (Pin 3) + Resistencia 4.7kΩ a 3.3V
```

#### Relé
```
Relé       Raspberry Pi
VCC    →   5V (Pin 2)
GND    →   GND (Pin 9)
IN     →   GPIO17 (Pin 11)
```

## Instalación

### 1. Clonar o descargar el proyecto
```bash
git clone <url-del-repositorio>
cd GSLiveBettingMySQL
```

### 2. Ejecutar el script de configuración
```bash
sudo bash setup.sh
```

### 3. Reiniciar el sistema
```bash
sudo reboot
```

### 4. Verificar la instalación
```bash
# Verificar que el sensor esté detectado
ls /sys/bus/w1/devices/

# Deberías ver algo como:
# 28-00000xxxxxxx
```

## Configuración

Edita el archivo `config.py` para personalizar el comportamiento:

```python
# Configuración de temperaturas
TEMP_LOW = 20.0      # Temperatura para activar relé (°C)
TEMP_HIGH = 25.0     # Temperatura para desactivar relé (°C)

# Configuración de hardware
RELAY_GPIO = 17      # GPIO del relé
CHECK_INTERVAL = 5   # Intervalo de verificación (segundos)

# Configuración del relé
RELAY_ACTIVE_LOW = True  # True si el relé se activa con señal baja

# Configuración de seguridad
MAX_TEMP = 50.0      # Temperatura máxima permitida
MIN_TEMP = -10.0     # Temperatura mínima permitida
```

## Uso

### Ejecución manual
```bash
sudo python3 temperature.py
```

### Ejecución como servicio (recomendado)
```bash
# Habilitar el servicio
sudo systemctl enable temperature-control.service

# Iniciar el servicio
sudo systemctl start temperature-control.service

# Verificar estado
sudo systemctl status temperature-control.service

# Ver logs en tiempo real
sudo journalctl -u temperature-control.service -f
```

### Comandos útiles
```bash
# Detener el servicio
sudo systemctl stop temperature-control.service

# Reiniciar el servicio
sudo systemctl restart temperature-control.service

# Ver logs del servicio
sudo journalctl -u temperature-control.service

# Ver logs del archivo local
tail -f temperature_control.log
```

## Funcionamiento

### Lógica de Control
1. **Temperatura ≤ TEMP_LOW**: Activa el relé (enciende calefacción)
2. **Temperatura ≥ TEMP_HIGH**: Desactiva el relé (apaga calefacción)
3. **Entre TEMP_LOW y TEMP_HIGH**: Mantiene el estado actual

### Ejemplo de funcionamiento
- Si `TEMP_LOW = 20°C` y `TEMP_HIGH = 25°C`:
  - Temperatura 18°C → Relé ACTIVADO
  - Temperatura 22°C → Relé ACTIVADO (mantiene estado)
  - Temperatura 26°C → Relé DESACTIVADO
  - Temperatura 23°C → Relé DESACTIVADO (mantiene estado)

## Logs y Monitoreo

### Archivo de log
El sistema genera logs en `temperature_control.log` con información detallada:
- Lecturas de temperatura
- Cambios de estado del relé
- Errores y advertencias
- Timestamps precisos

### Ejemplo de log
```
2024-01-15 10:30:15,123 - INFO - Controlador inicializado
2024-01-15 10:30:15,124 - INFO - Temperatura actual: 22.5°C
2024-01-15 10:30:15,125 - INFO - Relé ACTIVADO
2024-01-15 10:30:20,126 - INFO - Temperatura actual: 24.8°C
2024-01-15 10:30:25,127 - INFO - Temperatura actual: 25.2°C
2024-01-15 10:30:25,128 - INFO - Relé DESACTIVADO
```

## Solución de Problemas

### Sensor no detectado
```bash
# Verificar módulos cargados
lsmod | grep w1

# Recargar módulos
sudo modprobe w1-gpio
sudo modprobe w1-therm

# Verificar dispositivos
ls /sys/bus/w1/devices/
```

### Error de permisos GPIO
```bash
# Agregar usuario al grupo gpio
sudo usermod -a -G gpio $USER

# Reiniciar sesión o ejecutar como root
sudo python3 temperature.py
```

### Temperatura fuera de rango
- Verificar conexiones del sensor
- Comprobar resistencia pull-up de 4.7kΩ
- Revisar configuración de `MIN_TEMP` y `MAX_TEMP`

### Relé no responde
- Verificar conexiones del relé
- Comprobar configuración de `RELAY_ACTIVE_LOW`
- Verificar que el GPIO esté correctamente configurado

## Personalización Avanzada

### Múltiples sensores
Para usar múltiples sensores DS18B20, modifica el código para iterar sobre todos los dispositivos:

```python
import glob
sensors = glob.glob("/sys/bus/w1/devices/28-*/w1_slave")
for sensor in sensors:
    # Leer cada sensor
    pass
```

### Control de refrigeración
Para controlar refrigeración en lugar de calefacción, invierte la lógica:

```python
# En config.py
TEMP_LOW = 25.0      # Temperatura para activar refrigeración
TEMP_HIGH = 20.0     # Temperatura para desactivar refrigeración
```

### Histeresis personalizada
Modifica la lógica de control para agregar histeresis:

```python
def _control_logic(self, temperature: float):
    if temperature <= self.temp_low - 0.5 and not self.relay_active:
        self._set_relay(True)
    elif temperature >= self.temp_high + 0.5 and self.relay_active:
        self._set_relay(False)
```

## Seguridad

- ✅ Validación de rangos de temperatura
- ✅ Parada elegante con desactivación del relé
- ✅ Manejo de errores robusto
- ✅ Logging completo para auditoría
- ✅ Configuración de permisos adecuada

## Licencia

Este proyecto está bajo licencia MIT. Ver archivo LICENSE para más detalles.

## Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## Soporte

Para soporte técnico o preguntas:
- Abre un issue en GitHub
- Consulta la documentación oficial de Raspberry Pi
- Revisa los logs del sistema para diagnóstico 
#!/bin/bash
# Script de instalación para el controlador de temperatura DS18B20
# Este script configura el sistema 1-wire en Raspberry Pi

set -e

echo "=== Configuración del Controlador de Temperatura DS18B20 ==="
echo

# Verificar si se ejecuta como root
if [ "$EUID" -ne 0 ]; then
    echo "ERROR: Este script debe ejecutarse como root (sudo)"
    echo "Ejecuta: sudo bash setup.sh"
    exit 1
fi

echo "1. Habilitando módulos 1-wire..."
# Habilitar módulos en /boot/config.txt
if ! grep -q "dtoverlay=w1-gpio" /boot/config.txt; then
    echo "dtoverlay=w1-gpio" >> /boot/config.txt
    echo "  ✓ Módulo w1-gpio agregado a /boot/config.txt"
else
    echo "  ✓ Módulo w1-gpio ya está habilitado"
fi

if ! grep -q "dtoverlay=w1-therm" /boot/config.txt; then
    echo "dtoverlay=w1-therm" >> /boot/config.txt
    echo "  ✓ Módulo w1-therm agregado a /boot/config.txt"
else
    echo "  ✓ Módulo w1-therm ya está habilitado"
fi

echo
echo "2. Cargando módulos del kernel..."
# Cargar módulos
modprobe w1-gpio
modprobe w1-therm
echo "  ✓ Módulos cargados"

echo
echo "3. Verificando sensor DS18B20..."
# Esperar un momento para que el sistema detecte el sensor
sleep 2

# Buscar dispositivos 1-wire
if ls /sys/bus/w1/devices/28-* >/dev/null 2>&1; then
    echo "  ✓ Sensor DS18B20 detectado:"
    for device in /sys/bus/w1/devices/28-*; do
        echo "    - $(basename $device)"
    done
else
    echo "  ⚠ ADVERTENCIA: No se detectó ningún sensor DS18B20"
    echo "    Verifica las conexiones y reinicia el sistema"
fi

echo
echo "4. Configurando permisos..."
# Crear grupo para acceso a GPIO
if ! getent group gpio >/dev/null 2>&1; then
    groupadd gpio
    echo "  ✓ Grupo 'gpio' creado"
fi

# Agregar usuario actual al grupo gpio
if [ -n "$SUDO_USER" ]; then
    usermod -a -G gpio $SUDO_USER
    echo "  ✓ Usuario $SUDO_USER agregado al grupo gpio"
fi

echo
echo "5. Creando script de inicio..."
# Crear script de servicio systemd
cat > /etc/systemd/system/temperature-control.service << EOF
[Unit]
Description=DS18B20 Temperature Controller
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/python3 $(pwd)/temperature.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "  ✓ Servicio systemd creado: /etc/systemd/system/temperature-control.service"

echo
echo "6. Configurando permisos de archivos..."
chmod +x temperature.py
chmod +x setup.sh
echo "  ✓ Permisos configurados"

echo
echo "=== Configuración completada ==="
echo
echo "Para completar la configuración:"
echo "1. Reinicia el sistema: sudo reboot"
echo "2. Verifica que el sensor funcione: ls /sys/bus/w1/devices/"
echo "3. Ejecuta el controlador: sudo python3 temperature.py"
echo
echo "Para habilitar el servicio automático:"
echo "  sudo systemctl enable temperature-control.service"
echo "  sudo systemctl start temperature-control.service"
echo
echo "Para ver el estado del servicio:"
echo "  sudo systemctl status temperature-control.service"
echo
echo "Para ver los logs:"
echo "  sudo journalctl -u temperature-control.service -f"
echo
echo "¡Configuración completada!" 
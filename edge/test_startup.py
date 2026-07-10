print("Starting imports...")
import sys
import os
print("Basic imports OK")

import minimalmodbus
print("minimalmodbus OK")

import paho.mqtt.client as mqtt
print("mqtt OK")

sys.path.append('/home/user1/kybfarm/edge/src/sensor_interfaces')
print("Path added")

from sensor_SPH01_modbus import SPH01
print("SPH01 imported OK")

# Try initializing one sensor
try:
    sensor = SPH01('/dev/ttySC1', 8)
    print(f"Sensor init OK, pH: {sensor.get_pH()}")
except Exception as e:
    print(f"Sensor init failed: {e}")

print("Test complete")

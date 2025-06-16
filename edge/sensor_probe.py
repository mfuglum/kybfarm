import time
import sys
from src.sensor_interfaces import (
    sensor_SYM01_modbus, 
    sensor_SLIGHT01_modbus,
    sensor_SPAR02_modbus,
    sensor_SEC01_modbus,
    sensor_SPH01_modbus,
    sensor_CO2_VOC_modbus,
    sensor_STH01_modbus
)

SENSOR_CONFIG = [
    {"name": "SLIGHT01", "class": sensor_SLIGHT01_modbus.SLIGHT01, "port": "/dev/ttySC1", "address": 1},
    {"name": "SPAR02", "class": sensor_SPAR02_modbus.SPAR02, "port": "/dev/ttySC1", "address": 34},
    {"name": "SEC01-1", "class": sensor_SEC01_modbus.SEC01, "port": "/dev/ttySC1", "address": 3},
    {"name": "SEC01-2", "class": sensor_SEC01_modbus.SEC01, "port": "/dev/ttySC1", "address": 4},
    {"name": "SPH01-1", "class": sensor_SPH01_modbus.SPH01, "port": "/dev/ttySC1", "address": 5},
    {"name": "SPH01-2", "class": sensor_SPH01_modbus.SPH01, "port": "/dev/ttySC1", "address": 6},
    {"name": "SYM01", "class": sensor_SYM01_modbus.SYM01, "port": "/dev/ttySC1", "address": 11},
    {"name": "CO2_VOC_1", "class": sensor_CO2_VOC_modbus.CO2_VOC, "port": "/dev/ttySC0", "address": 7},
    {"name": "CO2_VOC_2", "class": sensor_CO2_VOC_modbus.CO2_VOC, "port": "/dev/ttySC0", "address": 1},
    {"name": "STH01-1", "class": sensor_STH01_modbus.STH01, "port": "/dev/ttySC0", "address": 70},
    {"name": "STH01-2", "class": sensor_STH01_modbus.STH01, "port": "/dev/ttySC0", "address": 69},
]

def probe_sensors():
    print("\n🔍 Probing sensors...\n")
    results = []
    for sensor in SENSOR_CONFIG:
        name = sensor["name"]
        cls = sensor["class"]
        port = sensor["port"]
        addr = sensor["address"]
        try:
            instance = cls(portname=port, slaveaddress=addr, debug=False)
            data = instance.fetch_and_return_data()  # basic functional check
            print(f"✅ {name} connected on {port}, address {addr}")
            results.append((name, True))
        except Exception as e:
            print(f"❌ {name} not responding on {port}, address {addr}: {e}")
            results.append((name, False))
        time.sleep(0.1)

    print("\n🧾 Summary:")
    for name, success in results:
        status = "OK" if success else "NOT FOUND"
        print(f"- {name}: {status}")

if __name__ == "__main__":
    probe_sensors()
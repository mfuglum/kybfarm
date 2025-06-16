#!/usr/bin/env python3
"""Quickly check if sensors respond by fetching a single data packet from each.

This script loads the environment variables from ``.env`` and attempts to
initialize each configured sensor. The result from ``fetch_and_print_data``
provides an indication that communication is working.
"""

import sys
if "pytest" in sys.modules:
    import pytest
    pytest.skip("utility script, not a test", allow_module_level=True)

import logging
import os
from dotenv import load_dotenv

from src.sensor_interfaces import (
    sensor_BMP280_I2C,
    sensor_SCD41_I2C,
    sensor_SLIGHT01_modbus,
    sensor_SPAR02_modbus,
    sensor_SEC01_modbus,
    sensor_SPH01_modbus,
    sensor_SYM01_modbus,
)

load_dotenv()
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s: %(message)s")

RS485_PORT = os.getenv("RS485_PORT", "/dev/ttySC1")


def init_modbus_sensor(cls, addr_env):
    """Instantiate a Modbus sensor class using the provided address env var."""
    address = int(os.getenv(addr_env, 1))
    return cls(portname=RS485_PORT, slaveaddress=address, debug=False)


def main():
    sensors = {}
    modbus_sensors = [
        ("SLIGHT01", sensor_SLIGHT01_modbus.SLIGHT01, "SENSOR_SLIGHT01_ADDR"),
        ("SPAR02", sensor_SPAR02_modbus.SPAR02, "SENSOR_SPAR02_ADDR"),
        ("SEC01_1", sensor_SEC01_modbus.SEC01, "SENSOR_SEC01_1_ADDR"),
        ("SEC01_2", sensor_SEC01_modbus.SEC01, "SENSOR_SEC01_2_ADDR"),
        ("SPH01_1", sensor_SPH01_modbus.SPH01, "SENSOR_SPH01_1_ADDR"),
        ("SPH01_2", sensor_SPH01_modbus.SPH01, "SENSOR_SPH01_2_ADDR"),
        ("SYM01", sensor_SYM01_modbus.SYM01, "SENSOR_SYM01_ADDR"),
    ]

    for name, cls, env_var in modbus_sensors:
        try:
            sensors[name] = init_modbus_sensor(cls, env_var)
            logging.info("%s initialized", name)
        except Exception as e:
            logging.error("%s init failed: %s", name, e)

    # Test Modbus sensors
    for name, sensor in sensors.items():
        try:
            sensor.fetch_and_print_data()
        except Exception as e:
            logging.error("%s fetch failed: %s", name, e)

    # Test I2C sensors (module based)
    i2c_modules = [
        ("BMP280", sensor_BMP280_I2C),
        ("SCD41", sensor_SCD41_I2C),
    ]

    for name, module in i2c_modules:
        try:
            module.fetch_and_print_data()
        except Exception as e:
            logging.error("%s fetch failed: %s", name, e)


if __name__ == "__main__":
    main()
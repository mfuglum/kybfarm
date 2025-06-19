import os
import time
import importlib
import minimalmodbus

MODBUS_PORT = "/dev/ttySC0" # manually editable
ADDRESS_RANGE = range(1, 274)
WHITELIST = [69,70]  # manually editable
SENSOR_OPTIONS = [
    ("SLIGHT01", "sensor_SLIGHT01_modbus", "SLIGHT01", 1),
    ("SPAR02", "sensor_SPAR02_modbus", "SPAR02", 34),
    ("SEC01", "sensor_SEC01_modbus", "SEC01", 30),
    ("SPH01", "sensor_SPH01_modbus", "SPH01", 4),
    ("STH01", "sensor_STH01_modbus", "STH01", 13),
    ("SYM01", "sensor_SYM01_modbus", "SYM01", 11),
    ("CO2_VOC", "sensor_CO2_VOC_modbus", "CO2_VOC", 13)
]

# Scan for a sensor address (just check for Modbus response)
def scan_for_sensor():
    print(f"\n🔍 Scanning {MODBUS_PORT} for sensor (excluding whitelist)...")
    for addr in ADDRESS_RANGE:
        if addr in WHITELIST:
            continue
        try:
            dummy = minimalmodbus.Instrument(MODBUS_PORT, addr)
            dummy.serial.baudrate = 9600
            dummy.read_register(0, functioncode=3)
            print(f"Sensor detected at address {addr}")
            return addr
        except:
            continue
    print("No unregistered sensor found.")
    return None

# Main routine
def main():
    found_address = scan_for_sensor()
    if not found_address:
        return

    print("\nAvailable sensor types:")
    for idx, (label, _, _, _) in enumerate(SENSOR_OPTIONS, 1):
        print(f"  {idx}. {label}")

    while True:
        try:
            choice = int(input("Select sensor type [1-{}]: ".format(len(SENSOR_OPTIONS))))
            if 1 <= choice <= len(SENSOR_OPTIONS):
                break
        except:
            pass
        print("Invalid choice. Try again.")

    label, module_name, class_name, default_address = SENSOR_OPTIONS[choice - 1]
    module = importlib.import_module(f"src.sensor_interfaces.{module_name}")
    cls = getattr(module, class_name)
    sensor = cls(portname=MODBUS_PORT, slaveaddress=found_address, debug=False)

    print("\nWhat would you like to do?")
    print("  1. Reset to default address")
    print("  2. Change to new custom address")
    print("  3. Nothing")
    action = input("Enter choice [1-2]: ").strip()

    if action == "1":
        try:
            sensor.set_slave_address(default_address)
            print(f" Address reset to default: {default_address}")
        except Exception as e:
            print("Failed to reset address:", e)

    elif action == "2":
        new_addr = input("Enter new address to assign: ")
        try:
            new_addr = int(new_addr.strip())

            if label == "SPAR02":
                print("Using broadcast mode to change SPAR02 address...")
                broadcast = minimalmodbus.Instrument(MODBUS_PORT, 0)
                broadcast.serial.baudrate = 9600
                broadcast.write_register(0x0001, new_addr, functioncode=6)
                print(f" Broadcast command sent. Power cycle the sensor to finalize address {new_addr}.")
            else:
                sensor.set_slave_address(new_addr)
                print(f" address changed to {new_addr}")

        except Exception as e:
            print(" Failed to change address:", e)

if __name__ == "__main__":
    main()

import time
# Make sure the path to your custom library is correct
# If the library is in the same folder, this is fine.
# Otherwise, you might need to adjust sys.path.
import sensor_CO2_VOC_modbus # Your library for this sensor

PORT = '/dev/ttySC0'
MYSTERY_ADDRESS = 1

print(f"🕵️  Attempting to communicate with device at address {MYSTERY_ADDRESS} on {PORT}...")
print(f"    Treating it as a CO2_VOC sensor...")

try:
    # Initialize the sensor object pointing to the mystery address
    mystery_sensor = sensor_CO2_VOC_modbus.CO2_VOC(portname=PORT,
                                                  slaveaddress=MYSTERY_ADDRESS)

    # Try to read a value using a method from your library
    # Replace 'read_co2()' with a real method that reads a value.
    # Look inside sensor_CO2_VOC_modbus.py to find a method name.
    # Common names might be get_co2, get_voc, read_value, etc.
    co2_value = mystery_sensor.read_co2() #<-- CHANGE THIS METHOD NAME IF NEEDED

    print("\n" + "="*40)
    print("✅  SUCCESS! Communication established.")
    print(f"    The device at address {MYSTERY_ADDRESS} responded like a CO2_VOC sensor.")
    print(f"    Read CO2 value: {co2_value}")
    print("    This is very likely your missing CO2_VOC_2 sensor!")
    print("="*40)

except Exception as e:
    print("\n" + "!"*40)
    print(f"❌  FAILED. The device at address {MYSTERY_ADDRESS} did not respond as expected.")
    print(f"    It is likely NOT a CO2_VOC sensor, or there was another error.")
    print(f"    Error details: {e}")
    print("!"*40)
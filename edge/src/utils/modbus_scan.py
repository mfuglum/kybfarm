import minimalmodbus
import serial

PORT = '/dev/ttySC1'  # Adjust if needed
BAUDRATE = 9600        # Match your sensor
REGISTER = 0           # Try reading register 0
SLAVE_ID_RANGE = range(1, 248)

def scan():
    print("Scanning Modbus addresses...")
    for slave_id in SLAVE_ID_RANGE:
        try:
            instrument = minimalmodbus.Instrument(PORT, slave_id)
            instrument.serial.baudrate = BAUDRATE
            instrument.serial.timeout = 0.3
            instrument.mode = minimalmodbus.MODE_RTU

            value = instrument.read_register(REGISTER, 0)
            print(f"✅ Found device at address {slave_id}: Register {REGISTER} = {value}")
        except IOError:
            pass  # No response
        except Exception as e:
            print(f"⚠️ Address {slave_id} error: {e}")

scan()

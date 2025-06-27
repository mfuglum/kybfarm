import minimalmodbus
import json
import serial

class Fan(minimalmodbus.Instrument):
    """
    Modbus RTU class for 0–10V Analog Output Fan (Channel 1).

    Assumes usage with Seeed Studio RS485 8-Channel Analog Output Module
    connected to channel 1 (register 0x08).

    Args:
        portname (str):              Serial port, e.g. '/dev/ttySC0'
        slaveaddress (int):         Modbus slave address
        mode (int):                 Communication mode (default: RTU)
        close_port_after_each_call (bool): Close port after each call (default: False)
        debug (bool):               Enable debug logging

    Modbus registers:
        0x08 (DEC 8): Output voltage (0–10000 for 0.0V to 10.0V)
    """

    def __init__(self,
                 portname="/dev/ttySC0",
                 slaveaddress=1,
                 mode=minimalmodbus.MODE_RTU,
                 close_port_after_each_call=False,
                 debug=False):
        super().__init__(portname, slaveaddress, mode, close_port_after_each_call, debug)
        self.serial.baudrate = 9600
        self.address = slaveaddress
        self.current_voltage = 0.0

    def set_voltage(self, voltage):
        """Sets the fan output voltage [0–10V]."""
        clamped = max(0.0, min(10.0, voltage))
        raw_value = int(clamped * 1000)
        try:
            self.write_register(0x08, raw_value, 0, 6, signed=False)
            self.current_voltage = clamped
        except Exception as e:
            print("Fan Modbus write error:", e)

    def read_voltage_raw(self):
        """Reads the raw 0–10000 value from the fan output register."""
        try:
            return self.read_register(0x08, 0, 3, signed=False)
        except Exception as e:
            print("Fan Modbus read error:", e)
            return None

    def get_slave_address(self):
        try:
            return self.read_register(512, 0, 3, signed=False)
        except Exception as e:
            print("Error reading slave address:", e)
            return None

    def set_slave_address(self, new_address):
        try:
            self.write_register(512, new_address, 0, 6, signed=False)
            self.address = new_address
        except Exception as e:
            print("Error setting slave address:", e)

    def on_message(self, client, userdata, msg):
        """MQTT handler to receive voltage command."""
        try:
            payload = json.loads(msg.payload)
            print(f"[FAN] Received MQTT message on {msg.topic}: {payload}")
            if payload.get("cmd") == "adjust":
                self.set_voltage(float(payload["value"]))
                client.publish(payload["res_topic"], json.dumps(self.current_voltage))
            else:
                print("Invalid command for fan.")
        except Exception as e:
            print("MQTT error in Fan:", e)

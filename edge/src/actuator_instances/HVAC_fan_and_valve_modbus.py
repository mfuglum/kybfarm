import json
import serial
import minimalmodbus
import paho.mqtt.client as mqtt
from modbus_tk import modbus_rtu
import modbus_tk.defines as cst

# ─────────────────────────────────────────────────────────────
# Shared ModbusWriter to coordinate fan + valve writes
# ─────────────────────────────────────────────────────────────
class ModbusWriter:
    def __init__(self, port="/dev/ttySC0", slave_address=1):
        self.slave_address = slave_address
        self.output = [0, 0]  # [valve, fan]
        self.master = modbus_rtu.RtuMaster(serial.Serial(
            port=port, baudrate=9600, bytesize=8, parity='N', stopbits=1
        ))
        self.master.set_timeout(2.0)
        self.master.set_verbose(True)

    def update_output(self, channel: int, raw_value: int):
        self.output[channel] = raw_value
        self.write_all()

    def write_all(self):
        try:
            self.master.execute(self.slave_address, cst.WRITE_MULTIPLE_REGISTERS, 0x00, 0x08, output_value=self.output)
            print(f"[MODBUS WRITE] Valve: {self.output[0]}  Fan: {self.output[1]}")
        except Exception as e:
            print("Modbus write error:", e)

# Shared instance
modbus_writer = ModbusWriter()

# ─────────────────────────────────────────────────────────────
# Valve Class – Controls channel 0
# ─────────────────────────────────────────────────────────────
class Valve:
    def __init__(self):
        self.current_voltage = 0.0

    def set_voltage(self, voltage):
        clamped = max(0.0, min(10.0, voltage))
        raw_value = int(clamped * 1000)
        modbus_writer.update_output(0, raw_value)
        self.current_voltage = clamped

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload)
            print(f"[VALVE] MQTT message: {payload}")
            if payload.get("cmd") == "adjust":
                self.set_voltage(float(payload["value"]))
                if "res_topic" in payload:
                    client.publish(payload["res_topic"], json.dumps(self.current_voltage))
            else:
                print("Invalid valve command")
        except Exception as e:
            print("Valve MQTT error:", e)

# ─────────────────────────────────────────────────────────────
# Fan Class – Controls channel 1
# ─────────────────────────────────────────────────────────────
class Fan:
    def __init__(self):
        self.current_voltage = 0.0

    def set_voltage(self, voltage):
        clamped = max(0.0, min(10.0, voltage))
        raw_value = int(clamped * 1000)
        modbus_writer.update_output(1, raw_value)
        self.current_voltage = clamped

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload)
            print(f"[FAN] MQTT message: {payload}")
            if payload.get("cmd") == "adjust":
                self.set_voltage(float(payload["value"]))
                if "res_topic" in payload:
                    client.publish(payload["res_topic"], json.dumps(self.current_voltage))
            else:
                print("Invalid fan command")
        except Exception as e:
            print("Fan MQTT error:", e)

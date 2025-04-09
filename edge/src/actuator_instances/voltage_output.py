import json
import time
import serial
import os

import threading
import paho.mqtt.client as mqtt
from modbus_tk import modbus_rtu
import modbus_tk.defines as cst

PORT="/dev/ttySC0"
master = modbus_rtu.RtuMaster(serial.Serial(port=PORT,baudrate=9600, bytesize=8, parity='N', stopbits=1, xonxoff=0))
master.set_timeout(5.0)
master.set_verbose(True)

# Vi starter med 0 på alle, siden kun kanal 1 (index 0) skal brukes til styring av vifte (enda)
output = [0] * 8
fan_output = 0
valve_output = 0

def on_message_FAN_VOLTAGE_CMD_REQ(client, userdata, msg):
    cmd_msg = json.loads(msg.payload)
    try:
        print("FAN_VOLTAGE", cmd_msg, "\n")
        if cmd_msg["cmd"] == "adjust":
            raw_fan_value = cmd_msg["value"]
            clamped_fan_value = max(0, min(10, raw_fan_value))
            fan_output = int(clamped_fan_value * 1000)
            print("Fan output set to:", fan_output)
        else:
            print("Invalid command")
    except Exception as e:
        print("Fan voltage, command error:", str(e))

def on_message_VALVE_VOLTAGE_CMD_REQ(client, userdata, msg):
    cmd_msg = json.loads(msg.payload)
    try:
        print("VALVE_VOLTAGE", cmd_msg, "\n")
        if cmd_msg["cmd"] == "adjust":
            raw_valve_value = cmd_msg["value"]
            clamped_valve_value = max(0, min(10, raw_valve_value))
            valve_output = int(clamped_valve_value * 1000)
            print("Valve output set to:", valve_output)
        else:
            print("Invalid command")
    except Exception as e:
        print("Valve voltage, command error:", str(e))



try:
    master.set_timeout(5.0)
    master.set_verbose(True)

    while(True):
        output[0] = fan_output
        output[1] = valve_output

        #Read Input Registers Funtion:04H station:01H  address:00 length:08
        red = master.execute(1, cst.WRITE_MULTIPLE_REGISTERS, 0x00, 0x08, output_value=output)
        print(red)
        time.sleep(1)

except Exception as exc:
    print(str(exc))

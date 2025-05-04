import json
import time
import serial
import os

import threading
import paho.mqtt.client as mqtt
from modbus_tk import modbus_rtu
import modbus_tk.defines as cst
from src.sensor_interfaces import sensor_STH01_modbus

from src.utils.pid_controller import PIDController

PORT="/dev/ttySC0"
master = modbus_rtu.RtuMaster(serial.Serial(port=PORT,baudrate=9600, bytesize=8, parity='N', stopbits=1, xonxoff=0))
master.set_timeout(5.0)
master.set_verbose(True)

sensor1 = sensor_STH01_modbus.STH01_1(   portname='/dev/ttySC0',
                                                slaveaddress=70, 
                                                debug=False)

sensor2 = sensor_STH01_modbus.STH01_2(   portname='/dev/ttySC0',
                                                slaveaddress=69, 
                                                debug=False)

# PID for kjølebatteri
cooling_pid = PIDController(Kp=1.3, Ki=0.03, Kd=0.05)
MAX_COOLING_PID_OUTPUT = 50.0
ref_humidity = 0  # Eller None, eller hva du vil som standard


# Vi starter med 0 på alle, siden kun kanal 1 (index 0) skal brukes til styring av vifte (enda)
output = [0] * 2
fan_output = 0
valve_output = 0

def on_message_REFHUMID_CMD_REQ(client, userdata, msg):
    global ref_humidity
    cmd_msg = json.loads(msg.payload)
    try:
        print("Ønsket fuktighet", cmd_msg, "\n")
        if cmd_msg["cmd"] == "adjust_ref_humid":
            ref_humidity = float(cmd_msg["value"])
        else:
            print("Invalid command")
        res_payload = json.dumps(ref_humidity)
        client.publish(cmd_msg["res_topic"], res_payload)
    except Exception as e:
        print("Ønsket fuktighet, command error:", str(e))

def on_message_FAN_VOLTAGE_CMD_REQ(client, userdata, msg):
    global fan_output
    cmd_msg = json.loads(msg.payload)
    try:
        print("FAN_VOLTAGE", cmd_msg, "\n")
        if cmd_msg["cmd"] == "adjust":
            raw_fan_value = float(cmd_msg["value"])
            clamped_fan_value = max(0, min(10, raw_fan_value))
            fan_output = int(clamped_fan_value * 1000)

            output[1] = fan_output
            output[0] = valve_output
            result = master.execute(1, cst.WRITE_MULTIPLE_REGISTERS, 0x00, 0x08, output_value=output)
            print("Result of write:", result)
            print("Fan output set to:", fan_output)
        else:
            print("Invalid command")
    except Exception as e:
        print("Fan voltage, command error:", str(e))

def on_message_VALVE_VOLTAGE_CMD_REQ(client, userdata, msg):
    global valve_output
    cmd_msg = json.loads(msg.payload)
    try:
        print("VALVE_VOLTAGE", cmd_msg, "\n")
        if cmd_msg["cmd"] == "adjust":
            raw_valve_value = float(cmd_msg["value"])
            clamped_valve_value = max(0, min(10, raw_valve_value))
            valve_output = int(clamped_valve_value * 1000)

            output[1] = fan_output
            output[0] = valve_output
            result = master.execute(1, cst.WRITE_MULTIPLE_REGISTERS, 0x00, 0x08, output_value=output)
            print("Result of write:", result)
            print("Valve output set to:", valve_output)
        else:
            print("Invalid command")
    except Exception as e:
        print("Valve voltage, command error:", str(e))

def run_pid():
    global ref_humidity
    print("humidity_ref:", ref_humidity)
    try:
        
        # Henter sensor data fra sensoren før viften
        humidity1 = sensor1.get_humidity()
        print("humidity1:", humidity1)
        time.sleep(1)
        # Henter sensor data fra sensoren etter viften
        humidity2 = sensor2.get_humidity()
        print("humidity2:", humidity2)
        # Sjekker om det i det hele tatt er behov for å kjøre viften
        if humidity1 > ref_humidity and humidity2 > ref_humidity:

            # PID-beregninger
            cooling_signal = cooling_pid.calculate_control_signal(ref_humidity, humidity2)

            # Skaler til 0–10 og så til 0–10000
            cooling_scaled = max(0.0, min(cooling_signal / MAX_COOLING_PID_OUTPUT, 1.0))
            cooling_output = int(cooling_scaled * 10000)  # 0–10V signal

            # === Disse to sendes ut som 0–10V analoge signaler ===
            output[0] = cooling_output  # Kjøling
            print("PID", output[0])
        else:
            # Ikke behov for viftekjøring – vi skrur den helt av (0)
            output[0] = 0

        # Skriver til Modbus
        result = master.execute(1, cst.WRITE_MULTIPLE_REGISTERS, 0x00, 0x08, output_value=output)
        print("Result of write:", result)
    except Exception as exc:
        print("Feil i kontrollsløyfe:", str(exc))





"""try:
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
"""
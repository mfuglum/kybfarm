import json
import time
import serial
import os

import paho.mqtt.client as mqtt
from modbus_tk import modbus_rtu
import modbus_tk.defines as cst


from src.utils.controllers import PIDController
from src.utils.latest_pid_data import latest_humidity_data, cooling_pid_settings


PORT="/dev/ttySC0"
master = modbus_rtu.RtuMaster(serial.Serial(port=PORT,baudrate=9600, bytesize=8, parity='N', stopbits=1, xonxoff=0))
master.set_timeout(5.0)
master.set_verbose(True)

previous_output = 0

# PID for kjølebatteri
cooling_pid = PIDController(Kp=0.0, Ki=0.0, Kd=0.0,  mode = "cooling", max_integral=10, min_integral=-10) 

MAX_COOLING_PID_OUTPUT = 10.0
ref_humidity = 0  # Eller None, eller hva du vil som standard


# Vi starter med 0 på alle, siden kun kanal 1 (index 0) skal brukes til styring av vifte (enda)
output = [0] * 2
fan_output = 0
valve_output = 0

def on_message_REFHUMID_CMD_REQ(client, userdata, msg):
    cmd_msg = json.loads(msg.payload)
    try:
        print("Desired humidity", cmd_msg["value"], "\n")
        if cmd_msg["cmd"] == "adjust_ref_humid":
            latest_humidity_data["REF_HUMID"] = float(cmd_msg["value"])
            ref_humidity = latest_humidity_data["REF_HUMID"]
        else:
            print("Invalid command")
        res_payload = json.dumps(ref_humidity)
        client.publish(cmd_msg["res_topic"], res_payload)
    except Exception as e:
        print("Desired humidity, command error:", str(e))

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
   
    try:
        
        # Henter sensor data fra sensoren før viften
        ref_humidity = latest_humidity_data["REF_HUMID"]
        humidity1 = latest_humidity_data["STH01_1"]
        #humidity2 = latest_humidity_data["STH01_2"]
        # Sjekker om det i det hele tatt er behov for å kjøre viften

        # Finn nærmeste referansefuktighet og hent tilhørende PID-parametre
        closest_ref = min(cooling_pid_settings.keys(), key=lambda k: abs(k - ref_humidity))
        latest_setting = cooling_pid_settings[closest_ref]

        cooling_pid.Kp = latest_setting["Kp"]
        cooling_pid.Ki = latest_setting["Ki"]
        cooling_pid.Kd = latest_setting["Kd"]

        print("Using closest PID setting for ref humidity:", closest_ref)
        print(f"  → Kp: {cooling_pid.Kp}, Ki: {cooling_pid.Ki}, Kd: {cooling_pid.Kd}")
        

        # PID-beregninger
        cooling_signal = cooling_pid.calculate_control_signal(ref_humidity, humidity1)
        if cooling_signal is None:
            raise ValueError("Cooling PID did not return a valid signal!")


        # Skaler til 0–10 og så til 0–10000
        cooling_scaled = max(0.0, min(cooling_signal / MAX_COOLING_PID_OUTPUT, 1.0))

        cooling__output_scaled = int(1800 + cooling_scaled * 8200)

        # === Disse to sendes ut som 0–10V analoge signaler ===
        output[0] = cooling__output_scaled  # Kjøling
        print("PID dehumid", output[0])
        print("PID dehumid KP value", cooling_pid.Kp)
        print("PID dehumid Ki value", cooling_pid.Ki)
        print("PID dehumid Kd value", cooling_pid.Kd)
      
        # Skriver til Modbus
        result = master.execute(1, cst.WRITE_MULTIPLE_REGISTERS, 0x00, 0x08, output_value=output)
        print("Result of write:", result)
    except Exception as exc:
        print("Error in dehumid control loop:", str(exc))


import json
import time
import serial
import os

import paho.mqtt.client as mqtt
from modbus_tk import modbus_rtu
import modbus_tk.defines as cst

from src.utils.controllers import PIDController
from src.utils.latest_pid_data import latest_humidity_data, cooling_pid_settings

# Serial port configuration for Modbus RTU communication
PORT = "/dev/ttySC0"
master = modbus_rtu.RtuMaster(serial.Serial(port=PORT, baudrate=9600, bytesize=8, parity='N', stopbits=1, xonxoff=0))
master.set_timeout(5.0)
master.set_verbose(True)

# PID controller for cooling coil
cooling_pid = PIDController(Kp=0.0, Ki=0.0, Kd=0.0, mode="cooling") 

MAX_COOLING_PID_OUTPUT = 10.0

# Output arrays for analog outputs (0–10V), only channel 1 (index 0) used for fan control currently
output = [0] * 2
fan_output = 0
valve_output = 0

def on_message_REFHUMID_CMD_REQ(client, userdata, msg):
    """
    MQTT callback for handling humidity reference setpoint commands.

    Expects a JSON payload with:
        - "cmd": should be "adjust_ref_humid"
        - "value": desired humidity reference value
        - "res_topic": topic to publish the response

    Updates the global humidity reference value and publishes the new value.
    """
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
            # Clamp the requested fan voltage value to [0, 10] and scale to 0–10000
            raw_fan_value = float(cmd_msg["value"])
            clamped_fan_value = max(0, min(10, raw_fan_value))
            fan_output = int(clamped_fan_value * 1000)

            # Update the output array: channel 1 is fan, channel 0 is valve
            output[1] = fan_output
            output[0] = valve_output

            try:
                test_valve = master.execute(1, cst.READ_HOLDING_REGISTERS, 0x00, 0)
                test_fan = master.execute(1, cst.READ_HOLDING_REGISTERS, 0x08, 0)
                print("Valve reg 0x00 read:", test_valve)
                print("Fan reg 0x08 read:", test_fan)
            except Exception as e:
                print("Read test error:", str(e))


            try:
                res = master.execute(1, cst.WRITE_SINGLE_REGISTER, 0x00, output_value=valve_output)
                print("Write to 0x00 OK:", res)
            except Exception as e:
                print("Failed to write to 0x00:", e)

            try:
                res = master.execute(1, cst.WRITE_SINGLE_REGISTER, 0x08, output_value=fan_output)
                print("Write to 0x08 OK:", res)
            except Exception as e:
                print("Failed to write to 0x08:", e)


            print("Fan output set to:", fan_output)
        else:
            print("Invalid command")
        res_payload = json.dumps(raw_fan_value)
        client.publish(cmd_msg["res_topic"], res_payload)
    except Exception as e:
        print("Fan voltage, command error:", str(e))

def on_message_VALVE_VOLTAGE_CMD_REQ(client, userdata, msg):
    global valve_output
    cmd_msg = json.loads(msg.payload)
    try:
        print("VALVE_VOLTAGE", cmd_msg, "\n")
        if cmd_msg["cmd"] == "adjust":
            # Clamp the requested valve voltage value to [0, 10] and scale to 0–10000
            raw_valve_value = float(cmd_msg["value"])
            clamped_valve_value = max(0, min(10, raw_valve_value))
            valve_output = int(clamped_valve_value * 1000)

            # Update the output array: channel 0 is valve, channel 1 is fan
            output[1] = fan_output
            output[0] = valve_output

            try:
                res = master.execute(1, cst.WRITE_SINGLE_REGISTER, 0x00, output_value=valve_output)
                print("Write to 0x00 OK:", res)
            except Exception as e:
                print("Failed to write to 0x00:", e)

            try:
                res = master.execute(1, cst.WRITE_SINGLE_REGISTER, 0x08, output_value=fan_output)
                print("Write to 0x08 OK:", res)
            except Exception as e:
                print("Failed to write to 0x08:", e)
            
           
            print("Valve output set to:", valve_output)
        else:
            print("Invalid command")
        res_payload = json.dumps(raw_valve_value)
        client.publish(cmd_msg["res_topic"], res_payload)
    except Exception as e:
        print("Valve voltage, command error:", str(e))

def run_pid():
    """
    Runs the cooling PID control loop:
      - Reads the current and reference humidity values.
      - Selects the closest PID settings based on the reference.
      - Calculates the control signal.
      - Scales and applies the signal to the analog output (0–10V).
      - Writes the output to the Modbus device.
    """
    try:
        # Fetch reference and measured humidity values
        ref_humidity = latest_humidity_data["REF_HUMID"]
        humidity1 = latest_humidity_data["sth01_1"]

        # Find the closest reference value and use its PID parameters
        closest_ref = min(cooling_pid_settings.keys(), key=lambda k: abs(k - ref_humidity))
        latest_setting = cooling_pid_settings[closest_ref]

        cooling_pid.Kp = latest_setting["Kp"]
        cooling_pid.Ki = latest_setting["Ki"]
        cooling_pid.Kd = latest_setting["Kd"]

        print("Using closest PID setting for ref humidity:", closest_ref)
        print(f"  → Kp: {cooling_pid.Kp}, Ki: {cooling_pid.Ki}, Kd: {cooling_pid.Kd}")

        # PID calculation
        cooling_signal = cooling_pid.calculate_control_signal(ref_humidity, humidity1)
        if cooling_signal is None:
            raise ValueError("Cooling PID did not return a valid signal!")

        # Scale to 0–10 and then to 0–10000 for analog output
        cooling_scaled = max(0.0, min(cooling_signal / MAX_COOLING_PID_OUTPUT, 1.0))
        cooling__output_scaled = int(1800 + cooling_scaled * 8200)

        # Set output for cooling (channel 0)
        output[0] = cooling__output_scaled
        print("PID dehumid", output[0])
        print("PID dehumid KP value", cooling_pid.Kp)
        print("PID dehumid Ki value", cooling_pid.Ki)
        print("PID dehumid Kd value", cooling_pid.Kd)

        # Write to Modbus device
        try:
            res = master.execute(1, cst.WRITE_SINGLE_REGISTER, 0x00, output_value=valve_output)
            print("Write to 0x00 OK:", res)
        except Exception as e:
            print("Failed to write to 0x00:", e)

        try:
            res = master.execute(1, cst.WRITE_SINGLE_REGISTER, 0x08, output_value=fan_output)
            print("Write to 0x08 OK:", res)
        except Exception as e:
            print("Failed to write to 0x08:", e)

        
    except Exception as exc:
        print("Error in dehumid control loop:", str(exc))


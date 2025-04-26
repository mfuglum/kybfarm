#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Henter sensor data
from edge.src.sensor_interfaces import sensor_CO2_VOC_modbus # Sensoren før viften
from src.sensor_interfaces import sensor_STH01_modbus # Sensoren etter viften

from src.utils.pid_controller import PIDController # Kode for PID kontroller

import time
import serial
import modbus_tk
import modbus_tk.defines as cst
import json
from modbus_tk import modbus_rtu


PORT="/dev/ttySC0"
master = modbus_rtu.RtuMaster(serial.Serial(port=PORT,baudrate=9600, bytesize=8, parity='N', stopbits=1, xonxoff=0))
master.set_timeout(5.0)
master.set_verbose(True)

sensor1 = sensor_CO2_VOC_modbus.CO2_VOC() # Henter klassen CO2_VOC 
sensor2 = sensor_STH01_modbus.STH01() # Henter klassen STH01

# PID for kjølebatteri
cooling_pid = PIDController(Kp=1.3, Ki=0.03, Kd=0.05)

# PID for vifte
fan_pid = PIDController(Kp=0.6, Ki=0.01, Kd=0.02)

# PID skaleringsgrenser
MAX_COOLING_PID_OUTPUT = 50.0
MAX_FAN_PID_OUTPUT = 40.0

# Vifte minimum og maksimum analogsignal (0–10000 = 0–10V)
FAN_MIN_SIGNAL = 3000
FAN_MAX_SIGNAL = 10000

def on_message_REFHUMID_CMD_REQ(client, userdata, msg):
    global ref_humidity
    cmd_msg = json.loads(msg.payload)
    try:
        print("Ønsket fuktighet", cmd_msg, "\n")
        if cmd_msg["cmd"] == "adjust_ref_humid":
            ref_humidity = (cmd_msg["value"])
        else:
            print("Invalid command")
        res_payload = json.dumps(ref_humidity)
        client.publish(cmd_msg["res_topic"], res_payload)
    except Exception as e:
        print("Ønsket fuktighet, command error:", str(e))


# Vi starter med 0 på alle, siden kun kanal 1 (index 0) skal brukes til styring av vifte (enda)
output = [0] * 8

try:
    master.set_timeout(5.0)
    master.set_verbose(True)

    while(True):

        # Henter sensor data fra sensoren før viften
        temperature1 = sensor1.get_temperature()
        humidity1 = sensor1.get_humidity()
        dewpoint1 = sensor1.get_dewpoint()
        volume_flow1 = sensor1.get_volume_flow()

        # Henter sensor data fra sensoren etter viften
        temperature2 = sensor2.get_temperature()
        humidity2 = sensor2.get_humidity()
        dewpoint2 = sensor2.get_dewpoint()

        # Sjekker om det i det hele tatt er behov for å kjøre viften
        if humidity1 > ref_humidity and humidity2 > ref_humidity:

            # PID-beregninger
            cooling_signal = cooling_pid.calculate_control_signal(ref_humidity, humidity2)
            fan_signal = fan_pid.calculate_control_signal(ref_humidity, humidity2)

            # Skaler til 0–10 og så til 0–10000
            cooling_scaled = max(0.0, min(cooling_signal / MAX_COOLING_PID_OUTPUT, 1.0))
            cooling_output = int(cooling_scaled * 10000)  # 0–10V signal

            # Skaler vifte til 30–80 % (dvs. 3000–8000)
            fan_scaled = max(0.0, min(fan_signal / MAX_FAN_PID_OUTPUT, 1.0))
            fan_output = int(FAN_MIN_SIGNAL + fan_scaled * (FAN_MAX_SIGNAL - FAN_MIN_SIGNAL))
            fan_output = min(fan_output, 10000)

            # === Disse to sendes ut som 0–10V analoge signaler ===
            cooling_voltage_output = cooling_output       # Kjøling
            fan_voltage_output = fan_output               # Vifte

            output[0] = cooling_output
            output[1] = fan_output

        else:
            # Ikke behov for viftekjøring – vi skrur den helt av (0)
            output[0] = 0
            output[1] = 0

        #Read Input Registers Funtion:04H station:01H  address:00 length:08
        red = master.execute(1, cst.WRITE_MULTIPLE_REGISTERS, 0x00, 0x08, output_value=output)
        print(red)
        time.sleep(1)

except Exception as exc:
    print(str(exc))




"""
def on_message_REFHUMID_DT(client, userdata, msg):
    msg = json.loads(msg.payload)
    try:
        print("Ønsket fuktighet", msg, "\n")
        if msg["req"] == "get_diagnostic_data":
            response = lamp_1.get_diagnostic_data()
        elif msg["req"] == "get_status":
            response = lamp_1.get_status()
        else:
            print("Invalid command")
        res_payload = json.dumps(response)
        client.publish(msg["res_topic"], res_payload)
    except Exception as e:
        print("Lamp 1, request error:", str(e))
"""

"""
# Beregn hvor mye kjøling som trengs, basert på temperatur etter kjøling
            temp_diff = temperature2 - dewpoint1
            max_cooling_range = 5.0  # eller en verdi du velger

            if temp_diff > 0:
                cooling_ratio = temp_diff / max_cooling_range
                cooling_ratio = min(max(cooling_ratio, 0.0), 1.0)

                modbus_water_cooling_level = int(cooling_ratio * 10000)

            # Setter kun kanal 1 (index 0) til ny vifteverdi, resten forblir 0
            output[1] = modbus_water_cooling_level
"""
"""
# Beregner differansen mellom aktuell fuktighet og ønsket nivå
            delta = humidity2 - ref_humidity
            total_range = humidity1 - ref_humidity
            total_range = max(total_range, 1)  # Hindrer deling på 0

            # Prosentvis avstand til mål – skaleres til styring
            fanspeed = int((delta / total_range) * 100)
            fanspeed = 100 - viftestyrke  # Snur styrken: høy hastighet = lengre fra målet
            fanspeed = max(0, min(100, viftestyrke))  # Sikrer verdi mellom 0 og 100

            modbus_value_fan = int((fanspeed / 100) * 10000)  # 100 % → 10000 (10 V)

            # Setter kun kanal 1 (index 0) til ny vifteverdi, resten forblir 0
            output[0] = modbus_value_fan"
            
"""
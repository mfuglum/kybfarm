#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Henter sensor data
from src.sensor_interfaces import sensor_C02_VOC_modbus # Sensoren før viften
from src.sensor_interfaces import sensor_STH01_modbus # Sensoren etter viften

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

sensor1 = sensor_C02_VOC_modbus.CO2_VOC() # Henter klassen CO2_VOC 
sensor2 = sensor_STH01_modbus.STH01() # Henter klassen STH01

# Henter sensor data fra sensoren før viften
temperature1 = sensor1.get_temperature()
humidity1 = sensor1.get_humidity()
dewpoint1 = sensor1.get_dewpoint()
volume_flow1 = sensor1.get_volume_flow()

# Henter sensor data fra sensoren etter viften
temperature2 = sensor2.get_temperature()
humidity2 = sensor2.get_humidity()
dewpoint2 = sensor2.get_dewpoint()

def on_message_REFHUMID_CMD_REQ(client, userdata, msg):
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


# Vi starter med 0 på alle, siden kun kanal 1 (index 0) skal brukes til styring av vifte (enda)
output = [0] * 8

try:
    master.set_timeout(5.0)
    master.set_verbose(True)

    while(True):

        # Sjekker om det i det hele tatt er behov for å kjøre viften
        if humidity1 > humidity2:
            # Beregner differansen mellom aktuell fuktighet og ønsket nivå
            delta = humidity2 - ref_humidity
            total_range = humidity1 - ref_humidity
            total_range = max(total_range, 1)  # Hindrer deling på 0

            # Prosentvis avstand til mål – skaleres til styring
            viftestyrke = int((delta / total_range) * 100)
            viftestyrke = 100 - viftestyrke  # Snur styrken: høy hastighet = lengre fra målet
            viftestyrke = max(0, min(100, viftestyrke))  # Sikrer verdi mellom 0 og 100

            modbus_value = int((viftestyrke / 100) * 10000)  # 100 % → 10000 (10 V)

            # Setter kun kanal 1 (index 0) til ny vifteverdi, resten forblir 0
            output[0] = modbus_value

        else:
            # Ikke behov for viftekjøring – vi skrur den helt av (0)
            output[0] = 0

        #Read Input Registers Funtion:04H station:01H  address:00 length:08
        red = master.execute(1, cst.WRITE_MULTIPLE_REGISTERS, 0x00, 0x08, output_value=output)
        print(red)
        time.sleep(1)

except Exception as exc:
    print(str(exc))

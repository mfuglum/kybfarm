# Henter sensor data
from src.sensor_interfaces import sensor_C02_VOC_modbus # Sensoren før varmebatteri
from src.sensor_interfaces import sensor_C02_VOC_modbus1 # Sensoren etter varmebatteri

from src.utils.pid_controller import PIDController # Kode for PID kontroller

import json
import time

sensor1 = sensor_C02_VOC_modbus.CO2_VOC() # Henter klassen CO2_VOC 
sensor2 = sensor_C02_VOC_modbus1.CO2_VOC() # Henter klassen CO2_VOC 

heating_pid = PIDController(Kp=6.0, Ki=0.1, Kd=0.05)
MAX_HEATING_PID_OUTPUT = 100.0  # 0–100% styring

def on_message_REFTEMP_CMD_REQ(client, userdata, msg):
    global ref_temperature
    cmd_msg = json.loads(msg.payload)
    try:
        print("Ønsket temperature", cmd_msg, "\n")
        if cmd_msg["cmd"] == "adjust_ref_temp":
            ref_temperature = (cmd_msg["value"])
        else:
            print("Invalid command")
        res_payload = json.dumps(ref_temperature)
        client.publish(cmd_msg["res_topic"], res_payload)
    except Exception as e:
        print("Ønsket temperatur, command error:", str(e))

try:

    while(True):

        # Henter temperatur data fra sensoren før varmebatteriet
        temperature1 = sensor1.get_temperature()

        # Henter temperatur data fra sensoren etter viften
        temperature2 = sensor2.get_temperature()

        # Sjekker om det i det hele tatt er behov for oppvarming
        if temperature2 > temperature1:

            # PID-beregninger
            heating_signal = heating_pid.calculate_control_signal(ref_temperature, temperature2)


            heating_scaled = max(0.0, min(heating_signal / MAX_HEATING_PID_OUTPUT, 1.0))
            heating_output = int(heating_scaled * 100)  # 0–100 %
        
        time.sleep(1)  # eller 0.5 for raskere regulering

except Exception as exc:
    print(str(exc))



# Henter sensor data


from src.actuator_instances.relay_devices_initialization import solid_state_relay_1

from src.utils.pid_controller import PIDController # Kode for PID kontroller
from src.utils.latest_pid_data import latest_heating_data

import json
import time

heating_pid = PIDController(Kp=4.5, Ki=0.25, Kd=0, mode ="heating")



def on_message_REFTEMP_CMD_REQ(client, userdata, msg):
    cmd_msg = json.loads(msg.payload)
    try:
        print("Desired temperature", cmd_msg, "\n")
        if cmd_msg["cmd"] == "adjust_ref_temp":
            latest_heating_data["REF_TEMP"]= float((cmd_msg["value"]))
            ref_temperature = latest_heating_data["REF_TEMP"]
            
        else:
            print("Invalid command")
        res_payload = json.dumps(ref_temperature)
        client.publish(cmd_msg["res_topic"], res_payload)
    except Exception as e:
        print("Desired temperature, command error:", str(e))

def run_heating_pid():
    try:

   
        ref_temperature = latest_heating_data["REF_TEMP"]
        temperature1 = latest_heating_data["STH01_1"]
        temperature2 = latest_heating_data["STH01_2"]
        temperature3 = latest_heating_data["CO2_VOC_1"]

        if temperature1 is not None and temperature1> 50:
            heating_signal = 0.0
            print("ALERT: Temperature before fan is too high:", temperature1)
        elif temperature2 is not None and temperature2 > 50:
            heating_signal = 0.0
            print("ALERT: Temperature after coolingbattery is too high:", temperature2)
        elif temperature3 is not None and temperature3 > 50:
            heating_signal = 0.0
            print("ALERT: Temperature after heater is too high:", temperature3)
        else:
            
            heating_signal = heating_pid.calculate_control_signal(ref_temperature, temperature1)
        
        if heating_signal is None:
            raise ValueError("Heating PID did not return a valid signal!")
    
        
        on_time = (heating_signal * 10) * 0.95
        
        print("Heating output [%]:", heating_signal * 100)
        
        if on_time > 0:
            print("Heating on for", on_time, "seconds")
            solid_state_relay_1.turn_on_for(on_time)
        else:
            print("Heating off")
            solid_state_relay_1.turn_off()
        

    except Exception as exc:
        print(str(exc))



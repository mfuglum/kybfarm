# Henter sensor data


from edge.src.actuator_instances.relay_devices_initialization import solid_state_relay_1

from src.utils.pid_controller import PIDController # Kode for PID kontroller

import json
import time

heating_pid = PIDController(Kp=6.0, Ki=0.1, Kd=0.05)
MAX_HEATING_PID_OUTPUT = 100.0  # 0–100% styring

latest_heating_data = {
    "REF_TEMP": None,
    "STH01_1": None,
    "STH01_2": None,
    "CO2_VOC_1": None,
}


def on_message_REFTEMP_CMD_REQ(client, userdata, msg):
    global ref_temperature
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
    #global ref_temperature
    print("ref_temperature:", ref_temperature)
    try:

   
        ref_temperature = latest_heating_data["REF_TEMP"]
        temperature1 = latest_heating_data["STH01_1"]
        temperature2 = latest_heating_data["STH01_2"]
        temperature3 = latest_heating_data["CO2_VOC_1"]

        if temperature1 > 50:
            heating_signal = 0.0
            print("ALERT: Temperature before fan is too high:", temperature1)
        elif temperature2 > 50:
            heating_signal = 0.0
            print("ALERT: Temperature after coolingbattery is too high:", temperature2)
        elif temperature3 > 50:
            heating_signal = 0.0
            print("ALERT: Temperature after heater is too high:", temperature3)
        
        
    

        # PID-beregninger
        heating_signal = heating_pid.calculate_control_signal(ref_temperature, temperature1)


        heating_scaled = max(0.0, min(heating_signal / MAX_HEATING_PID_OUTPUT, 1.0))
        #heating_output = int(heating_scaled * 100)  # 0–100 %

        on_time = heating_scaled * 30
        
        if on_time > 0:
            print("Heating on for", on_time, "seconds")
            solid_state_relay_1.turn_on_for(on_time)
        else:
            print("Heating off")
            solid_state_relay_1.turn_off()
        
        time.sleep(0.5)  # eller 0.5 for raskere regulering

    except Exception as exc:
        print(str(exc))



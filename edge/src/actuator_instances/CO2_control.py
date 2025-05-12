import json
import time


from src.utils.p_controller import PController # Kode for PID kontroller
from src.actuator_instances.relay_devices_initialization import relay_13

from src.utils.latest_pid_data import latest_CO2_data

CO2_pid = PController(Kp=0.1)



def on_message_REFCO2_CMD_REQ(client, userdata, msg):
    cmd_msg = json.loads(msg.payload)
    try:
        print("Desired CO2 level", cmd_msg, "\n")
        if cmd_msg["cmd"] == "adjust_ref_CO2":
            latest_CO2_data["REF_CO2"]= float((cmd_msg["value"]))
            ref_CO2 = latest_CO2_data["REF_CO2"]
            
        else:
            print("Invalid command")
        res_payload = json.dumps(ref_CO2)
        client.publish(cmd_msg["res_topic"], res_payload)
    except Exception as e:
        print("Desired CO2 level, command error:", str(e))

def run_CO2_pid():
    try:

   
        ref_CO2 = latest_CO2_data["REF_CO2"]
        CO2 = latest_CO2_data["CO2_VOC_1"]


        CO2_signal = CO2_pid.calculate_control_signal(ref_CO2, CO2)

        if CO2_signal < 0.1:
            on_time = 0
        else:
            on_time = CO2_signal

        
        print("CO2 output [%]:", CO2_signal * 100)
        
        if on_time > 0:
            print("CO2 on for", on_time, "seconds")
            relay_13.turn_on_for(on_time)
        else:
            print("CO2 off")
            relay_13.turn_off()

    except Exception as exc:
        print(str(exc))
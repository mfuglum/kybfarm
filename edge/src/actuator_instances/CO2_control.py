import json
import time


from src.utils.pid_controller import PIDController # Kode for PID kontroller
from src.utils.latest_pid_data import latest_CO2_data

CO2_pid = PIDController(Kp=0.1, Ki=0, Kd=0, mode ="CO2")
MAX_CO2_PID_OUTPUT = 1.0  # 0–100% styring


def on_message_CO2_PID_CMD_REQ(client, userdata, msg):
    cmd_msg = json.loads(msg.payload)
    try:
        print(cmd_msg)
        if cmd_msg["cmd"] == "pid_enable":
            # Send command to enable PID
            print("Enabling CO2 PID")
            run_CO2_pid()
            print("Running CO2 PID")
            

        else:
            print("Invalid command")
    except Exception as e:
        print("CO2 PID enable error:", str(e))


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


        CO2_signal = CO2_pid.calculate_control_signal(ref_CO2, latest_CO2_data)

        CO2_scaled = max(0.0, min(CO2_signal / MAX_CO2_PID_OUTPUT, 1.0))

        on_time = (CO2_scaled * 10) - 0.5
        
        print("CO2 output [%]:", CO2_scaled * 100)
        
        if on_time > 0:
            print("CO2 on for", on_time, "seconds")
            CO2.turn_on_for(on_time)
        else:
            print("CO2 off")
            CO2.turn_off()

    except Exception as exc:
        print(str(exc))
import json
import time


from src.utils.controllers import PIController # Kode for PID kontroller
from src.actuator_instances.relay_devices_initialization import relay_13

from src.utils.latest_pid_data import latest_CO2_data, CO2_pi_settings

CO2_pi = PIController(Kp=0, Ki = 0)



def on_message_REFCO2_CMD_REQ(client, userdata, msg):
    cmd_msg = json.loads(msg.payload)
    try:
        print("Desired CO2 level", cmd_msg["value"], "\n")
        if cmd_msg["cmd"] == "adjust_ref_co2":
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
        print("Ref_CO2:", ref_CO2)
        print("Latest CO2:", CO2)

        # Finn nærmeste referansefuktighet og hent tilhørende PI-parametre
        closest_ref = min(CO2_pi_settings.keys(), key=lambda k: abs(k - ref_CO2))
        latest_setting = CO2_pi_settings[closest_ref]

        CO2_pi.Kp = latest_setting["Kp"]
        CO2_pi.Ki = latest_setting["Ki"]

        print("Using closest PI setting for ref CO2:", closest_ref)
        print(f"  → Kp: {CO2_pi.Kp}, Ki: {CO2_pi.Ki}")
        


        CO2_signal = CO2_pi.calculate_control_signal(ref_CO2, CO2)
        print("CO2 sign", CO2_signal)

        CO2_scaled = max(0.0, min(CO2_signal/10, 1.0))
        print("CO2 scaled", CO2_scaled)

        if CO2_scaled is None:
            raise ValueError("CO2 PID did not return a valid signal!")

        if CO2_scaled < 0.1: # Ingen frekvens over 10Hz for å skåne mekanisk rele
            on_time = 0
        else:
            on_time = CO2_scaled

        
        print("CO2 output [%]:", CO2_scaled * 100)
        
        if on_time > 0:
            print("CO2 on for", on_time, "seconds")
            relay_13.turn_on_for(on_time)
        else:
            print("CO2 off")
            relay_13.turn_off()

    except Exception as exc:
        print(str(exc))
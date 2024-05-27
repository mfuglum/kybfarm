from src.utils import grow_lamp_elixia
import json
import time

# This constant must be imported from the environment file and updated in the main script
LAMP_01_IP = ""

def on_message_LAMP01_CMD(client, userdata, msg):
    cmd_msg = json.loads(msg.payload)
    try:
        print("LAMP01", cmd_msg, "\n")
        if cmd_msg["cmd"] == "adjust_intensity":
            response = lamp_1.set_channel_intensities(cmd_msg["intensity"])
        # elif cmd_msg["cmd"] == "off":
        #     lamp_1.turn_off()
        else:
            print("Invalid command")
        res_payload = res_payload = json.dumps(response)
        client.publish(cmd_msg["res_topic"], res_payload)
    except Exception as e:
        print("Lamp 1, command error:", str(e))

def on_message_LAMP01_DT(client, userdata, msg):
    msg = json.loads(msg.payload)
    try:
        print("LAMP01", msg, "\n")
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
    
# Initiate grow lamp
lamp_1 = grow_lamp_elixia(LAMP_01_IP)
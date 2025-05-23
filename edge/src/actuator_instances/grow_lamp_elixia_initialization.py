from src.utils import grow_lamp_elixia
import json

# This constant must be imported from the environment file and updated in the main script
LAMP_01_IP = ""
LAMP_02_IP = ""

def on_message_LAMP01_CMD_REQ(client, userdata, msg):
    """
    MQTT callback for handling commands to Lamp 1.

    Expects a JSON payload with:
        - "cmd": command string, e.g., "adjust_intensity"
        - "intensity": intensity settings (if applicable)
        - "res_topic": topic to publish the response

    Supported commands:
        - "adjust_intensity": Sets the channel intensities for lamp 1.

    Publishes the response to the specified response topic.
    """
    cmd_msg = json.loads(msg.payload)
    try:
        print("LAMP01", cmd_msg, "\n")
        if cmd_msg["cmd"] == "adjust_intensity":
            response = lamp_1.set_channel_intensities(cmd_msg["intensity"])
        # elif cmd_msg["cmd"] == "off":
        #     lamp_1.turn_off()
        else:
            print("Invalid command")
        res_payload = json.dumps(response)
        client.publish(cmd_msg["res_topic"], res_payload)
    except Exception as e:
        print("Lamp 1, command error:", str(e))

def on_message_LAMP01_DT(client, userdata, msg):
    """
    MQTT callback for handling diagnostic/status requests for Lamp 1.

    Expects a JSON payload with:
        - "req": request string, e.g., "get_diagnostic_data" or "get_status"
        - "res_topic": topic to publish the response

    Supported requests:
        - "get_diagnostic_data": Returns diagnostic data from lamp 1.
        - "get_status": Returns status information from lamp 1.

    Publishes the response to the specified response topic.
    """
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
try:
    lamp_1 = grow_lamp_elixia.grow_lamp_elixia(LAMP_01_IP)
except Exception as e:
    print("Error initiating grow lamp1:", str(e))


def on_message_LAMP02_CMD_REQ(client, userdata, msg):
    # Same structure as on_message_LAMP01_CMD_REQ, but for lamp_2

    cmd_msg = json.loads(msg.payload)
    try:
        print("LAMP02", cmd_msg, "\n")
        if cmd_msg["cmd"] == "adjust_intensity":
            response = lamp_2.set_channel_intensities(cmd_msg["intensity"])
        # elif cmd_msg["cmd"] == "off":
        #     lamp_1.turn_off()
        else:
            print("Invalid command")
        res_payload = json.dumps(response)
        client.publish(cmd_msg["res_topic"], res_payload)
    except Exception as e:
        print("Lamp 2, command error:", str(e))

def on_message_LAMP02_DT(client, userdata, msg):
    # Same structure as on_message_LAMP01_DT, but for lamp_2

    msg = json.loads(msg.payload)
    try:
        print("LAMP02", msg, "\n")
        if msg["req"] == "get_diagnostic_data":
            response = lamp_2.get_diagnostic_data()
        elif msg["req"] == "get_status":
            response = lamp_2.get_status()
        else:
            print("Invalid command")
        res_payload = json.dumps(response)
        client.publish(msg["res_topic"], res_payload)
    except Exception as e:
        print("Lamp 2, request error:", str(e))
    
# Initiate grow lamp
try:
    lamp_2 = grow_lamp_elixia.grow_lamp_elixia(LAMP_02_IP)
except Exception as e:
    print("Error initiating grow lamp2:", str(e))
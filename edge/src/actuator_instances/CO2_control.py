import json
import time

# Import PI controller class
from src.utils.controllers import PIController

# Import relay device for CO2 control (relay_13)
from src.actuator_instances.relay_devices_initialization import relay_13

# Import latest CO2 data and PI settings
from src.utils.latest_pid_data import latest_CO2_data, CO2_pi_settings

# Initialize PI controller for CO2 with default gains
CO2_pi = PIController(Kp=0, Ki=0)

def on_message_REFCO2_CMD_REQ(client, userdata, msg):
    """
    MQTT callback for handling CO2 reference setpoint commands.

    Args:
        client: MQTT client instance.
        userdata: User data (unused).
        msg: MQTT message object containing the payload.

    Expects a JSON payload with:
        - "cmd": should be "adjust_ref_co2"
        - "value": desired CO2 reference value
        - "res_topic": topic to publish the response

    Updates the global CO2 reference value and publishes the new value.
    """
    cmd_msg = json.loads(msg.payload)
    try:
        print("Desired CO2 level", cmd_msg["value"], "\n")
        if cmd_msg["cmd"] == "adjust_ref_co2":
            # Update the reference CO2 value
            latest_CO2_data["REF_CO2"] = float(cmd_msg["value"])
            ref_CO2 = latest_CO2_data["REF_CO2"]
        else:
            print("Invalid command")
        # Respond with the new reference value
        res_payload = json.dumps(ref_CO2)
        client.publish(cmd_msg["res_topic"], res_payload)
    except Exception as e:
        print("Desired CO2 level, command error:", str(e))

def run_CO2_pid():
    """
    Runs the CO2 PI control loop:
      - Reads the current and reference CO2 values.
      - Selects the closest PI settings based on the reference.
      - Calculates the control signal.
      - Scales and applies the signal to the relay (relay_13).
      - Ensures relay is not switched too frequently (protects relay).
    """
    try:
        # Get reference and measured CO2 values
        ref_CO2 = latest_CO2_data["REF_CO2"]
        CO2 = latest_CO2_data["CO2_VOC_1"]
        print("Ref_CO2:", ref_CO2)
        print("Latest CO2:", CO2)

        # Find the closest reference value and use its PI parameters
        closest_ref = min(CO2_pi_settings.keys(), key=lambda k: abs(k - ref_CO2))
        latest_setting = CO2_pi_settings[closest_ref]

        CO2_pi.Kp = latest_setting["Kp"]
        CO2_pi.Ki = latest_setting["Ki"]

        print("Using closest PI setting for ref CO2:", closest_ref)
        print(f"  → Kp: {CO2_pi.Kp}, Ki: {CO2_pi.Ki}")

        # Calculate the PI control signal
        CO2_signal = CO2_pi.calculate_control_signal(ref_CO2, CO2)
        print("CO2 sign", CO2_signal)

        # Scale the signal to [0, 1] range (max output)
        CO2_scaled = max(0.0, min(CO2_signal / 10, 1.0))
        print("CO2 scaled", CO2_scaled)

        if CO2_scaled is None:
            raise ValueError("CO2 PID did not return a valid signal!")

        # Protect relay: do not switch on for very short times
        if CO2_scaled < 0.1:  # No frequency above 10Hz to protect mechanical relay
            on_time = 0
        else:
            on_time = CO2_scaled

        print("CO2 output [%]:", CO2_scaled * 100)

        # Control relay based on calculated on_time
        if on_time > 0:
            print("CO2 on for", on_time, "seconds")
            relay_13.turn_on_for(on_time)
        else:
            print("CO2 off")
            relay_13.turn_off()

    except Exception as exc:
        print(str(exc))
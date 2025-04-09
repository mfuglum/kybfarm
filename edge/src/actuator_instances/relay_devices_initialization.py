from src.utils import relay_device
from src.utils import pwm_relay_device
import json

# Device to GPIO (BCD) pin mapping
GPIO_PIN = {
    "relay_1": 2,
    "relay_2": 3,
    "relay_3": 4,
    "relay_4": 14,
    "relay_5": 15,
    "relay_6": 17,
    "relay_7": 23,
    "relay_8": 10,
    "relay_9": 9,
    "relay_10": 25,
    "relay_11": 11,
    "relay_12": 8,
    "relay_13": 6,
    "relay_14": 12,
    "relay_15": 13,
    "relay_16": 16,
    "solid_state_relay_1": 26,
    "float_switch_1": 7,
    "float_switch_2": 0,
    "float_switch_3": 1,
    "float_switch_4": 5,
}

# Define MQTT callbacks for relay control
def on_message_RLY01(client, userdata, msg):
    cmd_msg = json.loads(msg.payload)
    try:
        print("RLY01", cmd_msg, "\n")
        if cmd_msg["cmd"] == "on":
            relay_1.turn_on()
        elif cmd_msg["cmd"] == "off":
            relay_1.turn_off()
        elif cmd_msg["cmd"] == "on_for":
            relay_1.turn_on_for(float(cmd_msg["time"]))
        else:
            print("Invalid command")
    except Exception as e:
        print("Relay 1, command error:", str(e))

def on_message_RLY02(client, userdata, msg):
    cmd_msg = json.loads(msg.payload)
    try:
        print("RLY02", cmd_msg, "\n")
        if cmd_msg["cmd"] == "on":
            relay_2.turn_on()
        elif cmd_msg["cmd"] == "off":
            relay_2.turn_off()
        elif cmd_msg["cmd"] == "on_for":
            relay_2.turn_on_for(float(cmd_msg["time"]))
        else:
            print("Invalid command")
    except Exception as e:
        print("Relay 2, command error:", str(e))

def on_message_RLY03(client, userdata, msg):
    cmd_msg = json.loads(msg.payload)
    try:
        print("RLY03", cmd_msg, "\n")
        if cmd_msg["cmd"] == "on":
            relay_3.turn_on()
        elif cmd_msg["cmd"] == "off":
            relay_3.turn_off()
        elif cmd_msg["cmd"] == "on_for":
            relay_3.turn_on_for(float(cmd_msg["time"]))
        else:
            print("Invalid command")
    except Exception as e:
        print("Relay 3, command error:", str(e))

def on_message_RLY04(client, userdata, msg):
    cmd_msg = json.loads(msg.payload)
    try:
        print("RLY04", cmd_msg, "\n")
        if cmd_msg["cmd"] == "on":
            relay_4.turn_on()
        elif cmd_msg["cmd"] == "off":
            relay_4.turn_off()
        elif cmd_msg["cmd"] == "on_for":
            relay_4.turn_on_for(float(cmd_msg["time"]))
        else:
            print("Invalid command")
    except Exception as e:
        print("Relay 4, command error:", str(e))

def on_message_RLY05(client, userdata, msg):
    cmd_msg = json.loads(msg.payload)
    try:
        print("RLY05", cmd_msg, "\n")
        if cmd_msg["cmd"] == "on":
            relay_5.turn_on()
        elif cmd_msg["cmd"] == "off":
            relay_5.turn_off()
        elif cmd_msg["cmd"] == "on_for":
            relay_5.turn_on_for(float(cmd_msg["time"]))
        else:
            print("Invalid command")
    except Exception as e:
        print("Relay 5, command error:", str(e))

def on_message_RLY06(client, userdata, msg):
    cmd_msg = json.loads(msg.payload)
    try:
        print("RLY06", cmd_msg, "\n")
        if cmd_msg["cmd"] == "on":
            relay_6.turn_on()
        elif cmd_msg["cmd"] == "off":
            relay_6.turn_off()
        elif cmd_msg["cmd"] == "on_for":
            relay_6.turn_on_for(float(cmd_msg["time"]))
        else:
            print("Invalid command")
    except Exception as e:
        print("Relay 6, command error:", str(e))

def on_message_RLY07(client, userdata, msg):
    cmd_msg = json.loads(msg.payload)
    try:
        print("RLY07", cmd_msg, "\n")
        if cmd_msg["cmd"] == "on":
            relay_7.turn_on()
        elif cmd_msg["cmd"] == "off":
            relay_7.turn_off()
        elif cmd_msg["cmd"] == "on_for":
            relay_7.turn_on_for(float(cmd_msg["time"]))
        else:
            print("Invalid command")
    except Exception as e:
        print("Relay 7, command error:", str(e))

def on_message_RLY08(client, userdata, msg):
    cmd_msg = json.loads(msg.payload)
    try:
        print("RLY08", cmd_msg, "\n")
        if cmd_msg["cmd"] == "on":
            relay_8.turn_on()
        elif cmd_msg["cmd"] == "off":
            relay_8.turn_off()
        elif cmd_msg["cmd"] == "on_for":
            relay_8.turn_on_for(float(cmd_msg["time"]))
        else:
            print("Invalid command")
    except Exception as e:
        print("Relay 8, command error:", str(e))

def on_message_RLY09(client, userdata, msg):
    cmd_msg = json.loads(msg.payload)
    try:
        print("RLY09", cmd_msg, "\n")
        if cmd_msg["cmd"] == "on":
            relay_9.turn_on()
        elif cmd_msg["cmd"] == "off":
            relay_9.turn_off()
        elif cmd_msg["cmd"] == "on_for":
            relay_9.turn_on_for(float(cmd_msg["time"]))
        else:
            print("Invalid command")
    except Exception as e:
        print("Relay 9, command error:", str(e))

def on_message_RLY10(client, userdata, msg):
    cmd_msg = json.loads(msg.payload)
    try:
        print("RLY10", cmd_msg, "\n")
        if cmd_msg["cmd"] == "on":
            relay_10.turn_on()
        elif cmd_msg["cmd"] == "off":
            relay_10.turn_off()
        elif cmd_msg["cmd"] == "on_for":
            relay_10.turn_on_for(float(cmd_msg["time"]))
        else:
            print("Invalid command")
    except Exception as e:
        print("Relay 10, command error:", str(e))

def on_message_RLY11(client, userdata, msg):
    cmd_msg = json.loads(msg.payload)
    try:
        print("RLY11", cmd_msg, "\n")
        if cmd_msg["cmd"] == "on":
            relay_11.turn_on()
        elif cmd_msg["cmd"] == "off":
            relay_11.turn_off()
        elif cmd_msg["cmd"] == "on_for":
            relay_11.turn_on_for(float(cmd_msg["time"]))
        else:
            print("Invalid command")
    except Exception as e:
        print("Relay 11, command error:", str(e))

def on_message_RLY12(client, userdata, msg):
    cmd_msg = json.loads(msg.payload)
    try:
        print("RLY12", cmd_msg, "\n")
        if cmd_msg["cmd"] == "on":
            relay_12.turn_on()
        elif cmd_msg["cmd"] == "off":
            relay_12.turn_off()
        elif cmd_msg["cmd"] == "on_for":
            relay_12.turn_on_for(float(cmd_msg["time"]))
        else:
            print("Invalid command")
    except Exception as e:
        print("Relay 12, command error:", str(e))

def on_message_RLY13(client, userdata, msg):
    cmd_msg = json.loads(msg.payload)
    try:
        print("RLY13", cmd_msg, "\n")
        if cmd_msg["cmd"] == "on":
            relay_13.turn_on()
        elif cmd_msg["cmd"] == "off":
            relay_13.turn_off()
        elif cmd_msg["cmd"] == "on_for":
            relay_13.turn_on_for(float(cmd_msg["time"]))
        else:
            print("Invalid command")
    except Exception as e:
        print("Relay 13, command error:", str(e))

def on_message_RLY14(client, userdata, msg):
    cmd_msg = json.loads(msg.payload)
    try:
        print("RLY14", cmd_msg, "\n")
        if cmd_msg["cmd"] == "on":
            relay_14.turn_on()
        elif cmd_msg["cmd"] == "off":
            relay_14.turn_off()
        elif cmd_msg["cmd"] == "on_for":
            relay_14.turn_on_for(float(cmd_msg["time"]))
        else:
            print("Invalid command")
    except Exception as e:
        print("Relay 14, command error:", str(e))

def on_message_RLY15(client, userdata, msg):
    cmd_msg = json.loads(msg.payload)
    try:
        print("RLY15", cmd_msg, "\n")
        if cmd_msg["cmd"] == "on":
            relay_15.turn_on()
        elif cmd_msg["cmd"] == "off":
            relay_15.turn_off()
        elif cmd_msg["cmd"] == "on_for":
            relay_15.turn_on_for(float(cmd_msg["time"]))
        else:
            print("Invalid command")
    except Exception as e:
        print("Relay 15, command error:", str(e))

def on_message_RLY16(client, userdata, msg):
    cmd_msg = json.loads(msg.payload)
    try:
        print("RLY16", cmd_msg, "\n")
        if cmd_msg["cmd"] == "on":
            relay_16.turn_on()
        elif cmd_msg["cmd"] == "off":
            relay_16.turn_off()
        elif cmd_msg["cmd"] == "on_for":
            relay_16.turn_on_for(float(cmd_msg["time"]))
        else:
            print("Invalid command")
    except Exception as e:
        print("Relay 16, command error:", str(e))

def on_message_SSR01(client, userdata, msg):
    cmd_msg = json.loads(msg.payload)
    try:
        print("SSR01", cmd_msg, "\n")
        if cmd_msg["cmd"] == "on":
            relay_16.turn_on()
        elif cmd_msg["cmd"] == "off":
            relay_16.turn_off()
        elif cmd_msg["cmd"] == "on_for":
            relay_16.turn_on_for(float(cmd_msg["time"]))
        
        elif cmd_msg["cmd"] == "adjust_ssr_pwm":
            period = float(cmd_msg["value_base_period"])
            duty_cycle = float(cmd_msg["value_duty_cycle"])
            solid_state_relay_1.set_pwm(period, duty_cycle)
        elif cmd_msg["cmd"] == "ssr_stop_pwm_loop":
            solid_state_relay_1.stop_pwm()

            #Kanskje legge til start loop?
        else:
            print("Invalid command")
    except Exception as e:
        print("Solid State Relay 01, command error:", str(e))

# Activate relay devices
try:
    relay_1 = relay_device.relay_device(GPIO_PIN["relay_1"])
    relay_2 = relay_device.relay_device(GPIO_PIN["relay_2"])
    relay_3 = relay_device.relay_device(GPIO_PIN["relay_3"])
    relay_4 = relay_device.relay_device(GPIO_PIN["relay_4"])
    relay_5 = relay_device.relay_device(GPIO_PIN["relay_5"])
    relay_6 = relay_device.relay_device(GPIO_PIN["relay_6"])
    relay_7 = relay_device.relay_device(GPIO_PIN["relay_7"])
    relay_8 = relay_device.relay_device(GPIO_PIN["relay_8"])
    relay_9 = relay_device.relay_device(GPIO_PIN["relay_9"])
    relay_10 = relay_device.relay_device(GPIO_PIN["relay_10"])
    relay_11 = relay_device.relay_device(GPIO_PIN["relay_11"])
    relay_12 = relay_device.relay_device(GPIO_PIN["relay_12"])
    relay_13 = relay_device.relay_device(GPIO_PIN["relay_13"])
    relay_14 = relay_device.relay_device(GPIO_PIN["relay_14"])
    relay_15 = relay_device.relay_device(GPIO_PIN["relay_15"])
    relay_16 = relay_device.relay_device(GPIO_PIN["relay_16"])
    solid_state_relay_1 = pwm_relay_device.pwm_relay_device(GPIO_PIN["solid_state_relay_1"])
except Exception as e:
    print("Relay device initialization error:", str(e))
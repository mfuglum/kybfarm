"""This is the main file to run on the edge computer.
It is subscribing to MQTT topics for data and command requests, and publishing the requested data or status to the MQTT broker.
To run this file create a python virtual envronment in kybfarm/edge/ and install the required packages from requirements.txt:
Create venv:
    python3 -m venv venv
Activate venv:
    source venv/bin/activate
Install required packages:
    pip install -r requirements.txt

Run the file:
    python edge_computer_main.py
"""
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json
import time
from dotenv import load_dotenv
import os
import string
# from sensor_interfaces import sensor_BMP280_I2C
from src.sensor_interfaces import (sensor_SCD41_I2C, 
                                   sensor_SYM01_modbus, 
                                   sensor_SLIGHT01_modbus,
                                   sensor_SPAR02_modbus)
from src.utils import relay_device

# Load environment variables from the .env file
load_dotenv()

# Fetch MQTT config values from .env file
MQTT_HOST = os.getenv("MOSQUITTO_BROKER_IP")
MQTT_PORT = int(os.getenv("MOSQUITTO_BROKER_PORT"))
MQTT_KEEP_ALIVE = int(os.getenv("MQTT_EDGE_KEEP_ALIVE"))

# MQTT data (dt) request (req) topics
MQTT_SLIGTH01_DT_REQ = os.getenv("MQTT_SENSOR_01_REQ")
MQTT_SPAR02_DT_REQ = os.getenv("MQTT_SENSOR_02_REQ")
MQTT_SYM01_DT_REQ = os.getenv("MQTT_SENSOR_10_REQ")
MQTT_SCD41_DT_REQ = os.getenv("MQTT_SENSOR_11_REQ")

# MQTT command (cmd) request (req) topics
# MQTT_RELAY01_CMD_REQ = os.getenv("MQTT_RELAY_01_REQ")
MQTT_RELAY12_CMD = os.getenv("MQTT_RELAY_12_CMD")

MQTT_SEC01_1_CMD = os.getenv("MQTT_SENSOR_03_CMD")

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
    "float_switch_1": 7,
    "float_switch_2": 0,
    "float_switch_3": 1,
    "float_switch_4": 5,
}

def on_connect(client, userdata, flags, rc):
    print("Connected with code " + str(rc))
    # Subscribe in on_connect to renew subsriptions in case of lost connection
    # Sensors #
    client.subscribe(MQTT_SLIGTH01_DT_REQ)
    client.subscribe(MQTT_SPAR02_DT_REQ)
    client.subscribe(MQTT_SYM01_DT_REQ)
    client.subscribe(MQTT_SCD41_DT_REQ)
    client.subscribe(MQTT_SEC01_1_CMD)

    # Actuators #
    client.subscribe(MQTT_RELAY12_CMD)

# Catch-all callback function for messages
def on_message(client, userdata, msg):
    print("\n" + msg.topic + ":\n", msg.payload)

# Sensors callback functions MQTT data request topics
def on_message_SLIGHT01(client, userdata, msg):
    req_msg = json.loads(msg.payload)
    try:
        res_payload = json.dumps(sensor_SLIGHT01.fetch_and_return_data())
        client.publish(req_msg["res_topic"], res_payload)
        print(res_payload + "\n")
    except Exception as e:
        print("SLIGHT01, data fetch error:", str(e))

def on_message_SPAR02(client, userdata, msg):
    req_msg = json.loads(msg.payload)
    try:
        res_payload = json.dumps(sensor_SPAR02.fetch_and_return_data())
        client.publish(req_msg["res_topic"], res_payload)
        print(res_payload + "\n")
    except Exception as e:
        print("SPAR02, data fetch error:", str(e))

def on_message_SYM01(client, userdata, msg):
    req_msg = json.loads(msg.payload)
    try:
        res_payload = json.dumps(sensor_SYM01.fetch_and_return_data())
        client.publish(req_msg["res_topic"], res_payload)
        print(res_payload + "\n")
    except Exception as e:
        print("SYM01, data fetch error:", str(e))

def on_message_SCD41(client, userdata, msg):
    req_msg = json.loads(msg.payload)
    try:
        res_payload = json.dumps(sensor_SCD41_I2C.fetch_and_return_data())
        client.publish(req_msg["res_topic"], res_payload, )
        print(res_payload + "\n")
    except Exception as e:
        print("SCD41, data fetch error:", str(e))

def on_message_SEC01_1_CMD(client, userdata, msg):
    cmd_msg = json.loads(msg.payload)
    try:
        print(cmd_msg)
        if cmd_msg["cmd"] == "register_ec_1413":
            # Send calibration command to sensor
            print("Dummy action: Registering EC 1413")
        elif cmd_msg["cmd"] == "register_ec_12880":
            # Send calibration command to sensor
            print("Dummy action: Registering EC 12880")
        else:
            print("Invalid command")
    except Exception as e:
        print("S-EC-01-1 error:", str(e))

# Actuators callback functions MQTT command request topics
def on_message_RLY12(client, userdata, msg):
    cmd_msg = json.loads(msg.payload)
    try:
        print(cmd_msg)
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

# Setup MQTT client for sensor host
client = mqtt.Client()

# Assign the generic callback functions for the client
client.on_connect = on_connect
client.on_message = on_message

# Assign the specific callback functions for the client
# Sensors #
client.message_callback_add(MQTT_SLIGTH01_DT_REQ, on_message_SLIGHT01)
client.message_callback_add(MQTT_SPAR02_DT_REQ, on_message_SPAR02)
client.message_callback_add(MQTT_SYM01_DT_REQ, on_message_SYM01)
client.message_callback_add(MQTT_SCD41_DT_REQ, on_message_SCD41)
client.message_callback_add(MQTT_SEC01_1_CMD, on_message_SEC01_1_CMD)

# Actuators #
client.message_callback_add(MQTT_RELAY12_CMD, on_message_RLY12)

# Connect to the MQTT server
try:
    client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEP_ALIVE)
    client.loop_start()
except:
    print("\nConnection failed\n")

# Activate SLIGHT-01 sensor
try:
    sensor_SLIGHT01 = sensor_SLIGHT01_modbus.SLIGHT01(  portname='/dev/ttySC1',
                                                        slaveaddress=13, 
                                                        debug=False)
    print(sensor_SLIGHT01)
except Exception as e:
    print("SLIGHT01, error:", str(e))

# Activate SPAR-02 sensor
try:
    sensor_SPAR02 = sensor_SPAR02_modbus.SPAR02(   portname='/dev/ttySC1',
                                                    slaveaddress=34, 
                                                    debug=False)
    print(sensor_SPAR02)
except Exception as e:
    print("SPAR02, error:", str(e))

# Activate SYM-01 sensor
try:
    sensor_SYM01 = sensor_SYM01_modbus.SYM01(   portname='/dev/ttySC1',
                                                slaveaddress=11, 
                                                debug=False)
    print(sensor_SYM01)
except Exception as e:
    print("SYM01, error:", str(e))

# Activate SCD-41 sensor
try:
    sensor_SCD41_I2C.start_low_periodic_measurement()
except Exception as e:
    print("SCD41, error:", str(e))

# Activate relay devices
try:
    relay_12 = relay_device.relay_device(GPIO_PIN["relay_12"])
except Exception as e:
    print("Relay device, error:", str(e))

# Start main loop
try:
    # Main loop
    while True:
        time.sleep(15)
except KeyboardInterrupt:
    print("Keyboard interrupt")
except Exception as e:
    print("\nException, error: ", str(e))

client.loop_stop()
sensor_SCD41_I2C.stop_periodic_measurement()


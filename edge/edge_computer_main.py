#!/usr/bin/env python3
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
import logging
import paho.mqtt.client as mqtt
import json
import time
from dotenv import load_dotenv
import os

from src.sensor_interfaces import (sensor_SCD41_I2C, 
                                   sensor_SYM01_modbus, 
                                   sensor_SLIGHT01_modbus,
                                   sensor_SPAR02_modbus,
                                   sensor_SEC01_modbus,
                                   sensor_SPH01_modbus)
from src.actuator_instances import (relay_devices_initialization,
                                    grow_lamp_elixia_initialization) 

# Load environment variables from the .env file
load_dotenv()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s:%(name)s:%(message)s')

# Fetch MQTT config values from .env file
MQTT_HOST = os.getenv("MOSQUITTO_BROKER_IP")
MQTT_PORT = int(os.getenv("MOSQUITTO_BROKER_PORT"))
MQTT_KEEP_ALIVE = int(os.getenv("MQTT_EDGE_KEEP_ALIVE"))

# Default serial port for Modbus sensors
RS485_PORT = os.getenv("RS485_PORT", "/dev/ttySC1")

# MQTT data (dt) request (req) topics
MQTT_SLIGTH01_DT_REQ = os.getenv("MQTT_SENSOR_01_DT_REQ")
MQTT_SPAR02_DT_REQ = os.getenv("MQTT_SENSOR_02_DT_REQ")
MQTT_SEC01_1_DT_REQ = os.getenv("MQTT_SENSOR_03_DT_REQ")
MQTT_SEC01_2_DT_REQ = os.getenv("MQTT_SENSOR_04_DT_REQ")
MQTT_SPH01_1_DT_REQ = os.getenv("MQTT_SENSOR_05_DT_REQ")
MQTT_SPH01_2_DT_REQ = os.getenv("MQTT_SENSOR_06_DT_REQ")
MQTT_SYM01_DT_REQ = os.getenv("MQTT_SENSOR_10_DT_REQ")
MQTT_SCD41_DT_REQ = os.getenv("MQTT_SENSOR_11_DT_REQ")

SENSOR_DT_TOPICS = {
    MQTT_SLIGTH01_DT_REQ: "SLIGHT01",
    MQTT_SPAR02_DT_REQ: "SPAR02",
    MQTT_SEC01_1_DT_REQ: "SEC01_1",
    MQTT_SEC01_2_DT_REQ: "SEC01_2",
    MQTT_SPH01_1_DT_REQ: "SPH01_1",
    MQTT_SPH01_2_DT_REQ: "SPH01_2",
    MQTT_SYM01_DT_REQ: "SYM01",
    MQTT_SCD41_DT_REQ: "SCD41",
}

# MQTT command (cmd) topics
# Relays #
MQTT_RELAY_01_CMD_REQ = os.getenv("MQTT_RELAY_01_CMD_REQ")
MQTT_RELAY_02_CMD_REQ = os.getenv("MQTT_RELAY_02_CMD_REQ")
MQTT_RELAY_03_CMD_REQ = os.getenv("MQTT_RELAY_03_CMD_REQ")
MQTT_RELAY_04_CMD_REQ = os.getenv("MQTT_RELAY_04_CMD_REQ")
MQTT_RELAY_05_CMD_REQ = os.getenv("MQTT_RELAY_05_CMD_REQ")
MQTT_RELAY_06_CMD_REQ = os.getenv("MQTT_RELAY_06_CMD_REQ")
MQTT_RELAY_07_CMD_REQ = os.getenv("MQTT_RELAY_07_CMD_REQ")
MQTT_RELAY_08_CMD_REQ = os.getenv("MQTT_RELAY_08_CMD_REQ")
MQTT_RELAY_09_CMD_REQ = os.getenv("MQTT_RELAY_09_CMD_REQ")
MQTT_RELAY_10_CMD_REQ = os.getenv("MQTT_RELAY_10_CMD_REQ")
MQTT_RELAY_11_CMD_REQ = os.getenv("MQTT_RELAY_11_CMD_REQ")
MQTT_RELAY_12_CMD_REQ = os.getenv("MQTT_RELAY_12_CMD_REQ")
MQTT_RELAY_13_CMD_REQ = os.getenv("MQTT_RELAY_13_CMD_REQ")
MQTT_RELAY_14_CMD_REQ = os.getenv("MQTT_RELAY_14_CMD_REQ")
MQTT_RELAY_15_CMD_REQ = os.getenv("MQTT_RELAY_15_CMD_REQ")
MQTT_RELAY_16_CMD_REQ = os.getenv("MQTT_RELAY_16_CMD_REQ")

RELAY_CMD_TOPICS = [
    MQTT_RELAY_01_CMD_REQ,
    MQTT_RELAY_02_CMD_REQ,
    MQTT_RELAY_03_CMD_REQ,
    MQTT_RELAY_04_CMD_REQ,
    MQTT_RELAY_05_CMD_REQ,
    MQTT_RELAY_06_CMD_REQ,
    MQTT_RELAY_07_CMD_REQ,
    MQTT_RELAY_08_CMD_REQ,
    MQTT_RELAY_09_CMD_REQ,
    MQTT_RELAY_10_CMD_REQ,
    MQTT_RELAY_11_CMD_REQ,
    MQTT_RELAY_12_CMD_REQ,
    MQTT_RELAY_13_CMD_REQ,
    MQTT_RELAY_14_CMD_REQ,
    MQTT_RELAY_15_CMD_REQ,
    MQTT_RELAY_16_CMD_REQ,
]

# Sensors #
MQTT_SEC01_1_CMD_REQ = os.getenv("MQTT_SENSOR_03_CMD_REQ")
MQTT_SEC01_2_CMD_REQ = os.getenv("MQTT_SENSOR_04_CMD_REQ")
MQTT_SPH01_1_CMD_REQ = os.getenv("MQTT_SENSOR_05_CMD_REQ")
MQTT_SPH01_2_CMD_REQ = os.getenv("MQTT_SENSOR_06_CMD_REQ")

SENSOR_CMD_TOPICS = [
    MQTT_SEC01_1_CMD_REQ,
    MQTT_SEC01_2_CMD_REQ,
    MQTT_SPH01_1_CMD_REQ,
    MQTT_SPH01_2_CMD_REQ,
]

# Grow Lamp Elixia #
LAMP_01_IP = os.getenv("LAMP_01_IP")
MQTT_LAMP_01_CMD_REQ = os.getenv("MQTT_LAMP_01_CMD_REQ")
MQTT_LAMP_01_DT_REQ = os.getenv("MQTT_LAMP_01_DT_REQ")
# Group lamp topics for convenience
LAMP_TOPICS = [MQTT_LAMP_01_CMD_REQ, MQTT_LAMP_01_DT_REQ]
# Dictionary to hold instantiated sensor objects
SENSORS = {}
# Update IP of lamp
grow_lamp_elixia_initialization.lamp_1.update_ip_address(LAMP_01_IP)

# Configure MQTT
def on_connect(client, userdata, flags, rc):
    logging.info("Connected with code %s", rc)
    # Subscribe in on_connect to renew subscriptions if connection is lost
    for topic in list(SENSOR_DT_TOPICS.keys()) + SENSOR_CMD_TOPICS + RELAY_CMD_TOPICS + LAMP_TOPICS:
        client.subscribe(topic)

# Catch-all callback function for messages
def on_message(client, userdata, msg):
    logging.info("%s: %s", msg.topic, msg.payload)


def make_sensor_data_handler(name):
    def handler(client, userdata, msg):
        req_msg = json.loads(msg.payload)
        sensor = SENSORS.get(name)
        if not sensor:
            logging.error("Sensor %s not initialized", name)
            return
        try:
            res_payload = json.dumps(sensor.fetch_and_return_data())
            client.publish(req_msg["res_topic"], res_payload)
            logging.info(res_payload)
        except Exception as e:
            logging.error("%s data fetch error: %s", name, e)
    return handler

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

def on_message_SEC01_1(client, userdata, msg):
    req_msg = json.loads(msg.payload)
    try:
        res_payload = json.dumps(sensor_SEC01_1.fetch_and_return_data())
        client.publish(req_msg["res_topic"], res_payload)
        print(res_payload + "\n")
    except Exception as e:
        print("SEC01-1, data fetch error:", str(e))

def on_message_SEC01_1_CMD_REQ(client, userdata, msg):
    cmd_msg = json.loads(msg.payload)
    try:
        logging.info(cmd_msg)
        if cmd_msg["cmd"] == "calibrate_ec_1413":
            # Send calibration command to sensor
            logging.info("Registering EC 1413")
            payload = json.dumps(sensor_SEC01_1.calibrate_ec_1413us())
            client.publish(cmd_msg["res_topic"], payload)

        elif cmd_msg["cmd"] == "calibrate_ec_12880":
            # Send calibration command to sensor
            logging.info("Registering EC 12880")
            payload = json.dumps(sensor_SEC01_1.calibrate_ec_12880us())
            client.publish(cmd_msg["res_topic"], payload)
        
        elif cmd_msg["cmd"] == "set_temperature_compensation":
            # Send calibration command to sensor
            logging.info("Setting temperature compensation")
            sensor_SEC01_1.set_temperature_compensation(float(cmd_msg["value"]))

        else:
            logging.info("Invalid command")
    except Exception as e:
        logging.error("S-EC-01-1 error: %s", e)

def on_message_SEC01_2(client, userdata, msg):
    req_msg = json.loads(msg.payload)
    try:
        res_payload = json.dumps(sensor_SEC01_2.fetch_and_return_data())
        client.publish(req_msg["res_topic"], res_payload)
        print(res_payload + "\n")
    except Exception as e:
        print("SEC01-2, data fetch error:", str(e))

def on_message_SEC01_2_CMD_REQ(client, userdata, msg):
    cmd_msg = json.loads(msg.payload)
    try:
        logging.info(cmd_msg)
        if cmd_msg["cmd"] == "calibrate_ec_1413":
            # Send calibration command to sensor
            logging.info("Registering EC 1413")
            payload = json.dumps(sensor_SEC01_2.calibrate_ec_1413us())
            client.publish(cmd_msg["res_topic"], payload)

        elif cmd_msg["cmd"] == "calibrate_ec_12880":
            # Send calibration command to sensor
            logging.info("Registering EC 12880")
            payload = json.dumps(sensor_SEC01_2.calibrate_ec_12880us())
            client.publish(cmd_msg["res_topic"], payload)
        
        elif cmd_msg["cmd"] == "set_temperature_compensation":
            # Send calibration command to sensor
            logging.info("Setting temperature compensation")
            sensor_SEC01_2.set_temperature_compensation(float(cmd_msg["value"]))

        else:
            logging.info("Invalid command")
    except Exception as e:
        logging.error("S-EC-01-2 error: %s", e)

def on_message_SPH01_1(client, userdata, msg):
    req_msg = json.loads(msg.payload)
    try:
        res_payload = json.dumps(sensor_SPH01_1.fetch_and_return_data())
        client.publish(req_msg["res_topic"], res_payload)
        print(res_payload + "\n")
    except Exception as e:
        print("SPH01-1, data fetch error:", str(e))
    
def on_message_SPH01_1_CMD_REQ(client, userdata, msg):
    cmd_msg = json.loads(msg.payload)
    try:
        logging.info(cmd_msg)
        if cmd_msg["cmd"] == "calibrate_ph_0401":
            # Send calibration command to sensor
            logging.info("Registering pH 4.01")
            payload = json.dumps(sensor_SPH01_1.calibrate_ph_0401())
            client.publish(cmd_msg["res_topic"], payload)

        elif cmd_msg["cmd"] == "calibrate_ph_0700":
            # Send calibration command to sensor
            logging.info("Registering pH 7.00")
            payload = json.dumps(sensor_SPH01_1.calibrate_ph_0700())
            client.publish(cmd_msg["res_topic"], payload)

        elif cmd_msg["cmd"] == "calibrate_ph_1001":
            # Send calibration command to sensor
            logging.info("Registering pH 10.01")
            payload = json.dumps(sensor_SPH01_1.calibrate_ph_1001())
            client.publish(cmd_msg["res_topic"], payload)

        elif cmd_msg["cmd"] == "set_temperature_compensation":
            # Send calibration command to sensor
            logging.info("Setting temperature compensation")
            sensor_SPH01_1.set_temperature_compensation(float(cmd_msg["value"]))

        else:
            logging.info("Invalid command")
    except Exception as e:
        logging.error("SPH01-1 error: %s", e)

def on_message_SPH01_2(client, userdata, msg):
    req_msg = json.loads(msg.payload)
    try:
        res_payload = json.dumps(sensor_SPH01_2.fetch_and_return_data())
        client.publish(req_msg["res_topic"], res_payload)
        print(res_payload + "\n")
    except Exception as e:
        print("SPH01-2, data fetch error:", str(e))

def on_message_SPH01_2_CMD_REQ(client, userdata, msg):
    cmd_msg = json.loads(msg.payload)
    try:
        logging.info(cmd_msg)
        if cmd_msg["cmd"] == "calibrate_ph_0401":
            # Send calibration command to sensor
            logging.info("Registering pH 4.01")
            payload = json.dumps(sensor_SPH01_2.calibrate_ph_0401())
            client.publish(cmd_msg["res_topic"], payload)

        elif cmd_msg["cmd"] == "calibrate_ph_0700":
            # Send calibration command to sensor
            logging.info("Registering pH 7.00")
            payload = json.dumps(sensor_SPH01_2.calibrate_ph_0700())
            client.publish(cmd_msg["res_topic"], payload)

        elif cmd_msg["cmd"] == "calibrate_ph_1001":
            # Send calibration command to sensor
            logging.info("Registering pH 10.01")
            payload = json.dumps(sensor_SPH01_2.calibrate_ph_1001())
            client.publish(cmd_msg["res_topic"], payload)

        elif cmd_msg["cmd"] == "set_temperature_compensation":
            # Send calibration command to sensor
            logging.info("Setting temperature compensation")
            sensor_SPH01_2.set_temperature_compensation(float(cmd_msg["value"]))

        else:
            logging.info("Invalid command")
    except Exception as e:
        logging.error("SPH01-2 error: %s", e)

def on_message_SYM01(client, userdata, msg):
    req_msg = json.loads(msg.payload)
    try:
        res_payload = json.dumps(sensor_SYM01.fetch_and_return_data())
        client.publish(req_msg["res_topic"], res_payload)
        logging.info(res_payload)
    except Exception as e:
        logging.error("SYM01, data fetch error: %s", e)

def on_message_SCD41(client, userdata, msg):
    req_msg = json.loads(msg.payload)
    try:
        res_payload = json.dumps(sensor_SCD41_I2C.fetch_and_return_data())
        client.publish(req_msg["res_topic"], res_payload, )
        logging.info(res_payload)
    except Exception as e:
        logging.error("SCD41, data fetch error: %s", e)


# Setup MQTT client for sensor host
client = mqtt.Client()

# Assign the generic callback functions for the client
client.on_connect = on_connect
client.on_message = on_message

# Assign the specific callback functions for the client
# Sensors data requests
for topic, name in SENSOR_DT_TOPICS.items():
    client.message_callback_add(topic, make_sensor_data_handler(name))
# Sensor command callbacks
client.message_callback_add(MQTT_SEC01_1_CMD_REQ, on_message_SEC01_1_CMD_REQ)
client.message_callback_add(MQTT_SEC01_2_CMD_REQ, on_message_SEC01_2_CMD_REQ)
client.message_callback_add(MQTT_SPH01_1_CMD_REQ, on_message_SPH01_1_CMD_REQ)
client.message_callback_add(MQTT_SPH01_2_CMD_REQ, on_message_SPH01_2_CMD_REQ)

# Actuators #
client.message_callback_add(MQTT_RELAY_01_CMD_REQ, relay_devices_initialization.on_message_RLY01)
client.message_callback_add(MQTT_RELAY_02_CMD_REQ, relay_devices_initialization.on_message_RLY02)
client.message_callback_add(MQTT_RELAY_03_CMD_REQ, relay_devices_initialization.on_message_RLY03)
client.message_callback_add(MQTT_RELAY_04_CMD_REQ, relay_devices_initialization.on_message_RLY04)
client.message_callback_add(MQTT_RELAY_05_CMD_REQ, relay_devices_initialization.on_message_RLY05)
client.message_callback_add(MQTT_RELAY_06_CMD_REQ, relay_devices_initialization.on_message_RLY06)
client.message_callback_add(MQTT_RELAY_07_CMD_REQ, relay_devices_initialization.on_message_RLY07)
client.message_callback_add(MQTT_RELAY_08_CMD_REQ, relay_devices_initialization.on_message_RLY08)
client.message_callback_add(MQTT_RELAY_09_CMD_REQ, relay_devices_initialization.on_message_RLY09)
client.message_callback_add(MQTT_RELAY_10_CMD_REQ, relay_devices_initialization.on_message_RLY10)
client.message_callback_add(MQTT_RELAY_11_CMD_REQ, relay_devices_initialization.on_message_RLY11)
client.message_callback_add(MQTT_RELAY_12_CMD_REQ, relay_devices_initialization.on_message_RLY12)
client.message_callback_add(MQTT_RELAY_13_CMD_REQ, relay_devices_initialization.on_message_RLY13)
client.message_callback_add(MQTT_RELAY_14_CMD_REQ, relay_devices_initialization.on_message_RLY14)
client.message_callback_add(MQTT_RELAY_15_CMD_REQ, relay_devices_initialization.on_message_RLY15)
client.message_callback_add(MQTT_RELAY_16_CMD_REQ, relay_devices_initialization.on_message_RLY16)
# Grow lamp Elixia
client.message_callback_add(MQTT_LAMP_01_CMD_REQ, grow_lamp_elixia_initialization.on_message_LAMP01_CMD_REQ)
client.message_callback_add(MQTT_LAMP_01_DT_REQ, grow_lamp_elixia_initialization.on_message_LAMP01_DT)

# Connect to the MQTT server
try:
    client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEP_ALIVE)
    client.loop_start()
except:
    logging.error("Connection failed")

# Activate SLIGHT-01 sensor
try:
    sensor_SLIGHT01 = sensor_SLIGHT01_modbus.SLIGHT01(
        portname=RS485_PORT,
        slaveaddress=int(os.getenv("SENSOR_SLIGHT01_ADDR", 1)),
        debug=False,
    )
    SENSORS["SLIGHT01"] = sensor_SLIGHT01
    logging.info(sensor_SLIGHT01)
except Exception as e:
    logging.error("SLIGHT01, error: %s", e)

# Activate SPAR-02 sensor
try:
    sensor_SPAR02 = sensor_SPAR02_modbus.SPAR02(
        portname=RS485_PORT,
        slaveaddress=int(os.getenv("SENSOR_SPAR02_ADDR", 34)),
        debug=False,
    )
    SENSORS["SPAR02"] = sensor_SPAR02
    logging.info(sensor_SPAR02)
except Exception as e:
    logging.error("SPAR02, error: %s", e)

# Activate SEC-01-1 sensor
try:
    sensor_SEC01_1 = sensor_SEC01_modbus.SEC01(
        portname=RS485_PORT,
        slaveaddress=int(os.getenv("SENSOR_SEC01_1_ADDR", 3)),
        debug=False,
    )
    SENSORS["SEC01_1"] = sensor_SEC01_1
    logging.info(sensor_SEC01_1)
except Exception as e:
    logging.error("SEC01-1, error: %s", e)

# Activate SEC-01-2 sensor
try:
    sensor_SEC01_2 = sensor_SEC01_modbus.SEC01(
        portname=RS485_PORT,
        slaveaddress=int(os.getenv("SENSOR_SEC01_2_ADDR", 4)),
        debug=False,
    )
    SENSORS["SEC01_2"] = sensor_SEC01_2
    logging.info(sensor_SEC01_2)
except Exception as e:
    logging.error("SEC01-2, error: %s", e)

# Activate SPH-01-1 sensor
try:
    sensor_SPH01_1 = sensor_SPH01_modbus.SPH01(
        portname=RS485_PORT,
        slaveaddress=int(os.getenv("SENSOR_SPH01_1_ADDR", 5)),
        debug=False,
    )
    SENSORS["SPH01_1"] = sensor_SPH01_1
    logging.info(sensor_SPH01_1)
except Exception as e:
    logging.error("SPH01-1, error: %s", e)

# Activate SPH-01-2 sensor
try:
    sensor_SPH01_2 = sensor_SPH01_modbus.SPH01(
        portname=RS485_PORT,
        slaveaddress=int(os.getenv("SENSOR_SPH01_2_ADDR", 6)),
        debug=False,
    )
    SENSORS["SPH01_2"] = sensor_SPH01_2
    logging.info(sensor_SPH01_2)
except Exception as e:
    logging.error("SPH01-2, error: %s", e)

# Activate SYM-01 sensor
try:
    sensor_SYM01 = sensor_SYM01_modbus.SYM01(
        portname=RS485_PORT,
        slaveaddress=int(os.getenv("SENSOR_SYM01_ADDR", 11)),
        debug=False,
    )
    SENSORS["SYM01"] = sensor_SYM01
    logging.info(sensor_SYM01)
except Exception as e:
    logging.error("SYM01, error: %s", e)


# Start main loop #
try:
    client.loop_forever()
except KeyboardInterrupt:
    logging.info("Keyboard interrupt")
except Exception as e:
    logging.error("Exception: %s", e)

client.loop_stop()

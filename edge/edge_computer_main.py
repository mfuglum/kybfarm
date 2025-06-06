#!/home/user1/Desktop/kybfarm/edge/venv/bin/python
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
import json
import time
from dotenv import load_dotenv
import os

from src.sensor_interfaces import (sensor_SCD41_I2C, 
                                   sensor_SYM01_modbus, 
                                   sensor_SLIGHT01_modbus,
                                   sensor_SPAR02_modbus,
                                   sensor_SEC01_modbus,
                                   sensor_SPH01_modbus,
                                   sensor_C02_VOC_modbus
                                   )
from src.actuator_instances import (relay_devices_initialization,
                                    grow_lamp_elixia_initialization) 

# Load environment variables from the .env file
load_dotenv()

# Fetch MQTT config values from .env file
MQTT_HOST = os.getenv("MOSQUITTO_BROKER_IP")
MQTT_PORT = int(os.getenv("MOSQUITTO_BROKER_PORT"))
MQTT_KEEP_ALIVE = int(os.getenv("MQTT_EDGE_KEEP_ALIVE"))

# MQTT data (dt) request (req) topics
MQTT_SLIGTH01_DT_REQ = os.getenv("MQTT_SENSOR_01_DT_REQ")
MQTT_SPAR02_DT_REQ = os.getenv("MQTT_SENSOR_02_DT_REQ")
MQTT_SEC01_1_DT_REQ = os.getenv("MQTT_SENSOR_03_DT_REQ")
MQTT_SEC01_2_DT_REQ = os.getenv("MQTT_SENSOR_04_DT_REQ")
MQTT_SPH01_1_DT_REQ = os.getenv("MQTT_SENSOR_05_DT_REQ")
MQTT_SPH01_2_DT_REQ = os.getenv("MQTT_SENSOR_06_DT_REQ")
MQTT_SYM01_DT_REQ = os.getenv("MQTT_SENSOR_10_DT_REQ")
MQTT_SCD41_DT_REQ = os.getenv("MQTT_SENSOR_11_DT_REQ")

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

# Sensors #
MQTT_SEC01_1_CMD_REQ = os.getenv("MQTT_SENSOR_03_CMD_REQ")
MQTT_SEC01_2_CMD_REQ = os.getenv("MQTT_SENSOR_04_CMD_REQ")
MQTT_SPH01_1_CMD_REQ = os.getenv("MQTT_SENSOR_05_CMD_REQ")
MQTT_SPH01_2_CMD_REQ = os.getenv("MQTT_SENSOR_06_CMD_REQ")

# Grow Lamp Elixia #
LAMP_01_IP = os.getenv("LAMP_01_IP")
MQTT_LAMP_01_CMD_REQ = os.getenv("MQTT_LAMP_01_CMD_REQ")
MQTT_LAMP_01_DT_REQ = os.getenv("MQTT_LAMP_01_DT_REQ")
# Update IP of lamp
grow_lamp_elixia_initialization.lamp_1.update_ip_address(LAMP_01_IP)

# Configure MQTT
def on_connect(client, userdata, flags, rc):
    print("Connected with code " + str(rc))
    # Subscribe in on_connect to renew subsriptions in case of lost connection
    # Sensors #
    client.subscribe(MQTT_SLIGTH01_DT_REQ)
    client.subscribe(MQTT_SPAR02_DT_REQ)
    client.subscribe(MQTT_SEC01_1_DT_REQ)
    client.subscribe(MQTT_SEC01_1_CMD_REQ)
    client.subscribe(MQTT_SEC01_2_DT_REQ)
    client.subscribe(MQTT_SEC01_2_CMD_REQ)
    client.subscribe(MQTT_SPH01_1_DT_REQ)
    client.subscribe(MQTT_SPH01_1_CMD_REQ)
    client.subscribe(MQTT_SPH01_2_DT_REQ)
    client.subscribe(MQTT_SPH01_2_CMD_REQ)
    client.subscribe(MQTT_SYM01_DT_REQ)
    client.subscribe(MQTT_SCD41_DT_REQ)

    # Actuators #
    client.subscribe(MQTT_RELAY_01_CMD_REQ)
    client.subscribe(MQTT_RELAY_02_CMD_REQ)
    client.subscribe(MQTT_RELAY_03_CMD_REQ)
    client.subscribe(MQTT_RELAY_04_CMD_REQ)
    client.subscribe(MQTT_RELAY_05_CMD_REQ)
    client.subscribe(MQTT_RELAY_06_CMD_REQ)
    client.subscribe(MQTT_RELAY_07_CMD_REQ)
    client.subscribe(MQTT_RELAY_08_CMD_REQ)
    client.subscribe(MQTT_RELAY_09_CMD_REQ)
    client.subscribe(MQTT_RELAY_10_CMD_REQ)
    client.subscribe(MQTT_RELAY_11_CMD_REQ)
    client.subscribe(MQTT_RELAY_12_CMD_REQ)
    client.subscribe(MQTT_RELAY_13_CMD_REQ)
    client.subscribe(MQTT_RELAY_14_CMD_REQ)
    client.subscribe(MQTT_RELAY_15_CMD_REQ)
    client.subscribe(MQTT_RELAY_16_CMD_REQ)
    client.subscribe(MQTT_LAMP_01_CMD_REQ)
    client.subscribe(MQTT_LAMP_01_DT_REQ)

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
        print(cmd_msg)
        if cmd_msg["cmd"] == "calibrate_ec_1413":
            # Send calibration command to sensor
            print("Registering EC 1413")
            payload = json.dumps(sensor_SEC01_1.calibrate_ec_1413us())
            client.publish(cmd_msg["res_topic"], payload)

        elif cmd_msg["cmd"] == "calibrate_ec_12880":
            # Send calibration command to sensor
            print("Registering EC 12880")
            payload = json.dumps(sensor_SEC01_1.calibrate_ec_12880us())
            client.publish(cmd_msg["res_topic"], payload)
        
        elif cmd_msg["cmd"] == "set_temperature_compensation":
            # Send calibration command to sensor
            print("Setting temperature compensation")
            sensor_SEC01_1.set_temperature_compensation(float(cmd_msg["value"]))

        else:
            print("Invalid command")
    except Exception as e:
        print("S-EC-01-1 error:", str(e))

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
        print(cmd_msg)
        if cmd_msg["cmd"] == "calibrate_ec_1413":
            # Send calibration command to sensor
            print("Registering EC 1413")
            payload = json.dumps(sensor_SEC01_2.calibrate_ec_1413us())
            client.publish(cmd_msg["res_topic"], payload)

        elif cmd_msg["cmd"] == "calibrate_ec_12880":
            # Send calibration command to sensor
            print("Registering EC 12880")
            payload = json.dumps(sensor_SEC01_2.calibrate_ec_12880us())
            client.publish(cmd_msg["res_topic"], payload)
        
        elif cmd_msg["cmd"] == "set_temperature_compensation":
            # Send calibration command to sensor
            print("Setting temperature compensation")
            sensor_SEC01_2.set_temperature_compensation(float(cmd_msg["value"]))

        else:
            print("Invalid command")
    except Exception as e:
        print("S-EC-01-2 error:", str(e))

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
        print(cmd_msg)
        if cmd_msg["cmd"] == "calibrate_ph_0401":
            # Send calibration command to sensor
            print("Registering pH 4.01")
            payload = json.dumps(sensor_SPH01_1.calibrate_ph_0401())
            client.publish(cmd_msg["res_topic"], payload)

        elif cmd_msg["cmd"] == "calibrate_ph_0700":
            # Send calibration command to sensor
            print("Registering pH 7.00")
            payload = json.dumps(sensor_SPH01_1.calibrate_ph_0700())
            client.publish(cmd_msg["res_topic"], payload)

        elif cmd_msg["cmd"] == "calibrate_ph_1001":
            # Send calibration command to sensor
            print("Registering pH 10.01")
            payload = json.dumps(sensor_SPH01_1.calibrate_ph_1001())
            client.publish(cmd_msg["res_topic"], payload)

        elif cmd_msg["cmd"] == "set_temperature_compensation":
            # Send calibration command to sensor
            print("Setting temperature compensation")
            sensor_SPH01_1.set_temperature_compensation(float(cmd_msg["value"]))

        else:
            print("Invalid command")
    except Exception as e:
        print("SPH01-1 error:", str(e))

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
        print(cmd_msg)
        if cmd_msg["cmd"] == "calibrate_ph_0401":
            # Send calibration command to sensor
            print("Registering pH 4.01")
            payload = json.dumps(sensor_SPH01_2.calibrate_ph_0401())
            client.publish(cmd_msg["res_topic"], payload)

        elif cmd_msg["cmd"] == "calibrate_ph_0700":
            # Send calibration command to sensor
            print("Registering pH 7.00")
            payload = json.dumps(sensor_SPH01_2.calibrate_ph_0700())
            client.publish(cmd_msg["res_topic"], payload)

        elif cmd_msg["cmd"] == "calibrate_ph_1001":
            # Send calibration command to sensor
            print("Registering pH 10.01")
            payload = json.dumps(sensor_SPH01_2.calibrate_ph_1001())
            client.publish(cmd_msg["res_topic"], payload)

        elif cmd_msg["cmd"] == "set_temperature_compensation":
            # Send calibration command to sensor
            print("Setting temperature compensation")
            sensor_SPH01_2.set_temperature_compensation(float(cmd_msg["value"]))

        else:
            print("Invalid command")
    except Exception as e:
        print("SPH01-2 error:", str(e))

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

def on_message_C02_VOC(client, userdata, msg):
    req_msg = json.loads(msg.payload)
    try:
        res_payload = json.dumps(sensor_C02_VOC.fetch_and_return_data())
        client.publish(req_msg["res_topic"], res_payload, )
        print(res_payload + "\n")
    except Exception as e:
        print("SCD41, data fetch error:", str(e))


# Setup MQTT client for sensor host
client = mqtt.Client()

# Assign the generic callback functions for the client
client.on_connect = on_connect
client.on_message = on_message

# Assign the specific callback functions for the client
# Sensors #
client.message_callback_add(MQTT_SLIGTH01_DT_REQ, on_message_SLIGHT01)
client.message_callback_add(MQTT_SPAR02_DT_REQ, on_message_SPAR02)
client.message_callback_add(MQTT_SEC01_1_DT_REQ, on_message_SEC01_1)
client.message_callback_add(MQTT_SEC01_1_CMD_REQ, on_message_SEC01_1_CMD_REQ)
client.message_callback_add(MQTT_SEC01_2_DT_REQ, on_message_SEC01_2)
client.message_callback_add(MQTT_SEC01_2_CMD_REQ, on_message_SEC01_2_CMD_REQ)
client.message_callback_add(MQTT_SPH01_1_DT_REQ, on_message_SPH01_1)
client.message_callback_add(MQTT_SPH01_1_CMD_REQ, on_message_SPH01_1_CMD_REQ)
client.message_callback_add(MQTT_SPH01_2_DT_REQ, on_message_SPH01_2)
client.message_callback_add(MQTT_SPH01_2_CMD_REQ, on_message_SPH01_2_CMD_REQ)
client.message_callback_add(MQTT_SYM01_DT_REQ, on_message_SYM01)
client.message_callback_add(MQTT_SCD41_DT_REQ,on_message_C02_VOC)

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
    print("\nConnection failed\n")

# Activate SLIGHT-01 sensor
try:
    sensor_SLIGHT01 = sensor_SLIGHT01_modbus.SLIGHT01(  portname='/dev/ttySC1',
                                                        slaveaddress=1, 
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

# Activate SEC-01-1 sensor
try: 
    sensor_SEC01_1 = sensor_SEC01_modbus.SEC01(   portname='/dev/ttySC1',
                                                  slaveaddress=3, 
                                                  debug=False)
    print(sensor_SEC01_1)
except Exception as e:
    print("SEC01-1, error:", str(e))

# Activate SEC-01-2 sensor
try: 
    sensor_SEC01_2 = sensor_SEC01_modbus.SEC01(   portname='/dev/ttySC1',
                                                  slaveaddress=4, 
                                                  debug=False)
    print(sensor_SEC01_2)
except Exception as e:
    print("SEC01-2, error:", str(e))

# Activate SPH-01-1 sensor
try:
    sensor_SPH01_1 = sensor_SPH01_modbus.SPH01(   portname='/dev/ttySC1',
                                                  slaveaddress=5,
                                                  debug=False)
    print(sensor_SPH01_1)
except Exception as e:
    print("SPH01-1, error:", str(e))

# Activate SPH-01-2 sensor
try:
    sensor_SPH01_2 = sensor_SPH01_modbus.SPH01(   portname='/dev/ttySC1',
                                                  slaveaddress=6, 
                                                  debug=False)
    print(sensor_SPH01_2)
except Exception as e:
    print("SPH01-2, error:", str(e))

# Activate SYM-01 sensor
try:
    sensor_SYM01 = sensor_SYM01_modbus.SYM01(   portname='/dev/ttySC1',
                                                slaveaddress=11, 
                                                debug=False)
    print(sensor_SYM01)
except Exception as e:
    print("SYM01, error:", str(e))

try:
    sensor_C02_VOC = sensor_C02_VOC_modbus.CO2_VOC(   portname='/dev/ttySC1',
                                                slaveaddress=7, 
                                                debug=False)
    print(sensor_C02_VOC)
except Exception as e:
    print("C02_VOC, error:", str(e))



# Start main loop #
try:
    # Main loop
    while True:
        time.sleep(15)
except KeyboardInterrupt:
    print("Keyboard interrupt")
except Exception as e:
    print("\nException, error: ", str(e))

client.loop_stop()

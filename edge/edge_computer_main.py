#!/home/user1/kybfarm/edge/venv/bin/python
"""
╔══════════════════════════════════════════════════════════════════════════╗
║               KYBFarm Edge Computer Main Controller Script               ║
╠══════════════════════════════════════════════════════════════════════════╣
║ This script runs on the edge computer (e.g., Jetson Nano / Raspberry Pi).║
║                                                                          ║
║ It performs the following tasks:                                         ║
║ • Subscribes to MQTT data and command topics                             ║
║ • Interacts with Modbus and I²C sensors and actuators                    ║
║ • Publishes sensor data and system responses over MQTT                   ║
║                                                                          ║
║ Setup Instructions:                                                      ║
║   cd kybfarm/edge                                                        ║
║   python3 -m venv venv                                                   ║
║   source venv/bin/activate                                               ║
║   pip install -r requirements.txt                                        ║
║   python edge_computer_main.py                                           ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

# ───────────────────────────── System / Third-Party Imports ───────────────────────────── #
import os
import time
import json
from dotenv import load_dotenv
import paho.mqtt.client as mqtt

# ───────────────────────────────────── Sensor Modules ──────────────────────────────────── #
from src.sensor_interfaces import (
    sensor_SYM01_modbus,
    sensor_SPAR02_modbus,
    sensor_SEC01_modbus,
    sensor_SPH01_modbus,
    sensor_CO2_VOC_modbus,
    sensor_STH01_modbus,
    sensor_BMP280_I2C,
    sensor_SCD41_I2C
)

# ───────────────────────────────────── Actuator Modules ────────────────────────────────── #
from src.actuator_instances import (
    relay_devices_initialization,
    grow_lamp_elixia_initialization,
    voltage_output,
    solid_state_relay,
    CO2_control
)

# ────────────────────────────────────── PID State Buffer ───────────────────────────────── #
from src.utils.latest_pid_data import (
    latest_heating_data,
    latest_humidity_data,
    latest_CO2_data
)

# ───────────────────────────── Load Environment ───────────────────────────── #
load_dotenv()

# ───────────────────────────── MQTT Broker Config ─────────────────────────── #
MQTT_HOST         = os.getenv("MOSQUITTO_BROKER_IP")
MQTT_PORT         = int(os.getenv("MOSQUITTO_BROKER_PORT", 1883))
MQTT_KEEP_ALIVE   = int(os.getenv("MQTT_EDGE_KEEP_ALIVE", 60))

# ───────────── Sensor Data Request Topics (DT_REQ) ───────────── #
MQTT_DT_REQ = {
    "ec_gt1":     os.getenv("MQTT_DT_REQ_EC_GT1"),
    "ec_gt2":     os.getenv("MQTT_DT_REQ_EC_GT2"),
    "ec_mx":      os.getenv("MQTT_DT_REQ_EC_MX"),
    "ph_gt1":     os.getenv("MQTT_DT_REQ_PH_GT1"),
    "ph_gt2":     os.getenv("MQTT_DT_REQ_PH_GT2"),
    "ph_mx":      os.getenv("MQTT_DT_REQ_PH_MX"),
    "par02_1":    os.getenv("MQTT_DT_REQ_PAR02_1"),
    "par02_2":    os.getenv("MQTT_DT_REQ_PAR02_2"),
    "sth01_1":    os.getenv("MQTT_DT_REQ_STH01_1"),
    "sth01_2":    os.getenv("MQTT_DT_REQ_STH01_2"),
    "co2voc":     os.getenv("MQTT_DT_REQ_CO2VOC"),
    "sym01":      os.getenv("MQTT_DT_REQ_SYM01")  
}

# ───────────── Sensor Command Request Topics (CMD_REQ) ───────────── #
MQTT_CMD_REQ = {
    "ec_gt1": os.getenv("MQTT_CMD_REQ_EC_GT1"),
    "ec_gt2": os.getenv("MQTT_CMD_REQ_EC_GT2"),
    "ec_mx":  os.getenv("MQTT_CMD_REQ_EC_MX"),
    "ph_gt1": os.getenv("MQTT_CMD_REQ_PH_GT1"),
    "ph_gt2": os.getenv("MQTT_CMD_REQ_PH_GT2"),
    "ph_mx":  os.getenv("MQTT_CMD_REQ_PH_MX")
}


# ───────────── Relay Control Topics ───────────── #
MQTT_RELAY_CMD = {
    1:  os.getenv("MQTT_RELAY_01_CMD_REQ"),
    2:  os.getenv("MQTT_RELAY_02_CMD_REQ"),
    3:  os.getenv("MQTT_RELAY_03_CMD_REQ"),
    4:  os.getenv("MQTT_RELAY_04_CMD_REQ"),
    5:  os.getenv("MQTT_RELAY_05_CMD_REQ"),
    6:  os.getenv("MQTT_RELAY_06_CMD_REQ"),
    7:  os.getenv("MQTT_RELAY_07_CMD_REQ"),
    8:  os.getenv("MQTT_RELAY_08_CMD_REQ"),
    9:  os.getenv("MQTT_RELAY_09_CMD_REQ"),
    10: os.getenv("MQTT_RELAY_10_CMD_REQ"),
    11: os.getenv("MQTT_RELAY_11_CMD_REQ"),
    12: os.getenv("MQTT_RELAY_12_CMD_REQ"),
    13: os.getenv("MQTT_RELAY_13_CMD_REQ"),
    14: os.getenv("MQTT_RELAY_14_CMD_REQ"),
    15: os.getenv("MQTT_RELAY_15_CMD_REQ"),
    16: os.getenv("MQTT_RELAY_16_CMD_REQ"),
}

# ───────────── Solid State Relay Topic ───────────── #
MQTT_SSR_CMD = os.getenv("MQTT_SOLID_STATE_RELAY_01_CMD_REQ")


# ───────────── Grow Lamp 1 (Elixia) ───────────── #
LAMP_01_IP             = os.getenv("LAMP_01_IP")
MQTT_LAMP_01_CMD_REQ   = os.getenv("MQTT_LAMP_01_CMD_REQ")
MQTT_LAMP_01_DT_REQ    = os.getenv("MQTT_LAMP_01_DT_REQ")
grow_lamp_elixia_initialization.lamp_1.update_ip_address(LAMP_01_IP)

# ───────────── Grow Lamp 2 (Elixia) ───────────── #
LAMP_02_IP             = os.getenv("LAMP_02_IP")
MQTT_LAMP_02_CMD_REQ   = os.getenv("MQTT_LAMP_02_CMD_REQ")
MQTT_LAMP_02_DT_REQ    = os.getenv("MQTT_LAMP_02_DT_REQ")
grow_lamp_elixia_initialization.lamp_2.update_ip_address(LAMP_02_IP)

# ───────────── PID Enable Topics ───────────── #
MQTT_PID_CMD = {
    "cooling": os.getenv("MQTT_COOLING_PID_ENABLE_CMD_REQ"),
    "heating": os.getenv("MQTT_HEATING_PID_ENABLE_CMD_REQ"),
    "co2":     os.getenv("MQTT_CO2_PID_ENABLE_CMD_REQ")
}

# ───────────── Voltage-Controlled Devices (0–10 V) ───────────── #
MQTT_VOLTAGE_CMD = {
    "fan_cmd":    os.getenv("MQTT_FAN_VOLTAGE_CMD_REQ"),
    "fan_res":    os.getenv("MQTT_FAN_VOLTAGE_CMD_RES"),
    "valve_cmd":  os.getenv("MQTT_VALVE_VOLTAGE_CMD_REQ"),
    "valve_res":  os.getenv("MQTT_VALVE_VOLTAGE_CMD_RES")
}

# ───────────── Setpoints (From Home Assistant) ───────────── #
MQTT_REF_CMDS = {
    "humidity_req": os.getenv("MQTT_REF_HUMID_CMD_REQ"),
    "humidity_res": os.getenv("MQTT_REF_HUMID_CMD_RES"),
    "temp_req":     os.getenv("MQTT_REF_TEMP_CMD_REQ"),
    "temp_res":     os.getenv("MQTT_REF_TEMP_CMD_RES"),
    "co2_req":      os.getenv("MQTT_REF_CO2_CMD_REQ"),
    "co2_res":      os.getenv("MQTT_REF_CO2_CMD_RES")
}

# ─────────────── MQTT Connection Handler ─────────────── #
def on_connect(client, userdata, flags, rc):
    print("Connected with code " + str(rc))

    # Subscribe in on_connect to renew subscriptions in case of lost connection
    # Sensors #
    for topic in MQTT_DT_REQ.values():
        client.subscribe(topic)

    for topic in MQTT_CMD_REQ.values():
        client.subscribe(topic)

    # Actuators #
    for topic in MQTT_RELAY_CMD.values():
        client.subscribe(topic)

    client.subscribe(MQTT_SSR_CMD)
    client.subscribe(MQTT_LAMP_01_CMD_REQ)
    client.subscribe(MQTT_LAMP_01_DT_REQ)
    client.subscribe(MQTT_LAMP_02_CMD_REQ)
    client.subscribe(MQTT_LAMP_02_DT_REQ)

    for topic in MQTT_REF_CMDS.values():
        client.subscribe(topic)

    # 0 - 10V control
    for topic in MQTT_VOLTAGE_CMD.values():
        client.subscribe(topic)

    # PID Enable
    for topic in MQTT_PID_CMD.values():
        client.subscribe(topic)


# ───────────────────────────── Activate Sensors ───────────────────────────── #

sensor_specs = {
        "par_gt1": (sensor_SPAR02_modbus.SPAR02, '/dev/ttySC1', 1),
        "par_gt2": (sensor_SPAR02_modbus.SPAR02, '/dev/ttySC1', 34),

        "ec_gt1":  (sensor_SEC01_modbus.SEC01, '/dev/ttySC1', 6),
        "ec_gt2":  (sensor_SEC01_modbus.SEC01, '/dev/ttySC1', 5),
        "ec_mx":   (sensor_SEC01_modbus.SEC01, '/dev/ttySC1', 7),

        "ph_gt1":  (sensor_SPH01_modbus.SPH01, '/dev/ttySC1', 8),
        "ph_gt2":  (sensor_SPH01_modbus.SPH01, '/dev/ttySC1', 9),
        "ph_mx":   (sensor_SPH01_modbus.SPH01, '/dev/ttySC1', 10),

        "sym01":   (sensor_SYM01_modbus.SYM01, '/dev/ttySC1', 12),
        "co2voc":  (sensor_CO2_VOC_modbus.CO2_VOC, '/dev/ttySC0', 7),

        "sth01_1": (sensor_STH01_modbus.STH01, '/dev/ttySC0', 69),
        "sth01_2": (sensor_STH01_modbus.STH01, '/dev/ttySC0', 70),
    }

sensors = {}

for label, (cls, port, addr) in sensor_specs.items():
    try:
        sensor = cls(portname=port, slaveaddress=addr, debug=False)
        sensors[label] = sensor
        print(f"{label} initialized: {sensor}")
    except Exception as e:
        print(f"{label} init error:", str(e))
    time.sleep(0.1)


# ─────────────── callback functions ─────────────── #
def on_message(client, userdata, msg):
    print("\n" + msg.topic + ":\n", msg.payload)


def sensor_handler(sensor_obj, label):
    def on_data(client, userdata, msg):
        req_msg = json.loads(msg.payload)
        try:
            data = sensor_obj.fetch_and_return_data()
            res_payload = json.dumps(data)
            client.publish(req_msg["res_topic"], res_payload)

            if label == "co2voc":
                latest_heating_data[label] = data["fields"]["temperature"]
                latest_CO2_data[label] = data["fields"]["co2"]
            elif label in ["sth01_1", "sth01_2"]:
                latest_heating_data[label] = data["fields"]["temperature"]
                latest_humidity_data[label] = data["fields"]["humidity"]

            print(f"{label} →", res_payload + "\n")
        except Exception as e:
            print(f"{label}, data fetch error:", str(e))

    def on_cmd_ec(client, userdata, msg):
        cmd_msg = json.loads(msg.payload)
        try:
            print(cmd_msg)
            if cmd_msg["cmd"] == "calibrate_ec_1413":
                payload = json.dumps(sensor_obj.calibrate_ec_1413us())
                client.publish(cmd_msg["res_topic"], payload)
            elif cmd_msg["cmd"] == "calibrate_ec_12880":
                payload = json.dumps(sensor_obj.calibrate_ec_12880us())
                client.publish(cmd_msg["res_topic"], payload)
            elif cmd_msg["cmd"] == "set_temperature_compensation":
                sensor_obj.set_temperature_compensation(float(cmd_msg["value"]))
            else:
                print("Invalid EC command")
        except Exception as e:
            print(f"{label}, EC command error:", str(e))

    def on_cmd_ph(client, userdata, msg):
        cmd_msg = json.loads(msg.payload)
        try:
            print(cmd_msg)
            if cmd_msg["cmd"] == "calibrate_ph_0401":
                payload = json.dumps(sensor_obj.calibrate_ph_0401())
                client.publish(cmd_msg["res_topic"], payload)
            elif cmd_msg["cmd"] == "calibrate_ph_0700":
                payload = json.dumps(sensor_obj.calibrate_ph_0700())
                client.publish(cmd_msg["res_topic"], payload)
            elif cmd_msg["cmd"] == "calibrate_ph_1001":
                payload = json.dumps(sensor_obj.calibrate_ph_1001())
                client.publish(cmd_msg["res_topic"], payload)
            elif cmd_msg["cmd"] == "set_temperature_compensation":
                sensor_obj.set_temperature_compensation(float(cmd_msg["value"]))
            else:
                print("Invalid pH command")
        except Exception as e:
            print(f"{label}, pH command error:", str(e))

    # Determine what to return based on sensor type
    if label.startswith("ec_"):
        return {"data": on_data, "cmd": on_cmd_ec}
    elif label.startswith("ph_"):
        return {"data": on_data, "cmd": on_cmd_ph}
    else:
        return {"data": on_data}

# PAR sensors (data only)
on_message_par02_1 = sensor_handler(sensors["par_gt1"], "par_gt1")["data"]
on_message_par02_2 = sensor_handler(sensors["par_gt2"], "par_gt2")["data"]

# EC sensors (data + command)
on_message_ec_gt1 = sensor_handler(sensors["ec_gt1"], "ec_gt1")["data"]
on_message_ec_gt1_cmd = sensor_handler(sensors["ec_gt1"], "ec_gt1")["cmd"]

on_message_ec_gt2 = sensor_handler(sensors["ec_gt2"], "ec_gt2")["data"]
on_message_ec_gt2_cmd = sensor_handler(sensors["ec_gt2"], "ec_gt2")["cmd"]

on_message_ec_mx = sensor_handler(sensors["ec_mx"], "ec_mx")["data"]
on_message_ec_mx_cmd = sensor_handler(sensors["ec_mx"], "ec_mx")["cmd"]

# pH sensors (data + command)
on_message_ph_gt1 = sensor_handler(sensors["ph_gt1"], "ph_gt1")["data"]
on_message_ph_gt1_cmd = sensor_handler(sensors["ph_gt1"], "ph_gt1")["cmd"]

on_message_ph_gt2 = sensor_handler(sensors["ph_gt2"], "ph_gt2")["data"]
on_message_ph_gt2_cmd = sensor_handler(sensors["ph_gt2"], "ph_gt2")["cmd"]

on_message_ph_mx = sensor_handler(sensors["ph_mx"], "ph_mx")["data"]
on_message_ph_mx_cmd = sensor_handler(sensors["ph_mx"], "ph_mx")["cmd"]

# SYM (data only)
on_message_SYM01 = sensor_handler(sensors["sym01"], "sym01")["data"]

# CO₂ VOC (data only)
on_message_CO2_VOC_1 = sensor_handler(sensors["co2voc"], "co2voc")["data"]

# STH sensors (data only)
on_message_sth01_1 = sensor_handler(sensors["sth01_1"], "sth01_1")["data"]
on_message_sth01_2 = sensor_handler(sensors["sth01_2"], "sth01_2")["data"]


#PDI
def create_pid_handler(label, run_function, data_source):
    def handler(client, userdata, msg):
        cmd_msg = json.loads(msg.payload)
        try:
            print(cmd_msg)
            if cmd_msg.get("cmd") == "pid_enable":
                print(f"Enabling {label} PID")
                print(f"Latest {label} data:", data_source)
                run_function()
            else:
                print("Invalid command")
        except Exception as e:
            print(f"{label.upper()} PID error:", str(e))
    return handler

on_message_COOLING_PID_CMD_REQ = create_pid_handler(
    "cooling", voltage_output.run_pid, latest_humidity_data
)

on_message_HEATING_PID_CMD_REQ = create_pid_handler(
    "heating", solid_state_relay.run_heating_pid, latest_heating_data
)

on_message_CO2_PID_CMD_REQ = create_pid_handler(
    "co2", CO2_control.run_CO2_pid, latest_CO2_data
)


# Setup MQTT client for sensor host
client = mqtt.Client()

# Assign the generic callback functions for the client
client.on_connect = on_connect
client.on_message = on_message

# Sensors #
# EC sensors
client.message_callback_add(MQTT_DT_REQ["ec_gt1"], on_message_ec_gt1)
client.message_callback_add(MQTT_CMD_REQ["ec_gt1"], on_message_ec_gt1_cmd)
client.message_callback_add(MQTT_DT_REQ["ec_gt2"], on_message_ec_gt2)
client.message_callback_add(MQTT_CMD_REQ["ec_gt2"], on_message_ec_gt2_cmd)
client.message_callback_add(MQTT_DT_REQ["ec_mx"],  on_message_ec_mx)
client.message_callback_add(MQTT_CMD_REQ["ec_mx"],  on_message_ec_mx_cmd)

# pH sensors
client.message_callback_add(MQTT_DT_REQ["ph_gt1"], on_message_ph_gt1)
client.message_callback_add(MQTT_CMD_REQ["ph_gt1"], on_message_ph_gt1_cmd)
client.message_callback_add(MQTT_DT_REQ["ph_gt2"], on_message_ph_gt2)
client.message_callback_add(MQTT_CMD_REQ["ph_gt2"], on_message_ph_gt2_cmd)
client.message_callback_add(MQTT_DT_REQ["ph_mx"],  on_message_ph_mx)
client.message_callback_add(MQTT_CMD_REQ["ph_mx"],  on_message_ph_mx_cmd)

# STH01 sensors
client.message_callback_add(MQTT_DT_REQ["sth01_1"], on_message_sth01_1)
client.message_callback_add(MQTT_DT_REQ["sth01_2"], on_message_sth01_2)

# PAR sensors (assuming callbacks are defined)
client.message_callback_add(MQTT_DT_REQ["par02_1"], on_message_par02_1)
client.message_callback_add(MQTT_DT_REQ["par02_2"], on_message_par02_2)

# CO₂ VOC sensor
client.message_callback_add(MQTT_DT_REQ["co2voc"], on_message_CO2_VOC_1)

# SYM flow sensor
client.message_callback_add(MQTT_DT_REQ["sym01"], on_message_SYM01)


# Actuators #
# Relays
client.message_callback_add(MQTT_RELAY_CMD[1],  relay_devices_initialization.on_message_RLY01)
client.message_callback_add(MQTT_RELAY_CMD[2],  relay_devices_initialization.on_message_RLY02)
client.message_callback_add(MQTT_RELAY_CMD[3],  relay_devices_initialization.on_message_RLY03)
client.message_callback_add(MQTT_RELAY_CMD[4],  relay_devices_initialization.on_message_RLY04)
client.message_callback_add(MQTT_RELAY_CMD[5],  relay_devices_initialization.on_message_RLY05)
client.message_callback_add(MQTT_RELAY_CMD[6],  relay_devices_initialization.on_message_RLY06)
client.message_callback_add(MQTT_RELAY_CMD[7],  relay_devices_initialization.on_message_RLY07)
client.message_callback_add(MQTT_RELAY_CMD[8],  relay_devices_initialization.on_message_RLY08)
client.message_callback_add(MQTT_RELAY_CMD[9],  relay_devices_initialization.on_message_RLY09)
client.message_callback_add(MQTT_RELAY_CMD[10], relay_devices_initialization.on_message_RLY10)
client.message_callback_add(MQTT_RELAY_CMD[11], relay_devices_initialization.on_message_RLY11)
client.message_callback_add(MQTT_RELAY_CMD[12], relay_devices_initialization.on_message_RLY12)
client.message_callback_add(MQTT_RELAY_CMD[13], relay_devices_initialization.on_message_RLY13)
client.message_callback_add(MQTT_RELAY_CMD[14], relay_devices_initialization.on_message_RLY14)
client.message_callback_add(MQTT_RELAY_CMD[15], relay_devices_initialization.on_message_RLY15)
client.message_callback_add(MQTT_RELAY_CMD[16], relay_devices_initialization.on_message_RLY16)

# Solid state relay
client.message_callback_add(MQTT_SSR_CMD, relay_devices_initialization.on_message_SSR01)

# Voltage output
#Fan
client.message_callback_add(MQTT_VOLTAGE_CMD["fan_cmd"], voltage_output.on_message_FAN_VOLTAGE_CMD_REQ)

#Valve
client.message_callback_add(MQTT_VOLTAGE_CMD["valve_cmd"], voltage_output.on_message_VALVE_VOLTAGE_CMD_REQ)


# Grow lamp1 Elixia
client.message_callback_add(MQTT_LAMP_01_CMD_REQ, grow_lamp_elixia_initialization.on_message_LAMP01_CMD_REQ)
client.message_callback_add(MQTT_LAMP_01_DT_REQ, grow_lamp_elixia_initialization.on_message_LAMP01_DT)
# Grow lamp2 Elixia
client.message_callback_add(MQTT_LAMP_02_CMD_REQ, grow_lamp_elixia_initialization.on_message_LAMP02_CMD_REQ)
client.message_callback_add(MQTT_LAMP_02_DT_REQ, grow_lamp_elixia_initialization.on_message_LAMP02_DT)

# ───────────── PID Control & Setpoints ───────────── #

# Cooling PID
client.message_callback_add(MQTT_PID_CMD["cooling"], on_message_COOLING_PID_CMD_REQ)
client.message_callback_add(MQTT_REF_CMDS["humidity_req"], voltage_output.on_message_REFHUMID_CMD_REQ)
client.message_callback_add(MQTT_REF_CMDS["humidity_res"], voltage_output.on_message_REFHUMID_CMD_REQ)

# Heating PID
client.message_callback_add(MQTT_PID_CMD["heating"], on_message_HEATING_PID_CMD_REQ)
client.message_callback_add(MQTT_REF_CMDS["temp_req"], solid_state_relay.on_message_REFTEMP_CMD_REQ)
client.message_callback_add(MQTT_REF_CMDS["temp_res"], solid_state_relay.on_message_REFTEMP_CMD_REQ)

# CO₂ PID
client.message_callback_add(MQTT_PID_CMD["co2"], on_message_CO2_PID_CMD_REQ)
client.message_callback_add(MQTT_REF_CMDS["co2_req"], CO2_control.on_message_REFCO2_CMD_REQ)
client.message_callback_add(MQTT_REF_CMDS["co2_res"], CO2_control.on_message_REFCO2_CMD_REQ)


# Connect to the MQTT server
try:
    client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEP_ALIVE)
    client.loop_start()
except:
    print("\nConnection failed\n")


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
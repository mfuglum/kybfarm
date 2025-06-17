#!/home/user1/kybfarm/edge/venv/bin/python
"""
╔══════════════════════════════════════════════════════════════════════════╗
║               KYBFarm Edge Computer Main Controller Script               ║
╠══════════════════════════════════════════════════════════════════════════╣
║ This script runs on the edge computer (e.g., Jetson Nano/RPi). It:       ║
║ • Subscribes to MQTT data and command topics                             ║
║ • Interacts with Modbus sensors and actuators                            ║
║ • Publishes sensor data and system responses over MQTT                   ║
║                                                                          ║
║ Setup:                                                                   ║
║   cd kybfarm/edge                                                        ║
║   python3 -m venv venv                                                   ║
║   source venv/bin/activate                                               ║
║   pip install -r requirements.txt                                        ║
║   python edge_computer_main.py                                           ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

# ─────────────────────── System / Third-Party Imports ─────────────────────── #
import os
import time
import json
from dotenv import load_dotenv
import paho.mqtt.client as mqtt

# ──────────────────────────────── Sensor Modules ───────────────────────────── #
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

# ─────────────────────────────── Actuator Modules ──────────────────────────── #
from src.actuator_instances import (
    relay_devices_initialization,
    grow_lamp_elixia_initialization,
    voltage_output,
    solid_state_relay,
    CO2_control
)

# ──────────────────────────────── PID State Buffer ─────────────────────────── #
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
    "ec_gt1":      os.getenv("MQTT_DT_REQ_EC_GT1"),
    "ec_gt2":      os.getenv("MQTT_DT_REQ_EC_GT2"),
    "ec_mx":       os.getenv("MQTT_DT_REQ_EC_MX"),
    "ph_gt1":      os.getenv("MQTT_DT_REQ_PH_GT1"),
    "ph_gt2":      os.getenv("MQTT_DT_REQ_PH_GT2"),
    "ph_mx":       os.getenv("MQTT_DT_REQ_PH_MX"),
    "par_gt1":     os.getenv("MQTT_DT_REQ_PAR_GT1"),
    "par_gt2":     os.getenv("MQTT_DT_REQ_PAR_GT2"),
    "sth01_1":     os.getenv("MQTT_DT_REQ_STH_1"),
    "sth01_2":     os.getenv("MQTT_DT_REQ_STH_2"),
    "co2voc":      os.getenv("MQTT_DT_REQ_CO2_VOC"),
    "flow_sym01":  os.getenv("MQTT_DT_REQ_SYM01")
}

# ───────────── Sensor Command Request Topics (CMD_REQ) ───────────── #
MQTT_CMD_REQ = {
    "ec_gt1":      os.getenv("MQTT_CMD_REQ_EC_GT1"),
    "ec_gt2":      os.getenv("MQTT_CMD_REQ_EC_GT2"),
    "ec_mx":       os.getenv("MQTT_CMD_REQ_EC_MX"),
    "ph_gt1":      os.getenv("MQTT_CMD_REQ_PH_GT1"),
    "ph_gt2":      os.getenv("MQTT_CMD_REQ_PH_GT2"),
    "ph_mx":       os.getenv("MQTT_CMD_REQ_PH_MX")
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

# ───────────── Grow Lamp 2 (Elixia) ───────────── #
LAMP_02_IP             = os.getenv("LAMP_02_IP")
MQTT_LAMP_02_CMD_REQ   = os.getenv("MQTT_LAMP_02_CMD_REQ")
MQTT_LAMP_02_DT_REQ    = os.getenv("MQTT_LAMP_02_DT_REQ")

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

# ────────────────────── Generic fallback for unknown topics ────────────────────── #
def on_message(client, userdata, msg):
    print(f"\n[MQTT] Unhandled message on topic: {msg.topic}\nPayload: {msg.payload}")

# ───────────────────────────── On Connect Callback ───────────────────────────── #
def on_connect(client, userdata, flags, rc):
    print(f"[MQTT] Connected with result code {rc}")

    for topic in MQTT_DT_REQ.values():
        if topic:
            client.subscribe(topic)
            print(f"[MQTT] Subscribed to data request: {topic}")

    for topic in MQTT_CMD_REQ.values():
        if topic:
            client.subscribe(topic)
            print(f"[MQTT] Subscribed to command request: {topic}")

    for topic in MQTT_RELAY_CMD.values():
        if topic:
            client.subscribe(topic)
            print(f"[MQTT] Subscribed to relay: {topic}")

    if MQTT_SSR_CMD:
        client.subscribe(MQTT_SSR_CMD)
        print(f"[MQTT] Subscribed to SSR: {MQTT_SSR_CMD}")

    # Lamps
    client.subscribe(MQTT_LAMP_01_CMD_REQ)
    client.subscribe(MQTT_LAMP_01_DT_REQ)
    client.subscribe(MQTT_LAMP_02_CMD_REQ)
    client.subscribe(MQTT_LAMP_02_DT_REQ)

    # Reference commands
    for topic in MQTT_REF_CMDS.values():
        if topic:
            client.subscribe(topic)

    # 0–10V control
    for topic in MQTT_VOLTAGE_CMD.values():
        if topic:
            client.subscribe(topic)

    # PID enable topics
    for topic in MQTT_PID_CMD.values():
        if topic:
            client.subscribe(topic)


# ───────────────────────────── MQTT Setup ───────────────────────────── #
client = mqtt.Client()

# Assign generic callbacks
client.on_connect = on_connect
client.on_message = on_message

# Assign sensor-specific callbacks
client.message_callback_add(MQTT_DT_REQ["par_gt1"], on_message_SLIGHT01)
client.message_callback_add(MQTT_DT_REQ["par_gt2"], on_message_SPAR02)
client.message_callback_add(MQTT_DT_REQ["ec_gt1"], on_message_SEC01_GT1)
client.message_callback_add(MQTT_CMD_REQ["ec_gt1"], on_message_SEC01_GT1_CMD)
client.message_callback_add(MQTT_DT_REQ["ec_gt2"], on_message_SEC01_GT2)
client.message_callback_add(MQTT_CMD_REQ["ec_gt2"], on_message_SEC01_GT2_CMD)
client.message_callback_add(MQTT_DT_REQ["ec_mx"], on_message_SEC01_MX)
client.message_callback_add(MQTT_CMD_REQ["ec_mx"], on_message_SEC01_MX_CMD)
client.message_callback_add(MQTT_DT_REQ["ph_gt1"], on_message_SPH01_GT1)
client.message_callback_add(MQTT_CMD_REQ["ph_gt1"], on_message_SPH01_GT1_CMD)
client.message_callback_add(MQTT_DT_REQ["ph_gt2"], on_message_SPH01_GT2)
client.message_callback_add(MQTT_CMD_REQ["ph_gt2"], on_message_SPH01_GT2_CMD)
client.message_callback_add(MQTT_DT_REQ["ph_mx"], on_message_SPH01_MX)
client.message_callback_add(MQTT_CMD_REQ["ph_mx"], on_message_SPH01_MX_CMD)
client.message_callback_add(MQTT_DT_REQ["sym01"], on_message_SYM01)
client.message_callback_add(MQTT_DT_REQ["co2voc"], on_message_CO2_VOC_1)
client.message_callback_add(MQTT_DT_REQ["sth01_1"], on_message_STH01_1)
client.message_callback_add(MQTT_DT_REQ["sth01_2"], on_message_STH01_2)

# Relay control callbacks
for i in range(1, 17):
    topic = MQTT_RELAY_CMD.get(i)
    if topic:
        client.message_callback_add(topic, getattr(relay_devices_initialization, f"on_message_RLY{i:02}"))

# Solid state relay
if MQTT_SSR_CMD:
    client.message_callback_add(MQTT_SSR_CMD, relay_devices_initialization.on_message_SSR01)

# Voltage-controlled outputs
client.message_callback_add(MQTT_VOLTAGE_CMD["fan_cmd"], voltage_output.on_message_FAN_VOLTAGE_CMD_REQ)
client.message_callback_add(MQTT_VOLTAGE_CMD["valve_cmd"], voltage_output.on_message_VALVE_VOLTAGE_CMD_REQ)

# Grow lamps
client.message_callback_add(MQTT_LAMP_01_CMD_REQ, grow_lamp_elixia_initialization.on_message_LAMP01_CMD_REQ)
client.message_callback_add(MQTT_LAMP_01_DT_REQ, grow_lamp_elixia_initialization.on_message_LAMP01_DT)
client.message_callback_add(MQTT_LAMP_02_CMD_REQ, grow_lamp_elixia_initialization.on_message_LAMP02_CMD_REQ)
client.message_callback_add(MQTT_LAMP_02_DT_REQ, grow_lamp_elixia_initialization.on_message_LAMP02_DT)

# PID control callbacks
client.message_callback_add(MQTT_PID_CMD["cooling"], on_message_COOLING_PID_CMD_REQ)
client.message_callback_add(MQTT_REF_CMDS["humidity_req"], voltage_output.on_message_REFHUMID_CMD_REQ)
client.message_callback_add(MQTT_PID_CMD["heating"], on_message_HEATING_PID_CMD_REQ)
client.message_callback_add(MQTT_REF_CMDS["temp_req"], solid_state_relay.on_message_REFTEMP_CMD_REQ)
client.message_callback_add(MQTT_PID_CMD["co2"], on_message_CO2_PID_CMD_REQ)
client.message_callback_add(MQTT_REF_CMDS["co2_req"], CO2_control.on_message_REFCO2_CMD_REQ)

            

# ───────────────────────────── Main Execution ───────────────────────────── #
try:
    client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEP_ALIVE)
    client.loop_start()
    print("[MQTT] Client loop started")
except Exception as e:
    print("[MQTT] Connection failed:", str(e))

# ───────────────────────────── Sensor Initialization ───────────────────────────── #
def initialize_sensor(name, cls, port, addr):
    try:
        instance = cls(portname=port, slaveaddress=addr, debug=False)
        print(f"[{name}] Initialized at address {addr} on {port}")
        return instance
    except Exception as e:
        print(f"[{name}] Initialization error:", str(e))
        return None

sensor_SLIGHT01 = initialize_sensor("SLIGHT01", sensor_SLIGHT01_modbus.SLIGHT01, "/dev/ttySC1", 1)
sensor_SPAR02 = initialize_sensor("SPAR02", sensor_SPAR02_modbus.SPAR02, "/dev/ttySC1", 34)
sensor_SEC01_1 = initialize_sensor("SEC01_GT1", sensor_SEC01_modbus.SEC01, "/dev/ttySC1", 3)
sensor_SEC01_2 = initialize_sensor("SEC01_GT2", sensor_SEC01_modbus.SEC01, "/dev/ttySC1", 4)
sensor_SPH01_1 = initialize_sensor("SPH01_GT1", sensor_SPH01_modbus.SPH01, "/dev/ttySC1", 5)
sensor_SPH01_2 = initialize_sensor("SPH01_GT2", sensor_SPH01_modbus.SPH01, "/dev/ttySC1", 6)
sensor_SYM01    = initialize_sensor("SYM01", sensor_SYM01_modbus.SYM01, "/dev/ttySC1", 11)
sensor_CO2_VOC_1 = initialize_sensor("CO2_VOC_1", sensor_CO2_VOC_modbus.CO2_VOC, "/dev/ttySC0", 7)
sensor_CO2_VOC_2 = initialize_sensor("CO2_VOC_2", sensor_CO2_VOC_modbus.CO2_VOC, "/dev/ttySC0", 1)
sensor_STH01_1 = initialize_sensor("STH01_1", sensor_STH01_modbus.STH01, "/dev/ttySC0", 70)
sensor_STH01_2 = initialize_sensor("STH01_2", sensor_STH01_modbus.STH01, "/dev/ttySC0", 69)

# ───────────────────────────── Main Loop ───────────────────────────── #
try:
    while True:
        time.sleep(15)
except KeyboardInterrupt:
    print("[Main Loop] Interrupted by user")
except Exception as e:
    print("[Main Loop] Error:", str(e))
finally:
    client.loop_stop()
    print("[MQTT] Client loop stopped")

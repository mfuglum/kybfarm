import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json
import time

# from sensor_interfaces import sensor_BMP280_I2C
from sensor_interfaces import sensor_SCD41_I2C, sensor_SYM01_modbus

MQTT_SERVER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_KEEP_ALIVE= 60
MQTT_PATHS = [
    "req/desktop_gf/sensors/BMP280",
    "req/desktop_gf/sensors/SCD41",
    "req/desktop_gf/sensors/SYM01",
    # "sensors/request/BMP280", 
    # "sensors/response/BMP280"
    ]

def on_connect(client, userdata, flags, rc):
    print("Connected with code " + str(rc))
    # Subscribe in on_connect to renew subsriptions in case of lost connection
    # NB: This way of subscribing to path is for testing purposes
    for path in MQTT_PATHS:
        client.subscribe(path)

# Catch-all callback function for messages
def on_message(client, userdata, msg):
    print("\n" + msg.topic + ":\n", msg.payload)

def on_message_SCD41(client, userdata, msg):
    req_msg = json.loads(msg.payload)
    # Check if new data is ready and publish it
    # if( sensor_SCD41_I2C.data_is_ready() ):
    try:
        res_payload = json.dumps(sensor_SCD41_I2C.fetch_and_return_data())
        client.publish(req_msg["res_topic"], res_payload)
        # Write to log
        log_file_SCD41.write("\n" + res_payload)
        sensor_SCD41_I2C.fetch_and_print_data()
    except Exception as e:
        print("SCD41, data fetch error:", str(e))
    # else:
    #     print("\nSCD41: No new data ready")

def on_message_SYM01(client, userdata, msg):
    req_msg = json.loads(msg.payload)
    try:
        res_payload = json.dumps(sensor_SYM01.fetch_and_return_data())
        client.publish(req_msg["res_topic"], res_payload)
        # Write to log
        #log_file_SCD41.write("\n" + json.dumps(req_msg))
        # sensor_SCD41_I2C.fetch_and_print_data()
        sensor_SYM01.fetch_and_print_data()
    except Exception as e:
        print("SYM01, data fetch error:", str(e))
    

# Open or create log file(s)
log_file_BMP280 = open("logging/log_file_BMP280.txt", "a")
log_file_SCD41 = open("logging/log_file_SCD41.txt", "a")

# Setup MQTT client for sensor host
client = mqtt.Client()

# Assign the generic callback functions for the client
client.on_connect = on_connect
client.on_message = on_message

# Assign the specific callback functions for the client
client.message_callback_add("req/desktop_gf/sensors/SCD41", on_message_SCD41)
client.message_callback_add("req/desktop_gf/sensors/SYM01", on_message_SYM01)

# Connect to the MQTT server
try:
    client.connect(MQTT_SERVER, MQTT_PORT, MQTT_KEEP_ALIVE)
    client.loop_start()
except:
    print("\nConnection failed\n")

# Activate SCD-41 sensor
try:
    sensor_SCD41_I2C.start_low_periodic_measurement()
except Exception as e:
    print("SCD41, error:", str(e))

# Activate SYM-01 sensor
try:
    sensor_SYM01 = sensor_SYM01_modbus.SYM01(   portname='/dev/ttySC1',
                                                slaveaddress=11, 
                                                debug=False)
    print(sensor_SYM01)
    print(sensor_SYM01.get_baudrate())
except Exception as e:
    print("SYM01, error:", str(e))

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
log_file_BMP280.close() 
log_file_SCD41.close()
sensor_SCD41_I2C.stop_periodic_measurement()
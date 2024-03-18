# Ref https://learn.adafruit.com/adafruit-scd-40-and-scd-41/python-circuitpython

# import time
import board
# import digitalio # For use with SPI
import adafruit_scd4x
import datetime

# A dictionary struct to send as payload over MQTT
data = {
    "measurement": "ambient",
    "tags": {
        "sensor_id": "1",
        "location": "GF, Gloeshaugen",
        "sensor_name": "SCD41"},
    "fields": {
            "temperature": 0,
            "humidity": 0,
            "CO2": 0},
    "time": datetime.datetime.now().isoformat(),
}


# Create sensor object I2C communcationg on default bus
i2c = board.I2C()   # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C() # Alternative for built-in STEMMA QT for I2C
scd41 = adafruit_scd4x.SCD4X(i2c)

# Put sensor in working mode with sampling every 30 sec
def start_low_periodic_measurement():
    scd41.start_low_periodic_measurement()

# Put sensor in working mode with sampling every 5 sec
def start_periodic_measurement():
    scd41.start_periodic_measurement()

# Stop measurement / working mode
def stop_periodic_measurement():
    scd41.stop_periodic_measurement()
    
# Check if ready data
def data_is_ready():
    return scd41.data_ready


# A function to fetch and print data from the sensor
def fetch_and_print_data():
    print("\nSCD41, I2C - Time: ", datetime.datetime.now())
    print("Temperature: %0.1f C" % scd41.temperature)
    print("Humidity: %0.1f %%" % scd41.relative_humidity)
    print("CO2: %d ppm" % scd41.CO2)


# A function to fetch and return data from the sensor
def fetch_and_return_data():
    data["fields"]["temperature"] = scd41.temperature
    data["fields"]["humidity"] = scd41.relative_humidity
    data["fields"]["CO2"] = scd41.CO2
    data["time"] = datetime.datetime.now().isoformat()
    return data

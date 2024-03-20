# Ref https://docs.circuitpython.org/projects/bmp280/en/latest/

# import time
import board
# import digitalio # For use with SPI
import adafruit_bmp280
import datetime

# A dictionary struct to send as payload over MQTT
data = {
    "measurement": "ambient_prototype",
    "tags": {
        "sensor_id": "1",
        "location": "GF, Gloeshaugen",
        "sensor_name": "bmp280"},
    "fields": {
            "temperature": 0,
            "pressure": 0},
    "time": datetime.datetime.now().isoformat(),
}


# Create sensor object I2C communcationg on default bus
i2c = board.I2C()   # uses board.SCL and board.SDA
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)

# OR Create sensor object, communicating over the board's default SPI bus
# spi = board.SPI()
# bmp_cs = digitalio.DigitalInOut(board.D10)
# bmp280 = adafruit_bmp280.Adafruit_BMP280_SPI(spi, bmp_cs)

# change this to match the location's pressure (hPa) at sea level
# bmp280.sea_level_pressure = 1013.25


# A function to fetch and print data from the sensor
def fetch_and_print_data():
    print("\nBMP280, I2C - Time: ", datetime.datetime.now())
    print("Temperature: %0.1f C" % bmp280.temperature)
    print("Pressure: %0.1f hPa" % bmp280.pressure)
    # print("Altitude = %0.2f meters" % bmp280.altitude)


# A function to fetch and return data from the sensor
def fetch_and_return_data():
    data["fields"]["temperature"] = bmp280.temperature
    data["fields"]["pressure"] = bmp280.pressure
    data["time"] = datetime.datetime.now().isoformat()
    return data

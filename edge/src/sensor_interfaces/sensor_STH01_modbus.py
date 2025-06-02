import minimalmodbus
import datetime

# Device/Instrument class for STH01 RS485 Modbus sensor
class STH01(minimalmodbus.Instrument):
    """
    Class for communicating with a STH01 sensor over Modbus RTU.
    Provides methods for reading temperature, humidity, dewpoint, and for device configuration.
    """

    def __init__(self,
                 portname='/dev/ttySC0',
                 slaveaddress=200,  # Default address as per datasheet
                 mode=minimalmodbus.MODE_RTU,
                 close_port_after_each_call=False,
                 debug=False):
        """
        Initialize the Modbus instrument for STH01.
        """
        minimalmodbus.Instrument.__init__(self, 
                                          portname, 
                                          slaveaddress=slaveaddress,
                                          mode=mode,
                                          close_port_after_each_call=close_port_after_each_call,
                                          debug=debug)    
        self.serial.baudrate = 9600

    def get_temperature(self):
        """
        Read temperature from register 0.
        Returns:
            float: Temperature in °C (can be negative, e.g., after cooling coil).
        """
        temperature = self.read_register(registeraddress=0,
                                         number_of_decimals=2,
                                         functioncode=3,
                                         signed=True)  # Signed for possible negative values
        return temperature

    def get_humidity(self):
        """
        Read relative humidity from register 1.
        Returns:
            float: Relative humidity (%).
        """
        humidity = self.read_register(registeraddress=1,
                                      number_of_decimals=2,
                                      functioncode=3,
                                      signed=False)
        return humidity
    
    def get_dewpoint(self):
        """
        Read dewpoint from register 2.
        Returns:
            float: Dewpoint temperature (°C).
        """
        dewpoint = self.read_register(registeraddress=2,
                                      number_of_decimals=2,
                                      functioncode=3,
                                      signed=False)
        return dewpoint
        
    def fetch_and_return_data(self, sensor_name):
        """
        Fetch all sensor values and return them in a data dictionary for MQTT.
        Args:
            sensor_name (str): Name of the sensor for tagging.
        Returns:
            dict: Data dictionary with all sensor readings and timestamp.
        """
        temperature = self.get_temperature()
        humidity = self.get_humidity()
        dewpoint = self.get_dewpoint()

        # Dictionary structure for MQTT payload
        data = {
            "measurement": "Temperature and Humidity",
            "tags": {
                "sensor_id": "8",
                "location": "GF, Gloeshaugen",
                "sensor_name": sensor_name
            },
            "fields": {
                "temperature": temperature,
                "dewpoint": dewpoint,
                "humidity": humidity
            },
            "time": datetime.datetime.now().isoformat(),
        }
        return data
    
    def get_slave_address(self):
        """
        Read the current Modbus slave address from register 512.
        Returns:
            int: Current slave address.
        """
        return self.read_register(registeraddress=512,
                                  functioncode=3)
    
    def set_slave_address(self, slaveaddress):
        """
        Set a new Modbus slave address by writing to register 512.
        Args:
            slaveaddress (int): New slave address to set.
        """
        self.write_register(registeraddress=512,
                            value=slaveaddress,
                            functioncode=16,
                            signed=False)
        
    def get_baudrate(self):
        """
        Read the current baudrate setting from register 513.
        Returns:
            int: Baudrate value.
        """
        return self.read_register(registeraddress=513,
                                  functioncode=3)
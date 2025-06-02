import minimalmodbus
import datetime
import serial

# Data dictionary structure for MQTT payloads
data = {
    "measurement": "ambient",
    "tags": {
        "sensor_id": "1",
        "location": "GF, Gloeshaugen",
        "sensor_name": "CO2+VOC"},
    "fields": {
        "temperature": 0,
        "humidity": 0,
        "co2": 0,
        "dewpoint": 0,
        "volumeFlow": 0},
    "time": datetime.datetime.now().isoformat(),
}

# Device class for Thermokon LK+ CO2+VOC RS485 Modbus sensor
class CO2_VOC(minimalmodbus.Instrument):
    """
    Class for communicating with a Thermokon LK+ CO2+VOC sensor over Modbus RTU.
    Provides methods for setting units and reading sensor values.
    """

    def __init__(self,
                 portname='/dev/ttySC0',
                 slaveaddress=7,  # Set correct address for your sensor
                 mode=minimalmodbus.MODE_RTU,
                 close_port_after_each_call=False,
                 debug=False):
        """
        Initialize the Modbus instrument and set default units.
        """
        minimalmodbus.Instrument.__init__(self, 
                                          portname, 
                                          slaveaddress=slaveaddress,
                                          mode=mode,
                                          close_port_after_each_call=close_port_after_each_call,
                                          debug=debug)   
        self.serial.baudrate = 9600 
        self.set_unit(unit="SI")

    def set_unit(self, unit="SI"):
        """
        Set the measurement unit for the sensor.
        Args:
            unit (str): "SI" for SI units, anything else for Imperial.
        """
        val = 1 if unit == "SI" else 2
        self.write_register(registeraddress=400,
                            value=val,
                            number_of_decimals=0,
                            functioncode=6,
                            signed=False)
    
    def set_volume_unit(self):
        """
        Set the unit for volume flow measurements to m3/s.
        """
        self.write_register(registeraddress=404,
                            value=2,  # Value 2 gives m3/s
                            number_of_decimals=0,
                            functioncode=6,
                            signed=False)

    def get_co2(self):
        """
        Read CO2 concentration from register 5.
        Returns:
            int: CO2 concentration in ppm.
        """
        co2 = self.read_register(registeraddress=5,
                                 number_of_decimals=0,
                                 functioncode=3,
                                 signed=False)
        return co2

    def get_humidity(self):
        """
        Read relative humidity from register 1.
        Returns:
            float: Relative humidity (%).
        """
        humidity = self.read_register(registeraddress=1,
                                      number_of_decimals=1,
                                      functioncode=3,
                                      signed=False)
        return humidity

    def get_temperature(self):
        """
        Read temperature from register 0.
        Returns:
            float: Temperature (°C).
        """
        temperature = self.read_register(registeraddress=0,
                                         number_of_decimals=1,
                                         functioncode=3,
                                         signed=False)
        return temperature
    
    def get_dewpoint(self):
        """
        Read dew point from register 4.
        Returns:
            float: Dew point (°C).
        """
        dewpoint = self.read_register(registeraddress=4,
                                      number_of_decimals=1,
                                      functioncode=3,
                                      signed=False)
        return dewpoint

    def get_volume_flow(self):
        """
        Read volume flow from register 9.
        Returns:
            float: Volume flow (m3/s).
        """
        volumeFlow = self.read_register(registeraddress=9,
                                        number_of_decimals=2,
                                        functioncode=3,
                                        signed=False)
        return volumeFlow

    # The following commented-out methods show how to read 32-bit volume flow values by combining two 16-bit registers.
    # def get_volume_flow_low(self):
    #     return self.read_register(registeraddress=50, number_of_decimals=0, functioncode=3, signed=False)
    # def get_volume_flow_high(self):
    #     return self.read_register(registeraddress=51, number_of_decimals=0, functioncode=3, signed=False)
    # def get_volume_flow(self):
    #     low = self.get_volume_flow_low()
    #     high = self.get_volume_flow_high()
    #     if low is not None and high is not None:
    #         volume_flow = (high << 16) | low
    #         return volume_flow
    #     else:
    #         return None

    def fetch_and_print_data(self):
        """
        Fetch CO2 value from the sensor and print it.
        """
        co2 = self.get_co2()
        print(f"CO2: {co2} ppm")

    def fetch_and_return_data(self):
        """
        Fetch all sensor values and return them in the data dictionary.
        Returns:
            dict: Data dictionary with all sensor readings and timestamp.
        """
        co2 = self.get_co2()
        temperature = self.get_temperature()
        humidity = self.get_humidity()
        dewpoint = self.get_dewpoint()
        volumeFlow = self.get_volume_flow()
        data["fields"]["co2"] = co2
        data["fields"]["humidity"] = humidity
        data["fields"]["temperature"] = temperature
        data["fields"]["dewpoint"] = dewpoint
        data["fields"]["volumeFlow"] = volumeFlow
        data["time"] = datetime.datetime.now().isoformat()
        return data



import minimalmodbus
import datetime
import serial

<<<<<<< HEAD
# A dictionary struct to send as payload over MQTT
=======
# Data dictionary structure for MQTT payloads
>>>>>>> hvac
data = {
    "measurement": "ambient",
    "tags": {
        "sensor_id": "1",
        "location": "GF, Gloeshaugen",
        "sensor_name": "CO2+VOC"},
    "fields": {
<<<<<<< HEAD
            "temperature": 0,
            "humidity": 0,
            "co2": 0,
            "dewpoint": 0,
            "volumeFlow": 0},
    "time": datetime.datetime.now().isoformat(),
}


# The device / Instrument class for Thermokon LK+ CO2+VOC RS485 Modbus 
class CO2_VOC( minimalmodbus.Instrument ):
    """Instrument class for  Light Intensity sensor.
    
    Args:
        * portname (str):                       port name
                                                Default is '/dev/ttySC1', which is the address to the RS-485 hat of the Raspberry Pi 4B
        * slaveaddress (int):                   slave address in the range 1 to 247
                                                Default is 13 (from manufacturer)
        * mode (str):                           Mode of communication.
                                                Default is minimalmodbus.MODE_RTU
        * close_port_after_each_call (bool):    Whether to close the port after each call.
                                                Default is False
        * debug (bool):                         Whether to print debug information.
                                                Default is False
    
    From datasheet:

    Baud rate, address and parity are set by manually setting pins on sensor
    Default:
        Baudrate: 9600
        Parity: None
        Address: 0 (Not usable as it is used to set address outside range 1-31 through an app)
    Current:
        Baudrate: 9600
        Parity: None
        Address: 7


    Imperial vs SI unit system is set using register 400

    Register value               Register Addr (HEX/DEC) Data    Type    Function code (DEC)     Range and Comments          Default Value
    C02                          0x0005 /5               UINT16  R       3                                                   N/A

    UNIT SYSTEM                  0x0190 /400             UINT16  R/W     6                        VAL=1->SI, 2->IMPERIAL     1

    Functions used from minimalmodbus API:
    https://minimalmodbus.readthedocs.io/en/stable/_modules/minimalmodbus.html#Instrument.read_bit

    def read_register(
        self,
        registeraddress: int,
        number_of_decimals: int = 0,
        functioncode: int = 3,
        signed: bool = False,
    )
    def write_register(
        self,
        registeraddress: int,
        value: Union[int, float],
        number_of_decimals: int = 0,
        functioncode: int = 6,
        signed: bool = False,
    )
=======
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
>>>>>>> hvac
    """

    def __init__(self,
                 portname='/dev/ttySC0',
<<<<<<< HEAD
                 slaveaddress=7, # Find correct adress
                 mode=minimalmodbus.MODE_RTU,
                 close_port_after_each_call=False,
                 debug=False):
=======
                 slaveaddress=7,  # Set correct address for your sensor
                 mode=minimalmodbus.MODE_RTU,
                 close_port_after_each_call=False,
                 debug=False):
        """
        Initialize the Modbus instrument and set default units.
        """
>>>>>>> hvac
        minimalmodbus.Instrument.__init__(self, 
                                          portname, 
                                          slaveaddress=slaveaddress,
                                          mode=mode,
                                          close_port_after_each_call=close_port_after_each_call,
                                          debug=debug)   
        self.serial.baudrate = 9600 
<<<<<<< HEAD
        self.set_unit(unit = "SI")


    # Setting SI unit as standard
    def set_unit(self,unit = "SI"):
        val= 1 if unit == "SI" else 2
        self.write_register(registeraddress=400,
                    value=val,
                    number_of_decimals=0,
                    functioncode=6,
                    signed=False)
    
    # Unit for Volume flow measurments
    def set_volume_unit(self):
        self.write_register(registeraddress=404,
                    value=2, # Value 2 gives m3/s
                    number_of_decimals=0,
                    functioncode=6,
                    signed=False)

    # C02 measurments - register 5
    def get_co2(self):

        co2 = self.read_register(registeraddress=5,
                                              number_of_decimals=0,
                                              functioncode=3,
                                              signed=False)
 
        return co2

    # Relative humidity measurment - register 1
    def get_humidity(self):

        humidity = self.read_register(registeraddress=1,
                                              number_of_decimals=1,
                                              functioncode=3,
                                              signed=False)
 
        return humidity

    # Temperature measurment - register 0
    def get_temperature(self):

        temperature = self.read_register(registeraddress=0,
                                              number_of_decimals=1,
                                              functioncode=3,
                                              signed=False)
 
        return temperature
    
    # Dewpoint measurment - register 4
    def get_dewpoint(self):

            dewpoint = self.read_register(registeraddress=4,
                                                number_of_decimals=1,
                                                functioncode=3,
                                                signed=False)
    
            return dewpoint

    def get_volume_flow(self):

            volumeFlow = self.read_register(registeraddress=9,
                                                number_of_decimals=2,
                                                functioncode=3,
                                                signed=False)
    
            return volumeFlow

    """def get_volume_flow_low(self):
        # Reading 16-bit lowregister (adress 50) for Volume Flow 1
        return self.read_register(registeraddress=50, 
                                number_of_decimals=0, 
                                functioncode=3, 
                                signed=False)

    def get_volume_flow_high(self):
        # Reading 16-bit highregister (adress 51) for Volume Flow 1
        return self.read_register(registeraddress=51, 
                                number_of_decimals=0, 
                                functioncode=3, 
                                signed=False)
    """
    """def get_volume_flow(self):
        # Reading Volume Flow 1 (32-bit) with combining LOW and HIGH values
        low = self.get_volume_flow_low()
        high = self.get_volume_flow_high()

        # Combining high and low registervalue to 32-bit
        if low is not None and high is not None:
            
            # Bitwise left shift by 16 bits, to make space for the low value, performed with bitwise OR
            volume_flow = (high << 16) | low

            return volume_flow
        else:
            return None  # Handles errors if one of the registers is not read correctly.
        """

    # A function to fetch and print data from the sensor
    def fetch_and_print_data(self):
        co2 = self.get_co2()
        print(f"CO2: {co2} ppm")

    # A funcion to fetch and return data from the sensor
    def fetch_and_return_data(self):
=======
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
>>>>>>> hvac
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
<<<<<<< HEAD
    
=======

>>>>>>> hvac


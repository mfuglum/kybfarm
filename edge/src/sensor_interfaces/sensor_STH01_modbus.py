import minimalmodbus
import datetime



# The device / Instrument class for Thermokon LK+ CO2+VOC RS485 Modbus 
class STH01( minimalmodbus.Instrument ):
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
    """

    def __init__(self,
                 portname='/dev/ttySC0',
                 slaveaddress=200, # Standard definert i datablad
                 mode=minimalmodbus.MODE_RTU,
                 close_port_after_each_call=False,
                 debug=False):
        minimalmodbus.Instrument.__init__(self, 
                                          portname, 
                                          slaveaddress=slaveaddress,
                                          mode=mode,
                                          close_port_after_each_call=close_port_after_each_call,
                                          debug=debug)    
        self.serial.baudrate = 9600

    # Temperature measurments - register 0
    def get_temperature(self):

        temperature = self.read_register(registeraddress=0,
                                              number_of_decimals=2,
                                              functioncode=3,
                                              signed=True) # Setter til True ettersom denne står etter kjølebatteriet og kan bli negativ
 
        return temperature

    # Relative humidity measurment - register 1
    def get_humidity(self):

        humidity = self.read_register(registeraddress=1,
                                              number_of_decimals=0,
                                              functioncode=3,
                                              signed=False)
 
        return humidity
    
    # Dewpoint measurment - register 2
    def get_dewpoint(self):

            dewpoint = self.read_register(registeraddress=2,
                                                number_of_decimals=2,
                                                functioncode=3,
                                                signed=False)
    
            return dewpoint
        
    # A funcion to fetch and return data from the sensor
    def fetch_and_return_data(self,sensor_name):
        temperature = self.get_temperature()
        humidity = self.get_humidity()
        dewpoint = self.get_dewpoint()


        # A dictionary struct to send as payload over MQTT
        data = {
        "measurement": "Temperature and Humidity",
        "tags": {
            "sensor_id": "8",
            "location": "GF, Gloeshaugen",
            "sensor_name": sensor_name},
        "fields": {
            "temperature": temperature,
            "dewpoint": dewpoint,
            "humidity": humidity},
        "time": datetime.datetime.now().isoformat(),
}
        return data
    
    def get_slave_address(self):
        return self.read_register(registeraddress=512,
                                  functioncode=3)
    
    def set_slave_address(self, slaveaddress):
        # Write slave address to register 512
        self.write_register(registeraddress=512,
                            value=slaveaddress,
                            functioncode=6,
                            signed=False)
        
    def get_baudrate(self):
        return self.read_register(registeraddress=513,
                                  functioncode=3)
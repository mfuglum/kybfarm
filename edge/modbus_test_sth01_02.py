import paho.mqtt.client as mqtt
import json
import time
from dotenv import load_dotenv
import os
import minimalmodbus
import datetime




from src.sensor_interfaces import (
                                   sensor_STH01_modbus # Legger til ny temp sensor - Not connected
                                   )

#load_dotenv()

# The device / Instrument class for Thermokon LK+ CO2+VOC RS485 Modbus 
class STH01_02( minimalmodbus.Instrument ):
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
                 slaveaddress=69,
                 mode=minimalmodbus.MODE_RTU,
                 close_port_after_each_call=False,
                 debug=False):
        minimalmodbus.Instrument.__init__(self, 
                                          portname, 
                                          slaveaddress=slaveaddress,
                                          mode=mode,
                                          close_port_after_each_call=close_port_after_each_call,
                                          debug=debug)

        print("slaveadress is: ", slaveaddress)
        print("portname is: ", portname)

        self.serial.baudrate = 9600
        # print(self.fetch_and_return_data())
        # self.address=42
    # Temperature measurments - register 0
    def get_temperature(self):

        temperature = self.read_register(registeraddress=0,
                                              number_of_decimals=2,
                                              functioncode=3,
                                              signed=False) # Setter til True ettersom denne står etter kjølebatteriet og kan bli negativ
 
        return temperature

    # Relative humidity measurment - register 1
    def get_humidity(self):

        humidity = self.read_register(registeraddress=1,
                                              number_of_decimals=2,
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
    def fetch_and_return_data(self,sensorkuk):
        temperature = self.get_temperature()
        humidity = self.get_humidity()
        dewpoint = self.get_dewpoint()

        data = {
        "measurement": "Temperature and Humidity",
        "tags": {
            "sensor_id": sensorkuk,
            "location": "GF, Gloeshaugen",
            "sensor_name": "S-TH-01"},
        "fields": {
            "temperature": temperature,
            "dewpoint": humidity,
            "humidity": dewpoint},
        "time": datetime.datetime.now().isoformat(),
}

        
        data["fields"]["humidity"] = humidity
        data["fields"]["temperature"] = temperature
        data["fields"]["dewpoint"] = dewpoint
        data["time"] = datetime.datetime.now().isoformat()
        return data
        
    
    def get_slave_address(self):
        return self.read_register(registeraddress=512,
                                  functioncode=3)
    

    def set_slave_address(self, slaveaddress):
        # Write slave address to register 512
        self.write_register(registeraddress=512,
                            value=slaveaddress,
                            functioncode=16,
                            signed=False)
        
    def get_baudrate(self):
        return self.read_register(registeraddress=513,
                                  functioncode=3)


try:
    sensor_STH01_2 = sensor_STH01_modbus.STH01_02(   portname='/dev/ttySC0',
                                                slaveaddress=69, 
                                                debug=False)
    print(sensor_STH01_2.fetch_and_return_data(sensor_name="STH01-2"))
    #print(sensor_STH01_2.set_slave_address(69))
    print("Slave address:",sensor_STH01_2.get_slave_address())
    #sensor_STH01_1.address = 42
    #sensor_STH01_1.set_slave_address(42)

    print(sensor_STH01_2)
except Exception as e:
    print("STH01-2, error:", str(e))

"""""
try:
    time.sleep(0.5)
    sensor_STH01_1 = sensor_STH01_modbus.STH01(   portname='/dev/ttySC0',
                                                slaveaddress=70, 
                                                debug=True)
    print(sensor_STH01_1.fetch_and_return_data(sensor_name="STH01-1"))
    #print(sensor_STH01_1.set_slave_address(70))
    print("Slave address:",sensor_STH01_1.get_slave_address())
    #sensor_STH01_1.address = 42
    #sensor_STH01_1.set_slave_address(42)

    print(sensor_STH01_1)
except Exception as e:
    print("STH01-1, error:", str(e))
"""""

# Start main loop #
try:
    # Main loop
    while True:
        time.sleep(15)
except KeyboardInterrupt:
    print("Keyboard interrupt")
except Exception as e:
    print("\nException, error: ", str(e))

#client.loop_stop()

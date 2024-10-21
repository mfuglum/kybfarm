import minimalmodbus
import datetime

# A dictionary struct to send as payload over MQTT
data = {
    "measurement": "ambient",
    "tags": {
        "sensor_id": "1",
        "location": "GF, Gloeshaugen",
        "sensor_name": "SCD41"},
    "fields": {
            "co2": 0},
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
    """

    def __init__(self,
                 portname='/dev/ttySC1',
                 slaveaddress=1, # Find correct adress
                 mode=minimalmodbus.MODE_RTU,
                 close_port_after_each_call=False,
                 debug=False):
        minimalmodbus.Instrument.__init__(self, 
                                          portname, 
                                          slaveaddress=slaveaddress,
                                          mode=mode,
                                          close_port_after_each_call=close_port_after_each_call,
                                          debug=debug)    
        self.set_unit(unit = "SI")



    def set_unit(self,unit = "SI"):
        val= 1 if unit == "SI" else 2
        self.write_register(registeraddress=400,
                    value=val,
                    number_of_decimals=0,
                    functioncode=6,
                    signed=False)

    def get_c02(self):

        c02 = self.read_register(registeraddress=5,
                                              number_of_decimals=0,
                                              functioncode=3,
                                              signed=False)
 
        return c02
    





    # A function to fetch and print data from the sensor
    def fetch_and_print_data(self):
        c02 = self.get_c02()
        print(f"C02: {c02} ppm")

    # A funcion to fetch and return data from the sensor
    def fetch_and_return_data(self):
        c02 = self.get_c02()
        data["fields"]["co2"] = c02
        data["time"] = datetime.datetime.now().isoformat()
        return data
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


# The device / Instrument class for Seeed Studio SenseCAP S-LIGHT-01 Light Intensity sensor
class CO2_VOC( minimalmodbus.Instrument ):
    """Instrument class for S-LIGHT-01 Light Intensity sensor.
    
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
    
    From datasheet, Ch. 6. RS485 Modbus Protocol:

    The default serial communication settings is slave
    address 1, Modbus RTU, 9600bps, 8 data bits and 1 stop bit.

    Following Modbus function code are supported by sensor.
    Modbus Function Code 0x03 : used for reading holding register.
    Modbus Function Code 0x04 : used for reading input register.
    Modbus Function Code 0x06 : used for writing single holding register.
    Modbus Function Code 0x10: used for writing multiple holding register.

    Register value               Register Addr (HEX/DEC) Data    Type    Function code (DEC)     Range and Comments          Default Value
    ILLUMINANCE HIGH 16 Bits     0x0000 /0               UINT16  RO      3/4                     0-200000 for 0-200000 lux   N/A
    ILLUMINANCE LOW 16 Bits      0x0001 /1               UINT16  RO      3/4                     0-200000 for 0-200000 lux   N/A
    STATUS                       0x0002 /2               UINT16  RO      3/4                     BIT1:Sensor Error           N/A
                                                                                                 BIT0:Over Range
    SLAVEADDRESS                 0x0200 /512             UINT16  R/W     3/6/16                  1-255                       1
    BAUDRATE                     0x0201 /513             UINT16  R/W     3/6/16                  3:9600bps/4:19200bps        3:9600bps
    RESPONSEDELAY                0x0206 /518             UINT16  R/W     3/6/16                  0-255 for 0-2550ms          0
    ACTIVEOUTPUTINTERVAL         0x0207 /519             UINT16  R/W     3/6/16                  0-255 for 0-255ms           0
    
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



    def set_unit(unit = "SI"):
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
        co2 = self.get_c02()
        print(f"C02: {c02} ppm")

    # A funcion to fetch and return data from the sensor
    def fetch_and_return_data(self):
        co2 = self.get_c02()
        data["fields"]["c02"] = c02
        data["time"] = datetime.datetime.now().isoformat()
        return data
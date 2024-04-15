import minimalmodbus
import datetime

# A dictionary struct to send as payload over MQTT
data = {
    "measurement": "light intensity",
    "tags": {
        "sensor_id": "01",
        "location": "Gloeshaugen",
        "sensor_name": "S-LIGHT-01"},
    "fields": {
            "illuminance": 0},
    "time": datetime.datetime.now().isoformat(),
}

# The device / Instrument class for Seeed Studio SenseCAP S-LIGHT-01 Light Intensity sensor
class SLIGHT01( minimalmodbus.Instrument ):
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
                 portname='/dev/ttySC0',
                 slaveaddress=1,
                 mode=minimalmodbus.MODE_RTU,
                 close_port_after_each_call=False,
                 debug=False):
        minimalmodbus.Instrument.__init__(self, 
                                          portname, 
                                          slaveaddress=slaveaddress,
                                          mode=mode,
                                          close_port_after_each_call=close_port_after_each_call,
                                          debug=debug)
    
    # Returns illuminance value in 0-200000 lux 
    def get_illuminance(self):
        # Get the illuminance value from the sensor
        # The illuminance value is stored in two registers, one for the high 16 bits and one for the low 16 bits
        # Read the high 16 bits register
        illuminance_high = self.read_register(registeraddress=0,
                                              number_of_decimals=0,
                                              functioncode=3,
                                              signed=False)
        illuminance_low = self.read_register(registeraddress=1,
                                             number_of_decimals=0,
                                             functioncode=3,
                                             signed=False)
        # Combine the high and low registers to get the full 32 bit value
        illuminance = illuminance_high << 16 | illuminance_low
        return illuminance
    
    def set_slave_address(self, new_slaveaddress):
        # Set the slave address of the sensor
        self.write_register(registeraddress=512,
                            value=new_slaveaddress,
                            number_of_decimals=0,
                            functioncode=6,
                            signed=False)
        self.slaveaddress = new_slaveaddress

        
    def get_slave_address(self):
        # Get the slave address of the sensor
        return self.read_register(registeraddress=512,
                                  number_of_decimals=0,
                                  functioncode=3,
                                  signed=False)
    
    def set_baudrate(self, baudrate):
        # Set the baudrate of the sensor
        self.write_register(registeraddress=513,
                            value=baudrate,
                            number_of_decimals=0,
                            functioncode=6,
                            signed=False)
        
    def get_baudrate(self):
        # Get the baudrate of the sensor
        return self.read_register(registeraddress=513,
                                  number_of_decimals=0,
                                  functioncode=3,
                                  signed=False)
    
    # A function to fetch and print data from the sensor
    def fetch_and_print_data(self):
        illuminance = self.get_illuminance()
        print(f"Illuminance: {illuminance} lux")

    # A funcion to fetch and return data from the sensor
    def fetch_and_return_data(self):
        illuminance = self.get_illuminance()
        data["fields"]["illuminance"] = illuminance
        data["time"] = datetime.datetime.now().isoformat()
        return data
import minimalmodbus
import datetime

# A dictionary struct to send as payload over MQTT
data = {
    "measurement": "ambient",
    "tags": {
        "sensor_id": "10",
        "location": "Gloeshaugen",
        "sensor_name": "S-YM-01"},
    "fields": {
            "temperature": 0,
            "wetness": 0},
    "time": datetime.datetime.now().isoformat(),
}


# The device / Instrument class for Seeed Studio SenseCAP S-YM-01 Leaf wetness & Temperature sensor
class SYM01( minimalmodbus.Instrument ):
    """Instrument class for S-YM-01 Leaf wetness & Temperature sensor.

    Args:
        * portname (str):       port name
                                Default is '/dev/ttySC1', which is the address to the RS-485 hat of the Raspberry Pi 4B
        * slaveaddress (int):   slave address in the range 1 to 247
                                Default is 11(from manufacturer)
    
    From datasheet, Ch. 6. RS485 Modbus Protocol:

    The default serial communication settings is slave
    address 1, Modbus RTU, 9600bps, 8 data bits and 1 stop bit.

    Following Modbus function code are supported by sensor.
    Modbus Function Code 0x03 : used for reading holding register.
    Modbus Function Code 0x04 : used for reading input register.
    Modbus Function Code 0x06 : used for writing single holding register.
    Modbus Function Code 0x10: used for writing multiple holding register.

    Register value          Register Addr (HEX/DEC) Data    Type    Function code (DEC)     Range and Comments          Default Value
    TEMPRATURE              0x0000 /0               INT16   RO      3/4
    WETNESS                 0x0001 /1               UINT16  RO      3/4                     0-10000 for 0-100%             N/A
    TEMPUNIT                0x0020 /32              UINT16  R/W     3/6/16                  0: °C / 1: ℉                   0 
    TEMPCALIB               0x0021 /33              INT16   R/W     3/6/16                  -999-999 for -9.99~9.99°C       0
    SLAVEADDRESS            0x0200 /512             UINT16  R/W     3/6/16                  0-255                           1
    BAUDRATE                0x0201 /513             UINT16  R/W     3/6/16                  3:9600bps/4:19200bps            3:9600bps
    RESPONSEDELAY           0x0206 /518             UINT16  R/W     3/6/16                  0-255 for 0-2550ms              0
    ACTIVEOUTPUTINTERVAL    0x0207 /519             UINT16  R/W     3/6/16                  0-255 for 0-255ms               0

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
        functioncode: int = 16,
        signed: bool = False,
    )
    """

    def __init__(self,
                 portname, 
                 slaveaddress=11,
                 mode='MODE_RTU',
                 close_port_after_each_call=False,
                 debug=False):
        minimalmodbus.Instrument.__init__(self,
                                          portname, 
                                          slaveaddress=slaveaddress,
                                          mode=mode,
                                          close_port_after_each_call=close_port_after_each_call, 
                                          debug=debug)
        self.serial.baudrate = 9600
        # self.mode = minimalmodbus.MODE_RTU

    # Returns temperature -40.00~80.00 Celcius
    def get_temperature(self):
        # Get the temperature value from Register 0, which is (signed) INT16
        return self.read_register(registeraddress=0,
                                  number_of_decimals=2,
                                  functioncode=3,
                                  signed=True)
    
    # Returns leaf wetness 0-100%
    def get_wetness(self):
        # Get the wetness / humidity value from Register 1, which is UINT16
        return self.read_register(registeraddress=1,
                                  number_of_decimals=2,
                                  functioncode=3,
                                  signed=False)
    
    def set_slave_address(self, slaveaddress):
        # Write slave address to Register 512
        self.write_register(registeraddress=512,
                            value=slaveaddress,
                            number_of_decimals=0,
                            functioncode=6,
                            signed=False)
                            
    def get_baudrate(self):
        return self.read_register(registeraddress=0x0201,
                                  functioncode=0x03)

    # A function to fetch and print data from the sensor
    def fetch_and_print_data(self):
        print("\nS-YM-01, Modbus - Time: ", datetime.datetime.now())
        print("Temperature: %0.1f C" % self.get_temperature())
        print("Wetness: %0.1f %%" % self.get_wetness())

    # A function to fetch and return data from the sensor
    def fetch_and_return_data(self):
        data["fields"]["temperature"] =  self.get_temperature()
        data["fields"]["wetness"] = self.get_wetness()
        data["time"] = datetime.datetime.now().isoformat()
        return data

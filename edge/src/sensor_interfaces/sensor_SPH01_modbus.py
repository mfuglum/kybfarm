import minimalmodbus
import datetime

# A dictionary struct to send as payload over MQTT
data = {
    "measurement": "pH and Temperature",
    "tags": {
        "sensor_id": "5",
        "location": "Gloeshaugen",
        "sensor_name": "S-PH-01"},
    "fields": {
        "ph": 0,
        "temperature": 0,
        "calibrated": 0},
    "time": datetime.datetime.now().isoformat()
}

# The device / Instrument class for Seeed Studio SenseCAP S-PH-01 pH and Temperature sensor
class SPH01( minimalmodbus.Instrument ):
    """Instrument class for S-PH-01 pH and Temperature sensor.
    
    Args:
        * portname (str):                       port name
                                                Default is '/dev/ttySC1', which is the address to the RS-485 hat of the Raspberry Pi 4B
        * slaveaddress (int):                   slave address in the range 1 to 247
                                                Default is 4 (from manufacturer)
        * mode (str):                           Mode of communication.
                                                Default is minimalmodbus.MODE_RTU
        * close_port_after_each_call (bool):    Whether to close the port after each call.
                                                Default is False
        * debug (bool):                         Whether to print debug information.
                                                Default is False

    From datasheet, Ch. 6 Modbus Communication Protocol

    The default communication parameters is slave
    address 1, Modbus RTU, 9600bps, 8 data bits, 1 stop bit, no parity.
    
    Following Modbus function code are supported by sensor.
    Modbus Function Code 0x03 : used for reading holding register.
    Modbus Function Code 0x04 : used for reading input register.
    Modbus Function Code 0x06 : used for writing single holding register.
    Modbus Function Code 0x10: used for writing multiple holding register.
    
    Register value           Register Addr (HEX/DEC)  Data     Type   Function code (DEC)   Range and Comments                                                     Default Value
    Temperature              0x0000/0                 INT16    RO     3/4                   -4000-8000 for -40.00-80.00 C                                          N/A
    pH                       0x0001/1                 INT16    RO     3/4                   0-1400 for 0.00-14.00 pH                                               N/A
    PHCALIBRAWAD             0x0002/2                 INT16    RO     3/4                   -2000-2000 corresponds to -2000-2000                                   N/A
    TEMPCOMPENSATION         0x0020/32                INT16    RW     3/6/16                Temp. comp. 0: Turn on, 1: Turn off                                    0
    PHCALIB_0401             0x0030/48                INT16    RW     3/6/16                Calibrate pH 4.01, stored as -2000-2000, Write 0xFFFF to calibrate     N/A
    PHCALIB_0700             0x0031/49                INT16    RW     3/6/16                Calibrate pH 7.00, stored as -2000-2000, Write 0xFFFF to calibrate     N/A
    PHCALIB_1001             0x0032/50                INT16    RW     3/6/16                Calibrate pH 10.01, stored as -2000-2000, Write 0xFFFF to calibrate    N/A
    SLAVEADDRESS             0x0200/512               INT16    RW     3/6/16                Read or write addr. in range 0-255                                     1
    BAUDRATE                 0x0201/513               INT16    RW     3/6/16                Read or write baudrate in range 0-5                                    3:9600bps

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
                 slaveaddress=4, 
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
    
    # Returns temperature -40.00~80.00 Celcius
    def get_temperature(self):
        return self.read_register(registeraddress=0,
                                  number_of_decimals=2,
                                  functioncode=3,
                                  signed=True)
    
    # Returns pH 0.00~14.00
    def get_pH(self):
        return self.read_register(registeraddress=1,
                                  number_of_decimals=2,
                                  functioncode=3,
                                  signed=False)
    
    # A function to fetch and return data from the sensor
    def fetch_and_return_data(self):
        temperature = self.get_temperature()
        pH = self.get_pH()

        data["fields"]["temperature"] = temperature
        data["fields"]["ph"] = pH
        data["time"] = datetime.datetime.now().isoformat()
        data["tags"]["sensor_id"] = self.address
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
    
    def get_temperature_compensation(self):
        return self.read_register(registeraddress=32,
                                  functioncode=3)
    
    def set_temperature_compensation(self, value):
        self.write_register(registeraddress=32,
                            value=value,
                            functioncode=6,
                            signed=False)
        
    # Coefficients
    def get_ph_calib_raw_ad(self):
        return self.read_register(registeraddress=2,
                                  functioncode=3) 
    
    def get_ph_calib_4_01(self):
        return self.read_register(registeraddress=48,
                                  functioncode=3)
    
    def get_ph_calib_7_00(self):
        return self.read_register(registeraddress=49,
                                  functioncode=3)
    
    def get_ph_calib_10_01(self):
        return self.read_register(registeraddress=50,
                                  functioncode=3)
    
    # Calibration functions
    def calibrate_ph_0401(self):
        self.write_register(registeraddress=48,
                            value=0xFFFF,
                            number_of_decimals=0,
                            functioncode=6,
                            signed=False)
        # Return data struct with calibrated field set to the timestamp
        time = datetime.datetime.now().isoformat()
        data["time"] = time
        data["sensor_id"] = self.address
        data["fields"]["calibrated"] = time
        return data
        
    def calibrate_ph_0700(self):
        self.write_register(registeraddress=49,
                            value=0xFFFF,
                            number_of_decimals=0,
                            functioncode=6,
                            signed=False)
        # Return data struct with calibrated field set to the timestamp
        time = datetime.datetime.now().isoformat()
        data["time"] = time
        data["sensor_id"] = self.address
        data["fields"]["calibrated"] = time
        return data
    
    def calibrate_ph_1001(self):
        self.write_register(registeraddress=50,
                            value=0xFFFF,
                            number_of_decimals=0,
                            functioncode=6,
                            signed=False)
        # Return data struct with calibrated field set to the timestamp
        time = datetime.datetime.now().isoformat()
        data["time"] = time
        data["sensor_id"] = self.address
        data["fields"]["calibrated"] = time
        return data

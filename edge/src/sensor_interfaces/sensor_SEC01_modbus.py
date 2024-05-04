import minimalmodbus
import datetime

# A dictionary struct to send as payload over MQTT
data = {
    "measurement": "EC, TDS, Salinity and Temperature",
    "tags": {
        "sensor_id": "03",
        "location": "Gloeshaugen",
        "sensor_name": "S-EC-01"},
    "fields": {
            "ec": 0,
            "temperature": 0,
            "calibrated": 0,},
    "time": datetime.datetime.now().isoformat(),
}

# The device / Instrument class for Seeed Studio SenseCAP S-EC-01 EC, TDS, Salinity and Temperature sensor
class SEC01( minimalmodbus.Instrument ):
    """Instrument class for S-EC-01 EC, TDS, Salinity and Temperature sensor.
    
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
    
    From datasheet, Ch. 7 RS485 Modbus Protocol:

    The default serial communication settings is slave
    address 1, Modbus RTU, 9600bps, 8 data bits and 1 stop bit.

    Following Modbus function code are supported by sensor.
    Modbus Function Code 0x03 : used for reading holding register.
    Modbus Function Code 0x04 : used for reading input register.
    Modbus Function Code 0x06 : used for writing single holding register.
    Modbus Function Code 0x10: used for writing multiple holding register.

    Register value               Register Addr (HEX/DEC) Data    Type    Function code (DEC)     Range and Comments                         Default Value
    Temperature                  0x0000 /0               INT16   RO      3/4                     -4000-8000 for -40.00-80.00 C              N/A
    EC                           0x0002 /2               UINT16  RO      3/4                     0-20000 for 0-20000 µS/cm                  N/A
    Salinity                     0x0003 /3               UINT16  RO      3/4                     0-20000 for 0-20000 mg/L                   N/A
    TDS                          0x0004 /4               UINT16  RO      3/4                     0-20000 for 0-20000 mg/L                   N/A
    TEMPCOMPENSATION             0x0020 /32              UINT16  R/W     3/6/16                  0: External / 1: Internal / 2: Disabled    0
    ECTEMPCOFF                   0x0022 /34              UINT16  R/W     3/6/16                  0-100 for 0.0% - 10.0%                     20(2%)
    SALINITYCOFF                 0x0023 /35              UINT16  R/W     3/6/16                  0-100 for 0.00 - 1.00                      55(0.55)
    TDSCOFF                      0x0024 /36              UINT16  R/W     3/6/16                  0-100 for 0.00 - 1.00                      50(0.50)
    ELECTRODECONSTANT            0x0025 /37              UINT16  R/W     3/6/16                  500-1500 for 0.500-1.500                   1000(1.000)
    ECCALIB_1413US               0x0030 /48              UINT16  R/W     3/6/16                  Write 0xFFFF when in 1413us/cm             223
    ECCALIB_12880US              0x0031 /49              UINT16  R/W     3/6/16                  Write 0xFFFF when in 12880us/cm            1851
    SLAVEADDRESS                 0x0200 /512             UINT16  R/W     3/6/16                  1-255                                      1 or 30
    BAUDRATE                     0x0201 /513             UINT16  R/W     3/6/16                  3:9600bps/4:19200bps                       3:9600bps     

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
                 slaveaddress=30,
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
        # Get the temperature value from Register 0, which is (signed) INT16
        return self.read_register(registeraddress=0,
                                  number_of_decimals=2,
                                  functioncode=3,
                                  signed=True)
    
    # Returns EC 0-20000 µS/cm
    def get_ec(self):
        # Get the EC value from Register 2, which is UINT16
        return self.read_register(registeraddress=2,
                                  number_of_decimals=0,
                                  functioncode=3,
                                  signed=False)
    
    # Returns Salinity 0-20000 mg/L
    def get_salinity(self):
        # Get the salinity value from Register 3, which is UINT16
        return self.read_register(registeraddress=3,
                                  number_of_decimals=0,
                                  functioncode=3,
                                  signed=False)
    
    # Returns TDS 0-20000 mg/L
    def get_tds(self):
        # Get the TDS value from Register 4, which is UINT16
        return self.read_register(registeraddress=4,
                                  number_of_decimals=0,
                                  functioncode=3,
                                  signed=False)
    
    # A function to fetch and print data from the sensor
    def fetch_and_print_data(self):
        temperature = self.get_temperature()
        ec = self.get_ec()
        # salinity = self.get_salinity()
        # tds = self.get_tds()
        print(f"Temperature: {temperature} C\n")
        print(f"EC: {ec} µS/cm\n")
        # print(f"Salinity: {salinity} mg/L\n")
        # print(f"TDS: {tds} mg/L\n")

    # A function to fetch and return data from the sensor
    def fetch_and_return_data(self):
        temperature = self.get_temperature()
        ec = self.get_ec()
        # salinity = self.get_salinity()
        # tds = self.get_tds()
        data["fields"]["temperature"] = temperature
        data["fields"]["ec"] = ec
        # data["fields"]["salinity"] = salinity
        # data["fields"]["tds"] = tds
        data["time"] = datetime.datetime.now().isoformat()
        data["tags"]["sensor_id"] = self.address
        return data
    
    def get_slave_address(self):
        return self.read_register(registeraddress=512,
                                  functioncode=3)
    
    def set_slave_address(self, slaveaddress):
        # Write slave address to Register 512
        self.write_register(registeraddress=512,
                            value=slaveaddress,
                            number_of_decimals=0,
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
                            number_of_decimals=0,
                            functioncode=6,
                            signed=False)

    # Coefficients, abbreviated as coff in the register names
    def get_ec_temp_coff(self):
        return self.read_register(registeraddress=34,
                                  functioncode=3)
    
    def set_ec_temp_coff(self, value):
        self.write_register(registeraddress=34,
                            value=value,
                            number_of_decimals=0,
                            functioncode=6,
                            signed=False)
    
    def get_salinity_coff(self):
        return self.read_register(registeraddress=35,
                                  functioncode=3)
    
    def set_salinity_coff(self, value):
        self.write_register(registeraddress=35,
                            value=value,
                            number_of_decimals=0,
                            functioncode=6,
                            signed=False)
    
    def get_tds_coff(self):
        return self.read_register(registeraddress=36,
                                  functioncode=3)
    
    def set_tds_coff(self, value):
        self.write_register(registeraddress=36,
                            value=value,
                            number_of_decimals=0,
                            functioncode=6,
                            signed=False)
    
    def get_electrode_constant(self):
        return self.read_register(registeraddress=37,
                                  functioncode=3)
    
    def set_elecrode_constant(self, value):
        self.write_register(registeraddress=37,
                            value=value,
                            number_of_decimals=0,
                            functioncode=6,
                            signed=False)
    
    # Calibration functions
    # Immerse the electrode in 1413us/cm solution for a while and 
    # write 0xFFFF into the register to perform the auto calibration
    def calibrate_ec_1413us(self):
        try:
            self.write_register(registeraddress=48,
                                value=0xFFFF,
                                number_of_decimals=0,
                                functioncode=6,
                                signed=False)
        except Exception as e:
            return str(e)
        # Return data struct with calibrated field set to 1 (True)
        data["time"] = datetime.datetime.now().isoformat()
        data["tags"]["sensor_id"] = self.address
        data["fields"]["calibrated"] = 1
        return data        
    
    def read_ec_1413us(self):
        return self.read_register(registeraddress=48,
                                  functioncode=3)
    
    # Immerse the electrode in 12880us/cm solution for a while and 
    # write 0xFFFF into the register to perform the auto calibration
    def calibrate_ec_12880us(self):
        self.write_register(registeraddress=49,
                            value=0xFFFF,
                            number_of_decimals=0,
                            functioncode=6,
                            signed=False)
    
    def read_ec_12880us(self):
        return self.read_register(registeraddress=49,
                                  functioncode=3)
    


import minimalmodbus
import datetime

# A dictionary struct to send as payload over MQTT
data = {
    "measurement": "photosynthetically active radiation",
    "tags": {
        "sensor_id": "02",
        "location": "Gloeshaugen",
        "sensor_name": "S-PAR-02"},
    "fields": {
            "par": 0},
    "time": datetime.datetime.now().isoformat(),
}

# The device / Instrument class for Seeed Studio SenseCAP S-PAR-02 Photosynthetically Active Radiation sensor
class SPAR02( minimalmodbus.Instrument ):
    """Instrument class for S-PAR-02 Photosynthetically Active Radiation sensor.

    Args:
        * portname (str):                       port name
                                                Default is '/dev/ttySC1', which is the address to the RS-485 hat of the Raspberry Pi 4B
        * slaveaddress (int):                   slave address in the range 1 to 247
                                                Default is 34 (from manufacturer)
        * mode (str):                           Mode of communication.
                                                Default is minimalmodbus.MODE_RTU
        * close_port_after_each_call (bool):    Whether to close the port after each call.
                                                Default is False
        * debug (bool):                         Whether to print debug information.
                                                Default is False

    
                                
    From datasheet, Sec. Modbus-RTU RS485:
    Standard Modbus-RTU protocol, baud rate: 9600; parity bit: none; data bit: 8; stop bit: 1.

    Register value             Register Addr (HEX/DEC) Data    Type    Function code (DEC)     Range and Comments          Default Value
    PAR                        0x0001 /1               UINT16  -       3                       0-2500 for 0-2500 µmol/m²/s   N/A

    Functions used from minimalmodbus API:
    https://minimalmodbus.readthedocs.io/en/stable/_modules/minimalmodbus.html#Instrument.read_bit

    Read a long integer (32 or 64 bits) from the slave:
    def read_long(
        self,
        registeraddress: int,
        functioncode: int = 3,
        signed: bool = False,
        byteorder: int = BYTEORDER_BIG,
        number_of_registers: int = 2,
    ) -> int:
    """

    def __init__(self, 
                 portname='/dev/ttySC1', 
                 slaveaddress=34, 
                 mode=minimalmodbus.MODE_RTU, 
                 close_port_after_each_call=False, 
                 debug=False):
        minimalmodbus.Instrument.__init__(self, 
                                          portname, 
                                          slaveaddress, 
                                          mode, 
                                          close_port_after_each_call, 
                                          debug)
        
    # Returns the value of the Photosynthetically Active Radiation (PAR) in µmol/m²/s
    def get_par(self):
        par = self.read_long(registeraddress=1,
                             functioncode=3,
                             signed=False,
                             byteorder=minimalmodbus.BYTEORDER_BIG,
                             number_of_registers=2)

        return par
        
    # A function to fetch and print data from the sensor
    def fetch_and_print_data(self):
        par = self.get_par()
        print(f"Photosynthetically Active Radiation (PAR): {par} µmol/m²/s")

    # A function to fetch and return data from the sensor
    def fetch_and_return_data(self):
        par = self.get_par()
        data["fields"]["par"] = par
        data["time"] = datetime.datetime.now().isoformat()
        return data
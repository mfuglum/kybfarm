import minimalmodbus
import datetime

class WLS01(minimalmodbus.Instrument):
    """
    Instrument class for Submersible Water Level Sensor with RS-485 Modbus RTU.
    
    Based on typical configuration from datasheet:
    - Communication: RS-485 Modbus RTU
    - Baudrate: 9600
    - Parity: None
    - Default Slave Address: Example 1 (set on sensor)
    - Register for Pressure: e.g. 0x0001 / 1 (see datasheet)
    - Register for Temperature (if available): e.g. 0x0002 / 2
    - Register for Unit selection (optional): e.g. 0x0190 / 400
    
    """
    def __init__(self,
                 portname='/dev/ttySC1',
                 slaveaddress=1,  # set this per sensor
                 mode=minimalmodbus.MODE_RTU,
                 close_port_after_each_call=False,
                 debug=False):
        super().__init__(portname,
                         slaveaddress=slaveaddress,
                         mode=mode,
                         close_port_after_each_call=close_port_after_each_call,
                         debug=debug)
        self.serial.baudrate = 9600
        self.serial.parity = minimalmodbus.serial.PARITY_NONE

    def get_pressure_kPa(self):
        """ Read raw pressure (kPa) from register address 1 """
        pressure = self.read_register(registeraddress=1,
                                      number_of_decimals=2,
                                      functioncode=3,
                                      signed=False)
        return pressure

    def get_water_level_cm(self, span_kPa=20.0):
        """ Convert pressure to water column height in cm.
            1 kPa ~ 10.2 cm H2O.
            Uses span_kPa for scale factor.
        """
        pressure_kPa = self.get_pressure_kPa()
        level_cm = pressure_kPa * 10.2  # Adjust for your sensor specs
        return level_cm

    def fetch_and_return_data(self, sensor_name):
        level_cm = self.get_water_level_cm()
        pressure_kPa = self.get_pressure_kPa()

        data = {
            "measurement": "WaterLevel",
            "tags": {
                "sensor_name": sensor_name
            },
            "fields": {
                "level_cm": level_cm,
                "pressure_kPa": pressure_kPa
            },
            "time": datetime.datetime.now().isoformat(),
        }
        return data

    def get_slave_address(self):
        return self.read_register(registeraddress=512,
                                  functioncode=3)

    def set_slave_address(self, slaveaddress):
        self.write_register(registeraddress=512,
                            value=slaveaddress,
                            functioncode=6,
                            signed=False)

    def get_baudrate(self):
        return self.read_register(registeraddress=513,
                                  functioncode=3)

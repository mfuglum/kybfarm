import minimalmodbus
import datetime

class SLLE01(minimalmodbus.Instrument):
    """
    Instrument class for S-LLE-01 (S-YW-01B) Liquid Level Sensor with RS-485 Modbus RTU.

```
    Datasheet-based configuration:
    - Communication: RS-485 Modbus RTU
    - Default Baudrate: 9600 (can be changed via register 0x0001)
    - Default Slave Address: 0x1A (26 decimal, can be changed via register 0x0000)
    - Measurement Register: 0x0004
    - Units selectable via register 0x0002 (e.g. cm, mm, kPa, etc.)
    """

    def __init__(self,
                portname='/dev/ttySC1',
                slaveaddress=26,  # default = 0x1A
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
        self.serial.bytesize = 8
        self.serial.stopbits = 1
        self.sensor_name = "S-LLE-01"

    def get_measurement_value(self):
        """ Read raw measurement value (register 0x0004). """
        value = self.read_register(registeraddress=4,
                                number_of_decimals=2,
                                functioncode=3,
                                signed=True)
        return value

    def get_slave_address(self):
        """ Read current slave address (register 0x0000). """
        return self.read_register(registeraddress=0,
                                functioncode=3)

    def set_slave_address(self, new_address):
        """ Write a new slave address (register 0x0000). """
        self.write_register(registeraddress=0,
                            value=new_address,
                            functioncode=6,
                            signed=False)

    def get_baudrate_code(self):
        """ Read baudrate setting code (register 0x0001). """
        return self.read_register(registeraddress=1,
                                functioncode=3)

    def set_baudrate_code(self, code):
        """
        Set baudrate code in register 0x0001.
        Codes:
        0=1200, 1=2400, 2=4800, 3=9600, 4=19200, 5=38400, 6=57600, 7=115200
        """
        self.write_register(registeraddress=1,
                            value=code,
                            functioncode=6,
                            signed=False)

    def get_unit_code(self):
        """ Read unit setting (register 0x0002). """
        return self.read_register(registeraddress=2,
                                functioncode=3)

    def get_zero_point(self):
        """ Read zero point calibration value (register 0x0005). """
        return self.read_register(registeraddress=5,
                                functioncode=3,
                                signed=True)

    def fetch_and_return_data(self):
        """ Fetch current measurement packaged as dict for logging. """
        measurement = self.get_measurement_value()
        unit_code = self.get_unit_code()

        data = {
            "measurement": "LiquidLevel",
            "tags": {
                "sensor_name": self.sensor_name,
                "unit_code": unit_code
            },
            "fields": {
                "value": measurement
            },
            "time": datetime.datetime.now().isoformat(),import minimalmodbus
import datetime

class SLLE01(minimalmodbus.Instrument):
    """
    Instrument class for S-LLE-01 (S-YW-01B) Liquid Level Sensor with RS-485 Modbus RTU.

    Datasheet-based configuration:
    - Communication: RS-485 Modbus RTU
    - Default Baudrate: 9600 (can be changed via register 0x0001)
    - Default Slave Address: 0x1A (26 decimal, can be changed via register 0x0000)
    - Measurement Register: 0x0004
    - Units selectable via register 0x0002 (e.g. cm, mm, kPa, etc.)
    """

    def __init__(self,
                 portname='/dev/ttySC1',
                 slaveaddress=26,  # default = 0x1A
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
        self.serial.bytesize = 8
        self.serial.stopbits = 1
        self.sensor_name = "S-LLE-01"

        # Force unit setting to centimeters (register 0x0002 = 1)
        # NOTE: the datasheet mentions the device may require a power cycle
        # to apply certain changes; if the register write appears ineffective,
        # power-cycle the sensor.
        try:
            current_unit = self.get_unit_code()
            if current_unit != 1:
                self.write_register(registeraddress=2, value=1, functioncode=6, signed=False)
        except Exception as e:
            print(f"[{self.sensor_name}] Warning: could not set unit to cm ({e})")

    def get_measurement_value(self):
        """ Read raw measurement value (register 0x0004) - in centimeters. """
        return self.read_register(registeraddress=4,
                                  number_of_decimals=2,
                                  functioncode=3,
                                  signed=True)

    def get_slave_address(self):
        """ Read current slave address (register 0x0000). """
        return self.read_register(registeraddress=0,
                                  number_of_decimals=0,
                                  functioncode=3,
                                  signed=False)

    def set_slave_address(self, new_address):
        """ Write a new slave address (register 0x0000). """
        self.write_register(registeraddress=0,
                            value=int(new_address),
                            functioncode=6,
                            signed=False)

    def get_baudrate_code(self):
        """ Read baudrate setting code (register 0x0001). """
        return self.read_register(registeraddress=1,
                                  number_of_decimals=0,
                                  functioncode=3,
                                  signed=False)

    def set_baudrate_code(self, code):
        """ Set baudrate code in register 0x0001. Codes:
        0=1200, 1=2400, 2=4800, 3=9600, 4=19200, 5=38400, 6=57600, 7=115200 """
        self.write_register(registeraddress=1,
                            value=int(code),
                            functioncode=6,
                            signed=False)

    def get_unit_code(self):
        """ Read unit setting (register 0x0002). """
        return self.read_register(registeraddress=2,
                                  number_of_decimals=0,
                                  functioncode=3,
                                  signed=False)

    def get_zero_point(self):
        """ Read zero point calibration value (register 0x0005). """
        return self.read_register(registeraddress=5,
                                  number_of_decimals=2,
                                  functioncode=3,
                                  signed=True)

    def fetch_and_return_data(self):
        """
        Fetch the current measurement packaged as dict for logging.
        Returns both water level (cm) and equivalent hydrostatic pressure (kPa).
        """
        timestamp = datetime.datetime.now().isoformat()
        try:
            level_cm = self.get_measurement_value()
            # compute pressure (kPa) from level in cm:
            # level_m = level_cm / 100.0
            # pressure_pa = rho * g * level_m  -> kPa = pressure_pa / 1000
            pressure_kPa = 0.0980665 * level_cm  # ρgh with ρ≈1000 kg/m³, g≈9.80665 m/s²

            data = {
                "measurement": "LiquidLevelPressure",
                "tags": {
                    "sensor_name": self.sensor_name,
                    "unit": "cm/kPa"
                },
                "fields": {
                    "level_cm": round(level_cm, 2),
                    "pressure_kPa": round(pressure_kPa, 3)
                },
                "time": timestamp,
            }
            return data

        except Exception as e:
            # Return an error structure instead of raising (adjust to your pipeline style)
            return {
                "measurement": "LiquidLevelPressure",
                "tags": {"sensor_name": self.sensor_name},
                "fields": {"error": str(e)},
                "time": timestamp
            }

        }
        return data


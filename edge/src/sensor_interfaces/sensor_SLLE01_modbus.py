import minimalmodbus
import datetime

class SLLE01(minimalmodbus.Instrument):
    """
    SLLE01 liquid level sensor Modbus interface.

    Fixes:
    - Use device decimal point register (0x0003) instead of hardcoding decimals.
    - Do not force unit writes (register 0x0002 may not be writable / may not apply).
    - Interpret unit_code 8 as millimeters (observed in field).
    """

    def __init__(self,
                 portname='/dev/ttySC1',
                 slaveaddress=26,
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

    # --- raw config reads ---
    def get_unit_code(self):
        return self.read_register(registeraddress=2, number_of_decimals=0, functioncode=3, signed=False)

    def get_decimal_points(self):
        return self.read_register(registeraddress=3, number_of_decimals=0, functioncode=3, signed=False)

    def get_zero_point(self):
        return self.read_register(registeraddress=5, number_of_decimals=0, functioncode=3, signed=True)

    # --- measurement ---
    def get_measurement_value(self):
        """
        Read measurement register 0x0004 with correct scaling.
        Returns a float in the sensor's configured engineering units.
        """
        dp = int(self.get_decimal_points())
        return self.read_register(registeraddress=4,
                                  number_of_decimals=dp,
                                  functioncode=3,
                                  signed=True)

    def get_level_cm(self):
        """
        Convert measurement to cm based on the configured unit.
        Field-observed: unit_code=8 behaves like millimeters with dp=0.
        """
        unit = int(self.get_unit_code())
        val = float(self.get_measurement_value())

        # Datasheet: 1=cm, 2=mm, 5=kPa (etc.)
        # Field: unit=8 -> treat as mm
        if unit == 1:          # cm
            return val
        elif unit in (2, 8):   # mm (8 observed)
            return val / 10.0
        elif unit == 5:        # kPa -> convert to cmH2O
            return val * 10.197
        else:
            # Unknown: try to infer by plausibility; default to mm-like behavior.
            # This is conservative because it avoids huge level values.
            return val / 10.0

    def fetch_and_return_data(self):
        timestamp = datetime.datetime.now().isoformat()
        try:
            unit = int(self.get_unit_code())
            dp = int(self.get_decimal_points())
            meas = float(self.get_measurement_value())
            level_cm = float(self.get_level_cm())

            # derive pressure estimate from level (for logging only)
            pressure_kPa_est = 0.0980665 * level_cm

            return {
                "measurement": "LiquidLevel",
                "tags": {
                    "sensor_name": self.sensor_name,
                    "unit_code": unit,
                    "decimal_points": dp,
                },
                "fields": {
                    "raw_measurement": meas,
                    "level_cm": round(level_cm, 2),
                    "pressure_kPa_est": round(pressure_kPa_est, 3),
                },
                "time": timestamp,
            }
        except Exception as e:
            return {
                "measurement": "LiquidLevel",
                "tags": {"sensor_name": self.sensor_name},
                "fields": {"error": str(e)},
                "time": timestamp
            }

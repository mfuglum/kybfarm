import minimalmodbus
import datetime
import struct

# Interface for EE671 Air Flow Probe sensor (Modbus RTU)
class EE671(minimalmodbus.Instrument):
    """
    Minimal interface:
      - get_temperature() -> °C (FLOAT32)
      - get_air_velocity_ms() -> m/s (FLOAT32)
      - fetch_and_return_data() -> dict with 'measurement','tags','fields','time'
    Default registers follow the device manual examples but can be overridden.
    """

    DEFAULT_TEMP_REG = 0x03EA  # 1002
    DEFAULT_VEL_REG  = 0x0410  # 1040

    def __init__(self, portname='/dev/ttySC0', slaveaddress=238,
                 baudrate=9600,
                 temp_reg=None,
                 vel_reg=None,
                 debug=False):
        super().__init__(portname, slaveaddress=slaveaddress, mode=minimalmodbus.MODE_RTU,
                         close_port_after_each_call=False, debug=debug)
        self.serial.baudrate = baudrate
        self.serial.parity = minimalmodbus.serial.PARITY_EVEN
        self.serial.bytesize = 8
        self.serial.stopbits = 1
        self.temp_reg = temp_reg or self.DEFAULT_TEMP_REG
        self.vel_reg = vel_reg or self.DEFAULT_VEL_REG
        self.sensor_name = "EE671"

    def _read_float32(self, registeraddress):
        """Read two registers and unpack FLOAT32 using manual byte re-ordering."""
        hi = self.read_register(registeraddress, number_of_decimals=0, functioncode=3, signed=False)
        lo = self.read_register(registeraddress + 1, number_of_decimals=0, functioncode=3, signed=False)
        # bytes: hi -> [hi_hi, hi_lo], lo -> [lo_hi, lo_lo]
        b_hi_hi = (hi >> 8) & 0xFF
        b_hi_lo = hi & 0xFF
        b_lo_hi = (lo >> 8) & 0xFF
        b_lo_lo = lo & 0xFF
        reordered = bytes([b_lo_hi, b_lo_lo, b_hi_hi, b_hi_lo])
        return struct.unpack('>f', reordered)[0]

    def get_temperature(self):
        return round(self._read_float32(self.temp_reg), 3)

    def get_air_velocity_ms(self):
        return round(self._read_float32(self.vel_reg), 4)

    def get_slave_address(self):
        return self.read_register(0, number_of_decimals=0, functioncode=3, signed=False)

    def set_slave_address(self, new_address):
        return self.write_register(0, int(new_address), functioncode=6, signed=False)

    def fetch_and_return_data(self):
        timestamp = datetime.datetime.now().isoformat()
        fields = {"temperature_c": None, "air_velocity_ms": None, "air_velocity_ft_min": None}
        try:
            t = self.get_temperature()
            v = self.get_air_velocity_ms()
            fields["temperature_c"] = t
            fields["air_velocity_ms"] = v
            fields["air_velocity_ft_min"] = round(v * 196.8503937, 2)  # m/s -> ft/min
        except Exception as e:
            fields["error"] = str(e)

        return {
            "measurement": "airflow",
            "tags": {"sensor_name": self.sensor_name},
            "fields": fields,
            "time": timestamp
        }

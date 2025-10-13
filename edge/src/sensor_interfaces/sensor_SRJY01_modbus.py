import minimalmodbus
import datetime

class SRJY01(minimalmodbus.Instrument):
    """
    Instrument class for S-RJY-01 Dissolved Oxygen (ODO) sensor (RS485 Modbus/RTU).

    Registers (per supplied datasheet):
      - 0x0101 (257) : ODO value (mg/L * 100)       (read)
      - 0x0100 (256) : temperature (°C * 10)        (read)
      - 0x0102 (258) : ODO saturation (% * 10)     (read)
      - 0x0000 (0)   : block read (value+decimals+temp+decimals) (read 4 regs)
      - 0x1001 (4097): ODO zero calibration        (write/read)
      - 0x1003 (4099): ODO slope calibration       (write/read)
      - 0x1000 (4096): temperature calibration     (write/read)
      - 0x2000 (8192): sensor address (default 55) (write/read)
      - 0x2003 (8195): baud rate setting (0/1/2 -> 4800/9600/19200) (write/read)
      - 0x2020 (8224): reset sensor (write 0)
    """

    def __init__(self,
                 portname='/dev/ttySC1',
                 slaveaddress=55,   # datasheet default = 55 decimal
                 mode=minimalmodbus.MODE_RTU,
                 close_port_after_each_call=False,
                 debug=False):
        super().__init__(portname,
                         slaveaddress=slaveaddress,
                         mode=mode,
                         close_port_after_each_call=close_port_after_each_call,
                         debug=debug)

        # serial config from datasheet
        self.serial.baudrate = 9600
        self.serial.parity = minimalmodbus.serial.PARITY_NONE
        self.serial.bytesize = 8
        self.serial.stopbits = 1

        self.sensor_name = "S-RJY-01"

        # register addresses (use integer version of hex addresses in datasheet)
        self._reg_odo = 0x0101      # 257
        self._reg_temp = 0x0100     # 256
        self._reg_sat = 0x0102      # 258
        self._reg_block = 0x0000    # 0 (4 registers)
        self._reg_zero = 0x1001     # 4097
        self._reg_slope = 0x1003    # 4099
        self._reg_temp_cal = 0x1000 # 4096
        self._reg_addr = 0x2000     # 8192
        self._reg_baud = 0x2003     # 8195
        self._reg_reset = 0x2020    # 8224

        # conversion factors (per datasheet)
        # ODO stored as integer = mg/L * 100  -> divide by 100
        # temperature stored as integer = °C * 10 -> divide by 10
        # saturation stored as integer = % * 10  -> divide by 10

    # -----------------------
    # Low-level reads/writes
    # -----------------------
    def read_register_safe(self, register, decimals=0, signed=False):
        """Read register with safe error propagation (raises on minimalmodbus exceptions)."""
        return self.read_register(registeraddress=register,
                                  number_of_decimals=decimals,
                                  functioncode=3,
                                  signed=signed)

    def read_registers_safe(self, register, count=1):
        """Read multiple registers (function code 3)."""
        return self.read_registers(registeraddress=register,
                                   number_of_registers=count,
                                   functioncode=3)

    # -----------------------
    # Basic sensor getters
    # -----------------------
    def get_odo_raw(self):
        """Read raw ODO integer (mg/L * 100)."""
        return self.read_register_safe(self._reg_odo, decimals=0, signed=False)

    def get_temperature_raw(self):
        """Read raw temperature integer (°C * 10)."""
        return self.read_register_safe(self._reg_temp, decimals=0, signed=False)

    def get_saturation_raw(self):
        """Read raw saturation integer (% * 10)."""
        return self.read_register_safe(self._reg_sat, decimals=0, signed=False)

    def read_block_0(self):
        """
        Read registers starting at 0x0000: returns list of 4 registers according to datasheet:
          [measured_value_high, measured_value_decimals, temperature_value, temperature_decimals]
        Use this if single-block read required by some firmwares.
        """
        return self.read_registers_safe(self._reg_block, count=4)

    # -----------------------
    # Comms & config helpers
    # -----------------------
    def get_slave_address(self):
        """Read sensor Modbus address (register 0x2000)."""
        return self.read_register_safe(self._reg_addr, decimals=0, signed=False)

    def set_slave_address(self, new_addr):
        """Write new Modbus address (register 0x2000)."""
        return self.write_register(registeraddress=self._reg_addr,
                                   value=int(new_addr),
                                   functioncode=6,
                                   signed=False)

    def get_baudrate_code(self):
        """Read baudrate code (0->4800,1->9600,2->19200) from register 0x2003."""
        return self.read_register_safe(self._reg_baud, decimals=0, signed=False)

    def set_baudrate_code(self, code):
        """Write baudrate code to register 0x2003 (0..2)."""
        return self.write_register(registeraddress=self._reg_baud,
                                   value=int(code),
                                   functioncode=6,
                                   signed=False)

    def reset_sensor(self):
        """Write reset command to 0x2020 (write 0 as per datasheet)."""
        return self.write_register(registeraddress=self._reg_reset,
                                   value=0,
                                   functioncode=6,
                                   signed=False)

    # -----------------------
    # Calibration helpers
    # -----------------------
    def zero_calibration(self):
        """Perform zero calibration (write 0 to 0x1001)."""
        return self.write_register(registeraddress=self._reg_zero,
                                   value=0,
                                   functioncode=6,
                                   signed=False)

    def slope_calibration(self):
        """Perform slope calibration (write 0 to 0x1003)."""
        return self.write_register(registeraddress=self._reg_slope,
                                   value=0,
                                   functioncode=6,
                                   signed=False)

    def temp_calibration(self, actual_temp_c):
        """
        Temperature calibration: write actual temp * 10 to 0x1000 (per datasheet).
        Example: to set 25.8°C write int(25.8 * 10) = 258
        """
        val = int(round(float(actual_temp_c) * 10.0))
        return self.write_register(registeraddress=self._reg_temp_cal,
                                   value=val,
                                   functioncode=6,
                                   signed=False)

    # -----------------------
    # High-level fetch
    # -----------------------
    def fetch_and_return_data(self):
        """
        Returns a dict with:
          - odo_mg_l (float)
          - temperature_c (float)
          - saturation_pct (float or None if unavailable)
          - plus timestamp and sensor_name
        Strategy:
          Prefer direct reads of 0x0101/0x0100/0x0102.
          If direct reads fail, attempt block read at 0x0000 and parse.
        """
        timestamp = datetime.datetime.now().isoformat()
        try:
            # Try direct reads first
            try:
                odo_raw = self.get_odo_raw()
                temp_raw = self.get_temperature_raw()
                # saturation register sometimes not available in block read; try read but ignore failure
                try:
                    sat_raw = self.get_saturation_raw()
                except Exception:
                    sat_raw = None

            except Exception:
                # fallback: attempt block read and parse according to datasheet layout
                block = self.read_block_0()  # 4 registers
                # datasheet indicates the block layout: measured value, decimal place, temperature value, decimal place
                # The measured value may itself need interpretation (e.g., integer + decimal digits)
                # Here we attempt a simple parse: first reg = value high, second reg = decimal places
                # If the sensor uses more complex packing, adapt parsing accordingly.
                if not block or len(block) < 4:
                    raise RuntimeError("Unable to read ODO/temp from sensor (no data)")

                # simple parse:
                measured_val = block[0]   # integer part
                measured_dec = block[1]   # decimal places (e.g., 2)
                temp_val = block[2]
                temp_dec = block[3]

                # combine measured value with decimal digits
                if measured_dec > 0:
                    odo_raw = measured_val / (10 ** measured_dec)
                    # But datasheet states ODO integer is mg/L * 100; so if decimals field indicates 2, this is consistent
                    # Normalize to raw integer representation (mg/L * 100)
                    odo_raw = int(round(odo_raw * 100))
                else:
                    odo_raw = int(measured_val)

                if temp_dec > 0:
                    temp_raw = temp_val / (10 ** temp_dec)
                    temp_raw = int(round(temp_raw * 10))
                else:
                    temp_raw = int(temp_val)
                sat_raw = None

            # Convert raw values to physical units
            odo_mg_l = round(float(odo_raw) / 100.0, 2)      # raw divided by 100
            temperature_c = round(float(temp_raw) / 10.0, 2) # raw divided by 10
            saturation_pct = round(float(sat_raw) / 10.0, 1) if sat_raw is not None else None

            data = {
                "measurement": "DissolvedOxygen",
                "tags": {"sensor_name": self.sensor_name},
                "fields": {
                    "odo_mg_l": odo_mg_l,
                    "temperature_c": temperature_c,
                    "saturation_pct": saturation_pct
                },
                "time": timestamp
            }
            return data

        except Exception as e:
            return {
                "measurement": "DissolvedOxygen",
                "tags": {"sensor_name": self.sensor_name},
                "fields": {"error": str(e)},
                "time": timestamp
            }

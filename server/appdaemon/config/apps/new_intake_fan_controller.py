import adbase as ad

import time
import serial
import modbus_tk
import modbus_tk.defines as cst
import json
from modbus_tk import modbus_rtu

class new_Intake_fan_controller(ad.ADBase):
    def initialize(self):
        self.adapi = self.get_ad_api()
        self.adapi.log("IntakeFanManualControl initialized...")

        # Setup Modbus
        self.port = "/dev/ttySC0"
        self.master = modbus_rtu.RtuMaster(serial.Serial(
            port=self.port,
            baudrate=9600,
            bytesize=8,
            parity='N',
            stopbits=1,
            xonxoff=0
        ))
        self.master.set_timeout(5.0)
        self.master.set_verbose(True)

        # Output array, only using index 1 for fan
        self.output = [0] * 8

        # Home Assistant input_select entity
        self.fan_mode = self.adapi.get_entity(self.args["fan_mode_id"])
        self.voltage_input = self.adapi.get_entity(self.args["fan_voltage_id"])
        self.manual_mode = self.adapi.get_entity(self.args["fan_manual_toggle_id"])

        # Listen for changes in the entities
        self.fan_mode.listen_state(self.on_mode_change)
        self.voltage_input.listen_state(self.on_mode_change)
        self.manual_mode.listen_state(self.on_mode_change)

        # Set initial mode
        self.set_fan_mode(self.fan_mode.get_state())

    def update_output(self, entity, attr, old, new, kwargs):
        try:
            if self.manual_mode.get_state() == "on":
                voltage = float(self.voltage_input.get_state())
                voltage = max(0.0, min(voltage, 10.0))
                raw_value = int((voltage / 10.0) * 10000)
                self.adapi.log(f"[MANUAL] Setting fan to {voltage:.2f} V → {raw_value}")
            else:
                mode = self.fan_mode.get_state().lower()
                voltage_map = {
                    "off": 0.0,
                    "low": 3.3,
                    "medium": 6.6,
                    "high": 10.0
                }
                voltage = voltage_map.get(mode, 0.0)
                raw_value = int((voltage / 10.0) * 10000)
                self.adapi.log(f"[MODE] Setting fan to '{mode}' → {voltage:.1f} V → {raw_value}")

            self.output[0] = 0
            self.output[1] = raw_value
            self.master.execute(1, cst.WRITE_MULTIPLE_REGISTERS, 0x00, 0x08, output_value=self.output)

        except Exception as e:
            self.adapi.log(f"Error updating fan output: {e}", level="ERROR")
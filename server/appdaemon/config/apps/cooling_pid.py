import appdaemon.plugins.hass.hassapi as hass
import json

class CoolingPID(hass.Hass):
    def initialize(self):
        self.enable_entity = self.args["enable_id"]
        self.humid_sensor = self.args["humid_sensor_id"]
        self.ref_entity = self.args["ref_id"]
        self.kp_entity = self.args["kp_id"]
        self.ki_entity = self.args["ki_id"]
        self.kd_entity = self.args["kd_id"]
        self.fan_topic = self.args["fan_cmd_topic"]
        self.valve_topic = self.args["valve_cmd_topic"]

        self.integral = 0
        self.prev_error = 0
        self.prev_time = self.datetime()

        # Run every 30 seconds to reduce wear on hardware
        self.run_every(self.control_loop, self.datetime(), 30)

    def control_loop(self, kwargs):
        if self.get_state(self.enable_entity) != "on":
            # Turn off actuators if PID disabled
            self.call_service("mqtt/publish", topic=self.fan_topic, payload=json.dumps({"cmd": "adjust", "value": 0}))
            self.call_service("mqtt/publish", topic=self.valve_topic, payload=json.dumps({"cmd": "adjust", "value": 0}))
            return

        try:
            ref = float(self.get_state(self.ref_entity))
            humid = float(self.get_state(self.humid_sensor))

            Kp = float(self.get_state(self.kp_entity))
            Ki = float(self.get_state(self.ki_entity))
            Kd = float(self.get_state(self.kd_entity))

            error = humid - ref
            now = self.datetime()
            dt = (now - self.prev_time).total_seconds()
            self.prev_time = now

            self.integral += error * dt
            derivative = (error - self.prev_error) / dt if dt > 0 else 0
            self.prev_error = error

            control_signal = Kp * error + Ki * self.integral + Kd * derivative
            control_signal = max(0.0, control_signal)  # Clamp to zero minimum

            # Scale to 0-10V for valve and fan (example scaling)
            valve_voltage = min(control_signal, 10.0)
            fan_voltage = valve_voltage  # Simple equal control, adjust if needed

            self.call_service("mqtt/publish", topic=self.fan_topic,
                              payload=json.dumps({"cmd": "adjust", "value": round(fan_voltage, 2)}))
            self.call_service("mqtt/publish", topic=self.valve_topic,
                              payload=json.dumps({"cmd": "adjust", "value": round(valve_voltage, 2)}))

            self.log(f"Cooling PID: ref={ref}%, humid={humid}%, error={error:.2f}, valve={valve_voltage:.2f}V, fan={fan_voltage:.2f}V")

        except Exception as e:
            self.log(f"[Cooling PID ERROR] {e}")

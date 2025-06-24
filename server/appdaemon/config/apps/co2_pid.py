import appdaemon.plugins.hass.hassapi as hass
import json

class CO2PID(hass.Hass):
    def initialize(self):
        self.enable_entity = self.args["co2_pid_enable_id"]
        self.sensor_entity = self.args["co2_sensor_id"]
        self.ref_entity = self.args["co2_ref_id"]
        self.kp_entity = self.args["co2_pid_kp_id"]
        self.ki_entity = self.args["co2_pid_ki_id"]
        self.kd_entity = self.args["co2_pid_kd_id"]
        self.relay_topic = "cmd/solid_state_relay13/req"  # Update if using a different CO₂ relay

        self.integral = 0
        self.prev_error = 0
        self.prev_time = self.datetime()

        self.run_every(self.control_loop, self.datetime(), 10)

    def control_loop(self, kwargs):
        if self.get_state(self.enable_entity) != "on":
            return

        try:
            ref = float(self.get_state(self.ref_entity))
            co2 = float(self.get_state(self.sensor_entity))

            Kp = float(self.get_state(self.kp_entity))
            Ki = float(self.get_state(self.ki_entity))
            Kd = float(self.get_state(self.kd_entity))

            error = ref - co2
            now = self.datetime()
            dt = (now - self.prev_time).total_seconds()
            self.prev_time = now

            self.integral += error * dt
            derivative = (error - self.prev_error) / dt if dt > 0 else 0
            self.prev_error = error

            control_signal = Kp * error + Ki * self.integral + Kd * derivative
            scaled = max(0.0, min(control_signal / 10.0, 1.0))
            on_time = round(scaled * 10, 2)

            payload = {
                "cmd": "on_for",
                "value": on_time
            }

            self.call_service("mqtt/publish", topic=self.relay_topic, payload=json.dumps(payload))
            self.log(f"CO2 PID: ref={ref}, CO2={co2}, error={error:.1f}, Kp={Kp}, Ki={Ki}, Kd={Kd}, ON={on_time}s")

        except Exception as e:
            self.log(f"[CO2 PID ERROR] {e}")

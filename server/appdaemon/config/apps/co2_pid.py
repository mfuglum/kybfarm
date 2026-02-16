import appdaemon.plugins.hass.hassapi as hass

class CO2PID(hass.Hass):

    def initialize(self):
        self.enable_entity = self.args["co2_pid_enable_id"]
        self.sensor_entity = self.args["co2_sensor_id"]
        self.ref_entity = self.args["co2_ref_id"]
        self.kp_entity = self.args["co2_pid_kp_id"]
        self.ki_entity = self.args["co2_pid_ki_id"]
        self.kd_entity = self.args["co2_pid_kd_id"]
        self.relay_entity = self.args["relay_13_id"]

        # PID state
        self.integral = 0.0
        self.prev_error = None # None -> first iteration
        self.prev_time = None
        self.off_timer = None

        # Physical constraint: maximum ON time per 30s cycle
        self.max_on_time = 10.0      # seconds (TPC, Time Proportional Control)

        self.run_every(self.control_loop, self.datetime(), 30)

    def control_loop(self, kwargs):
        if self.get_state(self.enable_entity) != "on":
            self._turn_off_relay()
            return

        try:
            # Read inputs
            ref = float(self.get_state(self.ref_entity))
            co2 = float(self.get_state(self.sensor_entity))

            # PID coefficients (set on HA)
            Kp = float(self.get_state(self.kp_entity))
            Ki = float(self.get_state(self.ki_entity))
            Kd = float(self.get_state(self.kd_entity))

            # PID error
            error = ref - co2

            # Time step calculation
            now = self.datetime()
            if self.prev_time is None:
                dt = 30.0               # assume nominal cycle period
            else:
                dt = (now - self.prev_time).total_seconds()
                if dt <= 0:
                    dt = 30.0
            self.prev_time = now

            # Integral
            self.integral += error * dt

            # Derivative
            if self.prev_error is None:
                derivative = 0.0        # first iteration
            else:
                derivative = (error - self.prev_error) / dt
            self.prev_error = error

            # PID output
            control_signal = Kp * error + Ki * self.integral + Kd * derivative

            # Saturation to 0–1
            scaled = max(0.0, min(control_signal / 1000.0, 1.0))
            # 1000 is an arbitrary “control authority” constant.
            # Adjust based on tuning later.

            # On-time command
            on_time = scaled * self.max_on_time

            if on_time < 0.1:
                self._turn_off_relay()
                self.log(f"[CO2 PID] CO2={co2}, error={error:.1f}, signal={control_signal:.2f}, relay OFF")
            else:
                self._turn_on_relay(on_time)
                self.log(f"[CO2 PID] CO2={co2}, error={error:.1f}, ON for {on_time:.2f}s")

        except Exception as e:
            self.log(f"[CO2 PID ERROR] {e}")

    def _turn_on_relay(self, duration):
        if self.off_timer:
            self.cancel_timer(self.off_timer)
        self.call_service("input_boolean/turn_on", entity_id=self.relay_entity)
        self.off_timer = self.run_in(self._turn_off_relay, duration)

    def _turn_off_relay(self, kwargs=None):
        self.call_service("input_boolean/turn_off", entity_id=self.relay_entity)
        if self.off_timer:
            self.cancel_timer(self.off_timer)
            self.off_timer = None

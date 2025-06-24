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

        self.integral = 0
        self.prev_error = 0
        self.prev_time = self.datetime()
        self.off_timer = None

        self.run_every(self.control_loop, self.datetime(), 30)  # 30s interval per relay spec

    def control_loop(self, kwargs):
        if self.get_state(self.enable_entity) != "on":
            self._turn_off_relay()
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
            scaled = max(0.0, min(control_signal / 0.0, 1.0))
            on_time = round(scaled * 10, 2)

            if on_time < 0.1:
                self._turn_off_relay()
                self.log(f"CO2 PID: ON time too low ({on_time}s), turning relay OFF")
            else:
                self._turn_on_relay(on_time)
                self.log(f"CO2 PID: ref={ref}, CO2={co2}, error={error:.1f}, ON for {on_time}s")

        except Exception as e:
            self.log(f"[CO2 PID ERROR] {e}")

    def _turn_on_relay(self, duration):
        # Cancel any existing off timer
        if self.off_timer:
            self.cancel_timer(self.off_timer)
        # Turn on relay boolean
        self.call_service("input_boolean/turn_on", entity_id=self.relay_entity)
        # Schedule relay turn off after duration seconds
        self.off_timer = self.run_in(self._turn_off_relay, duration)

    def _turn_off_relay(self, kwargs=None):
        self.call_service("input_boolean/turn_off", entity_id=self.relay_entity)
        if self.off_timer:
            self.cancel_timer(self.off_timer)
            self.off_timer = None

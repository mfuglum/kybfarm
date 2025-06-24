import appdaemon.plugins.hass.hassapi as hass

class HeatingPID(hass.Hass):
    def initialize(self):
        self.enable_entity = self.args["enable_id"]
        self.sensor_entity = self.args["sensor_id"]
        self.ref_entity = self.args["ref_id"]
        self.kp_entity = self.args["kp_id"]
        self.ki_entity = self.args["ki_id"]
        self.kd_entity = self.args["kd_id"]
        self.relay_entity = self.args["relay_id"]
        self.pwm_duty_entity = self.args.get("pwm_duty_cycle_id", None)
        self.pwm_period_entity = self.args.get("pwm_base_period_id", None)
        self.pwm_stop_entity = self.args.get("pwm_stop_id", None)

        self.integral = 0
        self.prev_error = 0
        self.prev_time = self.datetime()
        self.off_timer = None

        self.run_every(self.control_loop, self.datetime(), 30)

    def control_loop(self, kwargs):
        if self.get_state(self.enable_entity) != "on":
            self._turn_off_relay()
            return

        try:
            ref = float(self.get_state(self.ref_entity))
            temp = float(self.get_state(self.sensor_entity))

            Kp = float(self.get_state(self.kp_entity))
            Ki = float(self.get_state(self.ki_entity))
            Kd = float(self.get_state(self.kd_entity))

            error = ref - temp
            now = self.datetime()
            dt = (now - self.prev_time).total_seconds()
            self.prev_time = now

            self.integral += error * dt
            derivative = (error - self.prev_error) / dt if dt > 0 else 0
            self.prev_error = error

            control_signal = Kp * error + Ki * self.integral + Kd * derivative
            control_signal = max(0.0, control_signal)  # No negative control

            # Convert control signal to ON time seconds (max 10s)
            on_time = min(control_signal, 10)

            if on_time < 0.1:
                self._turn_off_relay()
                self.log(f"Heating PID: ON time too low ({on_time}s), turning relay OFF")
            else:
                self._turn_on_relay(on_time)
                self.log(f"Heating PID: ref={ref}, temp={temp}, error={error:.2f}, ON for {on_time}s")

            # PWM control if configured
            if self.pwm_duty_entity and self.pwm_period_entity and self.pwm_stop_entity:
                if self.get_state(self.pwm_stop_entity) != "on":
                    duty_cycle = min(max(control_signal / 10.0, 0.0), 1.0)
                    base_period = float(self.get_state(self.pwm_period_entity))
                    self.call_service("input_number/set_value", entity_id=self.pwm_duty_entity, value=duty_cycle)
                    self.call_service("input_number/set_value", entity_id=self.pwm_period_entity, value=base_period)
                else:
                    self.call_service("input_number/set_value", entity_id=self.pwm_duty_entity, value=0.0)

        except Exception as e:
            self.log(f"[Heating PID ERROR] {e}")

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

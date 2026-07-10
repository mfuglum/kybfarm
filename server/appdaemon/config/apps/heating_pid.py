import appdaemon.plugins.hass.hassapi as hass

class HeatingPID(hass.Hass):

    def initialize(self):
        self.enable_entity = self.args["enable_id"]
        self.sensor_entity = self.args["sensor_id"]      # co2voc sensor 2 temperature
        self.ref_entity = self.args["ref_id"]
        self.kp_entity = self.args["kp_id"]
        self.ki_entity = self.args["ki_id"]
        self.kd_entity = self.args["kd_id"]
        self.relay_entity = self.args["relay_id"]

        # PID state
        self.integral = 0.0
        self.prev_error = None
        self.prev_time = None
        self.off_timer = None

        # TPC (Time-Proportional Control) parameters
        self.max_on_time = 45.0      # time in seconds (maximum heater ON time per cycle)
        self.cycle_period = 60.0     # control cycle length

        self.run_every(self.control_loop, self.datetime(), self.cycle_period)

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
            if self.prev_time is None:
                dt = self.cycle_period
            else:
                dt = (now - self.prev_time).total_seconds()
                if dt <= 0:
                    dt = self.cycle_period
            self.prev_time = now

            # integral term (w/ anti-windup)
            self.integral += error * dt

            # reset integrator in case of overshooting
            if error < 0:
                self.integral = 0.0

            # clamp integral to avoid runaway
            self.integral = max(min(self.integral, 500), -500)

            # derivative term
            if self.prev_error is None:
                derivative = 0.0
            else:
                derivative = (error - self.prev_error) / dt
            self.prev_error = error

            # PID output
            control_signal = Kp * error + Ki * self.integral + Kd * derivative

            # Normalize in 0–1 range
            scaled = max(0.0, min(control_signal / 20.0, 1.0))

            # compute ON time for heater
            on_time = scaled * self.max_on_time

            if on_time < 0.1:
                self._turn_off_relay()
                self.log(f"[Heating PID] temp={temp:.2f}, err={error:.2f}, signal={control_signal:.2f}, relay OFF")
            else:
                self._turn_on_relay(on_time)
                self.log(f"[Heating PID] temp={temp:.2f}, err={error:.2f}, ON for {on_time:.2f}s")

        except Exception as e:
            self.log(f"[Heating PID ERROR] {e}")

    def _turn_on_relay(self, duration):

        if self.off_timer is not None:
            try:
                self.cancel_timer(self.off_timer)
            except:
                pass
            self.off_timer = None

        # turn relay ON
        self.call_service("input_boolean/turn_on", entity_id=self.relay_entity)

        # Schedule OFF
        self.off_timer = self.run_in(self._turn_off_relay, duration)

    def _turn_off_relay(self, kwargs=None):
        
        # turn relay OFF
        self.call_service("input_boolean/turn_off", entity_id=self.relay_entity)

        # clear timer
        if self.off_timer is not None:
            try:
                self.cancel_timer(self.off_timer)
            except:
                pass
            self.off_timer = None

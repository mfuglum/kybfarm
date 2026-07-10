import appdaemon.plugins.hass.hassapi as hass


class CO2PID(hass.Hass):


    CYCLE_PERIOD = 30.0
    MAX_ON_TIME = 10.0 # max relay ON-time (one cycle) in seconds
    CONTROL_SCALE = 1000.0
    ON_TIME_THRESHOLD = 0.1 # any value below this, treat as OFF
    INTEGRAL_MAX = 1000.0

    # plausibility windows: outside these it's a fail closed

    CO2_MIN_PLAUSIBLE = 200.0 # below ambient outdoor: likely broken sensor
    CO2_MAX_PLAUSIBLE = 10000.0 # 2x OSHA PEL: likely broken sensor
    REF_MIN_PLAUSIBLE = 200.0
    REF_MAX_PLAUSIBLE = 2000.0 # hard ceiling: never enrich above this!

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
        self.prev_error = None
        self.prev_time = None
        self.off_timer = None

        self._safe_off("init") # start in a known-safe state

        self.run_every(self.control_loop, self.datetime(), self.CYCLE_PERIOD)


    def control_loop(self, kwargs):
        # PID disabled in the UI -> fail closed
        if self.get_state(self.enable_entity) != "on":
            self._safe_off("disabled")
            return

        ref = self._read_float(self.ref_entity, self.REF_MIN_PLAUSIBLE, self.REF_MAX_PLAUSIBLE)
        co2 = self._read_float(self.sensor_entity, self.CO2_MIN_PLAUSIBLE, self.CO2_MAX_PLAUSIBLE)
        if ref is None:
            self._safe_off("invalid setpoint")
            return
        if co2 is None:
            self._safe_off("invalid CO2 reading")
            return

        Kp = self._read_gain(self.kp_entity)
        Ki = self._read_gain(self.ki_entity)
        Kd = self._read_gain(self.kd_entity)
        if Kp is None or Ki is None or Kd is None:
            self._safe_off("invalid PID gain")
            return

        error = ref - co2

        if error <= 0.0:
            self.integral = 0.0
            self.prev_error = None
            self.prev_time = None
            self._safe_off(f"co2={co2:.0f} ppm >= ref={ref:.0f} ppm")
            return

        now = self.datetime()
        if self.prev_time is None:
            dt = self.CYCLE_PERIOD
        else:
            dt = (now - self.prev_time).total_seconds()
            # clock skip / pause / first cycle after re-enable: use nominal
            if dt <= 0 or dt > 10 * self.CYCLE_PERIOD:
                dt = self.CYCLE_PERIOD
        self.prev_time = now

        # Integral with one-sided anti-windup
        self.integral += error * dt
        self.integral = max(0.0, min(self.integral, self.INTEGRAL_MAX))

        if self.prev_error is None:
            derivative = 0.0
        else:
            derivative = (error - self.prev_error) / dt
        self.prev_error = error

        # PID output
        control_signal = Kp * error + Ki * self.integral + Kd * derivative
        scaled = max(0.0, min(control_signal / self.CONTROL_SCALE, 1.0))
        on_time = scaled * self.MAX_ON_TIME

        if on_time < self.ON_TIME_THRESHOLD:
            self._turn_off_relay()
            self.log(
                f"[CO2 PID] co2={co2:.0f} ppm ref={ref:.0f} err={error:.1f} "
                f"I={self.integral:.1f} sig={control_signal:.2f} relay OFF"
            )
        else:
            self._turn_on_relay(on_time)
            self.log(
                f"[CO2 PID] co2={co2:.0f} ppm ref={ref:.0f} err={error:.1f} "
                f"I={self.integral:.1f} sig={control_signal:.2f} ON {on_time:.2f}s"
            )


    def _read_float(self, entity, lo, hi):
        """
         Return a finite float in [lo, hi], or None if the reading is unusable.
        """
        try:
            raw = self.get_state(entity)
        except Exception:
            return None
        if raw is None or raw in ("unknown", "unavailable", ""):
            return None
        try:
            val = float(raw)
        except (TypeError, ValueError):
            return None
        # NaN / inf
        if val != val or val == float("inf") or val == float("-inf"):
            return None
        if val < lo or val > hi:
            return None
        return val

    def _read_gain(self, entity):
        """Return a finite non-negative float, or None."""
        try:
            raw = self.get_state(entity)
        except Exception:
            return None
        if raw is None or raw in ("unknown", "unavailable", ""):
            return None
        try:
            val = float(raw)
        except (TypeError, ValueError):
            return None
        if val != val or val == float("inf") or val == float("-inf"):
            return None
        if val < 0.0:
            return None
        return val

    def _safe_off(self, reason):
        """
         force relay OFF, cancel any pending on-timer, clear PID state
        """
        self.integral = 0.0
        self.prev_error = None
        self.prev_time = None
        try:
            self._turn_off_relay()
        except Exception as e:
            self.log(f"[CO2 PID] _safe_off relay error: {e}")
        self.log(f"[CO2 PID] safe OFF ({reason})")

    def _turn_on_relay(self, duration):
        if self.off_timer is not None:
            try:
                self.cancel_timer(self.off_timer)
            except Exception:
                pass
            self.off_timer = None

        # Hard upper bound on commanded duration
        try:
            duration = float(duration)
        except (TypeError, ValueError):
            duration = 0.0
        duration = max(0.0, min(duration, self.MAX_ON_TIME))

        self.call_service("input_boolean/turn_on", entity_id=self.relay_entity)
        # if the loop dies before the next cycle, this still fires
        self.off_timer = self.run_in(self._turn_off_relay, duration)

    def _turn_off_relay(self, kwargs=None):
        try:
            self.call_service("input_boolean/turn_off", entity_id=self.relay_entity)
        finally:
            if self.off_timer is not None:
                try:
                    self.cancel_timer(self.off_timer)
                except Exception:
                    pass
                self.off_timer = None

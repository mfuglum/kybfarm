import appdaemon.plugins.hass.hassapi as hass
import json


class CoolingPID(hass.Hass):


    CYCLE_PERIOD = 30.0
    OUTPUT_MAX = 10.0 # 0–10 V range for fan/valve
    INTEGRAL_MAX = 50.0 # anti-windup cap (units: %·s)

    def initialize(self):
        self.enable_entity = self.args["enable_id"]
        self.humid_sensor = self.args["humid_sensor_id"]
        self.ref_entity = self.args["ref_id"]
        self.kp_entity = self.args["kp_id"]
        self.ki_entity = self.args["ki_id"]
        self.kd_entity = self.args["kd_id"]
        self.fan_topic = self.args["fan_cmd_topic"]
        self.valve_topic = self.args["valve_cmd_topic"]

        self.integral = 0.0
        self.prev_error = None
        self.prev_time = None

        # start with actuators commanded to 0 (known-safe)
        self._publish_outputs(0.0, 0.0)

        self.run_every(self.control_loop, self.datetime(), self.CYCLE_PERIOD)

    def control_loop(self, kwargs):
        if self.get_state(self.enable_entity) != "on":
            self._safe_off("disabled")
            return

        ref = self._read_float(self.ref_entity)
        humid = self._read_float(self.humid_sensor)
        if ref is None or humid is None:
            self._safe_off("invalid sensor/setpoint")
            return

        Kp = self._read_gain(self.kp_entity)
        Ki = self._read_gain(self.ki_entity)
        Kd = self._read_gain(self.kd_entity)
        if Kp is None or Ki is None or Kd is None:
            self._safe_off("invalid PID gain")
            return

        try:
            error = humid - ref

            now = self.datetime()
            if self.prev_time is None:
                dt = self.CYCLE_PERIOD
            else:
                dt = (now - self.prev_time).total_seconds()
                if dt <= 0 or dt > 10 * self.CYCLE_PERIOD:
                    dt = self.CYCLE_PERIOD
            self.prev_time = now

            # integral with one-sided anti-windup, reset on overshoot
            self.integral += error * dt
            if error < 0:
                self.integral = 0.0
            self.integral = max(0.0, min(self.integral, self.INTEGRAL_MAX))

            if self.prev_error is None:
                derivative = 0.0
            else:
                derivative = (error - self.prev_error) / dt
            self.prev_error = error

            control_signal = Kp * error + Ki * self.integral + Kd * derivative
            output = max(0.0, min(control_signal, self.OUTPUT_MAX))

            self._publish_outputs(output, output)
            self.log(
                f"[Cooling PID] ref={ref:.1f}% humid={humid:.1f}% err={error:.2f} "
                f"I={self.integral:.2f} out={output:.2f}V"
            )

        except Exception as e:
            self._safe_off(f"exception: {e}")

    def _read_float(self, entity):
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
        return val

    def _read_gain(self, entity):
        val = self._read_float(entity)
        if val is None or val < 0.0:
            return None
        return val

    def _safe_off(self, reason):
        self.integral = 0.0
        self.prev_error = None
        self.prev_time = None
        try:
            self._publish_outputs(0.0, 0.0)
        except Exception as e:
            self.log(f"[Cooling PID] _safe_off publish error: {e}")
        self.log(f"[Cooling PID] safe OFF ({reason})")

    def _publish_outputs(self, fan_v, valve_v):
        fan_v = max(0.0, min(float(fan_v), self.OUTPUT_MAX))
        valve_v = max(0.0, min(float(valve_v), self.OUTPUT_MAX))
        self.call_service(
            "mqtt/publish",
            topic=self.fan_topic,
            payload=json.dumps({"cmd": "adjust", "value": round(fan_v, 2)}),
        )
        self.call_service(
            "mqtt/publish",
            topic=self.valve_topic,
            payload=json.dumps({"cmd": "adjust", "value": round(valve_v, 2)}),
        )

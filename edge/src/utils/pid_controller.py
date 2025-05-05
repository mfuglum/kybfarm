import time

# ---------------------------------------
# PID Controller-klasse
# ---------------------------------------

class PIDController():
    def __init__(self, Kp: float, Ki: float, Kd: float, mode: str = "cooling", max_integral: float = 10, min_integral: float = -10):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.mode = mode
        self.max_integral = max_integral
        self.min_integral = min_integral

        self.previous_time = None
        self.previous_error = 0
        self.integral = 0

    def calculate_control_signal(self, setpoint: float, input_value: float) -> float:
        # Merk: positivt signal når input_value > setpoint (for avfukting)
        error = input_value - setpoint
        if self.mode == "cooling":
            error = input_value - setpoint
        elif self.mode == "heating":
            error = setpoint - input_value
        else:
            raise ValueError("Invalid mode. Use 'cooling' or 'heating'.")
        current_time = time.time()

        if self.previous_time is None:
            derivative = 0
        else:
            delta_time = current_time - self.previous_time
            delta_error = error - self.previous_error
            derivative = delta_error / delta_time if delta_time > 0 else 0
            self.integral += error * delta_time
            self.integral = max(min(self.integral, self.max_integral), self.min_integral)

        control_signal = (self.Kp * error) + (self.Ki * self.integral) + (self.Kd * derivative)

        self.previous_time = current_time
        self.previous_error = error

        # Returner aldri negativt signal
        return max(0.0, control_signal)
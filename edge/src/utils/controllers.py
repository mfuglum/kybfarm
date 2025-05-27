import time

class PController():
    """A Proportional (P) controller."""

    def __init__(self, Kp: float):
        """
        Initializes the P controller with specified gain.

        Parameters:
            Kp: The proportional gain.
        """
        self.Kp = Kp

    def calculate_control_signal(self, setpoint: float, input_value: float) -> float:
        """
        Calculates the control output value based on the setpoint and current input value.

        Parameters:
            setpoint: The desired target value.
            input_value: The current value of the input.

        Returns:
            control_signal: The output value from the P controller.
        """
        error = setpoint - input_value
        print("error:", error)
        control_signal = (self.Kp * error)
        return control_signal


class PIController():
    """A Proportional-Integral (PI) controller."""

    def __init__(self, Kp: float, Ki: float, max_integral: float = 10, min_integral: float = -10):
        """
        Initializes the PI controller with specified gains and integral windup limits.

        Parameters:
            Kp: The proportional gain.
            Ki: The integral gain.
            max_integral: Upper limit for integral windup.
            min_integral: Lower limit for integral windup.
        """
        self.Kp = Kp
        self.Ki = Ki
        self.max_integral = max_integral
        self.min_integral = min_integral

        # Initialize internal states
        self.previous_time = None  # Indicates first call of calculate_control_signal()
        self.integral = 0

    def calculate_control_signal(self, setpoint: float, input_value: float) -> float:
        """
        Calculates the control output value based on the setpoint and current input value.

        Parameters:
            setpoint: The desired target value.
            input_value: The current value of the input.

        Returns:
            control_signal: The output value from the PI controller.
        """
        error = setpoint - input_value
        current_time = time.time()

        if self.previous_time is None:
            # Skip integral term on the first call due to no time having passed.
            derivative = 0
        else:
            delta_time = current_time - self.previous_time
            self.integral += error * delta_time
            # Anti-windup: Clamp the integral term
            self.integral = max(min(self.integral, self.max_integral), self.min_integral)

        control_signal = (self.Kp * error) + (self.Ki * self.integral) 

        # Update for next calculation
        self.previous_time = current_time
        self.previous_error = error
        print("integral before cutoff:", self.integral)
        print("Eror:", error)
        print("Kp:", self.Kp)
        print("Ki:", self.Ki)
        print("Contribution Kp:", self.Kp * error)
        print("Contribution Ki:", self.Ki * self.integral)
        print("Total control signal:", control_signal)

        return control_signal


class PDController():
    """A Proportional-Derivative (PD) controller."""

    def __init__(self, Kp: float, Kd: float):
        """
        Initializes the PD controller with specified gains.

        Parameters:
            Kp: The proportional gain.
            Kd: The derivative gain.
        """
        self.Kp = Kp
        self.Kd = Kd

        # Initialize internal states
        self.previous_time = None
        self.previous_error = 0

    def calculate_control_signal(self, setpoint: float, input_value: float) -> float:
        """
        Calculates the control output value based on the setpoint and current input value.

        Parameters:
            setpoint: The desired target value.
            input_value: The current value of the input.

        Returns:
            control_signal: The output value from the PD controller.
        """
        error = setpoint - input_value
        current_time = time.time()

        if self.previous_time is None:
            # Skip derivative term on the first call due to no time having passed.
            derivative = 0
        else:
            delta_time = current_time - self.previous_time
            delta_error = error - self.previous_error
            derivative = delta_error / delta_time if delta_time > 0 else 0

        control_signal = (self.Kp * error) + (self.Kd * derivative)

        # Update for next calculation
        self.previous_time = current_time
        self.previous_error = error

        return control_signal


class PIDController():
    """
    A Proportional-Integral-Derivative (PID) controller with selectable mode for cooling or heating.

    Attributes:
        Kp: Proportional gain.
        Ki: Integral gain.
        Kd: Derivative gain.
        mode: "cooling" or "heating" (affects error sign).
        max_integral: Upper limit for integral windup.
        min_integral: Lower limit for integral windup.
    """

    def __init__(self, Kp: float, Ki: float, Kd: float, mode: str = "cooling", max_integral: float = 10, min_integral: float = -10):
        """
        Initializes the PID controller with specified gains, mode, and integral windup limits.

        Parameters:
            Kp: The proportional gain.
            Ki: The integral gain.
            Kd: The derivative gain.
            mode: "cooling" or "heating" (determines error sign).
            max_integral: Upper limit for integral windup.
            min_integral: Lower limit for integral windup.
        """
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
        """
        Calculates the control output value based on the setpoint and current input value.

        For "cooling" mode, error = input_value - setpoint (positive signal when input > setpoint).
        For "heating" mode, error = setpoint - input_value (positive signal when input < setpoint).

        Parameters:
            setpoint: The desired target value.
            input_value: The current value of the input.

        Returns:
            control_signal: The output value from the PID controller (never negative).
        """
        print("Mode:", self.mode)
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
            # Anti-windup: Clamp the integral term
            self.integral = max(min(self.integral, self.max_integral), self.min_integral)

        control_signal = (self.Kp * error) + (self.Ki * self.integral) + (self.Kd * derivative)
        print("Eror:", error)
        print("Contribution Kp:", self.Kp * error)
        print("Contribution Ki:", self.Ki * self.integral)
        print("Contribution Kd:", self.Kd * derivative * (-1))
        print("Total control signal:", control_signal)

        self.previous_time = current_time
        self.previous_error = error

        # Never return a negative signal
        return max(0.0, control_signal)
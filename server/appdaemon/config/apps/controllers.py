import time

class PController():
    """A Proportional (P) controller."""

    def __init__(self, Kp: float):
        """
        Initializes the P controller with specified gains

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
        # Initialize calculation parameters
        error = setpoint - input_value

        # P calculations
        control_signal = (self.Kp * error)

        return control_signal
    
class PDController():
    """A Proportional-Derivative (PD) controller."""

    def __init__(self, Kp: float, Kd: float):
        """
        Initializes the PD controller with specified gains

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
        # Initialize calculation parameters
        error = setpoint - input_value
        current_time = time.time()

        # Check if it is the first call
        if self.previous_time is None:
            # Skip derivative term on the first call due to no time having passed.
            derivative = 0
        else:
            # PD calculations
            delta_time = current_time - self.previous_time
            delta_error = error - self.previous_error
            derivative = delta_error / delta_time if delta_time > 0 else 0

        # Calculate output value
        control_signal = (self.Kp * error) + (self.Kd * derivative)

        # Update for next calculation
        self.previous_time = current_time
        self.previous_error = error

        return control_signal

class PIDController():
    """A Proportional-Integral-Derivative (PID) controller."""

    def __init__(self, Kp: float, Ki: float, Kd: float, max_integral: float = 10, min_integral: float = -10):
        """
        Initializes the PID controller with specified gains

        Parameters:
            Kp: The proportional gain.
            Ki: The integral gain.
            Kd: The derivative gain.
            max_integral: Upper limit for integral windup.
            min_integral: Lower limit for integral windup.
        """
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.max_integral = max_integral
        self.min_integral = min_integral

        # Initialize internal states
        self.previous_time = None  # Initialize as None to indicate first call of calculate_control_signal()
        self.previous_error = 0
        self.integral = 0

    def calculate_control_signal(self, setpoint: float, input_value: float) -> float:
        """
        Calculates the control output value based on the setpoint and current input value.

        Parameters:
            setpoint: The desired target value.
            input_value: The current value of the input.

        Returns:
            control_signal: The output value from the PID controller.
        """
        # Initialize calculation parameters
        error = setpoint - input_value
        current_time = time.time()

        # Check if it is the first call
        if self.previous_time is None:
            # Skip derivative and integral term on the first call due to no time having passed.
            derivative = 0
        else:
            # PID calculations
            delta_time = current_time - self.previous_time
            delta_error = error - self.previous_error
            derivative = delta_error / delta_time if delta_time > 0 else 0
            self.integral += error * delta_time
            self.integral = max(min(self.integral, self.max_integral), self.min_integral)  # Anti-Windup

        # Calculate output value
        control_signal = (self.Kp * error) + (self.Ki * self.integral) + (self.Kd * derivative)

        # Update for next calculation
        self.previous_time = current_time
        self.previous_error = error

        return control_signal

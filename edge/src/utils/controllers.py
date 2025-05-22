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
        error =  setpoint - input_value
        print("error:", error)
        # P calculations
        control_signal = (self.Kp * error)

        return control_signal


class PIController():
    """A Proportional-Integral (PI) controller."""

    def __init__(self, Kp: float, Ki: float, max_integral: float = 10, min_integral: float = -10):
        """
        Initializes the PID controller with specified gains

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
        self.previous_time = None  # Initialize as None to indicate first call of calculate_control_signal()
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

        # Initialize calculation parameters
        error = setpoint - input_value
        current_time = time.time()

        if self.previous_time is None:
            # Skip derivative and integral term on the first call due to no time having passed.
            derivative = 0
        else:
            # PID calculations
            delta_time = current_time - self.previous_time
            self.integral += error * delta_time
            self.integral = max(min(self.integral, self.max_integral), self.min_integral)  # Anti-Windup

        # Calculate output value
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




# ---------------------------------------
# PID Controller-class
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
            self.integral = max(min(self.integral, self.max_integral), self.min_integral)

        control_signal = (self.Kp * error) + (self.Ki * self.integral) + (self.Kd * derivative)
        print("Eror:", error)
        print("Contribution Kp:", self.Kp * error)
        print("Contribution Ki:", self.Ki * self.integral)
        print("Contribution Kd:", self.Kd * derivative * (-1))
        print("Total control signal:", control_signal)

        self.previous_time = current_time
        self.previous_error = error

        # Returner aldri negativt signal
        return max(0.0, control_signal)
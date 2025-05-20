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
class HeatPumpSimulator:
    """A simulated heat pump with specified operational efficiency."""

    def __init__(self, efficiency=1.0, min_output=0, max_output=100):
        """
        Initializes the heat pump simulator.

        Parameters:
            efficiency: The operational efficiency of the heat pump.
            min_output: The minimum heat output of the heat pump.
            max_output: The maximum heat output of the heat pump.
        """
        self.efficiency = efficiency
        self.min_output = min_output
        self.max_output = max_output

    def get_heat_output(self, control_signal):
        """
        Calculates the heat output based on the control signal and the pump's efficiency.

        Parameters:
            control_signal: The control signal from the PID controller.

        Returns:
            heat_output: The amount of heat added to the environment (in degrees per update).
        """
        heat_output = max(min(control_signal * self.efficiency, self.max_output), self.min_output)
        return heat_output

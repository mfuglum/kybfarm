import time, math

class AmbientTemperatureSimulator():
    """A simulated ambient temperature representing the outside weather temperature."""

    def __init__(self, temp_average: float=14, temp_variation:float=4, cycle_period: str="day"):
        """
        Initializes the ambient temperature simulator.

        Parameters:
            temp_average: The average temperature in a cycle.
            temp_variation: The temperature amplitude.
            temp_cycle: The amount of time to complete a cycle. Valid options are "minute", "hour" and "day".
        """
        self.temp_average = temp_average
        self.temp_variation = temp_variation
        self.cycle_period = cycle_period

    def get_ambient_temperature(self):
        """
        Gets the current ambient temperature based on the time of day.

        Returns:
            current_ambient_temp: The current ambient temperature.
        """
        # Determine the number of seconds in a cycle based on the specified cycle period
        if self.cycle_period == "minute":
            cycle_time = 60
        elif self.cycle_period == "hour":
            cycle_time = 60*60
        elif self.cycle_period == "day":
            cycle_time = 60*60*24

        current_ambient_temp = self.temp_average + self.temp_variation*math.cos(2*math.pi*time.time()/cycle_time)
        return current_ambient_temp

import random

class TemperatureSensorSimulator:
    """A simulated temperature sensor with specified measurement noise."""

    def __init__(self, noise_level=0.5):
        """
        Initializes the temperature sensor with a specified noise level.

        Parameters:
            noise_level: The maximum deviation due to noise.
        """
        self.noise_level = noise_level

    def read_temperature(self, actual_temperature):
        """
        Simulates reading the temperature by adding a random noise to the actual temperature.

        Parameters:
            actual_temperature: The true temperature of the environment.

        Returns:
            temperature_reading: The noisy temperature reading.
        """
        # Add noise to the temperature reading to simulate an imperfect sensor
        noise = random.uniform(-self.noise_level, self.noise_level)
        temperature_reading = actual_temperature + noise
        return temperature_reading

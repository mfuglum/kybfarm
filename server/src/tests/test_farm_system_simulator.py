import time
from simulators.temperature_sensor_simulator import TemperatureSensorSimulator
from simulators.heat_pump_simulator import HeatPumpSimulator
from simulators.ambient_temperature_simulator import AmbientTemperatureSimulator
from utils.controllers import PIDController

class FarmSystemSimulator:
    """A simulated farm system involving the climate variables within the farm, as well as the sensor and actuator devices interacting with the climate."""

    def __init__(self, initial_temp=20.0, target_temp=22.0, dt=1):
        """
        Initializes the farm system simulator.

        Parameters:
            initial_temp: The starting temperature within the farm.
            target_temp: The favored temperature within the farm.
            dt: The time interval between each simulation update.
        """
        self.current_temp = initial_temp
        self.target_temp = target_temp
        self.dt = dt
        self.heat_pump = HeatPumpSimulator(efficiency=1.0)
        self.pid_controller = PIDController(Kp=0.8, Ki=0.1, Kd=0.05)
        self.temperature_sensor = TemperatureSensorSimulator(noise_level=0.5)
        self.ambient_temperature = AmbientTemperatureSimulator(temp_average=14, temp_variation=4, cycle_period="minute")

    def update(self):
        """
        One iteration of the farm climate and the output of all its devices being updated.
        """
        # Update ambient temperature based on weather cycle
        ambient_temp = self.ambient_temperature.get_ambient_temperature()
        heat_change_from_ambient_temp = 0.2*(ambient_temp - self.current_temp)*self.dt

        # Update room temperature based on heat gained or lost from ambient temperature
        self.current_temp += heat_change_from_ambient_temp

        # Use the sensor to read current room temperature
        sensor_reading = self.temperature_sensor.read_temperature(self.current_temp)

        # Use sensor reading as controller input variable
        heat_pump_control_signal = self.pid_controller.calculate_control_signal(self.target_temp, sensor_reading)

        # Use control signal to determine heat pump output
        heat_change_from_heat_pump = self.heat_pump.get_heat_output(heat_pump_control_signal)
        
        # Update room temperature based on heat added from heat pump
        self.current_temp += heat_change_from_heat_pump
        
        print(f"Ambient temperature: {ambient_temp:.2f}°C, Sensor Reading: {sensor_reading:.2f}°C, Resulting room temperature: {self.current_temp:.2f}°C, Error: {self.current_temp-self.target_temp:.2f}°C")
        
    def simulate(self):
        """
        Update the simulated farm system every second indefinetely until manually stopped.
        """
        try:
            while True:
                self.update()
                time.sleep(self.dt)
        except KeyboardInterrupt:
            print("Simulation stopped.")

if __name__ == "__main__":
    simulator = FarmSystemSimulator(initial_temp=15.0, target_temp=22.0, dt=0.1)
    simulator.simulate()

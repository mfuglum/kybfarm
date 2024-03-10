import time
from server.src.utils.controllers import PIDController

# Simulation parameters
setpoint = 100.0  # Target temperature to maintain
initial_temperature = 20.0  # Starting temperature of the system
system_temperature = initial_temperature

# PID Controller Configuration
Kp = 0.6
Ki = 0.01
Kd = 0.005
pid_controller = PIDController(Kp, Ki, Kd)

# Simulation function to mimic applying output to the system and getting the system's response
def simulate_system(control_signal):
    global system_temperature
    # Simple model: system temperature changes proportionally to the control signal
    system_temperature += control_signal * 0.1
    return system_temperature

# Test loop
for _ in range(100):  # Run for 100 iterations
    # PID controller calculates the control signal
    control_signal = pid_controller.calculate_control_signal(setpoint, system_temperature)
    
    # Simulate applying the control signal to the system and getting the new temperature
    new_temperature = simulate_system(control_signal)
    
    # Print the results to observe how the temperature changes over time
    print(f"Control Signal: {control_signal:.2f}, New Temperature: {new_temperature:.2f}")
    
    # Wait a bit before the next iteration to simulate time passing
    time.sleep(0.1)

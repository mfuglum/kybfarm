import time
from utils.controllers import PIDController

# Simuleringsparametere
setpoint = 60.0  # Ønsket luftfuktighet i %
humidity = 80.0  # Startverdi
external_humidity_increase = 0.05  # Simulerer naturlig fuktighetstilførsel

# PID-innstillinger
Kp = 3.0
Ki = 0.1
Kd = 0.05
pid = PIDController(Kp, Ki, Kd)

# Simuleringsfunksjon
def simulate_dehumidification(control_signal):
    global humidity
    # Fuktighet synker proporsjonalt med styring (maks -0.5 % per steg)
    humidity -= control_signal * 0.005
    # Naturlig fuktighetstilførsel (systemlekkasje eller planter)
    humidity += external_humidity_increase
    # Begrens innen 0–100 %
    humidity = max(0.0, min(100.0, humidity))
    return humidity

# Simuleringsløkke
for i in range(100):
    control_signal = pid.calculate_control_signal(setpoint, humidity)
    new_humidity = simulate_dehumidification(control_signal)

    print(f"[{i}] Output: {control_signal:.2f}, Humidity: {new_humidity:.2f}%")
    time.sleep(0.1)

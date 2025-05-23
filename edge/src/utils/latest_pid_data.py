# Dictionaries for storing the latest sensor readings and reference values
# Used for sharing state between control loops and MQTT callbacks

latest_humidity_data = {
    "REF_HUMID": None,   # Reference humidity setpoint
    "STH01_1": None,     # Humidity sensor 1 reading
    "STH01_2": None,     # Humidity sensor 2 reading
}

latest_heating_data = {
    "REF_TEMP": None,    # Reference temperature setpoint
    "STH01_1": None,     # Temperature sensor 1 reading
    "STH01_2": None,     # Temperature sensor 2 reading
    "CO2_VOC_1": None,   # Additional temperature/CO2 sensor reading
}

latest_CO2_data = {
    "REF_CO2": None,     # Reference CO2 setpoint
    "CO2_VOC_1": None,   # CO2 sensor 1 reading
    "CO2_VOC_2": None,   # CO2 sensor 2 reading
}

# PID parameter sets for cooling control, keyed by reference humidity
cooling_pid_settings = {
    60: {"Kp": 0.5, "Ki": 0.01, "Kd": 0.2},
    65: {"Kp": 0.3, "Ki": 0.03, "Kd": 0.2},
}

# PI parameter sets for CO2 control, keyed by reference CO2 value
CO2_pi_settings = {
    1000: {"Kp": 0.2, "Ki": 0.03},
    800:  {"Kp": 0.13, "Ki": 0.02},
    600:  {"Kp": 0.1, "Ki": 0.01},
}
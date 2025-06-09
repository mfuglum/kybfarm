latest_humidity_data = {
    "REF_HUMID": None,
    "STH01_1": None,
    "STH01_2": None,
    }

latest_heating_data = {
    "REF_TEMP": None,
    "STH01_1": None,
    "STH01_2": None,
    "CO2_VOC_1": None,
}

latest_CO2_data = {
    "REF_CO2": None,
    "CO2_VOC_1": None,
    "CO2_VOC_2": None,
}

cooling_pid_settings = {
    60: {"Kp": 0.5, "Ki": 0.03, "Kd": 0.25},
    65: {"Kp": 0.2, "Ki": 0.05, "Kd": 0.25},
}

"""""
cooling_pid_settings = {
    60: {"Kp": 0.5, "Ki": 0.01, "Kd": 0.1},
    65: {"Kp": 0.3, "Ki": 0.03, "Kd": 0.1},
}
"""""

CO2_pi_settings = {
    1000:  {"Kp": 0.2, "Ki": 0.03},
    800: {"Kp": 0.13, "Ki": 0.02},
    600: {"Kp": 0.1, "Ki": 0.01},
}

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
    60: {"Kp": 0.5, "Ki": 0.01, "Kd": 0.1,},
    65: {"Kp": 0.3, "Ki": 0.03, "Kd": 0.1},
}
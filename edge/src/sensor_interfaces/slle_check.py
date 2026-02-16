from sensor_SLLE01_modbus import SLLE01

s = SLLE01(debug=False)
print("unit:", s.get_unit_code())
print("dp:", s.get_decimal_points())
print("raw:", s.get_measurement_value())
print("level_cm:", s.get_level_cm())

from sensor_SLLE01_modbus import SLLE01

print("Creating sensor instance...")
sensor = SLLE01(debug=True)

print("Reading unit code...")
print("Unit code:", sensor.get_unit_code())

print("Reading raw measurement...")
value = sensor.get_measurement_value()
print("Raw value:", value)

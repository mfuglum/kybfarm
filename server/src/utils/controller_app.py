"""
WORK IN PROGRESS

This is a general control app meant for inheriting custom control modules.
Its purpose is to abstract the interaction with InfluxDB and AppDaemon
"""

import os
import appdaemon.plugins.hass.hassapi as hass
from server.src.utils.influxdb_handler import InfluxDBHandler
from server.src.utils.controllers import PIDController

class PIDControllerApp(hass.Hass):
    def initialize(self):
        self.log("Initializing PID Controller App...")
        # Initialize your app. Get entity IDs from the app configuration and set up intervals
        self.sensor = self.args["sensor"]
        self.actuator = self.args["actuator"]
        self.setpoint = float(self.args["setpoint"])
        self.Kp = float(self.args["Kp"])
        self.Ki = float(self.args["Ki"])
        self.Kd = float(self.args["Kd"])

        # Initialize InfluxDBHandler with correct user details
        self.db_handler = InfluxDBHandler(
            bucket = os.getenv("DOCKER_INFLUXDB_INIT_BUCKET"),
            org = os.getenv("DOCKER_INFLUXDB_INIT_ORG"),
            token = os.getenv("DOCKER_INFLUXDB_INIT_ADMIN_TOKEN"),
            url = "http://localhost:8086"
        )

        # Initialize PID Controller
        self.pid = PIDController(Kp=self.Kp, Ki=self.Ki, Kd=self.Kd)

        # Listen for state changes on the sensor
        self.listen_state(self.on_sensor_change, self.sensor)

    def on_sensor_change(self, kwargs):
        """Called when the sensor state changes"""
        # Fetch latest data from InfluxDB
        query_measurement = "test_measurement"
        query_field = "temperature"
        query_tags = {"location": "middle_shelf"}
        query_start = "-10m"
        data = self.db_handler.query_from_database(
            measurement=query_measurement,
            field=query_field,
            tags=query_tags,
            start=query_start
        )
        previous_value = data[0].records[0].get_value() # NOTICE: Should you make this complex syntax in the influxdb_handler module instead?

        # Compute PID output
        control_signal = self.pid.calculate_output_value(self.setpoint, previous_value)

        # Update the actuator (placeholder)
        self.call_service("climate/set_temperature", entity_id=self.actuator, temperature=control_signal)

        self.log(f"Adjusted climate control based on PID output: {control_signal}")

    def terminate(self):
        # Clean up if needed when the app is stopped
        pass

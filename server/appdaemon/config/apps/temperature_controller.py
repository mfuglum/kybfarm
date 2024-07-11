import appdaemon.plugins.hass.hassapi as hass
from controllers import PIDController
from influxdb_handler import InfluxDBHandler
import json
import os

class TemperatureController(hass.Hass):
    def initialize(self):
        """Initialize the app."""
        self.log("Fetching app arguments...")
        # Get entity IDs and parameters from the app configuration.
        self.sensor = self.args["sensor"]
        # self.actuator = self.args["actuator"]  # Not implemented
        self.controller_on = bool(self.args["controller_on"])
        self.setpoint = float(self.args["setpoint"])
        self.sample_time = float(self.args["sample_time"])
        self.Kp = float(self.args["Kp"])
        self.Ki = float(self.args["Ki"])
        self.Kd = float(self.args["Kd"])

        # Initialize PIDController with specified parameters.
        self.log("Initializing PID controller...")
        self.pid = PIDController(
            Kp=self.Kp,
            Ki=self.Ki,
            Kd=self.Kd
            )

        # Initialize InfluxDBHandler with correct user details and query parameters.
        self.log("Establishing connection with InfluxDB...")
        self.db_handler = InfluxDBHandler(
            bucket = os.getenv("DOCKER_INFLUXDB_INIT_BUCKET"),
            org = os.getenv("DOCKER_INFLUXDB_INIT_ORG"),
            token = os.getenv("DOCKER_INFLUXDB_INIT_ADMIN_TOKEN"),
            url = os.getenv("INFLUXDB_CONTAINER_URL")
            )
        self.query_measurement = "°C"
        self.query_field = "value"
        self.query_tags = {"entity_id": self.sensor}

        # Initialize scheduler to run update function once every sample time, starting now.
        self.log(f"Initializing scheduler callback every {self.sample_time} seconds...")
        self.run_every(self.update, "now", self.sample_time)
        self.log("App initialization complete")

    def update(self, kwargs):
        """Called once every sample time"""
        # Get latest data from InfluxDB as input.
        tables = self.db_handler.query_latest_from_database(
            measurement=self.query_measurement,
            field=self.query_field,
            tags=self.query_tags,
            )
        input = tables[0].records[0].get_value()
        self.log(f"Value from InfluxDB: {input}")

        # Calculate PID controller output.
        if self.controller_on:
            output = self.pid.calculate_control_signal(
                self.setpoint,
                input
                )
        else:
            output = 0
        self.log(f"Controller output: {output}")

        # Update the actuator.
        message = {"control_signal": output}
        self.call_service(
            service="mqtt/publish",
            topic=os.getenv("HEAT_PUMP_SIMULATOR_01_TEMPERATURE_COMMAND_TOPIC"),
            payload=json.dumps(message),
            )

    def terminate(self):
        """Clean up when the app is stopped."""
        self.log("Closing connection with InfluxDB...")
        self.db_handler.close()
        self.log("App termination complete")

import time, math  # For the simulation functionality
import signal, sys  # For graceful shutdown of the process
import json  # For MQTT messages
import paho.mqtt.client as mqtt

class VFFSimulator:
    """A simulated VFF involving the climate variables within the farm, as well as the sensor and actuator devices interacting with the climate."""

    def __init__(self,
                 broker_hostname: str,
                 port: int,
                 subscribe_topic: str,
                 publish_topic: str,
                 dt: float=0.1,
                 ambient_temp_avg: float=14,
                 ambient_temp_var: float=4,
                 ambient_temp_cycle: str="day"):
        """
        Initializes the VFF simulator.

        Parameters:
            broker_hostname:
            port:
            subscribe_topic:
            publish_topic:
            dt:
            ambient_temp_avg:
            ambient_temp_var:
            ambient_temp_cycle:
        """
        # Process shutdown signal handler.
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        # Simulation configurations.
        self.dt = dt
        self.ambient_temp_avg = ambient_temp_avg
        self.ambient_temp_var = ambient_temp_var
        self.ambient_temp_cycle = ambient_temp_cycle
        # Initial temperature in the farm is the same as the ambient temperature.
        self.current_temp = self.get_ambient_temperature(
            ambient_temp_average=self.ambient_temp_avg,
            ambient_temp_variation=self.ambient_temp_var,
            ambient_temp_cycle=self.ambient_temp_cycle
        )
        self.heat_from_actuators = 0  # Default value

        # MQTT configurations.
        self.subscribe_topic = subscribe_topic
        self.publish_topic = publish_topic
        self.client = mqtt.Client("VFFSimulator")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        try:
            self.client.connect(broker_hostname, port)  # Connect to the Broker
        except Exception as e:
            print(f"Failed to connect to MQTT Broker at {broker_hostname}:{port}, error: {e}")
        self.client.loop_start()  # Start the loop

    def signal_handler(self):
        """
        Signal handler for gracefully shutting down the process.
        """
        print("Signal received, shutting down...")
        self.client.loop_stop()  # Stop the loop
        self.client.disconnect()  # Disconnect from the Broker
        sys.exit(0)

    def on_connect(self, client, userdata, flags, return_code):
        """
        Informs if connection to MQTT Broker is successful or not, and begins subscribing to subscribe_topic if it is.
        """
        if return_code == 0:
            print("Connected to MQTT Broker.")
            client.subscribe(self.subscribe_topic)
        else:
            print(f"Failed to connect to MQTT Broker, return code: {return_code}")

    def on_message(self, client, userdata, msg):
        """
        Runs every time a new message is recieved from the MQTT Broker.
        Messages are expected to have a structure according to the following example:
        {
          "type": "heat_output",
          "value": 14
        }
        """
        try:
            message = json.loads(msg.payload)
            message_type = message.get("type")
            value = message.get("value")

            if message_type == "heat_output":
                self.update_heat_output(value)
            # Add elif blocks and update functions for other message types as needed.
            else:
                print(f"Recieved unknown message type: {message_type}")
        except ValueError as e:
            print(f"Could not decode JSON payload: {e}")
    
    def update_heat_output(self, value):
        """
        Updates the heat that is currently emitted from actuators in the farm.
        """
        if value is not None:
            self.heat_from_actuators = value
        else:
            print("Heat output message is missing a value.")

    def get_ambient_temperature(self, ambient_temp_average, ambient_temp_variation, ambient_temp_cycle):
        """
        Gets the current ambient temperature.
        For testing purposes it will simply give a value according to a cosine wave based on the time and cycle period.

        Parameters:
            ambient_temp_average: The average temperature in a cycle.
            ambient_temp_variation: The temperature amplitude.
            ambient_temp_cycle: The amount of time to complete a cycle. Valid options are "minute", "hour" and "day".

        Returns:
            current_ambient_temp: The current ambient temperature.
        """
        # Determine the number of seconds in a cycle based on the specified cycle period.
        if ambient_temp_cycle == "minute":
            cycle_duration = 60
        elif ambient_temp_cycle == "hour":
            cycle_duration = 3600  # 60*60
        elif ambient_temp_cycle == "day":
            cycle_duration = 86400  # 60*60*24
        else:
            print("Unexpected value for ambient temperature cycle, valid arguments are 'minute', 'hour' and 'day'.\nDefaulting to one day cycle period.")
            self.ambient_temp_cycle = "day"
            cycle_duration = 86400

        current_ambient_temp = ambient_temp_average + ambient_temp_variation*math.cos(2*math.pi*time.time()/cycle_duration)
        return current_ambient_temp

    def update(self):
        """
        Makes a single update to the simulated VFF.
        """
        # Update ambient temperature based on time and cycle period.
        ambient_temp = self.get_ambient_temperature(
            ambient_temp_average=self.ambient_temp_avg,
            ambient_temp_variation=self.ambient_temp_var,
            ambient_temp_cycle=self.ambient_temp_cycle
        )
        heat_from_ambient_temp = 0.2*(ambient_temp - self.current_temp)*self.dt

        # Update room temperature based on heat gained or lost from ambient temperature.
        self.current_temp += heat_from_ambient_temp

        # Make current climate readable for sensors through MQTT.
        message_for_sensors = {
            "temperature": self.current_temp,
            #  Add more climate variables as needed.
        }
        self.client.publish(self.publish_topic, json.dumps(message_for_sensors))

        # Update room climate variables based on output from actuators.
        self.current_temp += self.heat_from_actuators

        print(f"Ambient temperature: {ambient_temp}°C, Heat from actuators: {self.heat_from_actuators}°C, Farm temperature: {self.current_temp}°C")
        
    def simulate(self):
        """
        Continuously updates the simulated VFF at a rate determined by the delta time (dt).
        """
        while True:
            self.update()
            time.sleep(self.dt)

if __name__ == "__main__":
    simulator = VFFSimulator(
        broker_hostname="mqtt_broker",
        port=1883,
        subscribe_topic="VFF/actuators/output",
        publish_topic="VFF/sensors/input",
        dt=0.1,
        ambient_temp_avg=14,
        ambient_temp_var=4,
        ambient_temp_cycle="minute")  # Use a short cycle for testing purposes
    simulator.simulate()

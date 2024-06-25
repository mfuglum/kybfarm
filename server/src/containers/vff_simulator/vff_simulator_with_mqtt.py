import time, math  # For the simulation functionality
import signal, sys  # For graceful shutdown of the process
import json  # For MQTT messages
import paho.mqtt.client as mqtt
import os  # For accessing environment variables

class VFFSimulator:
    """A simulated VFF involving the climate variables within the farm, as well as the sensor and actuator devices interacting with the climate."""

    def __init__(
            self,
            mqtt_broker_url: str,
            mqtt_broker_port: int,
            subscribe_topic: str,
            publish_topic: str,
            update_interval: float=0.1,
            ambient_temp_average: float=14,
            ambient_temp_amplitude: float=4,
            ambient_temp_cycle_time: str="day"
        ):
        """
        Initializes the VFF simulator.

        Parameters:
            mqtt_broker_url:
            mqtt_broker_port:
            subscribe_topic:
            publish_topic:
            update_interval:
            ambient_temp_average:
            ambient_temp_amplitude:
            ambient_temp_cycle_time:
        """
        # Process shutdown signal handler.
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        # Simulation configurations.
        self.update_interval = update_interval
        self.ambient_temp_average = ambient_temp_average
        self.ambient_temp_amplitude = ambient_temp_amplitude
        self.ambient_temp_cycle_time = ambient_temp_cycle_time
        # Initial temperature in the farm is the same as the ambient temperature.
        self.current_temp = self.get_ambient_temperature(
            ambient_temp_average=self.ambient_temp_average,
            ambient_temp_amplitude=self.ambient_temp_amplitude,
            ambient_temp_cycle_time=self.ambient_temp_cycle_time
        )
        self.heat_from_actuators = 0  # Default value

        # MQTT configurations.
        self.subscribe_topic = subscribe_topic
        self.publish_topic = publish_topic
        self.client = mqtt.Client("VFFSimulator")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        try:
            self.client.connect(mqtt_broker_url, mqtt_broker_port)  # Connect to the Broker
        except Exception as e:
            print(f"Failed to connect to MQTT Broker at {mqtt_broker_url}:{mqtt_broker_port}, error: {e}")
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

    def get_ambient_temperature(self, ambient_temp_average, ambient_temp_amplitude, ambient_temp_cycle_time):
        """
        Gets the current ambient temperature.
        For testing purposes it will simply give a value according to a cosine wave based on the time and cycle period.

        Parameters:
            ambient_temp_average: The average temperature in a cycle.
            ambient_temp_amplitude: The temperature amplitude.
            ambient_temp_cycle_time: The amount of time to complete a cycle. Valid options are "minute", "hour" and "day".

        Returns:
            current_ambient_temp: The current ambient temperature.
        """
        # Determine the number of seconds in a cycle based on the specified cycle period.
        if ambient_temp_cycle_time == "minute":
            cycle_duration = 60
        elif ambient_temp_cycle_time == "hour":
            cycle_duration = 3600  # 60*60
        elif ambient_temp_cycle_time == "day":
            cycle_duration = 86400  # 60*60*24
        else:
            print("Unexpected value for ambient temperature cycle, valid arguments are 'minute', 'hour' and 'day'.\nDefaulting to one day cycle period.")
            self.ambient_temp_cycle_time = "day"
            cycle_duration = 86400

        current_ambient_temp = ambient_temp_average + ambient_temp_amplitude*math.cos(2*math.pi*time.time()/cycle_duration)
        return current_ambient_temp

    def update(self):
        """
        Makes a single update to the simulated VFF.
        """
        # Update ambient temperature based on time and cycle period.
        ambient_temp = self.get_ambient_temperature(
            ambient_temp_average=self.ambient_temp_average,
            ambient_temp_amplitude=self.ambient_temp_amplitude,
            ambient_temp_cycle_time=self.ambient_temp_cycle_time
        )
        heat_from_ambient_temp = 0.2*(ambient_temp - self.current_temp)*self.update_interval

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
        Continuously updates the simulated VFF at a rate determined by the update interval.
        """
        while True:
            self.update()
            time.sleep(self.update_interval)

if __name__ == "__main__":
    mqtt_broker_url = os.getenv("MQTT_BROKER_CONTAINER_URL")
    mqtt_broker_port = int(os.getenv("MQTT_BROKER_CONTAINER_PORT"))
    subscribe_topic = os.getenv("VFF_SIMULATOR_SUBSCRIBE_TOPIC")
    publish_topic = os.getenv("VFF_SIMULATOR_PUBLISH_TOPIC")
    update_interval = float(os.getenv("VFF_SIMULATOR_UPDATE_INTERVAL"))
    ambient_temp_average = float(os.getenv("VFF_SIMULATOR_AMBIENT_TEMP_AVERAGE"))
    ambient_temp_amplitude = float(os.getenv("VFF_SIMULATOR_AMBIENT_TEMP_AMPLITUDE"))
    ambient_temp_cycle_time = os.getenv("VFF_SIMULATOR_AMBIENT_TEMP_CYCLE_TIME")

    simulator = VFFSimulator(
        mqtt_broker_url=mqtt_broker_url,
        mqtt_broker_port=mqtt_broker_port,
        subscribe_topic=subscribe_topic,
        publish_topic=publish_topic,
        update_interval=update_interval,
        ambient_temp_average=ambient_temp_average,
        ambient_temp_amplitude=ambient_temp_amplitude,
        ambient_temp_cycle_time=ambient_temp_cycle_time
    )
    simulator.simulate()

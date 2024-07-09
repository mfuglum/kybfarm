import random, time  # For the simulation functionality
import signal, sys  # For graceful shutdown of the process
import json  # For MQTT messages
import paho.mqtt.client as mqtt
import os  # For accessing environment variables

class TemperatureSensorSimulator:
    """A simulated temperature sensor with specified measurement noise."""

    def __init__(
        self,
        mqtt_broker_url: str,
        mqtt_broker_port: int,
        subscribe_vff_simulator_topic: str,
        publish_state_topic: str,
        #############################################################
        ##### MQTT DISCOVERY FUNCTIONALITY # NOT YET IMPLEMENTED ####
        # subscribe_home_assistant_status_topic: str,
        # publish_discovery_topic: str,
        #############################################################
        noise_level=0.5,
        sampling_time=0.1
        ):
        """
        Initializes the temperature sensor with a specified noise level.

        Parameters:
            mqtt_broker_url: Address of the container running the MQTT broker.
            mqtt_broker_port: Exposed port used by the container running the MQTT broker.
            subscribe_vff_simulator_topic: Topic used by the sensor simulator to get data from the VFF simulator.
            publish_state_topic: Topic used by the sensor simulator to pass on its latest sensor readings.
            #############################################################
            ##### MQTT DISCOVERY FUNCTIONALITY # NOT YET IMPLEMENTED ####
            subscribe_home_assistant_status_topic: Topic used by Home Assistant to notify clients when the service goes online or offline.
            publish_discovery_topic: Topic used by Home Assistant to discover and configure device automatically.
            #############################################################
            noise_level: The maximum deviation due to noise.
            sampling_time: Time between each sensor reading.
        """
        # Process shutdown signal handler.
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        # Simulation configurations.
        self.noise_level = noise_level
        self.sampling_time = sampling_time
        self.latest_temperature = None

        # MQTT configurations.
        self.subscribe_vff_simulator_topic = subscribe_vff_simulator_topic
        self.publish_state_topic = publish_state_topic
        #############################################################
        ##### MQTT DISCOVERY FUNCTIONALITY # NOT YET IMPLEMENTED ####
        # self.subscribe_home_assistant_status_topic = subscribe_home_assistant_status_topic
        # self.publish_discovery_topic = publish_discovery_topic
        #############################################################
        self.client = mqtt.Client("TemperatureSensorSimulator")
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
        Informs if connection to MQTT Broker is successful or not, and begins subscribing to subscribe_vff_simulator_topic if it is.
        """
        if return_code == 0:
            print("Connected to MQTT Broker.")
            self.client.subscribe(self.subscribe_vff_simulator_topic)
            #############################################################
            ##### MQTT DISCOVERY FUNCTIONALITY # NOT YET IMPLEMENTED ####
            # self.client.subscribe(self.subscribe_home_assistant_status_topic)
            # self.publish_discovery_message()
            #############################################################
        else:
            print(f"Failed to connect to MQTT Broker, return code: {return_code}")

    def on_message(self, client, userdata, msg):
        """
        Runs every time a new message is recieved from the MQTT Broker.
        """
        if msg.topic == self.subscribe_vff_simulator_topic:
            """
            Messages are expected to have a structure according to the following example:
            {
            "temperature": 14
            }
            """
            try:
                message = json.loads(msg.payload)
                actual_temperature = message.get("temperature")
                if actual_temperature is not None:
                    self.latest_temperature = actual_temperature
                else:
                    print("Temperature message missing value for 'temperature' key.")
            except ValueError as e:
                print(f"Could not decode JSON payload: {e}")

    #############################################################
    ##### MQTT DISCOVERY FUNCTIONALITY # NOT YET IMPLEMENTED ####
        # elif msg.topic == self.subscribe_home_assistant_status_topic:
        #     """
        #     Messages are expected to have a structure according to the following example:
        #     "status": online
        #     """
        #     if msg.payload == "online":
        #         self.publish_discovery_message()
        #         print("Sent a discovery message")
        

    # def publish_discovery_message(self):
    #     discovery_message = {
    #         "name": "Temperature",
    #         "unique_id": "temperature_sensor_simulator_01",
    #         "device_class": "temperature",
    #         "state_topic": "homeassistant/sensor/temperature_sensor_simulator_01/state",  # Discovery topic format: "<discovery_prefix>/<component>/[<node_id>/]<object_id>/config" (Best practice for entities with a unique_id is to set <object_id> to unique_id and omit the <node_id>.)
    #         "value_template": "{{ value_json.temperature_reading }}",
    #         "unit_of_measurement": "°C",
    #         "suggested_display_precision": 1,  # The number of decimals which should be used in the sensor's state when it's displayed.
    #         "device": {
    #             "name": "Sensor simulator",
    #             "identifiers": [
    #                 "tss01"
    #             ]
    #         }
    #     }
    #     self.client.publish(self.publish_discovery_topic, json.dumps(discovery_message), qos=1, retain=True)
    #############################################################

    def read_temperature(self, true_temperature):
        """
        Simulates reading the temperature by adding a random noise to the actual temperature.

        Parameters:
            true_temperature: The true temperature of the environment.

        Returns:
            temperature_reading: The noisy temperature reading.
        """
        # Add noise to the temperature reading to simulate an imperfect sensor
        noise = random.uniform(-self.noise_level, self.noise_level)
        temperature_reading = true_temperature + noise
        return temperature_reading

    def update(self):
        """
        Makes a single update to the simulated temperature sensor.
        """
        if self.latest_temperature is not None:
            temperature_reading = self.read_temperature(self.latest_temperature)
            print(f"Measured temperature: {temperature_reading}°C")
            message = {
                "temperature_reading": temperature_reading
            }
            self.client.publish(self.publish_state_topic, json.dumps(message))

    def simulate(self):
        """
        Continuously updates the simulated temperature sensor at a rate determined by the sampling time.
        """
        while True:
            update_start_time = time.time()
            self.update()
            update_stop_time = time.time()
            update_duration = update_stop_time - update_start_time
            remaining_sleep_time = self.sampling_time - update_duration
            if remaining_sleep_time < 0:
                remaining_sleep_time = 0
            time.sleep(remaining_sleep_time)

if __name__ == "__main__":
    mqtt_broker_url = os.getenv("MQTT_BROKER_CONTAINER_URL")
    mqtt_broker_port = int(os.getenv("MQTT_BROKER_CONTAINER_PORT"))
    subscribe_vff_simulator_topic = os.getenv("VFF_SIMULATOR_PUBLISH_TOPIC")
    publish_state_topic = os.getenv("TEMPERATURE_SENSOR_SIMULATOR_01_PUBLISH_STATE_TOPIC")
    noise_level = float(os.getenv("TEMPERATURE_SENSOR_SIMULATOR_01_NOISE_LEVEL"))
    sampling_time = float(os.getenv("TEMPERATURE_SENSOR_SIMULATOR_01_SAMPLING_TIME"))
    
    simulator = TemperatureSensorSimulator(
        mqtt_broker_url=mqtt_broker_url,
        mqtt_broker_port=mqtt_broker_port,
        subscribe_vff_simulator_topic=subscribe_vff_simulator_topic,
        publish_state_topic=publish_state_topic,
        #############################################################
        ##### MQTT DISCOVERY FUNCTIONALITY # NOT YET IMPLEMENTED ####
        # subscribe_home_assistant_status_topic="homeassistant/status",
        # publish_discovery_topic="homeassistant/sensor/temperature_sensor_simulator_01/config",
        #############################################################
        noise_level=noise_level,
        sampling_time=sampling_time
    )
    simulator.simulate()

import random, time  # For the simulation functionality
import signal, sys  # For graceful shutdown of the process
import json  # For MQTT messages
import paho.mqtt.client as mqtt

class TemperatureSensorSimulator:
    """A simulated temperature sensor with specified measurement noise."""

    def __init__(
        self,
        broker_hostname: str,
        port: int,
        subscribe_topic: str,
        publish_topic: str,
        noise_level=0.5,
        sampling_time=0.1):
        """
        Initializes the temperature sensor with a specified noise level.

        Parameters:
            broker_hostname:
            port:
            subscribe_topic:
            publish_topic:
            noise_level: The maximum deviation due to noise.
        """
        # Process shutdown signal handler.
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        # Simulation configurations.
        self.noise_level = noise_level
        self.sampling_time = sampling_time
        self.latest_temperature = None

        # MQTT configurations.
        self.subscribe_topic = subscribe_topic
        self.publish_topic = publish_topic
        self.client = mqtt.Client("TemperatureSensorSimulator")
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

    def read_temperature(self, actual_temperature):
        """
        Simulates reading the temperature by adding a random noise to the actual temperature.

        Parameters:
            actual_temperature: The true temperature of the environment.

        Returns:
            temperature_reading: The noisy temperature reading.
        """
        # Add noise to the temperature reading to simulate an imperfect sensor
        noise = random.uniform(-self.noise_level, self.noise_level)
        measured_temperature = actual_temperature + noise
        return measured_temperature

    def update(self):
        """
        Makes a single update to the simulated temperature sensor.
        """
        if self.latest_temperature is not None:
            measured_temperature = self.read_temperature(self.latest_temperature)
            print(f"Measured temperature: {measured_temperature}°C")
            message = {
                "measured_temperature": measured_temperature
            }
            self.client.publish(self.publish_topic, json.dumps(message))

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
    simulator = TemperatureSensorSimulator(
        broker_hostname="mqtt_broker",
        port=1883,
        subscribe_topic="VFF/sensors/input",
        publish_topic="VFF/sensors/output",
        noise_level=0.2,
        sampling_time=0.5
    )
    simulator.simulate()

import time # For the controller functionality
import signal, sys  # For graceful shutdown of the process
import json  # For MQTT messages
import paho.mqtt.client as mqtt
import os  # For accessing environment variables

class HeatPumpSimulator:
    """A simulated heat pump with specified operational efficiency."""

    def __init__(
        self,
        mqtt_broker_url: str,
        mqtt_broker_port: int,
        subscribe_control_signal_topic: str,
        publish_vff_simulator_topic: str,
        efficiency=1.0,
        min_heat_output=0,
        max_heat_output=100,
        sampling_time=0.1
        ):
        """
        Initializes the heat pump simulator.

        Parameters:
            mqtt_broker_url: Address of the container running the MQTT broker.
            mqtt_broker_port: Exposed port used by the container running the MQTT broker.
            subscribe_control_signal_topic: Topic used by the heat pump simulator to get control signal from temperature controller.
            publish_vff_simulator_topic: Topic used by the heat pump simulator to add temperature values to the VFF simulator.
            efficiency: The operational efficiency of the heat pump.
            min_heat_output: The minimum heat output of the heat pump.
            max_heat_output: The maximum heat output of the heat pump.
            sampling_time: Time between each heat pump temperature update.
        """
        # Process shutdown signal handler.
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        # Simulation configurations.
        self.efficiency = efficiency
        self.min_heat_output = min_heat_output
        self.max_heat_output = max_heat_output
        self.sampling_time = sampling_time
        self.latest_control_signal = None

        # MQTT configurations.
        self.subscribe_control_signal_topic = subscribe_control_signal_topic
        self.publish_vff_simulator_topic = publish_vff_simulator_topic
        self.client = mqtt.Client("HeatPumpSimulator")
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
        Informs if connection to MQTT Broker is successful or not, and begins subscribing to subscribe_control_signal_topic if it is.
        """
        if return_code == 0:
            print("Connected to MQTT Broker.")
            self.client.subscribe(self.subscribe_control_signal_topic)
        else:
            print(f"Failed to connect to MQTT Broker, return code: {return_code}")

    def on_message(self, client, userdata, msg):
        """
        Runs every time a new message is recieved from the MQTT Broker.
        """
        if msg.topic == self.subscribe_control_signal_topic:
            """
            Messages are expected to have a structure according to the following example:
            {
            "control_signal": 14
            }
            """
            try:
                message = json.loads(msg.payload)
                control_signal = message.get("control_signal")
                if control_signal is not None:
                    self.latest_control_signal = control_signal
                else:
                    print("Measured temperature message missing value for 'control_signal' key.")
            except ValueError as e:
                print(f"Could not decode JSON payload: {e}")

    def get_heat_output(self, control_signal):
        """
        Calculates the heat output based on the control signal and the pump's efficiency.

        Parameters:
            control_signal: The control signal from the temperature controller.

        Returns:
            heat_output: The amount of heat added to the environment (in degrees per update).
        """
        heat_output = max(min(control_signal * self.efficiency, self.max_heat_output), self.min_heat_output)
        return heat_output
    
    def update(self):
        """
        Makes a single update to the simulated heat pump.
        """
        if self.latest_control_signal is not None:
            heat_output = self.get_heat_output(self.latest_control_signal)
            print(f"Heat output: {heat_output}°C")
            message = {
                "type": "heat_output",
                "value": heat_output
            }
            self.client.publish(self.publish_vff_simulator_topic, json.dumps(message))

    def simulate(self):
        """
        Continuously updates the simulated heat pump at a rate determined by the sampling time.
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
    subscribe_control_signal_topic = os.getenv("HEAT_PUMP_SIMULATOR_01_TEMPERATURE_COMMAND_TOPIC")
    publish_vff_simulator_topic = os.getenv("VFF_SIMULATOR_SUBSCRIBE_TOPIC")
    efficiency = float(os.getenv("HEAT_PUMP_SIMULATOR_01_EFFICIENCY"))
    min_heat_output = float(os.getenv("HEAT_PUMP_SIMULATOR_01_MIN_TEMP"))
    max_heat_output = float(os.getenv("HEAT_PUMP_SIMULATOR_01_MAX_TEMP"))
    sampling_time = float(os.getenv("HEAT_PUMP_SIMULATOR_01_SAMPLING_TIME"))

    simulator = HeatPumpSimulator(
        mqtt_broker_url=mqtt_broker_url,
        mqtt_broker_port=mqtt_broker_port,
        subscribe_control_signal_topic=subscribe_control_signal_topic,
        publish_vff_simulator_topic=publish_vff_simulator_topic,
        efficiency=efficiency,
        min_heat_output=min_heat_output,
        max_heat_output=max_heat_output,
        sampling_time=sampling_time
    )
    simulator.simulate()

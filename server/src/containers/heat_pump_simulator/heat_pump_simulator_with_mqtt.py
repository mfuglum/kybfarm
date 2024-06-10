import time # For the controller functionality
import signal, sys  # For graceful shutdown of the process
import json  # For MQTT messages
import paho.mqtt.client as mqtt

class HeatPumpSimulator:
    """A simulated heat pump with specified operational efficiency."""

    def __init__(
        self,
        broker_hostname: str,
        port: int,
        subscribe_topic: str,
        publish_topic: str,
        efficiency=1.0,
        min_heat_output=0,
        max_heat_output=100,
        sampling_time=0.1):
        """
        Initializes the heat pump simulator.

        Parameters:
            broker_hostname:
            port:
            subscribe_topic:
            publish_topic:
            efficiency: The operational efficiency of the heat pump.
            min_heat_output: The minimum heat output of the heat pump.
            max_heat_output: The maximum heat output of the heat pump.
        """
        # Process shutdown signal handler.
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        # Simulation configurations.
        self.efficiency = efficiency
        self.min_heat_output = min_heat_output
        self.max_heat_output = max_heat_output
        self.sampling_time = sampling_time
        self.latest_measured_temperature = None

        # Controller configurations.
        self.controller = PIDController(
            Kp=0.4,
            Ki=0.1,
            Kd=0.05,
            max_integral=10,
            min_integral=-10
        )

        # MQTT configurations.
        self.subscribe_topic = subscribe_topic
        self.publish_topic = publish_topic
        self.client = mqtt.Client("HeatPumpSimulator")
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
          "measured_temperature": 14
        }
        """
        try:
            message = json.loads(msg.payload)
            measured_temperature = message.get("measured_temperature")
            if measured_temperature is not None:
                self.latest_measured_temperature = measured_temperature
            else:
                print("Measured temperature message missing value for 'measured_temperature' key.")
        except ValueError as e:
            print(f"Could not decode JSON payload: {e}")

    def get_heat_output(self, control_signal):
        """
        Calculates the heat output based on the control signal and the pump's efficiency.

        Parameters:
            control_signal: The control signal from the PID controller.

        Returns:
            heat_output: The amount of heat added to the environment (in degrees per update).
        """
        heat_output = max(min(control_signal * self.efficiency, self.max_heat_output), self.min_heat_output)
        return heat_output
    
    def update(self):
        """
        Makes a single update to the simulated heat pump.
        """
        if self.latest_measured_temperature is not None:
            control_signal = self.controller.calculate_control_signal(
                setpoint=22,
                input_value=self.latest_measured_temperature
            )
            heat_output = self.get_heat_output(control_signal)
            print(f"Heat output: {heat_output}°C")
            message = {
                "type": "heat_output",
                "value": heat_output
            }
            self.client.publish(self.publish_topic, json.dumps(message))

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

class PIDController():
    """A Proportional-Integral-Derivative (PID) controller."""

    def __init__(self, Kp: float, Ki: float, Kd: float, max_integral: float = 10, min_integral: float = -10):
        """
        Initializes the PID controller with specified gains

        Parameters:
            Kp: The proportional gain.
            Ki: The integral gain.
            Kd: The derivative gain.
            max_integral: Upper limit for integral windup.
            min_integral: Lower limit for integral windup.
        """
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.max_integral = max_integral
        self.min_integral = min_integral

        # Initialize internal states
        self.previous_time = None  # Initialize as None to indicate first call of calculate_control_signal()
        self.previous_error = 0
        self.integral = 0

    def calculate_control_signal(self, setpoint: float, input_value: float) -> float:
        """
        Calculates the control output value based on the setpoint and current input value.

        Parameters:
            setpoint: The desired target value.
            input_value: The current value of the input.

        Returns:
            control_signal: The output value from the PID controller.
        """
        # Initialize calculation parameters
        error = setpoint - input_value
        current_time = time.time()

        # Check if it is the first call
        if self.previous_time is None:
            # Skip derivative and integral term on the first call due to no time having passed.
            derivative = 0
        else:
            # PID calculations
            delta_time = current_time - self.previous_time
            delta_error = error - self.previous_error
            derivative = delta_error / delta_time if delta_time > 0 else 0
            self.integral += error * delta_time
            self.integral = max(min(self.integral, self.max_integral), self.min_integral)  # Anti-Windup

        # Calculate output value
        control_signal = (self.Kp * error) + (self.Ki * self.integral) + (self.Kd * derivative)

        # Update for next calculation
        self.previous_time = current_time
        self.previous_error = error

        return control_signal

if __name__ == "__main__":
    simulator = HeatPumpSimulator(
        broker_hostname="mqtt_broker",
        port=1883,
        subscribe_topic="VFF/sensors/output",
        publish_topic="VFF/actuators/output",
        efficiency=1.0,
        min_heat_output=0,
        max_heat_output=100,
        sampling_time=0.5
    )
    simulator.simulate()

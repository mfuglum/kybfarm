####################
# WORK IN PROGRESS #
####################

import signal
import sys
import json
import paho.mqtt.client as mqtt

class MQTTClient:

    def __init__(self,
                 client_name,
                 broker_address,
                 broker_port,
                 subscriber_topic,
                 publisher_topic):
        
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        self.subscriber_topic = subscriber_topic
        self.publisher_topic = publisher_topic

        self.client = mqtt.Client(client_name)

        # Configure callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_publish = self.on_publish
        self.client.on_subscribe = self.on_subscribe

        self.client.connect(broker_address,
                            broker_port)
        self.client.loop_start

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

    def on_publish(self, client, userdata):
        pass

    def on_subscribe(self, client, userdata, mid, qos):
        pass

    def publish_message(self, message, qos):
        self.client.publish(topic=self.publisher_topic,
                            payload=message,
                            qos=qos)
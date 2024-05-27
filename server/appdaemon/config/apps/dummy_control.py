# A dummy control app for testing purposes

# import appdaemon.plugins.hass.hassapi as hass
import hassapi as hass
import json

class DummyControl(hass.Hass):
    def initialize(self):
        self.log("Dummy Control App initialized")
        self.log("This is a dummy control app for testing purposes")

        # Load parameters:
        # Load gain from apps.yaml file
        self.gain = self.args["gain"]

        # Load reference value from apps.yaml file
        self.reference = self.args["reference_value"] 

        # Load sensor from apps.yaml file
        self.sensor = self.args["sensor"]

        # Load control signal topic from apps.yaml file
        self.control_signal_topic = self.args["control_signal_topic"]


        # When sensor device publishes to HA, the sensor_callback function is called
        self.listen_state(self.sensor_callback, self.sensor)


    def sensor_callback(self, entity, attribute, old, new, kwargs):
        self.log("Sensor: {}".format(entity))
        self.log("Old: {}".format(old))
        self.log("New: {}".format(new))
        self.log("Reference: {}".format(self.reference))

        # Assert that the new value is not None
        try: 
            assert new is not None
        except:
            self.log("Error: new value is None")
            return
        
        try:
            # Gain/P control: control_signal = gain * (reference - value)

            # Calculate the difference between the reference value and the new sensor value
            difference =  self.reference - float(new)
            self.log("Difference: {}".format(difference))

            # Calculate the control signal
            control_signal = self.gain * difference
            self.log("Control signal: {}".format(control_signal))

            # Create MQTT payload and publish to HA
            payload = {
                "control_signal": control_signal,
                "sensor_value": new,
                "reference_value": self.reference,
            }

            # Publish the control signal to HA in JSON format
            self.call_service("mqtt/publish", topic=self.control_signal_topic, payload=json.dumps(payload))
            self.log("Published to HA")
        except:
            self.log("Error: Could not calculate control signal")
            return


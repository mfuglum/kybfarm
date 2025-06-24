import RPi.GPIO as GPIO
import threading
import json
import time

class SolidStateRelay:
    """
    GPIO-based control class for Solid State Relay (SSR).

    This class controls an SSR used for resistive heating, using GPIO output.

    Args:
        pin (int): GPIO BCM pin number used to control the SSR (e.g. 26)

    Behavior:
        - HIGH: relay ON
        - LOW: relay OFF

    Pin notes:
        - Ensure correct wiring: optocoupler SSRs typically require active HIGH signal.
    """

    def __init__(self, pin=26):
        self.pin = pin
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)  # Default OFF

    def turn_on(self):
        """Turns the relay ON (SSR closed, heating active)."""
        GPIO.output(self.pin, GPIO.HIGH)

    def turn_off(self):
        """Turns the relay OFF (SSR open, heating inactive)."""
        GPIO.output(self.pin, GPIO.LOW)

    def turn_on_for(self, duration):
        """Turns the relay ON for a specific number of seconds."""
        self.turn_on()
        threading.Timer(duration, self.turn_off).start()

    def get_state(self):
        """Returns True if SSR is ON, False otherwise."""
        return GPIO.input(self.pin) == GPIO.HIGH

    def on_message(self, client, userdata, msg):
        """MQTT handler for SSR commands."""
        try:
            payload = json.loads(msg.payload)
            cmd = payload.get("cmd")
            if cmd == "on_for":
                self.turn_on_for(float(payload["value"]))
            elif cmd == "on":
                self.turn_on()
            elif cmd == "off":
                self.turn_off()
            elif cmd == "get_state":
                client.publish(payload["res_topic"], json.dumps({"state": self.get_state()}))
            else:
                print("Unknown SSR command")
        except Exception as e:
            print("MQTT error in SSR:", e)

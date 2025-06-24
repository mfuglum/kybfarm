import RPi.GPIO as GPIO
import threading
import json
import time

class SolidStateRelay:
    """
    GPIO-based control class for Solid State Relay (SSR) with optional PWM.

    Args:
        pin (int): GPIO BCM pin number to control the SSR (e.g. 26)
    """

    def __init__(self, pin=26):
        self.pin = pin
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)
        self._pwm_loop_enabled = False
        self._pwm_thread = None

    def turn_on(self):
        GPIO.output(self.pin, GPIO.HIGH)

    def turn_off(self):
        GPIO.output(self.pin, GPIO.LOW)

    def turn_on_for(self, duration):
        self.turn_on()
        threading.Timer(duration, self.turn_off).start()

    def get_state(self):
        return GPIO.input(self.pin) == GPIO.HIGH

    def start_pwm_loop(self, duty_cycle, base_period):
        self._pwm_loop_enabled = True

        def pwm_cycle():
            while self._pwm_loop_enabled:
                on_time = base_period * duty_cycle
                off_time = base_period - on_time
                if on_time > 0:
                    self.turn_on()
                    time.sleep(on_time)
                if off_time > 0:
                    self.turn_off()
                    time.sleep(off_time)

        self._pwm_thread = threading.Thread(target=pwm_cycle)
        self._pwm_thread.daemon = True
        self._pwm_thread.start()

    def stop_pwm_loop(self):
        self._pwm_loop_enabled = False
        self.turn_off()

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload)
            cmd = payload.get("cmd")

            if cmd == "on":
                self.turn_on()

            elif cmd == "off":
                self.turn_off()

            elif cmd == "on_for":
                duration = float(payload.get("value", 0))
                self.turn_on_for(duration)

            elif cmd == "adjust_ssr_pwm":
                duty = float(payload.get("value_duty_cycle", 0))
                base = float(payload.get("value_base_period", 1))
                if 0 <= duty <= 1 and base > 0:
                    self.start_pwm_loop(duty, base)
                else:
                    print("Invalid PWM parameters.")

            elif cmd == "ssr_stop_pwm_loop":
                self.stop_pwm_loop()

            elif cmd == "get_state":
                client.publish(payload["res_topic"], json.dumps({"state": self.get_state()}))

            else:
                print(f"Unknown SSR command: {cmd}")

        except Exception as e:
            print("MQTT error in SSR:", e)

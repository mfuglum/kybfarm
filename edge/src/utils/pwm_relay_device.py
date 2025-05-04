import RPi.GPIO as GPIO
import threading
import time


class pwm_relay_device:
    def __init__(self, pin):
        # Disable warnings
        GPIO.setwarnings(False)
        
        # Set the pin number
        self.pin = pin

        # Set the pin numbering mode
        GPIO.setmode(GPIO.BCM)
        # Set the pin as output
        GPIO.setup(pin, GPIO.OUT)
        # Set the pin to low as ssr relay is OFF in high state
        GPIO.output(pin, GPIO.LOW)

        self.period = 5.0
        self.duty_cycle = 0.0
        self._running = False
        self._lock = threading.Lock()
        self._thread = None

    def set_pwm(self, period, duty_cycle):
        with self._lock:
            self.period = max(1.0, min(10.0, period))
            self.duty_cycle = max(0.0, min(1.0, duty_cycle))

        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._pwm_loop)
            self._thread.daemon = True
            self._thread.start()

    def update_duty_cycle(self, duty_cycle):
        with self._lock:
            self.duty_cycle = max(0.0, min(1.0, duty_cycle))

    def update_period(self, period):
        with self._lock:
            self.period = max(1.0, min(10.0, period))

    def stop_pwm(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)
            self._thread = None
        self.turn_off()
    
    def _pwm_loop(self):
        while self._running:
            with self._lock:
                duty = self.duty_cycle
                period = self.period

                duty = max(0.0, min(1.0, duty))
                period = max(1.0, min(10.0, period))

                if duty <= 0.0:
                    self.turn_off()
                    time.sleep(period)
                elif duty >= 1.0:
                    self.turn_on()
                    time.sleep(period)
                else:
                    on_time = period * duty
                    off_time = period * (1.0 - duty)
                    self.turn_on()
                    time.sleep(on_time)
                    self.turn_off()
                    time.sleep(off_time)
    
            


        # Turn the relay ON
    def turn_on(self):
        GPIO.output(self.pin, GPIO.HIGH)
        
    # Turn the relay OFF
    def turn_off(self):
        GPIO.output(self.pin, GPIO.LOW)

    # Turn the relay ON for a specified amount of time (seconds)
    def turn_on_for(self, time):
        self.turn_on()
        # Create a thread to turn off the relay after the specified time (seconds)
        threading.Timer(time, self.turn_off).start()

    
    
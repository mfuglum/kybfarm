import RPi.GPIO as GPIO
import threading

# Relay device class to control individual relays on TTL-RELAY02 / 04 / 08 control boards
class relay_device:
    def __init__ (self, pin):
        # Disable warnings
        GPIO.setwarnings(False)
        # Set the pin numbering mode
        GPIO.setmode(GPIO.BCM)
        # Set the pin as output
        GPIO.setup(pin, GPIO.OUT)
        # Set the pin to high as relay is OFF in high state
        GPIO.output(pin, GPIO.HIGH)

        self.pin = pin
    
    # def __del__ (self):
        # self.cleanup()

    # Turn the relay ON
    def turn_on(self):
        GPIO.output(self.pin, GPIO.LOW)
        
    # Turn the relay OFF
    def turn_off(self):
        GPIO.output(self.pin, GPIO.HIGH)

    # Turn the relay ON for a specified amount of time (seconds)
    def turn_on_for(self, time):
        self.turn_on()
        # Create a thread to turn off the relay after the specified time (seconds)
        threading.Timer(time, self.turn_off).start()
    
    
    
    # Cleanup the GPIO i.e. set all used pins in program back to input mode
    # def cleanup(self):
        # GPIO.cleanup()

import adbase as ad
import time




# Ec controller for grow tanks
class Intake_fan_controller(ad.ADBase):
    def initialize(self):
        self.adapi = self.get_ad_api()
        self.adapi.log("Intake fan controller init...")
        
        self.humid_upper = self.args["upper_humid_limit"]
        self.humid_lower = self.args["lower_humid_limit"]
        humid_sensor_id = self.args["humidity_sensor_id"]
        self.humidity = self.adapi.get_entity(humid_sensor_id)

        temp_sens_id = self.args["temp_sensor_id"]
        self.temp = self.adapi.get_entity(temp_sens_id)

        intake_fan_id = self.args["intake_fan_id"]
        self.intake_fan = self.adapi.get_entity(intake_fan_id)
        self.humidity.listen_state(self.callback)
        self.adapi.log("Intake fan controller init finished")


    def callback(self, entity, attribute, old, new, cb_args):
        new = float(new)
        temp = float(self.temp.get_state())
        if new < self.humid_lower and temp < 24:
            # self.adapi.log(f"new value is {new}")
            # self.adapi.log("Humidity too low, turning off intake fan")
            self.intake_fan.turn_off()
        elif new > self.humid_upper or temp > 25:
            # self.adapi.log(f"new value is {new}")
            # self.adapi.log("Humidity too high, turning on intake fan")
            self.intake_fan.turn_on()
        




        




    

    
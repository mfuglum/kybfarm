import adbase as ad
import time








# Prob dont need timeout


############ SE ON_FOR IN EDGE COMPUTER, REWRITE WITH 
class Level_controller(ad.ADBase):
    def initialize(self):
        self.adapi = self.get_ad_api()

        self.fill_time = self.args["fill_time"]

        self.solenoid = self.adapi.get_entity(self.args["act_entity_id"])
        self.level_sensor = self.adapi.get_entity(self.args["sensor_entity_id"])

        
        self.level_sensor.listen_state(self.callback)

    def callback(self,entity,attribute,old,new,cb_args):

        self.log("Sensor: {}".format(entity))
        self.log("Old: {}".format(old))
        self.log("New: {}".format(new))
        self.log("Reference: {}".format(self.reference))


        if new == "on":
            self.solenoid.set_state("on")
            time.sleep(self.fill_time)
            self.log("level too low, activating solenoid")
        elif new == "off":
            self.solenoid.set_state("off")
            self.log("turning off solenoid")




        
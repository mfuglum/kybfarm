import adbase as ad
import time




# Ec controller for grow tanks
class Air_pump_controller(ad.ADBase):

    """
        Appdeamon App for controlling air pump controller. Main purpose is to make sure the air pump is always on,
        even if the edge computer has reset.

        configs:
            id : HA id of air pump

    """


    def initialize(self):
        self.adapi = self.get_ad_api()
        self.adapi.log("Air pump controller init...")
        air_pump_switch_id = self.args["id"]
        self.air_pump_switch = self.adapi.get_entity(air_pump_switch_id)

        self.adapi.run_every(self.callback,"now",60)
        self.adapi.log("Air pump controller init finished")


    def callback(self, cb_args):
        switch_state = self.air_pump_switch.get_state()
        if switch_state == "off":
            self.air_pump_switch.turn_off()
        else:
            self.air_pump_switch.turn_on()
        




        




    

    
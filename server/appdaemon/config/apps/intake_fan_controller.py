import adbase as ad
import time




class Intake_fan_controller(ad.ADBase):

    """
    Appdeamon app for controlling intake fan on the Kybfarm vertical farming system

    configs:
        humid_high_id : id of humidity upper bound input in HA
        humid_low_id : id of humidity lower bound input in HA
        temp_high_id : id of temperature upper bound input in HA
        temp_low_id : id of temperature lower bound input in HA
        humidity_sensor_id : HA id of humidity sensor
        temp_sensor_id : HA id of temperature sensor 
        toggle_id : HA id of toggle button for turning controller on/off
        intake_fan_id : HA id of intake fan

    """


    def initialize(self):
        self.adapi = self.get_ad_api()
        self.adapi.log("Intake fan controller init...")
        

        humid_high_id  = self.args["humid_high_id"]
        self.humid_high = self.adapi.get_entity(humid_high_id)
        humid_low_id  = self.args["humid_low_id"]
        self.humid_low = self.adapi.get_entity(humid_low_id)

        temp_high_id  = self.args["temp_high_id"]
        self.temp_high = self.adapi.get_entity(temp_high_id)

        temp_low_id  = self.args["temp_low_id"]
        self.temp_low = self.adapi.get_entity(temp_low_id)


        humid_sensor_id = self.args["humidity_sensor_id"]
        self.humidity = self.adapi.get_entity(humid_sensor_id)

        temp_sens_id = self.args["temp_sensor_id"]
        self.temp = self.adapi.get_entity(temp_sens_id)
        toggle_id = self.args["toggle_id"]
        
        intake_fan_id = self.args["intake_fan_id"]
        self.intake_fan = self.adapi.get_entity(intake_fan_id)
        self.toggle = self.adapi.get_entity(toggle_id)
        self.cb_handle = None
        if self.toggle.get_state() == "on":
           self.cb_handle =  self.humidity.listen_state(self.callback)

        self.toggle.listen_state(self.toggle_control)




        self.adapi.log("Intake fan controller init finished")


    def callback(self, entity, attribute, old, new, cb_args):
        new = float(new)
        temp = float(self.temp.get_state())
        if new < float(self.humid_low.get_state()) and temp < float(self.temp_low.get_state()):
            self.intake_fan.turn_off()
        elif new > float(self.humid_high.get_state()) or temp > float(self.temp_high.get_state()):
            self.intake_fan.turn_on()
        



    def toggle_control(self, entity, attribute, old, new, cb_args):

        if new == "on":
            self.cb_handle = self.humidity.listen_state(self.callback)
            self.adapi.log("Intake fan controller turned on")
        elif new == "off":
            self.adapi.cancel_listen_state(self.cb_handle)
            self.intake_fan.turn_off()
            self.adapi.log("Intake fan controller turned off")

        




    

    
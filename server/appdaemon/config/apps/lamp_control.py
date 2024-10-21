import adbase as ad

# Ec controller for grow tanks
class Lamp_control(ad.ADBase):
    def initialize(self):
        self.adapi = self.get_ad_api()
        self.adapi.log("Lamp controller init...")
        self.ampls = self.args["amplitudes"]
        self.on_time = self.args["on_time"]
        self.ids = self.args["ids"]

        self.values = [self.adapi.get_entity(id) for id in self.ids]

        # self.run_at(self.callback,"08:00:00")
        # self.run_at(self.callback,"23:59:00")
        # self.adapi.run_at(self.callback,"12:01:30")
        self.adapi.run_at(self.callback,"09:45:00")
        self.adapi.run_at(self.callback,"09:47:00")
        self.adapi.log("Lamp controller init finished")
    
    def callback(self,cb_args):
        self.adapi.log("hello from cb")
        amplitudes = [int(float(value.get_state())) for value in self.values]
        if any(amplitudes):
            self.adapi.log("Turning off lamp")
            [value.set_state(state = 0) for value in self.values]
            amplitudes = [int(float(value.get_state())) for value in self.values]
            self.adapi.log(f" Ampls are now {amplitudes}")

        else:
            self.adapi.log("Turning on lamp")
            [value.set_state(state = ampl) for value,ampl in zip(self.values,self.ampls)]


        


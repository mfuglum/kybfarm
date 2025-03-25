import adbase as ad

class Lamp_control(ad.ADBase):

    """
    Appdeamon app for controlling intensity and timing for Kybfarm's grow lamp



    configs:
        input_amplitude_ids : list of HA ids for amplitude inputs in Main dashboard
        amplitude_ids : list of HA ids for control of amplitudes
        toggle_id : HA id for toggle turning the controller on/off
        start_time_id : HA id for input in Main dashboard which controls at what time of the day the lamp should turn on
        finish_time_id : HA id for input in Main dashboard which controls at what time of the day the lamp should turn off



    """

    def initialize(self):
        self.adapi = self.get_ad_api()
        self.label = self.args["name"]
        self.adapi.log(f"[{self.label}] Lamp controller init...")
        input_amplitude_ids = self.args["input_amplitude_ids"]
        self.amplitudes =  [self.adapi.get_entity(id) for id in input_amplitude_ids]

        amplitude_ids = self.args["amplitude_ids"]

        self.values = [self.adapi.get_entity(id) for id in amplitude_ids]


        toggle_id = self.args["toggle_id"]
        self.toggle= self.adapi.get_entity(toggle_id)

        start_time_id = self.args["start_time_id"]
        finish_time_id = self.args["finish_time_id"]

        self.start_time = self.adapi.get_entity(start_time_id)
        self.finish_time = self.adapi.get_entity(finish_time_id)
        toggle = self.toggle.get_state()
        self.cb_handle_start = None
        self.cb_handle_finish = None
        if toggle == "on":
            self.cb_handle_start = self.adapi.run_at(self.callback,self.adapi.parse_datetime(self.start_time.get_state()))
            self.cb_handle_finish = self.adapi.run_at(self.callback,self.adapi.parse_datetime(self.finish_time.get_state()))
        self.toggle.listen_state(self.toggle_control)

        self.start_time.listen_state(self.new_start_time)
        self.finish_time.listen_state(self.new_finish_time)

        self.adapi.log(f"[{self.label}] Lamp controller init finished")
    
    def callback(self,cb_args):
        self.set_lamp_state()

        

    def toggle_control(self, entity, attribute, old, new, cb_args):

        if new == "on":
            self.adapi.log(f"[{self.label}]Lamp controller controller turned on")
            self.cb_handle_start = self.adapi.run_at(self.callback,self.adapi.parse_datetime(self.start_time.get_state()))
            self.cb_handle_finish = self.adapi.run_at(self.callback,self.adapi.parse_datetime(self.finish_time.get_state()))
            self.set_lamp_state()

        elif new == "off":
            self.adapi.cancel_timer(self.cb_handle_start)
            self.adapi.cancel_timer(self.cb_handle_finish)
            self.turn_off()

            self.adapi.log(f"[{self.label}] Lamp controller turned off")

    def new_start_time(self, entity, attribute, old, new, cb_args):
        self.cb_handle_start = self.adapi.run_at(self.callback,new)
        self.set_lamp_state()
    
    def new_finish_time(self, entity, attribute, old, new, cb_args):
        self.cb_handle_start = self.adapi.run_at(self.callback,new)
        self.set_lamp_state()        


    def should_turn_on(self,now,start,finish):
        now = now.time()
        start = start.time()
        finish = finish.time()
        print(now > start)
        print(now,start,finish)
        return (now > start and now < finish) or (now >= start and now < finish) or (now > start and now <= finish)
    
    def turn_on(self):
        ampls = [ampl.get_state() for ampl in self.amplitudes]
        [value.set_state(state = ampl) for value,ampl in zip(self.values,ampls)]
        self.adapi.log(f"[{self.label}] Turning on lamp")


    def turn_off(self):
        [value.set_state(state = 0) for value in self.values]
        self.adapi.log(f"[{self.label}] Turning off lamp")




    def set_lamp_state(self):
        now = self.adapi.get_now()
        start = self.adapi.parse_datetime(self.start_time.get_state())
        finish = self.adapi.parse_datetime(self.finish_time.get_state())
        if self.should_turn_on(now,start,finish):
            self.turn_on()
        else:
            self.turn_off()

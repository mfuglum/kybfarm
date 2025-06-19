import adbase as ad

class Lamp_control(ad.ADBase):
    """
    AppDaemon app for controlling intensity and scheduling of KYBFarm grow lamps.

    Features:
    - Turns lamps ON or OFF based on scheduled time (supports overnight ranges)
    - Copies values from user-set sliders to control channels
    - Listens to toggle and time changes in real-time

    Configuration args (from apps.yaml):
    - set_values_ids: entity_ids of user-set input_numbers for lamp intensity
    - amplitude_ids: entity_ids of actual channels controlling the lamp
    - toggle_id: input_boolean that enables/disables lamp control
    - start_time_id: input_datetime that defines lamp ON time
    - finish_time_id: input_datetime that defines lamp OFF time
    """

    def initialize(self):
        # Setup API access and log initialization
        self.adapi = self.get_ad_api()
        self.label = self.args["name"]
        self.adapi.log(f"[{self.label}] init...")

        # Get entities for set values (user sliders)
        set_values_ids = self.args["set_values_ids"]
        self.values=  [self.adapi.get_entity(id) for id in set_values_ids]

        # Get entities for actual lamp output channels
        amplitude_ids = self.args["amplitude_ids"]
        self.amplitudes = [self.adapi.get_entity(id) for id in amplitude_ids]

        # Get toggle entity (on/off switch)
        toggle_id = self.args["toggle_id"]
        self.toggle = self.adapi.get_entity(toggle_id)

        # Get time input entities
        start_time_id = self.args["start_time_id"]
        finish_time_id = self.args["finish_time_id"]
        self.start_time = self.adapi.get_entity(start_time_id)
        self.finish_time = self.adapi.get_entity(finish_time_id)

        # Prepare callback handles for scheduling
        self.cb_handle_start = None
        self.cb_handle_finish = None

        # If toggle is ON at startup, schedule start/stop callbacks
        toggle = self.toggle.get_state()
        if toggle == "on":
            self.cb_handle_start = self.adapi.run_at(self.callback, self.adapi.parse_datetime(self.start_time.get_state()))
            self.cb_handle_finish = self.adapi.run_at(self.callback, self.adapi.parse_datetime(self.finish_time.get_state()))

        # Watch for toggle and time changes
        self.toggle.listen_state(self.toggle_control)
        self.start_time.listen_state(self.new_start_time)
        self.finish_time.listen_state(self.new_finish_time)

        self.adapi.log(f"[{self.label}] Lamp controller init finished")

    def callback(self, cb_args):
        """Fires when the timer triggers — checks and sets lamp state"""
        self.set_lamp_state()

    def toggle_control(self, entity, attribute, old, new, cb_args):
        """Triggered when the ON/OFF toggle changes"""
        if new == "on":
            self.adapi.log(f"[{self.label}]Lamp controller controller turned on")
            self.cb_handle_start = self.adapi.run_at(self.callback, self.adapi.parse_datetime(self.start_time.get_state()))
            self.cb_handle_finish = self.adapi.run_at(self.callback, self.adapi.parse_datetime(self.finish_time.get_state()))
            self.set_lamp_state()
        elif new == "off":
            self.adapi.cancel_timer(self.cb_handle_start)
            self.adapi.cancel_timer(self.cb_handle_finish)
            self.turn_off()
            self.adapi.log(f"[{self.label}] Lamp controller turned off")

    def new_start_time(self, entity, attribute, old, new, cb_args):
        """Called when the start time is changed — reschedules callback"""
        self.cb_handle_start = self.adapi.run_at(self.callback, new)
        self.set_lamp_state()

    def new_finish_time(self, entity, attribute, old, new, cb_args):
        """Called when the finish time is changed — reschedules callback"""
        self.cb_handle_start = self.adapi.run_at(self.callback, new)
        self.set_lamp_state()

    def should_turn_on(self, now, start, finish):
        """Determines whether the current time is inside the lamp-on window"""
        now = now.time()
        start = start.time()
        finish = finish.time()

        # Daytime range (e.g. 08:00 to 20:00)
        if start < finish:
            return start <= now < finish
        else:
            # Overnight range (e.g. 22:00 to 06:00)
            return now >= start or now < finish

    def turn_on(self):
        """Copies the user-set values into the active lamp channels"""
        ampls = [ampl.get_state() for ampl in self.amplitudes]
        [value.set_state(state=ampl) for value, ampl in zip(self.values, ampls)]
        self.adapi.log(f"[{self.label}] Turning on lamp")

    def turn_off(self):
        """Turns off all lamp output channels (sets to 0)"""
        [value.set_state(state=0) for value in self.values]
        self.adapi.log(f"[{self.label}] Turning off lamp")

    def set_lamp_state(self):
        """Evaluates time range and toggles lamp accordingly"""
        now = self.adapi.get_now()
        start = self.adapi.parse_datetime(self.start_time.get_state())
        finish = self.adapi.parse_datetime(self.finish_time.get_state())

        if self.should_turn_on(now, start, finish):
            self.turn_on()
        else:
            self.turn_off()

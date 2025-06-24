import appdaemon.plugins.hass.hassapi as hass
from datetime import timedelta, datetime  

class MainLoop(hass.Hass):

    def initialize(self):
        self.flag_entity = self.args["flag_entity"]

        # List of scheduled task keys that will be posted sequentially to the flag
        self.tasks = [
            "spar02_gt1", "spar02_gt2", "ec_gt1", "ec_gt2", "ec_mx",
            "ph_gt1", "ph_gt2", "ph_mx", "sth01_1", "sth01_2",
            "sym01", "co2voc", "cooling_pid", "heating_pid", "co2_pid"
        ]

        self.index = 0  # Keeps track of the current position in the loop

        # Call `self.step` every 2 seconds, starting immediately
        self.run_every(self.step, datetime.now() + timedelta(seconds=0), 2.5)

    def step(self, kwargs):
        next_task = self.tasks[self.index]
        self.call_service("input_text/set_value", entity_id=self.flag_entity, value=next_task)
        self.log(f"[MainLoop] Flag set to '{next_task}'")
        self.index = (self.index + 1) % len(self.tasks)

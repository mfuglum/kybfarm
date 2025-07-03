import appdaemon.plugins.hass.hassapi as hass

class HSIScheduler(hass.Hass):

    def initialize(self):
        """Initialize: create a daily scan trigger at the selected time."""
        self.scan_time_id = self.args["scan_time_id"]

        # Get current time from input_datetime
        self.scan_time = self.get_state(self.scan_time_id)
        self.log(f"HSI Scheduler initialized — daily scan at {self.scan_time}")

        # Create the daily callback
        self.handle = self.run_daily(self.run_scan, self.parse_time(self.scan_time))

        # Listen for changes to the input_datetime so the schedule updates
        self.listen_state(self.reschedule, self.scan_time_id)

    def reschedule(self, entity, attribute, old, new, kwargs):
        """Update the daily callback if the input_datetime is changed."""
        self.log(f"HSI Scheduler time updated to {new}")

        # Cancel the old callback
        self.cancel_timer(self.handle)

        # Parse the new time and reschedule
        self.handle = self.run_daily(self.run_scan, self.parse_time(new))

    def run_scan(self, kwargs):
        """Trigger the full scan by sending an MQTT command."""
        self.log("Triggering daily HSI scan now.")

        self.call_service(
            "mqtt/publish",
            topic="cmd/gf/hs_camera/scan/req",
            payload='{"cmd":"run_scan"}'
        )

import appdaemon.plugins.hass.hassapi as hass
import json

class HSIConfigUpdate(hass.Hass):

    def initialize(self):
        """Initialize: listen for the Apply Config input_button press."""
        self.listen_event(
            self.apply_config,
            "call_service",
            domain="input_button",
            service="press",
            entity_id=self.args["apply_button_id"]
        )

    def apply_config(self, event_name, data, kwargs):
        """Triggered when the input_button is pressed."""
        self.log("Apply HSI Config button pressed — building new payload...")

        # CAMERA values
        exposure = self.get_state(self.args["camera_exposure_id"])
        gain = self.get_state(self.args["camera_gain_id"])
        blacklevel = self.get_state(self.args["camera_blacklevel_id"])

        # PRINTER values
        x_step = self.get_state(self.args["printer_x_step_id"])
        x_end = self.get_state(self.args["printer_x_end_id"])
        z_step = self.get_state(self.args["printer_z_step_id"])
        z_end = self.get_state(self.args["printer_z_end_id"])
        x_start = self.get_state(self.args["printer_x_start_id"])
        z_start = self.get_state(self.args["printer_z_start_id"])
        

        # Build config payload
        payload = {
            "cmd": "update_config",
            "config": {
                "camera": {
                    "EXPOSURE_TIME_MS": float(exposure),
                    "MASTER_GAIN": int(float(gain)),  # <-- fix here!
                    "BLACK_LEVEL": int(float(blacklevel))  # do same here if needed!
                },
                "printer": {
                    "X_STEP": float(x_step),
                    "X_END": int(float(x_end)),
                    "Z_STEP": float(z_step),
                    "Z_END": int(float(z_end))
                    "Z_START": int(float(z_start))
                    "X_START": int(float(x_start))
                }
            }
        }

        # Publish to the MQTT topic
        self.call_service(
            "mqtt/publish",
            topic="cmd/gf/hs_camera/config/req",
            payload=json.dumps(payload)
        )

        self.log(f"HSI config sent: {payload}")

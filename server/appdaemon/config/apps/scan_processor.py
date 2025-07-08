import appdaemon.plugins.hass.hassapi as hass
import subprocess

class ScanProcessor(hass.Hass):

    def initialize(self):
        self.listen_state(self.run_pipeline, self.args["scann_status_id"])
        self.listen_event(self.manual_trigger, "click", entity_id=self.args["process_button"])

    def run_pipeline(self, entity, attribute, old, new, kwargs):
        if old == "scanning" and new == "idle":
            self.log("Scan completed — running pipeline...")
            self.run_processing_steps()

    def manual_trigger(self, event_name, data, kwargs):
        self.log("Manual PROCESS HSI Data button clicked, running pipeline...")
        self.run_processing_steps()

    def run_processing_steps(self):
        band_idx = int(self.get_state(self.args["band_input"]))
        x = int(self.get_state(self.args["pixel_x_input"]))
        y = int(self.get_state(self.args["pixel_y_input"]))
        red_band = int(self.get_state(self.args["red_band_input"]))
        nir_band = int(self.get_state(self.args["nir_band_input"]))

        self.log(f"Parameters: Band={band_idx}, Pixel=({x},{y}), NDVI={red_band}/{nir_band}")

        subprocess.run(["python3", "/home/KFSpectra/server/generate_cube.py"], check=True)
        subprocess.run([
            "python3", "/home/KFSpectra/server/save_cube_plots.py",
            str(band_idx), str(x), str(y), str(red_band), str(nir_band)
        ], check=True)

        self.log("HSI pipeline done.")

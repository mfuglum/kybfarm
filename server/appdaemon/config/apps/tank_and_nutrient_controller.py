import appdaemon.plugins.hass.hassapi as hass

class TankAndNutrientControler(hass.Hass):

    def initialize(self):
        self.enable_id = self.args["enable_id"]

        self.wls01_gt1 = self.args["wls01_gt1_level_id"]
        self.wls01_gt2 = self.args["wls01_gt2_level_id"]
        self.wls01_mx = self.args["wls01_mx_level_id"]
        self.wls01_fwt = self.args["wls01_fwt_level_id"]

        self.ec_gt1 = self.args["ec_gt1_id"]
        self.ec_gt2 = self.args["ec_gt2_id"]
        self.ec_mx = self.args["ec_mx_id"]

        self.nutrient_1_ref = self.args["nutrient_1_ref_id"]

        self.mx_capacity = float(self.args["mx_capacity_liters"])
        self.gt1_capacity = float(self.args["gt1_capacity_liters"])
        self.gt2_capacity = float(self.args["gt2_capacity_liters"])

        self.peristaltic_1 = self.args["peristaltic_1_id"]
        self.peristaltic_2 = self.args["peristaltic_2_id"]
        self.peristaltic_3 = self.args["peristaltic_3_id"]

        self.flow_1 = float(self.args["peristaltic_flow_1"])
        self.flow_2 = float(self.args["peristaltic_flow_2"])
        self.flow_3 = float(self.args["peristaltic_flow_3"])

        self.solenoid_1 = self.args["solenoid_1_id"]
        self.solenoid_2 = self.args["solenoid_2_id"]
        self.water_pump_5k = self.args["water_pump_5k_id"]
        self.freshwater_valve = self.args["water_pump_350_id"]

        self.run_every(self.check_loop, "now", 60)

    def check_loop(self, kwargs):
        if self.get_state(self.enable_id) != "on":
            return

        ec_mx = float(self.get_state(self.ec_mx))
        ec_gt1 = float(self.get_state(self.ec_gt1))
        ec_gt2 = float(self.get_state(self.ec_gt2))

        ec_target = float(self.get_state(self.nutrient_1_ref)) * 1000
        ec_values = [ec_mx, ec_gt1, ec_gt2]
        ec_avg = sum(ec_values) / len(ec_values)

        if max(ec_values) - min(ec_values) > 20:
            self.log("EC mismatch detected, recirculating...")
            self.open_valves()
        else:
            self.close_valves()

        if ec_avg < ec_target - 10:
            self.log(f"EC too low ({ec_avg}), dosing...")
            self.dose_more(ec_target, ec_avg)

        # Check mixing tank level
        mx_level = float(self.get_state(self.wls01_mx))  # Assume % full
        mx_volume = mx_level / 100 * self.mx_capacity

        if mx_volume < 50:  # 50L as example threshold
            self.log("Mixing tank low, opening freshwater valve...")
            self.turn_on(self.freshwater_valve)
        else:
            self.turn_off(self.freshwater_valve)

    def open_valves(self):
        self.turn_on(self.water_pump_5k)
        self.turn_on(self.solenoid_1)
        self.turn_on(self.solenoid_2)

    def close_valves(self):
        self.turn_off(self.water_pump_5k)
        self.turn_off(self.solenoid_1)
        self.turn_off(self.solenoid_2)

    def dose_more(self, target_ec, current_ec):
        delta_ec = target_ec - current_ec
        delta_ml_per_L = delta_ec / 1000

        mx_level = float(self.get_state(self.wls01_mx))
        gt1_level = float(self.get_state(self.wls01_gt1))
        gt2_level = float(self.get_state(self.wls01_gt2))

        mx_vol = mx_level / 100 * self.mx_capacity
        gt1_vol = gt1_level / 100 * self.gt1_capacity
        gt2_vol = gt2_level / 100 * self.gt2_capacity

        total_volume = mx_vol + gt1_vol + gt2_vol
        ml_needed = delta_ml_per_L * total_volume

        run_time_1 = ml_needed / self.flow_1
        run_time_2 = ml_needed / self.flow_2
        run_time_3 = ml_needed / self.flow_3

        self.log(f"Running peristaltics: P1 {run_time_1}s, P2 {run_time_2}s, P3 {run_time_3}s")

        self.turn_on(self.peristaltic_1)
        self.turn_on(self.peristaltic_2)
        self.turn_on(self.peristaltic_3)

        self.run_in(self.stop_peristaltics, run_time_1, pump=self.peristaltic_1)
        self.run_in(self.stop_peristaltics, run_time_2, pump=self.peristaltic_2)
        self.run_in(self.stop_peristaltics, run_time_3, pump=self.peristaltic_3)

    def stop_peristaltics(self, kwargs):
        pump = kwargs["pump"]
        self.turn_off(pump)

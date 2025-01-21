



from datetime import datetime

# mixing_tank_ec_controller:
#   module: mixing_tank_ec_controller
#   class: Mixing_tank_ec_controller
#   ratio:
#     - 1.8 #dummy
#     - 1.2 #dummy
#     - 0.6 #dummy
#   flow_rates:
#     - 0.0004347
#     - 0.0003436
#     - 0.000357
#   ec_constant: 0.0034 # dummy
#   margin: 0.01 #dummy
#   ec_ref: 1 # dummy
#   tank_vol: 10
#   startup_delay: 10
#   pump_ids:
#     - "input_boolean.relay_14"
#     - "input_boolean.relay_15"
#     - "input_boolean.relay_16"
#   sensor_id: "sensor.s_ec_01_2_ec"
#   mixing_wait_time: 10






import adbase as ad
import asyncio

# Controller for mixing tank
class Mixing_tank_ec_controller(ad.ADBase):


    """
        Appdeamon App for controlling ec in mixing tank. Uses the ec reference set in HA as the target.
        The algorithm consists of:
          Calculating the required amount of time to run the nutrient pump, then running the pumps for half that time
          Current ec is measured and the time is recalculated. The algorithm repeats until the reference has been reached.

        configs:
            ratio : nutrient ratio
            ec_ref_id : HA id of ec reference
            ec_constant : empirically measured ec-volume proportionality constant
            flow_rates : flow rates of peristaltic pumps
            margin : margin of error to accept
            tank_vol : volume of mixing tank
            mixing_wait_time : time to wait between pausing peristaltic pumps and remeasuring the ec
            pump_ids : list of HA ids of peristaltic pumps
            sensor_id : HA id of mixing tank ec sensor
            mix_tank_pump_id : HA id of mixing tank circulation pump
            toggle_id : HA id for toggle turning the controller on/off



    """



    def initialize(self):
        self.adapi = self.get_ad_api()
        self.adapi.log("Mixing tank EC controller init...")

        ratio = self.args["ratio"]
        ratio_sum = sum(ratio)
        self.norm_ratio = [r_val/ratio_sum for r_val in ratio]
        
        # self.ec_ref = self.args["ec_ref"]
        ec_ref_id = self.args["ec_ref_id"]
        self.ec_ref  = self.adapi.get_entity(ec_ref_id)

        self.ec_const = self.args["ec_constant"]
        self.flow_rates = self.args["flow_rates"]
        self.margin = self.args["margin"]
        self.tank_vol = self.args["tank_vol"]
        self.mixing_wait_time = self.args["mixing_wait_time"]

        pump_ids = self.args["pump_ids"]
        self.pumps = [self.adapi.get_entity(pump_id) for pump_id in pump_ids]

        sensor_id = self.args["sensor_id"]
        self.ec_sensor = self.adapi.get_entity(sensor_id)


        mix_pump_id = self.args["mix_tank_pump_id"]
        self.mix_pump = self.adapi.get_entity(mix_pump_id)

        # self.mix_pump = self.adapi.get_entity("input_boolean.relay_2")

        toggle_id = self.args["toggle_id"]
        self.toggle= self.adapi.get_entity(toggle_id)

        toggle = self.toggle.get_state()
        self.run_in_handle = None
        self.cb_handle = None
        if toggle == "on":
            # This might never run if the mixing pump isnt on
            self.cb_handle = self.ec_sensor.listen_state(self.init_control)

        self.toggle.listen_state(self.toggle_control)
        self.grow_controller = self.adapi.get_app("grow_tank_ec_controller")
        self.is_running = False
        self.adapi.log("Mixing tank EC controller initialized!")

    @ad.global_lock
    def init_control(self, entity, attribute, old, new, cb_args):
        self.adapi.cancel_listen_state(self.cb_handle) # Might not be thread safe
        self.adapi.log("Hello from callback")
        # if self.grow_controller and getattr(self.grow_controller, "is_running", False):
        if self.grow_controller is None:
            self.adapi.log("Can't get grow controller is_running")

            self.adapi.run_in(self.reset_timer,delay = 60, random_start = 60 , random_end = 120 )
            return
        self.adapi.log(f"Grow running is {self.grow_controller.is_running}")
        if self.grow_controller.is_running:
            self.adapi.log("Grow controller running, mixing control can't run yet")
            self.adapi.run_in(self.reset_timer,delay = 60, random_start = 60 , random_end = 120 )
            return
        if self.is_running:
            self.adapi.log("Already an instance running")
            return
        self.adapi.log("helo from beyong")
        self.is_running = True

        self.mix_pump.turn_on()
        #  Need to be cancelable here
        self.run_in_handle = self.adapi.run_in(self.control,60)

    def control(self, cb_args):
        self.adapi.log("bingbong")
        ec_meas = self.ec_sensor.get_state()
        ec_meas = float(ec_meas)/1000
        self.adapi.log(ec_meas)
        if ec_meas == None:
            self.adapi.log("Error occured in mixing tank nutrient controller, can't measure EC")
            self.mix_pump.turn_off()
            self.is_running = False
            self.adapi.cancel_listen_state(self.cb_handle)
            self.adapi.run_in(self.reset_timer,300)
            return

        delta_ec = float(self.ec_ref.get_state()) - ec_meas
        if delta_ec < 0:
            self.mix_pump.turn_off()
            self.adapi.log("Mixing tank delta_ec is negative, mixing in freshwater is not yet implemented")
            self.is_running = False
            self.adapi.cancel_listen_state(self.cb_handle)
            self.adapi.run_in(self.reset_timer,300)
            return
        if abs(delta_ec) < self.margin:
            self.mix_pump.turn_off()
            self.is_running = False
            self.adapi.log("Mixing tank delta_ec is within margin, control is postponed")
            self.adapi.cancel_listen_state(self.cb_handle)
            self.adapi.run_in(self.reset_timer,300)
            return
        
        T = [0,0,0]
        for i in range(len(self.norm_ratio)):
            T[i] = self.ec_const*(delta_ec)*self.tank_vol*self.norm_ratio[i]/self.flow_rates[i]
            
        self.adapi.log(f"estimated running time: {str(max(T))}")

        T = [t/2 for t in T]
        T_max = max(T)
        for i,p in enumerate(self.pumps):
            self.adapi.log(f"Turning on pump number {i} for {T[i]} seconds")
            p.turn_on()
            self.adapi.run_in(self.turn_off_pump,delay = T[i],index = i,is_last = T[i] == T_max)



        
    def turn_off_pump(self, cb_args):
        index = cb_args["index"]
        pump = self.pumps[index]
        is_last = cb_args["is_last"]
        pump.turn_off()
        self.adapi.log(f"Turning off pump number {index}")
        
        if is_last:
            self.run_in_handle = self.adapi.run_in(self.control,self.mixing_wait_time)

            self.adapi.log(f"Waiting for ec to stabilize for {str(self.mixing_wait_time)}, seconds")





    def toggle_control(self, entity, attribute, old, new, cb_args):

        if new == "on":
            self.cb_handle = self.ec_sensor.listen_state(self.init_control)
            self.adapi.log("Mixing tank controller turned on")
        elif new == "off":
            self.adapi.cancel_listen_state(self.cb_handle)
            for pump in self.pumps:
                pump.turn_off()
            self.adapi.log(self.grow_controller.is_running)
            if self.grow_controller and not self.grow_controller.is_running:
                self.mix_pump.turn_off()
            self.is_running = False
            self.adapi.cancel_timer(self.run_in_handle)
            self.adapi.log("Mixing tank controller turned off")


    def reset_timer(self,cb_args):
        toggle = self.toggle.get_state()

        if toggle == "on":
            self.cb_handle = self.ec_sensor.listen_state(self.init_control)
        elif toggle == "off":
            self.adapi.cancel_listen_state(self.cb_handle)


    def terminate(self):
        self.adapi.log("Terminate")
        if not self.grow_controller or not getattr(self.grow_controller, "is_running", False):
            self.mix_pump.turn_off()
        for pump in self.pumps:
            pump.turn_off()
        self.is_running = False





    
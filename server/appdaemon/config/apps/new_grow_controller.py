import adbase as ad
import time
from datetime import datetime



# growth_tank_ec_controller:
#   module: grow
#   class: Grow_tank_ec_controller
#   flow_rate: 0.0486111  # l/s (estimate)
#   vol_mix_tank: 350
#   vol_growth_tank: 100
#   epsilon: 0.05
#   ec_growth: "sensor.s_ec_01_1_ec"
#   ec_mix: "sensor.s_ec_01_2_ec"
#   startup_delay: "0"
#   solenoid_id: "input_boolean.relay_11"
#   n_tau: 4
#   tau: 80 #s
#   max_run_time: 120
#   drain_time: 300





# Ec controller for grow tanks
class Grow_tank_ec_controller(ad.ADBase):



    """
        Appdeamon App for controlling the EC in a single grow tank, run two instances for two tanks.
        This controller just circulates the water from the mixing tank into the growing tank on a regular interval.

        Also estimates time constants and steady state value, however these are just logged and not actually used.

        configs:
            flow rate : flow rate in and out of grow tank, assumed to be identical for both input and output.
            vol_growth_tank : volume of the grow tank.
            vol_mix_tank : volume of the mixing tank.
            grow_tank_ec_sensor_id : HA id of the grow tank ec sensor.
            mix_tank_ec_sensor_id : HA id of the mixing tank ec sensor.
            solenoid_id : HA id of the input solenoid.
            tau : measured time constant of the system.
            n_tau : number of time constants to run circulation for.
            mix_tank_pump_id : HA id of mixing tank pump.
            max_run_time : maximum amount of time where the grow tank can be allowed to fill at a time,
                            this is to reduce the chance of overflow.
            draining_time : amount of time to wait between fillings. This gives time for the tank level to fall.
            toggle_id : HA id of toggle button for turning controller on/off.
            reset_time : time to wait before starting a new control session.
        

    """

    def initialize(self):
        self.adapi = self.get_ad_api()
        self.adapi.log("Grow tank EC controller init...")
        self.Fr = self.args["flow_rate"]
        self.V1 = self.args["vol_growth_tank"]
        self.V2 = self.args["vol_mix_tank"]
       # self.eps = self.args["epsilon"]

        sensor_id = self.args["grow_tank_ec_sensor_id"]
        self.ec_grow = self.adapi.get_entity(sensor_id)
        sensor_id = self.args["mix_tank_ec_sensor_id"]
        self.ec_mix = self.adapi.get_entity(sensor_id)

        acutator_id = self.args["solenoid_id"]
        self.solenoid = self.adapi.get_entity(acutator_id)

        self.n_tau = self.args["n_tau"]
        self.tau = self.time_constant(self.Fr,self.V1,self.V2)
        self.tau = self.args["tau"]
        self.adapi.log(f"time constant is {self.tau}")
        mix_pump_id = self.args["mix_tank_pump_id"]
        self.mix_pump = self.adapi.get_entity(mix_pump_id)

        # self.mix_pump = self.adapi.get_entity("input_boolean.relay_2")

        
        self.max_run_time = self.args["max_run_time"]
        self.drain_time = self.args["drain_time"]


        self.is_running = False
        toggle_id = self.args["toggle_id"]
        self.toggle = self.adapi.get_entity(toggle_id)

        self.run_in_handle = None

        self.cb_handle = None
        if self.toggle.get_state() == "on":
            self.cb_handle = self.ec_grow.listen_state(self.init_control)

        self.toggle.listen_state(self.toggle_control)

        self.mix_controller = self.adapi.get_app('mixing_tank_ec_controller')

        self.reset_time = self.args["reset_time"]

        # self.adapi.run_once(self.callback,start = "now")
        self.adapi.log("Grow tank EC controller init finished")  

    @ad.global_lock
    def init_control(self, entity, attribute, old, new, cb_args):
        self.adapi.cancel_listen_state(self.cb_handle)
        self.adapi.log("Hello from callback")
        # if self.mix_controller and getattr(self.mix_controller, "is_running", False):
        if self.mix_controller and self.mix_controller.is_running:
            self.adapi.log("Mixing control running, grow control can run yet")
            self.adapi.run_in(self.reset_timer, delay = 60, random_start = 60 , random_end = 120 )
            return
        if self.is_running:
            self.adapi.log("Already an instance running")
            return
        self.adapi.log("helo from beyong")
        self.is_running = True

        self.mix_pump.turn_on()

        self.run_in_handle = self.adapi.run_in(self.control,60)


    def control(self, cb_args):

        if "remaining" not in cb_args:
            remaining = self.n_tau*self.tau
        else:
            remaining = cb_args["remaining"]

        if remaining <= 0:
            self.adapi.log("Grow tank control ended")
            self.mix_pump.turn_off()
            self.is_running = False
            # Error here, need to 
            self.adapi.run_in(self.reset_timer,delay = self.reset_time)
            return
        
        self.adapi.log(f"Running growth tank control for {remaining} seconds")
        run_time = min(remaining,self.max_run_time)
        remaining = remaining - run_time
        self.adapi.log(f"Turning on for {run_time}")
        self.solenoid.turn_on()
        self.adapi.run_in(self.drain, delay = run_time, remaining = remaining )




    def drain(self,cb_args):
        self.solenoid.turn_off()
        remaining = cb_args["remaining"]
        self.adapi.log(f"Draining tank for {self.drain_time} seconds")
        self.run_in_handle = self.adapi.run_in(self.control,delay = self.drain_time,remaining = remaining ) 




    def reset_timer(self,cb_args):
        toggle = self.toggle.get_state()

        if toggle == "on":
            self.cb_handle = self.ec_grow.listen_state(self.init_control)
        elif toggle == "off":
            self.adapi.cancel_listen_state(self.cb_handle)
            



    def toggle_control(self, entity, attribute, old, new, cb_args):

        if new == "on":
            self.cb_handle = self.ec_grow.listen_state(self.init_control)
            self.adapi.log("Grow tank controller turned on")
        elif new == "off":
            self.adapi.cancel_listen_state(self.cb_handle)
            self.adapi.log(self.mix_controller.is_running)
            if self.mix_controller and  not self.mix_controller.is_running:
                self.mix_pump.turn_off()
            self.solenoid.turn_off()
            self.is_running = False
            self.adapi.cancel_timer(self.run_in_handle)
            self.adapi.log("Grow tank controller turned off")


    def time_constant(self,Fr,V1,V2):
        alpha1 = Fr/V1
        alpha2 = Fr/V2

        return 1/(alpha1+alpha2)

    # def x_10(self,eps,V1,V2,x_20):
    #     return (x_20*(1-V2/(V1+V2))-eps)*(V2+V1)/V1

    def ss(self,V1,V2,x10,x20):
        return V1/(V2+V1)*x10 + V2/(V1+V2)*x20
    

    def terminate(self):
        self.adapi.log("Terminate")
        if not self.mix_controller or not getattr(self.mix_controller, "is_running", False):
            self.mix_pump.turn_off()
        self.solenoid.turn_off()
        self.is_running = False



        
        # self.ec_ref = self.args["ec_ref"]
        # self.flow_rate = self.args["flow_rate"]
        # self.margin = self.args["margin"]
        # self.tank_vol = self.args["tank_vol"]


        # pump_id = self.args["pump_id"]
        # self.pump = self.adapi.get_entity(pump_id)

        # level_sensor_id = self.args["level_sensor_id"]
        # self.level_sensor = self.adapi.get_entity(level_sensor_id)

        # sensor_id = self.args["sensor_id"]
        # self.ec_sensor = self.adapi.get_entity(sensor_id)

        # startup_delay = self.args["startup_delay"]
        # self.adapi.run_every(self.callback ,"now" + startup_delay, 60*60*12)
        # self.log("Grow tank EC controller initialized!")

        
        # def callback(self,cb_args):


        #     level_meas = self.level_sensor.get_state()
        #     if level_meas.state == "off":
        #         self.log("Growing tank is not full, ec control will not run")
        #         return
        #     ec_meas = self.ec_sensor.get_state(attribute = "ec")

        #     if ec_meas == None:
        #         self.log("Error occured in grow tank nutrient controller, can't measure EC")
        #         return

        #     delta_ec = self.ec_ref - ec_meas
        #     if delta_ec < 0:
        #         self.log("Grow tank delta_ec is negative, can't produce negative input")
        #         return
        #     if abs(delta_ec) < self.margin:
        #         self.log("Mixing tank delta_ec is within margin, control is postponed")
        #         return

        #     self.log("delta_ec larger than margin, initiating control...")
        #     while delta_ec > self.margin:
        #         self.log("Turning on pump")
        #         self.pump.turn_on()
        #         time.sleep(0.1)
        #         ec_meas = self.ec_sensor.get_state(attribute = "ec")

        #         if ec_meas == None:
        #             self.log("Error occured in grow tank nutrient controller, can't measure EC")
        #             self.log("Turning of pump")
        #             self.pump.turn_off()
        #             return
        #         delta_ec = self.ec_ref - ec_meas
        #     self.log("delta_ec within margi, turning off pump")
        #     self.pump.turn_off()


            


        




    

    
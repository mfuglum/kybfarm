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
    def initialize(self):
        self.adapi = self.get_ad_api()
        self.adapi.log("Grow tank EC controller init...")
        self.Fr = self.args["flow_rate"]
        self.V1 = self.args["vol_growth_tank"]
        self.V2 = self.args["vol_mix_tank"]
        self.eps = self.args["epsilon"]

        sensor_id = self.args["ec_growth"]
        self.ec_growth = self.adapi.get_entity(sensor_id)
        sensor_id = self.args["ec_mix"]
        self.ec_mix = self.adapi.get_entity(sensor_id)

        acutator_id = self.args["solenoid_id"]
        self.solenoid = self.adapi.get_entity(acutator_id)

        self.n_tau = self.args["n_tau"]
        self.tau = self.time_constant(self.Fr,self.V1,self.V2)
        self.tau = self.args["tau"]
        self.adapi.log(f"time constant is {self.tau}")
        self.mix_pump = self.adapi.get_entity("input_boolean.relay_2")

        
        startup_delay = self.args["startup_delay"]
        self.max_run_time = self.args["max_run_time"]
        self.drain_time = self.args["drain_time"]
        self.adapi.log(f"Startup delay is {startup_delay}")
        # self.adapi.run_every(self.callback ,"now", 60*60*12)
        # self.adapi.run_at(self.callback,"12:00:00")
        datetime_object = datetime(2024, 10, 24, 12, 00, 00)

        self.adapi.run_every(self.callback,datetime_object,60*60*2)

        # self.adapi.run_once(self.callback,start = "now")
        self.adapi.log("Grow tank EC controller init finished")


    def callback(self,cb_args):
        # growth_meas = int(self.ec_growth.get_state())
        # self.adapi.log(f" grow tank ec is {growth_meas}")

        # mix_meas = int(self.ec_mix.get_state())
        # x_10 = self.x_10(self.eps,self.V1,self.V2,mix_meas)
        # self.adapi.log(f"Min needed Ec is {x_10}")
        # self.adapi.log(f"Steady state estimated to {self.ss(self.V1,self.V2,mix_meas,growth_meas)}")
        # if x_10 < growth_meas:

        #     return
        self.mix_pump.turn_on()
        time.sleep(60)
        remaining = self.n_tau*self.tau
        self.adapi.log(f"Running growth tank control for {remaining} seconds")
        while remaining > 0:

            run_time = min(remaining,self.max_run_time)
            self.adapi.log(f"Turning on for {run_time}")
            self.solenoid.turn_on()
            time.sleep(run_time)
            self.solenoid.turn_off()
            self.adapi.log(f"turning off for {self.drain_time}")
            time.sleep(self.drain_time)
            remaining = remaining - run_time
            self.adapi.log(f"Remaining time is {remaining}")
        self.adapi.log("Grow tank control ended")
        self.mix_pump.turn_off()


        


    def time_constant(self,Fr,V1,V2):
        alpha1 = Fr/V1
        alpha2 = Fr/V2

        return 1/(alpha1+alpha2)

    def x_10(self,eps,V1,V2,x_20):
        return (x_20*(1-V2/(V1+V2))-eps)*(V2+V1)/V1

    def ss(self,V1,V2,x10,x20):
        return V1/(V2+V1)*x10 + V2/(V1+V2)*x20


        
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


            


        




    

    
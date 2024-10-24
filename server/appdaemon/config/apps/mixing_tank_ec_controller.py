



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
    def initialize(self):
        self.adapi = self.get_ad_api()
        self.adapi.log("Mixing tank EC controller init...")

        ratio = self.args["ratio"]
        ratio_sum = sum(ratio)
        self.norm_ratio = [r_val/ratio_sum for r_val in ratio]
        
        self.ec_ref = self.args["ec_ref"]
        self.ec_const = self.args["ec_constant"]
        self.flow_rates = self.args["flow_rates"]
        self.margin = self.args["margin"]
        self.tank_vol = self.args["tank_vol"]
        self.mixing_wait_time = self.args["mixing_wait_time"]

        pump_ids = self.args["pump_ids"]
        self.pumps = [self.adapi.get_entity(pump_id) for pump_id in pump_ids]

        # self.p_pump_1 = self.adapi.get_entity("input_boolean.relay_14")
        # self.p_pump_2 = self.adapi.get_entity("input_boolean.relay_15")
        # self.p_pump_3 = self.adapi.get_entity("input_boolean.relay_16")
        sensor_id = self.args["sensor_id"]
        self.ec_sensor = self.adapi.get_entity(sensor_id)


        self.mix_pump = self.adapi.get_entity("input_boolean.relay_2")
        startup_delay = str(self.args["startup_delay"])
        self.adapi.log(f"startup_delay is {startup_delay}")
        # self.adapi.run_every(self.callback_feedback ,"now" + startup_delay, 60*60*24)
        # self.adapi.run_at(self.callback_feedback,"10:46:00")
        datetime_object = datetime(2024, 10, 24, 11, 00, 00)

        self.adapi.run_every(self.callback_feedback,datetime_object,60*60*2)
        self.ec_sensor.listen_state(self.check_overflow, attribute = "ec") # need to change polling rate in home assistent
        self.adapi.log("Mixing tank EC controller initialized!")

        
    async def callback_feedforward(self,cb_args):
        self.mix_pump.turn_on()
        await asyncio.sleep(60)
        ec_meas = self.ec_sensor.get_state()
        await ec_meas
        ec_meas = float(ec_meas.result())/1000
        self.adapi.log(ec_meas)
        if ec_meas == None:
            self.adapi.log("Error occured in mixing tank nutrient controller, can't measure EC")
            self.mix_pump.turn_off()
            return

        delta_ec = self.ec_ref - ec_meas
        if delta_ec < 0:
            self.mix_pump.turn_off()
            self.adapi.log("Mixing tank delta_ec is negative, mixing in freshwater is not yet implemented")
            return
        if abs(delta_ec) < self.margin:
            self.mix_pump.turn_off()
            self.adapi.log("Mixing tank delta_ec is within margin, control is postponed")
            return


        T = [0,0,0]
        for i in range(len(self.norm_ratio)):
            T[i] = self.ec_const*(self.ec_ref-ec_meas)*self.tank_vol*self.norm_ratio[i]/self.flow_rates[i]
            
        self.adapi.log(f"estimated running time: {str(max(T))}")
        # await asyncio.gather([self.run_for(i,T[i]) for i in range(len(T))])
        await asyncio.gather(*(self.run_for(i, T[i]) for i in range(len(T))))
        # async with asyncio.TaskGroup() as tg:
        #     for i in range(len(T)):
        #         tg.create_task(
        #             self.run_for(i,T[i])
        #         )
        

    async def callback_feedback(self,cb_args):
        self.mix_pump.turn_on()
        await asyncio.sleep(60)
        delta_ec = self.margin + 1 
        while delta_ec > self.margin:
            ec_meas = self.ec_sensor.get_state()
            await ec_meas
            ec_meas = float(ec_meas.result())/1000
            self.adapi.log(ec_meas)
            if ec_meas == None:
                self.adapi.log("Error occured in mixing tank nutrient controller, can't measure EC")
                self.mix_pump.turn_off()

                return

            delta_ec = self.ec_ref - ec_meas
            self.adapi.log(f"delta_ec is {str(delta_ec)}")
            if delta_ec < 0:
                self.mix_pump.turn_off()
                self.adapi.log("Mixing tank delta_ec is negative, mixing in freshwater is not yet implemented")
                return
            if abs(delta_ec) < self.margin:
                self.mix_pump.turn_off()
                self.adapi.log("Mixing tank delta_ec is within margin, control is postponed")
                return


            T = [0,0,0]
            for i in range(len(self.norm_ratio)):
                T[i] = self.ec_const*(self.ec_ref-ec_meas)*self.tank_vol*self.norm_ratio[i]/self.flow_rates[i]

            # T = [
            #     self.ec_const*(self.ec_ref-ec_meas)*self.tank_vol*self.norm_ratio[i]/self.flow_rates[i]
            #     for i,_ in self.norm_ratio
            # ]

            self.adapi.log(f"estimated running time: {max(T)}")
            T = [t/2 for t in T]

                

            await asyncio.gather(*(self.run_for(i, T[i]) for i in range(len(T))))
            self.adapi.log(f"Waiting for ec to stabilize for {str(self.mixing_wait_time)}, seconds")
            await asyncio.sleep(self.mixing_wait_time)



    async def run_for(self,pump_num,time):
        self.adapi.log(f"Turning on pump number {str(pump_num)}")
        self.pumps[pump_num].turn_on()

        await asyncio.sleep(time)

        self.adapi.log(f"Turning off pump number {str(pump_num)}")
        self.pumps[pump_num].turn_off() 
    
    
    def check_overflow(self,entity, attribute, old, new, cb_args):
        ec_meas = self.ec_sensor.get_state(attribute = "ec")
        if ec_meas < self.ec_ref:
            return
        
        pumps_running = [pump.get_state() for pump in self.pumps]

        if not any(pumps_running):
            return
        
        self.adapi.log("Pumps are running but ec_ref already reached, turning off")

        for pump in self.pumps:
            pump.turn_off()

        

        # T = (self.ec_ref-ec_meas)*self.ec_const*self.tank_vol/*self.flow_rate)
        # T_1 = self.ratio[0]/self.ratio_sum * T
        # T_2 = self.ratio[1]/self.ratio_sum * T
        # T_3 = self.ratio[2]/self.ratio_sum * T

        # Run pumps for given time
        # Should just allow EC to overshoot a little bit instead of 
        # stopping because it would ruin the ratio
        # Can just try to have a very low flow rate instead

# Feedback?
# Don't use it, its written by chatgpt and doesnt work because it assumes all running times are the same
# Need to edit s.t e.g it runs for half of the recommended time and then check and sets new
# T = T/2
# Run for
# Check again
async def control_pumps_feedback(self, delta_ec):
        # Run the pumps in feedback loop
        pump_increment = 2  # Run pumps for 2 seconds, then check EC again

        while delta_ec > self.margin:
            await asyncio.sleep(pump_increment)  # Sleep for incremental time

            mixing_wait = 3

            for pump_num, pump in enumerate(self.pumps):
                self.adapi.log(f"Turning off pump {pump_num}")
                pump.turn_off()

            await asyncio.sleep(mixing_wait)

            # Check EC value again
            ec_meas = await self.ec_sensor.get_state()
            ec_meas = float(ec_meas) / 1000
            delta_ec = self.ec_ref - ec_meas
            self.adapi.log(f"EC measurement: {ec_meas}, delta_ec: {delta_ec}")
            # Wait for ec to stabilize

            if delta_ec <= self.margin:
                self.adapi.log("EC is within margin, stopping pumps.")
                break

        for pump_num, pump in enumerate(self.pumps):
            self.adapi.log(f"Turning off pump {pump_num}")
            pump.turn_off()


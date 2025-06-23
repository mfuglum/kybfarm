import adbase as ad
from datetime import datetime, timedelta

class Lamp_control(ad.ADBase):
    """
    AppDaemon app for controlling intensity and scheduling of KYBFarm grow lamps with smooth dawn/dusk simulation.
    """

    def initialize(self):
        self.adapi = self.get_ad_api()
        self.label = self.args["name"]
        self.adapi.log(f"[{self.label}] init...")

        self.values = [self.adapi.get_entity(id) for id in self.args["set_values_ids"]]
        self.amplitudes = [self.adapi.get_entity(id) for id in self.args["amplitude_ids"]]
        self.dawns = [self.adapi.get_entity(id) for id in self.args["dawn_durations_ids"]]
        self.dusks = [self.adapi.get_entity(id) for id in self.args["dusk_durations_ids"]]
        self.toggle = self.adapi.get_entity(self.args["toggle_id"])
        self.start_time = self.adapi.get_entity(self.args["start_time_id"])
        self.finish_time = self.adapi.get_entity(self.args["finish_time_id"])

        self.cb_handle_step = None

        if self.toggle.get_state() == "on":
            self.cb_handle_step = self.adapi.run_every(self.update_ramp, datetime.now() + timedelta(seconds=1), 60)
            self.adapi.log(f"[{self.label}] Scheduled update_ramp every 60s")

        self.toggle.listen_state(self.toggle_control)
        self.start_time.listen_state(self.schedule_ramping)
        self.finish_time.listen_state(self.schedule_ramping)

        self.adapi.log(f"[{self.label}] Lamp controller init finished")

    def toggle_control(self, entity, attribute, old, new, cb_args):
        if new == "on":
            self.adapi.log(f"[{self.label}] Lamp controller turned ON")
            if self.cb_handle_step:
                self.adapi.cancel_timer(self.cb_handle_step)

            self.cb_handle_step = self.adapi.run_every(self.update_ramp, datetime.now() + timedelta(seconds=1), 60)
            self.adapi.log(f"[{self.label}] Scheduled update_ramp every 60s (toggle ON)")

            try:
                self.update_ramp({})
            except Exception as e:
                self.adapi.log(f"[{self.label}] ERROR during initial update_ramp: {str(e)}", level="ERROR")
        else:
            if self.cb_handle_step:
                self.adapi.cancel_timer(self.cb_handle_step)
            self.turn_off()
            self.adapi.log(f"[{self.label}] Lamp controller turned OFF")

    def schedule_ramping(self, entity, attribute, old, new, cb_args):
        try:
            self.update_ramp(cb_args)
        except Exception as e:
            self.adapi.log(f"[{self.label}] ERROR in schedule_ramping: {str(e)}", level="ERROR")

    def update_ramp(self, cb_args):
        try:
            now = datetime.now().astimezone()

            start = self._parse_time(self.start_time.get_state())
            finish = self._parse_time(self.finish_time.get_state())

            if self.toggle.get_state() != "on":
                self.turn_off()
                return

            if self.is_within_lighting_period(now, start, finish):
                values = []
                for i, (val_ent, dawn_ent, dusk_ent) in enumerate(zip(self.values, self.dawns, self.dusks)):
                    try:
                        target = float(val_ent.get_state())
                        dawn = int(float(dawn_ent.get_state()))
                        dusk = int(float(dusk_ent.get_state()))

                        gain = self.calculate_gain(now, start, finish, dawn, dusk)
                        ramped_value = round(target * gain)
                        values.append(ramped_value)
                        self.adapi.log(f"[{self.label}] Channel {i}: gain={gain:.2f}, target={target}, ramped={ramped_value}")
                    except Exception as e:
                        self.adapi.log(f"[{self.label}] ERROR in channel {i} gain calc: {str(e)}", level="ERROR")

                for amp, val in zip(self.amplitudes, values):
                    amp.set_state(state=val)

                self.adapi.log(f"[{self.label}] Ramping values: {values}")
            else:
                self.turn_off()
        except Exception as e:
            self.adapi.log(f"[{self.label}] ERROR in update_ramp: {str(e)}", level="ERROR")

    def is_within_lighting_period(self, now, start, finish):
        now_time = now.time()
        start_time = start.time()
        finish_time = finish.time()
        if start_time < finish_time:
            return start_time <= now_time < finish_time
        else:
            return now_time >= start_time or now_time < finish_time

    def calculate_gain(self, now, start, finish, dawn, dusk):
        minutes_since_start = self.time_difference_minutes(start, now)
        minutes_until_end = self.time_difference_minutes(now, finish)

        if dawn > 0 and minutes_since_start < dawn:
            return max(0.0, min(1.0, minutes_since_start / dawn))
        elif dusk > 0 and minutes_until_end < dusk:
            return max(0.0, min(1.0, minutes_until_end / dusk))
        else:
            return 1.0

    def time_difference_minutes(self, earlier, later):
        if later < earlier:
            later += timedelta(days=1)
        return (later - earlier).total_seconds() / 60

    def _parse_time(self, raw):
        try:
            if isinstance(raw, str):
                # If it's a time-only string like '15:03:00', combine with today
                if len(raw) == 8 and raw.count(":") == 2:
                    today = datetime.now().astimezone().date()
                    raw = f"{today}T{raw}"
                parsed = datetime.fromisoformat(raw)
            else:
                parsed = raw
            return parsed.astimezone()
        except Exception as e:
            self.adapi.log(f"[{self.label}] ERROR in _parse_time: {e}", level="ERROR")
            return datetime.now().astimezone()


    def turn_off(self):
        for amp in self.amplitudes:
            amp.set_state(state=0)
        self.adapi.log(f"[{self.label}] Turning off lamp")

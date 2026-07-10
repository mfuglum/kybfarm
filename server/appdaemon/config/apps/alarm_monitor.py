import appdaemon.plugins.hass.hassapi as hass
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta


class AlarmMonitor(hass.Hass):

    def initialize(self):
        self._smtp_host = self.args["smtp_host"]
        self._smtp_port = int(self.args["smtp_port"])
        self._smtp_user = self.args["smtp_user"]
        self._smtp_pass = self.args["smtp_pass"]
        self._recipient  = self.args["recipient"]
        self._cooldown   = timedelta(hours=int(self.args.get("cooldown_hours", 1)))
        self._last_sent  = {}

        alarms = [
            {
                "entity": self.args["entity_temperature"],
                "key":    "temperature",
                "label":  "Temperature (CO2-VOC Sensor 1)",
                "unit":   "C",
                "lo":     16.0,
                "hi":     25.0,
            },
            {
                "entity": self.args["entity_co2"],
                "key":    "co2",
                "label":  "CO2 (CO2-VOC Sensor 2)",
                "unit":   "ppm",
                "lo":     None,
                "hi":     1500.0,
            },
            {
                "entity": self.args["entity_ph_mx"],
                "key":    "ph_mx",
                "label":  "pH (Mixing Tank)",
                "unit":   "pH",
                "lo":     4.0,
                "hi":     9.0,
            },
        ]

        water_entities = self.args.get("entities_water_level", [])
        for idx, entity in enumerate(water_entities, start=1):
            alarms.append({
                "entity": entity,
                "key":    f"water_level_tank{idx}",
                "label":  f"Water Level Tank {idx}",
                "unit":   "cm",
                "lo":     15.0,
                "hi":     29.0,
            })

        for alarm in alarms:
            self.listen_state(self._on_state_change, alarm["entity"], alarm=alarm)
            self.log(f"AlarmMonitor: registered [{alarm['label']}] on {alarm['entity']}")

    def _on_state_change(self, entity, attribute, old, new, kwargs):
        alarm = kwargs["alarm"]
        try:
            value = float(new)
        except (ValueError, TypeError):
            return

        lo = alarm["lo"]
        hi = alarm["hi"]
        triggered = (lo is not None and value < lo) or (hi is not None and value > hi)

        if triggered:
            self._maybe_send(alarm, value)

    def _maybe_send(self, alarm, value):
        key  = alarm["key"]
        now  = datetime.now()
        last = self._last_sent.get(key)
        if last and (now - last) < self._cooldown:
            return
        self._last_sent[key] = now
        self._send_email(alarm, value)

    def _send_email(self, alarm, value):
        subject = f"[AgriBot Alarm] {alarm['label']} out of range"
        body = (
            f"AgriBot alarm triggered.\n\n"
            f"Parameter : {alarm['label']}\n"
            f"Value     : {value} {alarm['unit']}\n"
            f"Timestamp : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        msg            = MIMEText(body)
        msg["Subject"] = subject
        msg["From"]    = self._smtp_user
        msg["To"]      = self._recipient

        try:
            with smtplib.SMTP_SSL(self._smtp_host, self._smtp_port) as server:
                server.login(self._smtp_user, self._smtp_pass)
                server.sendmail(self._smtp_user, [self._recipient], msg.as_string())
            self.log(
                f"AlarmMonitor: alert sent for {alarm['label']} = {value} {alarm['unit']}"
            )
        except Exception as exc:
            self.log(
                f"AlarmMonitor: email FAILED for {alarm['label']}: {exc}",
                level="ERROR",
            )

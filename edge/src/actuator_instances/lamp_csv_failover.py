"""Edge-side autonomous lamp schedule failover for chamber 1.

Daemon thread started by edge_computer_main.py. PASSIVE while the MQTT broker
(co-located with the server) is reachable. TAKES OVER only when the broker
connection is lost beyond a grace period AND adaptive mode was last known armed
via the retained cfg/lamp01/adaptive_mode flag. Reuses the already-initialized
lamp_1 object and calls set_channel_intensities with the same 450:660:735:5700
string device_control.yaml builds.

Tied to the main process: dies when edge_computer_main.py exits.
"""

import csv
import os
import threading
import time
from datetime import date, datetime

import paho.mqtt.client as mqtt

# CSV columns in the SAME order device_control.yaml builds the string:
# 450 : 660 : 735 : 5700k
CHANNEL_COLUMNS = ["450nm", "660nm", "735nm", "5700nm"]
SLOT_MINUTES = 15
SLOTS_PER_DAY = 96


class LampCsvFailover:
    def __init__(
        self,
        lamp,                            # the already-initialized lamp_1 object
        broker_ip,
        csv_dir,
        start_date,                      # datetime.date of GROW DAY 14
        broker_port=1883,
        first_day=14,
        last_day=21,
        csv_file="20260423_optimal_daily_dli.csv",
        adaptive_topic="cfg/lamp01/adaptive_mode",
        grace_seconds=120,
        check_interval_seconds=60,
        username=None,
        password=None,
        armed_cache_file=None,
        log=print,
    ):
        self.lamp = lamp
        self.broker_ip = broker_ip
        self.broker_port = broker_port
        self.csv_dir = csv_dir
        self.start_date = start_date
        self.first_day = first_day
        self.last_day = last_day
        self.csv_file = csv_file
        self.adaptive_topic = adaptive_topic
        self.grace_seconds = grace_seconds
        self.check_interval_seconds = check_interval_seconds
        self.log = log
        self.armed_cache_file = armed_cache_file or os.path.join(
            csv_dir, ".adaptive_armed"
        )

        self.connected = False
        self.disconnected_since = time.monotonic()  # assume down until connected
        self.armed = self._load_armed_cache()       # survives edge reboot mid-outage
        self.active = False
        self.last_applied_slot = None
        self._stop = threading.Event()

        self.client = mqtt.Client(client_id="edge_lamp1_failover")
        if username:
            self.client.username_pw_set(username, password)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

    # ---------------- arming-state persistence ---------------- #
    def _load_armed_cache(self):
        try:
            with open(self.armed_cache_file) as fh:
                return fh.read().strip() == "on"
        except OSError:
            return False  # safe default: stay passive until told otherwise

    def _save_armed_cache(self):
        try:
            with open(self.armed_cache_file, "w") as fh:
                fh.write("on" if self.armed else "off")
        except OSError as exc:
            self.log(f"[failover] Could not write armed cache: {exc}")

    # ---------------- MQTT callbacks (network thread) ---------------- #
    def _on_connect(self, client, userdata, flags, rc):
        self.connected = (rc == 0)
        if self.connected:
            client.subscribe(self.adaptive_topic)  # retained -> last value arrives
            self.log(f"[failover] Connected to broker {self.broker_ip}.")

    def _on_disconnect(self, client, userdata, rc):
        self.connected = False
        self.disconnected_since = time.monotonic()
        self.log(f"[failover] Disconnected from broker (rc={rc}).")

    def _on_message(self, client, userdata, msg):
        if msg.topic == self.adaptive_topic:
            payload = msg.payload.decode(errors="ignore").strip().lower()
            new_armed = payload == "on"
            if new_armed != self.armed:
                self.armed = new_armed
                self._save_armed_cache()
                self.log(f"[failover] Adaptive mode armed={self.armed}.")

    # ---------------- schedule logic ---------------- #
    def _current_day_index(self):
        elapsed = (date.today() - self.start_date).days
        idx = self.first_day + max(elapsed, 0)
        return min(idx, self.last_day)

    def _load_day_file(self, day_index):
        # Combined file: 96-row blocks in grow-day order (day 1 = first block),
        # so grow day N is rows [(N-1)*96 : N*96]. Verified against the per-day
        # extracts. If the file is regenerated, keep this layout or the positional
        # slice will read the wrong day.
        path = os.path.join(self.csv_dir, self.csv_file)
        with open(path, newline="") as fh:
            all_rows = list(csv.DictReader(fh, delimiter=";"))
        start = (day_index - 1) * SLOTS_PER_DAY
        block = all_rows[start:start + SLOTS_PER_DAY]
        if len(block) < SLOTS_PER_DAY:
            raise ValueError(
                f"combined CSV lacks a full block for grow day {day_index} "
                f"(have {len(all_rows)} rows)"
            )
        if block[0]["Lamp timestamp"].strip() != "00:00":
            raise ValueError(
                f"combined CSV block for grow day {day_index} does not start at 00:00"
            )
        return {r["Lamp timestamp"].strip(): r for r in block}

    def _current_slot_key(self):
        now = datetime.now()
        floored = now.replace(
            minute=(now.minute // SLOT_MINUTES) * SLOT_MINUTES,
            second=0, microsecond=0,
        )
        return floored.strftime("%H:%M")

    def _apply_slot(self, slot_key):
        day_index = self._current_day_index()
        try:
            rows = self._load_day_file(day_index)
        except OSError as exc:
            self.log(f"[failover] CSV read error: {exc}")
            return
        row = rows.get(slot_key)
        if row is None:  # defensive; current files have all 96 slots
            return
        try:
            parts = [str(int(round(float(row[c])))) for c in CHANNEL_COLUMNS]
        except (KeyError, ValueError) as exc:
            self.log(f"[failover] Bad CSV value at {slot_key}: {exc}")
            return
        intensity = ":".join(parts)  # 450:660:735:5700, matches device_control.yaml
        result = self.lamp.set_channel_intensities(intensity)
        if isinstance(result, Exception):
            self.log(f"[failover] Lamp HTTP error for {intensity}: {result}")
            return
        self.last_applied_slot = slot_key
        self.log(f"[failover] APPLIED day {day_index} slot {slot_key}: {intensity}")

    # ---------------- lifecycle ---------------- #
    def start(self):
        if not getattr(self.lamp, "ip_address", ""):
            self.log("[failover] WARNING: lamp IP is empty; start after the main "
                     "script updates lamp_1's IP.")
        self.client.connect_async(self.broker_ip, self.broker_port, keepalive=60)
        self.client.loop_start()
        threading.Thread(target=self._run, daemon=True).start()
        self.log("[failover] Started. Passive while broker is reachable.")

    def stop(self):
        self._stop.set()
        self.client.loop_stop()
        self.client.disconnect()

    def _server_reachable(self):
        if self.connected:
            return True
        return (time.monotonic() - self.disconnected_since) < self.grace_seconds

    def _run(self):
        while not self._stop.is_set():
            try:
                if self._server_reachable():
                    if self.active:
                        self.log("[failover] Server back -> passive.")
                        self.active = False
                        self.last_applied_slot = None
                elif self.armed:
                    if not self.active:
                        self.log("[failover] Server unreachable + armed -> taking over.")
                        self.active = True
                    slot = self._current_slot_key()
                    if slot != self.last_applied_slot:
                        self._apply_slot(slot)
                # else: disconnected but disarmed -> do nothing
            except Exception as exc:  # never let the failover thread die silently
                self.log(f"[failover] Loop error: {exc}")
            self._stop.wait(self.check_interval_seconds)

import os
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

# Load environment variables
load_dotenv("/app/.env")

# Prepare the Jinja environment
env = Environment(loader=FileSystemLoader("/app/templates"))

# Load commonly used variables
HOST = os.getenv("HOST_IP", "127.0.0.1")

# ──────────────────────────────── InfluxDB Config ────────────────────────────────
print("[...] Generating influxdb.yaml...")
template = env.get_template("influxdb.yaml.j2")
rendered = template.render(
    HOST=HOST,
    PORT=os.getenv("INFLUXDB_PORT", 8086),
    TOKEN=os.getenv("INFLUXDB_TOKEN", ""),
    ORG=os.getenv("INFLUXDB_ORG", "kybfarm"),
    BUCKET=os.getenv("INFLUXDB_BUCKET", "FarmData")
)
with open("/app/output/include/influxdb.yaml", "w") as f:
    f.write(rendered)
print("[✓] influxdb.yaml generated.")

# ─────────────────────────────── AppDaemon Config ────────────────────────────────
print("[...] Generating appdaemon.yaml...")
template = env.get_template("appdaemon.yaml.j2")
rendered = template.render(
    LATITUDE=os.getenv("LATITUDE", 0),
    LONGITUDE=os.getenv("LONGITUDE", 0),
    ELEVATION=os.getenv("ELEVATION", 30),
    TIME_ZONE=os.getenv("TIME_ZONE", "Europe/Berlin"),
    HOST_IP=HOST,
    TOKEN=os.getenv("TOKEN", ""),
    APPDAEMON_PORT=os.getenv("APPDAEMON_PORT", 5050)
)
with open("/app/output/appdaemon/appdaemon.yaml", "w") as f:
    f.write(rendered)
print("[✓] appdaemon.yaml generated.")

# ─────────────────────────────── Mosquitto Config ────────────────────────────────
print("[...] Generating mosquitto.conf...")
template = env.get_template("mosquitto.conf.j2")
rendered = template.render(
    MQTT_PORT=os.getenv("MOSQUITTO_BROKER_PORT", 1883),
    ALLOW_ANONYMOUS=os.getenv("ALLOW_ANONYMOUS", "true").lower() == "true",
    PASSWORD_FILE=os.getenv("PASSWORD_FILE", "").strip() or None
)
with open("/app/output/mosquitto/mosquitto.conf", "w") as f:
    f.write(rendered)
print("[✓] mosquitto.conf generated.")

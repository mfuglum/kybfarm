from server.src.utils.influxdb_handler import InfluxDBHandler
from datetime import datetime
from zoneinfo import ZoneInfo
import os

def get_current_rfc3339():
    now_utc = datetime.now(ZoneInfo("Europe/Oslo"))
    rfc3339_timestamp = now_utc.isoformat()
    return rfc3339_timestamp

def main():
    # InfluxDB connection settings
    bucket = "TestData"
    org = os.getenv("DOCKER_INFLUX_INIT_ORG")
    token = os.getenv("DOCKER_INFLUX_INIT_ADMIN_TOKEN")
    url = "http://localhost:8086"

    # Initialize the InfluxDBHandler instance
    db_handler = InfluxDBHandler(bucket=bucket, org=org, token=token, url=url)

    try:
        # Example data point to write
        measurement = "test_measurement"
        fields = {"temperature": 22.5, "humidity": 60}
        tags = {"location": "middle_shelf"}
        current_time = get_current_rfc3339()

        # Write data to the database
        print("Writing data to InfluxDB...")
        db_handler.write_to_database(measurement=measurement, fields=fields, tags=tags, time=current_time)

        # Example query parameters
        query_measurement = "airSensors"
        query_field = "temperature"
        query_tags = {"sensor_id": "TLM0100"}

        # Query data from the database
        print("Querying data from InfluxDB...")
        tables = db_handler.query_latest_from_database(measurement=query_measurement, field=query_field, tags=query_tags)
        record = tables[0].records[0]
        print(f"Resulting record:\nTime: {record.get_time()}, Value: {record.get_value()}\n")

    finally:
        # Ensure to close the database connection
        db_handler.close()

if __name__ == "__main__":
    main()

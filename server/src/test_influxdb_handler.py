from influxdb_handler import InfluxDBHandler
from datetime import datetime
from zoneinfo import ZoneInfo
import time

def get_current_rfc3339():
    now_utc = datetime.now(ZoneInfo("Europe/Oslo"))
    rfc3339_timestamp = now_utc.isoformat()
    return rfc3339_timestamp

# current_rfc3339 = get_current_rfc3339()
# print(current_rfc3339)
# print(type(current_rfc3339))

# def get_current_epoch_ns():
#     current_time_ns = time.time_ns()
#     return current_time_ns

# current_epoch_ns = get_current_epoch_ns()
# print(current_epoch_ns)

#############

def main():
    # InfluxDB connection settings
    bucket = "FarmData"
    org = "kybfarm"
    token = "opk12eopkop12j3po12j321jioj4klbnads"
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
        query_measurement = "test_measurement"
        query_field = "temperature"
        query_tags = {"location": "middle_shelf"}
        query_start = "-10m"

        # Query data from the database
        print("Querying data from InfluxDB...")
        tables = db_handler.query_from_database(measurement=query_measurement, tags=query_tags, field=query_field, start=query_start)

        # Iterate over the result
        for table in tables:
            for record in table.records:
                print(f"Time: {record.get_time()}, Value: {record.get_value()}\n")

    finally:
        # Ensure to close the database connection
        db_handler.close()

if __name__ == "__main__":
    main()

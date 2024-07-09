from utils.influxdb_handler import InfluxDBHandler

def main():
    # InfluxDB connection settings
    bucket = "<bucket>"
    org = "<org>"
    token = "<token>"
    url = "<url>"  # Use http://localhost:<port>

    # Initialize the InfluxDBHandler instance
    db_handler = InfluxDBHandler(bucket=bucket, org=org, token=token, url=url)

    try:
        # Example query parameters
        query_measurement = "°C"
        query_field = "value"
        query_tags = {"source": "HASS"}

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

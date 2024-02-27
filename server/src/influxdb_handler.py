from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

class InfluxDBHandler:
    """Handles interactions with an InfluxDB database."""

    def __init__(self, bucket: str, org: str, token: str, url: str):
        """
        Initializes the database handler with connection settings.
        
        Parameters:
            bucket: The InfluxDB bucket name.
            org: The organization name.
            token: The authentication token.
            url: The URL of the InfluxDB server.
        """
        self._bucket=bucket
        self._org=org
        self._token=token
        self._url=url
        self._client=InfluxDBClient(org=org, token=token, url=url)
        self._write_api=self._client.write_api(write_options=SYNCHRONOUS)
        self._query_api=self._client.query_api()

    def write_to_database(self, measurement: str, fields: dict, tags: dict = None, time: str = None) -> None:
        """
        Writes a single data point to the database.
        
        Parameters:
            measurement: The measurement name.
            tags: The tag key-value pairs.
            fields (optional): The field key-value pairs.
            time (optional): The timestamp as a string in RFC3339 format.
        """
        # Validate that fields is a dictionary
        if not isinstance(fields, dict):
            raise TypeError('"fields" argument must be a dictionary')

        # Create a new data point with the measurement name
        data_point = Point(measurement)

        # Add tags from the tags dictionary if provided
        if tags is not None:
            # Validate that tags is a dictionary
            if not isinstance(tags, dict):
                raise TypeError('"tags" argument must be a dictionary')
            for tag_key, tag_value in tags.items():
                data_point.tag(tag_key, tag_value)
        
        # Add fields from the fields dictionary
        for field_key, field_value in fields.items():
            data_point.field(field_key, field_value)

        # Set the timestamp for the data point if provided
        if time is not None:
            data_point.time(time)

        # Write the datapoint to the database
        self._write_api.write(bucket=self._bucket, org=self._org, record=data_point)

    def query_from_database(self, measurement: str, field: str, tags: dict, start: str='1h', stop: str='now()') -> object:
        """
        Queries an array of data points from the database.
        
        Parameters:
            measurement: The measurement name.
            field (optional): The field key-value pairs.
            tags: The tag key-value pairs.
            start: The start of the time interval to query data over.
            stop (optional): The end of the time interval to query data over. Defaults to current time.

        Returns:
            tables: The tables that result from the query.
        """
        # Initialize the base of the flux query
        flux_query_base = f'from(bucket:"{self._bucket}")\n    |> range(start: {start}, stop: {stop})\n'

        # Initialize the filter part of the flux query
        flux_query_filters = ""

        # Add measurement filter
        flux_query_filters += f'    |> filter(fn:(r) => r._measurement == "{measurement}")\n'

        # Add field filter
        flux_query_filters += f'    |> filter(fn:(r) => r._field == "{field}")\n'
        
        # Add tag filters
        for tag, value in tags.items():
            flux_query_filters += f'    |> filter(fn:(r) => r.{tag} == "{value}")\n'

        # Concatenate the base and filter part of the flux query
        flux_query = flux_query_base + flux_query_filters

        # Query the data points from the database
        print("Querying database with the following Flux script:\n", flux_query)
        tables = self._query_api.query(query=flux_query)
        return tables
    
    # def delete_from_database():  # NOTICE: This function has yet to be implemented. Will delete selected / queried datapoints from database.
    
    # def custom_flux_query():  # NOTICE: This function has yet to be implemented. Will allow for custom queries to the database using the Flux language syntax.

    def close(self):
        """Closes the database connection."""
        self._client.close()

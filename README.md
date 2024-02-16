# kybfarm
Open-source IoT platform for Vertical Farming Facilities.

## Docker Compose: Build and launch the containers
Prerequisite: Docker Desktop is installed.


For local development the tunnel container 'cloudlfared' should be commented out from 'kybfarm-docker-compose.yaml'.

Make sure to provide an environment file '.env' located in the root folder with all the necessary parameters before calling 'docker compose ... --build'.
The tokens which will be configured after build are:
    - Long-lived access token for AppDaemon integration with Home Assistant: https://developers.home-assistant.io/docs/auth_api/#long-lived-access-token

In root folder of the cloned repo the following command builds and launches the containers:
``` bash
docker compose -f kybfarm-docker-compose.yaml up --build -d
```

## Onboarding in Home Assistant
Enter the Home Assistant dashboard at localhost:8123.
Create a new user.

## Configure communications between containers
Create a file 'secrets.yaml' to store local configurations for Home Assistant and integrated containers.

Integration of InfluxDB:
Create a InfluxDB all-access API token for integration with Home Assistant: https://docs.influxdata.com/influxdb/cloud/admin/tokens/create-token/#create-an-all-access-token
Fill in the token after for: 'influxdb_token' in 'secrets.yaml'.

Integration of AppDaemon:
In Home Assistant create a long-lived access token: https://developers.home-assistant.io/docs/auth_api/#long-lived-access-token
Then provide this token in '.env' for 'TOKEN' in the fields for AppDaemon.

## Configure MQTT broker in Home Assistant
The MQTT broker must be configured in the GUI of the Home Assistant dashboard.
Follow the steps under 'Configuration - Manual configuration steps', essentially:
    -   Go to Settings > Devices & Services.
    -   Select: + Add Integration.
    -   Select MQTT-
    -   Add the address and port for your MQTT broker. The suggested broker for development is 'broker.emqx.io'.
If using a public broker disable automatic discovery:
    -   Click on the three dots on the right hand side of the broker listed under Integrations entries and select 'System options'
    -   In the System options for MQTT menu disable both automatically adding options.

Now from Settings > Devices & Services under 'Entities' the configured MQTT devices should be available and can be enabled.
Here unwanted devices can disabled or deleted.

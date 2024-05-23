# IoT platform for VF: Software Manual
The [kybfarm repository](https://github.com/mfuglum/kybfarm/) provides an open-source IoT platform framework for vertical farming. This document serves as a user manual for detailed guidance.

The repository is available at:  
[https://github.com/mfuglum/kybfarm/](https://github.com/mfuglum/kybfarm/)

## Introduction
The design of this IoT platform framework enables the management and automation of vertical farming systems. It leverages containerization for modularity and scalability at the server-side, while specific interfaces enable control over actuators and data acquisition from sensors on the edge-side. The repository comprises the software for both server and edge, allowing one environment file for common parameters. Dedicated directories contain the server- and edge-specific code. The following outlines the repository structure:

```plaintext
kybfarm/
|-- edge/
|   |-- src/
|   |   |-- actuator_instances/
|   |   |   `-- relay_devices_initialization.py
|   |   |-- sensor_interfaces/
|   |   |   |-- __init__.py
|   |   |   |-- sensor_BMP280_I2C.py
|   |   |   |-- sensor_SCD41_I2C.py
|   |   |   |-- sensor_SEC01_modbus.py
|   |   |   |-- sensor_SLIGHT01_modbus.py
|   |   |   |-- sensor_SPAR02_modbus.py
|   |   |   |-- sensor_SPH01_modbus.py
|   |   |   `-- sensor_SYM01_modbus.py
|   |   `-- utils/
|   |       |-- __init__.py
|   |       `-- relay_device.py
|   |-- .gitignore
|   |-- auto_launch_at_reboot.sh
|   |-- edge_computer_main.py
|   |-- reboot_config_example.sh
|   `-- requirements.txt
|-- server/
|   |-- appdaemon/
|   |   `-- config/apps/
|   |       `-- dummy_control.py
|   |-- mosquitto/
|   |   `-- config/
|   |       `-- mosquitto.conf
|   `-- src/
|       `-- config_generator/
|           |-- appdaemon_templates/
|           |   `-- appdaemon_apps_template.yaml
|           `-- homeassistant_templates/
|               |-- automations_template.yaml
|               |-- config_generator.py
|               |-- configuration_template.yaml
|               |-- dockerfile
|               |-- influxdb_template.yaml
|               |-- input_boolean_template.json
|               |-- input_select_template.json
|               |-- input_text_template.json
|               `-- requirements.txt
|-- .gitignore
|-- README.md
|-- env_template.env
`-- kybfarm-docker-compose.yaml
```


# Getting Started
## Prerequisites

### Server:
- Docker and Docker Compose installed.
- Ensure the IP address is available from the edge by configuring the network or installing Tailscale or ZeroTier.

### Edge:
- A Raspberry Pi or similar device for edge computing.
- Sensors and actuators compatible with the platform.
  - See section on RS485 adapter configuration for Modbus communication.
- raspi-gpio installed for GPIO configuration on the edge computer.
- Ensure the server IP address is available by configuring the network or installing Tailscale or ZeroTier.

## Configuration
Configuration is managed through environment files (` .env `), which should be placed in the repository's root. The environment file includes parameters such as the MQTT broker address, device identifiers, and other settings specific to your deployment. The file ` env_template.env ` provides an example ` .env ` file and should be replaced with the actual parameters.

# Installation
## Server Setup
1. Clone the repository:
    ```bash
    git clone https://github.com/mfuglum/kybfarm.git
    cd kybfarm
    ```

2. Build and start the containers using Docker Compose:
    ```bash
    docker compose -f kybfarm-docker-compose.yaml up --build -d
    ```

3. Onboard to Home Assistant:
    1. Access the Home Assistant dashboard at:
        http://localhost:8123.
    2. Create a new user and complete the onboarding process.

4. Configure communication between InfluxDB and Home Assistant:
    1. Generate an all-access API token in InfluxDB: 
        https://docs.influxdata.com/influxdb/cloud/admin/tokens/create-token/#create-an-all-access-token.
    2. Add this token to the `.env` file as `INFLUXDB_TOKEN`.

5. Configure communication between AppDaemon and Home Assistant:
    1. Generate a long-lived access token in Home Assistant: 
        https://developers.home-assistant.io/docs/auth_api/#long-lived-access-token.
    2. Add this token to the `.env` file as `TOKEN`.

## Edge Computer Setup
1. Clone the repository on the edge computer:
    ```bash
    git clone https://github.com/mfuglum/kybfarm.git
    cd kybfarm/edge
    ```

2. Set up a Python virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3. Configure crontab for auto-launch at boot on Rasbian system:
    - The script for auto-launch is in the file `auto_launch_at_reboot.sh`.
    - It configures all GPIO ports to avoid unwanted relay states and utilizes `raspi-gpio` for this.
    - To make sure the script doesn't run too early, it waits for proper ping with the MQTT broker. The IP for the MQTT broker must be provided in the file or in a separate `reboot_config.sh` in the same folder. An example file is provided as `reboot_config_example.sh`. Rename the file and replace the value for the `mqtt_broker_ip`.
    - To make the auto-launch script executable, enter the following command in a terminal in the /edge folder:
        ```bash
        chmod +x auto_launch_at_reboot.sh
        ```
    - Then, a cron-job must be scheduled for every reboot. Open a terminal and enter:
        ```bash
        crontab -e
        ```
        If this is the first time using crontab, choose your preferred editor.
    - Add the following line to the crontab-file (replace `/path` with the actual path to kybfarm, e.g., `/home/username/`):
        ```bash
        @reboot /path/kybfarm/edge/auto_relaunch_at_reboot.sh
        ```
        When added, save and exit.

# Running the Platform
## Server Setup
After setting up the configuration, start the platform using Docker Compose:
```bash
docker compose -f kybfarm-docker-compose.yaml up --build -d
```

## Edge Computer Setup
To manually activate the virtual environment and start the script:
```bash
source /path/to/kybfarm/edge/venv/bin/activate
python /path/to/kybfarm/edge/edge_computer_main.py
```
# Server Components
Docker-Compose orchestrates all of the listed components based on the content of the file `kybfarm-docker-compose.yaml`.

## MQTT Broker
- **Purpose:** Facilitate communication between the server and edge devices.
- **Implementation:** Uses the Eclipse Mosquitto Docker Image.
- **Configuration:**
  - Port: 1883
  - Configured for "allow anonymous": This is enabled for simplicity while networking is end-to-end encrypted. If the IP address is available publicly, this should be changed.

## Home Assistant
- **Purpose:** Manage devices, data logging, automation, and provide a user interface.
- **Implementation:** Deployed using the Home Assistant Docker Image.
- **Configuration:**
  - Port: 8123
  - Integrates with InfluxDB for data storage
  - Integrates with AppDaemon for control and processing

## InfluxDB
- **Purpose:** Store time-series data.
- **Implementation:** Uses the InfluxDB Docker Image.
- **Configuration:**
  - Port: 8086
  - User details and bucket names are specified in the environment file

## AppDaemon
- **Purpose:** Host Python scripts for data processing, modeling, and control.
- **Implementation:** Uses the AppDaemon Docker Image.
- **Configuration:**
  - Scripts can access sensor data from InfluxDB, communicate via MQTT, and interact directly with entities in Home Assistant.

## Configuration Generator: `config_generator`
- **Purpose:** Implement Architecture as Code by generating configuration files with parameters from the environment file.
- **Implementation:** Executes in a container. It replaces placeholder values in the Home Assistant and AppDaemon configuration templates with actual parameters from the `.env` file.
- **Configuration:**
  - The YAML file for Docker Compose mounts relevant Home Assistant and AppDaemon directories so that configuration can be written from this container.
- **Usage:**
  - Add your configuration templates to the `config_generator/` directory.
  - Ensure the placeholders in the templates match the variable names in the `.env` file.
  - The `config_generator` container will automatically generate the final configuration files on startup if provided with the appropriate location.

# Edge Components
## Sensors
- **Purpose:** Gather data for the vertical farming system.
- **Implementation:** Most sensors use Modbus RTU protocol. Implemented in Python using minimalmodbus.
- **The implemented sensor interfaces:**

| Sensor Type                              | Model Name                                                                                         | Manufacturer | MPN.    |
|------------------------------------------|----------------------------------------------------------------------------------------------------|--------------|---------|
| **Modbus RTU protocol**                  |                                                                                                    |              |         |
| Photosynthetically Active Radiation      | [S-PAR-02](https://files.seeedstudio.com/products/314990735/res/PAR%20Sensor.pdf)                 | Seeed Studio | 314990735 |
| Light Intensity                          | [S-LIGHT-01](https://files.seeedstudio.com/products/314990739/Doc/LightIntensitySensor-UserGuide.pdf) | Seeed Studio | 314990740 |
| Temperature and Leaf Wetness            | [S-YM-01](https://files.seeedstudio.com/products/314990737/doc/LeafWetnessandTemperatureSensor-UserGuide.pdf) | Seeed Studio | 314990738 |
| pH and Temperature                      | [S-PH-01](https://files.seeedstudio.com/products/101990666/res/RS485%20&%200-2V%20pH%20Sensor%20(S-pH-01)%20-%20User%20Guide%20v2.0.pdf) | Seeed Studio | 101990666 |
| Electric Conductivity, Total Dissolved Solids, and Temperature | [S-EC-01](https://files.seeedstudio.com/products/314990634/res/Liquid%20EC%20and%20TDS%20Sensor%20Datasheet%20v1.1.pdf) | Seeed Studio | 314990634 |
| **I2C protocol**                         |                                                                                                    |              |         |
| Temperature and Barometric Pressure     | [BMP280](https://cdn-learn.adafruit.com/downloads/pdf/adafruit-bmp280-barometric-pressure-plus-temperature-sensor-breakout.pdf) | Adafruit     | 2651    |
| Temperature, Humidity, and CO2          | [SCD-41](https://cdn-learn.adafruit.com/downloads/pdf/adafruit-scd-40-and-scd-41.pdf)            | Adafruit     | 5190    |


## Actuators
- **Purpose:** Relays enable control of actuators in the vertical farming asset.
- **Implementation:** Controlled via GPIO pins using the RPi.GPIO package, implemented as a relay device class.

## Communication Controller
The main script on the edge, `edge_computer_main.py`, serves as a communication controller.
- **Purpose:** Enable central control and data acquisition.
- **Implementation:** Written in Python, utilizing paho-mqtt for MQTT communication.
- **Key Functions:**
  - Load parameters from the environment file
  - Initiate MQTT client and connect to the broker
  - Subscribe to topics and handle data/command requests

# MQTT Topic Convention
A well-defined MQTT topic structure ensures efficient communication:
- **Data Acquisition:**
  - Request: `dt/location/device-identifier/req`
  - Response: `dt/location/device-identifier/res`
- **Control and Configuration:**
  - Request: `cmd/location/device-identifier/req`
  - Response: `cmd/location/device-identifier/res`
Embed response topics in the payload to avoid hardcoding.

# Development Guidelines
This is an outline of the recommended development flow when integrating new sensors:
1. Assign device names and MQTT topics in the `.env` file.
2. Write a device interface for the edge computer.
3. Subscribe to data request topics and initialize the sensor.
4. Register callback functions to provide data on request.
5. On the server side, add sensor configuration in the Home Assistant config template (in `config_generator/homeassistant_templates/`).
6. Add automation for periodic data requests in the automations template (in `config_generator/homeassistant_templates/`).
7. Restart the systems with the applied code. The sensor will appear as discovered in Home Assistant and must be enabled if automatic enabling of discovered devices is not checked.

# Development and Debugging Tips
## On Edge / Raspberry Pi
### Stop Current Cronjob
1. Check the status of cron jobs:
    ```bash
    systemctl status cron
    ```
2. Identify the process under "cron.service" (e.g., `edge_computer_main.py`) and its PID.
3. Kill the process:
    ```bash
    kill [PID]
    ```
   This ensures the cron job does not conflict with manually started scripts.

## On Server
### Debugging with MQTT
1. Navigate to: `Settings > Devices & Services > MQTT > Configure`
2. Use the built-in tool to debug communication:
   - Detect if a packet is not published from the edge or server.
   - Publish packets to identify if the issue is on the edge computer or in the Home Assistant configuration.
   Typical errors include incorrect formatting or wrong topics.
### Debugging with Docker
1. Open Docker Desktop.
2. Select the container you are having trouble with:
   - Access files and logs in the container.
   - Inspect files that might be incorrect or simply read errors in the log.

### Debugging with Home Assistant GUI
Common errors occur when configuring relays and calibration GUI tools (Helpers). These errors often relate to entity IDs.
The following bullet points can be useful in such situations:
- Follow the naming convention of lowercase and underscore-separated names.
- If automations linked to helpers don’t trigger as expected, an ID error is likely.
- To identify this, simply click on the helper and check its entity ID in the GUI and see if it deviates from the one provided in the environment file.

# Miscellaneous

## Raspberry Pi 4B with RS485 Adapter
This section details the configuration of Raspberry Pi 4B as an edge computer with the RS485 adapter:
- Waveshare 2-CH RS485 HAT

The product wiki provides all the necessary information at:
[https://www.waveshare.com/wiki/2-CH_RS485_HAT](https://www.waveshare.com/wiki/2-CH_RS485_HAT)

In summary, the following steps must be conducted to deploy the adapter with Raspberry Pi 4B for Modbus RTU communication:
1. DIP switch configuration: Set the utilized channels to Full-auto mode.
2. Load driver:
   - Open the file `/boot/config.txt`.
   - Add the following line and save:
     ```bash
     dtoverlay=sc16is752-spi1, int_pin=24
     ```
   - Reboot and the RS485 channels are available at the ports:
     - `ttySC0`
     - `ttySC1`


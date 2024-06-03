

# IoT platform for VF: Software Manual

The [Kybfarm Embed repository](https://github.com/mfuglum/kybfarm/) provides
an open-source Internet of Things (IoT) platform framework for vertical
farming. This document serves as a user manual for detailed guidance.

The repository is available at: <https://github.com/mfuglum/kybfarm/>

## Introduction

The design of the Kybfarm Embed framework enables the management and
automation of vertical farming systems. It leverages containerization
for modularity and scalability at the server-side, while specific
interfaces enable control over actuators and data acquisition from
sensors on the edge-side. The repository comprises the software for both
server and edge, allowing one environment file for common parameters.
Dedicated directories contain the server- and edge-specific code.
The repository structure is outlined below:

``` {#lst:repo_structure caption="Outline of repository structure for Kybfarm Embed." label="lst:repo_structure"}
kybfarm/
|-- edge/
|   |-- src/
|   |   |-- actuator_instances/
|   |   |   |-- grow_lamp_elixia_initialization.py
|   |   |   `-- relay_devices_initialization.py
|   |   |-- sensor_interfaces/
|   |   |   |-- sensor_BMP280_I2C.py
|   |   |   |-- sensor_SCD41_I2C.py
|   |   |   |-- sensor_SEC01_modbus.py
|   |   |   |-- sensor_SLIGHT01_modbus.py
|   |   |   |-- sensor_SPAR02_modbus.py
|   |   |   |-- sensor_SPH01_modbus.py
|   |   |   `-- sensor_SYM01_modbus.py
|   |   `-- utils/
|   |       |-- grow_lamp_elixia.py
|   |       `-- relay_device.py
|   |-- auto_launch_at_reboot.sh
|   |-- edge_computer_main.py
|   |-- reboot_config_example.sh ( update and rename to -> reboot_config.sh )
|   `-- requirements.txt
|-- server/
|   |-- appdaemon/config/apps/
|   |             `-- dummy_control.py
|   |-- homeassistant/config/
|   |                 `-- ( generated after running docker-compose )
|   |-- mosquitto/config/
|   |             `-- mosquitto.conf
|   `-- src/config_generator/
|           |-- config_generator.py
|           |-- dockerfile
|           |-- requirements.txt
|           |-- appdaemon_templates/
|           |   `-- appdaemon_apps_template.yaml
|           `-- homeassistant_templates/
|               |-- automations_template.yaml
|               |-- configuration_template.yaml
|               |-- influxdb_template.yaml
|               |-- input_boolean_template.yaml
|               |-- input_number_template.yaml
|               |-- input_select_template.yaml
|               `-- input_text_template.yaml
|-- .gitignore
|-- README.md
|-- .env_template ( update and rename to -> .env )
`-- kybfarm-docker-compose.yaml
```

## Getting Started

### Prerequisites

#### Server:

-   Linux terminal (e.g. The native terminal for Linux-based systems, or
    Windows Subsystem for Linux) available on the installation machine.

-   Docker and Docker Compose installed.

-   Ensure the IP address is available from the edge by configuring the
    network or installing Tailscale or ZeroTier.

#### Edge:

-   A Raspberry Pi or similar device for edge computing.

    -   Tested edge computer configuration: Raspberry Pi 4B with Rasbian
        OS installed.

-   Sensors and actuators compatible with the platform.

    -   See section on RS485 adapter configuration for Modbus
        communication.

-   raspi-gpio installed for General Purpose Input/Output (GPIO)
    configuration on the edge computer.

-   Ensure the server IP address is available by configuring the network
    or installing Tailscale or ZeroTier.

### Configuration

**Place updated `.env`-file in repository root:** Configuration is
managed through an environment file (`.env`) and template files with
placeholder values. The environment file should be placed in the
repository's root. The environment file includes parameters such as the
MQTT broker address, device identifiers, and other settings specific to
your deployment. The file `.env_template` provides an example `.env`
file and should be replaced with the actual parameters.

### Docker Desktop as a tool during installation

Docker Desktop provides useful functionality for setup and debugging
during the installation process as well as after deployment. After
creating the containers using `docker compose`, check out the following
features of Docker Desktop:

-   Open the *Containers* overview.

-   Extend by clicking on the arrow beside `kybfarm`.

-   Network *Ports* are displayed and hyperlinked, enabling fast access
    to the container's interface.

-   For debugging, click on a containers name, and:

    -   *Logs*: Useful for identifying configuration errors or simply
        verifying proper functionality.

    -   *Exec*: Provides a terminal to operate easily within the
        container (e.g. for creating files).

    -   *Files*: Provide overview of file system. It is possible to
        verify content and modify or delete files without modifying
        permission flags (which is required if you access a container's
        files from an external interface).

## Installation

### Server Setup

1.  **Clone the repository:**

                git clone https://github.com/mfuglum/kybfarm.git
                cd kybfarm

2.  **Build and start the containers using Docker Compose:**

                docker compose -f kybfarm-docker-compose.yaml up --build -d

3.  **Onboard to Home Assistant:**

    1.  Access the Home Assistant dashboard at: <http://localhost:8123>.

    2.  Create a new user and complete the onboarding process.

    3.  The entered credentials are valid for the local instance created
        inside the recently created container.

4.  **Configure communication between InfluxDB and Home Assistant:**

    1.  Generate an all-access API token in InfluxDB (as outlined in the
        following steps):
        <https://docs.influxdata.com/influxdb/cloud/admin/tokens/create-token/#create-an-all-access-token>.

    2.  Access InfluxDB at: <http://localhost:8086>.

    3. Log-in credentials are provided in the `.env` file as `DOCKER_INFLUXDB_INIT_USERNAME` and `DOCKER_INFLUXDB_INIT_PASSWORD`.

    4.  Locate the arrow symbol in the left pane, and click the *API
        Tokens* option.

    5.  Click *GENERATE API TOKEN* and choose the *All Access API Token*
        option.

    6.  Add this token to the `.env` file as `INFLUXDB_TOKEN`.

5.  **Configure communication between AppDaemon and Home Assistant:**

    1.  Generate a long-lived access token in Home Assistant (as
        outlined in the following steps):
        <https://developers.home-assistant.io/docs/auth_api/#long-lived-access-token>.

    2.  Access the Home Assistant dashboard at:<http://localhost:8123>.

    3.  Click on the profile icon in the
        left pane of the dashboard.

    4.  Locate the token section in the *Security* tab, and create a *Long-lived access
        token*.

    5.  Add this token to the `.env` file as `TOKEN`.

6.  **Update IP address fields of `.env` file**

    1.  `HOST_IP`: For the integration of InfluxDB and Home Assistant.

    2.  `INFLUXDB_URL`: For *optional* dashboard integration for
        InfluxDB in Home Assistant.

    3.  `HA_URL`: For the integration of AppDaemon and Home Assistant.

    4.  `APPDAEMON_URL`: For *optional* dashboard integration for
        AppDaemon and Home Assistant.

    5.  `MOSQUITTO_BROKER_IP`: The broker IP for the server for edge to
        connect (Tailscale IP for server).

7.  **Rebuild containers with new parameters and tokens:**

                docker compose -f kybfarm-docker-compose.yaml up --build -d

8.  **Integrate MQTT broker with Home Assistant:**
    1. Access the Home Assistant dashboard at:<http://localhost:8123>.

    2. Click the *Settings* option on the left pane of the dashboard.

    3. Click *Devices & Services*.

    4. Click *Add Integration*.

    5. Search for *MQTT*, and choose *MQTT* twice.

    6. Provide `MOSQUITTO_BROKER_IP` as *Broker*, and `MOSQUITTO_BROKER_PORT` as *Port* if modified. 

    7. Save the broker settings, and configured MQTT devices appear automatically.


### Edge Computer Setup

1.  **Clone the repository on the edge computer:**

            git clone https://github.com/mfuglum/kybfarm.git
            cd kybfarm/edge

2.  **Set up a Python virtual environment:**

            python3 -m venv venv
            source venv/bin/activate
            pip install -r requirements.txt
3.  **Configure addresses**
    1. **For Modbus RTU sensors:** Provide the correct Modbus RTU address for each sensor instance in `edge_computer_main.py`
    2. **For HTTP interfaced grow lamp:** Provide the lamp's IP address in the `.env` file in the `LAMP_01_IP` field.

4.  **Configure crontab for auto-launch at boot on Rasbian system:**

    \
    The script for auto-launch is in the file
    `auto_launch_at_reboot.sh`. It configures all GPIO ports to avoid
    unwanted relay states and utilizes `raspi-gpio` for this. To make
    sure the script doesn't run too early, it waits for proper ping with
    the MQTT broker.

    **Provide `MOSQUITTO_BROKER_IP` in `reboot_config.sh`:**

    The IP for the MQTT broker must be provided in the file or in a
    separate `reboot_config.sh` in the same folder. An example file is
    provided as `reboot_config_example.sh`. Rename the file and replace
    the value for the `mqtt_broker_ip`.\
    To make the auto-launch script executable, enter the following
    command in a terminal in the /edge folder:

            chmod +x auto_launch_at_reboot.sh

    Then, a cron-job must be scheduled for every reboot. Open a terminal
    and enter:

            crontab -e

    If this is the first time using crontab, choose your preferred
    editor.

    \
    Add the following line to the crontab-file (replace `/path` with the
    actual path to kybfarm, e.g., `/home/username/`):

            @reboot /path/kybfarm/edge/auto_relaunch_at_reboot.sh

    When added, save and exit.

## Running the Platform

### Server Setup

After setting up the configuration, start the platform using Docker
Compose:

        docker compose -f kybfarm-docker-compose.yaml up --build -d

This will initialize all containers and start the services.

### Edge Computer Setup

For automatic launch, reboot the system from GUI or terminal:

        sudo reboot

To manually activate the virtual environment and start the script:

        source /path/to/kybfarm/edge/venv/bin/activate
        python /path/to/kybfarm/edge/edge_computer_main.py

## Server Components 

Docker-Compose orchestrates all of the listed components based on the
content of the file `kybfarm-docker-compose.yaml`.

### MQTT Broker

-   **Purpose:** Facilitate communication between the server and edge
    devices.

-   **Implementation:** Uses the Eclipse Mosquitto Docker Image.

-   **Configuration:**

    -   Port: 1883

    -   Configured for \"allow anonymous\": This is enabled for
        simplicity while networking is end-to-end encrypted. If the IP
        address is available publicly, this should be changed.

### Home Assistant

-   **Purpose:** Manage devices, data logging, automation, and provide a
    user interface.

-   **Implementation:** Deployed using the Home Assistant Docker Image.
    The \"config_generator\" provides all configuration and
    functionality when executed.

-   **Configuration:**

    -   Port: 8123

    -   Integrates with InfluxDB for data storage

    -   Integrates with AppDaemon for control and processing

### InfluxDB

-   **Purpose:** Store time-series data.

-   **Implementation:** Uses the InfluxDB Docker Image.

-   **Configuration:**

    -   Port: 8086

    -   User details and bucket names are specified in the environment
        file

### AppDaemon

-   **Purpose:** Host Python scripts for data processing, modeling, and
    control.

-   **Implementation:** Uses the AppDaemon Docker Image.

-   **Configuration:**

    -   Port: 5050

    -   Scripts can access sensor data from InfluxDB, communicate via
        MQTT, and interact directly with entities in Home Assistant.

### Configuration Generator: `config_generator`

-   **Purpose:** Implement Architecture as Code by generating
    configuration files with parameters from the environment file.

-   **Implementation:** Executes in a container. It replaces placeholder
    values in the Home Assistant and AppDaemon configuration templates
    with actual parameters from the `.env` file using Jinja2.

-   **Configuration:**

    -   The YAML file for Docker Compose mounts relevant Home Assistant
        and AppDaemon directories so that configuration can be written
        from this container.

-   **Usage:**

    -   Add or extend configuration templates in the `config_generator/`
        directory.

    -   Ensure the placeholders in the templates match the variable
        names in the `.env` file.

    -   The `config_generator` container will automatically generate the
        final configuration files on startup if provided with the
        appropriate location.

## Edge Components

### Sensors

-   **Purpose:** Gather data for the vertical farming system.

-   **Implementation:** Most sensors use Modbus Remote Terminal Unit
    (RTU) protocol. Implemented in Python using minimalmodbus.

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


### Actuators

#### Relay controlled devices
- **Purpose:** Relays enable control of actuators in the vertical farming asset.
- **Implementation:** Controlled via GPIO pins using the RPi.GPIO package, implemented as a relay device class.

#### HTTP controlled Grow Lamp
- **Purpose:** An ethernet interfaced grow lamp provides light in the vertical farming asset.
- **Implementation:** Controlled via HTTP using the requests package, implemented as a lamp device class.


| Actuator type | Model Name                | Links                                                                                       |
|---------------|---------------------------|---------------------------------------------------------------------------------------------|
| **HTTP protocol**                                                                                                                                         |
| Grow lamp     | Heliospectra Elixia LX 601C R4B | [Datasheet](https://led.heliospectra.com/hubfs/Heliospectra%20ELIXIA%20Technical%20Specifications%20V.4.pdf) & [User Manual](https://led.heliospectra.com/hubfs/Heliospectra%20ELIXIA%2c%20DYNA%20User%20Manual%20V.8.2.pdf) |

### Communication Controller

The main script on the edge, `edge_computer_main.py`, serves as a
communication controller.

-   **Purpose:** Enable central control and data acquisition.

-   **Implementation:** Written in Python, utilizing paho-mqtt for MQTT
    communication.

-   **Key Functions:**

    -   Load parameters from the environment file

    -   Initiate MQTT client and connect to the broker

    -   Subscribe to topics and handle data/command requests

## MQTT Topic Convention

A well-defined MQTT topic structure ensures efficient communication:

-   **Data Acquisition:**

    -   Request: `dt/location/device-identifier/req`

    -   Response: `dt/location/device-identifier/res`

-   **Control and Configuration:**

    -   Request: `cmd/location/device-identifier/req`

    -   Response: `cmd/location/device-identifier/res`

Embed response topics in the payload to avoid hardcoding.

## Development Guidelines

### Recommended Development Flow

This is an outline of the recommended development flow when integrating
new sensors:

1.  Assign device names and MQTT topics in the `.env` file.

2.  Write a device interface for the edge computer.

3.  Subscribe to data request topics and initialize the sensor.

4.  Register callback functions to provide data on request.

5.  On the server side, add sensor configuration in the Home Assistant
    config template (in `config_generator/homeassistant_templates/`).

6.  Add automation for periodic data requests in the automations
    template (in `config_generator/homeassistant_templates/`).

7.  Restart the systems with the applied code. The sensor will appear as
    discovered in Home Assistant and must be enabled if automatic
    enabling of discovered devices is not checked.

### Outline of Configuration File Templates

All of the configuration files mentioned below are located in
`kybfarm/server/config_generator/`, and the following paths are relative
to this directory:

#### AppDaemon Templates

-   `appdaemon_templates/appdaemon_apps_template.yaml`:\
    This template is used to create instances of modules/classes
    developed in `kybfarm/server/appdaemon/config/apps`. It overwrites
    the `apps.yaml` file in that directory.

#### Home Assistant Templates

-   `homeassistant_templates/automations_template.yaml`:\
    Manage, add, or modify all time- and event-based automations here.
    These automations can use entity IDs from entities defined in the
    other configuration files.

-   `homeassistant_templates/configuration_template.yaml`:\
    This is the main configuration file for Home Assistant. New sensors
    are added here.

-   `homeassistant_templates/influxdb_template.yaml`:\
    Provide InfluxDB configuration relevant to Home Assistant
    integration here.

-   `homeassistant_templates/input_boolean_template.yaml`:\
    Manage or add switches for relay control here.

-   `homeassistant_templates/input_select_template.yaml`:\
    Manage, add, or modify calibration menus for sensors here.

-   `homeassistant_templates/input_text_template.yaml`:\
    Manage or add status fields here.

-   `homeassistant_templates/input_number_template.yaml`:\
    Manage, add, or modify number inputs for adjusting grow lamp wavelength-specific channel intensities here.

## Development and Debugging Tips

### On Edge / Raspberry Pi

#### Stop Current Cronjob

1.  Check the status of cron jobs:

            systemctl status cron

2.  Identify the process under \"cron.service\" (e.g.,
    `edge_computer_main.py`) and its Process ID (PID).

3.  Kill the process by entering the following command replacing `PID`
    with the actual number:

            kill PID

    This ensures the cron job does not conflict with manually started
    scripts.

#### Modifying Modbus RTU Address of Device

Follow these steps to modify the Modbus RTU address of a device:

1.  **Open terminal**

    -   Access the terminal on your edge computer (Raspberry Pi).

    -   Navigate to the `/kybfarm/edge/` directory.

    -   Activate the Python virtual environment.

    -   Start Python by entering:

                python

2.  **Import the relevant device interface**

    -   Import the device interface to interact with the Modbus RTU
        device (replacing `RELEVANT_DEVICE`):

                from src.sensor_interfaces import sensor_RELEVANT_DEVICE

3.  **Create an Instance with the Original Address**

    -   Initialize the Modbus RTU device with its current address:

                device_1 = sensor_RELEVANT_DEVICE( portname='/dev/ttySC1', 
                                                   slaveaddress=original_address )

    -   Replace `/dev/ttySC1` with the correct port.

    -   Replace `original_address` with the current Modbus address of
        the sensor.

    -   Verify correct initialization entering the device instance name:

                device_1

    -   The returned output should list the object with the provided
        port, address and default values.

    -   Verify communication by inspecting the return from
        `get_slave_address()`

                device_1.get_slave_address()

4.  **Set the New Slave Address**

    -   Change the Modbus address to the desired new address:

                device_1.set_slave_address( new_address )

    -   Replace `new_address` with the new Modbus address you want to
        assign.

5.  **Repower the Sensor**

    -   Power off the sensor and then power it back on to apply the new
        address.

6.  **Test with a New Instance**

    -   Create a new instance to verify that the sensor is responding at
        the new address:

                device_2 = sensor_RELEVANT_DEVICE( portname='/dev/ttySC1', 
                                                   slaveaddress=new_address )

    -   Test communication to ensure the address change was successful:

                device_2.get_slave_address()

By following these steps, you can change and verify the Modbus RTU
address of your sensor.

### On Server

#### Debugging with MQTT

1.  Navigate to: `Settings > Devices & Services > MQTT > Configure`

2.  Use the built-in tool to debug communication:

    -   Detect if a packet is not published from the edge or server.

    -   Publish packets to identify if the issue is on the edge computer
        or in the Home Assistant configuration.

Typical errors include incorrect formatting or wrong topics.

#### Debugging with Docker

1.  Open Docker Desktop.

2.  Select the container you are having trouble with:

    -   Access files and logs in the container.

    -   Inspect files that might be incorrect or simply read errors in
        the log.

#### Debugging with Home Assistant Graphical User Interface (GUI)

Common errors occur when configuring relays and calibration GUI tools
(Helpers). These errors often relate to entity IDs. The following bullet
points can be useful in such situations:

-   Follow the naming convention of lowercase and underscore-separated
    names.

-   If automations linked to helpers don't trigger as expected, an ID
    error is likely.

-   To identify this, simply click on the helper and check its entity ID
    in the GUI and see if it deviates from the one provided in the
    environment file.

## Miscellaneous
### Raspberry Pi 4B with RS485 Adapter

This section details the configuration of Raspberry Pi 4B as an edge
computer with the RS485 adapter:

-   Waveshare 2-CH RS485 HAT

The product wiki provides all the necessary information at:
[https: //www.waveshare.com/wiki/2-CH_RS485_HAT](https: //www.waveshare.com/wiki/2-CH_RS485_HAT){.uri}

In summary, the following steps must be conducted to deploy the adapter
with Raspberry Pi 4B for Modbus RTU communication:

-   DIP switch configuration: Set the utilized channels to Full-auto
    mode.

-   Load driver:

    -   Open the file `/boot/config.txt`.

    -   Add the following line and save:

                        dtoverlay=sc16is752-spi1, int_pin=24

    -   Reboot and the RS485 channels are available at the ports:

        -   `ttySC0`

        -   `ttySC1`

## Glossary

- **GPIO:** General Purpose Input/Output
- **GUI:** Graphical User Interface
- **IoT:** Internet of Things
- **MPN:** Manufacturer Part Number
- **PID:** Process ID
- **RTU:** Remote Terminal Unit

## Author and Date

This user manual was created by Martin Fuglum in May 2024.
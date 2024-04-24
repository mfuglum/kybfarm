## Prototyping a Python virtual environment with scripts to run the IoT platform in VF container

### Required system wide installations, see [this section](#system-wide-installatins)

### For auto-launch at reboot, see [this section](#auto-launch-at-reboot)

### If cloned with complete python virtual environment (venv):
#### Activate the venv:
```
source ./venv/bin/activate
```

### Else, if venv is not created, create one, and install requirements:
#### Create:
```
python3 -m venv venv
```
#### Activate:
```
source ./venv/bin/activate
```
#### Install requirements:
```
pip install -r requirements.txt
```

#### To install new packages:
Installing:
```
pip install <packagename>
```

To export requirement list to **requirements.txt**:
```
pip freeze > requirements.txt
```

### To run the main program:
```
python3 main.py
```

### To stop the program and deacitvate environment:
Quit program:
```
ctrl + c
```
Deactivate:
```
deactivate
```

#### Explanation of installed requirements
Should all be listed in **requirements.txt**:

For interfacing with the BMP280 sensor:
adafruit-circuitpython-bmp280

For MQTT:
paho-mqtt

### Required system wide installations <a id="system-wide-installatins"></a>
Due to not beeing Python packages, these must be installed system wide:
Tailscale

### Auto-launch edge script at reboot on Rasbian system <a id="auto-launch-at-reboot"></a>
This section goes through the auto-launch script configuration and how to set a cron-job to execute it.

The script for auto-launch in the file "auto_launch_at_reboot.sh"

To make sure the script doesn't run too early it is implemented to wait for proper ping with the MQTT broker.
To do so the IP for the MQTT broker must be provided in the file or in a separate "reboot_config.sh" in the same folder.
An example file is provided as "reboot_config_example.sh". 
Rename the file and replace the value for the "mqtt_broker_ip". 

Also change the path to the repository and to the Python virtual environment in "auto_launch_at_reboot.sh" and "edge_computer_main.py"

To make the auto-launch script executable enter the following command in a terminal in the folder of the file:
```
chmod +x auto_launch_at_reboot.sh
```

#### Then, a cron-job must be scheduled for every reboot:

Open a terminal and enter:
```
crontab -e
```
If this is the first time using crontab, choose your preferred editor.

Add the following line to the crontab-file (replace 'path_to_repository' with actual path, e.g. '/home/username/'):
```
@reboot /path_to_repository/kybfarm/edge/auto_relaunch_at_reboot.sh
```

When added, save and exit.




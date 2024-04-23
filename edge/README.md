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
Open a terminal and enter:
```
crontab -e
```
If this is the first time using crontab chose your editor.

Then add the following line to the crontab-file (replace 'path_to_repository' with actual path, e.g. '/home/username/'):
```
@reboot cd /path_to_repository/kybfarm/edge/ && source /venv/bin/activate && python edge_computer_main.py
```


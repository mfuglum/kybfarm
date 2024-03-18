## Prototyping a Python virtual environment with scripts to run the IoT platform in VF container

### Required system wide installations, see [this section](#system-wide-installatins)

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
Mosquitto, to be able to run as a MQTT broker (On debian/Ubuntu systems):
```
sudo apt-get update
```
```
sudo apt install -y mosquitto mosquitto-clients
```
To start the broker:
```
sudo systemctl start mosquitto
```
To enable the broker at startup:
```
sudo systemctl enable mosquitto
```
To verify it's running:
```
sudo systemctl status mosquitto
```

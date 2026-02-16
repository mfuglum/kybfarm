#!/bin/bash

# This script is launched at reboot on the edge computer as a #reboot cronjob
# First the GPIO pins are configured
# Then the virtual environment is activated
# Finally, after network connection with the broker is established, the main script is launched
# Configure GPIO pins to avoid wrong relay behavior before starting main

# Refering to the GPIO (BCD) pin mapping on the edge computer

# GPIO_PIN = {
#     "relay_1": 2,
#     "relay_2": 3,
#     "relay_3": 4,
#     "relay_4": 14,
#     "relay_5": 15,
#     "relay_6": 17,
#     "relay_7": 23,
#     "relay_8": 10,
#     "relay_9": 9,
#     "relay_10": 25,
#     "relay_11": 11,
#     "relay_12": 8,
#     "relay_13": 6,
#     "relay_14": 12,
#     "relay_15": 13,
#     "relay_16": 16,
#     "float_switch_1": 7,
#     "float_switch_2": 0,
#     "float_switch_3": 1,
#     "float_switch_4": 5,
# }


# Set GPIO mode to output and drive high utilizing raspi-gpio
raspi-gpio set 2 op dh
raspi-gpio set 3 op dh
raspi-gpio set 4 op dh
raspi-gpio set 14 op dh
raspi-gpio set 15 op dh
raspi-gpio set 17 op dh
raspi-gpio set 23 op dh
raspi-gpio set 10 op dh
raspi-gpio set 9 op dh
raspi-gpio set 25 op dh
raspi-gpio set 11 op dh
raspi-gpio set 8 op dh
raspi-gpio set 6 op dh
raspi-gpio set 12 op dh
raspi-gpio set 13 op dh
raspi-gpio set 16 op dh

# Set GPIO mode to input for float switches
raspi-gpio set 7 ip
raspi-gpio set 0 ip
raspi-gpio set 1 ip
raspi-gpio set 5 ip

# Activate venv on edge
source /home/user1/kybfarm/edge/venv/bin/activate

# Load MQTT broker IP (can also be configured directly in this file)
source /home/user1/kybfarm/edge/reboot_config.sh

# Wait for ping to broker is successful
until ping -c 1 $mqtt_broker_ip; do
	echo "Waiting for network"
	sleep 1
done

echo "Network is up, starting main on edge:"

python /home/user1/kybfarm/edge/edge_computer_main.py > /home/user1/kybfarm/cronlog.log 2>&1
#!/bin/bash

#!/bin/bash

# This script is launched at reboot on the edge computer as a #reboot cronjob
# First the GPIO pins are configured
# Then the virtual environment is activated
# Finally, after network connection with the broker is established, the main script is launched
# Configure GPIO pins to avoid wrong relay behavior before starting main

# Refering to the GPIO (BCD) pin mapping on the edge computer
"""
GPIO_PIN = {
    "relay_1": 2,
    "relay_2": 3,
    "relay_3": 4,
    "relay_4": 14,
    "relay_5": 15,
    "relay_6": 17,
    "relay_7": 23,
    "relay_8": 10,
    "relay_9": 9,
    "relay_10": 25,
    "relay_11": 11,
    "relay_12": 8,
    "relay_13": 6,
    "relay_14": 12,
    "relay_15": 13,
    "relay_16": 16,
    "float_switch_1": 7,
    "float_switch_2": 0,
    "float_switch_3": 1,
    "float_switch_4": 5,
}
"""
# Set GPIO level to high to avoid relay activation at boot
gpio write 2 1
gpio write 3 1
gpio write 4 1
gpio write 14 1
gpio write 15 1
gpio write 17 1
gpio write 23 1
gpio write 10 1
gpio write 9 1
gpio write 25 1
gpio write 11 1
gpio write 8 1
gpio write 6 1
gpio write 12 1
gpio write 13 1
gpio write 16 1

# Set GPIO mode to output for relays
gpio mode 2 out
gpio mode 3 out
gpio mode 4 out
gpio mode 14 out
gpio mode 15 out
gpio mode 17 out
gpio mode 23 out
gpio mode 10 out
gpio mode 9 out
gpio mode 25 out
gpio mode 11 out
gpio mode 8 out
gpio mode 6 out
gpio mode 12 out
gpio mode 13 out
gpio mode 16 out

# Set GPIO mode to input for float switches
gpio mode 7 in
gpio mode 0 in
gpio mode 1 in
gpio mode 5 in

# Activate venv on edge
source /home/user1/Desktop/kybfarm/edge/venv/bin/activate

# Load MQTT broker IP (can also be configured directly in this file)
source /home/user1/Desktop/kybfarm/edge/reboot_config.sh

# Wait for ping to broker is successful
until ping -c 1 $mqtt_broker_ip; do
	echo "Waiting for network"
	sleep 1
done

echo "Network is up, starting main on edge:"

python /home/user1/Desktop/kybfarm/edge/edge_computer_main.py > /home/user1/Desktop/cronlog.log 2>&1

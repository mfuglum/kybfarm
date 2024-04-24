#!/bin/bash

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

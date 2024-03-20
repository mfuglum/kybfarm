# This file contains functions to fetch MQTT topic data from a .env file
import os

def fetch_mqtt_topics(env_file_path, topic_keywords):
    mqtt_topics = []
    with open(env_file_path, 'r') as file:
        for line in file:
            if line.startswith('MQTT_'):
                for keyword in topic_keywords:
                    if keyword in line:
                        # Append the topic which is behind '=' (position 1) and strip any whitespace
                        mqtt_topics.append(line.split('=')[1].strip())
    return mqtt_topics
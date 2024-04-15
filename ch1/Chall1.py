# Challenge 1: Setting up an MQTT Broker & Basic Communication

import time
import random
import os
import paho.mqtt.client as paho
from paho import mqtt
import ssl  # Importing the ssl module for setting TLS version

# Setting callbacks for different events

def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)

def on_publish(client, userdata, mid, properties=None):
    print("mid: " + str(mid))

def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_message(client, userdata, msg):
    print("Message: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

if __name__ == '__main__':

    broker_address = 'ade35bc1fc0843cbbeb1419f06320add.s1.eu.hivemq.cloud'
    broker_port = 8883
    username = 'dweng'
    password = 'Woah!!!5'

    client1 = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="Client1", userdata=None, protocol=paho.MQTTv5)
    client1.tls_set(tls_version=ssl.PROTOCOL_TLS)
    client1.username_pw_set(username, password)
    client1.connect(broker_address, broker_port)
    client1.on_subscribe = on_subscribe
    client1.on_message = on_message
    client1.on_publish = on_publish 

    client2 = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="Client2", userdata=None, protocol=paho.MQTTv5)
    client2.tls_set(tls_version=ssl.PROTOCOL_TLS)
    client2.username_pw_set(username, password)
    client2.connect(broker_address, broker_port)
    client2.on_subscribe = on_subscribe
    client2.on_message = on_message
    client2.on_publish = on_publish 

    client3 = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="Client3", userdata=None, protocol=paho.MQTTv5)
    client3.tls_set(tls_version=ssl.PROTOCOL_TLS)
    client3.username_pw_set(username, password)
    client3.connect(broker_address, broker_port)
    client3.on_subscribe = on_subscribe
    client3.on_message = on_message
    client3.on_publish = on_publish 
    client3.subscribe("data/#")

    while(True):
        client1.publish('data/1', random.randint(1,10))
        client2.publish('data/2', random.randint(1,10))
        time.sleep(1)
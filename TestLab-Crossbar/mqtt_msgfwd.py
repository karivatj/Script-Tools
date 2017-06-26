#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

from twisted.internet.defer import inlineCallbacks
from twisted.logger import Logger

from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import ApplicationSession
from requests import ConnectionError
from access_tokens import *

import json
import paho.mqtt.client as mqtt
import requests
import socket

mqtt_client = mqtt.Client()

#These handler functions forward received WAMP events to a external MQTT Broker
def on_haltian_location(msg):
    print("event for 'on_haltian_location' received: {}".format(msg))
    msg = json.loads(msg)
    if len(msg) == 0:
        print("'on_haltian_location' response is empty")
        return
    targetId = "vehicle4564"
    data = dict()
    data["lat"] = float(msg[0]["lat"])
    data["lon"] = float(msg[0]["lon"])
    data["level"] = 0 #floor number
    mqtt_client.publish('com/testlab/user/' + targetId + '/LOC', json.dumps(data))   

def on_withings_bp(msg):
    print("event for 'on_withings_bp' received: {}".format(msg))
    targetId = msg[0] 
    payload = msg[2]
    data = dict()
    data["value"] = payload
    mqtt_client.publish('com/testlab/user/' + targetId + '/bloodpressure', json.dumps(data))        

def on_withings_heartrate(msg):
    print("event for 'on_withings_heartrate' received: {}".format(msg))
    targetId = msg[0] 
    payload = msg[2]
    data = dict()
    data["value"] = payload
    mqtt_client.publish('com/testlab/user/' + targetId + '/avgheartrate', json.dumps(data))    

def on_withings_bodytemp(msg):
    print("event for 'on_withings_bodytemp' received: {}".format(msg))
    targetId = msg[0] 
    payload = msg[2]
    data = dict()
    data["value"] = payload
    mqtt_client.publish('com/testlab/user/' + targetId + '/bodytemp', json.dumps(data))    

def on_mqtt_connect(client, userdata, flags, rc):
    print("MQTT node up")

class AppSession(ApplicationSession):

    log = Logger()

    @inlineCallbacks
    def onJoin(self, details):
        try:
            self.log.info("Connecting to MQTT Broker")
            mqtt_client.username_pw_set(mqtt_username, mqtt_password)
            mqtt_client.on_connect = on_mqtt_connect
            mqtt_client.connect(mqtt_broker_url, mqtt_broker_port)
            mqtt_client.loop_start()
        except socket.gaierror:
            self.log.error("Connection error: MQTT Broker unavailable")

        ## SUBSCRIBE to topics and receive events
        sub = yield self.subscribe(on_haltian_location, 'com.testlab.haltian_location_update')
        print("subscribed to topic 'on_haltian_location'")
        sub = yield self.subscribe(on_withings_bp, 'com.testlab.withings_bloodpressure_update')
        print("subscribed to topic 'on_withings_bp'")
        sub = yield self.subscribe(on_withings_heartrate, 'com.testlab.withings_heartrate_update')
        print("subscribed to topic 'on_withings_heartrate'")
        sub = yield self.subscribe(on_withings_bodytemp, 'com.testlab.withings_bodytemp_update')
        print("subscribed to topic 'on_withings_bodytemp'")

        while True:
            yield sleep(60)
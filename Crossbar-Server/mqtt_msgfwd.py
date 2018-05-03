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

TAG = "MQTT Node: "

mqtt_client = mqtt.Client("Crossbar MQTT Bridge")
debug = False

#These handler functions forward received WAMP events to a external MQTT Broker
def on_ibm_cloud_update(msg):
    pass

def on_ecg_update(msg):
    print(str(TAG) + "event for 'on_ecg_update' received: {}".format(msg))
    try:
        mqtt_client.username_pw_set(mqtt_ekg_accesstoken)
        mqtt_client.connect(mqtt_broker_url, 1883, 60)
        msg = json.loads(msg)
        targetId = msg[0]
        date = msg[1]
        payload = msg[2]
        data = dict()
        data["value"] = payload
        data["date"] = date
        mqtt_client.publish('v1/devices/me/telemetry', json.dumps(data))
    except socket.gaierror:
        print(str(TAG) + "Connection error: MQTT Broker unavailable")
    finally:
        mqtt_client.disconnect()
    #mqtt_client.publish('com/testlab/user/' + targetId + '/avgheartrate', json.dumps(data))

def on_haltian_location(msg):
    print(str(TAG) + "event for 'on_haltian_location' received: {}".format(msg))
    try:
        mqtt_client.username_pw_set(mqtt_haltian_accesstoken)
        mqtt_client.connect(mqtt_broker_url, 1883, 60)
        msg = json.loads(msg)
        data = dict()
        targetId = "vehicle4564"
        if len(msg) == 0:
            if debug:
                print(str(TAG) + "'on_haltian_location' response is empty. Using default value")
            data["lat"] = 65.006198
            data["lon"] = 25.5229728
        else:
            try:
                data["lat"] = float(msg[0]["lat"])
                data["lon"] = float(msg[0]["lon"])
            except KeyError: #in case we post a default value
                data["lat"] = float(msg["lat"])
                data["lon"] = float(msg["lon"])
        data["level"] = 0 #floor number
        mqtt_client.publish('v1/devices/me/telemetry', json.dumps(data))
    except socket.gaierror:
        print(str(TAG) + "Connection error: MQTT Broker unavailable")
    finally:
        mqtt_client.disconnect()
    #mqtt_client.publish('com/testlab/user/' + targetId + '/LOC', json.dumps(data))

def on_withings_bp(msg):
    print(str(TAG) + "event for 'on_withings_bp' received: {}".format(msg))
    try:
        mqtt_client.username_pw_set(mqtt_bp_accesstoken)
        mqtt_client.connect(mqtt_broker_url, 1883, 60)
        targetId = msg[0]
        date = msg[1]
        payload = msg[2]
        data = dict()
        data["systolic"] = payload[0]
        data["diastolic"] = payload[1]
        data["date"] = date
        mqtt_client.publish('v1/devices/me/telemetry', json.dumps(data))
    except socket.gaierror:
        print(str(TAG) + "Connection error: MQTT Broker unavailable")
    finally:
        mqtt_client.disconnect()
    #mqtt_client.publish('com/testlab/user/' + targetId + '/bloodpressure', json.dumps(data))

def on_withings_heartrate(msg):
    print(str(TAG) + "event for 'on_withings_heartrate' received: {}".format(msg))
    try:
        mqtt_client.username_pw_set(mqtt_heartrate_accesstoken)
        mqtt_client.connect(mqtt_broker_url, 1883, 60)
        targetId = msg[0]
        date = msg[1]
        payload = msg[2]
        data = dict()
        data["value"] = payload
        data["date"] = date
        mqtt_client.publish('v1/devices/me/telemetry', json.dumps(data))
    except socket.gaierror:
        print(str(TAG) + "Connection error: MQTT Broker unavailable")
    finally:
        mqtt_client.disconnect()
    #mqtt_client.publish('com/testlab/user/' + targetId + '/avgheartrate', json.dumps(data))

def on_withings_bodytemp(msg):
    print(str(TAG) + "event for 'on_withings_bodytemp' received: {}".format(msg))
    try:
        mqtt_client.username_pw_set(mqtt_bodytemp_accesstoken)
        mqtt_client.connect(mqtt_broker_url, 1883, 60)
        targetId = msg[0]
        date = msg[1]
        payload = msg[2]
        data = dict()
        data["value"] = payload
        data["date"] = date
        mqtt_client.publish('v1/devices/me/telemetry', json.dumps(data))
    except socket.gaierror:
        print(str(TAG) + "Connection error: MQTT Broker unavailable")
    finally:
        mqtt_client.disconnect()
    #mqtt_client.publish('com/testlab/user/' + targetId + '/bodytemp', json.dumps(data))

def on_withings_activity(msg):
    print(str(TAG) + "event for 'on_withings_activity' received: {}".format(msg))
    try:
        mqtt_client.username_pw_set(mqtt_activity_accesstoken)
        mqtt_client.connect(mqtt_broker_url, 1883, 60)
        targetId = msg[0]
        date = msg[1]
        payload = msg[2]
        data = dict()
        data["value"] = payload
        data["date"] = date
        mqtt_client.publish('v1/devices/me/telemetry', json.dumps(data))
    except socket.gaierror:
        print(str(TAG) + "Connection error: MQTT Broker unavailable")
    finally:
        mqtt_client.disconnect()
    #mqtt_client.publish('com/testlab/user/' + targetId + '/activity', json.dumps(data))

def on_withings_sleep(msg):
    print(str(TAG) + "event for 'on_withings_sleep' received: {}".format(msg))
    try:
        mqtt_client.username_pw_set(mqtt_sleep_accesstoken)
        mqtt_client.connect(mqtt_broker_url, 1883, 60)
        targetId = msg[0]
        date = msg[1]
        payload = msg[2]
        data = dict()
        data["value"] = payload
        data["date"] = date
        mqtt_client.publish('v1/devices/me/telemetry', json.dumps(data))
    except socket.gaierror:
        print(str(TAG) + "Connection error: MQTT Broker unavailable")
    finally:
        mqtt_client.disconnect()
    #mqtt_client.publish('com/testlab/user/' + targetId + '/sleep', json.dumps(data))

def on_withings_energy(msg):
    print(str(TAG) + "event for 'on_withings_energy' received: {}".format(msg))
    try:
        mqtt_client.username_pw_set(mqtt_energy_accesstoken)
        mqtt_client.connect(mqtt_broker_url, 1883, 60)
        targetId = msg[0]
        date = msg[1]
        payload = msg[2]
        data = dict()
        data["value"] = payload
        data["date"] = date
        mqtt_client.publish('v1/devices/me/telemetry', json.dumps(data))
    except socket.gaierror:
        print(str(TAG) + "Connection error: MQTT Broker unavailable")
    finally:
        mqtt_client.disconnect()
    #mqtt_client.publish('com/testlab/user/' + targetId + '/sleep', json.dumps(data))

def on_mqtt_connect(client, userdata, flags, rc):
    print(str(TAG) + "MQTT node up")

class AppSession(ApplicationSession):
    log = Logger()

    @inlineCallbacks
    def onJoin(self, details):

        '''
        try:
            self.log.info(str(TAG) + "Connecting to MQTT Broker")
            mqtt_client.on_connect = on_mqtt_connect
            mqtt_client.username_pw_set(mqtt_bodytemp_accesstoken)
            mqtt_client.connect(mqtt_broker_url, 1883, 60)
            mqtt_client.loop_start()
        except socket.gaierror:
            self.log.error(str(TAG) + "Connection error: MQTT Broker unavailable")
        '''
        ## SUBSCRIBE to topics and receive events
        sub = yield self.subscribe(on_ecg_update, 'com.testlab.ecg_update')
        print(str(TAG) + "subscribed to topic 'on_ecg_update'")
        sub = yield self.subscribe(on_ibm_cloud_update, 'com.testlab.ibm_cloud_update')
        print(str(TAG) + "subscribed to topic 'on_ibm_cloud_update'")
        sub = yield self.subscribe(on_haltian_location, 'com.testlab.haltian_location_update')
        print(str(TAG) + "subscribed to topic 'on_haltian_location'")
        sub = yield self.subscribe(on_withings_bp, 'com.testlab.withings_bloodpressure_update')
        print(str(TAG) + "subscribed to topic 'on_withings_bp'")
        sub = yield self.subscribe(on_withings_heartrate, 'com.testlab.withings_heartrate_update')
        print(str(TAG) + "subscribed to topic 'on_withings_heartrate'")
        sub = yield self.subscribe(on_withings_bodytemp, 'com.testlab.withings_bodytemp_update')
        print(str(TAG) + "subscribed to topic 'on_withings_bodytemp'")
        sub = yield self.subscribe(on_withings_activity, 'com.testlab.withings_activity_update')
        print(str(TAG) + "subscribed to topic 'on_withings_activity'")
        sub = yield self.subscribe(on_withings_sleep, 'com.testlab.withings_sleep_update')
        print(str(TAG) + "subscribed to topic 'on_withings_sleep'")
        sub = yield self.subscribe(on_withings_energy, 'com.testlab.withings_energy_update')
        print(str(TAG) + "subscribed to topic 'on_withings_energy'")

        while True:
            yield sleep(60)

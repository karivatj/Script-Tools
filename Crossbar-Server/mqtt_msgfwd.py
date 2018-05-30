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
from collections import OrderedDict

TAG = "MQTT Node: "

# MQTT clients for each sensor
ecg_mqtt_client = mqtt.Client('com.testlab.ecg_mqtt_client')
ibm_cloud_mqtt_client = mqtt.Client('com.testlab.ibm_cloud_mqtt_client')
haltian_mqtt_client = mqtt.Client('com.testlab.haltian_mqtt_client')
withings_bp_mqtt_client = mqtt.Client('com.testlab.withings_bloodpressure_mqtt_client')
withings_heartrate_mqtt_client = mqtt.Client('com.testlab.withings_heartrate_mqtt_client')
withings_bodytemp_mqtt_client = mqtt.Client('com.testlab.withings_bodytemp_mqtt_client')
withings_activity_mqtt_client = mqtt.Client('com.testlab.withings_activity_mqtt_client')
withings_sleep_mqtt_client = mqtt.Client('com.testlab.withings_sleep_mqtt_client')
withings_energy_mqtt_client = mqtt.Client('com.testlab.withings_energy_mqtt_client')

debug = False

#These handler functions forward received WAMP events to a external MQTT Broker
def on_ibm_cloud_update(msg):
    print(str(TAG) + "event for 'on_ibm_cloud_update' received: {}".format(msg))
    try:
        msg = json.loads(msg)
        for elem in msg:
            ibm_cloud_mqtt_client.publish('v1/devices/me/telemetry', json.dumps(elem, sort_keys=True))
    except socket.gaierror:
        print(str(TAG) + "Connection error: MQTT Broker unavailable")

def on_ecg_update(msg):
    try:
        msg = json.loads(msg)
        data = dict()
        data["date"] = msg[1]
        data["value"] = msg[2]
        ecg_mqtt_client.publish('v1/devices/me/telemetry', json.dumps(data))
    except Exception as e:
        print(str(TAG) + "Error occured while sending data {}".format(e))

def on_haltian_location(msg):
    print(str(TAG) + "event for 'on_haltian_location' received: {}".format(msg))
    try:
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
        haltian_mqtt_client.publish('v1/devices/me/telemetry', json.dumps(data))
    except socket.gaierror:
        print(str(TAG) + "Connection error: MQTT Broker unavailable")

def on_withings_bp(msg):
    print(str(TAG) + "event for 'on_withings_bp' received: {}".format(msg))
    try:
        date = msg[1]
        payload = msg[2]
        data = dict()
        data["date"] = date
        data["systolic"] = payload[0]
        data["diastolic"] = payload[1]
        withings_bp_mqtt_client.publish('v1/devices/me/telemetry', json.dumps(data))
    except socket.gaierror:
        print(str(TAG) + "Connection error: MQTT Broker unavailable")

def on_withings_heartrate(msg):
    print(str(TAG) + "event for 'on_withings_heartrate' received: {}".format(msg))
    try:
        data = dict()
        data["date"] = msg[1]
        data["value"] = msg[2]
        withings_heartrate_mqtt_client.publish('v1/devices/me/telemetry', json.dumps(data))
    except socket.gaierror:
        print(str(TAG) + "Connection error: MQTT Broker unavailable")

def on_withings_bodytemp(msg):
    print(str(TAG) + "event for 'on_withings_bodytemp' received: {}".format(msg))
    try:
        data = dict()
        data["date"] = msg[1]
        data["value"] = msg[2]
        withings_bodytemp_mqtt_client.publish('v1/devices/me/telemetry', json.dumps(data))
    except socket.gaierror:
        print(str(TAG) + "Connection error: MQTT Broker unavailable")

def on_withings_activity(msg):
    print(str(TAG) + "event for 'on_withings_activity' received: {}".format(msg))
    try:
        data = dict()
        data["date"] = msg[1]
        data["value"] = msg[2]
        withings_activity_mqtt_client.publish('v1/devices/me/telemetry', json.dumps(data))
    except socket.gaierror:
        print(str(TAG) + "Connection error: MQTT Broker unavailable")

def on_withings_sleep(msg):
    print(str(TAG) + "event for 'on_withings_sleep' received: {}".format(msg))
    try:
        data = dict()
        data["date"] = msg[1]
        data["value"] = msg[2]
        withings_sleep_mqtt_client.publish('v1/devices/me/telemetry', json.dumps(data))
    except socket.gaierror:
        print(str(TAG) + "Connection error: MQTT Broker unavailable")

def on_withings_energy(msg):
    print(str(TAG) + "event for 'on_withings_energy' received: {}".format(msg))
    try:
        data = dict()
        data["date"] = msg[1]
        data["value"] = msg[2]
        withings_energy_mqtt_client.publish('v1/devices/me/telemetry', json.dumps(data))
    except socket.gaierror:
        print(str(TAG) + "Connection error: MQTT Broker unavailable")

def on_mqtt_connect(client, userdata, flags, rc):
    print(str(TAG) + "MQTT node up")

class AppSession(ApplicationSession):
    log = Logger()

    @inlineCallbacks
    def onJoin(self, details):
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

        # CONNECT MQTT Clients
        ecg_mqtt_client.username_pw_set(mqtt_ekg_accesstoken)
        ecg_mqtt_client.connect(mqtt_broker_url, 1883, 60)
        ibm_cloud_mqtt_client.username_pw_set(mqtt_ibm_steelhr_accesstoken)
        ibm_cloud_mqtt_client.connect(mqtt_broker_url, 1883, 60)
        haltian_mqtt_client.username_pw_set(mqtt_haltian_accesstoken)
        haltian_mqtt_client.connect(mqtt_broker_url, 1883, 60)
        withings_bp_mqtt_client.username_pw_set(mqtt_bp_accesstoken)
        withings_bp_mqtt_client.connect(mqtt_broker_url, 1883, 60)
        withings_heartrate_mqtt_client.username_pw_set(mqtt_heartrate_accesstoken)
        withings_heartrate_mqtt_client.connect(mqtt_broker_url, 1883, 60)
        withings_bodytemp_mqtt_client.username_pw_set(mqtt_bodytemp_accesstoken)
        withings_bodytemp_mqtt_client.connect(mqtt_broker_url, 1883, 60)
        withings_activity_mqtt_client.username_pw_set(mqtt_activity_accesstoken)
        withings_activity_mqtt_client.connect(mqtt_broker_url, 1883, 60)
        withings_sleep_mqtt_client.username_pw_set(mqtt_sleep_accesstoken)
        withings_sleep_mqtt_client.connect(mqtt_broker_url, 1883, 60)
        withings_energy_mqtt_client.username_pw_set(mqtt_energy_accesstoken)
        withings_energy_mqtt_client.connect(mqtt_broker_url, 1883, 60)

        # start the loops
        ecg_mqtt_client.loop_start()
        ibm_cloud_mqtt_client.loop_start()
        haltian_mqtt_client.loop_start()
        withings_bp_mqtt_client.loop_start()
        withings_heartrate_mqtt_client.loop_start()
        withings_bodytemp_mqtt_client.loop_start()
        withings_activity_mqtt_client.loop_start()
        withings_sleep_mqtt_client.loop_start()
        withings_energy_mqtt_client.loop_start()

        try:
            while True:
                yield sleep(60)
        except Exception as e:
            pass
        finally:
            ecg_mqtt_client.disconnect()
            ibm_cloud_mqtt_client.disconnect()
            haltian_mqtt_client.disconnect()
            withings_bp_mqtt_client.disconnect()
            withings_heartrate_mqtt_client.disconnect()
            withings_bodytemp_mqtt_client.disconnect()
            withings_activity_mqtt_client.disconnect()
            withings_sleep_mqtt_client.disconnect()
            withings_energy_mqtt_client.disconnect()


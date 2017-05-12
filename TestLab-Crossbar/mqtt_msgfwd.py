###############################################################################
#
# Copyright (c) Crossbar.io Technologies GmbH and/or collaborators. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
###############################################################################

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

def on_haltian_location(msg):
    print("event for 'on_haltian_location' received: {}".format(msg))
    msg = json.loads(msg)
    userid = "12762571"
    data = dict()
    data["lat"] = msg[0]["lat"]
    data["lon"] = msg[0]["lon"]
    mqtt_client.publish('com/testlab/user/' + user_id + '/LOC', json.dumps(data))   

def on_withings_bp(msg):
    print("event for 'on_withings_bp' received: {}".format(msg))
    msg = json.loads(msg)
    userid = "0"
    #mqtt_client.publish('com/testlab/user/' + user_id + '/bloodpressure', "data")        

def on_withings_heartrate(msg):
    print("event for 'on_withings_heartrate' received: {}".format(msg))
    msg = json.loads(msg)    
    userid = "0"
    #mqtt_client.publish('com/testlab/user/' + user_id + '/avgheartrate', "data")    

def on_withings_bodytemp(msg):
    print("event for 'on_withings_bodytemp' received: {}".format(msg))
    msg = json.loads(msg)    
    userid = "0"
    #mqtt_client.publish('com/testlab/user/' + user_id + '/bodytemp', "data")    

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
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
import requests

TAG = "Haltian Node: "

class AppSession(ApplicationSession):

    log = Logger()

    @inlineCallbacks
    def onJoin(self, details):

        # REGISTER a procedure for remote calling. Return location information
        def haltian_location():
            self.log.info(str(TAG) + "haltian_location() called. Delivering payload")
            return json.dumps(location_data)

        yield self.register(haltian_location, 'com.testlab.haltian_location')
        self.log.info(str(TAG) + "procedure haltian_location() registered")

        headers = {'Authorization': haltian_pw, 'Content-Type': 'application/json'}

        #two dictionaries to hold the current and previous location
        location_data = {}
        last_location = {}

        while True:
            try:
                #get location information
                r = requests.post(haltian_url, data=None, headers=headers)
            except ConnectionError:
                #self.log.error(str(TAG) + "Haltian Node: Connection Error. Check connectivity and / or connection parameters and try again!")
                yield sleep(300)
                continue

            if r.status_code == 200:
                data = r.text
                try:
                    location_data = json.loads(r.text)
                    if len(location_data) == 0:
                        location_data = dict()
                        location_data["lat"] = 65.0067789
                        location_data["lon"] = 25.5236168
                except ValueError:
                    self.log.error(str(TAG) + "Haltian Node: Error while decoding JSON data. Trying again later.")
                else:
                    if location_data == last_location:
                        pass
                    else:
                        last_location = location_data
                        self.log.info(str(TAG) + "Haltian Node: publishing Thingsee location")
                        yield self.publish('com.testlab.haltian_location_update', json.dumps(location_data))
            else:
                self.log.error(str(TAG) + "Haltian Node: " + str(r.status_code) + " Error. Service not available at this moment")
                yield sleep(300)

            yield sleep(60)
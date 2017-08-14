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

class AppSession(ApplicationSession):

    log = Logger()

    @inlineCallbacks
    def onJoin(self, details):

        # REGISTER a procedure for remote calling. Return location information
        def haltian_location():
            self.log.info("haltian_location() called. Delivering payload")
            return json.dumps(location_data)

        yield self.register(haltian_location, 'com.testlab.haltian_location')
        self.log.info("procedure haltian_location() registered")  

        headers = {'Authorization': haltian_pw, 'Content-Type': 'application/json'}

        #two dictionaries to hold the current and previous location
        location_data = {}
        last_location = {}

        while True:
            try:
                #get location information
                r = requests.post(haltian_url, data=None, headers=headers)
            except ConnectionError:
                self.log.error("Connection Error. Check connectivity and / or connection parameters and try again!")
                yield sleep(300)
                continue

            if r.status_code == 200:
                data = r.text
                try:
                    location_data = json.loads(r.text)
                except ValueError:
                    self.log.error("Error while decoding JSON data. Trying again later.")
                else:
                    if location_data == last_location:
                        pass
                    else:
                        last_location = location_data
                        self.log.info("publishing Thingsee location")
                        yield self.publish('com.testlab.haltian_location_update', json.dumps(location_data))                
            else:
                self.log.error(r.status_code + " Error. Check connectivity and / or connection parameters and try again!")

            yield sleep(5)
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

            if r.status_code == 404:
                self.log.error("404 Error. Check connectivity and / or connection parameters and try again!")
            else:
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

            yield sleep(5)
#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

from twisted.internet.defer import inlineCallbacks
from twisted.logger import Logger

from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import ApplicationSession
from ecg_data import ecg_data

import time
import json
import datetime
import itertools

TAG = "ECG Node: "

class AppSession(ApplicationSession):

    log = Logger()

    @inlineCallbacks
    def onJoin(self, details):
        self.log.info(str(TAG) + "ECG node up")
        try:
            for value in itertools.cycle(ecg_data):
                yield self.publish('com.testlab.ecg_update', json.dumps(['12762571', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), int(value)]))
                yield sleep(0.033)
        except Exception as e:
            self.log.error(str(TAG) + "Error: {}".format(e))
            pass

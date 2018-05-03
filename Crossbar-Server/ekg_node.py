#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

from twisted.internet.defer import inlineCallbacks
from twisted.logger import Logger

from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import ApplicationSession

import time
import json
import datetime

TAG = "ECG Node: "

#generator that yields values from file
def ecg_gen(f):
    while True:
        row = f.readline()
        if len(row) == 0:
            f.seek(0,0)
            row = f.readline()
        yield row

class AppSession(ApplicationSession):

    log = Logger()

    @inlineCallbacks
    def onJoin(self, details):
        self.log.info(str(TAG) + "ECG node up")
        counter = 0
        with open("../ECG_data.txt", "r") as f: #simulated sample of an ECG-curve
            value = ecg_gen(f)
            while True:
                try:
                    yield self.publish('com.testlab.ecg_update', json.dumps(['12762571', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), int(next(value))]))
                    yield sleep(0.033)
                except Exception as e:
                    self.log.error(str(TAG) + "Error: {}".format(e.message))
                    pass

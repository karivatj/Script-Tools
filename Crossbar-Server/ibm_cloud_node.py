#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

from twisted.internet.defer import inlineCallbacks
from twisted.logger import Logger

from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import ApplicationSession
from access_tokens import *

import time
import json
import datetime
import ibmiotf.application
import ibmiotf.device

TAG = "IBM Cloud Node: "

class AppSession(ApplicationSession):

    log = Logger()

    def messageHandler(self, event):
        self.log(str(TAG) + "Received data from IBM Cloud")
        self.log(str(TAG) + event.deviceId)
        self.log(str(TAG) + event.deviceType)
        self.log(str(TAG) + event.timestamp)
        self.log(str(TAG) + event.timestamp.strftime("%H:%M:%S"))
        self.log(str(TAG) + event.payload)

    @inlineCallbacks
    def onJoin(self, details):
        self.log.info(str(TAG) + "node up")

        appCli = ibmiotf.application.Client(ibm_options)
        appCli.connect()
        appCli.subscribeToDeviceEvents(deviceType=ibm_deviceType)
        appCli.deviceEventCallback = self.messageHandler

        while True:
            yield sleep(0.1)

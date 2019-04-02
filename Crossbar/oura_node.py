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

TAG = "OURA Node: "

class AppSession(ApplicationSession):

    log = Logger()

    @inlineCallbacks
    def onJoin(self, details):
        self.log.info(str(TAG) + " Node up")
        while True:
            yield sleep(60)
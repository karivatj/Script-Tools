#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

from twisted.internet.defer import inlineCallbacks
from twisted.logger import Logger

from threading import Thread, Lock
from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import ApplicationSession
from access_tokens import *

import time
from datetime import datetime
import json
import ibmiotf.application
import ibmiotf.device

TAG = "IBM Cloud Node: "

class AppSession(ApplicationSession):

    log = Logger()
    mutex = Lock()
    data = None

    def normalize_value(self, value, unit):
        return value * pow(10, unit)

    def get_meas_type(self, measure):
        if measure["type"] is 1:
            return "Weight"
        elif measure["type"] is 4:
            return "Height"
        elif measure["type"] is 5:
            return "Fat Free Mass"
        elif measure["type"] is 6:
            return "Fat Ratio"
        elif measure["type"] is 8:
            return "Fat Mass Weight"
        elif measure["type"] is 9:
            return "Diastolic Blood Pressure"
        elif measure["type"] is 10:
            return "Systolic Blood Pressure"
        elif measure["type"] is 11:
            return "Heart Pulse"
        elif measure["type"] is 12:
            return "Temperature"
        elif measure["type"] is 54:
            return "SP0"
        elif measure["type"] is 71:
            return "Body Temperature"
        elif measure["type"] is 73:
            return "Skin Temperature"
        elif measure["type"] is 76:
            return "Muscle Mass"
        elif measure["type"] is 77:
            return "Hydration"
        elif measure["type"] is 88:
            return "Bone Mass"
        elif measure["type"] is 91:
            return "Pulse Wave Velocity"

        return "Unknown"

    def messageHandler(self, event):
        self.log.info(str(TAG) + "Received data from IBM Cloud")
        '''
        self.log.info(str(TAG) + event.deviceId)
        self.log.info(str(TAG) + event.deviceType)
        self.log.info(str(TAG) + str(event.timestamp))
        self.log.info(str(TAG) + event.timestamp.strftime("%H:%M:%S"))
        date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(measuregroup["date"])))
        payload = json.loads(event.payload.decode('utf-8'))
        '''
        print("IBM Payload: {}".format(payload))

        data_list = []

        # check if measuregroups is present. If yes, we are talking about bodymeasures
        try:
            for measuregroup in payload["d"]["body"]["measuregrps"]:
                parsed_data = {}
                #date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(measuregroup["date"])))
                #parsed_data["date"] = date
                parsed_data["ts"] = int(measuregroup["date"] * 1000.0)
                parsed_data["values"] = {}
                for measure in measuregroup["measures"]:
                    measure_type = self.get_meas_type(measure)
                    value = self.normalize_value(measure['value'], measure['unit'])
                    parsed_data["values"][measure_type] = value
                data_list.append(parsed_data)
        except KeyError:
            # if an exception is raised. Check if activity key is present
            try:
                for exercise in payload["d"]["body"]["activities"]:
                    parsed_data = {}
                    parsed_data["ts"] = int(datetime.strptime(exercise["date"], "%Y-%m-%d").timestamp() * 1000.0)
                    parsed_data["values"] = {}
                    parsed_data["values"]["distance"] = exercise["distance"]
                    parsed_data["values"]["elevation"] = exercise["elevation"]
                    parsed_data["values"]["brand"] = exercise["brand"]
                    parsed_data["values"]["calories"] = exercise["calories"]
                    parsed_data["values"]["is_tracker"] = exercise["is_tracker"]
                    parsed_data["values"]["steps"] = exercise["steps"]
                    parsed_data["values"]["totalcalories"] = exercise["totalcalories"]
                    parsed_data["values"]["timezone"] = exercise["timezone"]
                    parsed_data["values"]["moderate"] = exercise["moderate"]
                    parsed_data["values"]["soft"] = exercise["soft"]
                    parsed_data["values"]["intense"] = exercise["intense"]
                    data_list.append(parsed_data)
            except KeyError:
                print(str(TAG) + "Unrecognized data received. Skipping")
                return

        self.mutex.acquire()
        try:
            self.data = data_list
        finally:
            self.mutex.release()

    @inlineCallbacks
    def onJoin(self, details):
        self.log.info(str(TAG) + "node up")

        appCli = ibmiotf.application.Client(ibm_options)
        appCli.connect()
        appCli.subscribeToDeviceEvents(deviceType=ibm_deviceType)
        appCli.deviceEventCallback = self.messageHandler

        while True:
            self.mutex.acquire()
            try:
                if self.data is not None:
                    yield self.publish('com.testlab.ibm_cloud_update', json.dumps(self.data))
                    self.data = None
            finally:
                self.mutex.release()
            yield sleep(5)

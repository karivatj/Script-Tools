#!/usr/bin/python
# -*- coding: utf-8 -*-

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
from autobahn.wamp.exception import ApplicationError

from dateutil.parser import parse
from withings_api import WithingsCredentials, WithingsApi
from data_formatter import *
from requests import ConnectionError

import crossbarhttp

import datetime
import json

#access tokens and secrets.
from access_tokens import user_access_tokens, user_access_secret

#dictionaries to hold measurement data
energy_data          = {}
activity_data        = {}
sleep_data           = {}
heartrate_data       = {}
bloodpressure_data   = {}
bodytemperature_data = {}

timedelta = datetime.date.today() - datetime.timedelta(days=60)

meastype = [10, 9, 11, 71] #weight (1), systolic / diastolic blood pressure (10 & 9), average pulse (11), body temperature (71)
user_ids = [0, 12762562, 12762571, 12762926]

#utility functions to get initial data chunks from Withings.
def get_energy_and_activity(user_id, client):
    activity = client.get_activity(startdateymd=timedelta, enddateymd=datetime.date.today()) #get step count & energy consumption statistics
    steps = []
    calories = []
    for record in activity['activities']:
        date = parse(record['date']).strftime('%Y-%m-%d')
        steps.append([date, record['steps']])
        calories.append([date, record['calories'] + record['totalcalories']])
    return calories, steps

def get_sleep(user_id, client):
    sleep_summary = client.get_sleepsummary(startdateymd=timedelta, enddateymd=datetime.date.today()) #get sleep summary statistics
    sleep = []
    last_measurement = datetime.datetime.fromtimestamp(0)
    this_measurement = None
    for record in sleep_summary['series']:
        this_measurement = parse(record['date'])
        if last_measurement < this_measurement:
            sleep.append([this_measurement.strftime('%Y-%m-%d'), (record['data']['deepsleepduration'] + record['data']['lightsleepduration']) / 60 / 60])
        last_measurement = this_measurement
    return sleep

def get_measurement_data(user_id, client):
    measures      = []
    heartrate     = []
    bodytemp      = []
    bloodpressure = []
    temp_bloodpressure = {}
    for m in meastype: measures.append(client.get_measures(meastype=m)) #get various of user body measurements

    for measure in measures:
        for group in measure:
            for result in group.measures:
                date = group.date.strftime('%Y-%m-%d %H:%M:%S')
                value = normalize_value(result['value'], result['unit'])
                if(result["type"] == 11): #Average Heartrate
                    if len([item for item in heartrate if item[0] == date]) == 0:
                        heartrate.append([date, value])
                elif(result["type"] == 71): #Body Temperature
                    if len([item for item in bodytemp if item[0] == date]) == 0:
                        bodytemp.append([date, value])
                elif(result["type"] == 10): #Systolic BP
                    temp_bloodpressure[date] = []
                    temp_bloodpressure[date].append(value)
                elif(result["type"] == 9): #Diastolic BP
                    temp_bloodpressure[date].append(value)
                    if len([item for item in bloodpressure if item[0] == date]) == 0:
                        bloodpressure.append([date, temp_bloodpressure[date]])

    return heartrate, bloodpressure, bodytemp

def normalize_value(value, unit):
    return value * pow(10, unit)

def update_list_entry(alist, key, value):
    return [(k,v) if (k != key) else (key, value) for (k, v) in alist]

# Stops iterating through the list as soon as it finds the value
def get_list_index(list, index, value):
    for pos, t in enumerate(list):
        if t[index] == value:
            return pos
    # Matches behavior of list.index
    raise ValueError("list.index(x): x not in list")

class AppSession(ApplicationSession):

    log = Logger()

    @inlineCallbacks
    def onJoin(self, details):
        '''
        Register various of different RPC methods that allows clients to get up-to-date
        data gathered from Withings API.

        Six RPC:s registered for Withings related stuff. Used to request complete data sets:
            - Energy Consumption
            - Activity
            - Sleep
            - Blood pressure
            - Body temperature
            - Average heartrate
        Six topics that are available for clients. Updates are published when ever *new* data is available
            - Energy Data Update
            - Activity Data Update
            - Sleep Data Update
            - BP Data Update
            - Body temp Data Update
            - Heartrate Data Update
        '''
        self.log.info("Connecting to HTTP Bridge")
        crossbar_client = crossbarhttp.Client('http://web.testlab.local:8080/publish')
        print(type(crossbar_client))

        # REGISTER a procedure for remote calling. Return Energy Consumption rates
        def withings_energy(data_format):
            data = {}
            self.log.info("withings_energy() called. Delivering payload")
            if data_format in "plotly": #return plotly compatible data
                for x in energy_data:
                    data[x] = format_data_to_plotly(energy_data, x)
                return json.dumps(data)
            else:
                return json.dumps(energy_data)

        yield self.register(withings_energy, 'com.testlab.withings_energy')
        self.log.info("procedure withings_energy() registered")

        # REGISTER a procedure for remote calling. Return Daily Activity
        def withings_activity(data_format):
            data = {}
            self.log.info("withings_activity() called. Delivering payload")
            if data_format in "plotly": #return plotly compatible data
                for x in activity_data:
                    data[x] = format_data_to_plotly(activity_data, x)
                return json.dumps(data)
            if data_format in "intersystems": #return plotly compatible data
                for x in activity_data:
                    data[x] = format_measurement_data_to_intersystems(activity_data, x)
                return json.dumps(data)
            else:
                return json.dumps(activity_data)

        yield self.register(withings_activity, 'com.testlab.withings_activity')
        self.log.info("procedure withings_activity() registered")

        # REGISTER a procedure for remote calling. Return Sleep Statistics
        def withings_sleep(data_format):
            data = {}
            self.log.info("withings_sleep() called. Delivering payload")
            if data_format in "plotly": #return plotly compatible data
                for x in sleep_data:
                    data[x] = format_data_to_plotly(sleep_data, x)
                return json.dumps(data)
            else:
                return json.dumps(sleep_data)

        yield self.register(withings_sleep, 'com.testlab.withings_sleep')
        self.log.info("procedure withings_sleep() registered")

        # REGISTER a procedure for remote calling. Return Bloodpressure measurements
        def withings_bloodpressure(data_format):
            data = {}
            self.log.info("withings_bloodpressure() called. Delivering payload")
            if data_format in "plotly": #return plotly compatible data
                for x in bloodpressure_data:
                    data[x] = format_bloodpressure_data_to_plotly(bloodpressure_data, x)
                return json.dumps(data)
            elif data_format in "intersystems": #return intersystems compatible data via HTTP bridge
                for x in bloodpressure_data:
                    data[x] = format_bloodpressure_data_to_intersystems(bloodpressure_data, x, "bloodPressure")
                    #return json.dumps(data)
                return json.dumps(data) #Testing: return first user back
            else:
                return json.dumps(bloodpressure_data)

        yield self.register(withings_bloodpressure, 'com.testlab.withings_bloodpressure')
        self.log.info("procedure withings_bloodpressure() registered")

        # REGISTER a procedure for remote calling. Return Body Temperature readings
        def withings_bodytemperature(data_format):
            data = {}
            self.log.info("withings_bodytemperature() called. Delivering payload")
            if data_format in "plotly": #return plotly compatible data
                for x in bodytemperature_data:
                    data[x] = format_measurement_data_to_plotly(bodytemperature_data, x)
                return json.dumps(data)
            elif data_format in "intersystems": #return intersystems compatible data via HTTP bridge
                for x in bodytemperature_data:
                    data[x] = format_measurement_data_to_intersystems(bodytemperature_data, x, "bodyTemp")
                    #return json.dumps(data)
                return json.dumps(data) #Testing: return first user back
            else:
                return json.dumps(bodytemperature_data)

        yield self.register(withings_bodytemperature, 'com.testlab.withings_bodytemperature')
        self.log.info("procedure withings_bodytemperature() registered")

        # REGISTER a procedure for remote calling. Return Heartrate readings
        def withings_average_heartrate(data_format):
            data = {}
            self.log.info("withings_average_heartrate() called. Delivering payload")
            if data_format in "plotly": #return plotly compatible data
                for x in heartrate_data:
                    data[x] = format_measurement_data_to_plotly(heartrate_data, x)
                return json.dumps(data)
            else:
                return json.dumps(heartrate_data)

        yield self.register(withings_average_heartrate, 'com.testlab.withings_average_heartrate')
        self.log.info("procedure withings_average_heartrate() registered")

        '''
        In this point fetch data from Withings API for given user IDs.
        Publish new data to relevant topics. RPC functionality provides an interface
        for new clients to get up-to-date data relevant to their needs.
        '''
        api_token  = "4d81fb1981978544dfc3fe06cd93fec9004727d14bd4d26669c2be0333529"
        api_secret = "7234060961cf43bff9064c2d5c4361bfb460227470c7506bc54dd77f0070"

        #fetch initial datasets for userids
        for i in range (0, len(user_ids)):
            user_id = str(user_ids[i])
            if user_id == '0':
                continue
            credentials = WithingsCredentials(user_access_tokens[i], user_access_secret[i], api_token, api_secret, user_ids[i])
            withings_client = WithingsApi(credentials)
            energy_data[user_id], activity_data[user_id] = get_energy_and_activity(user_ids[i], withings_client)
            sleep_data[user_id] = get_sleep(user_ids[i], withings_client)
            heartrate_data[user_id], bloodpressure_data[user_id], bodytemperature_data[user_id] = get_measurement_data(user_ids[i], withings_client)

        while True:
            for i in range (0, len(user_ids)):
                user_id = str(user_ids[i])
                if user_id == '0':
                    continue

                #get credentials for this user and authenticate
                credentials = WithingsCredentials(user_access_tokens[i], user_access_secret[i], api_token, api_secret, user_id)
                withings_client = WithingsApi(credentials)

                today = datetime.date.today()

                measures = []
                temp_activity = {}
                temp_sleep = {}
                temp_bloodpressure = {}

                try:
                    #fetch updated data for this user:
                    temp_activity = withings_client.get_activity(date=today)
                    temp_sleep = withings_client.get_sleepsummary(startdateymd=today - datetime.timedelta(days=1), enddateymd=today)
                    for m in meastype: measures.append(withings_client.get_measures(limit=1, meastype=m))
                except ConnectionError:
                    self.log.error("Connection Error. Check connectivity and / or connection parameters and try again!")
                    yield sleep(60)
                    continue

                #parse for updates in activity and energy and publish data
                try:
                    for record in temp_activity['activities']:
                        date = parse(record['date']).strftime('%Y-%m-%d')
                        steps = record['steps']
                        calories = record['calories'] + record['totalcalories']
                        try:
                            position = get_list_index(activity_data[user_id], 0, date) #raises ValueError if date is not found
                            if activity_data[user_id][position][1] != steps:
                                self.log.info("publishing to 'Withings Activity Update' with {userid} {date} {old} -> {result}", userid=user_id, date=date, old=activity_data[user_id][position][1], result=steps)
                                activity_data[user_id] = update_list_entry(activity_data[user_id], date, steps)
                                yield self.publish('com.testlab.withings_activity_update', [user_id, date, steps])
                        except ValueError:
                            activity_data[user_id].append([date, steps])
                            yield self.publish('com.testlab.withings_activity_update', [user_id, date, steps])
                            self.log.info("publishing to 'Withings Activity Update' with {userid} {date} {result}", userid=user_id, date=date, result=steps)

                        try:
                            position = get_list_index(energy_data[user_id], 0, date) #raises ValueError if date is not found
                            if energy_data[user_id][position][1] != calories:
                                self.log.info("publishing to 'Withings Energy Update' with {userid} {date} {old} -> {result}", userid=user_id, date=date, old=energy_data[user_id][position][1], result=calories)
                                energy_data[user_id][get_list_index(activity_data[user_id], 0, date)][1] = calories
                                yield self.publish('com.testlab.withings_energy_update', [user_id, date, calories])
                        except ValueError:
                            energy_data[user_id].append([date, calories])
                            yield self.publish('com.testlab.withings_energy_update', [user_id, date, calories])
                            self.log.info("publishing to 'Withings Energy Update' with {userid} {date} {result}", userid=user_id, date=date, result=calories)
                except KeyError:
                    pass

                #parse for updates in sleep statistics and publish new data
                try:
                    for record in temp_sleep['series']:
                        date = parse(record['date']).strftime('%Y-%m-%d')
                        duration = (record['data']['deepsleepduration'] + record['data']['lightsleepduration']) / 60 / 60
                        try:
                            position = get_list_index(sleep_data[user_id], 0, date) #raises ValueError if date is not found
                            if sleep_data[user_id][position][1] != duration: #and the value is different than current
                                self.log.info("publishing to 'Withings Sleep Update' with {userid} {date} {old} -> {result}", userid=user_id, date=date, old=sleep_data[user_id][position][1], result=duration)
                                sleep_data[user_id][position][1] = duration #update the field and publish
                                yield self.publish('com.testlab.withings_sleep_update', [user_id, date, duration])
                        except ValueError:
                            sleep_data[user_id].append([date, duration])
                            yield self.publish('com.testlab.withings_sleep_update', [user_id, date, duration])
                            self.log.info("publishing to 'Withings Sleep Update' with {userid} {date} {result}", userid=user_id, date=date, result=duration)
                except KeyError:
                    pass

                #loop through measurements and publish new information if necessary
                for measure in measures:
                    for measuregroup in measure:
                        for result in measuregroup.measures:
                            date = measuregroup.date.strftime('%Y-%m-%d %H:%M:%S')
                            value = normalize_value(result['value'], result['unit'])

                            if(result["type"] == 11): #Average Heartrate
                                if len([item for item in heartrate_data[user_id] if item[0] == date]) >= 1:
                                    if heartrate_data[user_id][get_list_index(heartrate_data[user_id], 0, date)][1] != value:
                                        self.log.info("publishing to 'Withings HR Update' with {userid} {date} {old} -> {result}", userid=user_id, date=date, old=heartrate_data[user_id][get_list_index(heartrate_data[user_id], 0, date)][1], result=value)
                                        heartrate_data[user_id][get_list_index(heartrate_data[user_id], 0, date)][1] = value
                                        yield self.publish('com.testlab.withings_heartrate_update', [user_id, date, value])
                                else:
                                    self.log.info("publishing to 'Withings HR Update' with {userid} {date} {result}", userid=user_id, date=date, result=value)
                                    heartrate_data[user_id].append([date, value])
                                    yield self.publish('com.testlab.withings_heartrate_update', [user_id, date, value])

                            elif(result["type"] == 71): #Body Temperature

                                #form a temp data variable from this update for InterSystems
                                temp_data = {}
                                temp_data[user_id] = []
                                temp_data[user_id].append([date, value])                                        
                                temp_data = format_measurement_data_to_intersystems(temp_data, user_id, "bodyTemp")   

                                if len([item for item in bodytemperature_data[user_id] if item[0] == date]) >= 1:
                                    if bodytemperature_data[user_id][get_list_index(bodytemperature_data[user_id], 0, date)][1] != value:
                                        self.log.info("publishing to 'Withings BodyTemp Update' with {userid} {date} {old} -> {result}", userid=user_id, date=date, old=bodytemperature_data[user_id][get_list_index(bodytemperature_data[user_id], 0, date)][1], result=value)
                                        bodytemperature_data[user_id][get_list_index(bodytemperature_data[user_id], 0, date)][1] = value
                                        yield self.publish('com.testlab.withings_bodytemp_update', [user_id, date, value])

                                        self.log.info("publishing to Intersystems a new Temp reading")
                                        print(json.dumps(temp_data))    
                                        result = crossbar_client.publish('com.testlab.withings_healthconnect_bodytemp_update', ["test"])#json.dumps(temp_data))  
                                        print(result)                  
                                        #yield self.publish('com.testlab.withings_healthconnect_bodytemp_update', json.dumps(temp_data))
                                else:
                                    self.log.info("publishing to 'Withings BodyTemp Update' with {userid} {date} {result}", userid=user_id, date=date, result=value)
                                    bodytemperature_data[user_id].append([date, value])
                                    yield self.publish('com.testlab.withings_bodytemp_update', [user_id, date, value])

                                    self.log.info("publishing to Intersystems a new Temp reading")
                                    print(json.dumps(temp_data))       
                                    result = crossbar_client.publish('com.testlab.withings_healthconnect_bodytemp_update', ["test"])#json.dumps(temp_data))  
                                    print(result)                 
                                    #yield self.publish('com.testlab.withings_healthconnect_bodytemp_update', json.dumps(temp_data))

                            elif(result["type"] == 10): #Systolic BP
                                temp_bloodpressure[date] = []
                                temp_bloodpressure[date].append(value)

                            elif(result["type"] == 9): #Diastolic BP
                                temp_bloodpressure[date].append(value)

                                #form a temp data variable from this update for InterSystems
                                temp_data = {}
                                temp_data[user_id] = []
                                temp_data[user_id].append([date, temp_bloodpressure[date]])
                                temp_data = format_measurement_data_to_intersystems(temp_data, user_id, "bloodPressure")                               
                                
                                if len([item for item in bloodpressure_data[user_id] if item[0] == date]) >= 1:
                                    if len(set(bloodpressure_data[user_id][get_list_index(bloodpressure_data[user_id], 0, date)][1]).intersection(temp_bloodpressure[date])) < 2: #check if bloodpressure readings are identical. If not, update
                                        self.log.info("publishing to 'Withings BP Update' with {date} {old} -> {result}", date=date, old=bloodpressure_data[user_id][get_list_index(bloodpressure_data[user_id], 0, date)][1], result=temp_bloodpressure[date])
                                        bloodpressure_data[user_id][get_list_index(heartrate_data[user_id], 0, date)][1] = temp_bloodpressure[date]
                                        yield self.publish('com.testlab.withings_bloodpressure_update', [user_id, date, temp_bloodpressure[date]])

                                        #send data to intersystems over the http-bridge
                                        self.log.info("publishing to Intersystems a new BP reading")
                                        result = crossbar_client.publish('com.testlab.withings_healthconnect_bloodpressure_update', event=json.dumps(temp_data))
                                        #yield self.publish('com.testlab.withings_healthconnect_bloodpressure_update', json.dumps(temp_data))
                                else:
                                    self.log.info("publishing to 'Withings BP Update' with {userid} {date} {result}", userid=user_id, date=date, result=temp_bloodpressure[date])
                                    bloodpressure_data[user_id].append([date, temp_bloodpressure[date]])
                                    yield self.publish('com.testlab.withings_bloodpressure_update', [user_id, date, temp_bloodpressure[date]])

                                    #send data to intersystems over the http-bridge
                                    self.log.info("publishing to Intersystems a new BP reading")
                                    result = crossbar_client.publish('com.testlab.withings_healthconnect_bloodpressure_update', event=json.dumps(temp_data))
                                    #yield self.publish('com.testlab.withings_healthconnect_bloodpressure_update', json.dumps(temp_data))
            yield sleep(30)
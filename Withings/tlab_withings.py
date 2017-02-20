#!/usr/bin/python3.4
#  -*- coding: UTF-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

from builtins import input
from builtins import str
from builtins import range

from withings import WithingsCredentials, WithingsApi
import logging
import datetime
import time
import codecs
import sys

#autobahn for websockets
import autobahn

from collections import OrderedDict
from dateutil.parser import parse
from optparse import OptionParser
parser = OptionParser()
parser.add_option("--userid", dest="userid", default="12762571")
parser.add_option("--access-token", dest="access_token", default="18c90ec9d3559655e4bce5855bd3829648b89b2451f0b39c58ff55c2341e")
parser.add_option("--access-secret", dest="access_secret", default="efbdeb586bcbc59d0725214d3b5d2805c18022dd2fe3d5f9c91323c3eeb34d")
parser.add_option("--api-key", dest="api_key", default="4d81fb1981978544dfc3fe06cd93fec9004727d14bd4d26669c2be0333529")
parser.add_option("--api-secret", dest="api_secret", default="7234060961cf43bff9064c2d5c4361bfb460227470c7506bc54dd77f0070")
(options, args) = parser.parse_args()

#configure logging
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s', )

#disable urllib3 debug logging
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("withings").setLevel(logging.WARNING)
logging.getLogger("requests_oauthlib").setLevel(logging.WARNING)
logging.getLogger("oauthlib").setLevel(logging.WARNING)

def normalize_value(value, unit):
    return value * pow(10, unit)

if __name__ == "__main__":
    logging.debug("Welcome to Withings API toolkit")

    #ids, access tokens and secrets for our test users
    user_ids = [0, 12762562, 12762571, 12762926]

    user_access_tokens = ["2c9ebd310b36190955e054d5887de3402714070f67ec686d13f1dde9f2298",
                          "d2bd0d043f35624cd72fc7307bd587fb95dee536fee90157674ec0dc3724f",
                          "18c90ec9d3559655e4bce5855bd3829648b89b2451f0b39c58ff55c2341e",
                          "41d42276fce073530544e8bbd40fe0c88343867d208523f60062958d571"]

    user_access_secret = ["6e3b31ffd209fc82206939d2d59c28751759dd023e64bec198c0b7fcec99",
                          "357dff943d283c5f9e235cc2c3b1b305f2413d3bcc50b8812c2eb4c39",
                          "efbdeb586bcbc59d0725214d3b5d2805c18022dd2fe3d5f9c91323c3eeb34d",
                          "9e9272f2e293f8e712267de68c939f4722ee936d45f28b8024d588396c7542"]

    #get epoch times for today and last week
    now_epoch_time = int(time.time())
    two_weeks_epoch_time = now_epoch_time - (7 * 86400) #substract 7 days in seconds
    # time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(1347517370)) #epoch to date

    #get real dates for today and last week because withings API is inconsistent
    today = datetime.date.today()
    timedelta = today - datetime.timedelta(days=30)

    logging.debug("Epoch Now: " + str(now_epoch_time))
    logging.debug("Epoch Week earlier: " + str(two_weeks_epoch_time))
    logging.debug("Now: " + str(today))
    logging.debug("Week earlier: " + str(timedelta))

    for i in range (0, len(user_ids)):
        
        if user_ids[i] == 0:
            continue

        user_id = user_ids[i]
        logging.debug("Accessing Withings API for userID: " + str(user_id))
        credentials = WithingsCredentials(user_access_tokens[i], user_access_secret[i], options.api_key, options.api_secret, user_id)
        client = WithingsApi(credentials)

        measures        = []
        activity        = None
        sleep           = None
        sleep_summary   = None

        #get Activity Statistics for the last week.
        activity = client.get_activity(startdateymd=timedelta, enddateymd=today)
        ordered = OrderedDict()
        for record in activity['activities']:
            ordered[record['date']] = record['steps']

        #get Sleep Statistics
        #sleep = client.get_sleep(startdate=two_weeks_epoch_time, enddate=now_epoch_time)

        #get Sleep Summary
        sleep_summary = client.get_sleepsummary(startdateymd=timedelta, enddateymd=today)

        #write fetched data to a CSV file for further processing
        with codecs.open(str(user_id) + "_steps_per_day.csv", "w", "utf-8") as f:
            f.write("Date,Steps\n")
            for record in ordered.items():
                logging.debug("Activity: " + str(record[0]) + " " + str(record[1]))
                f.write(str(record[0]) + "," + str(record[1]) + "\n")

        with codecs.open(str(user_id) + "_calories_per_day.csv", "w", "utf-8") as f:
            f.write("Date,Calories\n")        
            for record in activity['activities']:
                f.write(str(record['date']) + "," + str(record['totalcalories'] + record['calories']) + "\n")

        with codecs.open(str(user_id) + "_sleep_summary.csv", "w", "utf-8") as f:
            f.write("Date,Duration\n")
            last_measurement = datetime.datetime.fromtimestamp(0)
            this_measurement = None
            for record in sleep_summary['series']:
                this_measurement = parse(record['date'])
                if last_measurement < this_measurement:
                    f.write(record['date'] + "," + str((record['data']['deepsleepduration'] + record['data']['lightsleepduration']) / 60 / 60) + "\n")
                last_measurement = this_measurement

        #get Users Body Measurements
        limit = 20                    #get last 20 measurements
        meastype = [1, 10, 9, 11, 71] #weight, systolic / diastolic blood pressure, average pulse, body temperature    
        for m in meastype:
            measures.append(client.get_measures(limit=limit, meastype=m))

        logging.debug("")
        logging.debug("Parsing last " + str(limit) + " measures (measurement type(s)=" + str(meastype) + "):")
        logging.debug("-----------------")

        with codecs.open(str(user_id) + "_bodytemperature.csv", "w", "utf-8") as f:
            f.write("Index,Temperature\n")        

        avg_heartrate = {}
        bodytemp = {}
        bp = {}

        for measure in measures:
            index = 0
            for group in measure:
                for result in group.measures:
                    if(result["type"] == 1):
                        logging.debug("Weight: " + str(normalize_value(result['value'], result['unit'])) + "kg")                                   
                    elif(result["type"] == 11):
                        avg_heartrate[index] = normalize_value(result['value'], result['unit'])
                        index += 1
                    elif(result["type"] == 12): #Room temp
                        logging.debug("Temperature: " + str(normalize_value(result['value'], result['unit'])) + "C") 
                    elif(result["type"] == 71): #Body temp
                        bodytemp[index] = normalize_value(result['value'], result['unit'])
                        index += 1
                    elif(result["type"] == 10): #Systolic BP
                        bp[index] = []
                        bp[index].append(normalize_value(result['value'], result['unit']))
                        index += 1                        
                    elif(result["type"] == 9): #Diastolic BP
                        bp[index].append(normalize_value(result['value'], result['unit']))
                        index += 1
                    else:
                        logging.debug("Unknown measurement: " + str(normalize_value(result['value'], result['unit'])))
            logging.debug("-----------------")
        
        with codecs.open(str(user_id) + "_bodytemperature.csv", "w", "utf-8") as f:
            f.write("Index,Temperature\n")
            for item in bodytemp.items():
                f.write(str(item[0]) + "," + str(item[1]) + "\n")

        with codecs.open(str(user_id) + "_bloodpressure.csv", "w", "utf-8") as f:
            f.write("Index,Systolic,Diastolic\n")
            for item in bp.items():
                f.write(str(item[0]) + "," + str(item[1][0]) + "," + str(item[1][1]) + "\n")
        
        with codecs.open(str(user_id) + "_heartrate.csv", "w", "utf-8") as f:
            f.write("Index,Rate\n")
            for item in avg_heartrate.items():
                f.write(str(item[0]) + "," + str(item[1]) + "\n")
    
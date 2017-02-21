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

#access tokens and secrets.
from tlab_tokens import user_access_tokens, user_access_secret

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
    logging.debug("-------")

    #ids, access tokens and secrets for our test users
    user_ids = [0, 12762562, 12762571, 12762926]

    #get epoch times for today and last week
    now_epoch_time = int(time.time())
    two_weeks_epoch_time = now_epoch_time - (7 * 86400) #substract 7 days in seconds
    # time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(1347517370)) #epoch to date

    #get dates instead of epoch because withings API is inconsistent
    today = datetime.date.today()
    timedelta = today - datetime.timedelta(days=30)

    try:
        for i in range (0, len(user_ids)):
            
            if user_ids[i] == 0:
                continue

            user_id = user_ids[i]
            logging.debug("Accessing Withings API for userID: " + str(user_id))
            credentials = WithingsCredentials(user_access_tokens[i], user_access_secret[i], options.api_key, options.api_secret, user_id)
            client = WithingsApi(credentials)

            measures        = []              #list to contain measurement objects
            limit           = 20              #get last 20 measurements
            meastype        = [10, 9, 11, 71] #weight (1), systolic / diastolic blood pressure (10 & 9), average pulse (11), body temperature (71)              
            activity        = None
            sleep           = None
            sleep_summary   = None
 
            #dictionaries to hold measurement data 
            avg_heartrate   = {}
            bodytemp        = {}
            bp              = {}
            steps           = {}
            calories        = {}

            #fetch all the necessary data:
            activity = client.get_activity(startdateymd=timedelta, enddateymd=today)            #get step & calorie statistics
            sleep_summary = client.get_sleepsummary(startdateymd=timedelta, enddateymd=today)   #get sleep summary statistics
            for m in meastype: measures.append(client.get_measures(limit=limit, meastype=m))    #get various of user body measurements

            for record in activity['activities']:
                date = parse(record['date'])
                steps[date] = record['steps']
                calories[date] = record['calories'] + record['totalcalories']
            
            logging.debug("Parsing last " + str(limit) + " measures (measurement type(s)=" + str(meastype) + "):")

            for measure in measures:
                index = 0
                for group in measure:
                    for result in group.measures:                                
                        if(result["type"] == 11): #Average Heartrate
                            avg_heartrate[index] = normalize_value(result['value'], result['unit'])
                            index += 1
                        elif(result["type"] == 71): #Body Temperature
                            bodytemp[index] = normalize_value(result['value'], result['unit'])
                            index += 1
                        elif(result["type"] == 10): #Systolic BP
                            bp[index] = []
                            bp[index].append(normalize_value(result['value'], result['unit']))
                            index += 1                        
                        elif(result["type"] == 9): #Diastolic BP
                            bp[index].append(normalize_value(result['value'], result['unit']))
                            index += 1        

            logging.debug("Done! Outputting data to CSV")
            logging.debug("")

            #write fetched data to a CSV file for further processing
            #daily steps data
            with codecs.open(str(user_id) + "_steps_per_day.csv", "w", "utf-8") as f:
                f.write("Date,Steps\n")
                for record in sorted(steps):
                    f.write(str(record) + "," + str(steps[record]) + "\n")

            #daily calorie burn
            with codecs.open(str(user_id) + "_calories_per_day.csv", "w", "utf-8") as f:
                f.write("Date,Calories\n")        
                for record in sorted(calories):
                    f.write(str(record) + "," + str(calories[record]) + "\n")

            #daily sleep duration
            with codecs.open(str(user_id) + "_sleep_summary.csv", "w", "utf-8") as f:
                f.write("Date,Duration\n")
                last_measurement = datetime.datetime.fromtimestamp(0)
                this_measurement = None
                for record in sleep_summary['series']:
                    this_measurement = parse(record['date'])
                    if last_measurement < this_measurement:
                        f.write(record['date'] + "," + str((record['data']['deepsleepduration'] + record['data']['lightsleepduration']) / 60 / 60) + "\n")
                    last_measurement = this_measurement

            #body temperature readings
            with codecs.open(str(user_id) + "_bodytemperature.csv", "w", "utf-8") as f:
                f.write("Index,Temperature\n")
                for record in sorted(bodytemp):
                    f.write(str(record) + "," + str(bodytemp[record]) + "\n")

            #bloodpressure readings
            with codecs.open(str(user_id) + "_bloodpressure.csv", "w", "utf-8") as f:
                f.write("Index,Systolic,Diastolic\n")
                for record in sorted(bp):
                    f.write(str(record) + "," + str(bp[record][0]) + "," + str(bp[record][1]) + "\n")
            
            #average heartrate
            with codecs.open(str(user_id) + "_heartrate.csv", "w", "utf-8") as f:
                f.write("Index,Rate\n")
                for record in sorted(avg_heartrate):
                    f.write(str(record) + "," + str(avg_heartrate[record]) + "\n")
        logging.debug("Done. Goodbye!")
    except KeyboardInterrupt:
        logging.debug("Interrupted. Goodbye!")
        sys.exit(0)    
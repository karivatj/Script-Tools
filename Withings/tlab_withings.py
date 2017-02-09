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

#autobahn for websockets
import autobahn

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
    limit = 10
    meastype = [1]
    logging.debug("Welcome to Withings API toolkit")
    logging.debug("Accessing Withings API for userID: " + options.userid)
    credentials = WithingsCredentials(options.access_token, options.access_secret, options.api_key, options.api_secret, options.userid)
    client = WithingsApi(credentials)

    measures        = None
    activity        = None
    sleep           = None
    sleep_summary   = None

    #get epoch times for today and last week
    now_epoch_time = int(time.time())
    two_weeks_epoch_time = now_epoch_time - (7 * 86400) #substract 7 days in seconds
    # time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(1347517370)) #epoch to date

    #get real dates for today and last week because withings API is inconsistent
    today = datetime.date.today()
    two_weeks_ago = today - datetime.timedelta(days=7)

    logging.debug("Epoch Now: " + str(now_epoch_time))
    logging.debug("Epoch Week earlier: " + str(two_weeks_epoch_time))
    logging.debug("Now: " + str(today))
    logging.debug("Week earlier: " + str(two_weeks_ago))

    #get Activity Statistics for the last week.
    activity = client.get_activity(startdateymd=two_weeks_ago, enddateymd=today)

    #get Sleep Statistics
    #sleep = client.get_sleep(startdate=two_weeks_epoch_time, enddate=now_epoch_time)

    #get Sleep Summary
    sleep_summary = client.get_sleepsummary(startdateymd=two_weeks_ago, enddateymd=today)

    #write fetched data to a CSV file for further processing
    with codecs.open(str(options.userid) + "_steps_per_day.csv", "w", "utf-8") as f:
        f.write("Date,Steps\n")
        for record in activity['activities']:
            f.write(str(record['date']) + "," + str(record['steps']) + "\n")
    with codecs.open(str(options.userid) + "_calories_per_day.csv", "w", "utf-8") as f:
        f.write("Date,Calories\n")        
        for record in activity['activities']:
            f.write(str(record['date']) + "," + str(record['totalcalories'] + record['calories']) + "\n")
    with codecs.open(str(options.userid) + "_sleep_summary.csv", "w", "utf-8") as f:
        f.write("Date,Duration\n")
        for record in sleep_summary['series']:
            f.write(record['date'] + "," + str((record['data']['deepsleepduration'] + record['data']['lightsleepduration']) / 60 / 60) + "\n")
    """
    #get Users Body Measurements 
    measures = client.get_measures(limit=limit, meastype=meastype, startdate=two_weeks_epoch_time, enddate=now_epoch_time)

    #logging.debug(activity)
    #logging.debug(sleep)
    #logging.debug(sleep_summary)

    logging.debug("")
    logging.debug("Parsing last " + str(limit) + " measures (measurement type=" + str(meastype) + ":")
    logging.debug("-----------------")
    for group in range(0, len(measures)):
        for m in measures[group].measures:
            if(m["type"] == 1):
                logging.debug("Weight: " + str(normalize_value(m['value'], m['unit'])) + "kg")             
            if(m["type"] == 4):
                logging.debug("Height: " + str(normalize_value(m['value'], m['unit']) * 100) + "cm")                       
            if(m["type"] == 11):
                logging.debug("Pulse: " + str(normalize_value(m['value'], m['unit'])) + "bpm")                 
            if(m["type"] == 12):
                logging.debug("Temperature: " + str(normalize_value(m['value'], m['unit'])) + "C") 
            if(m["type"] == 71):
                logging.debug("Body Temperature: " + str(normalize_value(m['value'], m['unit'])) + "C") 
            if(m["type"] == 73):
                logging.debug("Skin Temperature: " + str(normalize_value(m['value'], m['unit'])) + "C") 
    logging.debug("-----------------")
    """
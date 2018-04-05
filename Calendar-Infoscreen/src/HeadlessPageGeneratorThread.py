#!/usr/bin/python3.4
#  -*- coding: UTF-8 -*-

from __future__ import print_function
from builtins import str
from threading import Thread

import codecs
import logging
import os
import traceback

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from datetime import timedelta
from exchangelib import EWSDateTime, EWSTimeZone, DELEGATE, Account, Credentials, NTLM, Configuration
from exchangelib.protocol import BaseProtocol, NoVerifyHTTPAdapter

import WebpageTemplate

# setup logging
logger = logging.getLogger('infoscreen')

class HeadlessPageGeneratorThread(Thread):
    exiting = False
    calendars = {}
    workdirectory = os.getcwd()
    credentials = None
    config = None

    def __init__(self, calendars, username, password, server, ignoreSSL, workdir):
        Thread.__init__(self)
        self.calendars = calendars
        self.workdirectory = workdir
        try:
            if int(ignoreSSL) == 2:
                logger.info("Using unverified HTTP adapter. Please reconsider!")
                BaseProtocol.HTTP_ADAPTER_CLS = NoVerifyHTTPAdapter

            self.credentials = Credentials(username=str(username), password=str(password))
            self.config = Configuration(service_endpoint=str(server), credentials=self.credentials, auth_type=NTLM)
        except Exception as e:
            logger.debug("Failed to connect to EWS server. Check your settings: {0}".format(traceback.print_exc()))
            self.exiting = True

    def __del__(self):
        self.exiting = True

    def run(self):
        self.exiting = False
        self.work()

    def get_appointments(self, acc):
        # define the timezone
        tz = EWSTimeZone.timezone('Europe/Helsinki')
        now = tz.localize(EWSDateTime.now())

        items = {}

        try:
            logger.debug("Getting appointments")
            items = acc.calendar.view(
                start=tz.localize(EWSDateTime(now.year, now.month, now.day, 6, 0)),
                end=tz.localize(EWSDateTime(now.year, now.month, now.day, 18, 0)),
            )
            logger.debug("Getting appointments was a success")
            return items, True
        except Exception as e:
            logger.error("Failed to get appointments. Trying again later. Error: {0}".format(traceback.print_exc()))
            return items, False

    def work(self):
        logger.debug("Starting work thread")
        calendar_data = {} #dictionary containing the data

        try:
            for key, value in self.calendars.items():
                calendar_name  = key
                calendar_email = value

                logger.debug("Fetching data for calendar: {0}".format(calendar_name))
                logger.debug("Setting up EWS account for calendar: {0}".format(calendar_email))

                try:
                    account = Account(primary_smtp_address=str(calendar_email), config=self.config, autodiscover=False, access_type=DELEGATE)
                except Exception as e:
                    logger.error("Failure: {0}".format(traceback.print_exc()))
                    continue

                calendar_data[calendar_name], result = self.get_appointments(account)

                if result is not True:
                    logger.error("Failed to fetch calendar data for calendar: {0}".format(calendar_email))

                logger.debug("Done with calendar: {0}".format(calendar_email))
        except Exception as e:
            logger.debug("General failure occured when fetching calendar data! Error: {0}".format(traceback.print_exc()))
            return

        logger.debug("Calendar data retrieved. Outputting webpage...")
        #calendar_data = collections.OrderedDict(sorted(calendar_data.items(), key=lambda t: t[0]))

        if not os.path.exists(self.workdirectory + "/web/"):
            os.makedirs(self.workdirectory + "/web/")

        try:
            content = ""
            content += "<table>\n"
            content += "<colgroup\n"
            content += "<col class=\"column10\"/>\n"
            content += "<col class=\"column30\"/>\n"
            content += "<col class=\"column15\"/>\n"
            content += "<col class=\"column30\"/>\n"
            content += "<col class=\"column15\"/>\n"
            content += "</colgroup>\n"
            content += "<tr>"
            content += "<th>Huone</th>"
            content += "<th>Tällä hetkellä / Seuraavaksi</th>"
            content += "<th></th>"
            content += "<th>Myöhemmin tänä päivänä</th>"
            content += "<th></th>"
            content += "</tr>"

            now = EWSDateTime.now()

            for calendar in calendar_data:
                primary_event_found = False
                secondary_event_found = False
                content += "<tr>\n"
                content += "<td class=\"meetingroom\">" + calendar + "</td>\n"

                delta = 2
                if now > EWSDateTime(now.year, 3, 26, 3, 0, 0) and now < EWSDateTime(now.year, 10, 29, 4, 0, 0):
                    delta = 3

                try:
                    for item in calendar_data[calendar]:

                        #logger.debug(item)
                        subject = item.subject
                        if subject is None or subject is "":
                            subject = "Varaus ilman otsikkoa"

                        logger.debug(calendar + " " + subject)
                        start_time = EWSDateTime(item.start.year, item.start.month, item.start.day, item.start.hour, item.start.minute, 0) + timedelta(hours=delta)
                        end_time = EWSDateTime(item.end.year, item.end.month, item.end.day, item.end.hour, item.end.minute, 0) + timedelta(hours=delta)
                        if(now < end_time and primary_event_found == False):
                            primary_event_found = True
                            content += "<td class=\"event_primary\">" + str(subject) + "</td>\n"
                            content += "<td class=\"eventdate_primary\">%d:%02d - %d:%02d</td>\n" % (start_time.hour, start_time.minute, end_time.hour, end_time.minute)
                        elif(now < end_time and secondary_event_found == False):
                            secondary_event_found = True
                            content += "<td class=\"event_secondary\">" + str(subject) + "</td>\n"
                            content += "<td class=\"eventdate_secondary\">%d:%02d - %d:%02d</td>\n" % (start_time.hour, start_time.minute, end_time.hour, end_time.minute)
                            break
                except Exception as e: # failure in data communication
                    logger.error("Failed to parse calendar data: {0}".format(traceback.print_exc()))
                    content += "<td class=\"event_primary\">Virhe tiedonsiirrossa</td>\n"
                    content += "<td class=\"eventdate_primary\"></td>\n"
                    content += "<td class=\"event_secondary\">Virhe tiedonsiirrossa</td>\n"
                    content += "<td class=\"eventdate_secondary\"></td>\n"
                    primary_event_found = True
                    secondary_event_found = True
                    continue

                if(primary_event_found != True):
                    logger.debug("Ei varauksia kalenterille " + calendar)
                    content += "<td class=\"event_primary\">Vapaa</td>\n"
                    content += "<td class=\"eventdate_primary\"></td>\n"
                if(secondary_event_found != True):
                    logger.debug("Ei toissijaisia kalenterille " + calendar)
                    content += "<td class=\"event_secondary\">Vapaa</td>\n"
                    content += "<td class=\"eventdate_secondary\"></td>\n"

                content += "</tr>\n"
            content += "</table>"

            webpage = WebpageTemplate.template
            webpage = webpage.replace("%REPLACE_THIS_WITH_CONTENT%", content)

            with codecs.open(self.workdirectory + "/web/index.html", "w+", "utf-8") as f:
                f.write(webpage)
            with codecs.open(self.workdirectory + "/web/stylesheet.css", "w+", "utf-8") as f:
                f.write(WebpageTemplate.css_template)

        except Exception:
            logger.error("Failure during content output: {0}".format(traceback.print_exc()))
            return

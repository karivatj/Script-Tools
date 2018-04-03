#!/usr/bin/python3.4
#  -*- coding: UTF-8 -*-

from __future__ import print_function
from builtins import str

import codecs
import collections
import logging
import os
import requests
import traceback

from datetime import timedelta

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal

from exchangelib import EWSDateTime, EWSTimeZone, DELEGATE, Account, Credentials, NTLM, Configuration
from exchangelib.protocol import BaseProtocol, NoVerifyHTTPAdapter

# setup logging

from logging import handlers
logger = logging.getLogger('pagegenerator')
logger.setLevel(logging.DEBUG)

# create file handler which logs debug messages
fh = handlers.TimedRotatingFileHandler(os.getcwd() + '/logs/pagegenerator.log', when="d", interval=1, backupCount=7)
fh.setLevel(logging.DEBUG)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

from exchangelib.util import PrettyXmlHandler

logging.basicConfig(level=logging.DEBUG, handlers=[PrettyXmlHandler(), fh,ch])



class PageGeneratorThread(QtCore.QThread):
    #signals
    progress = pyqtSignal(int)
    statusupdate = pyqtSignal(int, str)

    exiting = False

    calendars = {}
    credentials = None
    config = None
    headless = False

    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.exiting = False

    def __del__(self):
        self.exiting = True
        self.wait()

    def startworking(self, calendars, username, password, server, ignoreSSL, headless):
        self.calendars = calendars
        try:
            if int(ignoreSSL) == 2:
                logger.info("Using unverified HTTP adapter")
                BaseProtocol.HTTP_ADAPTER_CLS = NoVerifyHTTPAdapter

            self.headless = headless

            self.credentials = Credentials(username=str(username), password=str(password))
            self.config = Configuration(service_endpoint=str(server), credentials=self.credentials, auth_type=NTLM)
            self.exiting = False
            self.start()
        except Exception as e:
            logger.debug("Failed to connect to EWS server. Check your settings: {0}".format(traceback.print_exc()))
            self.exiting = True

    def stopworking(self):
        self.exiting = True

    def run(self):
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

        progress_step = 100 / len(self.calendars)
        progress_now = 0

        #Get appointment data for each calendar
        try:
            for key, value in self.calendars.items():
                calendar_name  = key
                calendar_email = value

                logger.debug("Fetching data for calendar: {0}".format(calendar_name))
                logger.debug("Setting up EWS account for calendar: {0}".format(calendar_email))
                logger.debug("ACCOUNT DEBUG2")

                try:
                    logger.debug("ACCOUNT DEBUG3")
                    account = Account(primary_smtp_address=str(calendar_email), config=self.config, autodiscover=False, access_type=DELEGATE)
                    logger.debug("ACCOUNT DEBUG4")
                except Exception as e:
                    logger.error("Failure")
                    continue

                logger.debug("ACCOUNT DEBUG")
                logger.debug("Account : " + str(account))

                calendar_data[calendar_name], result = self.get_appointments(account)

                if result is not True:
                    logger.error("Failed to fetch calendar data for calendar: {0}".format(calendar_email))

                progress_now += progress_step
                if self.headless is not True:
                    self.progress.emit(progress_now)

                logger.debug("Done with calendar: {0}".format(calendar_email))
        except Exception as e:
            logger.debug("General failure occured when fetching calendar data! Error: {0}".format(traceback.print_exc()))
            if self.headless is not True:
                self.statusupdate.emit(-1, "Failure while fetching calendar data!")
                self.progress.emit(100)
            return

        logger.debug("Calendar data retrieved. Outputting webpage...")
        #calendar_data = collections.OrderedDict(sorted(calendar_data.items(), key=lambda t: t[0]))

        if not os.path.exists("./web/"):
            os.makedirs("./web/")

        try:
            with codecs.open("./web/content.html", "w", "utf-8") as f:
                f.write("<table>\n")
                f.write("<colgroup\n")
                f.write("<col class=\"column10\"/>\n")
                f.write("<col class=\"column30\"/>\n")
                f.write("<col class=\"column15\"/>\n")
                f.write("<col class=\"column30\"/>\n")
                f.write("<col class=\"column15\"/>\n")
                f.write("</colgroup>\n")
                f.write("<tr>")
                f.write("<th>Huone</th>")
                f.write("<th>Tällä hetkellä / Seuraavaksi</th>")
                f.write("<th></th>")
                f.write("<th>Myöhemmin tänä päivänä</th>")
                f.write("<th></th>")
                f.write("</tr>")

                now = EWSDateTime.now()

                for calendar in calendar_data:
                    primary_event_found = False
                    secondary_event_found = False
                    f.write("<tr>\n")
                    f.write("<td class=\"meetingroom\">" + calendar + "</td>\n")

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
                            logger.debug(start_time)
                            logger.debug(end_time)
                            logger.debug(now)
                            if(now < end_time and primary_event_found == False):
                                primary_event_found = True
                                f.write("<td class=\"event_primary\">" + str(subject) + "</td>\n")
                                f.write("<td class=\"eventdate_primary\">%d:%02d - %d:%02d</td>\n" % (start_time.hour, start_time.minute, end_time.hour, end_time.minute))
                            elif(now < end_time and secondary_event_found == False):
                                secondary_event_found = True
                                f.write("<td class=\"event_secondary\">" + str(subject) + "</td>\n")
                                f.write("<td class=\"eventdate_secondary\">%d:%02d - %d:%02d</td>\n" % (start_time.hour, start_time.minute, end_time.hour, end_time.minute))
                                break

                    except Exception as e: # failure in data communication
                        logger.error("Failed to parse calendar data: {0}".format(traceback.print_exc()))
                        f.write("<td class=\"event_primary\">Virhe tiedonsiirrossa</td>\n")
                        f.write("<td class=\"eventdate_primary\"></td>\n")
                        f.write("<td class=\"event_secondary\">Virhe tiedonsiirrossa</td>\n")
                        f.write("<td class=\"eventdate_secondary\"></td>\n")
                        primary_event_found = True
                        secondary_event_found = True
                        continue

                    if(primary_event_found != True):
                        logger.debug("Ei varauksia kalenterille " + calendar)
                        f.write("<td class=\"event_primary\">Vapaa</td>\n")
                        f.write("<td class=\"eventdate_primary\"></td>\n")
                    if(secondary_event_found != True):
                        logger.debug("Ei toissijaisia kalenterille " + calendar)
                        f.write("<td class=\"event_secondary\">Vapaa</td>\n")
                        f.write("<td class=\"eventdate_secondary\"></td>\n")

                    f.write("</tr>\n")
                f.write("</table>")
        except FileNotFoundError:
            logger.error("Failed to open file ./web/content.html. No such file or directory")
            if self.headless is not True:
                self.statusupdate.emit(-1, "Failed to open file ./web/content.html. No such file or directory")
                self.progress.emit(100)
            return

        if self.headless is not True:
            self.statusupdate.emit(1, "Calendar data succesfully fetched!")
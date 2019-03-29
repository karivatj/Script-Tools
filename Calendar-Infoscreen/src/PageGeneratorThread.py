#!/usr/bin/python3.4
#  -*- coding: UTF-8 -*-

from __future__ import print_function
from builtins import str

import codecs
import logging
import os
import traceback

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from exchangelib import EWSDateTime, EWSTimeZone, DELEGATE, Account, Credentials, NTLM, Configuration
from exchangelib.protocol import BaseProtocol, NoVerifyHTTPAdapter

import WebpageTemplate

# setup logging
logger = logging.getLogger('infoscreen')

class PageGeneratorThread(QtCore.QThread):
    #signals
    tz = EWSTimeZone.timezone('Europe/Helsinki')
    progress = pyqtSignal(int)
    statusupdate = pyqtSignal(int, str)

    exiting = False
    calendars = {}
    workdirectory = os.getcwd()
    credentials = None
    config = None

    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.exiting = False

    def __del__(self):
        self.exiting = True
        self.wait()

    def startworking(self, calendars, username, password, server, ignoreSSL, workdir):
        self.calendars = calendars
        self.workdirectory = workdir
        try:
            if int(ignoreSSL) == 2:
                logger.info("Using unverified HTTP adapter. Please reconsider!")
                BaseProtocol.HTTP_ADAPTER_CLS = NoVerifyHTTPAdapter

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
        now = EWSDateTime.now(self.tz)
        items = {}

        try:
            logger.debug("Getting appointments")
            items = acc.calendar.view(
                start=self.tz.localize(EWSDateTime(now.year, now.month, now.day, 4, 0)),
                end=self.tz.localize(EWSDateTime(now.year, now.month, now.day, 22, 0)),
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

                progress_now += progress_step
                self.progress.emit(progress_now)

                logger.debug("Done with calendar: {0}".format(calendar_email))
        except Exception as e:
            logger.debug("General failure occured when fetching calendar data! Error: {0}".format(traceback.print_exc()))
            self.statusupdate.emit(-1, "Failure while fetching calendar data!")
            self.progress.emit(100)
            return

        logger.debug("Calendar data retrieved. Outputting webpage...")

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

            now = self.tz.localize(EWSDateTime.utcnow())

            for calendar in calendar_data:
                primary_event_found = False
                secondary_event_found = False
                content += "<tr>\n"
                content += "<td class=\"meetingroom\">" + calendar + "</td>\n"

                try:
                    for item in calendar_data[calendar]:
                        subject = item.subject

                        item.start = item.start.astimezone(self.tz) #adjust timezone to local timezone
                        item.end = item.end.astimezone(self.tz) #adjust timezone to local timezone

                        if subject is None or subject is "":
                            subject = "Varaus ilman otsikkoa"

                        if(now < item.end and primary_event_found == False):
                            primary_event_found = True
                            content += "<td class=\"event_primary\">" + str(subject) + "</td>\n"
                            content += "<td class=\"eventdate_primary\">%s - %s</td>\n" % (item.start.strftime("%H:%M"), item.end.strftime("%H:%M"))

                        elif(now < item.end and secondary_event_found == False):
                            secondary_event_found = True
                            content += "<td class=\"event_secondary\">" + str(subject) + "</td>\n"
                            content += "<td class=\"eventdate_secondary\">%s - %s</td>\n" % (item.start.strftime("%H:%M"), item.end.strftime("%H:%M"))
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

            logger.debug("Updating webpage content!")

            with codecs.open(self.workdirectory + "/web/content.html", "w+", "utf-8") as f:
                f.write(content) # write the file first

            if os.path.isfile(self.workdirectory + "/web/index.html") is False: # if index.html already exists. Don't rewrite it constantly
                with codecs.open(self.workdirectory + "/web/index.html", "w+", "utf-8") as f:
                    f.write(WebpageTemplate.template.replace("%REPLACE_THIS_WITH_CONTENT%", ""))

            if os.path.isfile(self.workdirectory + "/web/stylesheet.css") is False: # if the stylesheet already exists. Don't rewrite it constantly
                with codecs.open(self.workdirectory + "/web/stylesheet.css", "w+", "utf-8") as f:
                    f.write(WebpageTemplate.css_template)

        except FileNotFoundError:
            logger.error("Failed to open files for page generation.")
            self.statusupdate.emit(-1, "Failed to open files for page generation.")
            self.progress.emit(100)
            return

        self.statusupdate.emit(1, "Calendar data succesfully fetched!")
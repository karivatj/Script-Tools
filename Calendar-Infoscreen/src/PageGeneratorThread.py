#!/usr/bin/python3.4
#  -*- coding: UTF-8 -*-

from __future__ import print_function
from builtins import str

import collections
import codecs

from datetime import timedelta

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal

from exchangelib import EWSDateTime, EWSTimeZone, DELEGATE, Account, Credentials, NTLM, Configuration

class PageGeneratorThread(QtCore.QThread):
    #signals
    progress = pyqtSignal(int)
    statusupdate = pyqtSignal(int, str)

    exiting = False

    calendar_list = list()
    credentials = None
    config = None
    account = None

    # define the timezone
    tz = EWSTimeZone.timezone('Europe/Helsinki')

    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.exiting = False

    def __del__(self):
        self.exiting = True
        self.wait()

    def startworking(self, calendars, username, password, server):
        self.calendar_list = calendars
        try:
            print(server)
            self.credentials = Credentials(username=username, password=password)
            self.config = Configuration(service_endpoint=server, credentials=self.credentials, auth_type=NTLM)
            self.exiting = False
            self.start()
        except Exception as e:
            print("Failed to connect to EWS server. Check your settings: {0}".format(e))
            self.exiting = True

    def stopworking(self):
        self.exiting = True

    def run(self):
        self.work()

    def get_appointments(self, account):
        now = self.tz.localize(EWSDateTime.now())

        items = {}

        try:
            items = account.calendar.view(
                start=self.tz.localize(EWSDateTime(now.year, now.month, now.day, 6, 0)),
                end=self.tz.localize(EWSDateTime(now.year, now.month, now.day, 18, 0)),
            ).order_by('start')
        except Exception as e:
            print("Failed to get appointments. Trying again later. Error: {0}".format(e))
            return items, False

        return items, True

    def work(self):
        calendar_data = {} #dictionary containing the data

        progress_step = 100 / len(self.calendar_list)
        progress_now = 0

        #Get appointment data for each calendar
        for calendar in self.calendar_list:
            calendar_name  = calendar[0]
            calendar_email = calendar[1]

            print("Fetching data for: " + calendar_name)

            # setup EWS account where the data is coming from
            self.account = Account(primary_smtp_address=calendar_email, config=self.config, autodiscover=False, access_type=DELEGATE)

            calendar_data[calendar_name], result = self.get_appointments(self.account)

            progress_now += progress_step
            self.progress.emit(progress_now)

            if result is not True:
                print("Failed to fetch calendar data.")

        print("Calendar data retrieved. Outputting webpage...")
        calendar_data = collections.OrderedDict(sorted(calendar_data.items(), key=lambda t: t[0]))

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
                            start_time = EWSDateTime(item.start.year, item.start.month, item.start.day, item.start.hour, item.start.minute, 0) + timedelta(hours=delta)
                            end_time = EWSDateTime(item.end.year, item.end.month, item.end.day, item.end.hour, item.end.minute, 0) + timedelta(hours=delta)
                            if(now < end_time and primary_event_found == False):
                                print(str(now) + " < " + str(end_time))
                                primary_event_found = True
                                f.write("<td class=\"event_primary\">" + item.subject + "</td>\n")
                                f.write("<td class=\"eventdate_primary\">%d:%02d - %d:%02d</td>\n" % (start_time.hour, start_time.minute, end_time.hour, end_time.minute))
                            elif(now < end_time and secondary_event_found == False):
                                secondary_event_found = True
                                f.write("<td class=\"event_secondary\">" + item.subject + "</td>\n")
                                f.write("<td class=\"eventdate_secondary\">%d:%02d - %d:%02d</td>\n" % (start_time.hour, start_time.minute, end_time.hour, end_time.minute))
                                break
                    except Exception as e: # failure in data communication
                        print("Failed to parse calendar data: {0}".format(e))
                        f.write("<td class=\"event_primary\">Virhe tiedonsiirrossa</td>\n")
                        f.write("<td class=\"eventdate_primary\"></td>\n")
                        f.write("<td class=\"event_secondary\">Virhe tiedonsiirrossa</td>\n")
                        f.write("<td class=\"eventdate_secondary\"></td>\n")
                        primary_event_found = True
                        secondary_event_found = True
                        break

                    if(primary_event_found != True):
                        f.write("<td class=\"event_primary\">Vapaa</td>\n")
                        f.write("<td class=\"eventdate_primary\"></td>\n")
                    if(secondary_event_found != True):
                        f.write("<td class=\"event_secondary\">Vapaa</td>\n")
                        f.write("<td class=\"eventdate_secondary\"></td>\n")

                    f.write("</tr>\n")
                f.write("</table>")
        except FileNotFoundError:
            print("Failed to open file ./web/content.html. No such file or directory")
            self.statusupdate.emit(-1, "Failed to open file ./web/content.html. No such file or directory")
            return

        self.statusupdate.emit(1, "Calendar data succesfully fetched!")
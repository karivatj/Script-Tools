#!/usr/bin/python3.4
#  -*- coding: UTF-8 -*-

from __future__ import print_function
from builtins import input
from builtins import str
from builtins import range

import collections
import codecs
import datetime
import logging
import requests
import sys

from dateutil.parser import parse
from requests_ntlm import HttpNtlmAuth
from xml.etree import ElementTree

#configure logging
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s', )

#content-type header must be this or server responds with 451
headers = {'Content-Type': 'text/xml; charset=utf-8'} # set what your server accepts

#date format
format = "%Y-%m-%d"

#Sample message used to query calendar data. Remember to replace relevant parts of this message
sample_getcalendar_request = '''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
       xmlns:m="http://schemas.microsoft.com/exchange/services/2006/messages" 
       xmlns:t="http://schemas.microsoft.com/exchange/services/2006/types" 
       xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Header>
    <t:RequestServerVersion Version="Exchange2010_SP2" />
  </soap:Header>
  <soap:Body>
    <m:FindItem Traversal="Shallow">
      <m:ItemShape>
        <t:BaseShape>IdOnly</t:BaseShape>
        <t:AdditionalProperties>
          <t:FieldURI FieldURI="item:Subject" />
          <t:FieldURI FieldURI="calendar:Start" />
          <t:FieldURI FieldURI="calendar:End" />
        </t:AdditionalProperties>
      </m:ItemShape>
      <m:CalendarView MaxEntriesReturned="10" StartDate="!Start_Date!" EndDate="!End_Date!" />
      <m:ParentFolderIds>
        <t:DistinguishedFolderId Id="calendar">
          <t:Mailbox>
            <t:EmailAddress>!Replace_Email_Of_Calendar!</t:EmailAddress>
          </t:Mailbox>
        </t:DistinguishedFolderId>
      </m:ParentFolderIds>
    </m:FindItem>
  </soap:Body>
</soap:Envelope>'''

def generateCalendarInfoScreen(calendar_list, username, password, server):
    calendar_data = {} #dictionary containing the data

    try:
        response = requests.get(server, auth=HttpNtlmAuth(username,password))
    except requests.exceptions.ConnectionError:
        logging.error("Error while connecting to EWS Service. Try again later!")
        return False

    if(response.status_code != 200):
        logging.error("Error while connecting to EWS Service. Try again later!")
        return False
    else:
        logging.debug("Connection OK - Continuing with the task")

    #Send a GetFolder request. Use Sample request as a template and replace necessary parts from it
    for calendar in calendar_list:
        calendar_name  = calendar[0]
        calendar_email = calendar[1]

        logging.debug("Creating field for " + calendar_name)
        calendar_data[calendar_name] = []

        logging.debug("Get Calendar: " + calendar_name)
        start_time = datetime.datetime.today().strftime(format) + "T00:00:00.000Z"
        end_time = datetime.datetime.today().strftime(format) + "T23:59:59.999Z"
        #logging.debug(start_time)
        #logging.debug(end_time)
        message = sample_getcalendar_request.replace("!Replace_Email_Of_Calendar!", calendar_email)
        message = message.replace("!Start_Date!", start_time)
        message = message.replace("!End_Date!", end_time)
        #logging.debug(message)
        
        try:
            response = requests.post(server, data=message, headers=headers, auth=HttpNtlmAuth(username, password))
        except requests.exceptions.ConnectionError:
            return False

        if(response.status_code != 200):
            logging.error("Error occured while fetching calendar: " + calendar[1])
            continue
        else:
            logging.debug("Response OK. Parsing data...")        
            tree = ElementTree.fromstring(response.content)
            today = datetime.datetime.now()
            timedelta = 2

            if today > datetime.datetime(datetime.date.today().year, 3, 26, 3, 0, 0) and today < datetime.datetime(datetime.date.today().year, 10, 29, 4, 0, 0):
                timedelta = 3    

            for elem in tree.iter(tag='{http://schemas.microsoft.com/exchange/services/2006/types}CalendarItem'):
                for child in elem:
                    print(child.text)
                    if("Subject" in child.tag):
                        calendar_data[calendar_name].append(child.text)
                    elif("Start" in child.tag):
                        date = parse(child.text)
                        date = date + datetime.timedelta(hours=timedelta) #add timedifference
                        calendar_data[calendar_name].append(date.strftime("%H:%M"))
                    elif("End" in child.tag):
                        date = parse(child.text)                   
                        date = date + datetime.timedelta(hours=timedelta) #add timedifference
                        calendar_data[calendar_name].append(date.strftime("%H:%M"))
        logging.debug("Success!")
        print()
             
    logging.debug("Calendar data retrieved. Outputting into HTML...")
    now = datetime.datetime.now()
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

                for calendar in calendar_data:
                    primary_event_found = False
                    secondary_event_found = False
                    f.write("<tr>\n")
                    f.write("<td class=\"meetingroom\">" + calendar + "</td>\n")

                    for item in range(0, len(calendar_data[calendar]), 3):
                        end_date = parse(calendar_data[calendar][item+2])
                        if(now < end_date and primary_event_found == False):
                            primary_event_found = True
                            f.write("<td class=\"event_primary\">" + calendar_data[calendar][item] + "</td>\n")
                            f.write("<td class=\"eventdate_primary\">"+ calendar_data[calendar][item+1] + " - " + calendar_data[calendar][item+2] + "</td>\n")

                        elif(now < end_date and secondary_event_found == False):
                            secondary_event_found = True
                            f.write("<td class=\"event_secondary\">" + calendar_data[calendar][item] + "</td>\n")
                            f.write("<td class=\"eventdate_secondary\">"+ calendar_data[calendar][item+1] + " - " + calendar_data[calendar][item+2] + "</td>\n")
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
        logging.error("Failed to open file ./dist/data.dat: No such file or directory")
        return False
    return True
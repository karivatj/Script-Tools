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
sample_getcalendar = '''<?xml version="1.0" encoding="utf-8"?>
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

#Calendars that are going to be parsed
calendar_list = ["RES_L3TestLab@ppshp.fi",
                 "RES_L3212Aortta@ppshp.fi",
                 "RES_L3213Cave@ppshp.fi",
                 "RES_L3215Lappa@ppshp.fi",
                 "RES_L3219OikKammio@ppshp.fi",
                 "RES_L3219AVasKammio@ppshp.fi",
                 "RES_L3223Pulssi@ppshp.fi",
                 "RES_L3228Laskimo@ppshp.fi",
                 "RES_L3229Valtimo@ppshp.fi"]

if __name__ == "__main__":
    logging.debug("Starting up...")
    calendar_data = {} #dictionary containing the data
    response = requests.get("https://sposti.ppshp.fi/EWS/Exchange.asmx",auth=HttpNtlmAuth('OYSNET\\TestLab_Res','CP3525dn%4x4'))
    if(response.status_code != 200):
        logging.error("Error while connecting to EWS Service. Try again later!")
        sys.exit(0)
    else:
        logging.debug("Connection OK - Continuing with the task")

    #Send a GetFolder request. Use Sample request as a template and replace necessary parts from it
    for calendar in calendar_list:
        calendar_name = ""

        if("TestLab" in calendar):
            calendar_name = "OYS TestLab"
        elif("Aortta" in calendar):
            calendar_name = "Aortta"
        elif("Cave" in calendar):
            calendar_name = "Cave"
        elif("Lappa" in calendar):
            calendar_name = "Läppä"
        elif("OikKammio" in calendar):
            calendar_name = "Oikea Kammio"
        elif("VasKammio" in calendar):
            calendar_name = "Vasen Kammio"
        elif("Pulssi" in calendar):
            calendar_name = "Pulssi"
        elif("Laskimo" in calendar):
            calendar_name = "Laskimo"
        elif("Valtimo" in calendar):
            calendar_name = "Valtimo"
        else:
            continue

        logging.debug("Creating field for " + calendar_name)
        calendar_data[calendar_name] = []

        logging.debug("Get Calendar: " + calendar_name)
        start_time = datetime.datetime.today().strftime(format) + "T00:00:00.000Z"
        end_time = datetime.datetime.today().strftime(format) + "T23:59:59.999Z"
        #logging.debug(start_time)
        #logging.debug(end_time)

        message = sample_getcalendar.replace("!Replace_Email_Of_Calendar!", calendar)
        message = message.replace("!Start_Date!", start_time)
        message = message.replace("!End_Date!", end_time)
        #logging.debug(message)
        
        response = requests.post("https://sposti.ppshp.fi/EWS/Exchange.asmx", data=message, headers=headers, auth=HttpNtlmAuth('OYSNET\\TestLab_Res','CP3525dn%4x4'))
        
        if(response.status_code != 200):
            logging.error("Error occured while fetching calendar: " + calendar)
            continue
        else:
            logging.debug("Response OK. Parsing data...")        
            tree = ElementTree.fromstring(response.content)

            for elem in tree.iter(tag='{http://schemas.microsoft.com/exchange/services/2006/types}CalendarItem'):
                for child in elem:
                    if("Subject" in child.tag):
                        calendar_data[calendar_name].append(child.text)
                    elif("Start" in child.tag):
                        date = parse(child.text)
                        date = date + datetime.timedelta(hours=2) #add timedifference
                        calendar_data[calendar_name].append(date.strftime("%H:%M"))
                    elif("End" in child.tag):
                        date = parse(child.text)
                        date = date + datetime.timedelta(hours=2) #add timedifference
                        calendar_data[calendar_name].append(date.strftime("%H:%M"))
        logging.debug("Success!")
        print()
             
    logging.debug("Calendar data retrieved. Outputting into HTML...")
    now = datetime.datetime.now()
    calendar_data = collections.OrderedDict(sorted(calendar_data.items(), key=lambda t: t[0]))

    with codecs.open("meetings.txt", "w", "utf-8") as f:
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
                f.write("<td class=\"meetingroom\" data-swiper-parallax=\"-200\">" + calendar + "</td>\n")

                for item in range(0, len(calendar_data[calendar]), 3):
                    end_date = parse(calendar_data[calendar][item+2])
                    if(now < end_date and primary_event_found == False):
                        primary_event_found = True
                        f.write("<td class=\"event_primary\" data-swiper-parallax=\"-200\">" + calendar_data[calendar][item] + "</td>\n")
                        f.write("<td class=\"eventdate_primary\" data-swiper-parallax=\"-200\">"+ calendar_data[calendar][item+1] + " - " + calendar_data[calendar][item+2] + "</td>\n")

                    elif(now < end_date and secondary_event_found == False):
                        secondary_event_found = True
                        f.write("<td class=\"event_secondary\" data-swiper-parallax=\"-200\">" + calendar_data[calendar][item] + "</td>\n")
                        f.write("<td class=\"eventdate_secondary\" data-swiper-parallax=\"-200\">"+ calendar_data[calendar][item+1] + " - " + calendar_data[calendar][item+2] + "</td>\n")
                        break
         
                if(primary_event_found != True):
                    f.write("<td class=\"event_primary\" data-swiper-parallax=\"-200\">Vapaa</td>\n")
                    f.write("<td class=\"eventdate_primary\" data-swiper-parallax=\"-200\"></td>\n")
                if(secondary_event_found != True):
                    f.write("<td class=\"event_secondary\" data-swiper-parallax=\"-200\">Vapaa</td>\n")
                    f.write("<td class=\"eventdate_secondary\" data-swiper-parallax=\"-200\"></td>\n")

                f.write("</tr>\n")
            f.write("</table>")

    logging.debug("Ready. Thank you and come again!")
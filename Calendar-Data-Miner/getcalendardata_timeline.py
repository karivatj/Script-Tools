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
import certifi

from auth_credentials import *
from dateutil.parser import parse
from requests_ntlm import HttpNtlmAuth
from xml.etree import ElementTree

# setup logging
# create logger with 'ipost_converter'
logger = logging.getLogger('getcalendardata')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('debug.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

# content-type header must be this or server responds with 451
headers = {'Content-Type': 'text/xml; charset=utf-8'} # set what your server accepts

# date format
format = "%Y-%m-%d"

# sample message used to query calendar data. Remember to replace relevant parts of this message
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

# calendars that are going to be parsed
calendar_list = ["calendar_email@domain.com"]

#  utility functions
def write_empty_node(f, node_index, group_index):
    f.write("<li class='work'>\n")
    f.write("<input class='radio' id='event" + str(node_index) + "' name='group" + str(group_index) + "' type='radio'>\n")
    f.write("<div class='relative'><label for='event" + str(node_index) + "'></label>\n")
    f.write("<span class='date'></span>\n")
    f.write("</div><div class='content'><p></p></div></li>\n")

def write_empty_node_type2(f, node_index, group_index):
    f.write("<li class='work'>\n")
    f.write("<input class='radio' id='event" + str(node_index) + "' name='group" + str(group_index) + "' type='radio'>\n")
    f.write("<div class='relative'><label for='event" + str(node_index) + "'></label>\n")
    f.write("<span class='date'></span>\n")
    f.write("</div><div class='content2'><p></p></div></li>\n")

def write_empty_node_prime(f, node_index, group_index):
    f.write("<li class='work'>\n")
    f.write("<input class='radio' id='event" + str(node_index) + "' name='group" + str(group_index) + "' type='radio' checked>\n")
    f.write("<div class='relative'><label for='event" + str(node_index) + "'></label>\n")
    f.write("<span class='date'></span>\n")
    f.write("</div><div class='content'><p></p></div></li>\n")    

def write_content_node(f, node_index, group_index, calendar, index):
    f.write("<li class='work'>\n")
    f.write("<input class='radio' id='event" + str(node_index) + "' name='group" + str(group_index) + "' type='radio'>\n")
    f.write("<div class='relative'><label for='event" + str(node_index) + "'>" + calendar[index] + "</label>\n")
    f.write("<span class='date'>" + calendar[index+1] + " - " + calendar[index+2] + "</span>\n")
    f.write("<span class='circle'></span></div><div class='content'><p></p></div></li>\n")

def write_content_node_prime(f, node_index, group_index, calendar, index):
    f.write("<li class='work'>\n")
    f.write("<input class='radio' id='event" + str(node_index) + "' name='group" + str(group_index) + "' type='radio' checked>\n")
    f.write("<div class='relative'><label for='event" + str(node_index) + "'>" + calendar[index] + "</label>\n")
    f.write("<span class='date'>" + calendar[index+1] + " - " + calendar[index+2] + "</span>\n")
    f.write("<span class='circle'></span></div><div class='content'><p></p></div></li>\n")

def write_content_node_prime_type2(f, node_index, group_index, calendar, index):
    f.write("<li class='work'>\n")
    f.write("<input class='radio2' id='event" + str(node_index) + "' name='group" + str(group_index) + "' type='radio' checked>\n")
    f.write("<div class='relative'><label for='event" + str(node_index) + "'>" + calendar[index] + "</label>\n")
    f.write("<span class='date'>" + calendar[index+1] + " - " + calendar[index+2] + "</span>\n")
    f.write("<span class='circle'></span></div><div class='content'><p></p></div></li>\n")

if __name__ == "__main__":
    logger.debug("Starting up...")
    calendar_data = {} #dictionary containing the data
    try:
        logger.info("Establishing connection to {0}...".format(server))
        response = requests.get(server, auth=HttpNtlmAuth(username, password), verify=certifi.where())
    except requests.exceptions.ConnectionError as e:
        logger.info("Connection error ({0})".format(e))
        sys.exit(0)

    if(response.status_code != 200):
        logger.error("Connection error. Status Code was {0}".format(response_status_code))
        sys.exit(0)
    else:
        logger.info("Connection OK - Continuing with the task")

    # Send a GetFolder request. Use Sample request as a template and replace necessary parts from it
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
            calendar_name = "Oik. Kammio"
        elif("VasKammio" in calendar):
            calendar_name = "Vas. Kammio"
        elif("Pulssi" in calendar):
            calendar_name = "Pulssi"
        elif("Laskimo" in calendar):
            calendar_name = "Laskimo"
        elif("Valtimo" in calendar):
            calendar_name = "Valtimo"
        else:
            continue

        logger.debug("Creating field for " + calendar_name)
        calendar_data[calendar_name] = []

        logger.debug("Get Calendar: " + calendar_name)
        start_time = datetime.datetime.today().strftime(format) + "T00:00:00.000Z"
        end_time = datetime.datetime.today().strftime(format) + "T23:59:59.999Z"
        
        message = sample_getcalendar.replace("!Replace_Email_Of_Calendar!", calendar)
        message = message.replace("!Start_Date!", start_time)
        message = message.replace("!End_Date!", end_time)
        
        response = requests.post(server, data=message, headers=headers, auth=HttpNtlmAuth(username, password), verify=certifi.where())
        
        if(response.status_code != 200):
            logger.error("Error occured while fetching calendar: " + calendar)
            continue
        else:
            logger.debug("Response OK. Parsing data...")        
            tree = ElementTree.fromstring(response.content)
            today = datetime.datetime.now()
            timedelta = 2
            
            if today > datetime.datetime(datetime.date.today().year, 3, 26, 3, 0, 0) and today < datetime.datetime(datetime.date.today().year, 10, 29, 4, 0, 0):
                timedelta = 3    

            office_endtime = datetime.datetime.now(datetime.timezone.utc).replace(hour=16,minute=0,second=0)
            start_time = None
            end_time = None
            subject = None

            for elem in tree.iter(tag='{http://schemas.microsoft.com/exchange/services/2006/types}CalendarItem'):
                for child in elem:
                    if("Subject" in child.tag):
                        subject = child.text                        
                    elif("Start" in child.tag):
                        start_time = parse(child.text)
                        start_time = start_time + datetime.timedelta(hours=timedelta) # add timedifference
                        if(end_time != None): # compare this start time to the previous end time
                            difference = abs(start_time - end_time)
                            if(difference.seconds > 0): # there is free time between the events
                                calendar_data[calendar_name].append("Vapaa") # add a slot indicating that the meetingroom is free
                                calendar_data[calendar_name].append(end_time.strftime("%H:%M"))
                                calendar_data[calendar_name].append((end_time + difference).strftime("%H:%M"))                          
                    elif("End" in child.tag):
                        end_time = parse(child.text)
                        end_time = end_time + datetime.timedelta(hours=2) # add timedifference   

                # add the event to the list 
                calendar_data[calendar_name].append(subject)
                calendar_data[calendar_name].append(start_time.strftime("%H:%M"))
                calendar_data[calendar_name].append(end_time.strftime("%H:%M"))

        if(end_time == None or end_time < office_endtime): # if theres nothing going on, just write a single event indicating the meetingroom is free for the day
            if(end_time == None):
                end_time = datetime.datetime.now(datetime.timezone.utc).replace(hour=8, minute=0, second=0)
            difference = office_endtime - end_time
            if(difference.seconds != 0):
                calendar_data[calendar_name].append("Vapaa")
                calendar_data[calendar_name].append(end_time.strftime("%H:%M"))
                calendar_data[calendar_name].append((end_time + difference).strftime("%H:%M"))

        logger.debug("Added " + str(len(calendar_data[calendar_name]) / 3) + " items. Success!")
        print()
             
    logger.debug("Calendar data retrieved. Outputting into HTML...")
    now = datetime.datetime.now()
    calendar_data = collections.OrderedDict(sorted(calendar_data.items(), key=lambda t: t[0]))

    node_index  = 0
    group_index = 0
    with codecs.open("meetings_timeline.txt", "w", "utf-8") as f:
        for calendar in calendar_data:
            f.write("<ul id='timeline'><span class='title'>" + calendar + "</span>\n")
            temp_calendar_data = []

            # read through the dictionaries and look for still active events and add it to temp_calendar list
            for index in range(0, len(calendar_data[calendar]), 3):
                event_end_time = parse(calendar_data[calendar][index + 2])
                if(now < event_end_time):
                    temp_calendar_data.append(calendar_data[calendar][index])
                    temp_calendar_data.append(calendar_data[calendar][index+1])
                    temp_calendar_data.append(calendar_data[calendar][index+2])

            data_length = len(temp_calendar_data) / 3

            if(data_length == 0): # after office hours no events so add a dummy event saying all rooms are available
                temp_calendar_data.append("Vapaa")
                temp_calendar_data.append("16:00")
                temp_calendar_data.append("")      

            if(data_length == 1):
                write_empty_node_type2(f, node_index, group_index)
                write_content_node_prime_type2(f, node_index+1, group_index, temp_calendar_data, 0)
                write_empty_node_type2(f, node_index+2, group_index)
                write_empty_node_type2(f, node_index+3, group_index)
                write_empty_node_type2(f, node_index+4, group_index)
            else:
                elements_written = 0
                first_element_written = False                
                index = 0                

                while elements_written < 5:
                    if first_element_written == False: # if we haven't written the first element yet, it should be a prime one e.g. checked
                        if(index < data_length and temp_calendar_data[index] == "Vapaa"): # first element should be an actual event, skip Free slots
                            index +=1
                            continue
                        if(index == data_length): # last node, special case
                            write_empty_node_type2(f, node_index, group_index)
                            logger.debug(len(temp_calendar_data))
                            logger.debug(index * 3)
                            logger.debug(calendar)
                            write_content_node_prime_type2(f, node_index+1, group_index, temp_calendar_data, index * 3)
                            write_empty_node_type2(f, node_index+2, group_index)
                            write_empty_node_type2(f, node_index+3, group_index)
                            write_empty_node_type2(f, node_index+4, group_index)      
                            break;
                        else: # else just write the content
                            write_content_node_prime(f, node_index, group_index, temp_calendar_data, index * 3)
                            first_element_written = True
                            elements_written += 1
                    elif index < data_length: # else just write a node containing some event information
                        write_content_node(f, node_index + index, group_index, temp_calendar_data, index * 3)   
                        elements_written += 1                     
                    else: # finally, just write a empty node to fill up the timeline
                        write_empty_node(f, node_index + index, group_index)
                        elements_written += 1
                    index += 1
            node_index += 5
            group_index += 1
            f.write("</ul>\n")

    logger.debug("Ready. Thank you and come again!")
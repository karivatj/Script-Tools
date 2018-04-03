# -*- coding: utf-8 -*-import argparse

import csv
import logging
import os
import requests
import sys
import traceback

from logging import handlers

logger = logging.getLogger('headless')
logger.setLevel(logging.DEBUG)

fh = handlers.TimedRotatingFileHandler(os.getcwd() + '/logs/headless.log', when="d", interval=1, backupCount=7)
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

def headless_load_preferences(fileinput):
    try:
        prefs = {}
        password = ""
        with open(fileinput, "r") as finput:
            reader = csv.reader(finput)
            for row in reader:
                items = [ str(field) for field in row ]
        for c in items[1]:
            password += chr(ord(c) - 5)

        prefs["password"]       = password
        prefs["username"]       = items[0]
        prefs["server"]         = items[2]
        prefs["serverport"]     = items[3]
        prefs["interval"]       = items[4]
        prefs["updatedata"]     = items[5]
        prefs["ignoreSSL"]      = items[6]
        prefs["lastusedconfig"] = items[7]

        return prefs
    except FileNotFoundError as e:
        logger.error("Could not load preferences from {0}. Reason: {1}".format(fileinput, traceback.print_exc()))
        return None

def headless_save_preferences(filename):
    pass

def headless_load_calendar_configuration(fileinput):
    try:
        calendars = {}
        with open(fileinput, "r") as finput:
            reader = csv.reader(finput)
            for row in reader:
                items = [ str(field) for field in row ]
                calendars[items[0]] = items[1]
        return calendars
    except FileNotFoundError as e:
        logger.error("Could not load calendars from {0}. Reason: {1}".format(fileinput, traceback.print_exc()))
        return None

def headless_save_calendar_configuration(filename):
    pass
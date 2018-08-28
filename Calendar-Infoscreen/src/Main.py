# -*- coding: utf-8 -*-

import argparse
import logging
import os
import sys
import time

from PyQt5 import QtCore, QtWidgets

from HttpDaemon import HttpDaemon
from InfoScreen import Infoscreen
from logging import handlers

# commandline arguments
parser = argparse.ArgumentParser(prog="Infoscreen")
parser.add_argument("--headless", help="run the program in headless mode", action='store_true')
parser.add_argument("--preferences", help="preferences file that contains necessary configuration information", type=str, default="preferences.dat")
parser.add_argument("--configuration", help="calendar configuration to be used", type=str, default="calendar_configuration.conf")
parser.add_argument("--daemon", help="run the program as daemon", action='store_true')
parser.add_argument("--http", help="use simpleHttp to serve the content", action='store_true')
parser.add_argument("--serverport", help="server port is mandatory if daemon is defined", type=int, default=8080)
parser.add_argument("--workdir", help="working directory for the program", type=str, default="")
args = parser.parse_args()

# pyinstaller workaround for determining the workdir
if getattr(sys, 'frozen', False):
    rootdir = os.path.dirname(sys.executable)
else:
    rootdir = os.path.dirname(os.path.abspath(__file__))

# change workdir to scripts location
os.chdir(rootdir)

if args.workdir == "":
    args.workdir = rootdir

# setup logging
if not os.path.exists(args.workdir + "/logs/"):
    os.makedirs(args.workdir + "/logs/")

logger = logging.getLogger('infoscreen')
logger.setLevel(logging.DEBUG)

fh = handlers.TimedRotatingFileHandler(args.workdir + '/logs/debug.log', when="d", interval=1, backupCount=7)
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

# workthread which executes calendar data fetching
from HeadlessPageGeneratorThread import HeadlessPageGeneratorThread

# utility methods for running this program in headless mode
import HeadlessUtilities

if __name__ == "__main__":
    if not args.headless:
        app = QtWidgets.QApplication(sys.argv)
        myWindow = Infoscreen(rootdir, args.workdir, None)
        myWindow.show()
        app.exec_()
    else:
        logger.info("User request to run in headless mode")
        logger.info("Reading preferences from {0}\{1}.".format(rootdir, args.preferences))

        preferences = HeadlessUtilities.headless_load_preferences(rootdir, args.preferences)

        if preferences is None:
            logger.error("Failure while reading preferences. Check data integrity. Exiting.")
            sys.exit(0)

        logger.info("Preferences OK.")
        logger.info("Reading calendar configuration from {0}\{1}.".format(rootdir, args.configuration))

        calendars = HeadlessUtilities.headless_load_calendar_configuration(rootdir, args.configuration)

        if calendars is None:
            logger.error("Failure while reading calendars. Check data integrity. Exiting")
            sys.exit(0)

        logger.info("Calendar data OK.")

        if args.daemon or args.http:
            if args.http:
                httpd = HttpDaemon(port=args.serverport, root=args.workdir)
                httpd.start()
                logger.debug("HTTP server up. Using port: {0}".format(args.serverport))
            try:
                while True:
                    generatorthread = HeadlessPageGeneratorThread(calendars, preferences["username"], preferences["password"], preferences["server"], preferences["ignoreSSL"], args.workdir)
                    generatorthread.start()
                    generatorthread.join()
                    logger.debug("Sleeping for {0} seconds before refreshing...".format(int(preferences["interval"]) * 60))
                    time.sleep(int(preferences["interval"]) * 60)
            except KeyboardInterrupt as e:
                if args.http:
                    logger.debug("Server shutdown requested")
                    httpd.force_stop()
                    httpd.join()
                generatorthread.join()
        else:
            generatorthread = HeadlessPageGeneratorThread(calendars, preferences["username"], preferences["password"], preferences["server"], preferences["ignoreSSL"], args.workdir)
            generatorthread.start()
            generatorthread.join()
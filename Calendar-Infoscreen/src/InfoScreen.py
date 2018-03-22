# -*- coding: utf-8 -*-

import csv
import logging
import os
import requests
import sys

from http.server import HTTPServer, SimpleHTTPRequestHandler

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QDialog

# import UI files created with pyuic4
from InfoScreenUI import Ui_InfoScreen_Window
from AboutUI import Ui_About

import Preferences
import AddCalendar

# setup logging
if not os.path.exists(os.getcwd() + "/logs/"):
    os.makedirs(os.getcwd() + "/logs/")
from logging import handlers
logger = logging.getLogger('infoscreen')
logger.setLevel(logging.DEBUG)
# create file handler which logs debug messages
fh = handlers.TimedRotatingFileHandler(os.getcwd() + '/logs/debug.log', when="d", interval=1, backupCount=7)
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

# workthread which executes calendar data fetching
from PageGeneratorThread import PageGeneratorThread

#HOST, PORT = '127.0.0.1', 8080

class HttpDaemon(QtCore.QThread):

    stopped = False
    allow_reuse_address = True
    def __init__(self, port, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.notifyProgress = QtCore.pyqtSignal(int)
        self.port = port

    def run(self):
        logger.debug("HTTP Server Starting Up")
        self.stopped = False
        try:
            self._server = HTTPServer(('0.0.0.0', int(self.port)), SimpleHTTPRequestHandler)
        except OSError:
            logger.debug("Could not start the server. Perhaps the port is in use. Exiting!!")
            return
        self.serve_forever()

    def serve_forever(self):
        logger.debug("Serving over HTTP")
        while not self.stopped:
            self._server.handle_request() #blocks
        logger.debug("HTTP Server Exiting")

    def force_stop(self):
        logger.debug("Requesting HTTP Server Shutdown")
        self.stopped = True
        self.create_dummy_request()

    def set_port(self, port):
        self.port = port

    def create_dummy_request(self):
        try:
            requests.get("http://%s:%s/web/" % ('127.0.0.1', int(self.port)), timeout=1)
        except requests.exceptions.ReadTimeout:
            pass
        except requests.exceptions.ConnectionError:
            pass

    def stop(self):
        self._server.server_close()


# class for used for stdout redirecting
class EmittingStream(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)
    def write(self, text):
        self.textWritten.emit(str(text))
    def writelines(self, l):
        map(self.write, l)
    def flush(self):
        pass

# self declared exceptions:
class InvalidComboBoxValue(Exception):
    pass

# main program
class Infoscreen(QtWidgets.QMainWindow, Ui_InfoScreen_Window):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)

        self.setupUi(self)

        # minimize the console on startup
        #ctypes.windll.user32.ShowWindow( ctypes.windll.kernel32.GetConsoleWindow(), 6 )

        # redirect stdout
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)

        # member variables
        self.selectedRow  = -1
        self.selectedCol  = -1
        self.savePending  = False

        # HTTP daemon
        self.httpd = HttpDaemon(port=8080)

        # preferences variables
        self.username = ""
        self.password = ""
        self.server = "https://sposti.ppshp.fi/EWS/Exchange.asmx"
        self.serverport = 8080
        self.interval = 5
        self.updatedata = 0
        self.ignoreSSL = 0
        self.lastusedconfig = ""

        # connect signals / slots of UI controls
        self.btnAdd.clicked.connect(self.buttonAddPressed)
        self.btnClear.clicked.connect(self.buttonClearPressed)
        self.btnDelete.clicked.connect(self.buttonDeletePressed)
        self.btnMoveDown.clicked.connect(self.buttonMoveDownPressed)
        self.btnMoveUp.clicked.connect(self.buttonMoveUpPressed)
        self.btnEdit.clicked.connect(self.buttonUpdatePressed)
        self.actionAbout.triggered.connect(self.aboutActionTriggered)
        self.actionLoad.triggered.connect(self.loadActionTriggered)
        self.actionSave.triggered.connect(self.saveActionTriggered)
        self.actionClose.triggered.connect(self.closeActionTriggered)
        self.actionPreferences.triggered.connect(self.preferencesActionTriggered)
        self.btnStart.clicked.connect(self.buttonStartPressed)
        self.table.itemClicked.connect(self.cellClicked)
        self.chkUseHTTP.stateChanged.connect(self.HTTPCheckBoxToggled)

        self.btnStart.setText("Generate")

        self.thread = PageGeneratorThread()
        self.thread.progress.connect(self.updateProgressBar)
        self.thread.statusupdate.connect(self.onWorkerThreadStatusUpdate)

        self.loadPreferences()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.generateCalendarPage)

    def __del__(self):
        sys.stdout = sys.__stdout__

    def closeEvent(self, event):
        if self.httpd.isRunning():
            self.httpd.stop()
        self.savePreferences()

    def normalOutputWritten(self, text):
        if len(text) == 1 and ord(str(text)) == 10:
            return
        self.statusBar().showMessage(text, 0)

    def aboutActionTriggered(self):
        dialog = QDialog()
        dialog.ui = Ui_About()
        dialog.ui.setupUi(dialog)
        dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        dialog.exec_()

    def loadPreferences(self):
        try:
            with open("preferences.dat", "r") as fileInput:
                reader = csv.reader(fileInput)
                for row in reader:
                    items = [ str(field) for field in row ]
            for c in items[1]:
                self.password += chr(ord(c) - 5)
            self.username         = items[0]
            self.server           = items[2]
            self.serverport       = items[3]
            self.interval         = items[4]
            self.updatedata       = items[5]
            self.ignoreSSL        = items[6]
            self.lastusedconfig   = items[7]

            if self.lastusedconfig is not "":
                if(self.load(self.lastusedconfig)):
                    self.enableUI()
                else:
                    self.lastusedconfig = ""
                    self.disableUI()

        except FileNotFoundError as e:
            self.notify("It seems that this is the first time you are launching this program. Please configure necessary connection parameters to get started")
            logger.debug("loadPreferences FileNotFoundError: {0}".format(e))
            self.preferencesActionTriggered()

    def savePreferences(self):
        try:
            temp_pw = ""
            for c in self.password:
                temp_pw += chr(ord(c) + 5)

            if self.lastusedconfig == "":
                self.lastusedconfig = "calendar_configuration.conf"

            self.save(self.lastusedconfig)

            with open("preferences.dat", "w", newline="\n", encoding="utf-8") as fileOutput:
                writer = csv.writer(fileOutput)
                writer.writerow([self.username, temp_pw, self.server, self.serverport, self.interval, self.updatedata, self.ignoreSSL, self.lastusedconfig])
        except FileNotFoundError as e:
            self.warning("Failed to save preferences: {0}".format(e))
            sys.exit(0)

    def onWorkerThreadStatusUpdate(self, value, message):
        logger.debug("Status: %s: %s" %(str(value), message))
        self.progressBar.setValue(0)

    def loadActionTriggered(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(self, "Load Calendar Configuration", "", "Configuration files (*.conf)", "Configuration files (*.conf)")
        if filename == "":
            return
        if self.savePending == True or self.table.rowCount() != 0:
            if self.confirm("About to clear current configuration. Are you sure?") == True:
                self.clearTable()
            else:
                return

        if(self.load(filename)):
            self.lastusedconfig = filename[0]
        self.enableUI()

    def saveActionTriggered(self):
        filename = QtWidgets.QFileDialog.getSaveFileName(self, "Save Configuration", "", "Configuration files (*.conf)", "Configuration files (*.conf)")

        if filename == "":
            return
        else:
            self.save(filename)

    def closeActionTriggered(self):
        self.close()

    def preferencesActionTriggered(self):
        dialog = Preferences.PreferencesDialog()
        dialog.setPreferences([self.username, self.password, self.server, self.serverport, self.interval, self.updatedata, self.ignoreSSL])
        if dialog.exec_():
            try:
                result = dialog.getPreferences()

                self.username   = result[0]
                self.password   = result[1]
                self.server     = result[2]
                self.serverport = result[3]
                self.interval   = result[4]
                self.updatedata = result[5]
                self.ignoreSSL  = result[6]

                self.savePreferences()

            except ValueError as e:
                QtWidgets.QMessageBox.question(self, 'Error', "Invalid values given. Please check your parameters: {0}".format(e), QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
                return

    def updateProgressBar(self, value):
        self.progressBar.setValue(value)

    def generateCalendarPage(self):
        self.progressBar.setValue(0)
        self.thread.startworking(self.tableToList(), self.username, self.password, self.server, self.ignoreSSL)

    def buttonStartPressed(self):
        if self.btnStart.text() == "Start Server":
            self.generateCalendarPage()
            self.httpd.set_port(self.serverport)
            self.httpd.start()
            self.btnStart.setText("Stop Server")
            self.disableUI()
            self.timer.start(int(self.interval) * 1000 * 60)
            self.notify("HTTP Server running. Open your browser and point to http://localhost:" + self.serverport + "/web/")
        elif self.btnStart.text() == "Stop Server":
            self.httpd.force_stop()
            self.thread.stopworking()
            self.btnStart.setText("Start Server")
            self.enableUI()
            self.timer.stop()
        else:
            self.generateCalendarPage()

    def HTTPCheckBoxToggled(self, value):
        if value == 2:
            self.btnStart.setText("Start Server")
        else:
            self.btnStart.setText("Generate")

    def buttonAddPressed(self):
        dialog = AddCalendar.AddCalendarDialog()
        if dialog.exec_():
            try:
                result = dialog.getCalendar()
                name   = result[0]
                email  = result[1]

                if name == "" or email == "":
                    self.warning("Invalid calendar data submitted!")
                    return

                self.addTableEntry(name, email)

                self.btnStart.setEnabled(True)
                self.btnClear.setEnabled(True)
                self.btnMoveDown.setEnabled(False)
                self.btnMoveUp.setEnabled(False)
                self.btnDelete.setEnabled(False)

                self.savePending = True
            except ValueError as e:
                QtWidgets.QMessageBox.question(self, 'Error', "Invalid values given. Please check your parameters: {0}".format(e), QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
                return

    def buttonUpdatePressed(self):
        if self.selectedRow != -1 and self.selectedCol != -1:

            name = str(self.table.item(self.selectedRow, 0).text())
            email = str(self.table.item(self.selectedRow, 1).text())

            dialog = AddCalendar.AddCalendarDialog()
            dialog.setCalendar([name, email])

            if dialog.exec_():
                try:
                    result = dialog.getCalendar()
                    name   = result[0]
                    email  = result[1]

                    if name == "" or email == "":
                        self.warning("Invalid calendar data submitted!")
                        return

                    self.updateTableEntry(self.selectedRow, name, email)
                    self.btnStart.setEnabled(True)
                    self.btnClear.setEnabled(True)

                    self.savePending = True
                except ValueError as e:
                    QtWidgets.QMessageBox.question(self, 'Error', "Invalid values given. Please check your parameters: {0}".format(e), QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
                    return

    def buttonMoveUpPressed(self):
        row = self.table.currentRow()

        if row != 0:
            self.table.insertRow(row - 1)
            for i in range(self.table.columnCount()):
                self.table.setItem(row - 1, i, self.table.takeItem(row + 1, i))
            self.table.removeRow(row + 1)
            self.table.setCurrentCell(row - 1, 0)
            self.table.selectRow(self.table.currentRow())

    def buttonMoveDownPressed(self):
        row = self.table.currentRow()

        if row != self.table.rowCount() - 1:
            self.table.insertRow(row + 2)
            for i in range(self.table.columnCount()):
                self.table.setItem(row + 2, i, self.table.takeItem(row, i))
            self.table.removeRow(row)
            self.table.setCurrentCell(row + 1, 0)
            self.table.selectRow(self.table.currentRow())

    def buttonDeletePressed(self):
        self.table.removeRow(self.table.currentRow())

        if self.table.rowCount() == 0:
            self.btnMoveDown.setEnabled(False)
            self.btnMoveUp.setEnabled(False)
            self.btnDelete.setEnabled(False)
            self.btnClear.setEnabled(False)
            self.btnEdit.setEnabled(False)
            self.btnStart.setEnabled(False)
            self.savePending = False

    def buttonClearPressed(self):
        if self.confirm("About to clear current configuration. Are you sure?") == True:
            self.clearTable()
            self.savePending = False
        else:
            return

    def cellClicked(self, item):
        self.selectedRow = item.row()
        self.selectedCol = item.column()

        self.btnMoveDown.setEnabled(True)
        self.btnMoveUp.setEnabled(True)
        self.btnDelete.setEnabled(True)
        self.btnEdit.setEnabled(True)

    def clearTable(self):
        while self.table.rowCount() > 0:
            self.table.removeRow(0)

        self.btnMoveUp.setEnabled(False)
        self.btnMoveDown.setEnabled(False)
        self.btnDelete.setEnabled(False)
        self.btnClear.setEnabled(False)
        self.btnStart.setEnabled(False)
        self.btnEdit.setEnabled(False)

    def tableToList(self):
        contents = []

        for i in range(self.table.rowCount()):
            templist = []
            for j in range(self.table.columnCount()):
                templist.append(str(self.table.item(i, j).text()))
            contents.append(templist)

        return contents

    def listToTable(self, list):
        try:
            for i in range(len(list[0])):
                self.table.insertRow(i)
                for j in range(len(list[0][i])):
                    self.table.setItem(i , j, QtWidgets.QTableWidgetItem(str(list[0][i][j])))
                    self.table.item(i, j).setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter | QtCore.Qt.AlignCenter)
        except AttributeError as e:
            self.clearTable()
            self.warning("Failed to load data. Check configuration files integrity and try again: {0}".format(e))

    def updateTableEntry(self, row, name, email):
        self.insertRow(row, name, email)

    def addTableEntry(self, name, email):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.insertRow(row, name, email)

    def insertRow(self, row, name, email):
        self.table.setItem(row , 0, QtWidgets.QTableWidgetItem(str(name)))
        self.table.setItem(row , 1, QtWidgets.QTableWidgetItem(str(email)))
        self.table.item(row, 0).setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter | QtCore.Qt.AlignCenter)
        self.table.item(row, 1).setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter | QtCore.Qt.AlignCenter)

    def disableUI(self):
        for w in self.findChildren(QtWidgets.QPushButton):
            w.setEnabled(False)
        for w in self.findChildren(QtWidgets.QLineEdit):
            w.setEnabled(False)
        for w in self.findChildren(QtWidgets.QCheckBox):
            w.setEnabled(False)

        self.table.setEnabled(False)
        self.btnStart.setEnabled(True)

    def enableUI(self):
        for w in self.findChildren(QtWidgets.QPushButton):
            w.setEnabled(True)
        for w in self.findChildren(QtWidgets.QLineEdit):
            w.setEnabled(True)
        for w in self.findChildren(QtWidgets.QCheckBox):
            w.setEnabled(True)

        self.table.setEnabled(True)

    def load(self, fileName):
        contents = []

        file = ""

        if type(fileName) == str:
            file = fileName
        else:
            file = fileName[0]

        try:
            with open(file, "r", encoding="iso-8859-1") as fileInput:
                reader = csv.reader(fileInput)
                templist = []
                for row in reader:
                    items = [ str(field) for field in row ]
                    templist.append(items)
                contents.append(templist)

            self.listToTable(contents)
            return True
        except Exception as e:
            logger.error("Failed to load configuration file: {0}".format(e))
            return False

    def save(self, fileName):
        contents = self.tableToList()

        file = ""

        if type(fileName) == str:
            file = fileName
        else:
            file = fileName[0]

        if file is "":
            return

        with open(file, "w", newline="\n", encoding="iso-8859-1") as fileOutput:
            writer = csv.writer(fileOutput)
            writer.writerows(contents)

        self.lastusedconfig = file
        self.savePending = False

    def confirm(self, question):
        reply = QtWidgets.QMessageBox.question(self, 'Confirmation Required', question, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            return True
        else:
            return False

    def warning(self, message):
        QtWidgets.QMessageBox.warning(self, 'Warning', message, QtWidgets.QMessageBox.Ok)

    def notify(self, message):
        QtWidgets.QMessageBox.information(self, 'Attention', message, QtWidgets.QMessageBox.Ok)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myWindow = Infoscreen(None)
    myWindow.show()
    app.exec_()
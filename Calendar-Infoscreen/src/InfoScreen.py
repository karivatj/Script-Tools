# -*- coding: utf-8 -*-

import csv
import logging
import sys
import traceback

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QDialog

# import UI files created with pyuic4
from InfoScreenUI import Ui_InfoScreen_Window
from AboutUI import Ui_About

from HttpDaemon import HttpDaemon
import Preferences
import AddCalendar

# workthread which executes calendar data fetching
from PageGeneratorThread import PageGeneratorThread

logger = logging.getLogger('infoscreen')

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
    def __init__(self, rootdir="", workdir="", parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)

        self.setupUi(self)

        self.lblInfoScreen.setText("InfoScreen Setup 1.1.1")

        # redirect stdout
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)

        # member variables
        self.selectedRow  = -1
        self.selectedCol  = -1
        self.savePending  = False
        self.rootdir = rootdir
        self.siteroot = workdir

        # HTTP daemon
        self.httpd = None

        # preferences dictionary
        self.preferences = {}
        self.preferences["username"] = ""
        self.preferences["password"] = ""
        self.preferences["server"] = ""
        self.preferences["serverport"] = 8080
        self.preferences["interval"] = 5
        self.preferences["updatedata"] = 0
        self.preferences["ignoreSSL"] = 0
        self.preferences["httpServer"] = 0
        self.preferences["lastusedconfig"] = ""

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

        self.thread = PageGeneratorThread()
        self.thread.progress.connect(self.updateProgressBar)
        self.thread.statusupdate.connect(self.onWorkerThreadStatusUpdate)

        self.loadPreferences()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.generateCalendarPage)

    def __del__(self):
        sys.stdout = sys.__stdout__

    def closeEvent(self, event):
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
            items = []
            with open(self.rootdir + "/preferences.dat", "r", newline="\n", encoding="utf-8") as fileInput:
                while True:
                    line = fileInput.readline()
                    if not line:
                        break
                    else:
                        items.append(line.strip("\n"))

            for c in items[1]:
                self.preferences["password"]  += chr(ord(c) - 5)

            self.preferences["username"]       = str(items[0])
            self.preferences["server"]         = str(items[2])
            self.preferences["serverport"]     = str(items[3])
            self.preferences["interval"]       = int(items[4])
            self.preferences["updatedata"]     = int(items[5])
            self.preferences["ignoreSSL"]      = int(items[6])
            self.preferences["httpServer"]     = int(items[7])
            self.preferences["lastusedconfig"] = str(items[8])

            if self.preferences["lastusedconfig"] is not "":
                if(self.load(self.preferences["lastusedconfig"])):
                    self.enableUI()
                else:
                    self.preferences["lastusedconfig"] = ""
                    self.disableUI()

        except FileNotFoundError as e:
            self.notify("It seems that this is the first time you are launching this program. Please configure necessary connection parameters to get started")
            logger.debug("loadPreferences FileNotFoundError: {0}".format(traceback.print_exc()))
            self.preferencesActionTriggered()
        except IndexError as e:
            self.notify("Preferences file seems to be corrupt. Please reconfigure the software in the settings dialog")
            logger.debug("loadPreferences IndexError: {0}".format(traceback.print_exc()))
            self.preferencesActionTriggered()

    def savePreferences(self):
        try:
            temp_pw = ""
            for c in self.preferences["password"]:
                temp_pw += chr(ord(c) + 5)

            if self.preferences["lastusedconfig"] == "":
                self.preferences["lastusedconfig"] = self.rootdir + "/calendar_configuration.conf"

            self.save(self.preferences["lastusedconfig"])

            with open(self.rootdir + "/preferences.dat", "w", newline="\n", encoding="utf-8") as fileOutput:
                fileOutput.write(str(self.preferences["username"]).strip() + "\n")
                fileOutput.write(str(temp_pw) + "\n")
                fileOutput.write(str(self.preferences["server"]).strip() + "\n")
                fileOutput.write(str(self.preferences["serverport"]).strip() + "\n")
                fileOutput.write(str(self.preferences["interval"]).strip() + "\n")
                fileOutput.write(str(self.preferences["updatedata"]).strip() + "\n")
                fileOutput.write(str(self.preferences["ignoreSSL"]).strip() + "\n")
                fileOutput.write(str(self.preferences["httpServer"]).strip() + "\n")
                fileOutput.write(str(self.preferences["lastusedconfig"]).strip() + "\n")

        except FileNotFoundError as e:
            self.warning("Failed to save preferences: {0}".format(traceback.print_exc()))
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
            self.preferences["lastusedconfig"] = filename[0]
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
        dialog.setPreferences([self.preferences["username"],
                               self.preferences["password"],
                               self.preferences["server"],
                               self.preferences["serverport"],
                               self.preferences["interval"],
                               self.preferences["updatedata"],
                               self.preferences["ignoreSSL"],
                               self.preferences["httpServer"]])

        if dialog.exec_():
            try:
                result = dialog.getPreferences()

                self.preferences["username"]   = result[0]
                self.preferences["password"]   = result[1]
                self.preferences["server"]     = result[2]
                self.preferences["serverport"] = result[3]
                self.preferences["interval"]   = result[4]
                self.preferences["updatedata"] = result[5]
                self.preferences["ignoreSSL"]  = result[6]
                self.preferences["httpServer"] = result[7]

                self.savePreferences()

            except ValueError as e:
                QtWidgets.QMessageBox.question(self, 'Error', "Invalid values given. Please check your parameters: {0}".format(traceback.print_exc()), QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
                return

    def updateProgressBar(self, value):
        self.progressBar.setValue(value)

    def generateCalendarPage(self):
        self.progressBar.setValue(0)
        self.thread.startworking(self.tabletoDict(), self.preferences["username"],
                                                     self.preferences["password"],
                                                     self.preferences["server"],
                                                     self.preferences["ignoreSSL"],
                                                     self.siteroot)

    def buttonStartPressed(self):
        if self.preferences["httpServer"] == 2:
            if self.btnStart.text() == "Start":
                self.btnStart.setText("Stop")
                self.httpd = HttpDaemon(port=8080, root=self.siteroot)
                self.httpd.set_port(self.preferences["serverport"])
                self.httpd.start()
                self.disableUI()
                if self.preferences["updatedata"] == 2:
                    self.timer.start(self.preferences["interval"] * 1000 * 60)
                self.notify("HTTP Server running. Open your browser and point to http://<server_ip>:" + self.preferences["serverport"] + "/web/")
                self.generateCalendarPage()
            elif self.btnStart.text() == "Stop":
                self.btnStart.setText("Start")
                self.httpd.force_stop()
                self.thread.stopworking()
                self.enableUI()
                self.timer.stop()
        else:
            if self.btnStart.text() == "Start":
                self.btnStart.setText("Stop")
                self.disableUI()
                if self.preferences["updatedata"] == 2:
                    self.timer.start(self.preferences["interval"] * 1000 * 60)
                self.generateCalendarPage()
            elif self.btnStart.text() == "Stop":
                self.btnStart.setText("Start")
                self.thread.stopworking()
                self.enableUI()
                self.timer.stop()

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
                QtWidgets.QMessageBox.question(self, 'Error', "Invalid values given. Please check your parameters: {0}".format(traceback.print_exc()), QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
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
                    QtWidgets.QMessageBox.question(self, 'Error', "Invalid values given. Please check your parameters: {0}".format(traceback.print_exc()), QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
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

    def tabletoDict(self):
        contents = {}

        for i in range(self.table.rowCount()):
            templist = []
            for j in range(self.table.columnCount()):
                templist.append(str(self.table.item(i, j).text()))
            contents[templist[0]] = templist[1]
        return contents

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
            self.warning("Failed to load data. Check configuration files integrity and try again: {0}".format(traceback.print_exc()))

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
            logger.error("Failed to load configuration file: {0}".format(traceback.print_exc()))
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
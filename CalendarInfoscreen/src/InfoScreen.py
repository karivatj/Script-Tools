import sys
import csv
from urllib.request import urlopen
from http.server import HTTPServer, SimpleHTTPRequestHandler

from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

# import UI files created with pyuic4
from InfoScreenUI import *
from AddCalendarUI import *
from AboutUI import *
from PreferencesUI import *
import Preferences
import AddCalendar
import PageGenerator

HOST, PORT = '127.0.0.1', 8080

class HttpDaemon(QtCore.QThread):
    def run(self):
        self._server = HTTPServer((HOST, PORT), SimpleHTTPRequestHandler)
        self._server.serve_forever()

    def stop(self):
        print("Stopping")
        self._server.shutdown()
        print("Closing socket")
        self._server.socket.close()
        self.wait()
        print("Done")

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

        # redirect stdout
        # sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)        
        
        # member variables
        self.selectedRow  = -1
        self.selectedCol  = -1
        self.savePending  = False

        # HTTP daemon
        self.httpd = HttpDaemon(self)

        # preferences variables
        self.username = "OYSNET\TestLab_Res"
        self.password = "CP3525dn%4x4"
        self.server = "https://sposti.ppshp.fi/EWS/Exchange.asmx"
        self.interval = 5
        
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
        self.actionPreferences.triggered.connect(self.preferencesActionTriggered)
        self.btnStart.clicked.connect(self.buttonStartPressed)
        self.table.itemClicked.connect(self.cellClicked)
        self.chkUseHTTP.stateChanged.connect(self.HTTPCheckBoxToggled)

        self.btnStart.setText("Generate")

        self.loadPreferences()
        
    def __del__(self):
        sys.stdout = sys.__stdout__ 

    def closeEvent(self, event):
        if self.httpd.isRunning():
            self.httpd.stop()

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
            with open("preferences", "r") as fileInput:
                reader = csv.reader(fileInput)
                for row in reader:
                    items = [ str(field) for field in row ]
            self.username  = items[0]
            self.password  = items[1]
            self.server    = items[2]
            self.interval  = items[3]        

        except FileNotFoundError:
            self.notify("It seems that this is the first time you are launching this program. Please configure necessary connection parameters to get started")
            self.preferencesActionTriggered()

    def savePreferences(self):
        with open("preferences", "w", newline="\n", encoding="utf-8") as fileOutput:
            writer = csv.writer(fileOutput)
            writer.writerow([self.username, self.password, self.server, self.interval])

    def loadActionTriggered(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(self, "Load Calendar Configuration", "", "Configuration files (*.conf)", "Configuration files (*.conf)")
        if filename == "":
            return
        if self.savePending == True or self.table.rowCount() != 0:
            if self.confirm("About to clear current configuration. Are you sure?") == True:
                self.clearTable()
            else:
                return

        self.load(filename)
        self.enableUI()

    def saveActionTriggered(self):
        filename = QtWidgets.QFileDialog.getSaveFileName(self, "Save Configuration", "", "Configuration files (*.conf)", "Configuration files (*.conf)")

        if filename == "":
            return
        else:            
            self.save(filename)

    def preferencesActionTriggered(self):
        dialog = Preferences.PreferencesDialog()
        dialog.setPreferences([self.username, self.password, self.server, self.interval])
        if dialog.exec_():
            try:
                result = dialog.getPreferences()

                self.username  = result[0]
                self.password  = result[1]
                self.server    = result[2]
                self.interval  = result[3]

                self.savePreferences()
                
            except ValueError:
                QtWidgets.QMessageBox.question(self, 'Error', "Invalid values given. Please check your parameters.", QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
                return

    def buttonStartPressed(self):
        if self.btnStart.text() == "Start Server":
            #TODO put pagegenerator running in a separate thread
            result = PageGenerator.generateCalendarInfoScreen(self.tableToList(), self.username, self.password, self.server)
            if result is False:
                self.warning("Failed to retrieve calendar information, check connection parameters and try again")
                return
            print("Starting HTTP Server")
            #TODO investigate whats going on with httpd and why it hangs
            self.httpd.start()            
            self.notify("HTTP Server running. Open your browser and point to http://localhost:8080/web/")
            self.btnStart.setText("Stop Server")
            self.disableUI()
        elif self.btnStart.text() == "Stop Server":
            print("Stopping HTTP Server")
            self.httpd.stop()            
            self.btnStart.setText("Start Server")
            self.enableUI()
        else:
            result = PageGenerator.generateCalendarInfoScreen(self.tableToList(), self.username, self.password, self.server)
            if result is False:
                self.warning("Failed to retrieve calendar information, check connection parameters and try again")
                return
            self.notify("Calendar page generated!")

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
            except ValueError:
                QtWidgets.QMessageBox.question(self, 'Error', "Invalid values given. Please check your parameters.", QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
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
                except ValueError:
                    QtWidgets.QMessageBox.question(self, 'Error', "Invalid values given. Please check your parameters.", QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
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

        name  = self.table.item(self.selectedRow, 0).text()
        email = self.table.item(self.selectedRow, 1).text()

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
        except AttributeError:
            self.clearTable()            
            self.warning("Failed to load data. Check configuration files integrity and try again")

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

        self.table.setEnabled(False)
        self.btnStart.setEnabled(True)

    def enableUI(self):
        for w in self.findChildren(QtWidgets.QPushButton):
            w.setEnabled(True)
        for w in self.findChildren(QtWidgets.QLineEdit):
            w.setEnabled(True)

        self.table.setEnabled(True)

    def load(self, fileName):
        contents = []
        with open(fileName[0], "r") as fileInput:
            reader = csv.reader(fileInput)
            templist = []
            for row in reader:
                items = [ str(field) for field in row ]
                templist.append(items)
            contents.append(templist)

        self.listToTable(contents)

    def save(self, fileName):
        contents = self.tableToList()

        with open(fileName[0], "w", newline="\n", encoding="utf-8") as fileOutput:
            writer = csv.writer(fileOutput)
            writer.writerows(contents)

        self.savePending = False

    def confirm(self, question):
        reply = QtWidgets.QMessageBox.question(self, 'Confirmation Required', question, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            return True
        else:
            return False

    def warning(self, message):
        reply = QtWidgets.QMessageBox.warning(self, 'Warning', message, QtWidgets.QMessageBox.Ok)  

    def notify(self, message):
        reply = QtWidgets.QMessageBox.information(self, 'Page Generated', message, QtWidgets.QMessageBox.Ok)  

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myWindow = Infoscreen(None)
    myWindow.show()
    app.exec_()
import re

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

# import UI files created with pyuic4
from InfoScreenUI import *
from PreferencesUI import *

class PreferencesDialog(QtWidgets.QDialog, Ui_Preferences_Window):
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)
        self.username = ""
        self.password = ""
        self.server   = ""
        self.updateInterval = 5
        self.buttonBox.accepted.connect(self.accepted)
        self.buttonBox.rejected.connect(self.rejected)
        self.destroyed.connect(self.rejected)

    def getPreferences(self):
        return [self.username, self.password, self.server, self.updateInterval]

    def setPreferences(self, preferences):
        self.username = preferences[0]
        self.password = preferences[1]
        self.server   = preferences[2]
        self.updateInterval = preferences[3]
        self.lineUsername.setText(self.username)
        self.linePassword.setText(self.password)
        self.lineServer.setText(self.server)
        self.spinInterval.setValue(int(self.updateInterval))

    def accepted(self):
        self.username = self.lineUsername.text()
        self.password = self.linePassword.text()
        self.server   = self.lineServer.text()
        self.updateInterval = self.spinInterval.value()
        self.accept()

    def rejected(self):
        self.reject()

    def closeEvent(self, event):
        self.rejected()
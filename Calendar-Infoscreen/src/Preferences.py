from PyQt5 import QtCore, QtWidgets

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

# import UI files created with pyuic4
from PreferencesUI import Ui_Preferences_Window

class PreferencesDialog(QtWidgets.QDialog, Ui_Preferences_Window):

    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)
        self.username = ""
        self.password = ""
        self.server   = ""
        self.port     = 8080
        self.updateData = 0
        self.ignoreSSL = 0
        self.updateInterval = 5
        self.buttonBox.accepted.connect(self.accepted)
        self.buttonBox.rejected.connect(self.rejected)
        self.destroyed.connect(self.rejected)

    def getPreferences(self):
        return [self.username, self.password, self.server, self.port, self.updateInterval, self.updateData, self.ignoreSSL]

    def setPreferences(self, preferences):
        self.username = preferences[0]
        self.password = preferences[1]
        self.server   = preferences[2]
        self.port     = preferences[3]
        self.updateInterval = int(preferences[4])
        self.updateData = int(preferences[5])
        self.ignoreSSL = int(preferences[6])

        self.lineUsername.setText(self.username)
        self.linePassword.setText(self.password)
        self.lineServer.setText(self.server)
        self.linePort.setText(str(self.port))
        self.spinInterval.setValue(int(self.updateInterval))

        if self.updateData == 2:
            self.chkUpdateData.setChecked(True)
        else:
            self.chkUpdateData.setChecked(False)

        if self.ignoreSSL == 2:
            self.chkSSL.setChecked(True)
        else:
            self.chkSSL.setChecked(False)

    def accepted(self):
        self.username = self.lineUsername.text()
        self.password = self.linePassword.text()
        self.server   = self.lineServer.text()
        self.port     = self.linePort.text()
        self.updateInterval = self.spinInterval.value()

        if self.chkUpdateData.isChecked():
            self.updateData = 2
        else:
            self.updateData = 0

        if self.chkSSL.isChecked():
            self.ignoreSSL = 2
        else:
            self.ignoreSSL = 0

        self.accept()

    def rejected(self):
        self.reject()

    def closeEvent(self, event):
        self.rejected()
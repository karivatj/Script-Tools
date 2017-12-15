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
        self.updateData = 0
        self.updateInterval = 5
        self.buttonBox.accepted.connect(self.accepted)
        self.buttonBox.rejected.connect(self.rejected)
        self.destroyed.connect(self.rejected)

    def getPreferences(self):
        return [self.username, self.password, self.server, self.updateInterval, self.updateData]

    def setPreferences(self, preferences):
        self.username = preferences[0]
        self.password = preferences[1]
        self.server   = preferences[2]
        self.updateInterval = int(preferences[3])
        self.updateData = int(preferences[4])

        self.lineUsername.setText(self.username)
        self.linePassword.setText(self.password)
        self.lineServer.setText(self.server)
        self.spinInterval.setValue(int(self.updateInterval))

        if self.updateData == 2:
            self.chkUpdateData.setChecked(True)
        else:            
            self.chkUpdateData.setChecked(False)

    def accepted(self):
        self.username = self.lineUsername.text()
        self.password = self.linePassword.text()
        self.server   = self.lineServer.text()
        self.updateInterval = self.spinInterval.value()

        if self.chkUpdateData.isChecked():
            self.updateData = 2
        else:
            self.updateData = 0

        self.accept()

    def rejected(self):
        self.reject()

    def closeEvent(self, event):
        self.rejected()
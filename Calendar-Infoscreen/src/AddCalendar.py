from PyQt5 import QtWidgets

# import UI files created with pyuic4
from AddCalendarUI import Ui_AddCalendar_Window

class AddCalendarDialog(QtWidgets.QDialog, Ui_AddCalendar_Window):
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)
        self.calendarName = ""
        self.calendarEmail = ""
        self.buttonBox.accepted.connect(self.accepted)
        self.buttonBox.rejected.connect(self.rejected)
        self.destroyed.connect(self.rejected)

    def getCalendar(self):
        return [self.calendarName, self.calendarEmail]

    def setCalendar(self, calendar):
        self.calendarName = calendar[0]
        self.calendarEmail = calendar[1]
        self.lineName.setText(self.calendarName)
        self.lineEmail.setText(self.calendarEmail)

    def accepted(self):
        self.calendarName = self.lineName.text()
        self.calendarEmail = self.lineEmail.text()
        self.accept()

    def rejected(self):
        self.reject()

    def closeEvent(self, event):
        self.rejected()
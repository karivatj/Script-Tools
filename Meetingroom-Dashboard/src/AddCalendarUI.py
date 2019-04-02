# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '../ui/AddCalendar.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtWidgets

class Ui_AddCalendar_Window(object):
    def setupUi(self, AddCalendar_Window):
        AddCalendar_Window.setObjectName("AddCalendar_Window")
        AddCalendar_Window.resize(310, 124)
        self.gridLayout = QtWidgets.QGridLayout(AddCalendar_Window)
        self.gridLayout.setObjectName("gridLayout")
        self.lblEmail = QtWidgets.QLabel(AddCalendar_Window)
        self.lblEmail.setObjectName("lblEmail")
        self.gridLayout.addWidget(self.lblEmail, 1, 0, 1, 1)
        self.lineEmail = QtWidgets.QLineEdit(AddCalendar_Window)
        self.lineEmail.setObjectName("lineEmail")
        self.gridLayout.addWidget(self.lineEmail, 1, 1, 1, 1)
        self.lblName = QtWidgets.QLabel(AddCalendar_Window)
        self.lblName.setObjectName("lblName")
        self.gridLayout.addWidget(self.lblName, 0, 0, 1, 1)
        self.lineName = QtWidgets.QLineEdit(AddCalendar_Window)
        self.lineName.setObjectName("lineName")
        self.gridLayout.addWidget(self.lineName, 0, 1, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(AddCalendar_Window)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 2, 1, 1, 1)

        self.retranslateUi(AddCalendar_Window)
        self.buttonBox.accepted.connect(AddCalendar_Window.accept)
        self.buttonBox.rejected.connect(AddCalendar_Window.reject)
        QtCore.QMetaObject.connectSlotsByName(AddCalendar_Window)
        AddCalendar_Window.setTabOrder(self.lineName, self.lineEmail)

    def retranslateUi(self, AddCalendar_Window):
        _translate = QtCore.QCoreApplication.translate
        AddCalendar_Window.setWindowTitle(_translate("AddCalendar_Window", "Add Calendar"))
        self.lblEmail.setText(_translate("AddCalendar_Window", "Email:"))
        self.lblName.setText(_translate("AddCalendar_Window", "Name:"))


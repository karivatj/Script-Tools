# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '../ui/Preferences.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Preferences_Window(object):
    def setupUi(self, Preferences_Window):
        Preferences_Window.setObjectName("Preferences_Window")
        Preferences_Window.resize(446, 246)
        self.verticalLayout = QtWidgets.QVBoxLayout(Preferences_Window)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(Preferences_Window)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.lblUsername = QtWidgets.QLabel(self.groupBox)
        self.lblUsername.setObjectName("lblUsername")
        self.gridLayout_2.addWidget(self.lblUsername, 1, 0, 1, 1)
        self.lblPassword = QtWidgets.QLabel(self.groupBox)
        self.lblPassword.setObjectName("lblPassword")
        self.gridLayout_2.addWidget(self.lblPassword, 2, 0, 1, 1)
        self.linePassword = QtWidgets.QLineEdit(self.groupBox)
        self.linePassword.setText("")
        self.linePassword.setEchoMode(QtWidgets.QLineEdit.Password)
        self.linePassword.setObjectName("linePassword")
        self.gridLayout_2.addWidget(self.linePassword, 2, 1, 1, 1)
        self.lineUsername = QtWidgets.QLineEdit(self.groupBox)
        self.lineUsername.setObjectName("lineUsername")
        self.gridLayout_2.addWidget(self.lineUsername, 1, 1, 1, 1)
        self.lblServer = QtWidgets.QLabel(self.groupBox)
        self.lblServer.setObjectName("lblServer")
        self.gridLayout_2.addWidget(self.lblServer, 3, 0, 1, 1)
        self.lineServer = QtWidgets.QLineEdit(self.groupBox)
        self.lineServer.setObjectName("lineServer")
        self.gridLayout_2.addWidget(self.lineServer, 3, 1, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(Preferences_Window)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout.setObjectName("gridLayout")
        self.lblMinutes = QtWidgets.QLabel(self.groupBox_2)
        self.lblMinutes.setObjectName("lblMinutes")
        self.gridLayout.addWidget(self.lblMinutes, 0, 2, 1, 1)
        self.spinInterval = QtWidgets.QSpinBox(self.groupBox_2)
        self.spinInterval.setMinimum(1)
        self.spinInterval.setProperty("value", 5)
        self.spinInterval.setObjectName("spinInterval")
        self.gridLayout.addWidget(self.spinInterval, 0, 1, 1, 1)
        self.lblInterval = QtWidgets.QLabel(self.groupBox_2)
        self.lblInterval.setObjectName("lblInterval")
        self.gridLayout.addWidget(self.lblInterval, 0, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 3, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.buttonBox = QtWidgets.QDialogButtonBox(Preferences_Window)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Preferences_Window)
        self.buttonBox.accepted.connect(Preferences_Window.accept)
        self.buttonBox.rejected.connect(Preferences_Window.reject)
        QtCore.QMetaObject.connectSlotsByName(Preferences_Window)
        Preferences_Window.setTabOrder(self.lineUsername, self.linePassword)
        Preferences_Window.setTabOrder(self.linePassword, self.lineServer)
        Preferences_Window.setTabOrder(self.lineServer, self.spinInterval)

    def retranslateUi(self, Preferences_Window):
        _translate = QtCore.QCoreApplication.translate
        Preferences_Window.setWindowTitle(_translate("Preferences_Window", "Preferences"))
        self.groupBox.setTitle(_translate("Preferences_Window", "Authentication"))
        self.lblUsername.setText(_translate("Preferences_Window", "EWS Username:"))
        self.lblPassword.setText(_translate("Preferences_Window", "EWS Password:"))
        self.lblServer.setText(_translate("Preferences_Window", "EWS Server:"))
        self.lineServer.setText(_translate("Preferences_Window", "https://sposti.ppshp.fi/EWS/Exchange.asmx"))
        self.groupBox_2.setTitle(_translate("Preferences_Window", "Other"))
        self.lblMinutes.setText(_translate("Preferences_Window", "Minutes"))
        self.lblInterval.setText(_translate("Preferences_Window", "Update Interval:"))


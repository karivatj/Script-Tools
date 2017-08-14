# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '../ui/About.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_About(object):
    def setupUi(self, About):
        About.setObjectName("About")
        About.resize(250, 130)
        About.setMinimumSize(QtCore.QSize(250, 130))
        About.setMaximumSize(QtCore.QSize(250, 130))
        self.verticalLayout = QtWidgets.QVBoxLayout(About)
        self.verticalLayout.setObjectName("verticalLayout")
        self.lblHeadline = QtWidgets.QLabel(About)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblHeadline.sizePolicy().hasHeightForWidth())
        self.lblHeadline.setSizePolicy(sizePolicy)
        self.lblHeadline.setAlignment(QtCore.Qt.AlignCenter)
        self.lblHeadline.setWordWrap(True)
        self.lblHeadline.setObjectName("lblHeadline")
        self.verticalLayout.addWidget(self.lblHeadline)
        self.lblSummary = QtWidgets.QLabel(About)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblSummary.sizePolicy().hasHeightForWidth())
        self.lblSummary.setSizePolicy(sizePolicy)
        self.lblSummary.setScaledContents(False)
        self.lblSummary.setAlignment(QtCore.Qt.AlignCenter)
        self.lblSummary.setObjectName("lblSummary")
        self.verticalLayout.addWidget(self.lblSummary)
        self.lblInfo = QtWidgets.QLabel(About)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblInfo.sizePolicy().hasHeightForWidth())
        self.lblInfo.setSizePolicy(sizePolicy)
        self.lblInfo.setScaledContents(False)
        self.lblInfo.setAlignment(QtCore.Qt.AlignCenter)
        self.lblInfo.setObjectName("lblInfo")
        self.verticalLayout.addWidget(self.lblInfo)

        self.retranslateUi(About)
        QtCore.QMetaObject.connectSlotsByName(About)

    def retranslateUi(self, About):
        _translate = QtCore.QCoreApplication.translate
        About.setWindowTitle(_translate("About", "About"))
        self.lblHeadline.setText(_translate("About", "Infoscreen Setup tool"))
        self.lblSummary.setText(_translate("About", "Easily configure infoscreen contents"))
        self.lblInfo.setText(_translate("About", "Author: Kari Vatjus-Anttila\n"
"Email: kari.vatjusanttila@gmail.com"))

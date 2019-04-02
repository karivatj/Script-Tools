# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SymbolUI.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_SymbolUI(object):
    def setupUi(self, SymbolUI):
        SymbolUI.setObjectName(_fromUtf8("SymbolUI"))
        SymbolUI.resize(460, 300)
        SymbolUI.setMinimumSize(QtCore.QSize(460, 300))
        self.gridLayout = QtGui.QGridLayout(SymbolUI)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.lblSymbol = QtGui.QLabel(SymbolUI)
        self.lblSymbol.setObjectName(_fromUtf8("lblSymbol"))
        self.verticalLayout.addWidget(self.lblSymbol)
        self.lblMarketCap = QtGui.QLabel(SymbolUI)
        self.lblMarketCap.setObjectName(_fromUtf8("lblMarketCap"))
        self.verticalLayout.addWidget(self.lblMarketCap)
        self.lblLastBid = QtGui.QLabel(SymbolUI)
        self.lblLastBid.setObjectName(_fromUtf8("lblLastBid"))
        self.verticalLayout.addWidget(self.lblLastBid)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.txtSymbol = QtGui.QLineEdit(SymbolUI)
        self.txtSymbol.setEnabled(False)
        self.txtSymbol.setObjectName(_fromUtf8("txtSymbol"))
        self.verticalLayout_3.addWidget(self.txtSymbol)
        self.txtMarketCap = QtGui.QLineEdit(SymbolUI)
        self.txtMarketCap.setEnabled(False)
        self.txtMarketCap.setObjectName(_fromUtf8("txtMarketCap"))
        self.verticalLayout_3.addWidget(self.txtMarketCap)
        self.txtLastBid = QtGui.QLineEdit(SymbolUI)
        self.txtLastBid.setEnabled(False)
        self.txtLastBid.setObjectName(_fromUtf8("txtLastBid"))
        self.verticalLayout_3.addWidget(self.txtLastBid)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.divider = QtGui.QFrame(SymbolUI)
        self.divider.setFrameShape(QtGui.QFrame.VLine)
        self.divider.setFrameShadow(QtGui.QFrame.Sunken)
        self.divider.setObjectName(_fromUtf8("divider"))
        self.horizontalLayout.addWidget(self.divider)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.lblName = QtGui.QLabel(SymbolUI)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.verticalLayout_2.addWidget(self.lblName)
        self.lblPrice = QtGui.QLabel(SymbolUI)
        self.lblPrice.setObjectName(_fromUtf8("lblPrice"))
        self.verticalLayout_2.addWidget(self.lblPrice)
        self.lblLastClose = QtGui.QLabel(SymbolUI)
        self.lblLastClose.setObjectName(_fromUtf8("lblLastClose"))
        self.verticalLayout_2.addWidget(self.lblLastClose)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.verticalLayout_5 = QtGui.QVBoxLayout()
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.txtName = QtGui.QLineEdit(SymbolUI)
        self.txtName.setEnabled(False)
        self.txtName.setObjectName(_fromUtf8("txtName"))
        self.verticalLayout_5.addWidget(self.txtName)
        self.txtPrice = QtGui.QLineEdit(SymbolUI)
        self.txtPrice.setEnabled(False)
        self.txtPrice.setObjectName(_fromUtf8("txtPrice"))
        self.verticalLayout_5.addWidget(self.txtPrice)
        self.txtLastClose = QtGui.QLineEdit(SymbolUI)
        self.txtLastClose.setEnabled(False)
        self.txtLastClose.setObjectName(_fromUtf8("txtLastClose"))
        self.verticalLayout_5.addWidget(self.txtLastClose)
        self.horizontalLayout.addLayout(self.verticalLayout_5)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)
        self.plotWidget = PlotWidget(SymbolUI)
        self.plotWidget.setObjectName(_fromUtf8("plotWidget"))
        self.gridLayout.addWidget(self.plotWidget, 0, 0, 1, 1)

        self.retranslateUi(SymbolUI)
        QtCore.QMetaObject.connectSlotsByName(SymbolUI)

    def retranslateUi(self, SymbolUI):
        SymbolUI.setWindowTitle(_translate("SymbolUI", "Symbol Information", None))
        self.lblSymbol.setText(_translate("SymbolUI", "Symbol:", None))
        self.lblMarketCap.setText(_translate("SymbolUI", "Market cap", None))
        self.lblLastBid.setText(_translate("SymbolUI", "Last Bid/Ask:", None))
        self.lblName.setText(_translate("SymbolUI", "Name:", None))
        self.lblPrice.setText(_translate("SymbolUI", "Stock price", None))
        self.lblLastClose.setText(_translate("SymbolUI", "Last close:", None))

from pyqtgraph import PlotWidget

import re

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

# import UI files created with pyuic4
from MainUI import *
from SymbolUI import *

class SymbolDialog(QtGui.QDialog, Ui_SymbolUI):

    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)

        self.plotWidget.showGrid(x = True, y= True, alpha = 0.5)
        self.plotWidget.setBackground(QtGui.QColor(QtCore.Qt.white))

        self.data = []
        self.symbol = ""
        self.name = ""

    def setData(self, data, symbol, name):
        self.data = data
        self.symbol = symbol
        self.name = name

        self.setWindowTitle("Symbol Information - " + symbol + " (" + name + ")")
        self.txtName.setText(name)
        self.txtSymbol.setText(symbol)
        self.txtPrice.setText("15.20$")
        self.txtMarketCap.setText("500 M$")
        self.txtLastBid.setText("15.45$")
        self.txtLastClose.setText("15.00$")

    def keyPressEvent(self, event):
        pass

    def getResult(self):
        return "Result"

    def accepted(self):
        self.accept()

    def rejected(self):
        self.reject()

    def closeEvent(self, event):
        self.rejected()
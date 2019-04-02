# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainUI.ui'
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

class Ui_FinanceTool_Window(object):
    def setupUi(self, FinanceTool_Window):
        FinanceTool_Window.setObjectName(_fromUtf8("FinanceTool_Window"))
        FinanceTool_Window.resize(550, 300)
        self.centralwidget = QtGui.QWidget(FinanceTool_Window)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tableView = QtGui.QTableView(self.centralwidget)
        self.tableView.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tableView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tableView.setShowGrid(True)
        self.tableView.setSortingEnabled(True)
        self.tableView.setObjectName(_fromUtf8("tableView"))
        self.tableView.horizontalHeader().setDefaultSectionSize(200)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.gridLayout.addWidget(self.tableView, 1, 1, 1, 1)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.txtFilter = QtGui.QLineEdit(self.centralwidget)
        self.txtFilter.setObjectName(_fromUtf8("txtFilter"))
        self.horizontalLayout_2.addWidget(self.txtFilter)
        self.btnFilter = QtGui.QPushButton(self.centralwidget)
        self.btnFilter.setDefault(True)
        self.btnFilter.setObjectName(_fromUtf8("btnFilter"))
        self.horizontalLayout_2.addWidget(self.btnFilter)
        self.btnOpenDialog = QtGui.QPushButton(self.centralwidget)
        self.btnOpenDialog.setObjectName(_fromUtf8("btnOpenDialog"))
        self.horizontalLayout_2.addWidget(self.btnOpenDialog)
        self.gridLayout.addLayout(self.horizontalLayout_2, 2, 1, 1, 1)
        self.lblStockExchange = QtGui.QLabel(self.centralwidget)
        self.lblStockExchange.setObjectName(_fromUtf8("lblStockExchange"))
        self.gridLayout.addWidget(self.lblStockExchange, 0, 0, 1, 1)
        self.lblFilter = QtGui.QLabel(self.centralwidget)
        self.lblFilter.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.lblFilter.setObjectName(_fromUtf8("lblFilter"))
        self.gridLayout.addWidget(self.lblFilter, 2, 0, 1, 1)
        self.cmbStockExchange = QtGui.QComboBox(self.centralwidget)
        self.cmbStockExchange.setObjectName(_fromUtf8("cmbStockExchange"))
        self.cmbStockExchange.addItem(_fromUtf8(""))
        self.cmbStockExchange.addItem(_fromUtf8(""))
        self.cmbStockExchange.addItem(_fromUtf8(""))
        self.cmbStockExchange.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbStockExchange, 0, 1, 1, 1)
        self.lblSymbols = QtGui.QLabel(self.centralwidget)
        self.lblSymbols.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.lblSymbols.setObjectName(_fromUtf8("lblSymbols"))
        self.gridLayout.addWidget(self.lblSymbols, 1, 0, 1, 1)
        self.horizontalLayout_3.addLayout(self.gridLayout)
        FinanceTool_Window.setCentralWidget(self.centralwidget)
        self.menuBar = QtGui.QMenuBar(FinanceTool_Window)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 550, 21))
        self.menuBar.setObjectName(_fromUtf8("menuBar"))
        FinanceTool_Window.setMenuBar(self.menuBar)
        self.statusBar = QtGui.QStatusBar(FinanceTool_Window)
        self.statusBar.setObjectName(_fromUtf8("statusBar"))
        FinanceTool_Window.setStatusBar(self.statusBar)

        self.retranslateUi(FinanceTool_Window)
        QtCore.QMetaObject.connectSlotsByName(FinanceTool_Window)
        FinanceTool_Window.setTabOrder(self.cmbStockExchange, self.txtFilter)
        FinanceTool_Window.setTabOrder(self.txtFilter, self.btnFilter)
        FinanceTool_Window.setTabOrder(self.btnFilter, self.tableView)

    def retranslateUi(self, FinanceTool_Window):
        FinanceTool_Window.setWindowTitle(_translate("FinanceTool_Window", "Finance Tool v0.0", None))
        self.btnFilter.setText(_translate("FinanceTool_Window", "Filter", None))
        self.btnOpenDialog.setText(_translate("FinanceTool_Window", "Test", None))
        self.lblStockExchange.setText(_translate("FinanceTool_Window", "Stock Exchange:", None))
        self.lblFilter.setText(_translate("FinanceTool_Window", "Filter Symbols:", None))
        self.cmbStockExchange.setItemText(0, _translate("FinanceTool_Window", "Choose Stock Exchange", None))
        self.cmbStockExchange.setItemText(1, _translate("FinanceTool_Window", "NASDAQ", None))
        self.cmbStockExchange.setItemText(2, _translate("FinanceTool_Window", "NYSE", None))
        self.cmbStockExchange.setItemText(3, _translate("FinanceTool_Window", "AMEX", None))
        self.lblSymbols.setText(_translate("FinanceTool_Window", "Symbols:", None))


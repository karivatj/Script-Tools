# -*- coding: utf-8 -*-

# general imports
import csv
import simplejson as json
import requests
import sys, os, time, datetime

# import QT related stuff
from PyQt4 import QtCore, QtGui, uic

# import UI files created with pyuic4
from MainUI import *
from SymbolUI import *
import Symbol

# other imports
from DataModels import *

# download urls for couple of stock exchanges; NYSE and NASDAQ being the largest ones
nasdaq_tickers_url = "http://www.nasdaq.com/screening/companies-by-industry.aspx?exchange=NASDAQ&render=download" 
nyse_tickers_url   = "http://www.nasdaq.com/screening/companies-by-industry.aspx?exchange=NYSE&render=download"
amex_tickers_url   = "http://www.nasdaq.com/screening/companies-by-industry.aspx?exchange=AMEX&render=download"

"""
Information about the CSV data provided by NASDAQ

For ex. UBNK symbol:
"UBNK","United Financial Bancorp Inc.","13.47","666796331.22","n/a","n/a","Finance","Banks","http://www.nasdaq.com/symbol/ubnk"

1. Symbol name
2. Description / Name
3. Last sale ($)
4. Market Capital
5. ADR TSO
6. Year founded?
7. Sector
8. Subsector
9. NASDAQ symbol url
"""

# class for used for stdout redirecting
class EmittingStream(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)
    def write(self, text):
        self.textWritten.emit(str(text))
    def writelines(self, l): 
        map(self.write, l) 

class FinanceTool(QtGui.QMainWindow, Ui_FinanceTool_Window):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        # redirect stdout - Disabled for Debug purposes
        # sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)

        self.model = None

        self.nasdaq_loaded = False
        self.nyse_loaded   = False        
        self.amex_loaded   = False

        self.current_dataset = {} 
        self.nasdaq_symbols  = {}
        self.nyse_symbols    = {}
        self.amex_symbols    = {}

        self.selected_symbol = ""
        self.selected_symbol_name = ""

        # connect necessary signals
        self.cmbStockExchange.currentIndexChanged.connect(self.stockExchangeSelected)
        self.tableView.doubleClicked.connect(self.tableRowDoubleClicked)
        self.tableView.clicked.connect(self.tableRowClicked)
        self.btnFilter.clicked.connect(self.filterPressed)
        self.btnOpenDialog.clicked.connect(self.openSymbolDialog)

        # disable controls
        self.tableView.setEnabled(False)
        self.txtFilter.setEnabled(False)
        self.btnFilter.setEnabled(False)
        self.loadSymbols()

    def __del__(self):
        sys.stdout = sys.__stdout__
        print "Exiting..."

    def normalOutputWritten(self, text):       
        if len(text) == 1 and ord(str(text)) == 10:
            return
        self.statusBar.showMessage(text, 0)

    def openSymbolDialog(self):
        ''' Create and open the Symbol dialog '''
        dialog = Symbol.SymbolDialog()
        dialog.setData(self.current_dataset, self.selected_symbol, self.selected_symbol_name)
        if dialog.exec_():
            result = dialog.getResult()

    def tableRowClicked(self, QModelIndex):
        ''' Select a symbol from the table when a row is clicked '''
        self.selected_symbol = self.current_dataset.keys()[QModelIndex.row()]

    def tableRowDoubleClicked(self, QModelIndex):
        ''' Select a symbol from the table and open the Symbol specs dialog '''
        self.selected_symbol = str(self.current_dataset.keys()[QModelIndex.row()])
        self.selected_symbol_name = str(self.current_dataset.values()[QModelIndex.row()])
        self.openSymbolDialog()
        # TODO open the symbol dialog with a double click for ex

    def stockExchangeSelected(self, index):
        ''' Update the selected Stock Ex. when selecting values from the combobox '''
        if index == 1:
            self.setActiveExchange("NASDAQ")
            self.model = TableModel(self.nasdaq_symbols)
            print "NASDAQ Loaded: " + str(len(self.nasdaq_symbols)) + " entries"
        elif index == 2:
            self.setActiveExchange("NYSE")
            self.model = TableModel(self.nyse_symbols)
            print "NYSE Loaded: " + str(len(self.nyse_symbols)) + " entries"
        elif index == 3:
            self.setActiveExchange("AMEX")
            self.model = TableModel(self.amex_symbols)
            print "AMEX Loaded: " + str(len(self.amex_symbols)) + " entries"

        self.changeModel(self.model)
        self.tableView.setEnabled(True)
        self.txtFilter.setEnabled(True)
        self.btnFilter.setEnabled(True)

    def changeModel(self, model):
        self.tableView.setModel(model)
        self.tableView.resizeColumnsToContents()

    def setActiveExchange(self, name):
        if name in "NASDAQ":
            self.current_dataset = self.nasdaq_symbols
        elif name in "NYSE":
            self.current_dataset = self.nyse_symbols
        elif name in "AMEX":
            self.current_dataset = self.amex_symbols
        else:
            print "Invalid Stock Exchange provided"

    def filterPressed(self):
        filter_text = str(self.txtFilter.text())
        temp = {}

        if filter_text == "":
            self.stockExchangeSelected(self.cmbStockExchange.currentIndex())
        else:
            for key in self.current_dataset.keys():                        
                if filter_text.upper() in key or filter_text.lower() in self.current_dataset[key].lower():
                    temp[key] = self.current_dataset[key]            

        if len(temp.keys()) == 0:
            print "No Search Results"
        else:
            print "Filtered result contains " + str(len(temp.keys())) + " records"
            self.changeModel(TableModel(temp))
            self.current_dataset = temp

    def loadSymbols(self):
        self.nasdaq_symbols, self.nasdaq_loaded = self.load("../symbols/nasdaq_symbols.dat", "NASDAQ")
        self.amex_symbols,   self.amex_loaded   = self.load("../symbols/amex_symbols.dat", "AMEX")
        self.nyse_symbols,   self.nyse_loaded   = self.load("../symbols/nyse_symbols.dat", "NYSE")

        # print summary about the data
        print str.format("NASDAQ: {0} symbols loaded", len(self.nasdaq_symbols))
        print str.format("AMEX: {0} symbols loaded", len(self.amex_symbols))
        print str.format("NYSE: {0} symbols loaded", len(self.nyse_symbols))
        print str.format("Symbol data loaded. NASDAQ: {0} AMEX: {1} NYSE {2}", len(self.nasdaq_symbols), len(self.amex_symbols), len(self.nyse_symbols))

    def load(self, filename, header): 
        """ Load Symbol Data
        Attempts to load symbol data from given file descriptor.
        If the file is corrupt, does not exist or is over 24 hours
        old, the data is going to be re-downloaded from NASDAQ.com.

        @input filename where existing data should be
        @input header - header should be either "NASDAQ", "AMEX", or "NYSE"
        @return a dictionary containing the data
        """   
        data = {}
        try:
            with open(filename, "r") as infile:
                # check how old is our data
                date_modified = datetime.datetime.fromtimestamp(os.path.getmtime(filename))
                date_now = datetime.datetime.now()
                difference = date_now - date_modified

                # if data is older than 24 hours
                if difference.total_seconds() > 86400:
                    print str.format("{0} Symbol Data - EXPIRED", header)
                    raise IOError
                else:
                    data = json.loads(infile.read())
                    print str.format("{0} Symbol Data - OK", header)                
        except IOError:
            url = ""

            print str.format("Updating {0} symbol data", header)

            if header == "NASDAQ":
                url = nasdaq_tickers_url
            elif header == "NYSE":
                url = nyse_tickers_url
            elif header == "AMEX":
                url = amex_tickers_url
            else:
                print "Invalid Stock Market name given!"
                return None, False

            # request the data, parse it through and save it to file
            temp = requests.get(url).text            
            if temp == None:
                return None, False

            reader = csv.reader(temp.splitlines(), delimiter=',')
            for row in reader:
                symbol = str(row[0]).strip()
                name   = str(row[1]).strip()

                # skip header
                if symbol == "Symbol":
                    continue

                # add the entry to dictionary
                data[symbol] = name

            # save the data to a file for future use
            f = open(filename, 'w')
            json.dump(data, f, sort_keys=True)
            f.close()

        return data, True

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myWindow = FinanceTool(None)
    myWindow.show()
    app.exec_()
    del myWindow # delete reference to myWindow
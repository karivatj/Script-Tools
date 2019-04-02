# -*- coding: utf-8 -*-

# import QT related stuff
from PyQt4 import QtCore, QtGui, uic

class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data, parent=None):
        super(TableModel, self).__init__(parent)
        self._data = data
        self.dict_key = data.keys()[0]
        self.headers = ['Symbol', 'Name']

    def set_key(self, key):
        self.beginResetModel()
        self.dict_key = key
        self.endResetModel()

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            return self.headers[section]        
        return QtCore.QAbstractTableModel.headerData(self, section, orientation, role)

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self._data)

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self.headers)

    def data(self, QModelIndex, int_role=None):
        row = QModelIndex.row()
        column = QModelIndex.column()
        key = self._data.keys()[row]

        if int_role == QtCore.Qt.DisplayRole:
            if column == 0:
                return key
            else:
                return self._data[key]

class ListModel(QtCore.QAbstractListModel):
    def __init__(self, data, parent=None):
        super(ListModel, self).__init__(parent)
        self._data = data

    def list_clicked(self, index):
        row = index.row()
        key = self._data[row]
        table_model.set_key(key)

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self._data)

    def data(self, QModelIndex, int_role=None):
        row = QModelIndex.row()
        if int_role == QtCore.Qt.DisplayRole:
            return str(self._data[row])

    def flags(self, QModelIndex):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


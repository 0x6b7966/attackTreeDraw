from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QWidget
from PyQt5 import QtCore, QtGui, QtWidgets


class NodeEdit(QWidget):
    def __init__(self, node):
        QWidget.__init__(self)

        self.nodeItem = node

        self.setupUi()

        self.show()

    def setupUi(self):
        self.resize(320, 240)
        self.setWindowTitle("Node: %s" % self.nodeItem.node.title)
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.tableView = QtWidgets.QTableView(self)
        self.gridLayout.addWidget(self.tableView, 0, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.ok = QtWidgets.QPushButton(self)
        self.horizontalLayout.addWidget(self.ok)
        self.cancel = QtWidgets.QPushButton(self)
        self.horizontalLayout.addWidget(self.cancel)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)
        self.ok.setText('Ok')
        self.cancel.setText('Cancel')

        self.model = QStandardItemModel(1, 2, self)

        self.model.setHeaderData(0, Qt.Horizontal, 'Key')
        self.model.setHeaderData(1, Qt.Horizontal, 'Value')

        self.tableView.setModel(self.model)

        self.model.insertRow(0, [QStandardItem('title'), QStandardItem(self.nodeItem.node.title)])
        self.model.insertRow(1, [QStandardItem('description'), QStandardItem(self.nodeItem.node.description)])

        self.rows = 2

        for k, v in self.nodeItem.node.attributes.items():
            self.model.insertRow(2, [QStandardItem(k), QStandardItem(v)])
            self.rows += 1

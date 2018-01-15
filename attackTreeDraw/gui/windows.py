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

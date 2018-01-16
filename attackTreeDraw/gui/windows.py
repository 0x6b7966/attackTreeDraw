from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QWidget, QHeaderView
from PyQt5 import QtCore, QtGui, QtWidgets


class NodeEdit(QWidget):
    def __init__(self, node):
        QWidget.__init__(self)

        self.nodeItem = node

        self.setupUi()

        self.show()

    def setupUi(self):
        self.resize(320, 440)
        self.setWindowTitle("Node: %s" % self.nodeItem.node.title)
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.tableView = QtWidgets.QTableView(self)
        self.gridLayout.addWidget(self.tableView, 0, 0, 1, 1)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.ok = QtWidgets.QPushButton(self)
        self.horizontalLayout.addWidget(self.ok)
        self.cancel = QtWidgets.QPushButton(self)
        self.horizontalLayout.addWidget(self.cancel)

        self.gridLayout.addLayout(self.horizontalLayout, 5, 0, 1, 1)
        self.line = QtWidgets.QFrame(self)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.gridLayout.addWidget(self.line, 3, 0, 1, 1)
        self.horizontalLayout2 = QtWidgets.QHBoxLayout()
        self.label = QtWidgets.QLabel(self)
        self.horizontalLayout2.addWidget(self.label)
        self.title = QtWidgets.QLineEdit(self)
        self.horizontalLayout2.addWidget(self.title)
        self.gridLayout.addLayout(self.horizontalLayout2, 0, 0, 1, 1)

        self.gridLayout.addWidget(self.tableView, 4, 0, 1, 1)
        self.label2 = QtWidgets.QLabel(self)
        self.gridLayout.addWidget(self.label2, 1, 0, 1, 1)
        self.description = QtWidgets.QPlainTextEdit(self)
        self.description.setMaximumSize(QtCore.QSize(16777215, 100))
        self.gridLayout.addWidget(self.description, 2, 0, 1, 1)

        self.ok.setText('Ok')
        self.cancel.setText('Cancel')
        self.label.setText('Title: ')
        self.label2.setText('Description:')

        self.cancel.clicked.connect(self.close)

        self.title.setText(self.nodeItem.node.title)
        self.description.setPlainText(self.nodeItem.node.description)

        self.model = QStandardItemModel(1, 2, self)

        self.tableView.horizontalHeader().setStretchLastSection(True)

        self.model.setHeaderData(0, Qt.Horizontal, 'Key')
        self.model.setHeaderData(1, Qt.Horizontal, 'Value')

        self.tableView.setModel(self.model)

        self.model.itemChanged.connect(self.rowCheck)

        self.rows = 0

        for k, v in self.nodeItem.node.attributes.items():
            self.model.insertRow(self.rows, [QStandardItem(k), QStandardItem(v)])
            self.rows += 1

    def rowCheck(self):
        if self.model.item(self.rows, 0) is not None or self.model.item(self.rows, 1) is not None:
            self.rows += 1
            self.model.insertRow(self.rows, [])


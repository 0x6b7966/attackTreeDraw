from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QWidget, QHeaderView, QMessageBox
from PyQt5 import QtCore, QtGui, QtWidgets


class NodeEdit(QWidget):
    def __init__(self, node, parent):
        QWidget.__init__(self)
        self.nodeItem = node
        self.parentWidget = parent
        self.setupUi()
        self.show()

    def setupUi(self):
        self.resize(320, 440)
        self.setWindowTitle("Node: %s" % self.nodeItem.node.title)

        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.idLayout = QtWidgets.QHBoxLayout()
        self.idLabel = QtWidgets.QLabel(self)
        self.idLabel.setMaximumSize(QtCore.QSize(70, 16777215))
        self.idLayout.addWidget(self.idLabel)
        self.idTextLabel = QtWidgets.QLabel(self)
        self.idLayout.addWidget(self.idTextLabel)
        self.verticalLayout.addLayout(self.idLayout)

        self.titleLayout = QtWidgets.QHBoxLayout()
        self.titleLabel = QtWidgets.QLabel(self)
        self.titleLayout.addWidget(self.titleLabel)
        self.titleEdit = QtWidgets.QLineEdit(self)
        self.titleLayout.addWidget(self.titleEdit)
        self.verticalLayout.addLayout(self.titleLayout)

        self.descriptionLabel = QtWidgets.QLabel(self)
        self.verticalLayout.addWidget(self.descriptionLabel)
        self.descriptionEdit = QtWidgets.QPlainTextEdit(self)
        self.descriptionEdit.setMaximumSize(QtCore.QSize(16777215, 100))
        self.verticalLayout.addWidget(self.descriptionEdit)

        self.line = QtWidgets.QFrame(self)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.verticalLayout.addWidget(self.line)

        self.tableView = QtWidgets.QTableView(self)
        self.verticalLayout.addWidget(self.tableView)

        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.ok = QtWidgets.QPushButton(self)
        self.buttonLayout.addWidget(self.ok)
        self.cancel = QtWidgets.QPushButton(self)
        self.buttonLayout.addWidget(self.cancel)
        self.verticalLayout.addLayout(self.buttonLayout)

        self.ok.setText('Ok')
        self.cancel.setText('Cancel')
        self.titleLabel.setText('Title: ')
        self.descriptionLabel.setText('Description:')
        self.idLabel.setText('Node-ID: ')
        self.idTextLabel.setText(self.nodeItem.node.id)

        self.cancel.clicked.connect(self.close)
        self.ok.clicked.connect(self.submit)

        self.titleEdit.setText(self.nodeItem.node.title)
        self.descriptionEdit.setPlainText(self.nodeItem.node.description)

        self.model = QStandardItemModel(0, 2, self)

        self.tableView.horizontalHeader().setStretchLastSection(True)

        self.model.setHeaderData(0, Qt.Horizontal, 'Key')
        self.model.setHeaderData(1, Qt.Horizontal, 'Value')

        self.tableView.setModel(self.model)

        self.model.itemChanged.connect(self.rowCheck)

        self.rows = 0

        for k, v in self.nodeItem.node.attributes.items():
            self.model.insertRow(self.rows, [QStandardItem(k), QStandardItem(v)])
            self.rows += 1

        self.model.insertRow(self.rows, [])

    def rowCheck(self):
        for i in range(self.rows):
            if (self.model.item(i, 0) is None or self.model.item(i, 0).text() == '') \
                    and (self.model.item(i, 1) is None or self.model.item(i, 1).text() == ''):
                self.model.removeRow(i)
                self.rows -= 1

        if (self.model.item(self.rows, 0) is not None and self.model.item(self.rows, 0).text() != '') \
                or (self.model.item(self.rows, 1) is not None and self.model.item(self.rows, 1).text() != ''):
            self.rows += 1
            self.model.insertRow(self.rows, [])

    def submit(self):
        self.model.removeRow(self.rows)
        self.rows -= 1

        newEntires = {}

        if self.titleEdit.text() == '':
            msgBox = QMessageBox()
            msgBox.setText("Error in with the title")
            msgBox.setInformativeText("The title can't be none")
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.setDefaultButton(QMessageBox.Ok)
            msgBox.exec()
            return

        for i in range(self.rows + 1):
            if self.model.item(i, 0) is None or self.model.item(i, 0).text() == '':
                msgBox = QMessageBox()
                msgBox.setText("Error in key at row %s" % (i + 1))
                msgBox.setInformativeText("The key can't be none")
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.setDefaultButton(QMessageBox.Ok)
                msgBox.exec()
                return

            if self.model.item(i, 1) is None or self.model.item(i, 1).text() == '':
                msgBox = QMessageBox()
                msgBox.setText("Error in value at row %s" % (i + 1))
                msgBox.setInformativeText("The value can't be none")
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.setDefaultButton(QMessageBox.Ok)
                msgBox.exec()
                return

            if self.model.item(self.rows, 0).text() in newEntires.keys():
                msgBox = QMessageBox()
                msgBox.setText("Error in with the key at row %s" % (i + 1))
                msgBox.setInformativeText("The key already exists")
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.setDefaultButton(QMessageBox.Ok)
                msgBox.exec()
                return

            newEntires[self.model.item(i, 0).text()] = self.model.item(i, 1).text()

        self.nodeItem.node.attributes = newEntires.copy()
        self.nodeItem.node.title = self.titleEdit.text()
        self.nodeItem.node.description = self.descriptionEdit.toPlainText()

        self.nodeItem.redraw()

        viewport = self.parentWidget.graphicsView.viewport()
        viewport.update()

        self.close()

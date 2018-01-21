import traceback
import sys

import os
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import QWidget, QMessageBox, QDialog
from PyQt5 import QtCore, QtWidgets


class MessageBox:
    def __init__(self, title, text, buttons=QMessageBox.Ok, icon=QMessageBox.Information, default=QMessageBox.Ok):
        includePath = os.path.dirname(os.path.abspath(__file__))
        self.msgBox = QMessageBox()
        self.msgBox.setWindowTitle(title)
        self.msgBox.setText(text)
        self.msgBox.setStandardButtons(buttons)
        self.msgBox.setDefaultButton(default)
        self.msgBox.setIcon(icon)
        self.msgBox.setWindowIcon(QIcon(os.path.join(includePath, 'assets/icons/logo.png')))

    def run(self):
        return self.msgBox.exec()


class NodeEdit(QDialog):
    def __init__(self, node, parent):
        QWidget.__init__(self)
        self.nodeItem = node
        self.parentWidget = parent
        self.setupUi()
        self.show()

    def setupUi(self):
        includePath = os.path.dirname(os.path.abspath(__file__))
        self.resize(320, 440)
        self.setWindowTitle("Node: %s" % self.nodeItem.node.title)
        self.setWindowIcon(QIcon(os.path.join(includePath, 'assets/icons/logo.png')))

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
            MessageBox('Error in the title', 'The title can\'t be none!', icon=QMessageBox.Critical).run()
            return

        for i in range(self.rows + 1):
            if self.model.item(i, 0) is None or self.model.item(i, 0).text() == '':
                MessageBox('Error in key at row %s' % (i + 1), '"The key in row %s can\'t be none!' % (i + 1), icon=QMessageBox.Critical).run()
                return

            if self.model.item(i, 1) is None or self.model.item(i, 1).text() == '':
                MessageBox('Error in value at row %s' % (i + 1), 'The value in row %s can\'t be none!' % (i + 1), icon=QMessageBox.Critical).run()
                return

            if self.model.item(self.rows, 0).text() in newEntires.keys():
                MessageBox('Error with the key at row %s' % (i + 1), 'The key in row %s already exists!' % (i + 1), icon=QMessageBox.Critical).run()
                return

            newEntires[self.model.item(i, 0).text()] = self.model.item(i, 1).text()

        self.nodeItem.node.attributes = newEntires.copy()
        self.nodeItem.node.title = self.titleEdit.text()
        self.nodeItem.node.description = self.descriptionEdit.toPlainText()

        self.nodeItem.redraw()

        viewport = self.parentWidget.graphicsView.viewport()
        viewport.update()

        self.close()


class MetaEdit(QDialog):
    def __init__(self, parent):
        QWidget.__init__(self)
        self.parentWidget = parent
        self.setupUi()

    def setupUi(self):
        includePath = os.path.dirname(os.path.abspath(__file__))
        self.resize(400, 300)
        self.setWindowTitle('Edit meta information')
        self.setWindowIcon(QIcon(os.path.join(includePath, 'assets/icons/logo.png')))

        self.verticalLayout = QtWidgets.QVBoxLayout(self)

        self.titleLayout = QtWidgets.QHBoxLayout()
        self.titleLabel = QtWidgets.QLabel(self)
        self.titleLabel.setMinimumSize(QtCore.QSize(80, 0))
        self.titleLayout.addWidget(self.titleLabel)
        self.titleEdit = QtWidgets.QLineEdit(self)
        self.titleLayout.addWidget(self.titleEdit)
        self.verticalLayout.addLayout(self.titleLayout)

        self.authorLayout = QtWidgets.QHBoxLayout()
        self.authorLabel = QtWidgets.QLabel(self)
        self.authorLabel.setMinimumSize(QtCore.QSize(80, 0))
        self.authorLayout.addWidget(self.authorLabel)
        self.authorEdit = QtWidgets.QLineEdit(self)
        self.authorLayout.addWidget(self.authorEdit)
        self.verticalLayout.addLayout(self.authorLayout)

        self.dateLayout = QtWidgets.QHBoxLayout()
        self.dateLabel = QtWidgets.QLabel(self)
        self.dateLabel.setMaximumSize(QtCore.QSize(80, 16777215))
        self.dateLayout.addWidget(self.dateLabel)
        self.dateEdit = QtWidgets.QDateEdit(self)
        self.dateLayout.addWidget(self.dateEdit)
        self.verticalLayout.addLayout(self.dateLayout)

        self.dateEdit.setDate(QDate.currentDate())

        self.rootLayout = QtWidgets.QHBoxLayout()
        self.rootLabel = QtWidgets.QLabel(self)
        self.rootLabel.setMaximumSize(QtCore.QSize(80, 16777215))
        self.rootLayout.addWidget(self.rootLabel)
        self.rootSelect = QtWidgets.QComboBox(self)
        self.rootLayout.addWidget(self.rootSelect)
        self.verticalLayout.addLayout(self.rootLayout)

        self.line = QtWidgets.QFrame(self)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.verticalLayout.addWidget(self.line)

        self.descriptionLabel = QtWidgets.QLabel(self)
        self.verticalLayout.addWidget(self.descriptionLabel)
        self.descriptionEdit = QtWidgets.QPlainTextEdit(self)
        self.descriptionEdit.setMaximumSize(QtCore.QSize(16777215, 100))
        self.verticalLayout.addWidget(self.descriptionEdit)

        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.ok = QtWidgets.QPushButton(self)
        self.buttonLayout.addWidget(self.ok)
        self.cancel = QtWidgets.QPushButton(self)
        self.buttonLayout.addWidget(self.cancel)
        self.verticalLayout.addLayout(self.buttonLayout)

        self.ok.setText('Ok')
        self.cancel.setText('Cancel')

        self.titleLabel.setText('Title:')
        self.authorLabel.setText('Author:')
        self.dateLabel.setText('Date:')
        self.rootLabel.setText('Root node:')
        self.descriptionLabel.setText('Description:')

        self.cancel.clicked.connect(self.close)
        self.ok.clicked.connect(self.submit)

        for k, v in self.parentWidget.tree.nodeList.items():
            if len(v.parents) == 0 and v.type == 'threat':
                self.rootSelect.addItem(k + ' -- ' + v.title)

    def submit(self):
        if self.titleEdit.text() == '':
            MessageBox('Error in the title', 'The title can\'t be none!', icon=QMessageBox.Critical).run()
            return

        if self.authorEdit.text() == '':
            MessageBox('Error with the author', 'The author can\'t be none!', icon=QMessageBox.Critical).run()
            return

        self.parentWidget.tree.meta['author'] = self.authorEdit.text()
        self.parentWidget.tree.meta['title'] = self.titleEdit.text()
        self.parentWidget.tree.meta['date'] = self.dateEdit.date().toString('yyyy-MM-dd')
        self.parentWidget.tree.meta['description'] = self.descriptionEdit.toPlainText()
        if self.parentWidget.tree.root is not None:
            self.parentWidget.tree.nodeList[self.parentWidget.tree.root].isRoot = False
        if self.rootSelect.currentText() != '':
            self.parentWidget.tree.root = self.rootSelect.currentText().split(' -- ')[0]
            self.parentWidget.tree.nodeList[self.rootSelect.currentText().split(' -- ')[0]].isRoot = True
        self.close()

import os

from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import QWidget, QMessageBox, QDialog, QLabel, QColorDialog, QFrame
from PyQt5 import QtCore, QtWidgets

from data.types import Threat


class MessageBox:
    """
    Class to display a message box with options
    """
    def __init__(self, title, text, buttons=QMessageBox.Ok, icon=QMessageBox.Information, default=QMessageBox.Ok):
        """
        Constructor for the message box.
        Sets all options

        @param title: Title of the message box
        @param text: Message box text
        @param buttons: Buttons for the message box (default: ok)
        @param icon: Icon for the message box (default: information)
        @param default: default button to click (default: ok)
        """
        includePath = os.path.dirname(os.path.abspath(__file__))
        self.msgBox = QMessageBox()
        self.msgBox.setWindowTitle(title)
        self.msgBox.setText(text)
        self.msgBox.setStandardButtons(buttons)
        self.msgBox.setDefaultButton(default)
        self.msgBox.setIcon(icon)
        self.msgBox.setWindowIcon(QIcon(os.path.join(includePath, 'assets/icons/logo.png')))

    def run(self):
        """
        Runs the message box
        @return: Status code
        """
        return self.msgBox.exec()


class NodeEdit(QDialog):
    """
    Dialog box to edit nodes
    The user can change the title or attributes of a node in this window
    """
    def __init__(self, node, parent):
        """
        Constructor for the node edit UI

        @param node: Node to edit
        @param parent: Parent widget
        """
        QWidget.__init__(self)
        self.nodeItem = node
        self.parentWidget = parent
        self.setupUi()

    def setupUi(self):
        """
        Sets up the UI.
        """
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
        """
        This function checks if there are empty rows and adds an empty row to the end of the tableView
        """
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
        """
        This function checks if the input in the form is correct.
        If the check is false it will print an error message

        After all checks where successful the Window will be closed and the node updated
        """
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
    """
    Dialog box to edit the meta information of the tree
    The user can change the title, author, date, description and the root node
    """
    def __init__(self, parent):
        """
        Constructor for the node edit UI

        @param parent: Parent widget
        """
        QWidget.__init__(self)
        self.parentWidget = parent
        self.setupUi()

    def setupUi(self):
        """
        Sets up the UI.
        """
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
            if len(v.parents) == 0 and isinstance(v, Threat):
                self.rootSelect.addItem(k + ' -- ' + v.title)

    def submit(self):
        """
        This function checks if the input in the form is correct.
        If the check is false it will print an error message

        After all checks where successful the Window will be closed and the node updated
        """
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


class Options(QDialog):
    """
    Dialog box to edit the options of the GUI
    The user can change the color of the nodes
    """
    def __init__(self, parent):
        """
        Constructor for the node edit UI

        @param parent: Parent widget
        """
        QWidget.__init__(self)
        self.parentWidget = parent
        self.setupUi()
        self.show()

    def setupUi(self):
        """
        Sets up the UI.
        """
        self.resize(407, 408)
        self.verticalLayout = QtWidgets.QVBoxLayout(self)

        includePath = os.path.dirname(os.path.abspath(__file__))
        self.setWindowIcon(QIcon(os.path.join(includePath, 'assets/icons/logo.png')))

        self.tabWidget = QtWidgets.QTabWidget(self)
        self.tab = QtWidgets.QWidget()
        self.tabWidget.addTab(self.tab, "")

        self.colors = QtWidgets.QWidget()

        self.colorsLayout = QtWidgets.QVBoxLayout(self.colors)
        self.threatLabel = QtWidgets.QLabel(self.colors)
        self.colorsLayout.addWidget(self.threatLabel)

        self.threatBackgroundLayout = QtWidgets.QHBoxLayout()
        self.threatBackgroundLayout.addItem(QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum))
        self.threatBackgroundLabel = QtWidgets.QLabel(self.colors)
        self.threatBackgroundLayout.addWidget(self.threatBackgroundLabel)
        self.threatBackgroundPicker = ColorLabel(self.parentWidget.threatBackground, self.colors)
        self.threatBackgroundLayout.addWidget(self.threatBackgroundPicker)
        self.colorsLayout.addLayout(self.threatBackgroundLayout)

        self.threatBorderLayout = QtWidgets.QHBoxLayout()
        self.threatBorderLayout.addItem(QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum))
        self.threatBorderLabel = QtWidgets.QLabel(self.colors)
        self.threatBorderLayout.addWidget(self.threatBorderLabel)
        self.threatBorderPicker = ColorLabel(self.parentWidget.threatBorder, self.colors)
        self.threatBorderLayout.addWidget(self.threatBorderPicker)
        self.colorsLayout.addLayout(self.threatBorderLayout)

        self.threatFontLayout = QtWidgets.QHBoxLayout()
        self.threatFontLayout.addItem(QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum))
        self.threatFontLabel = QtWidgets.QLabel(self.colors)
        self.threatFontLayout.addWidget(self.threatFontLabel)
        self.threatFontPicker = ColorLabel(self.parentWidget.threatFont, self.colors)
        self.threatFontLayout.addWidget(self.threatFontPicker)
        self.colorsLayout.addLayout(self.threatFontLayout)

        self.line_2 = QtWidgets.QFrame(self.colors)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.colorsLayout.addWidget(self.line_2)

        self.countermeasureLabel = QtWidgets.QLabel(self.colors)
        self.colorsLayout.addWidget(self.countermeasureLabel)

        self.countermeasureBackgroundLayout = QtWidgets.QHBoxLayout()
        self.countermeasureBackgroundLayout.addItem(QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum))
        self.countermeasureBackgroundLabel = QtWidgets.QLabel(self.colors)
        self.countermeasureBackgroundLayout.addWidget(self.countermeasureBackgroundLabel)
        self.countermeasureBackgroundPicker = ColorLabel(self.parentWidget.countermeasureBackground, self.colors)
        self.countermeasureBackgroundLayout.addWidget(self.countermeasureBackgroundPicker)
        self.colorsLayout.addLayout(self.countermeasureBackgroundLayout)

        self.countermeasureBorderLayout = QtWidgets.QHBoxLayout()
        self.countermeasureBorderLayout.addItem(QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum))
        self.countermeasureBorderLabel = QtWidgets.QLabel(self.colors)
        self.countermeasureBorderLayout.addWidget(self.countermeasureBorderLabel)
        self.countermeasureBorderPicker = ColorLabel(self.parentWidget.countermeasureBorder, self.colors)
        self.countermeasureBorderLayout.addWidget(self.countermeasureBorderPicker)
        self.colorsLayout.addLayout(self.countermeasureBorderLayout)

        self.countermeasureFontLayout = QtWidgets.QHBoxLayout()
        self.countermeasureFontLayout.addItem(QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum))
        self.countermeasureFontLabel = QtWidgets.QLabel(self.colors)
        self.countermeasureFontLayout.addWidget(self.countermeasureFontLabel)
        self.countermeasureFontPicker = ColorLabel(self.parentWidget.countermeasureFont, self.colors)
        self.countermeasureFontLayout.addWidget(self.countermeasureFontPicker)
        self.colorsLayout.addLayout(self.countermeasureFontLayout)

        self.line = QtWidgets.QFrame(self.colors)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.colorsLayout.addWidget(self.line)
        self.tabWidget.addTab(self.colors, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.horizontalLayout = QtWidgets.QHBoxLayout()

        self.ok = QtWidgets.QPushButton(self)
        self.horizontalLayout.addWidget(self.ok)

        self.cancel = QtWidgets.QPushButton(self)
        self.horizontalLayout.addWidget(self.cancel)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.tabWidget.setCurrentIndex(1)
        
        self.setWindowTitle("Dialog")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), "General")
        self.threatLabel.setText("Threat colors:")
        self.threatBackgroundLabel.setText("Background:")
        self.threatBorderLabel.setText("Border:")
        self.threatFontLabel.setText("Font:")
        self.countermeasureLabel.setText("Countermeasure colors:")
        self.countermeasureBackgroundLabel.setText("Background:")
        self.countermeasureBorderLabel.setText("Border:")
        self.countermeasureFontLabel.setText("Font:")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.colors), "Colors")
        self.cancel.setText("Cancel")
        self.ok.setText("Ok")

        self.cancel.clicked.connect(self.close)
        self.ok.clicked.connect(self.submit)

    def submit(self):
        """
        This function saves the input of the color picker to the parent widget and redraws the tree

        After that the window will be closed
        """
        self.parentWidget.threatBackground = self.threatBackgroundPicker.color
        self.parentWidget.threatBorder = self.threatBorderPicker.color
        self.parentWidget.threatFont = self.threatFontPicker.color

        self.parentWidget.countermeasureBackground = self.countermeasureBackgroundPicker.color
        self.parentWidget.countermeasureBorder = self.countermeasureBorderPicker.color
        self.parentWidget.countermeasureFont = self.countermeasureFontPicker.color

        self.parentWidget.redrawItems()
        self.close()


class ColorLabel(QLabel):
    """
    This class implements an color picker for the options GUI
    """
    def __init__(self, color, parent=None):
        """
        Constructor for the node edit UI

        @param color: Default color for the color picker
        @param parent: Parent widget
        """
        super().__init__(parent)

        self.color = color

        palette = self.palette()
        palette.setColor(self.backgroundRole(), color)
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        self.setFrameStyle(QFrame.Panel)

    def mousePressEvent(self, QMouseEvent):
        """
        Mouse event for the color picker

        @param QMouseEvent: Mouse event
        """
        self.color = QColorDialog.getColor(self.color, self, "Pick a color", QColorDialog.DontUseNativeDialog)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), self.color)
        self.setAutoFillBackground(True)
        self.setPalette(palette)

import functools
import os

from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon, QFont, QColor
from PyQt5.QtWidgets import QWidget, QMessageBox, QDialog, QLabel, QColorDialog, QFrame, QFontDialog
from PyQt5 import QtCore, QtWidgets

from data.types import Threat
from gui import helper
from gui.helper import Configuration


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
        self.nodeItem.node.title = self.titleEdit.text().replace('\n', ' ').replace('\r', '')
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


class Options(QWidget):
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
        self.rows = {
            'threat': {'node': {}, 'composition': {}, 'alternative': {}, 'sequence': {}, 'threshold': {}},
            'countermeasure': {'node': {}, 'composition': {}, 'alternative': {}, 'sequence': {}, 'threshold': {}}
        }

        self.setupUi()
        self.show()

    def setupUi(self):
        """
        Sets up the UI.
        """
        self.resize(432, 392)

        self.mainLayout = QtWidgets.QVBoxLayout(self)

        self.tabWidget = QtWidgets.QTabWidget(self)
        self.generalTab = QtWidgets.QWidget()
        self.threatColorTab = QtWidgets.QWidget()
        self.countermeasureColorTab = QtWidgets.QWidget()

        colorParts = ['background', 'border', 'font']

        """ General Tab """
        self.generalTabLayout = QtWidgets.QVBoxLayout(self.generalTab)
        self.fontLayout = QtWidgets.QHBoxLayout()
        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.fontLayout.addItem(spacer)
        self.fontTitleLabel = QtWidgets.QLabel(self.generalTab)
        self.fontLayout.addWidget(self.fontTitleLabel)
        self.fontValueLabel = QtWidgets.QLabel(self.generalTab)
        self.fontLayout.addWidget(self.fontValueLabel)
        self.fontChangeButton = QtWidgets.QPushButton(self.generalTab)
        self.fontLayout.addWidget(self.fontChangeButton)
        self.generalTabLayout.addLayout(self.fontLayout)
        self.generalLine = QtWidgets.QFrame(self.generalTab)
        self.generalLine.setFrameShape(QtWidgets.QFrame.HLine)
        self.generalLine.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.generalTabLayout.addWidget(self.generalLine)

        self.generalTabFreeLayout = QtWidgets.QVBoxLayout()
        self.generalTabLayout.addLayout(self.generalTabFreeLayout)

        self.fontTitleLabel.setText("Font:")
        self.fontValueLabel.setText(Configuration.font.family() + ' ' + str(Configuration.font.pointSizeF()))
        self.fontChangeButton.setText("Change")
        self.fontChangeButton.clicked.connect(self.openFontPicker)

        """ Threat Color Tab """
        self.threatColorTabLayout = QtWidgets.QVBoxLayout(self.threatColorTab)
        self.threatColorTabTitle = QtWidgets.QLabel(self.threatColorTab)
        self.threatColorTabTitle.setText('Threat Colors')
        self.threatColorTabLayout.addWidget(self.threatColorTabTitle)

        for k, r in self.rows['threat'].items():
            layout = QtWidgets.QHBoxLayout()
            spacer1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
            layout.addItem(spacer1)
            titleLabel = QtWidgets.QLabel(self.threatColorTab)
            titleLabel.setMinimumSize(QtCore.QSize(90, 0))
            titleLabel.setMaximumSize(QtCore.QSize(90, 16777215))
            titleLabel.setText(k.title() + ':')
            layout.addWidget(titleLabel)
            for c in colorParts:
                pass
                r[c] = (QtWidgets.QLabel(self.threatColorTab))
                palette = r[c].palette()
                palette.setColor(r[c].backgroundRole(), QColor(Configuration.colors['threat'][k][c]))
                r[c].setAutoFillBackground(True)
                r[c].setPalette(palette)
                r[c].setFrameStyle(QFrame.Panel)
                layout.addWidget(r[c])

            change = QtWidgets.QPushButton(self.threatColorTab)
            change.setText('Change')

            change.clicked.connect(functools.partial(self.openColorPicker, 'threat', k))

            layout.addWidget(change)

            self.threatColorTabLayout.addLayout(layout)

        """ Countermeasure Color Tab """
        self.countermeasureColorTabLayout = QtWidgets.QVBoxLayout(self.countermeasureColorTab)
        self.countermeasureColorTabTitle = QtWidgets.QLabel(self.countermeasureColorTab)
        self.countermeasureColorTabTitle.setText('Countermeasure Colors')
        self.countermeasureColorTabLayout.addWidget(self.countermeasureColorTabTitle)

        for k, r in self.rows['countermeasure'].items():
            layout = QtWidgets.QHBoxLayout()
            spacer1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
            layout.addItem(spacer1)
            titleLabel = QtWidgets.QLabel(self.countermeasureColorTab)
            titleLabel.setMinimumSize(QtCore.QSize(90, 0))
            titleLabel.setMaximumSize(QtCore.QSize(90, 16777215))
            titleLabel.setText(k.title() + ':')
            layout.addWidget(titleLabel)
            for c in colorParts:
                pass
                r[c] = (QtWidgets.QLabel(self.countermeasureColorTab))
                palette = r[c].palette()
                palette.setColor(r[c].backgroundRole(), QColor(Configuration.colors['countermeasure'][k][c]))
                r[c].setAutoFillBackground(True)
                r[c].setPalette(palette)
                r[c].setFrameStyle(QFrame.Panel)
                layout.addWidget(r[c])

            change = QtWidgets.QPushButton(self.countermeasureColorTab)
            change.setText('Change')

            change.clicked.connect(functools.partial(self.openColorPicker, 'countermeasure', k))

            layout.addWidget(change)

            self.countermeasureColorTabLayout.addLayout(layout)

        self.mainLayout.addWidget(self.tabWidget)


        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.ok = QtWidgets.QPushButton(self)
        self.buttonLayout.addWidget(self.ok)
        self.ok.setDefault(True)
        self.cancel = QtWidgets.QPushButton(self)
        self.buttonLayout.addWidget(self.cancel)
        self.mainLayout.addLayout(self.buttonLayout)

        self.cancel.setText("Cancel")
        self.ok.setText("Ok")

        self.tabWidget.setCurrentIndex(1)

        self.ok.clicked.connect(self.submit)
        self.cancel.clicked.connect(self.close)

        self.tabWidget.addTab(self.generalTab, "General")
        self.tabWidget.addTab(self.threatColorTab, "Threat Colors")
        self.tabWidget.addTab(self.countermeasureColorTab, "Countermeasure Colors")

    def submit(self):
        """
        This function saves the config and calls the configuration helper to save it to the config file

        After that the window will be closed
        """
        helper.Configuration.saveConfig()

        self.parentWidget.redrawItems()
        self.close()

    def openColorPicker(self, parentType, childType):
        """
        Opens the color picker to choose a color for the node
        @param parentType: Parent type for the color (Threat, Countermeasure, default)
        @param childType: Conjunction type or node
        """
        picker = ColorPicker(self, parentType, childType)
        picker.exec()
        for k, i in self.rows[parentType][childType].items():
            palette = i.palette()
            palette.setColor(i.backgroundRole(), QColor(Configuration.colors[parentType][childType][k]))
            i.setAutoFillBackground(True)
            i.setPalette(palette)
            i.setFrameStyle(QFrame.Panel)

    def openFontPicker(self):
        """
        Opens the font picker for the font of the nodes
        """
        dialog = QFontDialog()
        font, ok = dialog.getFont(QFont('Roboto Mono', 12), self)
        Configuration.font = font

        self.fontValueLabel.setText(font.family() + ' ' + str(font.pointSizeF()))


class ColorPicker(QDialog):
    """
    Dialog box to edit the options of the GUI
    The user can change the color of the nodes
    """

    def __init__(self, parent, parentType, childType):
        """
        Constructor for the node edit UI

        @param parent: Parent widget
        """
        QWidget.__init__(self)
        self.parentWidget = parent
        self.parentType = parentType
        self.childType = childType
        self.setupUi()

    def setupUi(self):
        """
        Sets up the UI.
        """
        self.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.nodeLabel = QtWidgets.QLabel(self)
        self.verticalLayout.addWidget(self.nodeLabel)

        self.borderLayout = QtWidgets.QHBoxLayout()
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.borderLayout.addItem(spacerItem)
        self.borderLabel = QtWidgets.QLabel(self)

        self.borderLayout.addWidget(self.borderLabel)
        self.borderPicker = ColorLabel(Configuration.colors[self.parentType][self.childType]['border'], self)

        self.borderLayout.addWidget(self.borderPicker)
        self.verticalLayout.addLayout(self.borderLayout)
        self.fontLayout = QtWidgets.QHBoxLayout()

        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.fontLayout.addItem(spacer)
        self.fontLabel = QtWidgets.QLabel(self)

        self.fontLayout.addWidget(self.fontLabel)
        self.fontPicker = ColorLabel(Configuration.colors[self.parentType][self.childType]['font'], self)

        self.fontLayout.addWidget(self.fontPicker)
        self.verticalLayout.addLayout(self.fontLayout)
        self.backgroundLayout = QtWidgets.QHBoxLayout()

        spacer2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.backgroundLayout.addItem(spacer2)
        self.backgroundLabel = QtWidgets.QLabel(self)

        self.backgroundLayout.addWidget(self.backgroundLabel)
        self.backgroundPicker = ColorLabel(Configuration.colors[self.parentType][self.childType]['background'], self)

        self.backgroundLayout.addWidget(self.backgroundPicker)
        self.verticalLayout.addLayout(self.backgroundLayout)

        self.line = QtWidgets.QFrame(self)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.verticalLayout.addWidget(self.line)
        self.horizontalLayout = QtWidgets.QHBoxLayout()

        self.ok = QtWidgets.QPushButton(self)
        self.horizontalLayout.addWidget(self.ok)

        self.cancel = QtWidgets.QPushButton(self)
        self.horizontalLayout.addWidget(self.cancel)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.cancel.setText("Cancel")
        self.ok.setText("Ok")

        self.cancel.clicked.connect(self.close)
        self.ok.clicked.connect(self.submit)

        self.setWindowTitle(self.parentType + ' ' + self.childType + ' Colors')
        self.nodeLabel.setText(self.parentType + ' ' + self.childType + ' Colors:')

        self.borderLabel.setText('Border:')
        self.fontLabel.setText('Font:')
        self.backgroundLabel.setText('Background:')

    def submit(self):
        """
        This function saves the input of the color picker to the parent widget and redraws the tree

        After that the window will be closed
        """
        helper.Configuration.colors[self.parentType][self.childType]['background'] = QColor(self.backgroundPicker.color).name()
        helper.Configuration.colors[self.parentType][self.childType]['border'] = QColor(self.borderPicker.color).name()
        helper.Configuration.colors[self.parentType][self.childType]['font'] = QColor(self.fontPicker.color).name()

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
        palette.setColor(self.backgroundRole(), QColor(color))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        self.setFrameStyle(QFrame.Panel)

    def mousePressEvent(self, QMouseEvent):
        """
        Mouse event for the color picker

        @param QMouseEvent: Mouse event
        """
        self.color = QColorDialog.getColor(QColor(self.color), self, "Pick a color", QColorDialog.DontUseNativeDialog)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(self.color))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

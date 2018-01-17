import sys

from PyQt5 import QtCore, QtGui, QtWidgets

from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QApplication, QToolBox, QGraphicsScene, QGraphicsItem, \
    QGraphicsItemGroup, QWidget, QFileDialog, QMessageBox, QDialog
from PyQt5.QtGui import QIcon, QImage, QPainter

from .items import Node, Arrow, Threat, Countermeasure, Conjunction, AttackTreeScene

from data.handler import Handler

from data import types


class Main(QMainWindow):

    def __init__(self):
        super().__init__()

        self.tree = types.Tree(False)
        self.saved = True
        self.file = ('', '')
        self.itemList = []
        self.initUI()

        self.mode = 0  # 0: default, 1: add threat, 2: add countermeasure, 3: add composition

        self.scene.clear()

    def initUI(self):

        # from PyQt5 import uic
        # uic.loadUi('../../attackTreeDrawQt/self.ui', self)
        # self.setWindowTitle('attackTreeDraw')
        # self.show()

        # return

        menuBarItems = {
            'File': {
                # Name     shortcut   tip          action
                '&New': ['Ctrl+N', 'New Tree', self.new],
                '&Open': ['Ctrl+O', 'Open File', self.loadFile],
                '&Save': ['Ctrl+S', 'Print Tree', self.saveFile],
                'Save &As ...': ['Ctrl+Shift+S', 'Print Tree', self.saveFileAs],
                'SEPARATOR01': [],
                'Export as P&DF': ['Ctrl+Shift+E', 'Export Tree', self.exportPDF],
                'Export as PN&G': ['Ctrl+Shift+Alt+E', 'Export Tree', self.exportPNG],
                'SEPARATOR02': [],
                '&Close Tree': ['Ctrl+W', 'Open File', self.close],
                '&Print': ['Ctrl+P', 'Print Tree', self.print],
                '&Exit': ['Ctrl+Q', 'Print Tree', self.close],

            },
            'Edit': {
                # Name     shortcut   tip          action
                '&Undo': ['Ctrl+U', 'Undo Action', self.close],
                '&Redo': ['Ctrl+Shift+U', 'Redo Action', self.close],
                'SEPARATOR01': [],

            },
            'Tree': {
                # Name     shortcut   tip          action
                '&Redraw Tree': ['Ctrl++Shift+R', 'Redraw and reorder Tree', self.redrawGraph],
                'SEPARATOR01': [],

            },
            'Window': {
                # Name     shortcut   tip          action
            },
            'About': {
                # Name     shortcut   tip          action
                '&Help': ['', 'Help', self.close],
                '&About': ['', 'About', self.close],
            },
        }

        mainToolbarItems = {
            'New': ['gui/assets/icons/new.png', 'Ctrl+N', 'New Tree', self.new],
            'Open': ['gui/assets/icons/open.png', 'Ctrl+O', 'Open Tree', self.loadFile],
            'Save': ['gui/assets/icons/save.png', 'Ctrl+S', 'Save Tree', self.saveFile],
            'Print': ['gui/assets/icons/print.png', 'Ctrl+P', 'Print File', self.print],
            'Undo': ['gui/assets/icons/undo.png', 'Ctrl+U', 'Undo', self.close],
            'Redo': ['gui/assets/icons/redo.png', 'Ctrl+Shift+U', 'Redo', self.close],
        }

        editToolbarItems = {
            'New Threat': ['gui/assets/icons/threat.png', '', 'New Threat', self.newThreat],
            'New Counter': ['gui/assets/icons/counter.png', '', 'New Countermeasure', self.newCountermeasure],
            'New Composition': ['gui/assets/icons/arrow.png', '', 'New Composition', self.newComposition],
        }

        self.setObjectName("MainWindow")

        self.resize(814, 581)
        self.setMinimumSize(QtCore.QSize(0, 0))
        self.setWindowTitle("attackTreeDraw")
        self.setDocumentMode(True)

        menuBar = self.menuBar()
        for k, v in menuBarItems.items():
            menuItem = menuBar.addMenu(k)
            for ks, s in v.items():
                if ks.startswith('SEPARATOR'):
                    menuItem.addSeparator()
                else:
                    action = QAction(ks, self)
                    action.setShortcut(s[0])
                    action.setStatusTip(s[1])
                    action.triggered.connect(s[2])
                    menuItem.addAction(action)

        self.centralWidget = QtWidgets.QWidget(self)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)

#        self.scrollArea = QtWidgets.QScrollArea(self.centralWidget)
#        self.scrollArea.setEnabled(True)
#        self.scrollArea.setStatusTip("")
#        self.scrollArea.setAccessibleName("")
#        self.scrollArea.setLineWidth(0)
#        self.scrollArea.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
#        self.scrollArea.setWidgetResizable(True)
#        self.scrollAreaWidgetContents = QtWidgets.QWidget()
#        # self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 1032, 1024))
#        self.formLayout = QtWidgets.QFormLayout(self.scrollAreaWidgetContents)
#        self.formLayout.setContentsMargins(0, 0, 0, 0)
#        self.formLayout.setSpacing(0)
#        self.graphicsView = QtWidgets.QGraphicsView(self.scrollAreaWidgetContents)

        self.graphicsView = QtWidgets.QGraphicsView(self.centralWidget)

        self.graphicsView.setMinimumSize(QtCore.QSize(self.width(), self.height()))
        self.graphicsView.setSizeIncrement(QtCore.QSize(0, 0))
        self.graphicsView.setBaseSize(QtCore.QSize(0, 0))
#        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.graphicsView)
#        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
#        self.verticalLayout.addWidget(self.scrollArea)
        self.setCentralWidget(self.centralWidget)
        self.statusBar = QtWidgets.QStatusBar(self)
        self.setStatusBar(self.statusBar)

        mainToolBar = QtWidgets.QToolBar(self)
        self.addToolBar(QtCore.Qt.TopToolBarArea, mainToolBar)
        for k, v in mainToolbarItems.items():
            action = QAction(QIcon(v[0]), k, self)
            action.setShortcut(v[2])
            action.setStatusTip(v[2])
            action.triggered.connect(v[3])

            mainToolBar.addAction(action)

        self.scene = AttackTreeScene(self)

        self.graphicsView.setScene(self.scene)

        # self.graphicsView.mapToScene(0, 0)

        self.scene.setSceneRect(self.scene.itemsBoundingRect())

        self.graphicsView.setAlignment(Qt.AlignTop)

        workToolbar = self.addToolBar('WorkToolbar')
        toolbox = QToolBox()
        workToolbar.setOrientation(Qt.Vertical)
        self.addToolBar(Qt.LeftToolBarArea, workToolbar)

        for k, v in editToolbarItems.items():
            action = QAction(QIcon(v[0]), k, self)
            action.setShortcut(v[2])
            action.setStatusTip(v[2])
            action.triggered.connect(v[3])

            workToolbar.addAction(action)

        workToolbar.addWidget(toolbox)

        self.show()

        self.graphicsView.setMinimumSize(QtCore.QSize(self.width() + 200, self.height() + 200))
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        width = self.scrollArea.frameSize().width() if self.scrollArea.frameSize().width() > self.scene.sceneRect().width() else self.scene.sceneRect().width()
        height = self.scrollArea.frameSize().height() if self.scrollArea.frameSize().height() > self.scene.sceneRect().height() else self.scene.sceneRect().height()

        width = self.frameSize().width() if self.frameSize().width() > self.scene.sceneRect().width() else self.scene.sceneRect().width()
        height = self.frameSize().height() if self.frameSize().height() > self.scene.sceneRect().height() else self.scene.sceneRect().height()

        self.graphicsView.setFixedSize(width + 10, height + 10)

    def printGraph(self):

        g = self.printGraphRecursion(self.tree.nodeList[self.tree.root], 0, 10)
        i = 0
        while self.reorderTree(g) is not True and i < 100:
            i += 1

        self.scene.setSceneRect(QRectF(self.scene.itemsBoundingRect().x() - 100, 0, self.scene.itemsBoundingRect().width() + 200, self.scene.itemsBoundingRect().height() + 100))

        width = self.scrollArea.frameSize().width() if self.scrollArea.frameSize().width() > self.scene.sceneRect().width() else self.scene.sceneRect().width()
        height = self.scrollArea.frameSize().height() if self.scrollArea.frameSize().height() > self.scene.sceneRect().height() else self.scene.sceneRect().height()

        viewport = self.graphicsView.viewport()
        viewport.update()

        self.graphicsView.setFixedSize(width + 10, height + 10)
        print('----- DONE -----')

    def printGraphRecursion(self, node, x, y, parent=None):
        g = []
        rec = False
        if node.view is None:
            if node.type == 'threat':
                n = Threat(node, self)
            elif node.type == 'countermeasure':
                n = Countermeasure(node, self)
            else:
                n = Node(node, self)

            node.view = n
            self.scene.addItem(n)
            n.setPos(x, y)
            g.append(n)
        else:
            n = node.view
            rec = True

        startX = (n.x() + n.boundingRect().center().x()) - ((len(node.edges.keys()) / 2) * 250)

        if parent is not None:
            if parent.node.type == 'threat' and n.node.type == 'threat':
                self.scene.addItem(parent.threatConjunction.addArrow(n))
            elif n.node.type == 'countermeasure':
                self.scene.addItem(parent.counterConjunction.addArrow(n))

        it = 0
        threatConj = False
        counterConj = False

        for k, v in node.edges.items():
            if self.tree.nodeList[v.destination].type == 'threat' and n.threatConjunction is None:
                n.threatConjunction = Conjunction(n, v.conjunction)
                self.scene.addItem(n.threatConjunction)
                self.scene.addItem(n.threatConjunction.addParentArrow())
                g.append(n.threatConjunction)
                n.threatConjunction.setPos(n.x() + n.boundingRect().center().x() - 100, n.y() + n.boundingRect().height() + 100)
                threatConj = True
            elif self.tree.nodeList[v.destination].type == 'countermeasure' and n.counterConjunction is None:
                n.counterConjunction = Conjunction(n, v.conjunction)
                self.scene.addItem(n.counterConjunction)
                self.scene.addItem(n.counterConjunction.addParentArrow())
                g.append(n.counterConjunction)
                n.counterConjunction.setPos(n.x() + n.boundingRect().center().x() + 25, n.y() + n.boundingRect().height() + 100)
                counterConj = True

            if threatConj is True:
                conj = n.threatConjunction
            elif counterConj is True:
                conj = n.counterConjunction
            else:
                pass
            #    print('blub')

            if rec is False:
                subG = self.printGraphRecursion(self.tree.nodeList[v.destination], startX + (it * 250), conj.y() + conj.boundingRect().height() + 100, n)
                g.append(subG)
            it += 1

        if threatConj is not counterConj:
            if n.threatConjunction is not None:
                n.threatConjunction.setPos(n.x() + n.boundingRect().x() + 50, n.y() + n.boundingRect().height() + 100)
            if n.counterConjunction is not None:
                n.counterConjunction.setPos(n.x() + n.boundingRect().x() + 50, n.y() + n.boundingRect().height() + 100)

        return g

    def reorderTree(self, g):
        if not isinstance(g, Node):
            left = g[:int(len(g) / 2)]
            right = g[int(len(g) / 2):]

            r = False

            for subG in g:
                if isinstance(subG, Node):
                    i = self.reorderTree(subG)
                    if i is True:
                        r = True

            i = self.fixCollision(left, right)
            if i is True:
                r = True
            return r

    def fixCollision(self, left, right):
        collisions = self.checkCollRec(left, right)

        collision = collisions

        while collisions is True:
            for leftItem in left:
                self.moveRec(leftItem, -125, 0)

            for rightItem in right:
                self.moveRec(rightItem, 125, 0)

            collisions = self.checkCollRec(left, right)

        return collision

    def checkCollRec(self, item, toCheckList):  # @TODO: return parent item of subtree (or true/false)
        if isinstance(item, list):
            for i in item:
                l = self.checkCollRec(i, toCheckList)
                if l is True:
                    return True
        else:
            if isinstance(toCheckList, list):
                for r in toCheckList:
                    l = self.checkCollRec(item, r)
                    if l is True:
                        return True
            else:
                if toCheckList in item.collidingItems():
                    return True
        return False

    def moveRec(self, item, x, y):
        if isinstance(item, list):
            for i in item:
                self.moveRec(i, x, y)
        else:
            item.setPos(item.x() + x, item.y() + y)

    def resizeEvent(self, QResizeEvent):
        self.graphicsView.setMinimumSize(QtCore.QSize(self.width() + 200, self.height() + 200))
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        width = self.scrollArea.frameSize().width() if self.scrollArea.frameSize().width() > self.scene.sceneRect().width() else self.scene.sceneRect().width()
        height = self.scrollArea.frameSize().height() if self.scrollArea.frameSize().height() > self.scene.sceneRect().height() else self.scene.sceneRect().height()

        self.graphicsView.setFixedSize(width + 10, height + 10)

    def loadFile(self):

        if len(self.tree.nodeList) > 0 and self.saved is False:

            msgBox = QMessageBox()
            msgBox.setText("The document has been modified.")
            msgBox.setInformativeText("Do you want to save your changes?")
            msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            msgBox.setDefaultButton(QMessageBox.Save)
            reply = msgBox.exec()

            if reply == QMessageBox.Yes:
                self.saveFile()
            elif reply == QMessageBox.Cancel:
                return

        dialog = QFileDialog()
        fileName = dialog.getOpenFileName(self, 'Open Attack Tree', '', 'attack tree file (*.xml);;All Files (*)')

        if fileName == ('', ''):
            return

        h = Handler()

        self.tree = h.buildFromXML(fileName[0])

        self.scene.clear()

        self.printGraph()
        # For Testing
        self.saved = False

    def saveFile(self):
        if len(self.tree.nodeList) == 0:
            msgBox = QMessageBox()
            msgBox.setText('Saving is not possible')
            msgBox.setInformativeText('Won\'t save an empty tree')
            msgBox.exec()
            return False

        if self.tree.checkCycle() is False:
            msgBox = QMessageBox()
            msgBox.setText('Saving is not possible')
            msgBox.setInformativeText('There is a cycle in the graph at node ID: %s\nTitle: %s' % (self.tree.cycleNode.id, self.tree.cycleNode.title))
            msgBox.exec()
            return False

        if self.tree.checkExtended():
            msgBox = QMessageBox()
            msgBox.setText('Simple Mode not available')
            msgBox.setInformativeText("There is only the extended mode available")
            msgBox.exec()
            fileExt = 'Extended Attack Tree File (*.xml)'
        else:
            fileExt = 'Simple Attack Tree File (*.xml);;Extended Attack Tree File (*.xml)'

        if self.file == ('', ''):
            dialog = QFileDialog()
            self.file = dialog.getSaveFileName(self, 'Save Attack Tree', '', fileExt)  # TODO: check if saving was good
        handler = Handler()

        if self.file == ('', ''):
            return

        if self.file[1] == 'Extended Attack Tree File (*.xml)':
            self.tree.extended = True

        return handler.saveToXML(self.tree, self.file[0])

    def saveFileAs(self):
        file = self.file
        self.file = ('', '')

        if self.saveFile():
            pass

    def exportPNG(self):

        dialog = QFileDialog()
        fileName = dialog.getSaveFileName(self, 'Export as PNG', '', 'PNG (*.png)')

        if fileName != ('', ''):
            try:
                image = QImage(self.scene.sceneRect().size().toSize(), QImage.Format_ARGB32)
                image.fill(Qt.white)
                painter = QPainter(image)
                self.scene.render(painter)
                painter.end()
                image.save(fileName[0])
            except Exception as e:
                print(e)
            return True

    def exportPDF(self):
        dialog = QFileDialog()
        fileName = dialog.getSaveFileName(self, 'Export as PDF', '', 'PDF (*.pdf)')

        if fileName != ('', ''):
            try:
                printer = QPrinter(QPrinter.HighResolution)
                printer.setOutputFormat(QPrinter.PdfFormat)
                printer.setOutputFileName(fileName[0])

                p = QPainter()

                if p.begin(printer) is False:
                    raise Exception('Error starting painter')

                self.scene.setSceneRect(self.scene.itemsBoundingRect())
                self.scene.render(p)
                p.end()
            except Exception as e:
                print(e)
            return True

    def print(self):

        printer = QPrinter(QPrinter.HighResolution)
        printer.setPageSize(QPrinter.A4)
        printer.setOrientation(QPrinter.Portrait)

        printDialog = QPrintDialog(printer, self)
        if printDialog.exec() == QDialog.Accepted:
            p = QPainter()
            if p.begin(printer) is False:
                raise Exception('Error starting painter')
            self.scene.setSceneRect(self.scene.itemsBoundingRect())
            self.scene.render(p)
            p.end()

    def new(self):
        if len(self.tree.nodeList) > 0 and self.saved is False:

            msgBox = QMessageBox()
            msgBox.setText("The document has been modified.")
            msgBox.setInformativeText("Do you want to save your changes?")
            msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            msgBox.setDefaultButton(QMessageBox.Save)
            reply = msgBox.exec()

            if reply == QMessageBox.Yes:
                self.saveFile()
            elif reply == QMessageBox.Cancel:
                return

        self.tree = types.Tree(False)
        self.scene.clear()

    def redrawGraph(self):
        self.scene.clear()
        self.printGraph()

    def newThreat(self):
        self.mode = 1
        self.setCursor(Qt.CrossCursor)

    def newCountermeasure(self):
        self.mode = 2
        self.setCursor(Qt.CrossCursor)

    def newComposition(self):
        self.mode = 3
        self.setCursor(Qt.CrossCursor)


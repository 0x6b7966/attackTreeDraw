import copy
import sys
import traceback

import os
from PyQt5 import QtCore, QtWidgets

from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtWidgets import QMainWindow, QAction, QToolBox, QFileDialog, QMessageBox, QDialog, QGraphicsView, QGraphicsItemGroup
from PyQt5.QtGui import QIcon, QImage, QPainter, QBrush

from data.exceptions import ParserError, XMLXSDError
from .items import Node, Threat, Countermeasure, Conjunction, AttackTreeScene
from .windows import MessageBox, MetaEdit

from data.handler import TreeHandler

from data import types


class Main(QMainWindow):

    def __init__(self):
        super().__init__()

        self.tree = types.Tree(False)
        self.saved = True
        self.file = ('', '')
        self.itemList = []
        self.initUI()

        self.lastAction = []
        self.nextAction = []

        self.mode = 0  # 0: default, 1: add threat, 2: add countermeasure, 3: add composition

    def initUI(self):

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
                '&Undo': ['Ctrl+U', 'Undo Action', self.undo],
                '&Redo': ['Ctrl+Shift+U', 'Redo Action', self.redo],
                'SEPARATOR01': [],

            },
            'Tree': {
                # Name     shortcut   tip          action
                '&Redraw Tree': ['Ctrl++Shift+R', 'Redraw and reorder Tree', self.redrawGraph],
                '&Edit Meta Information': ['', 'Edit Meta Information', self.editMeta],
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
        includePath = os.path.dirname(os.path.abspath(__file__))
        mainToolbarItems = {
            'New': [os.path.join(includePath, 'assets/icons/new.png'), 'Ctrl+N', 'New Tree', self.new],
            'Open': [os.path.join(includePath, 'assets/icons/open.png'), 'Ctrl+O', 'Open Tree', self.loadFile],
            'Save': [os.path.join(includePath, 'assets/icons/save.png'), 'Ctrl+S', 'Save Tree', self.saveFile],
            'Print': [os.path.join(includePath, 'assets/icons/print.png'), 'Ctrl+P', 'Print File', self.print],
            'Undo': [os.path.join(includePath, 'assets/icons/undo.png'), 'Ctrl+U', 'Undo', self.undo],
            'Redo': [os.path.join(includePath, 'assets/icons/redo.png'), 'Ctrl+Shift+U', 'Redo', self.redo],
        }

        editToolbarItems = {
            'Mouse': [os.path.join(includePath, 'assets/icons/mouse.png'), '', 'Use Mouse', self.mouse],
            'New Threat': [os.path.join(includePath, 'assets/icons/threat.png'), '', 'New Threat', self.newThreat],
            'New Counter': [os.path.join(includePath, 'assets/icons/counter.png'), '', 'New Countermeasure', self.newCountermeasure],
            'New Composition': [os.path.join(includePath, 'assets/icons/arrow.png'), '', 'New Composition', self.newComposition],
            'Delete Item': [os.path.join(includePath, 'assets/icons/trash.png'), '', 'Delete selected Items', self.delete],

        }

        self.setObjectName("MainWindow")

        self.resize(814, 581)
        self.setMinimumSize(QtCore.QSize(0, 0))
        self.setWindowTitle("attackTreeDraw")
        self.setWindowIcon(QIcon(os.path.join(includePath, 'assets/icons/logo.png')))
        self.setDocumentMode(True)
        self.setUnifiedTitleAndToolBarOnMac(True)

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

        self.graphicsView = QtWidgets.QGraphicsView(self.centralWidget)
        self.verticalLayout.addWidget(self.graphicsView)

        self.graphicsView.setMinimumSize(QtCore.QSize(self.width(), self.height()))

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

        self.graphicsView.setAlignment(Qt.AlignTop)

        self.graphicsView.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        self.graphicsView.setRenderHint(QPainter.Antialiasing)
        self.graphicsView.setCacheMode(QGraphicsView.CacheBackground)
        self.graphicsView.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        self.graphicsView.setDragMode(QGraphicsView.RubberBandDrag)
        self.graphicsView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.graphicsView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

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

    def printGraph(self):

        for k, n in self.tree.nodeList.items():
            n.initDFS()
            n.view = None

        g = self.printGraphRecursion(self.tree.nodeList[self.tree.root], 0, 10)
        i = 0

        while self.reorderTree(g) is not True and i < 100:
            i += 1

        for k, n in self.tree.nodeList.items():
            if len(n.parents) == 0 and n.visited is False:
                g = self.printGraphRecursion(n, 0, self.scene.itemsBoundingRect().height() + 50)
                i = 0
                while self.reorderTree(g) is not True and i < 100:
                   i += 1

        self.graphicsView.centerOn(0, 0)
        self.graphicsView.viewport().update()

        print('----- DONE -----')

    def printGraphRecursion(self, node, x, y, parent=None):
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
        else:
            n = node.view
            rec = True
        startX = (n.x() + n.boundingRect().center().x()) - ((len(node.edges.keys()) / 2) * 250)

        if parent is not None:
            if parent.node.type == 'threat' and n.node.type == 'threat':
                self.scene.addItem(parent.threatConjunction.addArrow(n))
            elif n.node.type == 'countermeasure':
                self.scene.addItem(parent.counterConjunction.addArrow(n))

        node.visited = True

        threatConj = False
        counterConj = False

        children = []
        threatConjChildren = []
        counterConjChildren = []

        it = 0
        for k, v in node.edges.items():
            if self.tree.nodeList[v.destination].type == 'threat':
                if n.threatConjunction is None:
                    if node.type == 'threat':
                        n.threatConjunction = Conjunction(n, v.conjunction, -50)
                    else:
                        n.threatConjunction = Conjunction(n, v.conjunction)
                    self.scene.addItem(n.threatConjunction)
                    self.scene.addItem(n.threatConjunction.addParentArrow())
                    n.threatConjunction.setPos(n.x() + n.boundingRect().center().x() - 100, n.y() + n.boundingRect().height() + 100)
                    threatConj = True
                if rec is False:
                    subG = self.printGraphRecursion(self.tree.nodeList[v.destination], startX + (it * 250), n.threatConjunction.y() + n.threatConjunction.boundingRect().height() + 100, n)
                    threatConjChildren.append(subG)
                it += 1

        if threatConj is True:
            children.append((n.threatConjunction, threatConjChildren))

        for k, v in node.edges.items():
            if self.tree.nodeList[v.destination].type == 'countermeasure':
                if n.counterConjunction is None:
                    if node.type == 'threat':
                        n.counterConjunction = Conjunction(n, v.conjunction, 50)
                    else:
                        n.counterConjunction = Conjunction(n, v.conjunction)
                    self.scene.addItem(n.counterConjunction)
                    self.scene.addItem(n.counterConjunction.addParentArrow())
                    n.counterConjunction.setPos(n.x() + n.boundingRect().center().x() + 25, n.y() + n.boundingRect().height() + 100)
                    counterConj = True
                if rec is False:
                    subG = self.printGraphRecursion(self.tree.nodeList[v.destination], startX + (it * 250), n.counterConjunction.y() + n.counterConjunction.boundingRect().height() + 100, n)
                    counterConjChildren.append(subG)
                it += 1

        if counterConj is True:
            children.append((n.counterConjunction, counterConjChildren))

        if threatConj is not counterConj:
            if n.threatConjunction is not None:
                n.threatConjunction.setPos(n.x() + n.boundingRect().x() + 50, n.y() + n.boundingRect().height() + 100)
            if n.counterConjunction is not None:
                n.counterConjunction.setPos(n.x() + n.boundingRect().x() + 50, n.y() + n.boundingRect().height() + 100)

        return n, children

    def reorderTree(self, g):
        r = False
        for subG in g[1]:
            i = self.reorderTree(subG)
            if i is True:
                r = True

        if len(g[1]) == 2:
            i = self.fixCollision(g[1][0], g[1][1])
            if i is True:
                r = True
        return r

    def fixCollision(self, l, r):
        left = []
        right = []

        self.makeList(l, left)
        self.makeList(r, right)

        collisions = self.checkCollRec(left, right)
        collision = collisions

        while collisions is True:
            for leftItem in list(set(left)):
                self.moveRec(leftItem, -125, 0)
            for rightItem in list(set(right)):
                self.moveRec(rightItem, 125, 0)
            collisions = self.checkCollRec(left, right)

        return collision

    def makeList(self, item, itemList):
        itemList.append(item[0])
        for i in item[1]:
            self.makeList(i, itemList)

    def checkCollRec(self, item, toCheckList):
        if isinstance(item, list):
            for i in item:
                if self.checkCollRec(i, toCheckList) is True:
                    return True
        else:
            if isinstance(toCheckList, list):
                for r in toCheckList:
                    if self.checkCollRec(item, r) is True:
                        return True
            else:
                if toCheckList in item.collidingItems(): # and isinstance(toCheckList):
                    return True
        return False

    def moveRec(self, item, x, y):
        if isinstance(item, list):
            for i in item:
                self.moveRec(i, x, y)
        else:
            item.setPos(item.x() + x, item.y() + y)

    def resizeEvent(self, QResizeEvent):
        pass

    def loadFile(self):
        if len(self.tree.nodeList) > 0 and self.saved is False:

            reply = MessageBox('The document has been modified', 'Do you want to save your changes?', QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Warning, QMessageBox.Save).run()

            if reply == QMessageBox.Yes:
                self.saveFile()
            elif reply == QMessageBox.Cancel:
                return

        dialog = QFileDialog()
        fileName = dialog.getOpenFileName(self, 'Open Attack Tree', '', 'attack tree file (*.xml);;All Files (*)')

        if fileName == ('', ''):
            return
        try:
            h = TreeHandler()
            self.tree = h.buildFromXML(fileName[0])
        except ParserError:
            MessageBox('Loading is not possible', 'The requested file is not compatible', icon=QMessageBox.Critical).run()
        except XMLXSDError as e:
            MessageBox('Loading is not possible', '%s' % e, icon=QMessageBox.Critical).run()
        finally:
            self.scene.clear()
            self.printGraph()

    def saveFile(self):
        if len(self.tree.nodeList) == 0:
            MessageBox('Saving is not possible', 'Won\'t save an empty tree!', icon=QMessageBox.Critical).run()
            return False

        if self.tree.checkMeta() is False:
            edit = MetaEdit(self)
            edit.exec()
            if self.tree.checkMeta() is False:
                return False

        if self.tree.checkCycle() is False:
            MessageBox('Saving is not possible', 'There is a cycle in the graph at node ID: %s\nTitle: %s' % (self.tree.cycleNode.id, self.tree.cycleNode.title), icon=QMessageBox.Critical).run()
            return False

        if self.tree.checkNodes() is False:
            MessageBox('Saving is not possible', 'The title is missing at node ID:\n %s' % ', '.join(self.tree.falseNodes), icon=QMessageBox.Critical).run()
            return False

        if self.tree.checkExtended():
            MessageBox('Simple Mode not available', 'There is only the extended mode available.', icon=QMessageBox.Information).run()
            fileExt = 'Extended Attack Tree File (*.xml)'
        else:
            fileExt = 'Simple Attack Tree File (*.xml);;Extended Attack Tree File (*.xml)'

        if self.file == ('', ''):
            dialog = QFileDialog()
            self.file = dialog.getSaveFileName(self, 'Save Attack Tree', '', fileExt)  # TODO: check if saving was good
        handler = TreeHandler()

        if self.file == ('', ''):
            return False

        if self.file[1] == 'Extended Attack Tree File (*.xml)':
            self.tree.extended = True

        save = handler.saveToXML(self.tree, self.file[0])
        if save is not True:
            MessageBox('Error while saving file', 'There was an error saving the tree.\nError Message: %s' % save, icon=QMessageBox.Information).run()
            return False
        return True

    def saveFileAs(self):
        # @TODO: reset file if save as failed
        file = self.file
        self.file = ('', '')
        if self.saveFile() is False:
            self.file = file

    def exportPNG(self):
        dialog = QFileDialog()
        fileName = dialog.getSaveFileName(self, 'Export as PNG', '', 'PNG (*.png)')

        if fileName != ('', ''):  # @TODO; Error handling
            self.scene.setSceneRect(self.scene.itemsBoundingRect())
            image = QImage(self.scene.sceneRect().size().toSize(), QImage.Format_ARGB32)
            image.fill(Qt.white)
            painter = QPainter(image)
            self.scene.render(painter)
            self.scene.setSceneRect(QRectF())
            image.save(fileName[0])
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
                self.scene.setSceneRect(QRectF())
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
            self.scene.setSceneRect(None)

    def new(self):
        if len(self.tree.nodeList) > 0 and self.saved is False:
            reply = MessageBox('The document has been modified', 'Do you want to save your changes?', QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Warning, QMessageBox.Save).run()
            if reply == QMessageBox.Yes:
                self.saveFile()
            elif reply == QMessageBox.Cancel:
                return

        self.tree = types.Tree(False)

        self.scene.clear()

        self.graphicsView.centerOn(0, 0)

        # print(self.scene.itemsBoundingRect())
        self.graphicsView.setSceneRect(self.scene.itemsBoundingRect())

        # print(self.scene.sceneRect())
        self.graphicsView.viewport().update()

    def redrawGraph(self):
        if self.tree.checkMeta() is False:
            edit = MetaEdit(self)
            edit.exec()
            if self.tree.checkMeta() is False:
                return
        self.scene.clear()
        self.printGraph()

    def mouse(self):
        self.mode = 0
        self.setCursor(Qt.ArrowCursor)
        self.graphicsView.setDragMode(QGraphicsView.RubberBandDrag)

    def newThreat(self):
        self.mode = 1
        self.setCursor(Qt.CrossCursor)

    def newCountermeasure(self):
        self.mode = 2
        self.setCursor(Qt.CrossCursor)

    def newComposition(self):
        self.mode = 3
        self.setCursor(Qt.CrossCursor)
        self.graphicsView.setDragMode(QGraphicsView.NoDrag)

    def delete(self):
        self.mode = 4
        self.setCursor(Qt.CrossCursor)

    def editMeta(self):
        edit = MetaEdit(self)
        edit.exec()

    def undo(self):
        if len(self.lastAction) > 0:
            tree = self.lastAction.pop()
            self.nextAction.append(copy.deepcopy(self.tree))
            self.tree = copy.copy(tree)

            if self.tree.root is None and len(self.tree.nodeList) != 0:
                self.tree.root = list(self.tree.nodeList.keys())[0]
                self.tree.nodeList[self.tree.root].isRoot = True
                self.scene.clear()
                self.printGraph()
            else:
                self.scene.clear()

    def redo(self):
        if len(self.nextAction) > 0:
            tree = self.nextAction.pop()
            self.lastAction.append(copy.deepcopy(self.tree))
            self.tree = copy.copy(tree)

            if self.tree.root is None and len(self.tree.nodeList) != 0:
                self.tree.root = list(self.tree.nodeList.keys())[0]
                self.tree.nodeList[self.tree.root].isRoot = True
                self.scene.clear()
                self.printGraph()
            else:
                self.scene.clear()

    def addLastAction(self):
        self.lastAction.append(copy.deepcopy(self.tree))

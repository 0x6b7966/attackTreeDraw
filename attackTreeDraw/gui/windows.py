import sys

from PyQt5 import QtCore, QtGui, QtWidgets

from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QApplication, QToolBox, QGraphicsScene, QGraphicsItem, \
    QGraphicsItemGroup
from PyQt5.QtGui import QIcon

from .items import Node, Arrow, Threat, Countermeasure


class Main(QMainWindow):

    def __init__(self, tree):
        super().__init__()

        self.tree = tree

        self.itemList = []

        self.initUI()

        # For testing
        self.printGraph()

    def initUI(self):

        # from PyQt5 import uic
        # uic.loadUi('../../attackTreeDrawQt/self.ui', self)
        # self.setWindowTitle('attackTreeDraw')
        # self.show()

        # return

        self.setObjectName("MainWindow")

        self.resize(814, 581)
        self.setMinimumSize(QtCore.QSize(0, 0))
        self.setWindowTitle("attackTreeDraw")
        self.setDocumentMode(True)
        self.centralWidget = QtWidgets.QWidget(self)
        self.centralWidget.setObjectName("centralWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)

        self.verticalLayout.setObjectName("verticalLayout")
        self.scrollArea = QtWidgets.QScrollArea(self.centralWidget)
        self.scrollArea.setEnabled(True)
        self.scrollArea.setStatusTip("")
        self.scrollArea.setAccessibleName("")
        self.scrollArea.setLineWidth(0)
        self.scrollArea.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        # self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 1032, 1024))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.formLayout = QtWidgets.QFormLayout(self.scrollAreaWidgetContents)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setSpacing(0)
        self.formLayout.setObjectName("formLayout")
        self.graphicsView = QtWidgets.QGraphicsView(self.scrollAreaWidgetContents)

        self.graphicsView.setMinimumSize(QtCore.QSize(self.width(), self.width()))
        self.graphicsView.setSizeIncrement(QtCore.QSize(0, 0))
        self.graphicsView.setBaseSize(QtCore.QSize(0, 0))
        self.graphicsView.setObjectName("graphicsView")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.graphicsView)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)
        self.setCentralWidget(self.centralWidget)
        self.statusBar = QtWidgets.QStatusBar(self)
        self.statusBar.setObjectName("statusBar")
        self.setStatusBar(self.statusBar)

        menuBarItems = {
            'File': {
                # Name     shortcut   tip          action
                '&New': ['Ctrl+N', 'New Tree', self.close],
                '&Open': ['Ctrl+O', 'Open File', self.close],
                '&Save': ['Ctrl+S', 'Print Tree', self.close],
                'Save &As ...': ['Ctrl+Shift+S', 'Print Tree', self.close],
                'SEPARATOR01': [],
                '&Close Tree': ['Ctrl+W', 'Open File', self.close],
                '&Print': ['Ctrl+P', 'Print Tree', self.close],
                '&Exit': ['Ctrl+Q', 'Print Tree', self.close],

            },
            'Edit': {
                # Name     shortcut   tip          action
                '&Undo': ['Ctrl+U', 'Undo Action', self.close],
                '&Redo': ['Ctrl+Shift+U', 'Redo Action', self.close],
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
            'New': ['gui/assets/icons/new.png', 'Ctrl+N', 'New Tree', self.close],
            'Open': ['gui/assets/icons/open.png', 'Ctrl+O', 'Open Tree', self.close],
            'Save': ['gui/assets/icons/save.png', 'Ctrl+S', 'Save Tree', self.close],
            'Print': ['gui/assets/icons/print.png', 'Ctrl+P', 'Print File', self.close],
            'Undo': ['gui/assets/icons/undo.png', 'Ctrl+U', 'Undo', self.close],
            'Redo': ['gui/assets/icons/redo.png', 'Ctrl+Shift+U', 'Redo', self.close],

        }

        menubar = QtWidgets.QMenuBar(self)
        for k, v in menuBarItems.items():
            menuItem = menubar.addMenu(k)
            for ks, s in v.items():
                if ks.startswith('SEPARATOR'):
                    menuItem.addSeparator()
                else:
                    action = QAction(ks, self)
                    action.setShortcut(s[0])
                    action.setStatusTip(s[1])
                    action.triggered.connect(s[2])
                    menuItem.addAction(action)

        mainToolBar = QtWidgets.QToolBar(self)
        self.addToolBar(QtCore.Qt.TopToolBarArea, mainToolBar)
        for k, v in mainToolbarItems.items():
            action = QAction(QIcon(v[0]), k, self)
            action.setShortcut(v[2])
            action.setStatusTip(v[2])
            action.triggered.connect(self.close)

            mainToolBar.addAction(action)

        self.scene = QGraphicsScene(self)

        self.graphicsView.setScene(self.scene)

        # self.graphicsView.mapToScene(0, 0)

        self.scene.setSceneRect(self.scene.itemsBoundingRect())

        self.graphicsView.setAlignment(Qt.AlignTop)

        workToolbar = self.addToolBar('WorkToolbar')
        toolbox = QToolBox()
        # toolbox.add
        workToolbar.setOrientation(Qt.Vertical)
        self.addToolBar(Qt.LeftToolBarArea, workToolbar)

        workToolbar.addWidget(toolbox)

        self.show()

    def printGraph(self):

        g = self.printGraphRecursion(self.tree.nodeList[self.tree.root], 0, 10)

        while self.reorderTree(g) is not True:
            pass

        self.scene.setSceneRect(QRectF(self.scene.itemsBoundingRect().x() - 100, 0, self.scene.itemsBoundingRect().width() + 200, self.scene.itemsBoundingRect().height() + 100))
        print('----- DONE -----')

    def printGraphRecursion(self, node, x, y, parent=None):

        if node.type == 'threat':
            n = Threat(node)
        elif node.type == 'countermeasure':
            n = Countermeasure(node)
        else:
            n = Node(node)

        g = []
        self.scene.addItem(n)

        n.setPos(x, y)

        startX = (n.x() + n.boundingRect().center().x()) - ((len(node.edges.keys()) / 2) * 250)

        g.append(n)

        if parent is not None:
            a = Arrow(parent, n)
            self.scene.addItem(a)

        it = 0
        for k, v in node.edges.items():
            subG = self.printGraphRecursion(self.tree.nodeList[v.destination], startX + (it * 250), n.y() + n.boundingRect().height() + 100, n)
            g.append(subG)
            it += 1
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

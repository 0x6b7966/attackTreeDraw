import copy
import functools
import platform
import traceback

import os

import sys
from PyQt5 import QtCore, QtWidgets

from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtWidgets import QMainWindow, QAction, QToolBox, QFileDialog, QMessageBox, QDialog, QGraphicsView, \
    QProgressDialog
from PyQt5.QtGui import QIcon, QImage, QPainter, QFontDatabase, QFont, QPageSize, QKeySequence

from data.exceptions import ParserError, XMLXSDError
from gui.helper import Configuration
from .items import Node, Threat, Countermeasure, Conjunction, AttackTreeScene
from .windows import MessageBox, MetaEdit, Options

from data.handler import TreeHandler

from data import types


class Main(QMainWindow):
    """
    This Class is the main window for attackTreeDraw.
    It sets up the window and handles the GraphicsView for the Tree
    """

    def __init__(self):
        """
        Constructor for the Main window.
        Initializes all needed variables and calls the init function
        """
        super().__init__()

        self.tree = types.Tree(False)
        self.saved = True
        self.file = ('', '')
        self.itemList = []
        self.modeAction = None
        self.defaultModeAction = None
        self.modeActions = {}
        self.progress = None

        self.lastAction = []
        self.nextAction = []

        self.copyBuffer = []

        """
        0: default
        1: add threat
        2: add countermeasure
        3: add conjunction
        4: new edge
        5: delete item
        6: paste item
        """
        self.mode = 0
        """
        Sets the hook to print unhandled exceptions in the GUI
        """
        sys.excepthook = self.exceptionHook

        self.initUI()

    def initUI(self):
        """
        Initialisation of the UI.
        Sets up all menus and  toolbars
        Registers function for buttons
        """
        menuBarItems = {
            'File': {
                # Name     shortcut   tip          action
                '&New': [QKeySequence.New, 'New Tree', self.new],
                '&Open': [QKeySequence.Open, 'Open File', self.loadFile],
                '&Save': [QKeySequence.Save, 'Print Tree', self.saveFile],
                'Save &As ...': [QKeySequence.SaveAs, 'Print Tree', self.saveFileAs],
                'SEPARATOR01': [],
                'Export as P&DF': ['Ctrl+Shift+E', 'Export Tree', self.exportPDF],
                'Export as PN&G': ['Ctrl+Shift+Alt+E', 'Export Tree', self.exportPNG],
                'SEPARATOR02': [],
                'Op&tions': [QKeySequence.Preferences, 'Options', self.options],
                'SEPARATOR03': [],
                '&Print': [QKeySequence.Print, 'Print Tree', self.print],
                '&Close Tree': [QKeySequence.Close, 'Open File', self.new],
                '&Exit': [QKeySequence.Quit, 'Print Tree', self.close],

            },
            'Edit': {
                # Name     shortcut   tip          action
                '&Undo': [QKeySequence.Undo, 'Undo Action', self.undo],
                '&Redo': [QKeySequence.Redo, 'Redo Action', self.redo],
                'SEPARATOR01': [],
                '&Copy': [QKeySequence.Copy, 'Copy Selection', self.copy],
                'Cu&t': [QKeySequence.Cut, 'Cut Selection', self.cut],
                '&Paste': [QKeySequence.Paste, 'Pate Selection', self.paste],

            },
            'Tree': {
                # Name     shortcut   tip          action
                '&Reload Tree': [QKeySequence.Refresh, 'Reload the Tree', self.refreshGraph],
                '&Reformat Tree': ['Ctrl+Shift+R', 'Redraw and reorder Tree', self.redrawGraph],
                '&Generate Simple Tree': ['', 'Generate Simple Tree', self.generateSimple],
                '&Edit Meta Information': ['', 'Edit Meta Information', self.editMeta],
                'SEPARATOR01': [],
                'Zoom &In': [QKeySequence.ZoomIn, 'Zoom in', self.zoomIn],
                'Zoom &Out': [QKeySequence.ZoomOut, 'Zoom out', self.zoomOut],

            },
            'About': {
                # Name     shortcut   tip          action
                '&Help': ['', 'Help', self.help],
                '&About': ['', 'About', self.about],
            },
        }
        includePath = os.path.dirname(os.path.abspath(__file__))
        mainToolbarItems = {
            """
            Here are no shortcuts set, because they are already in the menu declared.
            If they would have been set there would be an conflict.
            
            Name     icon                                                  shortcut   tip           action
            """
            'New': [os.path.join(includePath, 'assets/icons/new.png'), '', 'New Tree', self.new],
            'Open': [os.path.join(includePath, 'assets/icons/open.png'), '', 'Open Tree', self.loadFile],
            'Save': [os.path.join(includePath, 'assets/icons/save.png'), '', 'Save Tree', self.saveFile],
            'Print': [os.path.join(includePath, 'assets/icons/print.png'), '', 'Print File', self.print],
            'Undo': [os.path.join(includePath, 'assets/icons/undo.png'), '', 'Undo', self.undo],
            'Redo': [os.path.join(includePath, 'assets/icons/redo.png'), '', 'Redo', self.redo],
        }

        editToolbarItems = {
            'Mouse': [os.path.join(includePath, 'assets/icons/mouse.png'), 'M', 'Use Mouse (M)', self.mouse, True,
                      None],
            'New Threat': [os.path.join(includePath, 'assets/icons/threat.png'), 'T', 'New Threat (T)', self.newThreat,
                           False, None],
            'New Counter': [os.path.join(includePath, 'assets/icons/counter.png'), 'C', 'New Countermeasure (C)',
                            self.newCountermeasure, False, None],
            'New Conjunction': [os.path.join(includePath, 'assets/icons/conjunction.png'), 'J', 'New Conjunction (J)',
                                self.newConjunction, False, None],
            'New Edge': [os.path.join(includePath, 'assets/icons/arrow.png'), 'E', 'New Edge (E)', self.newEdge, False,
                         None],
            'Delete Item': [os.path.join(includePath, 'assets/icons/trash.png'), 'D', 'Delete selected Items (D)',
                            self.delete, False, None],
            'Paste Items': [os.path.join(includePath, 'assets/icons/paste.png'), '', 'Paste Items', self.paste, False,
                            'pasteAction'],

        }

        QFontDatabase.addApplicationFont(os.path.join(includePath, 'assets/fonts/RobotoMono-Regular.ttf'))
        if Configuration.font is None:
            if platform.system() == 'Windows':
                Configuration.font = QFont('Roboto Mono', 10)
            elif platform.system() == 'Linux':
                Configuration.font = QFont('Roboto Mono', 8)
            else:
                Configuration.font = QFont('Roboto Mono', 12)
        Configuration.loadConfigFile()

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
        """
        Generate toolbar from list
        """
        for k, v in mainToolbarItems.items():
            action = QAction(QIcon(v[0]), k, self)
            action.setShortcut(v[1])
            action.setStatusTip(v[2])
            action.triggered.connect(v[3])

            mainToolBar.addAction(action)

        self.scene = AttackTreeScene(self)

        self.graphicsView.setScene(self.scene)

        self.graphicsView.setAlignment(Qt.AlignTop)

        """
        These are options for smother rendering
        """
        self.graphicsView.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        self.graphicsView.setRenderHint(QPainter.Antialiasing)
        self.graphicsView.setRenderHint(QPainter.SmoothPixmapTransform)
        self.graphicsView.setCacheMode(QGraphicsView.CacheBackground)
        """
        This option allows the drag and drop of the nodes
        """
        self.graphicsView.setDragMode(QGraphicsView.RubberBandDrag)
        """
        Display always the scroll bars
        """
        self.graphicsView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.graphicsView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        workToolbar = self.addToolBar('WorkToolbar')
        toolbox = QToolBox()
        workToolbar.setOrientation(Qt.Vertical)
        self.addToolBar(Qt.LeftToolBarArea, workToolbar)

        """
        Generate toolbar from list
        """
        for k, v in editToolbarItems.items():
            action = QAction(QIcon(v[0]), k, self)
            action.setShortcut(v[1])
            action.setStatusTip(v[2])
            action.triggered.connect(functools.partial(v[3], action))

            action.setCheckable(True)

            """
            Set the default action for the modes
            """
            if v[4] is True:
                self.defaultModeAction = action
                self.modeAction = action
                action.setChecked(True)
            if v[5] is not None:
                self.modeActions[v[5]] = action

            workToolbar.addAction(action)

        workToolbar.addWidget(toolbox)

        self.show()

    def printGraph(self, fixedPositions=False, doReorderTree=True):
        """
        Prints the attack tree onto the graphics view
        after the full graph was printed it will be reordered to have a nice graph
        :param fixedPositions: prints the node at a fixed position
        :param doReorderTree:
        """
        for k, n in self.tree.nodeList.items():
            n.initDFS()
            n.view = None

        self.graphicsView.setScene(None)

        """
        Prints the reorder dialog
        """
        if doReorderTree is True:
            self.progress = QProgressDialog("Reordering tree...", "Abort Reorder", 0, 2 ** 10, self)
            self.progress.setWindowModality(Qt.WindowModal)

        """
        Prints all nodes connected to the root node
        """
        if self.tree.root is not None:
            g = self.printGraphRecursion(self.tree.nodeList[self.tree.root], 0, 10, fixedPositions=fixedPositions)
            if doReorderTree is True and self.progress.wasCanceled() is False:
                i = 0
                while fixedPositions is False and self.reorderTree(g) is not True and i < 20:
                    i += 1
        """
        Prints all nodes w/o a parent node
        """
        for k, n in self.tree.nodeList.items():
            if n.visited is False and len(n.parents) == 0:
                g = self.printGraphRecursion(n, 0, self.scene.itemsBoundingRect().height() + 50,
                                             fixedPositions=fixedPositions)
                if doReorderTree is True and self.progress.wasCanceled() is False:
                    i = 0
                    while fixedPositions is False and self.reorderTree(g) is not True and i < 20:
                        i += 1
        """
        Prints the rest
        """
        for k, n in self.tree.nodeList.items():
            if n.visited is False:
                g = self.printGraphRecursion(n, 0, self.scene.itemsBoundingRect().height() + 50,
                                             fixedPositions=fixedPositions)
                if doReorderTree is True and self.progress.wasCanceled() is False:
                    i = 0
                    while fixedPositions is False and self.reorderTree(g) is not True and i < 20:
                        i += 1

        for k, n in self.tree.nodeList.items():
            n.view = None

        if fixedPositions is not True:
            self.graphicsView.centerOn(0, 0)
        if doReorderTree is True:
            self.progress.setValue(2 ** 10)
        self.graphicsView.setScene(self.scene)
        self.graphicsView.viewport().update()

    def printGraphRecursion(self, node, x, y, parent=None, fixedPositions=False):
        """
        Prints a node recursively with its child nodes
        returns a tuple in the style of:
        (node, ([left_half_of_children], [right_half_of_children])

        :param fixedPositions: prints the node at a fixed position
        :param node: data node to print
        :param x: x position of the node
        :param y: y position of the mode
        :param parent: parent node
        """
        rec = False

        if node.view is None:
            """
            Generates a graphical object for the node
            """
            if fixedPositions is True and node.position is not None:
                x = node.position[0]
                y = node.position[1]
            if isinstance(node, types.Threat):
                n = Threat(node, self, x, y)
            elif isinstance(node, types.Countermeasure):
                n = Countermeasure(node, self, x, y)
            else:
                n = Conjunction(node, self, x, y)

            node.view = n
            self.scene.addItem(n)
        else:
            n = node.view
            rec = True
        startX = (n.x() + n.boundingRect().center().x()) - ((len(node.children) / 2) * 250)

        if parent is not None:
            parent.addEdge(n)

        node.visited = True
        children = []
        it = 0
        for c in node.children:
            if rec is False:
                """
                Calls the children recursively if they are not already drawn
                """
                subG = self.printGraphRecursion(self.tree.nodeList[c], startX + (it * 250),
                                                n.y() + n.boundingRect().height() + 100, n,
                                                fixedPositions=fixedPositions)
                children.append(subG)
            it += 1

        n.actualizeEdges()
        left = []
        right = []
        sortedChildren = n.getLeftRightChildren()

        for c in children:
            if c[0] in sortedChildren[0]:
                left.append(c)
            else:
                right.append(c)

        return n, (left, right)

    def reorderTree(self, g):
        """
        Reoders the tree recursively.
        The function splits the tree into two parts when it's possible

        :param g: Part of the graph
        :return: True if no collisions where found
        """
        r = False

        self.progress.setValue(self.progress.value() + 1)
        if self.progress.wasCanceled():
            return False

        for subG in g[1][0]:
            i = self.reorderTree(subG)
            if i is True:
                r = True
        for subG in g[1][1]:
            i = self.reorderTree(subG)
            if i is True:
                r = True

        i = self.fixCollision(g[1][0], g[1][1])
        if i is True:
            r = True

        if self.progress.wasCanceled():
            return False

        return r

    def fixCollision(self, left, right):
        """
        Checks if there is a collision between l and r
        If there is one both parts will be moved to the left or right side

        :param left: left part of the subtree
        :param right: right part of the subtree
        :return: True if there was an collision
        """
        collisions = self.checkCollRec(left, right)
        collision = collisions

        while collisions is True:
            if self.progress.wasCanceled():
                return False
            for leftItem in left:
                self.moveRec(leftItem, -125, 0)
            for rightItem in right:
                self.moveRec(rightItem, 125, 0)
            collisions = self.checkCollRec(left, right)
            self.progress.setValue(self.progress.value() + 1)
        return collision

    def checkCollRec(self, item, toCheckList):
        """
        Checks recursively if there is a collision between an item or a list of times and a list of times

        :param item: item or list to check for collisions
        :param toCheckList: list to check the collision with item
        :return: True if there is a collision
        """
        if self.progress.wasCanceled():
            return False
        if isinstance(item, list):
            for i in item:
                if self.checkCollRec(i[0], toCheckList) is True:
                    return True
                if self.checkCollRec(i[1][0], toCheckList) is True:
                    return True
                if self.checkCollRec(i[1][1], toCheckList) is True:
                    return True
        else:
            if len(item.collidingItems()) == 0:
                return False
            if isinstance(toCheckList, list):
                for r in toCheckList:
                    if self.checkCollRec(item, r[0]) is True:
                        return True
                    if self.checkCollRec(item, r[1][0]) is True:
                        return True
                    if self.checkCollRec(item, r[1][1]) is True:
                        return True
            else:
                if toCheckList in item.collidingItems():
                    return True
        return False

    def moveRec(self, item, x, y):
        """
        Moves an item or a list of items by (x,y)

        :param item: item or list of item in graphicsScene
        :param x: x-offset to move
        :param y: y-offset to move
        """
        if self.progress.wasCanceled():
            return False
        if isinstance(item, list):
            for i in item:
                self.moveRec(i, x, y)
        else:
            item[0].setPos(item[0].x() + x, item[0].y() + y)
            self.moveRec(item[1][0], x, y)
            self.moveRec(item[1][1], x, y)

    def loadFile(self):
        """
        Opens a dialog to load a file.
        Also checks if the file is compatible and tries to load it
        """
        self.mouse()
        if len(self.tree.nodeList) > 0 and self.saved is False:

            reply = MessageBox('The document has been modified', 'Do you want to save your changes?',
                               QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Warning,
                               QMessageBox.Save).run()

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
        except ParserError as e:
            MessageBox('Loading is not possible', 'The requested file is not compatible',
                       icon=QMessageBox.Critical).run()
            return
        except XMLXSDError as e:
            MessageBox('Loading is not possible', '%s' % e, icon=QMessageBox.Critical).run()
            print(traceback.format_exc())
            return
        except Exception:
            print(traceback.format_exc())
            return
        try:
            self.file = fileName
            self.scene.clear()
            self.scene.setSceneRect(self.scene.itemsBoundingRect())
            self.printGraph(doReorderTree=False)
            self.scene.setSceneRect(QRectF(None))
            self.graphicsView.setScene(self.scene)
            self.graphicsView.update()
        except Exception:
            print(traceback.format_exc())

    def saveFile(self):
        """
        Opens a dialog to save the tree.
        It checks if all information are correct
        and does a check for an cycle
        :return: True if saving was successful
        """
        self.mouse()
        if len(self.tree.nodeList) == 0:
            MessageBox('Saving is not possible', 'Won\'t save an empty tree!', icon=QMessageBox.Critical).run()
            return False

        if self.tree.checkMeta() is False:
            edit = MetaEdit(self)
            edit.exec()
            if self.tree.checkMeta() is False:
                return False

        if self.tree.checkCycle() is False:
            MessageBox('Saving is not possible', 'There is a cycle in the graph at node ID: %s\nTitle: %s' % (
                self.tree.cycleNode.id, self.tree.cycleNode.title), icon=QMessageBox.Critical).run()
            return False

        if self.tree.checkNodes() is False:
            MessageBox('Saving is not possible',
                       'The title is missing at node ID:\n %s' % ', '.join(self.tree.falseNodes),
                       icon=QMessageBox.Critical).run()
            return False

        if self.tree.checkExtended():
            MessageBox('Simple Mode not available', 'There is only the extended mode available.',
                       icon=QMessageBox.Information).run()
            fileExt = 'Extended Attack Tree File (*.xml)'
        else:
            fileExt = 'Simple Attack Tree File (*.xml);;Extended Attack Tree File (*.xml)'

        if self.file == ('', ''):
            dialog = QFileDialog()
            self.file = dialog.getSaveFileName(self, 'Save Attack Tree', '', fileExt)
        handler = TreeHandler()

        if self.file == ('', ''):
            return False

        if self.file[1] == 'Extended Attack Tree File (*.xml)':
            self.tree.extended = True

        save = handler.saveToXML(self.tree, self.file[0])
        if save is not True:
            MessageBox('Error while saving file', 'There was an error saving the tree.\nError Message: %s' % save,
                       icon=QMessageBox.Information).run()
            return False
        self.saved = True
        return True

    def saveFileAs(self):
        """
        Opens a dialog to save the tree to a specific file
        """
        self.mouse()
        file = self.file
        self.file = ('', '')
        if self.saveFile() is False:
            self.file = file

    def exportPNG(self):
        """
        Opens a dialog to export the tree as png.
        Saves the tree to the declared location

        :return: True if saving was successful
        """
        self.mouse()
        dialog = QFileDialog()
        fileName = dialog.getSaveFileName(self, 'Export as PNG', '', 'PNG (*.png)')

        if fileName != ('', ''):
            self.scene.clearSelection()
            self.scene.setSceneRect(self.scene.itemsBoundingRect())
            self.graphicsView.setScene(self.scene)
            self.graphicsView.update()
            image = QImage(self.scene.sceneRect().size().toSize(), QImage.Format_ARGB32)
            image.fill(Qt.white)
            painter = QPainter(image)
            self.scene.render(painter)
            self.scene.setSceneRect(QRectF())
            image.save(fileName[0])
            painter.end()
            return True
        return False

    def exportPDF(self):
        """
        Opens a dialog to export the tree as pdf.
        Saves the tree to the declared location

        :return: True if saving was successful
        """
        self.mouse()
        dialog = QFileDialog()
        fileName = dialog.getSaveFileName(self, 'Export as PDF', '', 'PDF (*.pdf)')
        if fileName != ('', ''):
            self.scene.clearSelection()
            try:
                printer = QPrinter(QPrinter.HighResolution)
                printer.setOutputFormat(QPrinter.PdfFormat)
                printer.setPageSize(QPageSize(self.scene.itemsBoundingRect().size(), QPageSize.Point))
                printer.setOutputFileName(fileName[0])

                p = QPainter()

                if p.begin(printer) is False:
                    raise Exception('Error starting painter')

                self.scene.setSceneRect(self.scene.itemsBoundingRect())
                self.graphicsView.setScene(self.scene)
                self.graphicsView.update()

                self.scene.render(p)
                p.end()
                self.scene.setSceneRect(QRectF(None))
            except Exception as e:
                MessageBox('Error while saving to pdf', str(e))
                return False
            return True
        return False

    def print(self):
        """
        Opens an printing dialog
        """
        self.mouse()
        printer = QPrinter(QPrinter.HighResolution)
        printer.setPageSize(QPrinter.A4)
        printer.setOrientation(QPrinter.Portrait)
        self.scene.clearSelection()
        printDialog = QPrintDialog(printer, self)
        if printDialog.exec() == QDialog.Accepted:
            try:
                p = QPainter()
                if p.begin(printer) is False:
                    raise Exception('Error starting painter')
                self.scene.setSceneRect(self.scene.itemsBoundingRect())
                self.scene.render(p)
                p.end()
                self.scene.setSceneRect(QRectF(None))
            except Exception as e:
                MessageBox('Error while printing', e)

    def new(self):
        """
        Resets the Scene
        """
        self.mouse()
        if len(self.tree.nodeList) > 0 and self.saved is False:
            reply = MessageBox('The document has been modified', 'Do you want to save your changes?',
                               QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Warning,
                               QMessageBox.Save).run()
            if reply == QMessageBox.Yes:
                self.saveFile()
            elif reply == QMessageBox.Cancel:
                return
        self.tree = types.Tree(False)
        self.scene.clear()
        self.graphicsView.centerOn(0, 0)
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.graphicsView.setScene(self.scene)
        self.graphicsView.update()
        self.graphicsView.viewport().update()
        self.scene.setSceneRect(QRectF())

    def redrawGraph(self):
        """
        Redraws the graph.
        Before the redrawing it checks the meta information of the tree
        """
        self.mouse()
        if self.tree.checkMeta() is False:
            edit = MetaEdit(self)
            edit.exec()
            if self.tree.checkMeta() is False:
                return
        self.scene.clear()
        self.printGraph()

    def refreshGraph(self):
        """
        Refreshes the graph.
        """
        for n in self.scene.items():
            if isinstance(n, Node):
                n.node.position = n.x(), n.y()
        self.scene.clear()
        self.printGraph(fixedPositions=True)

    def redrawItems(self):
        """
        Redraws a single item
        """
        for e in self.scene.items():
            if isinstance(e, Node) or isinstance(e, Conjunction):
                e.redraw()

    def mouse(self, action=None):
        """
         Sets the edit mode to normal mouse mode

        :param action: Button for the edit mode
        """
        if self.modeAction is not None:
            self.modeAction.setChecked(False)

        self.mode = 0
        self.modeAction = self.defaultModeAction
        self.modeAction.setChecked(True)
        self.setCursor(Qt.ArrowCursor)
        self.graphicsView.setDragMode(QGraphicsView.RubberBandDrag)

    def newThreat(self, action):
        """
        Sets the edit mode to threat insertion

         :param action: Button for the edit mode
         """
        if self.modeAction is not None:
            self.modeAction.setChecked(False)
            if self.modeAction is action:
                self.mode = 0
                self.modeAction = self.defaultModeAction
                self.modeAction.setChecked(True)
                self.setCursor(Qt.ArrowCursor)
                self.graphicsView.setDragMode(QGraphicsView.RubberBandDrag)
                return

        self.mode = 1
        self.modeAction = action
        self.setCursor(Qt.CrossCursor)

    def newCountermeasure(self, action):
        """
         Sets the edit mode to countermeasure insertion

         :param action: Button for the edit mode
         """
        if self.modeAction is not None:
            self.modeAction.setChecked(False)
            if self.modeAction is action:
                self.mode = 0
                self.modeAction = self.defaultModeAction
                self.modeAction.setChecked(True)
                self.setCursor(Qt.ArrowCursor)
                self.graphicsView.setDragMode(QGraphicsView.RubberBandDrag)
                return
        self.mode = 2
        self.modeAction = action
        self.setCursor(Qt.CrossCursor)

    def newConjunction(self, action):
        """
        Sets the edit mode to composition insertion

         :param action: Button for the edit mode
         """
        if self.modeAction is not None:
            self.modeAction.setChecked(False)
            if self.modeAction is action:
                self.mode = 0
                self.modeAction = self.defaultModeAction
                self.modeAction.setChecked(True)
                self.setCursor(Qt.ArrowCursor)
                self.graphicsView.setDragMode(QGraphicsView.RubberBandDrag)
                return
        self.mode = 3
        self.modeAction = action
        self.setCursor(Qt.CrossCursor)
        self.graphicsView.setDragMode(QGraphicsView.NoDrag)

    def newEdge(self, action):
        """
        Sets the edit mode to composition insertion

         :param action: Button for the edit mode
         """
        if self.modeAction is not None:
            self.modeAction.setChecked(False)
            if self.modeAction is action:
                self.mode = 0
                self.modeAction = self.defaultModeAction
                self.modeAction.setChecked(True)
                self.setCursor(Qt.ArrowCursor)
                self.graphicsView.setDragMode(QGraphicsView.RubberBandDrag)
                return
        self.mode = 4
        self.modeAction = action
        self.setCursor(Qt.CrossCursor)
        self.graphicsView.setDragMode(QGraphicsView.NoDrag)

    def delete(self, action):
        """
        Sets the edit mode to delete items

         :param action: Button for the edit mode
         """
        if self.modeAction is not None:
            self.modeAction.setChecked(False)
            if self.modeAction is action:
                self.mode = 0
                self.modeAction = self.defaultModeAction
                self.modeAction.setChecked(True)
                self.setCursor(Qt.ArrowCursor)
                self.graphicsView.setDragMode(QGraphicsView.RubberBandDrag)
                return
        self.mode = 5
        self.modeAction = action
        self.setCursor(Qt.CrossCursor)

    def editMeta(self):
        """
        Opens the meta edit dialog
        """
        edit = MetaEdit(self)
        edit.exec()

    def options(self):
        """
        Opens the options dialog
        """
        options = Options(self)
        options.show()

    def undo(self):
        """
        Undos the last action
        """
        self.mouse()
        if len(self.lastAction) > 0:
            tree = self.lastAction.pop()
            self.nextAction.append(copy.deepcopy(self.tree))
            self.tree = copy.deepcopy(tree)

            self.refreshGraph()

    def redo(self):
        """
        Undos the last undid action
        """
        self.mouse()

        if len(self.nextAction) > 0:
            tree = self.nextAction.pop()
            self.lastAction.append(copy.deepcopy(self.tree))
            self.tree = copy.deepcopy(tree)

            self.refreshGraph()

    def addLastAction(self):
        """
        Adds the last undo action to the undo stack
        """
        for n in self.scene.items():
            if isinstance(n, Node):
                n.node.position = n.x(), n.y()
        self.lastAction.append(copy.deepcopy(self.tree))

    def copy(self):
        """
        Saves the selected elements in the copyBuffer
        """
        self.copyBuffer = []
        self.tree.reservedList = []

        for i in self.scene.selectedItems():
            if isinstance(i, Node):
                self.copyBuffer.append(copy.copy(i.node))

        self.scene.clearSelection()

        idMapper = {}

        """
        Generates an array to map the old IDs to new one
        """
        for n in self.copyBuffer:
            id = n.id
            n.id = self.tree.getNextID(idMapper.values())
            idMapper[id] = n.id

        """
        Changes the IDs of the nodes in the copy buffer
        """
        for n in self.copyBuffer:
            parents = copy.copy(n.parents)
            n.parents = []
            for p in parents:
                if p in idMapper.keys():
                    n.parents.append(idMapper[p])
            children = copy.copy(n.children)
            n.children = []
            for c in children:
                if c in idMapper.keys():
                    n.children.append(idMapper[c])
        self.tree.reservedList = copy.copy(list(idMapper.values()))

    def cut(self):
        """
        Saves the selected elements in the copyBuffer and deletes them from view
        """
        self.addLastAction()
        self.saved = False
        self.addLastAction()
        self.copyBuffer = []
        self.tree.reservedList = []

        for i in self.scene.selectedItems():
            if isinstance(i, Node):
                self.copyBuffer.append(copy.copy(i.node))
                self.tree.reservedList.append(i.node.id)
        self.scene.deleteSelected()
        self.scene.clearSelection()

    def paste(self, action=None):
        """
        Sets the edit mode to insert the  items from the copy buffer

        :param action: Button for the edit mode
        """
        if action is None or action is False:
            action = self.modeActions['pasteAction']

        if self.modeAction is not None:
            self.modeAction.setChecked(False)
            if self.modeAction is action:
                self.mode = 0
                self.modeAction = self.defaultModeAction
                self.modeAction.setChecked(True)
                self.setCursor(Qt.ArrowCursor)
                self.graphicsView.setDragMode(QGraphicsView.RubberBandDrag)
                return
        self.mode = 6
        self.modeAction = action
        self.setCursor(Qt.CrossCursor)
        self.modeAction.setChecked(True)
        self.graphicsView.setDragMode(QGraphicsView.NoDrag)

    def insertCopyBuffer(self, x, y):
        """
        Inserts the copied elements at the position (x,y)
        :param x: X part of the position
        :param y: Y part of the position
        """
        self.addLastAction()
        self.saved = False
        xStart = None
        yStart = None

        if len(self.copyBuffer) > 0:
            for i in self.copyBuffer:
                if xStart is None:
                    xStart = i.position[0]
                    yStart = i.position[1]
                i.position = (i.position[0] + x - xStart, i.position[1] + y - yStart)
                for e in i.children:
                    self.tree.edgeList.append(types.Edge(i.id, e))
                self.tree.nodeList[i.id] = copy.copy(i)

            self.copyBuffer = []
            self.tree.reservedList = []

            self.refreshGraph()

    def zoomIn(self):
        """
        Zoom in
        """
        self.graphicsView.scale(1.10, 1.10)

    def zoomOut(self):
        """
        Zoom out
        """
        self.graphicsView.scale(0.90, 0.90)

    def closeEvent(self, event):
        """
        Reimplemented the close event to ask if the user wants to save the changes
        :param event: The close event
        """
        if len(self.tree.nodeList) > 0 and self.saved is False:
            reply = MessageBox('The document has been modified', 'Do you want to save your changes?',
                               QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Warning,
                               QMessageBox.Save).run()
            if reply == QMessageBox.Save:
                if self.saveFile() is True:
                    event.accept()
                    super().closeEvent(event)
                else:
                    event.ignore()
            elif reply == QMessageBox.Discard:
                event.accept()
                super().closeEvent(event)
            else:
                event.ignore()
        else:
            event.accept()
            super().closeEvent(event)

    def about(self):
        """
        Prints a simple about box
        """
        QMessageBox.about(self, 'About attackTreeDraw',
                          'atackTreeDraw is a tool to draw attack trees<br><br>Author: Daniel Fischer <br>'
                          'Supervisor: Prof. Dr. Christoph Karg<br><br>This is a part of his bachelor thesis<br><br>'
                          '<img src=' + os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                     'assets/images/hs-aalen-logo.png') + '>')

    def help(self):
        """
        Prints a simple help box
        """
        QMessageBox.about(self, 'Help', 'Visit <a href="https://github.com/masteroflittle/attackTreeDraw">'
                                        'https://github.com/masteroflittle/attackTreeDraw</a> for help')

    def generateSimple(self):
        """
        Generates an simple tree and redraws the tree
        """
        self.tree.makeSimple()
        self.redrawGraph()

    def exceptionHook(self, exctype, value, tb):
        """
        Hook for exceptions to print a message instead of crashing the program

        :param exctype: Type of the exception
        :param value: Value of the exception
        :param tb: Traceback
        """
        MessageBox('Something went wrong', 'Oops something went wrong:\nError Type: %s\nError Message: %s' %
                   (exctype, value), icon=QMessageBox.Critical).run()

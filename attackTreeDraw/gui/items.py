import math
import traceback

import sys
from PyQt5.QtCore import Qt, QRectF, QSizeF, QLineF, QPointF, QRect

from PyQt5.QtGui import QBrush, QFont, QPen, QPolygonF, QTransform
from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsItem, QGraphicsTextItem, QGraphicsRectItem, QGraphicsLineItem, QStyleOptionGraphicsItem, QStyle, QGraphicsScene, QMenu, QGraphicsView, QMessageBox

from .windows import NodeEdit, MessageBox

from data import types


class Node(QGraphicsItemGroup):
    """
    Parent class for all types of nodes.

    It contains all necessary functions to print a node in the GUI
    """

    def __init__(self, node, parent, background, border, text, x=0, y=0, offset=20):
        """
        Constructor for the node class.
        It generates all necessary variables and calls the draw function

        @param node: data node which it gets the data from
        @param parent: parent widget
        @param background: background color of the node
        @param border: border color for the node
        @param text: text color for the node
        @param x: x-position of the node
        @param y: y-position of the node
        @param offset: offset for the type to center it
        """
        super().__init__()

        self.typeOffset = offset

        self.node = node

        self.parent = parent

        self.threatEdge = None
        self.counterEdge = None
        self.defaultEdge = None
        
        self.childEdges = []
        self.parentEdges = []

        self.parentConjunctions = []

        self.headerGroup = QGraphicsItemGroup()
        self.attributes = QGraphicsItemGroup()
        self.footerGroup = QGraphicsItemGroup()

        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

        self.attributesHeight = 0
        self.headerHeight = 0

        self.printHeader(background, border, text)
        self.printAttributes(background, border, text)
        self.printFooter(background, border, text)

        self.setPos(x, y)

    def getTypeRecursiveDown(self):
        if isinstance(self, Conjunction):
            for c in self.childEdges:
                if isinstance(c.dst, Conjunction):
                    return c.dst.getTypeRecursiveDown()
                else:
                    return type(c.dst)
            return type(self)
        else:
            return type(self)

    def getTypeRecursiveUp(self):
        if isinstance(self, Conjunction):
            for c in self.childEdges:
                if isinstance(c.dst, Conjunction):
                    return c.dst.getTypeRecursiveUp()
                else:
                    return type(c.dst)
            return type(self)
        else:
            return type(self)

    def addEdge(self, dst):
        if isinstance(self, Threat) and dst.getTypeRecursiveDown() is Threat:
            self.childEdges.append(Edge(self, dst, -50))
        elif isinstance(self, Threat) and dst.getTypeRecursiveDown() is Countermeasure:
            self.childEdges.append(Edge(self, dst, 50))
        else:
            self.childEdges.append(Edge(self, dst, 0))
        dst.parentEdges.append(self.childEdges[-1])
        self.parent.scene.addItem(self.childEdges[-1])

    def actualizeEdges(self):
        for e in self.childEdges:
            if isinstance(self, Threat) and e.dst.getTypeRecursiveDown() is Threat:
                e.offset = -50
            elif isinstance(self, Threat) and e.dst.getTypeRecursiveDown() is Countermeasure:
                e.offset = 50
            else:
                e.offset = 0

    def getLeftRightChildren(self):
        left = []
        right = []
        neutralLeft = False
        for e in self.childEdges:
            if e.offset < 0:
                left.append(e.dst)
            elif e.offset > 0:
                right.append(e.dst)
            else:
                if neutralLeft is False:
                    left.append(e.dst)
                    neutralLeft = True
                else:
                    right.append(e.dst)
                    neutralLeft = False
        return left, right

    def printHeader(self, background, border, text):
        """
        Prints the the header of the node.
        It contains the Node id, title and type

        @param background: background color of the node
        @param border: border color for the node
        @param text: text color for the node
        """
        x = self.x()
        y = self.y()

        self.idText = QGraphicsTextItem()
        self.typeText = QGraphicsTextItem()
        self.titleText = QGraphicsTextItem()

        self.idRect = QGraphicsRectItem()
        self.typeRect = QGraphicsRectItem()
        self.titleRect = QGraphicsRectItem()

        self.typeText.setFont(QFont('Arial', 10))
        self.titleText.setFont(QFont('Arial', 10))
        self.idText.setFont(QFont('Arial', 10))

        self.typeText.setDefaultTextColor(text)
        self.titleText.setDefaultTextColor(text)
        self.idText.setDefaultTextColor(text)

        self.titleText.setTextWidth(200)

        self.idText.setPlainText(self.node.id)
        self.typeText.setPlainText(self.node.type)
        self.titleText.setPlainText(self.node.title)

        titleHeight = int(self.titleText.boundingRect().height() / 20 + 0.5) * 20

        self.idRect.setRect(x, y, 50, 20)
        self.typeRect.setRect(x + 50, y, 150, 20)
        self.titleRect.setRect(x, y + 20, 200, titleHeight)

        self.idRect.setBrush(QBrush(background))
        self.typeRect.setBrush(QBrush(background))
        self.titleRect.setBrush(QBrush(background))

        self.idRect.setPen(QPen(border))
        self.typeRect.setPen(QPen(border))
        self.titleRect.setPen(QPen(border))

        self.idText.setPos(x, y)
        self.typeText.setPos(x + self.typeOffset, y)
        self.titleText.setPos(x, y + 18)

        self.headerHeight = titleHeight + 20

        self.headerGroup.addToGroup(self.idRect)
        self.headerGroup.addToGroup(self.typeRect)
        self.headerGroup.addToGroup(self.titleRect)
        self.headerGroup.addToGroup(self.idText)
        self.headerGroup.addToGroup(self.typeText)
        self.headerGroup.addToGroup(self.titleText)
        self.addToGroup(self.headerGroup)

    def printAttributes(self, background, border, text):
        """
        Prints the attributes of the node
        The attributes are a key, value pair

        @param background: background color of the node
        @param border: border color for the node
        @param text: text color for the node
        """
        y = self.y() + self.headerHeight
        x = self.x()

        self.attributesHeight = 0

        for k, v in self.node.attributes.items():
            key = QGraphicsTextItem()
            key.setFont(QFont('Arial', 10))
            key.setDefaultTextColor(text)
            key.setTextWidth(100)
            key.setPlainText(k)
            keyHeight = int(key.boundingRect().height() / 20 + 0.5) * 20

            value = QGraphicsTextItem()
            value.setFont(QFont('Arial', 10))
            value.setDefaultTextColor(text)
            value.setTextWidth(100)
            value.setPlainText(v)
            valueHeight = int(value.boundingRect().height() / 20 + 0.5) * 20

            height = valueHeight if valueHeight > keyHeight else keyHeight

            keyRect = QGraphicsRectItem()
            keyRect.setRect(x, y, 100, height)
            valueRect = QGraphicsRectItem()
            valueRect.setRect(x + 100, y, 100, height)

            keyRect.setBrush(QBrush(background))
            valueRect.setBrush(QBrush(background))

            keyRect.setPen(QPen(border, 1))
            valueRect.setPen(QPen(border, 1))

            key.setPos(x, y)
            value.setPos(x + 100, y)

            self.attributes.addToGroup(keyRect)
            self.attributes.addToGroup(valueRect)
            self.attributes.addToGroup(key)
            self.attributes.addToGroup(value)

            y = y + height
            self.attributesHeight += height

        self.addToGroup(self.attributes)

    def redrawOptions(self, background, border, text):
        """
        Redraws the node with option for the background, border and text color

        @param background: background color of the node
        @param border: border color for the node
        @param text: text color for the node
        """
        y = self.y()
        x = self.x()

        self.prepareGeometryChange()

        for i in self.attributes.childItems():
            self.attributes.removeFromGroup(i)
            self.parent.scene.removeItem(i)

        for i in self.headerGroup.childItems():
            self.headerGroup.removeFromGroup(i)
            self.parent.scene.removeItem(i)

        for i in self.footerGroup.childItems():
            self.footerGroup.removeFromGroup(i)
            self.parent.scene.removeItem(i)

        self.removeFromGroup(self.attributes)
        self.removeFromGroup(self.footerGroup)
        self.removeFromGroup(self.headerGroup)

        self.printHeader(background, border, text)

        self.printAttributes(background, border, text)

        self.printFooter(background, border, text)

        self.parent.scene.removeItem(self)
        self.parent.scene.addItem(self)

        self.update()
        self.parent.graphicsView.update()

        self.setPos(x, y)

    def redraw(self):
        """
        Redraws the node with standard colors
        """
        self.redrawOptions(Qt.white, Qt.black, Qt.black)

    def printFooter(self, background, border, text):
        """
        Prototype function for the footer.
        Implemented in the child classes

        @param background: background color of the node
        @param border: border color for the node
        @param text: text color for the node
        """
        pass

    def paint(self, painter, options, widget=None):
        """
        Reimplementation for the paint function of the QGraphicsItemGroup.
        The Reimplementation is needed to print a proper border when the item is selected

        @param painter: The painter, which draws the node
        @param options: options for the paint job
        @param widget: widget of the Item
        """
        myOption = QStyleOptionGraphicsItem(options)
        myOption.state &= ~QStyle.State_Selected

        super().paint(painter, myOption, widget=None)

        if self.isSelected():
            painter.setPen(QPen(Qt.black, 1, Qt.DashLine))
            rect = QRect(self.boundingRect().x() - 2, self.boundingRect().y() - 2, self.boundingRect().x() + self.boundingRect().width() + 4, self.boundingRect().y() + self.boundingRect().height() + 3)
            painter.drawRect(rect)

    def mouseDoubleClickEvent(self, event):
        """
        Handles a double click on the node.
        The double click opens the edit window for this node

        @param event: click event
        """
        edit = NodeEdit(self, self.parent)
        edit.exec()


class Threat(Node):
    """
    This class handles the gui for a threat node
    """

    def __init__(self, node, parent, x=0, y=0):
        """
        Constructor for the threat node.
        It generates all necessary variables and calls the draw function

        @param node: data node which it gets the data from
        @param parent: parent widget
        @param x: x-position of the node
        @param y: y-position of the node
        """
        self.threatBox = None
        self.counterBox = None

        self.threatBoxText = None
        self.counterBoxText = None

        super().__init__(node, parent, parent.threatBackground, parent.threatBorder, parent.threatFont, x, y, 91)

    def printFooter(self, background, border, text):
        """
        Prints the footer for the threat node
        The footer contains two columns where the conjunction will start from

        @param background: background color of the node
        @param border: border color for the node
        @param text: text color for the node
        """
        self.threatBoxText = QGraphicsTextItem()
        self.threatBoxText.setFont(QFont('Arial', 10))
        self.threatBoxText.setDefaultTextColor(text)
        self.threatBoxText.setPlainText('T')

        self.counterBoxText = QGraphicsTextItem()
        self.counterBoxText.setFont(QFont('Arial', 10))
        self.counterBoxText.setDefaultTextColor(text)
        self.counterBoxText.setPlainText('C')

        self.threatBox = QGraphicsRectItem()
        self.counterBox = QGraphicsRectItem()

        self.threatBox.setBrush(QBrush(background))
        self.counterBox.setBrush(QBrush(background))

        self.threatBox.setPen(QPen(border))
        self.counterBox.setPen(QPen(border))

        self.footerGroup = QGraphicsItemGroup()

        self.footerGroup.addToGroup(self.threatBox)
        self.footerGroup.addToGroup(self.counterBox)
        self.footerGroup.addToGroup(self.threatBoxText)
        self.footerGroup.addToGroup(self.counterBoxText)

        self.threatBox.setRect(0, 0, 100, 20)
        self.counterBox.setRect(100, 0, 100, 20)

        self.threatBoxText.setPos(40, 0)
        self.counterBoxText.setPos(140, 0)

        self.footerGroup.setPos(self.x(), self.y() + self.headerHeight + self.attributesHeight)

        self.addToGroup(self.footerGroup)

    def redraw(self):
        """
        Redraws the node with the colors set in the options menu
        """
        super().redrawOptions(self.parent.threatBackground, self.parent.threatBorder, self.parent.threatFont)


class Countermeasure(Node):
    """
    This class handles the gui for a countermeasure node
    """

    def __init__(self, node, parent, x=0, y=0):
        """
        Constructor for the countermeasure node.
        It generates all necessary variables and calls the draw function

        @param node: data node which it gets the data from
        @param parent: parent widget
        @param x: x-position of the node
        @param y: y-position of the node
        """
        super().__init__(node, parent, parent.countermeasureBackground, parent.countermeasureBorder, parent.countermeasureFont, x, y, 63)

    def printFooter(self, background, border, text):
        """
        This function is not needed in the countermeasure node
        But needs to be implemented because it is called in the parent node

        @param background: background color of the node
        @param border: border color for the node
        @param text: text color for the node
        """
        pass

    def redraw(self):
        """
        Redraws the node with the colors set in the options menu
        """
        super().redrawOptions(self.parent.countermeasureBackground, self.parent.countermeasureBorder, self.parent.countermeasureFont)


class Conjunction(Node):
    pass


class ConjunctionRect(QGraphicsRectItem):
    def paint(self, painter, options, widget=None):
        """
        Reimplementation for the paint function of the QGraphicsItem.
        This is needed to draw a rounded rectangle
        The Reimplementation is also needed to print a proper border when the item is selected

        @param painter: The painter, which draws the node
        @param options: options for the paint job
        @param widget: widget of the Item
        """
        if self.isSelected():
            painter.setPen(QPen(Qt.black, 1, Qt.DashLine))
            rect = QRect(self.boundingRect().x() - 2, self.boundingRect().y() - 2, self.boundingRect().x() + self.boundingRect().width() + 4, self.boundingRect().y() + self.boundingRect().height() + 3)
            painter.drawRect(rect)

        painter.setBrush(self.brush())
        painter.setPen(self.pen())

        painter.drawRoundedRect(self.boundingRect(), 20, 20)


class Edge(QGraphicsLineItem):
    """
    Implements an Edge to two nodes
    """
    def __init__(self, start, dst, offset, color=Qt.black):
        """
        Constructor for a conjunction.
        It generates all necessary variables and calls the draw function
        It adds also the parent arrow from the source to the conjunction rectangle

        @param start: Starting object of the arrow
        @param end: End object of the arrow
        @param offset: left/right offset for the starting arrow
        @param color: Color of the arrow
        """
        super().__init__()

        self.arrowHead = QPolygonF()

        self.start = start
        self.dst = dst

        self.offset = offset

        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

        self.setPen(QPen(color, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

    def boundingRect(self):
        """
        New calculation of the bounding rect, because the arrow is not only a line

        @return: new bounding rectangle
        """
        extra = (self.pen().width() + 20) / 2.0

        return QRectF(self.line().p1(), QSizeF(self.line().p2().x() - self.line().p1().x(), self.line().p2().y() - self.line().p1().y())).normalized().adjusted(-extra, -extra, extra, extra)

    def shape(self):
        """
        Calculation of the shape of the arrow

        @return: shape of the arrow
        """
        path = QGraphicsLineItem.shape(self)
        path.addPolygon(self.arrowHead)
        return path

    def updatePosition(self):
        """
        Updates the position of the arrow
        """
        line = QLineF(self.mapFromItem(self.start, 0, 0), self.mapFromItem(self.dst, 0, 0))
        self.setLine(line)

    def paint(self, painter, options, widget=None):
        """
        Painter implementation for the arrow.
        First it draws the line and then the triangle on the end

        @param painter: The painter, which draws the node
        @param options: options for the paint job
        @param widget: widget of the Item
        """

        if self.start.collidesWithItem(self.dst):
            return

        myPen = self.pen()
        arrowSize = 10
        painter.setPen(myPen)
        painter.setBrush(myPen.color())

        centerLine = QLineF(QPointF(self.start.x() + self.start.boundingRect().center().x() + self.offset, self.start.y() + self.start.boundingRect().bottom()), QPointF(self.dst.x() + self.dst.boundingRect().center().x(), self.dst.y()))
        endPolygon = self.dst.mapFromItem(self.dst, self.dst.boundingRect())
        p1 = endPolygon.first() + self.dst.pos()
        p2 = None
        intersectPoint = QPointF()

        for i in endPolygon:
            p2 = i + self.dst.pos()

            polyLine = QLineF(p1, p2)

            intersectType = polyLine.intersect(centerLine, intersectPoint)
            if intersectType == QLineF.BoundedIntersection:
                break
            p1 = p2

        self.setLine(QLineF(intersectPoint, QPointF(self.start.x() + self.start.boundingRect().center().x() + self.offset, self.start.y() + self.start.boundingRect().bottom())))

        angle = math.atan2(-self.line().dy(), self.line().dx())
        arrowP1 = self.line().p1() + QPointF(math.sin(angle + math.pi / 3) * arrowSize, math.cos(angle + math.pi / 3) * arrowSize)
        arrowP2 = self.line().p1() + QPointF(math.sin(angle + math.pi - math.pi / 3) * arrowSize, math.cos(angle + math.pi - math.pi / 3) * arrowSize)

        self.arrowHead.clear()
        self.arrowHead << self.line().p1() << arrowP1 << arrowP2

        painter.drawLine(self.line())
        painter.drawPolygon(self.arrowHead)
        if self.isSelected():
            painter.setPen(QPen(Qt.black, 1, Qt.DashLine))
            myLine = self.line()
            myLine.translate(0, 4.0)
            painter.drawLine(myLine)
            myLine.translate(0, -8.0)
            painter.drawLine(myLine)


class AttackTreeScene(QGraphicsScene):
    """
    This Class Implements the click actions for the graphics scene
    """

    def __init__(self, parent=None):
        """
        Constructor for the AttackTreeScene.
        Sets the needed class variables and initializes the context menu

        @param parent: Parent widget for the AttackTreeScene
        """
        super().__init__(parent)
        self.startCollisions = None
        self.dstCollisions = None
        self.conjunction = None
        self.insertLine = None

        self.mousePos = (0, 0)

        self.menu = QMenu(parent)

        self.menu.addAction('Alternative', self.addAlternative)
        self.menu.addAction('Composition', self.addComposition)
        self.menu.addAction('Sequence', self.addSequence)
        self.menu.addAction('Threshold', self.addThreshold)

    def addAlternative(self):
        """
        Adds an alternative as edge
        """
        self.addEdge('alternative')

    def addComposition(self):
        """
        Adds an composition as edge
        """
        self.addEdge('composition')

    def addSequence(self):
        """
        Adds an sequence as edge
        """
        self.addEdge('sequence')

    def addThreshold(self):
        """
        Adds an threshold as edge
        """
        self.addEdge('threshold')

    def addEdge(self, type):
        """
        Adds an edge to the graph with the specific type
        @param type: Type of the edge (alternative|alternative|sequence|threshold)
        """

        node = types.Conjunction(conjunctionType=type)
        self.parent().tree.addNode(node)

        n = Conjunction(node, self.parent(), self.parent().threatBackground, self.parent().threatBorder, self.parent().threatFont,x=self.mousePos[0],y=self.mousePos[1], offset=60)  # @TODO: Change color
        self.addItem(n)

        self.parent().graphicsView.update()
        self.reset()
        self.parent().saved = False

    def reset(self):
        """
        Resets all actions if a mode was selected.
        Also deletes the Line for inserting a edge
        """
        self.startCollisions = None
        self.dstCollisions = None
        self.conjunction = None
        self.parent().mode = 0
        self.parent().modeAction.setChecked(False)
        self.parent().modeAction = self.parent().defaultModeAction
        self.parent().modeAction.setChecked(True)
        if self.insertLine is not None:
            self.removeItem(self.insertLine)
            self.insertLine = None
        self.parent().setCursor(Qt.ArrowCursor)
        self.parent().graphicsView.setDragMode(QGraphicsView.RubberBandDrag)

    def mousePressEvent(self, mouseEvent):
        """
        Handles the press event for the mouse
        On click it will insert a node or set the start position for a conjunction

        @param mouseEvent: Mouse Event
        """
        if mouseEvent.button() == Qt.LeftButton:
            try:
                if self.parent().mode == 1:
                    self.parent().addLastAction()

                    node = types.Threat()
                    self.parent().tree.addNode(node)
                    n = Threat(node, self.parent(), mouseEvent.scenePos().x(), mouseEvent.scenePos().y())
                    self.addItem(n)

                    self.parent().graphicsView.update()

                    edit = NodeEdit(n, n.parent)
                    edit.exec()

                    self.parent().saved = False
                    self.reset()
                    super().mousePressEvent(mouseEvent)
                elif self.parent().mode == 2:
                    self.parent().addLastAction()

                    node = types.Countermeasure()
                    self.parent().tree.addNode(node)
                    n = Countermeasure(node, self.parent(), mouseEvent.scenePos().x(), mouseEvent.scenePos().y())
                    self.addItem(n)
                    self.parent().graphicsView.update()
                    self.parent().saved = False

                    edit = NodeEdit(n, n.parent)
                    edit.exec()

                    super().mousePressEvent(mouseEvent)
                    self.reset()
                elif self.parent().mode == 3:
                    self.mousePos = mouseEvent.scenePos().x(), mouseEvent.scenePos().y()
                    self.menu.popup(self.parent().mapToGlobal(self.parent().graphicsView.mapFromScene(mouseEvent.scenePos())), None)
                    super().mousePressEvent(mouseEvent)
                    self.reset()
                elif self.parent().mode == 4:

                    self.startCollisions = self.itemAt(mouseEvent.scenePos(), QTransform())
                    self.insertLine = QGraphicsLineItem(QLineF(mouseEvent.scenePos(), mouseEvent.scenePos()))
                    self.insertLine.setPen(QPen(Qt.black, 2))
                    self.addItem(self.insertLine)

                    self.parent().addLastAction()
                else:
                    super().mousePressEvent(mouseEvent)
            except Exception as e:
                print(traceback.format_exc())
                exit(-1)

    def mouseMoveEvent(self, mouseEvent):
        """
        Handler for the move event of the mouse.
        If the mode is to draw a line (3) it will update the feedback line

        @param mouseEvent: Mouse Event
        """
        if self.insertLine is not None:
            newLine = QLineF(self.insertLine.line().p1(), mouseEvent.scenePos())
            self.insertLine.setLine(newLine)
        super().mouseMoveEvent(mouseEvent)

    def mouseReleaseEvent(self, mouseEvent):
        """
        Handles the mouse release event.
        In this event the edge will be completed or the item to delete are certain

        @param mouseEvent: Mouse Event
        """

        if mouseEvent.button() == Qt.LeftButton:
            if self.parent().mode == 4:
                try:
                    self.parent().addLastAction()
                    self.insertLine.setZValue(-1)
                    self.dstCollisions = self.itemAt(mouseEvent.scenePos(), QTransform())
                    if self.startCollisions is None or self.dstCollisions is None or self.startCollisions == self.dstCollisions:
                        self.reset()
                        super().mouseReleaseEvent(mouseEvent)
                        return
                    if isinstance(self.startCollisions.parentItem(), Node):
                        self.startCollisions = self.startCollisions.parentItem()
                    elif isinstance(self.startCollisions.parentItem(), QGraphicsItemGroup) and isinstance(self.startCollisions.parentItem().parentItem(), Node):
                        self.startCollisions = self.startCollisions.parentItem().parentItem()
                    else:
                        self.reset()
                        super().mouseReleaseEvent(mouseEvent)
                        return
                    if isinstance(self.dstCollisions.parentItem(), Node):
                        self.dstCollisions = self.dstCollisions.parentItem()
                    elif isinstance(self.dstCollisions.parentItem(), QGraphicsItemGroup) and isinstance(self.dstCollisions.parentItem().parentItem(), Node):
                        self.dstCollisions = self.dstCollisions.parentItem().parentItem()
                    else:
                        self.reset()
                        super().mouseReleaseEvent(mouseEvent)
                        return

                    if self.parent().tree.addEdge(self.startCollisions.node.id, self.dstCollisions.node.id) is True:
                        self.startCollisions.addEdge(self.dstCollisions)
                        self.parent().graphicsView.update()
                        self.reset()
                        self.parent().saved = False
                    else:
                        MessageBox('Adding Edge is not possible', 'The Edge is not supported', icon=QMessageBox.Critical).run()
                        self.reset()
                except Exception as e:
                    print(traceback.format_exc())
            elif self.parent().mode == 5:  # @TODO: Rework
                self.parent().addLastAction()
                try:  # @TODO: remove try
                    deleted = []
                    for i in self.selectedItems():
                        if i not in deleted:
                            if isinstance(i, Node):
                                for c in i.parentConjunctions:
                                    if len(c.arrows) != 0 and len(c.children) != 0:
                                        deleted.append(c.arrows[c.children.index(i)])
                                        self.removeItem(c.arrows[c.children.index(i)])
                                        del c.arrows[c.children.index(i)]
                                        c.children.remove(i)
                                    if len(c.children) == 0:
                                        if c == c.parent.threatConjunction:
                                            c.parent.threatConjunction = None
                                        else:
                                            c.parent.counterConjunction = None
                                        children = c.children.copy()
                                        for a in children:
                                            deleted.append(c.arrows[c.children.index(a)])
                                            self.removeItem(c.arrows[c.children.index(a)])
                                            del c.arrows[c.children.index(a)]
                                            c.children.remove(a)
                                        deleted.append(c.parentArrow)
                                        deleted.append(c)
                                        self.removeItem(c.parentArrow)
                                        self.removeItem(c)

                                if i.threatConjunction is not None:
                                    deleted.append(i.threatConjunction.parentArrow)
                                    self.removeItem(i.threatConjunction.parentArrow)
                                    children = i.threatConjunction.children.copy()
                                    for a in children:
                                        deleted.append(i.threatConjunction.arrows[i.threatConjunction.children.index(a)])
                                        self.removeItem(i.threatConjunction.arrows[i.threatConjunction.children.index(a)])
                                        del i.threatConjunction.arrows[i.threatConjunction.children.index(a)]
                                        i.threatConjunction.children.remove(a)
                                    deleted.append(i.threatConjunction)
                                    self.removeItem(i.threatConjunction)

                                if i.counterConjunction is not None:
                                    deleted.append(i.counterConjunction.parentArrow)
                                    self.removeItem(i.counterConjunction.parentArrow)
                                    children = i.counterConjunction.children.copy()
                                    for a in children:
                                        deleted.append(i.counterConjunction.arrows[i.counterConjunction.children.index(a)])
                                        self.removeItem(i.counterConjunction.arrows[i.counterConjunction.children.index(a)])
                                        del i.counterConjunction.arrows[i.counterConjunction.children.index(a)]
                                        i.counterConjunction.children.remove(a)
                                    deleted.append(i.counterConjunction)
                                    self.removeItem(i.counterConjunction)

                                self.parent().tree.removeNode(i.node.id)
                                deleted.append(i)
                                self.removeItem(i)
                            elif isinstance(i, Conjunction):
                                children = i.children.copy()
                                for c in children:
                                    self.parent().tree.removeEdge(i.parent.node.id + '-' + c.node.id)
                                    deleted.append(i.arrows[i.children.index(c)])
                                    self.removeItem(i.arrows[i.children.index(c)])
                                    del i.arrows[i.children.index(c)]
                                    i.children.remove(c)
                                if i == i.parent.threatConjunction:
                                    i.parent.threatConjunction = None
                                else:
                                    i.parent.counterConjunction = None
                                deleted.append(i.parentArrow)
                                deleted.append(i)
                                self.removeItem(i.parentArrow)
                                self.removeItem(i)
                            elif isinstance(i, Arrow):
                                if isinstance(i.start, Conjunction):
                                    del i.start.children[i.start.arrows.index(i)]
                                    i.start.arrows.remove(i)
                                    self.parent().tree.removeEdge(i.start.parent.node.id + '-' + i.end.node.id)
                                    deleted.append(i)
                                    self.removeItem(i)
                                    if len(i.start.children) == 0:
                                        if i.start == i.start.parent.threatConjunction:
                                            i.start.parent.threatConjunction = None
                                        else:
                                            i.start.parent.counterConjunction = None
                                        for a in i.start.children:
                                            deleted.append(i.start.arrows[i.start.children.index(a)])
                                            self.removeItem(i.start.arrows[i.start.children.index(a)])
                                            del i.start.arrows[i.start.children.index(a)]
                                            i.start.children.remove(a)
                                        deleted.append(i.start.parentArrow)
                                        deleted.append(i.start)
                                        self.removeItem(i.start.parentArrow)
                                        self.removeItem(i.start)
                                else:
                                    if isinstance(i.start, Node):
                                        edges = i.start.node.edges.copy()
                                        for c in edges:
                                            self.parent().tree.removeEdge(i.start.node.id + '-' + c)

                                        children = i.end.children.copy()
                                        for a in children:
                                            deleted.append(i.end.arrows[i.end.children.index(a)])
                                            self.removeItem(i.end.arrows[i.end.children.index(a)])
                                            del i.end.arrows[i.end.children.index(a)]

                                            a.parentConjunctions.remove(i.end)
                                            i.end.children.remove(a)

                                        if i.end == i.start.threatConjunction:
                                            i.start.threatConjunction = None
                                        else:
                                            i.start.counterConjunction = None
                                        deleted.append(i.end)
                                        self.removeItem(i.end)
                                    else:
                                        for c in i.start.parent().node.edges:
                                            self.parent().tree.removeEdge(i.start.parent().node.id + '-' + c.id)
                                        deleted.append(i.end)
                                        self.removeItem(i.end)
                                    deleted.append(i)
                                    self.removeItem(i)
                except Exception as e:
                    print(sys.exc_info())
                    print(traceback.format_exc())
                    exit(-1)

                self.parent().graphicsView.update()
                self.reset()
                self.parent().saved = False
            else:
                self.reset()
        super().mouseReleaseEvent(mouseEvent)

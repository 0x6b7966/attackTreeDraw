import functools
import math
import traceback

from PyQt5.QtCore import Qt, QRectF, QSizeF, QLineF, QPointF, QRect, QPoint

from PyQt5.QtGui import QBrush, QFont, QPen, QPolygonF, QTransform, QPainter, QColor
from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsItem, QGraphicsTextItem, QGraphicsRectItem, QGraphicsLineItem, \
    QStyleOptionGraphicsItem, QStyle, QGraphicsScene, QMenu, QGraphicsView, QMessageBox

from .windows import NodeEdit, MessageBox, ConjunctionEdit

from data import types
from .helper import Configuration


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

        self.setAcceptDrops(True)

        self.setPos(x, y)

    def getTypeRecursiveDown(self):
        """
        Searches the children of a node to get a node with type != Conjunction
        If there is no other node with type != Conjunction, Conjunction will be returned
        @return: type of first child node with type != Conjunction or Conjunction
        """
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
        """
        Searches the parents of a node to get a node with type != Conjunction
        If there is no other node with type != Conjunction, Conjunction will be returned
        @return: type of first parent node with type != Conjunction or Conjunction
        """
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
        """
        Adds an child edge to this node an places the start of the arrow in the right place
        @param dst: destination node for the edge
        """
        if isinstance(self, Threat) and dst.getTypeRecursiveDown() is Threat:
            edge = Edge(self, dst, -50)
        elif isinstance(self, Threat) and dst.getTypeRecursiveDown() is Countermeasure:
            edge = Edge(self, dst, 50)
        else:
            edge = Edge(self, dst, 0)
        self.parent.scene.addItem(edge)
        self.childEdges.append(edge)
        dst.parentEdges.append(self.childEdges[-1])

    def actualizeEdges(self):
        """
        Actualizes all child edges of this node so they start at the right position
        """
        for e in self.childEdges:
            if isinstance(self, Threat) and e.dst.getTypeRecursiveDown() is Threat:
                e.offset = -50
            elif isinstance(self, Threat) and e.dst.getTypeRecursiveDown() is Countermeasure:
                e.offset = 50
            else:
                e.offset = 0

    def fixParentEdgeRec(self):
        """
        Fixes all starts of the parent edges so they start at the right position
        """
        for p in self.parentEdges:
            if isinstance(p.start, Conjunction):
                p.start.fixParentEdgeRec()
            else:
                p.start.actualizeEdges()

    def getLeftRightChildren(self):
        """
        Splits the children in to arrays with the same size
        @return: Tuple (left, right) with child elements split in to arrays
        """
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

        self.typeText.setFont(Configuration.font)
        self.titleText.setFont(Configuration.font)
        self.idText.setFont(Configuration.font)

        self.typeText.setDefaultTextColor(QColor(text))
        self.titleText.setDefaultTextColor(QColor(text))
        self.idText.setDefaultTextColor(QColor(text))

        self.titleText.setTextWidth(200)

        self.idText.setPlainText(self.node.id)
        self.typeText.setPlainText(type(self.node).__name__)
        self.titleText.setPlainText(self.node.title)

        titleHeight = int(self.titleText.boundingRect().height() / 20 + 0.5) * 20

        self.idRect.setRect(x, y, 50, 20)
        self.typeRect.setRect(x + 50, y, 150, 20)
        self.titleRect.setRect(x, y + 20, 200, titleHeight)

        self.idRect.setBrush(QBrush(QColor(background)))
        self.typeRect.setBrush(QBrush(QColor(background)))
        self.titleRect.setBrush(QBrush(QColor(background)))

        self.idRect.setPen(QPen(QColor(border), 2))
        self.typeRect.setPen(QPen(QColor(border), 2))
        self.titleRect.setPen(QPen(QColor(border), 2))

        self.idText.setPos(x, y - 2)
        self.typeText.setPos(x + self.typeOffset, y - 2)
        self.titleText.setPos(x, y + 18)

        self.headerHeight = titleHeight + 20

        self.setToolTip(self.node.description)

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
            key.setFont(Configuration.font)
            key.setDefaultTextColor(QColor(text))
            key.setTextWidth(100)
            key.setPlainText(k)
            keyHeight = int(key.boundingRect().height() / 20 + 0.5) * 20

            value = QGraphicsTextItem()
            value.setFont(Configuration.font)
            value.setDefaultTextColor(QColor(text))
            value.setTextWidth(100)
            value.setPlainText(v)
            valueHeight = int(value.boundingRect().height() / 20 + 0.5) * 20

            height = valueHeight if valueHeight > keyHeight else keyHeight

            keyRect = QGraphicsRectItem()
            keyRect.setRect(x, y, 100, height)
            valueRect = QGraphicsRectItem()
            valueRect.setRect(x + 100, y, 100, height)

            keyRect.setBrush(QBrush(QColor(background)))
            valueRect.setBrush(QBrush(QColor(background)))

            keyRect.setPen(QPen(QColor(border), 2))
            valueRect.setPen(QPen(QColor(border), 2))

            key.setPos(x, y - 2)
            value.setPos(x + 100, y - 2)

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

    def setPos(self, x, y):
        """
        Overloads setPos to set the position of the visible node in the data node

        @param x: X part of the position
        @param y: Y part of the position
        """
        self.node.position = (x, y)
        super().setPos(x, y)

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

        if options.state & QStyle.State_Selected:
            painter.setPen(QPen(Qt.black, 2, Qt.DotLine))
            rect = QRect(self.boundingRect().x() - 1.5, self.boundingRect().y() - 1.5,
                         self.boundingRect().x() + self.boundingRect().width() + 3,
                         self.boundingRect().y() + self.boundingRect().height() + 0.5)
            painter.drawRect(rect)

    def selectChildren(self):
        """
        Select all children
        """
        self.setSelected(True)
        for i in self.childEdges:
            i.setSelected(True)
            i.dst.selectChildren()

    def delete(self):
        """
        Deletes this node
        """
        for e in self.parentEdges:
            self.parent.scene.removeItem(e)
        for e in self.childEdges:
            self.parent.scene.removeItem(e)
        self.parent.tree.removeNode(self.node.id)
        self.parent.scene.removeItem(self)

    def edit(self):
        """
        Opens the edit dialog
        """
        NodeEdit(self, self.parent).exec()

    def mouseDoubleClickEvent(self, event):
        """
        Handles a double click on the node.
        The double click opens the edit window for this node

        @param event: click event
        """
        self.edit()

    def dropEvent(self, event):
        """
        Sets the correct position to the data node if the item is drag & dropped

        @param event: Drop event
        @return: Changed Value
        """

        print("ok")
        self.node.position = (event.pos().x(), event.pos().y())
        return super().dropEvent(self, event)


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

        super().__init__(node, parent, Configuration.colors['threat']['node']['background'],
                         Configuration.colors['threat']['node']['border'],
                         Configuration.colors['threat']['node']['font'], x, y, 91)

    def printFooter(self, background, border, text):
        """
        Prints the footer for the threat node
        The footer contains two columns where the conjunction will start from

        @param background: background color of the node
        @param border: border color for the node
        @param text: text color for the node
        """
        self.threatBoxText = QGraphicsTextItem()
        self.threatBoxText.setFont(Configuration.font)
        self.threatBoxText.setDefaultTextColor(QColor(text))
        self.threatBoxText.setPlainText('T')

        self.counterBoxText = QGraphicsTextItem()
        self.counterBoxText.setFont(Configuration.font)
        self.counterBoxText.setDefaultTextColor(QColor(text))
        self.counterBoxText.setPlainText('C')

        self.threatBox = QGraphicsRectItem()
        self.counterBox = QGraphicsRectItem()

        self.threatBox.setBrush(QBrush(QColor(background)))
        self.counterBox.setBrush(QBrush(QColor(background)))

        self.threatBox.setPen(QPen(QColor(border), 2))
        self.counterBox.setPen(QPen(QColor(border), 2))

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
        super().redrawOptions(Configuration.colors['threat']['node']['background'],
                              Configuration.colors['threat']['node']['border'],
                              Configuration.colors['threat']['node']['font'])


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
        super().__init__(node, parent, Configuration.colors['countermeasure']['node']['background'],
                         Configuration.colors['countermeasure']['node']['border'],
                         Configuration.colors['countermeasure']['node']['font'], x, y, 63)

    def redraw(self):
        """
        Redraws the node with the colors set in the options menu
        """
        super().redrawOptions(Configuration.colors['countermeasure']['node']['background'],
                              Configuration.colors['countermeasure']['node']['border'],
                              Configuration.colors['countermeasure']['node']['font'])


class Conjunction(Node):
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
        if len(node.children) > 0:
            if parent.tree.getTypeRecursiveDown(parent.tree.nodeList[node.children[0]]) is types.Countermeasure:
                parentType = 'countermeasure'
            elif parent.tree.getTypeRecursiveDown(parent.tree.nodeList[node.children[0]]) is types.Threat:
                parentType = 'threat'
            else:
                parentType = 'default'
        else:
            parentType = 'default'
        super().__init__(node, parent, Configuration.colors[parentType][node.conjunctionType]['background'],
                         Configuration.colors[parentType][node.conjunctionType]['border'],
                         Configuration.colors[parentType][node.conjunctionType]['font'], x, y, 60)
        self.conjunctionRect = ConjunctionRect()
        self.conjunctionRect.setPen(QPen(QColor(Configuration.colors[parentType][node.conjunctionType]['border']), 2))
        self.conjunctionRect.setBrush(
            QBrush(QColor(Configuration.colors[parentType][node.conjunctionType]['background'])))
        self.conjunctionRect.setRect(self.x() - 20, self.y() + 1, 240, self.headerHeight - 2)
        self.conjunctionRect.setZValue(-1)
        self.addToGroup(self.conjunctionRect)

    def redraw(self):
        """
        Redraws the node with the colors set in the options menu
        """
        if len(self.node.children) > 0:
            if self.parent.tree.getTypeRecursiveDown(
                    self.parent.tree.nodeList[self.node.children[0]]) is types.Countermeasure:
                parentType = 'countermeasure'
            elif self.parent.tree.getTypeRecursiveDown(
                    self.parent.tree.nodeList[self.node.children[0]]) is types.Threat:
                parentType = 'threat'
            else:
                parentType = 'default'
        else:
            parentType = 'default'
        self.removeFromGroup(self.conjunctionRect)
        self.parent.scene.removeItem(self.conjunctionRect)
        super().redrawOptions(Configuration.colors[parentType][self.node.conjunctionType]['background'],
                              Configuration.colors[parentType][self.node.conjunctionType]['border'],
                              Configuration.colors[parentType][self.node.conjunctionType]['font'])
        """
        Prints the rounded corners around the node
        """
        self.conjunctionRect = ConjunctionRect()
        self.conjunctionRect.setPen(
            QPen(QColor(Configuration.colors[parentType][self.node.conjunctionType]['border']), 2))
        self.conjunctionRect.setBrush(
            QBrush(QColor(Configuration.colors[parentType][self.node.conjunctionType]['background'])))
        self.conjunctionRect.setRect(self.x() - 20, self.y() + 1, 240, self.headerHeight - 2)
        self.conjunctionRect.setZValue(-1)
        self.addToGroup(self.conjunctionRect)

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

        if options.state & QStyle.State_Selected:
            painter.setPen(QPen(Qt.black, 2, Qt.DotLine))
            rect = QRect(self.boundingRect().x() - 1.5, self.boundingRect().y() - 1.5,
                         self.boundingRect().x() + self.boundingRect().width() + 23.5,
                         self.boundingRect().y() + self.boundingRect().height() + 3.5)
            painter.drawRect(rect)

        super().paint(painter, myOption, widget=None)

    def edit(self):
        """
        Opens the edit dialog for conjunction to change the conjunction type
        """
        ConjunctionEdit(self, self.parent).exec()


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
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        painter.setPen(self.pen())
        painter.setBrush(self.brush())

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
        @param dst: End object of the arrow
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

        self.updatePosition()

    def boundingRect(self):
        """
        New calculation of the bounding rect, because the arrow is not only a line

        @return: new bounding rectangle
        """
        extra = (self.pen().width() + 20) / 2.0
        return QRectF(self.line().p1(), QSizeF(self.line().p2().x() - self.line().p1().x(),
                                               self.line().p2().y() - self.line().p1().y())).normalized().adjusted(
            -extra, -extra, extra, extra)

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
        """
        Calculation for the line
        """
        centerLine = QLineF(QPointF(self.start.x() + self.start.boundingRect().center().x() + self.offset,
                                    self.start.y() + self.start.boundingRect().bottom()),
                            QPointF(self.dst.x() + self.dst.boundingRect().center().x(), self.dst.y()))
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

        self.setLine(QLineF(intersectPoint,
                            QPointF(self.start.x() + self.start.boundingRect().center().x() + self.offset,
                                    self.start.y() + self.start.boundingRect().bottom())))

        """
        Calculation for the arrow
        It calculates an left and an right part of the arrow
        """
        angle = math.atan2(-self.line().dy(), self.line().dx())
        arrowP1 = self.line().p1() + QPointF(math.sin(angle + math.pi / 3) * arrowSize,
                                             math.cos(angle + math.pi / 3) * arrowSize)
        arrowP2 = self.line().p1() + QPointF(math.sin(angle + math.pi - math.pi / 3) * arrowSize,
                                             math.cos(angle + math.pi - math.pi / 3) * arrowSize)

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

    def selectChildren(self):
        """
        Select all children of the destination
        """
        self.dst.selectChildren()


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

        n = Conjunction(node, self.parent(), x=self.mousePos[0], y=self.mousePos[1])
        self.addItem(n)

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
            if self.parent().mode == 1:
                """
                Mode 1: Insert threat node
                """
                self.parent().addLastAction()

                node = types.Threat()
                self.parent().tree.addNode(node)
                n = Threat(node, self.parent(), mouseEvent.scenePos().x(), mouseEvent.scenePos().y())
                self.addItem(n)

                edit = NodeEdit(n, n.parent)
                edit.exec()

                self.parent().saved = False
                self.reset()
                super().mousePressEvent(mouseEvent)
            elif self.parent().mode == 2:
                """
                Mode 2: Insert countermeasure node
                """
                self.parent().addLastAction()

                node = types.Countermeasure()
                self.parent().tree.addNode(node)
                n = Countermeasure(node, self.parent(), mouseEvent.scenePos().x(), mouseEvent.scenePos().y())
                self.addItem(n)
                self.parent().saved = False

                edit = NodeEdit(n, n.parent)
                edit.exec()

                super().mousePressEvent(mouseEvent)
                self.reset()

            elif self.parent().mode == 3:
                """
                Mode 3: Insert conjunction node
                Displays an popup menu
                """
                self.mousePos = mouseEvent.scenePos().x(), mouseEvent.scenePos().y()
                self.menu.popup(
                    self.parent().mapToGlobal(self.parent().graphicsView.mapFromScene(mouseEvent.scenePos())), None)
                super().mousePressEvent(mouseEvent)
                self.reset()
            elif self.parent().mode == 4:
                """
                Mode 4: Insert line
                Start node of the line is set here
                """
                self.startCollisions = self.itemAt(mouseEvent.scenePos(), QTransform())
                self.insertLine = QGraphicsLineItem(QLineF(mouseEvent.scenePos(), mouseEvent.scenePos()))
                self.insertLine.setPen(QPen(Qt.black, 2))
                self.addItem(self.insertLine)
            elif self.parent().mode == 6:
                """
                Mode 6: Insert copy buffer
                """
                self.parent().insertCopyBuffer(mouseEvent.scenePos().x(), mouseEvent.scenePos().y())
                self.reset()
            else:
                super().mousePressEvent(mouseEvent)
        elif mouseEvent != Qt.RightButton:
            self.reset()
            super().mousePressEvent(mouseEvent)

    def contextMenuEvent(self, event):
        """
        Handles the event to open a context menu on a node
        The event will open a context menu to edit the node

        @param event: context menu Event
        """
        try:
            if len(self.selectedItems()) > 0:
                menu = QMenu(self.parent())
                menu.addAction('Delete', self.deleteSelected)
                menu.addAction('Select Children', self.selectNodesChildren)
                menu.addAction('Copy', self.parent().copy)
                menu.addAction('Cut', self.parent().cut)

                menu.popup(event.screenPos(), None)
            elif self.itemAt(event.scenePos(), QTransform()) is not None:
                item = self.itemAt(event.scenePos(), QTransform())
                item.setSelected(True)
                menu = QMenu(self.parent())

                if isinstance(item.parentItem(), Node):
                    item = item.parentItem()
                    menu.addAction('Edit', item.edit)
                    menu.addAction('Delete', item.delete)
                    menu.addAction('Select Children', item.selectChildren)
                    menu.addAction('Copy', self.parent().copy)
                    menu.addAction('Cut', self.parent().cut)
                elif isinstance(item.parentItem(), QGraphicsItemGroup) and isinstance(item.parentItem().parentItem(),
                                                                                      Node):
                    item = item.parentItem().parentItem()
                    menu.addAction('Edit', item.edit)
                    menu.addAction('Delete', item.delete)
                    menu.addAction('Select Children', item.selectChildren)
                    menu.addAction('Copy', self.parent().copy)
                    menu.addAction('Cut', self.parent().cut)
                elif isinstance(item, Edge):
                    menu.addAction('Delete', functools.partial(self.deleteEdge, item))
                    menu.addAction('Select Children', item.selectChildren)
                else:
                    menu.popup(event.screenPos(), None)
            else:
                menu = QMenu(self.parent())
                menu.addAction('Paste', functools.partial(self.parent().insertCopyBuffer, event.scenePos().x(),
                                                          event.scenePos().y()))
                menu.popup(event.screenPos(), None)

        except Exception as e:
            print(traceback.format_exc())

    def deleteEdge(self, edge):
        """
        Deletes an edge
        @param edge: Edge to delete
        """
        self.removeItem(edge)
        edge.start.childEdges.remove(edge)
        edge.dst.parentEdges.remove(edge)
        self.parent().tree.removeEdge(edge.start.node.id + '-' + edge.dst.node.id)

    def deleteSelected(self):
        """
        Deletes an selection
        """
        self.parent().addLastAction()
        deleted = []
        for i in self.selectedItems():
            if i not in deleted:
                if isinstance(i, Node):
                    deleted.append(i)
                    i.delete()
                elif isinstance(i, Edge):
                    deleted.append(i)
                    if not (i.start in deleted or i.dst in deleted):
                        self.removeItem(i)
                        i.start.childEdges.remove(i)
                        i.dst.parentEdges.remove(i)
                        self.parent().tree.removeEdge(i.start.node.id + '-' + i.dst.node.id)

    def selectNodesChildren(self):
        """
        Selects all children of the selection
        """
        for i in self.selectedItems():
            i.selectChildren()

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
                """
                Mode 4: Insert edge
                Inserts the edge
                """
                self.parent().addLastAction()
                self.insertLine.setZValue(-1)
                self.dstCollisions = self.itemAt(mouseEvent.scenePos(), QTransform())
                if self.startCollisions is None or self.dstCollisions is None \
                        or self.startCollisions == self.dstCollisions:
                    self.reset()
                    super().mouseReleaseEvent(mouseEvent)
                    return
                if isinstance(self.startCollisions.parentItem(), Node):
                    """
                    Gets the start node view object
                    """
                    self.startCollisions = self.startCollisions.parentItem()
                elif isinstance(self.startCollisions.parentItem(), QGraphicsItemGroup) \
                        and isinstance(self.startCollisions.parentItem().parentItem(), Node):
                    """
                    Gets the start node view object if the user clicks on the text in the item
                    """
                    self.startCollisions = self.startCollisions.parentItem().parentItem()
                else:
                    self.reset()
                    super().mouseReleaseEvent(mouseEvent)
                    return
                if isinstance(self.dstCollisions.parentItem(), Node):
                    """
                    Gets the destination node view object
                    """
                    self.dstCollisions = self.dstCollisions.parentItem()
                elif isinstance(self.dstCollisions.parentItem(), QGraphicsItemGroup) \
                        and isinstance(self.dstCollisions.parentItem().parentItem(), Node):
                    """
                    Gets the destination node view object if the user clicks on the text in the item
                    """
                    self.dstCollisions = self.dstCollisions.parentItem().parentItem()
                else:
                    self.reset()
                    super().mouseReleaseEvent(mouseEvent)
                    return
                if self.parent().tree.addEdge(self.startCollisions.node.id, self.dstCollisions.node.id) is True:
                    self.startCollisions.addEdge(self.dstCollisions)
                    if isinstance(self.startCollisions, Conjunction):
                        self.startCollisions.fixParentEdgeRec()
                        self.startCollisions.redraw()
                    self.reset()
                    self.parent().saved = False
                else:
                    MessageBox('Adding Edge is not possible', 'The Edge is not supported',
                               icon=QMessageBox.Critical).run()
                    self.reset()
            elif self.parent().mode == 5:
                """
                Mode 4: Deletes selected items
                Deletes all selected items plus edges from on to the selection
                """
                self.deleteSelected()
                self.reset()
                self.parent().saved = False
            else:
                self.reset()
        super().mouseReleaseEvent(mouseEvent)

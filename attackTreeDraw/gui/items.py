import math
import traceback

import sys
from PyQt5.QtCore import Qt, QRectF, QSizeF, QLineF, QPointF, QRect

from PyQt5.QtGui import QBrush, QFont, QPen, QPolygonF, QTransform
from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsItem, QGraphicsTextItem, QGraphicsRectItem, QGraphicsLineItem, QStyleOptionGraphicsItem, QStyle, QGraphicsScene, QMenu, QGraphicsView, QMessageBox

from .windows import NodeEdit, MessageBox

from data import types


class Node(QGraphicsItemGroup):

    def __init__(self, node, parent, background, border, text, x=0, y=0, offset=20):
        super().__init__()

        self.typeOffset = offset

        self.node = node

        self.parent = parent

        self.edit = None

        self.threatConjunction = None
        self.counterConjunction = None

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

    def printHeader(self, background, border, text):
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
        y = self.y() + self.headerHeight
        x = self.x()

        self.attributesHeight = 0

        for k, v in self.node.attributes.items():
            key = QGraphicsTextItem()
            key.setFont(QFont('Arial', 10))
            key.setTextWidth(100)
            key.setPlainText(k)
            keyHeight = int(key.boundingRect().height() / 20 + 0.5) * 20

            value = QGraphicsTextItem()
            value.setFont(QFont('Arial', 10))
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
        self.redrawOptions(Qt.white, Qt.black, Qt.black)

    def printFooter(self, background, border, text):
        pass

    def paint(self, painter, options, widget=None):
        myOption = QStyleOptionGraphicsItem(options)
        myOption.state &= ~QStyle.State_Selected

        super().paint(painter, myOption, widget=None)

        if self.isSelected():
            painter.setPen(QPen(Qt.black, 1, Qt.DashLine))
            rect = QRect(self.boundingRect().x() - 2, self.boundingRect().y() - 2, self.boundingRect().x() + self.boundingRect().width() + 4, self.boundingRect().y() + self.boundingRect().height() + 3)
            painter.drawRect(rect)

    def mouseDoubleClickEvent(self, event):
        self.edit = NodeEdit(self, self.parent)


class Threat(Node):

    def __init__(self, node, parent, x=0, y=0):
        self.threatBox = None
        self.counterBox = None

        self.threatBoxText = None
        self.counterBoxText = None

        super().__init__(node, parent, parent.threatBackground, parent.threatBorder, parent.threatFont, x, y, 91)

    def printFooter(self, background, border, text):
        self.threatBoxText = QGraphicsTextItem()
        self.threatBoxText.setFont(QFont('Arial', 10))
        self.threatBoxText.setPlainText('T')

        self.counterBoxText = QGraphicsTextItem()
        self.counterBoxText.setFont(QFont('Arial', 10))
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
        super().redrawOptions(self.parent.threatBackground, self.parent.threatBorder, self.parent.threatFont)


class Countermeasure(Node):
    def __init__(self, node, parent, x=0, y=0):
        super().__init__(node, parent, parent.countermeasureBackground, parent.countermeasureBorder, parent.countermeasureFont, x, y, 63)

        print(parent.countermeasureBackground)

    def printFooter(self, background, border, text):
        pass

    def redraw(self):
        super().redrawOptions(self.parent.countermeasureBackground, self.parent.countermeasureBorder, self.parent.countermeasureFont)


class Conjunction(QGraphicsItemGroup):
    def __init__(self, parent, conjType, childType, offset=0):
        super().__init__()

        self.parent = parent

        self.offset = offset

        self.parentArrow = None
        self.conjType = conjType

        self.children = []
        self.arrows = []

        self.title = QGraphicsTextItem()
        self.title.setFont(QFont('Arial', 12))
        self.title.setPlainText(conjType)

        self.conRect = ConjunctionRect()
        self.conRect.setRect(0, 0, 100, 40)
        self.title.setPos(6, 6)

        self.childType = childType

        if self.childType == 1:
            self.background = self.parent.parent.threatBackground
            self.border = self.parent.parent.threatBorder
            self.font = self.parent.parent.threatFont
        else:
            self.background = self.parent.parent.countermeasureBackground
            self.border = self.parent.parent.countermeasureBorder
            self.font = self.parent.parent.countermeasureFont

        self.addToGroup(self.conRect)
        self.addToGroup(self.title)

        self.conRect.setBrush(QBrush(self.background))
        self.conRect.setPen(QPen(self.border))

        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

    def addArrow(self, child):
        self.arrows.append(Arrow(self, child, 0, self.border))
        self.children.append(child)

        child.parentConjunctions.append(self)

        return self.arrows[-1]

    def addParentArrow(self):
        self.parentArrow = Arrow(self.parent, self, self.offset, self.border)
        return self.parentArrow

    def paint(self, painter, options, widget=None):

        myOption = QStyleOptionGraphicsItem(options)
        myOption.state &= ~QStyle.State_Selected

        super().paint(painter, myOption, widget=None)

        if self.isSelected():
            painter.setPen(QPen(Qt.black, 1, Qt.DashLine))
            rect = QRect(self.boundingRect().x() - 2, self.boundingRect().y() - 2, self.boundingRect().x() + self.boundingRect().width() + 4, self.boundingRect().y() + self.boundingRect().height() + 3)
            painter.drawRect(rect)

    def redraw(self):

        if self.childType == 1:
            self.background = self.parent.parent.threatBackground
            self.border = self.parent.parent.threatBorder
            self.font = self.parent.parent.threatFont
        else:
            self.background = self.parent.parent.countermeasureBackground
            self.border = self.parent.parent.countermeasureBorder
            self.font = self.parent.parent.countermeasureFont

        self.conRect.setBrush(QBrush(self.background))
        self.conRect.setPen(QPen(self.border))

        self.conRect.update()
        self.parentArrow.setPen(QPen(self.border, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

        self.parentArrow.update()
        for a in self.arrows:
            a.setPen(QPen(self.border, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            a.update()


class ConjunctionRect(QGraphicsRectItem):
    def paint(self, painter, options, widget=None):

        if self.isSelected():
            painter.setPen(QPen(Qt.black, 1, Qt.DashLine))
            rect = QRect(self.boundingRect().x() - 2, self.boundingRect().y() - 2, self.boundingRect().x() + self.boundingRect().width() + 4, self.boundingRect().y() + self.boundingRect().height() + 3)
            painter.drawRect(rect)

        painter.setBrush(self.brush())
        painter.setPen(self.pen())

        painter.drawRoundedRect(self.boundingRect(), 20, 20)


class Arrow(QGraphicsLineItem):
    def __init__(self, start, end, offset, color=Qt.black):
        super().__init__()

        self.arrowHead = QPolygonF()

        self.start = start
        self.end = end

        self.offset = offset

        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

        self.setPen(QPen(color, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

    def boundingRect(self):
        extra = (self.pen().width() + 20) / 2.0

        return QRectF(self.line().p1(), QSizeF(self.line().p2().x() - self.line().p1().x(), self.line().p2().y() - self.line().p1().y())).normalized().adjusted(-extra, -extra, extra, extra)

    def shape(self):
        path = QGraphicsLineItem.shape(self)
        path.addPolygon(self.arrowHead)
        return path

    def updatePosition(self):
        line = QLineF(self.mapFromItem(self.start, 0, 0), self.mapFromItem(self.end, 0, 0))
        self.setLine(line)

    def paint(self, painter, options, widget=None):

        if self.start.collidesWithItem(self.end):
            return

        myPen = self.pen()
        arrowSize = 10
        painter.setPen(myPen)
        painter.setBrush(myPen.color())

        centerLine = QLineF(QPointF(self.start.x() + self.start.boundingRect().center().x() + self.offset, self.start.y() + self.start.boundingRect().bottom()), QPointF(self.end.x() + self.end.boundingRect().center().x(), self.end.y()))
        endPolygon = self.end.mapFromItem(self.end, self.end.boundingRect())
        p1 = endPolygon.first() + self.end.pos()
        p2 = None
        intersectPoint = QPointF()

        for i in endPolygon:
            p2 = i + self.end.pos()

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

    def __init__(self, parent=None):
        super().__init__(parent)
        self.startCollisions = None
        self.endCollisions = None
        self.conjunction = None

        self.menu = QMenu(parent)

        self.menu.addAction('Alternative', self.addAlternative)
        self.menu.addAction('Composition', self.addComposition)
        self.menu.addAction('Sequence', self.addSequence)
        self.menu.addAction('Threshold', self.addThreshold)

    def addAlternative(self):
        self.addEdge('alternative')

    def addComposition(self):
        self.addEdge('composition')

    def addSequence(self):
        self.addEdge('sequence')

    def addThreshold(self):
        self.addEdge('threshold')

    def addEdge(self, type):
        if self.endCollisions.node.type == 'countermeasure':
            if self.startCollisions.node.type == 'threat':
                self.startCollisions.counterConjunction = Conjunction(self.startCollisions, type, 0, 50)
            else:
                self.startCollisions.counterConjunction = Conjunction(self.startCollisions, type, 0)

            self.addItem(self.startCollisions.counterConjunction)
            self.addItem(self.startCollisions.counterConjunction.addParentArrow())
            self.startCollisions.counterConjunction.setPos(self.startCollisions.x() + self.startCollisions.boundingRect().center().x() - 100, self.startCollisions.y() + self.startCollisions.boundingRect().height() + 100)
            self.addItem(self.startCollisions.counterConjunction.addArrow(self.endCollisions))

            self.startCollisions.counterConjunction.setPos(self.startCollisions.counterConjunction.x() + 100, self.startCollisions.counterConjunction.y())
        else:
            if self.startCollisions.node.type == 'threat':
                self.startCollisions.threatConjunction = Conjunction(self.startCollisions, type, 1, -50)
            else:
                self.startCollisions.threatConjunction = Conjunction(self.startCollisions, type, 1)

            self.addItem(self.startCollisions.threatConjunction)
            self.addItem(self.startCollisions.threatConjunction.addParentArrow())
            self.startCollisions.threatConjunction.setPos(self.startCollisions.x() + self.startCollisions.boundingRect().center().x() - 100, self.startCollisions.y() + self.startCollisions.boundingRect().height() + 100)
            self.addItem(self.startCollisions.threatConjunction.addArrow(self.endCollisions))

        self.parent().tree.addEdge(self.startCollisions.node.id, self.endCollisions.node.id, type)
        self.parent().graphicsView.update()
        self.reset()
        self.parent().saved = False

    def reset(self):
        self.startCollisions = None
        self.endCollisions = None
        self.conjunction = None
        self.parent().mode = 0
        self.parent().setCursor(Qt.ArrowCursor)
        self.parent().graphicsView.setDragMode(QGraphicsView.RubberBandDrag)

    def mousePressEvent(self, mouseEvent):
        if mouseEvent.button() == Qt.LeftButton:
            try:
                if self.parent().mode == 1:
                    self.parent().addLastAction()

                    node = types.Threat()
                    self.parent().tree.addNode(node)
                    n = Threat(node, self.parent(), mouseEvent.scenePos().x(), mouseEvent.scenePos().y())
                    self.addItem(n)

                    self.parent().graphicsView.update()

                    self.parent().saved = False
                    super().mousePressEvent(mouseEvent)
                elif self.parent().mode == 2:
                    self.parent().addLastAction()

                    node = types.Countermeasure()
                    self.parent().tree.addNode(node)
                    n = Countermeasure(node, self.parent(), mouseEvent.scenePos().x(), mouseEvent.scenePos().y())
                    self.addItem(n)
                    self.parent().graphicsView.update()
                    self.parent().saved = False

                    super().mousePressEvent(mouseEvent)
                elif self.parent().mode == 3:

                    self.startCollisions = self.itemAt(mouseEvent.scenePos(), QTransform())
                    self.parent().addLastAction()
                else:
                    super().mousePressEvent(mouseEvent)
            except Exception as e:
                print(traceback.format_exc())
                exit(-1)

    def mouseMoveEvent(self, mouseEvent):
        super().mouseMoveEvent(mouseEvent)

    def mouseReleaseEvent(self, mouseEvent):
        if mouseEvent.button() == Qt.LeftButton:
            if self.parent().mode == 3:
                self.parent().addLastAction()
                try:
                    self.endCollisions = self.itemAt(mouseEvent.scenePos(), QTransform())
                    if self.startCollisions is None or self.endCollisions is None or self.startCollisions == self.endCollisions:
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
                    if isinstance(self.endCollisions.parentItem(), Node):
                        self.endCollisions = self.endCollisions.parentItem()
                    elif isinstance(self.endCollisions.parentItem(), QGraphicsItemGroup) and isinstance(self.endCollisions.parentItem().parentItem(), Node):
                        self.endCollisions = self.endCollisions.parentItem().parentItem()
                    else:
                        self.reset()
                        super().mouseReleaseEvent(mouseEvent)
                        return
                    if isinstance(self.endCollisions, Node) and isinstance(self.startCollisions, Node):
                        if (self.startCollisions.node.type == 'threat' and self.endCollisions.node.type == 'countermeasure') \
                                or (self.startCollisions.node.type == 'countermeasure' and self.endCollisions.node.type == 'countermeasure'):
                            self.conjunction = self.startCollisions.counterConjunction
                        elif (self.startCollisions.node.type == 'threat' and self.endCollisions.node.type == 'countermeasure') \
                                or (self.startCollisions.node.type == 'threat' and self.endCollisions.node.type == 'threat'):
                            self.conjunction = self.startCollisions.threatConjunction
                        else:
                            MessageBox('Adding Edge is not possible', 'Edge from Countermeasure to Threat not possible', icon=QMessageBox.Critical).run()
                            return
                        if self.conjunction is None:
                            self.menu.popup(self.parent().mapToGlobal(self.parent().graphicsView.mapFromScene(mouseEvent.scenePos())), None)
                        else:
                            self.parent().tree.addEdge(self.startCollisions.node.id, self.endCollisions.node.id)
                            self.addItem(self.conjunction.addArrow(self.endCollisions))

                            self.parent().graphicsView.update()
                            self.reset()
                            self.parent().saved = False

                except Exception:
                    print(traceback.format_exc())
                    exit(-1)

            elif self.parent().mode == 4:  # @TODO: Rework
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
                                        children =c.children.copy()
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

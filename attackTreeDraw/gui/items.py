import math
from PyQt5.QtCore import Qt, QRectF, QSizeF, QLineF, QPointF, QRect

from PyQt5.QtGui import QBrush, QFontMetrics, QFont, QPen, QPolygonF
from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsItem, QGraphicsTextItem, QGraphicsRectItem, QGraphicsLineItem, QStyleOptionGraphicsItem, QStyle


class Node(QGraphicsItemGroup):  # QGraphicsItemGroup as parent?
    def __init__(self, node):
        super().__init__()

        self.node = node

        self.attributes = QGraphicsItemGroup()

        self.title = QGraphicsTextItem()
        self.title.setFont(QFont('Arial'))
        self.title.setTextWidth(200)  # @TODO: change to variable width
        self.title.setPlainText(node.title)

        titleHeight = int(self.title.boundingRect().height()/20 + 0.5) * 20

        self.typeRect = QGraphicsRectItem()
        self.typeRect.setRect(0, 0, 200, 20)
        self.titleRect = QGraphicsRectItem()
        self.titleRect.setRect(0, 20, 200, titleHeight)  # @TODO: add more height if text is broken

        self.title.setPos(0, 20)

        self.titleRect.setBrush(QBrush(Qt.white))
        self.typeRect.setBrush(QBrush(Qt.white))

        self.addToGroup(self.typeRect)
        self.addToGroup(self.titleRect)
        self.addToGroup(self.title)

        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

        self.headerHeight = titleHeight + 20

    def setPosition(self, x, y):
        self.setX(x)
        self.setY(y)

    def printAttributes(self):

        y = self.headerHeight

        for k, v in self.node.attributes.items():
            key = QGraphicsTextItem()
            key.setFont(QFont('Arial'))
            key.setTextWidth(100)  # @TODO: change to variable width
            key.setPlainText(k)
            keyHeight = int(key.boundingRect().height() / 20 + 0.5) * 20

            value = QGraphicsTextItem()
            value.setFont(QFont('Arial'))
            value.setTextWidth(100)  # @TODO: change to variable width
            value.setPlainText(v)
            valueHeight = int(key.boundingRect().height() / 20 + 0.5) * 20

            height = valueHeight if valueHeight > keyHeight else keyHeight

            keyRect = QGraphicsRectItem()
            keyRect.setRect(0, y, 100, height)
            valueRect = QGraphicsRectItem()
            valueRect.setRect(100, y, 100, height)

            key.setPos(0, y)
            value.setPos(100, y)

            self.attributes.addToGroup(keyRect)
            self.attributes.addToGroup(valueRect)
            self.attributes.addToGroup(key)
            self.attributes.addToGroup(value)

            y = y + height

        self.addToGroup(self.attributes)

    def paint(self, painter, options, widget=None):

        myOption = QStyleOptionGraphicsItem(options)
        myOption.state &= ~QStyle.State_Selected

        super().paint(painter, myOption, widget=None)

        if self.isSelected():
            painter.setPen(QPen(Qt.black, 1, Qt.DashLine))
            rect = QRect(self.boundingRect().x() - 2, self.boundingRect().y() - 2, self.boundingRect().x() + self.boundingRect().width() + 4, self.boundingRect().y() + self.boundingRect().height() + 3)
            painter.drawRect(rect)


class Threat(Node):
    def __init__(self, node):
        super().__init__(node)

        self.type = QGraphicsTextItem()
        self.type.setFont(QFont('Arial'))
        self.type.setPlainText(node.type)

        self.type.setPos(81, 0)
        self.addToGroup(self.type)

        self.printAttributes()


class Countermeasure(Node):
    def __init__(self, node):
        super().__init__(node)

        self.type = QGraphicsTextItem()
        self.type.setFont(QFont('Arial'))
        self.type.setPlainText(node.type)

        self.type.setPos(53, 0)
        self.addToGroup(self.type)

        self.printAttributes()


class Conjunction(Node):
    pass


class Arrow(QGraphicsLineItem):

    def __init__(self, start, end):
        super().__init__()

        self.arrowHead = QPolygonF()

        self.start = start
        self.end = end

        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

        self.setPen(QPen(Qt.black, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

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
        myPen.setColor(Qt.black)
        arrowSize = 10
        painter.setPen(myPen)
        painter.setBrush(Qt.black)

        centerLine = QLineF(QPointF(self.start.x()+self.start.boundingRect().center().x(), self.start.y() + self.start.boundingRect().bottom()), QPointF(self.end.x()+self.end.boundingRect().center().x(), self.end.y()))
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

        self.setLine(QLineF(intersectPoint, QPointF(self.start.x()+self.start.boundingRect().center().x(), self.start.y() + self.start.boundingRect().bottom())))

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

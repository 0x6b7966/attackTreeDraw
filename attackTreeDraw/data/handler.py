from PyQt5.QtCore import Qt

from .exceptions import ParserError
from .types import *
from .parsers import parseExtendedConnection, parseExtendedNode, parseSimpleNode
from fileHandler.xml import Handler as XmlHandler


class TreeHandler:

    @staticmethod
    def buildFromXML(file):
        xmlHandler = XmlHandler()
        if xmlHandler.loadFile(file) is False:
            raise ParserError('Root Element with ID %s not found in node list')
        tree = Tree(xmlHandler.extended)
        meta = xmlHandler.xml.find('meta')
        for m in meta.iterchildren():
            tree.meta[m.tag] = m.text
        if xmlHandler.extended is False:
            xTree = xmlHandler.xml.find('tree')
            root = parseSimpleNode(tree, xTree[0])
            root.isRoot = True
        elif xmlHandler.extended is True:
            threats = xmlHandler.xml.find('threats')
            for t in threats.iterchildren():
                parseExtendedNode(tree, t)
            countermeasures = xmlHandler.xml.find('countermeasures')
            for c in countermeasures.iterchildren():
                parseExtendedNode(tree, c)
            connections = xmlHandler.xml.find('connections')
            for c in connections.iterchildren():
                parseExtendedConnection(tree, c)
            tree.root = meta.find('root').text
            if tree.root in tree.nodeList.keys():
                tree.nodeList[tree.root].isRoot = True
            else:
                raise ParserError('Root Element with ID %s not found in node list' % tree.root)
        else:
            return None
        return tree

    @staticmethod
    def saveToXML(tree, file):
        # @TODO implement checks
        xmlHandler = XmlHandler()
        xmlHandler.generateTree(tree)
        return xmlHandler.saveToFile(file)


class ConfigHandler:
    threatBackgroundColor = Qt.white
    threatTextColor = Qt.black
    threatBorderColor = Qt.black
    countermeasureBackgroundColor = Qt.white
    countermeasureTextColor = Qt.black
    countermeasureBorderColor = Qt.black

    @staticmethod
    def loadConfig():
        pass

    @staticmethod
    def saveConfig():
        pass

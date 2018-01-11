from .exceptions import ParserError
from .types import *
from .parsers import parseExtendedConnection, parseExtendedNode, parseSimpleNode
from ..fileHandler.xml import Handler as XmlHandler


class Handler:

    def buildFromXML(self, file):
        xmlHandler = XmlHandler()
        xmlHandler.loadFile(file)
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

    def saveToXML(self, tree, file):
        # @TODO implement checks
        xmlHandler = XmlHandler()
        xmlHandler.generateTree(tree)
        xmlHandler.saveToFile(file)
        return True  # @TODO: check if file is saved

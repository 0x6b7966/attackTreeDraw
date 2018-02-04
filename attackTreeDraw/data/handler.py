from PyQt5.QtCore import Qt

from .exceptions import ParserError
from .types import *
from fileHandler.xml import Handler as XmlHandler


class TreeHandler:
    """
    This Class handles loading and saving for the tree
    """

    @staticmethod
    def buildFromXML(file):
        """
        Generates a Class which represents the tree in the given xml file

        @param file: File to load the tree from
        @return: data.Tree or None if format is not correct
        @raise ParserError if loading fails
        """
        xmlHandler = XmlHandler()
        if xmlHandler.loadFile(file) is False:
            raise ParserError(('Can\'t load %s, check dir. Abort' % file))
        tree = Tree(xmlHandler.extended)
        meta = xmlHandler.xml.find('meta')
        for m in meta.iterchildren():
            tree.meta[m.tag] = m.text
        if xmlHandler.extended is False:
            xTree = xmlHandler.xml.find('tree')
            root = Parsers.parseSimpleNode(tree, xTree[0])
            root.isRoot = True
        elif xmlHandler.extended is True:
            threats = xmlHandler.xml.find('threats')
            for t in threats.iterchildren():
                Parsers.parseExtendedNode(tree, t)
            countermeasures = xmlHandler.xml.find('countermeasures')
            for c in countermeasures.iterchildren():
                Parsers.parseExtendedNode(tree, c)
            connections = xmlHandler.xml.find('connections')
            for c in connections.iterchildren():
                Parsers.parseExtendedConnection(tree, c)
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
        """
        Saves a given tree to a file

        @param tree: Tree to save to file
        @param file: File to save to
        @return: True if saving was successfully else returns exception
        """
        # @TODO implement checks
        xmlHandler = XmlHandler()
        xmlHandler.generateTree(tree)
        return xmlHandler.saveToFile(file)


class Parsers:
    """
    This Class contains parsers for the xml items
    """

    @staticmethod
    def parseExtendedConnection(tree, edge):
        """
        Parses a edge from a xml file

        @param tree: Tree to save generated files in
        @param edge: Edge to parse
        @raise ParserError: if edge can't be parsed
        """
        if edge.get('source') in tree.nodeList.keys():
            source = edge.get('source')
            for dst in edge.iterchildren(tag='destination'):
                if dst.text in tree.nodeList.keys():
                    fail = False
                    for c in tree.edgeList:
                        if (source, dst.text) == c:
                            # print(('Edge %s to %s already exists' % source, dst.text), file=sys.stderr)
                            fail = True
                            break
                    if fail is not True and source is not None:
                        tree.addEdge(source, dst.text, edge.get('type'))
                else:
                    raise ParserError('Destination node %s does not exist' % dst.text)
        else:
            raise ParserError('Source node %s does not exist' % edge.get('source'))

    @staticmethod
    def parseNode(node):
        """
        Parses a node and returns it

        @param node: Node to parse
        @return: Parsed node
        """
        if node.tag == 'threat':
            n = Threat()
            n.id = node.get('id')
        elif node.tag == 'countermeasure':
            n = Countermeasure()
            n.id = node.get('id')
        else:
            raise ParserError('Parsing failed for element %s' % node.tag)

        for a in node.findall('attribute'):
            n.attributes[a.get('key')] = a.text
        n.title = node.find('title').text
        n.description = node.find('description').text

        return n

    @staticmethod
    def parseExtendedNode(tree, node):
        """
        Parses a extended node and adds it to a tree

        @param tree: Tree to add the node to
        @param node: Node to parse
        @return: Parsed node
        """
        n = Parsers.parseNode(node)

        check = tree.addNode(n)
        if check is False:
            raise ParserError('Can\'t add node %s. NodeID exists' % n.id)
        if n is None:
            raise ParserError('Can\'t add node %s.' % n.id)
        return n

    @staticmethod
    def parseSimpleNode(tree, node, parent=None):
        """
        Parses a simple node and adds it to a tree

        @param tree: Tree to add the node to
        @param node: Node to parse
        @param parent: paren from node
        @return: Parsed node
        """
        n = Parsers.parseNode(node)

        if parent is None:
            n.isRoot = True
            tree.root = n.id
        check = tree.addNode(n)

        if node.find('subtree') is not None:
            conjunction = node.find('subtree')[0].tag
            for subNode in node.find('subtree')[0].iterchildren():
                subN = Parsers.parseSimpleNode(tree, subNode, n.id)
                if subN is not None:
                    tree.addEdge(n.id, subN.id, conjunction)

        if node.find('countermeasures') is not None:
            conjunction = node.find('countermeasures')[0].tag
            for subNode in node.find('countermeasures')[0].iterchildren():
                subN = Parsers.parseSimpleNode(tree, subNode, n.id)
                if subN is not None:
                    if not tree.addEdge(n.id, subN.id, conjunction):
                        raise ParserError('Cant\'t add Edge %s to %s with %s' % (n.id, subN.id, conjunction))

        if check is False:
            raise ParserError('Can\'t add node %s. NodeID exists' % n.id)
        if n is None:
            raise ParserError('Can\'t add node %s.' % n.id)
        return n


class ConfigHandler:
    # @TODO: Remove or implement
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

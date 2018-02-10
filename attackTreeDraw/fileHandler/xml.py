import os
from lxml import etree

from data.exceptions import XMLXSDError


class Handler:
    """
    This class Handles all needed actions to save and load xml files
    """

    def __init__(self):
        """
        Constructor for Handler

        The Constructor initialises the xml parser and xsd files
        """
        self.parser = etree.XMLParser(dtd_validation=True)
        self.xml = None
        self.extended = False

        includePath = os.path.dirname(os.path.abspath(__file__))

        try:
            self.simpleXSD = etree.XMLSchema(etree.parse(os.path.join(includePath, '../../doc/xml/attackTreeSimple.xsd')))  # @TODO: change path
        except OSError:
            raise XMLXSDError('Can\'t load attackTreeSimple.xsd, check installation')
        try:
            self.extendedXSD = etree.XMLSchema(etree.parse(os.path.join(includePath, '../../doc/xml/attackTreeExtended.xsd')))  # @TODO: change path
        except OSError:
            raise XMLXSDError('Can\'t load attackTreeExtended.xsd, check installation')

    def loadFile(self, file):
        """
        Loads a given file and validates it against the xsd files

        @param file: a file to load from
        @return: True if file is valid, else False
        """
        try:
            self.xml = etree.parse(file)
        except OSError:
            return False
        finally:
            return self.validate()

    def validate(self):
        """
        Checks if the given xml-file is in simple or extended format
        If the format is extended self.extended is True

        @return: True if validation was successful else false
        """
        if self.validateSimple():
            self.extended = False
            return True
        elif self.validateExtended():
            self.extended = True
            return True
        else:
            return False

    def validateSimple(self):
        """
        Validates xml-file against the simple format

        @return: True if the xml-file is in simple format. else false
        """
        return self.simpleXSD.validate(self.xml)

    def validateExtended(self):
        """
        Validates xml-file against the extended format

        @return: True if the xml-file is in extended format. else false
        """
        return self.extendedXSD.validate(self.xml)

    def generateTemplate(self, extended):
        """
        Generates frame for the xml-file

        @param extended: The format which needs to be generated
        @return: True
        """
        self.extended = extended
        # @TODO: change namespace location?
        if extended is False:
            root = etree.XML('''
                        <attackTree
                                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns=""
                                xsi:noNamespaceSchemaLocation="../doc/xml/attackTreeSimple.xsd">
                            <meta>
                            </meta>
                            <tree>
                            </tree>
                        </attackTree>
                        ''')
        else:
            root = etree.XML('''
                        <attackTree
                                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns=""
                                xsi:noNamespaceSchemaLocation="../doc/xml/attackTreeExtended.xsd">
                            <meta>
                            </meta>
                            <threats>
                            </threats>
                            <countermeasures>
                            </countermeasures>
                            <connections>
                            </connections>
                        </attackTree>
                        ''')
        self.xml = etree.ElementTree(root)
        # @TODO: Error handling?
        return True

    def generateMetaElements(self, elements):
        """
        Generates the elements in the 'meta'-block of the xml file

        @param elements: The elements which will be in the meta block
        @return: True
        """
        meta = self.xml.find('meta')
        meta.clear()
        for k, v in elements.items():
            el = etree.SubElement(meta, k)
            el.text = v
        return True

    def generateTree(self, tree):
        """
        Generates the tree as a xml file.
        Before the generation it checks if it is a simple or extended tree

        @param tree: Tree to generate the xml from
        @return: True
        """
        if tree.extended is False:
            if tree.checkExtended() is not True:
                self.generateSimpleTree(tree)
                return True
        self.generateExtendedTree(tree)
        return True

    def generateSimpleTree(self, tree):
        """
        Generates the tree in the simple format.

        @param tree: Tree to generate the xml from
        """
        self.generateTemplate(False)
        xmlTree = self.xml.find('tree')
        tree.meta['root'] = tree.root
        self.generateMetaElements(tree.meta)
        self.addSimpleNode(tree, xmlTree, tree.nodeList[tree.root])

    def generateExtendedTree(self, tree):
        """
        Generates the tree in the extended format.

        @param tree: Tree to generate the xml from
        """
        self.generateTemplate(True)
        tree.meta['root'] = tree.root
        self.generateMetaElements(tree.meta)
        self.addExtendedNodes(tree)
        self.addExtendedEdges(tree)

    def addSimpleNode(self, tree, root, element):
        """
        Adds nodes to the xml file in the simple format

        @param tree: Tree from which are the nodes
        @param root: Root element of the tree
        @param element: parent element
        """
        e = self.addNode(root, element)

        if len(element.edges) > 0:
            subGenerated = False
            counterGenerated = False
            conjunctionCounter = None
            conjunctionSubTree = None
            for dst, edge in element.edges.items():
                if tree.nodeList[dst].type == 'countermeasure':
                    if counterGenerated is False:
                        counter = etree.SubElement(e, 'countermeasures')
                        conjunctionCounter = etree.SubElement(counter, edge.conjunction)
                        counterGenerated = True
                    self.addSimpleNode(tree, conjunctionCounter, tree.nodeList[dst])
                else:
                    if subGenerated is False:
                        subtree = etree.SubElement(e, 'subtree')
                        conjunctionSubTree = etree.SubElement(subtree, edge.conjunction)
                        subGenerated = True
                    self.addSimpleNode(tree, conjunctionSubTree, tree.nodeList[dst])

        return e

    def addExtendedNodes(self, tree):
        """
        Adds nodes to the xml file in the extended format

        @param tree: Tree from which are the nodes
        """
        xmlThreats = self.xml.find('threats')
        xmlCounter = self.xml.find('countermeasures')

        for v in tree.nodeList.values():
            if v.type == 'countermeasure':
                self.addNode(xmlCounter, v)
            else:
                self.addNode(xmlThreats, v)

    def addExtendedEdges(self, tree):
        """
        Adds edges to the xml file in the extended format

        @param tree: Tree from which are the edges
        """
        xmlConnection = self.xml.find('connections')
        edges = {}
        for edge in tree.edgeList:
            if edge.source in edges.keys():
                edges[edge.source].append(edge)
            else:
                edges[edge.source] = [edge]

        for k, v in edges.items():
            c = etree.SubElement(xmlConnection, 'connection', source=k, type=v[0].conjunction)
            for edge in v:
                e = etree.SubElement(c, 'destination')
                e.text = edge.destination

    def addNode(self, root, element):
        """
        Generates a node and inserts it as sub element of root

        @param root: Parent element for edge
        @param element: Element to insert
        @return: Generated XML Element
        """
        e = etree.SubElement(root, element.type, id=element.id)
        title = etree.SubElement(e, 'title')
        title.text = element.title

        description = etree.SubElement(e, 'description')
        description.text = element.description

        for k, v, in element.attributes.items():
            el = etree.SubElement(e, 'attribute', key=k)
            el.text = v

        return e

    def saveToFile(self, file):
        """
        Saves the xml to a file

        @param file: File to save to
        @return: True if saving was successfully else returns exception
        """
        try:
            self.xml.write(file, pretty_print=True, xml_declaration=True, encoding="utf-8")
        except Exception as e:
            return e
        finally:
            return True

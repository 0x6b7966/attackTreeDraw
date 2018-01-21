import traceback

from lxml import etree
import sys


class Handler:

    def __init__(self):
        self.parser = etree.XMLParser(dtd_validation=True)
        self.xml = None
        self.extended = False

        try:
            self.simpleXSD = etree.XMLSchema(etree.parse('../doc/xml/attackTreeSimple.xsd'))  # @TODO: change path
        except OSError:
            print('Can\'t load attackTreeSimple.xsd, check installation. Abort', file=sys.stderr)
        try:
            self.extendedXSD = etree.XMLSchema(etree.parse('../doc/xml/attackTreeExtended.xsd'))  # @TODO: change path
        except OSError:
            print('Can\'t load attackTreeExtended.xsd, check installation. Abort', file=sys.stderr)

    def loadFile(self, file):
        try:
            self.xml = etree.parse(file)
        except OSError:
            print(('Can\'t load %s, check dir. Abort' % file), file=sys.stderr)
            return False
        finally:
            return self.validate()

    def validate(self):
        # @TODO: Add error message
        if self.validateSimple():
            self.extended = False
            return True
        elif self.validateExtended():
            self.extended = True
            return True
        else:
            return False

    def validateSimple(self):
        return self.simpleXSD.validate(self.xml)

    def validateExtended(self):
        return self.extendedXSD.validate(self.xml)

    def generateTemplate(self, extended):
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

    def generateMetaElements(self, elements):
        meta = self.xml.find('meta')
        meta.clear()

        print(elements)

        for k, v in elements.items():
            el = etree.SubElement(meta, k)
            el.text = v

    def generateTree(self, tree):
        if tree.extended is False:  # @TODO call checkFormat()
            self.generateSimpleTree(tree)
        else:
            self.generateExtendedTree(tree)

    def generateSimpleTree(self, tree):
        self.generateTemplate(False)
        xmlTree = self.xml.find('tree')
        xmlTree.clear()  # @TODO need?
        self.generateMetaElements(tree.meta)
        self.addSimpleNode(tree, xmlTree, tree.nodeList[tree.root])

    def generateExtendedTree(self, tree):
        self.generateTemplate(True)
        # xmlTree.clear()  # @TODO need?
        self.generateMetaElements(tree.meta)
        self.addExtendedNodes(tree)
        self.addExtendedEdges(tree)

    def addSimpleNode(self, tree, root, element):
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

    def addExtendedNodes(self,tree):
        xmlThreats = self.xml.find('threats')
        xmlCounter = self.xml.find('countermeasures')

        for v in tree.nodeList.values():
            if v.type == 'countermeasure':
                self.addNode(xmlCounter, v)
            else:
                self.addNode(xmlThreats, v)

    def addExtendedEdges(self, tree):
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
        # @TODO: check if file is writeable
        try:
            self.xml.write(file, pretty_print=True, xml_declaration=True, encoding="utf-8")
        except Exception as e:
            return e
        finally:
            return True

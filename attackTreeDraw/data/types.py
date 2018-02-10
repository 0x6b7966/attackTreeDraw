import sys


class Node:
    """
    Parent class for all nodes
    """
    type = None

    def __init__(self):
        """
        Constructor for Node.
        Initialises all needed variables
        """
        self.isRoot = False  # @TODO: check if there is only one root / move to Tree()
        self.id = None  # @TODO: move ID to constructor
        self.title = ''
        self.description = ''
        self.attributes = {}
        self.parents = []
        self.children = []

        self.view = None

        self.visited = False
        self.finished = False

    def initDFS(self):
        """
        Initialises both variables for the dfs
        """
        self.visited = False
        self.finished = False


class Threat(Node):
    """
    Class for threat nodes
    """
    type = 'threat'


class Countermeasure(Node):
    """
    Class for countermeasure nodes
    """
    type = 'countermeasure'


class Conjunction(Node):
    type = 'conjunction'

    def __init__(self, id=None, conjunctionType=None):
        super().__init__()

        self.id = id
        self.conjunctionType = conjunctionType
        self.title = conjunctionType


class Edge:
    """
     Class for edges

     The Class contains the source, destination and the conjunction for the edge
     """
    def __init__(self, source, destination):
        """
        Constructor for Node.
        Initialises all needed variables
        """
        self.source = source
        self.destination = destination

    def __hash__(self):
        """
        Returns an hash of the edge
        @return: hash of the edge
        """
        return '%s-%s' % (self.source, self.destination)


class Tree:
    """
    Class which moulds the tree
    """

    def __init__(self, extended):
        """
        Constructor for Tree
        This function initialises a tree with the given format

        @param extended: Format of the tree
        """
        self.extended = extended

        self.nodeList = {}
        self.edgeList = []
        self.extended = False
        self.falseNodes = []
        self.cycleNode = None
        # @TODO: check if there is only one root / move to Tree()
        self.root = None
        self.meta = {'title': '', 'author': '', 'date': '', 'description': '', 'root': ''}

    def getTypeRecursiveDown(self, node):
        """
        Returns the first type of a node which is not a Conjunction.
        The function searches downwards.
        If there was no other element it will return Conjunction

        @param node: Node to start the search from
        @return: Type of node
        """
        if isinstance(node, Conjunction):
            for c in node.children:
                if isinstance(self.nodeList[c], Conjunction):
                    return self.getTypeRecursiveDown(self.nodeList[c])
                else:
                    return type(self.nodeList[c])
            return type(node)
        else:
            return type(node)

    def getTypeRecursiveUp(self, node):
        """
        Returns the first type of a node which is not a Conjunction.
        The function searches upwards.
        If there was no other element it will return Conjunction

        @param node: Node to start the search from
        @return: Type of node
        """
        if isinstance(node, Conjunction):
            for c in node.parents:
                if isinstance(self.nodeList[c], Conjunction):
                    return self.getTypeRecursiveUp(self.nodeList[c])
                else:
                    return type(self.nodeList[c])
            return type(node)
        else:
            return type(node)

    def getFirstElementRecursiveDown(self, node):
        """
        Returns the first node which is not a Conjunction.
        The function searches downwards.
        If there was no other element it will return the Conjunction

        @param node: Node to start the search from
        @return: node
        """
        if isinstance(node, Conjunction):
            for c in node.parents:
                if isinstance(self.nodeList[c], Conjunction):
                    return self.getFirstElementRecursiveDown(self.nodeList[c])
                else:
                    return self.nodeList[c]
            return node
        else:
            return node

    def getFirstElementRecursiveUp(self, node):
        """
        Returns the first node which is not a Conjunction.
        The function searches upwards.
        If there was no other element it will return the Conjunction

        @param node: Node to start the search from
        @return: node
        """
        if isinstance(node, Conjunction):
            for c in node.parents:
                if isinstance(self.nodeList[c], Conjunction):
                    return self.getFirstElementRecursiveUp(self.nodeList[c])
                else:
                    return self.nodeList[c]
            return node
        else:
            return node

    def addNode(self, node):
        """
        Adds a node to the tree

        @param node: node to add to the tree
        @return: True if succeed else false
        """
        if node.id is None:
            node.id = self.getNextID()
            if node.id is None:
                return False  # @TODO: Return error code?
        if node.id in self.nodeList:
            return False
        self.nodeList[node.id] = node
        return True

    def addEdge(self, sourceId, destinationId, conjunction=None):  # @TODO: remove conjunction
        """
        Adds a edge to the tree
        If conjunction is none, the conjunction from the other edges from source will be taken

        @param sourceId: Id of the source node
        @param destinationId: Id of the destination node
        @param conjunction: Conjunction for the edge
        @return: True if add was successful else false
        """
        if sourceId not in self.nodeList:
            return False
        if destinationId not in self.nodeList:
            return False

        source = self.nodeList[sourceId]
        destination = self.nodeList[destinationId]

        edge = Edge(sourceId, destinationId)
        for c in self.edgeList:
            if edge.__hash__() == c.__hash__():
                # raise ValueError('Edge %s to %s already exists' % edge.source, edge.destination) @TODO: Exception needed?
                return False

        if self.getTypeRecursiveUp(source) is Countermeasure and self.getTypeRecursiveDown(source) is Threat:
            return False

        if self.getTypeRecursiveUp(source) is Conjunction and len(source.children) > 0 and self.getTypeRecursiveDown(source) is not self.getTypeRecursiveDown(destination):
            return False

        if len(self.getFirstElementRecursiveUp(source).children) > 0 and self.getTypeRecursiveDown(self.getFirstElementRecursiveUp(source)) is self.getTypeRecursiveDown(destination):
            return False

        if not isinstance(source, Conjunction) and len(source.children) > 0 and self.getTypeRecursiveDown(source) is Countermeasure and self.getTypeRecursiveDown(destination) is Countermeasure:
            return False

        if not isinstance(source, Conjunction) and len(source.children) > 0 and self.getTypeRecursiveDown(source) is Countermeasure and self.getTypeRecursiveDown(destination) is Countermeasure:
            return False

        if not isinstance(source, Conjunction) and len(source.children) > 0 and self.getTypeRecursiveDown(source) is Countermeasure and isinstance(destination, Conjunction):
            return False

        self.edgeList.append(edge)
        self.nodeList[edge.source].children.append(edge.destination)  # @TODO: Edge to id?
        self.nodeList[edge.destination].parents.append(edge.source)

        return True

    def checkMeta(self):
        """
        Checks if the needed meta information are there

        @return: True if meta information are correct else false
        """
        if 'author' not in self.meta or self.meta['author'] == '' or 'title' not in self.meta or self.meta['title'] == '' or self.root is None:
            return False
        else:
            return True

    def checkNodes(self):
        """
        Checks if all nodes have needed parameters and saves them into falseNodes

        @return: False if len(falseNodes) > 0 else True
        """
        self.falseNodes = []
        for k, v in self.nodeList.items():
            if v.title == '':
                self.falseNodes.append(k)
        return False if len(self.falseNodes) > 0 else True

    def checkExtended(self):
        """
        Checks if the Tree is an extended or an simple tree


        @return: True if tree is extended else false
        """
        # @TODO check if edge has no parent (except root)
        test = []
        for edge in self.edgeList:
            if edge.destination not in test:
                test.append(edge.destination)
            else:
                self.extended = True
                return True
        for k, n in self.nodeList.items():
            n.initDFS()
        self.dfs(self.nodeList[self.root])
        for k, n in self.nodeList.items():
            if n.finished is False:
                self.extended = True
                return True
        self.extended = False
        return False

    def checkCycle(self):
        """
        Checks if the tree has a cycle with the dfs
        @return: True if the tree has no cycle else false
        """
        for k, n in self.nodeList.items():
            n.initDFS()
        for k, n in self.nodeList.items():
            c = self.dfs(n)
            if c is not True:
                return False
        return True

    def dfs(self, node):
        """
        Depth-first search to check the tree for a cycle

        @param node: Node to check
        @return: True if node is finished false if a cycle is detected
        """
        if node.finished:
            return True
        if node.visited:
            self.cycleNode = node
            return False
        node.visited = True
        for subN in node.children:
            c = self.dfs(self.nodeList[subN])
            if c is not True:
                return False
        node.finished = True
        return True

    def getNextID(self):
        """
        Gets the next free id for a node in the format N[0-9]{4}

        @return: next free node id
        """
        for i in range(10000):
            if 'N'+str(i).zfill(4) not in self.nodeList.keys():
                return 'N'+str(i).zfill(4)
        return None

    def removeNode(self, nodeId):
        """
        Removes a node and all edges to an from this node
        @param nodeId: Id of the node which need to deleted
        @return: True if it was successful else false
        """
        if nodeId in self.nodeList:
            for i in self.nodeList[nodeId].parents:
                print(self.nodeList[i].edges)
                self.edgeList.remove(self.nodeList[i].edges[nodeId])
                del self.nodeList[i].edges[nodeId]
            for i, e in self.nodeList[nodeId].edges.items():
                self.nodeList[i].parents.remove(nodeId)
                self.edgeList.remove(e)
            del self.nodeList[nodeId]
            return True
        else:
            return False

    def removeEdge(self, edgeId):
        """
        Removes an edge

        @param edgeId: Id of the edge (hash)
        @return: True if successful else false
        """
        edge = None
        for e in self.edgeList:
            if edgeId == e.__hash__():
                edge = e
        if edge is not None:
            del self.nodeList[edge.source].edges[edge.destination]
            self.nodeList[edge.destination].parents.remove(edge.source)
            self.edgeList.remove(edge)
            return True
        else:
            return False

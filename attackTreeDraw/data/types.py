import copy


class Node:
    """
    Parent class for all nodes
    """

    def __init__(self):
        """
        Constructor for Node.
        Initialises all needed variables
        """
        self.type = 'Node'

        self.isRoot = False
        self.id = None
        self.title = ''
        self.description = ''
        self.attributes = {}
        self.parents = []
        self.children = []

        self.view = None
        self.position = None

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
    pass


class Countermeasure(Node):
    """
    Class for countermeasure nodes
    """
    pass


class Conjunction(Node):
    """
    Class for conjunction nodes
    """

    def __init__(self, id=None, conjunctionType=None):
        """
        Constructor for conjunctions.
        sets the conjunction type and the id, calls Node.__init__()

        :param id: ID of the node
        :param conjunctionType: Type for this conjunction
        """
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
        :return: hash of the edge
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

        :param extended: Format of the tree
        """
        self.extended = extended

        self.nodeList = {}
        self.edgeList = []
        self.extended = False
        self.falseNodes = []
        self.cycleNode = None
        self.root = None
        self.meta = {'title': '', 'author': '', 'date': '', 'description': '', 'root': ''}
        """
        List for reserved nodeIDs while copy/paste is active
        """
        self.reservedList = []

        self.lastError = ''

    def getTypeRecursiveDown(self, node):
        """
        Returns the first type of a node which is not a Conjunction.
        The function searches downwards.
        If there was no other element it will return Conjunction

        :param node: Node to start the search from
        :return: Type of node
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

        :param node: Node to start the search from
        :return: Type of node
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

        :param node: Node to start the search from
        :return: node
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

        :param node: Node to start the search from
        :return: node
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

        :param node: node to add to the tree
        :return: True if succeed else false
        """
        if node.id is None:
            node.id = self.getNextID()
            if node.id is None:
                self.lastError = 'No free node IDs left'
                return False
        if node.id in self.nodeList:
            self.lastError = 'Node ID already in tree'
            return False
        self.nodeList[node.id] = node
        return True

    def addEdge(self, sourceId, destinationId):
        """
        Adds a edge to the tree

        :param sourceId: Id of the source node
        :param destinationId: Id of the destination node
        :return: True if add was successful else false
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
                return False

        if destinationId == sourceId:
            return False

        if self.getTypeRecursiveUp(source) is Countermeasure and self.getTypeRecursiveDown(destination) is Threat:
            return False
        if isinstance(source, Conjunction) and isinstance(destination, Conjunction) \
                and self.getTypeRecursiveDown(source) is not Conjunction \
                and self.getTypeRecursiveDown(destination) is not Conjunction \
                and self.getTypeRecursiveDown(source) is not self.getTypeRecursiveDown(destination):
            return False
        if not isinstance(source, Conjunction) and len(source.children) > 0 \
                and self.getTypeRecursiveDown(source) is Threat and self.getTypeRecursiveDown(destination) is Threat:
            return False
        if not isinstance(source, Conjunction) and len(source.children) > 0 \
                and self.getTypeRecursiveDown(source) is Countermeasure \
                and self.getTypeRecursiveDown(destination) is Countermeasure:
            return False
        if not isinstance(source, Conjunction) and len(source.children) > 0 \
                and self.getTypeRecursiveDown(source) is Countermeasure and isinstance(destination, Conjunction):
            return False
        if self.getTypeRecursiveUp(source) is not Conjunction and self.getTypeRecursiveDown(destination) is Conjunction:
            for c in self.getFirstElementRecursiveUp(source).children:
                if self.getTypeRecursiveDown(destination) is not Conjunction \
                        and self.getTypeRecursiveDown(self.nodeList[c]) is self.getTypeRecursiveDown(destination):
                    return False

        self.edgeList.append(edge)
        self.nodeList[edge.source].children.append(edge.destination)
        self.nodeList[edge.destination].parents.append(edge.source)

        return True

    def checkMeta(self):
        """
        Checks if the needed meta information are there

        :return: True if meta information are correct else false
        """
        if 'author' not in self.meta or self.meta['author'] == '' \
                or 'title' not in self.meta or self.meta['title'] == '' or self.root is None:
            return False
        else:
            return True

    def checkNodes(self):
        """
        Checks if all nodes have needed parameters and saves them into falseNodes

        :return: False if len(falseNodes) > 0 else True
        """
        self.falseNodes = []
        for k, v in self.nodeList.items():
            if v.title == '':
                self.falseNodes.append(k)
        return False if len(self.falseNodes) > 0 else True

    def checkExtended(self):
        """
        Checks if the Tree is an extended or an simple tree

        :return: True if tree is extended else false
        """
        for node in self.nodeList.values():
            if isinstance(node, Conjunction) and len(node.children) == 0:
                self.extended = True
                return True
            if node.isRoot is False and len(node.parents) == 0:
                self.extended = True
                return True
            if len(node.parents) > 1:
                self.extended = True
                return True
        self.extended = False
        return False

    def checkCycle(self):
        """
        Checks if the tree has a cycle with the dfs
        :return: True if the tree has no cycle else false
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

        :param node: Node to check
        :return: True if node is finished false if a cycle is detected
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

    def getNextID(self, keyList=None):
        """
        Gets the next free id for a node in the format N[0-9]{4}

        :param: keyList list of keys already used
        :return: next free node id
        """
        if keyList is None:
            keyList = []
        for i in range(10000):
            if 'N' + str(i).zfill(4) not in self.nodeList.keys() and 'N' + str(i).zfill(4) not in keyList \
                    and 'N' + str(i).zfill(4) not in self.reservedList:
                return 'N' + str(i).zfill(4)
        return None

    def removeNode(self, nodeId):
        """
        Removes a node and all edges to an from this node
        :param nodeId: Id of the node which need to deleted
        :return: True if it was successful else false
        """
        if nodeId in self.nodeList:
            parents = copy.copy(self.nodeList[nodeId].parents)
            for i in parents:
                self.removeEdge(i + '-' + nodeId)
            children = copy.copy(self.nodeList[nodeId].children)
            for i in children:
                self.removeEdge(nodeId + '-' + i)
            if self.nodeList[nodeId].isRoot:
                self.root = None
            del self.nodeList[nodeId]
            return True
        else:
            return False

    def removeEdge(self, edgeId):
        """
        Removes an edge

        :param edgeId: Id of the edge (hash)
        :return: True if successful else false
        """
        edge = None
        for e in self.edgeList:
            if edgeId == e.__hash__():
                edge = e
                break
        if edge is not None:
            self.nodeList[edge.source].children.remove(edge.destination)
            self.nodeList[edge.destination].parents.remove(edge.source)
            self.edgeList.remove(edge)
            return True
        else:
            return False

    def makeSimple(self):
        """
        Generates an simple tree out of an extended one.

        Copies every element with two or more parents.
        """
        nodeList = copy.copy(self.nodeList)
        changed = False
        for node in nodeList.values():
            if len(node.parents) > 1:
                newNode = copy.copy(node)
                newNode.id = None
                newNode.parents = []
                newNode.children = []
                self.addNode(newNode)
                parent = node.parents[-1]
                self.removeEdge(node.parents[-1] + '-' + node.id)
                self.addEdge(parent, newNode.id)
                newNode.children = copy.copy(node.children)
                for c in newNode.children:
                    self.edgeList.append(Edge(newNode.id, c))
                    self.nodeList[c].parents.append(newNode.id)
                changed = True
        if changed is True:
            self.makeSimple()

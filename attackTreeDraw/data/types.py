import sys


class Node:
    type = None

    def __init__(self):
        self.isRoot = False  # @TODO: check if there is only one root / move to Tree()
        self.id = None  # @TODO: move ID to constructor
        self.title = ''
        self.description = ''
        self.attributes = {}
        self.parents = []
        self.edges = {}

        self.view = None

        self.visited = False
        self.finished = False

    def toString(self):
        print('-----------\nNode: %s\nParent: %s\nChild: %s\nConjunction: %s\nTitle: %s' % (
            self.id, self.parents, self.edges.keys(), self.edges.values(), self.title))

    def initDFS(self):
        self.visited = False
        self.finished = False


class Threat(Node):
    type = 'threat'


class Countermeasure(Node):
    type = 'countermeasure'


class Edge:
    def __init__(self, source, destination, conjunction):
        self.source = source
        self.destination = destination
        self.conjunction = conjunction

    def __hash__(self):
        return '%s-%s' % (self.source, self.destination)


class Tree:

    def __init__(self, extended):
        self.extended = extended

        self.nodeList = {}
        self.edgeList = []
        self.extended = False
        self.falseNodes = []
        # @TODO: check if there is only one root / move to Tree()
        self.root = None
        self.meta = {'title': '', 'author': '', 'date': '', 'description': '', 'root': ''}

    def addNode(self, node):
        if node.id is None:
            node.id = self.getNextID()
            if node.id is None:
                return False  # @TODO: Return error code?
        if node.id in self.nodeList:
            return False
        self.nodeList[node.id] = node
        return True

    def addEdge(self, sourceId, destinationId, conjunction=None):  # @TODO: only IDs as args
        if sourceId not in self.nodeList:
            return False
        if destinationId not in self.nodeList:
            return False

        source = self.nodeList[sourceId]
        destination = self.nodeList[destinationId]

        # @TODO: Check if source is C and dst is T,
        # @TODO: Add return value for error
        # @TODO: Add conjunction

        if conjunction is None:
            for e in self.edgeList:
                if destination.type == self.nodeList[e.destination].type:
                    conjunction = e.conjunction
            if conjunction is None:
                return False
        else:
            for e in self.nodeList[sourceId].edges:
                if destination.type == self.nodeList[e].type:
                    if conjunction != self.nodeList[sourceId].edges[e].conjunction:
                        print('Edge %s to %s not equal conjunctions' % (sourceId, destinationId))  # Better error handling
                        return False

        edge = Edge(sourceId, destinationId, conjunction)

        for c in self.edgeList:
            if edge.__hash__() == c.__hash__():
                print('Edge %s to %s already exists' % (edge.source, edge.destination), file=sys.stderr)
                if edge.conjunction != c.conjunction:
                    print('Edge %s to %s not equal conjunctions' % (edge.source, edge.destination), file=sys.stderr)
                return False
        self.edgeList.append(edge)

        self.nodeList[edge.source].edges[edge.destination] = edge  # @TODO: Edge to id?
        self.nodeList[edge.destination].parents.append(edge.source)

        return True

    def checkMeta(self):
        if 'author' not in self.meta or self.meta['author'] == '' or 'title' not in self.meta or self.meta['title'] == '' or self.root is None:
            return False
        else:
            return True

    def checkNodes(self):
        self.falseNodes = []
        for k,v in self.nodeList.items():
            if v.title == '':
                self.falseNodes.append(k)
        return False if len(self.falseNodes) > 0 else True

    def checkExtended(self):
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
        for k, n in self.nodeList.items():
            n.initDFS()
        for k, n in self.nodeList.items():
            c = self.dfs(n)
            if c is not True:
                return False
        return True

    def dfs(self, node):
        if node.finished:
            return True
        if node.visited:
            self.cycleNode = node
            return False
        node.visited = True
        for subN in node.edges.keys():
            c = self.dfs(self.nodeList[subN])
            if c is not True:
                return False
        node.finished = True
        return True

    def getNextID(self):
        for i in range(10000):
            if 'N'+str(i).zfill(4) not in self.nodeList.keys():
                return 'N'+str(i).zfill(4)
        return None

    def removeNode(self, nodeId):
        if nodeId in self.nodeList:
            print(self.nodeList)
            print(self.edgeList)
            for i in self.nodeList[nodeId].parents:
                self.edgeList.remove(self.nodeList[i].edges[nodeId])
                del self.nodeList[i].edges[nodeId]
            for i in self.nodeList[nodeId].edges:
                self.nodeList[i].parents.remove(nodeId)
                self.edgeList.remove(i)
            del self.nodeList[nodeId]
            print(self.nodeList)
            print(self.edgeList)
            return True
        else:
            return False

    def removeEdge(self, edgeId):
        edge = None
        for e in self.edgeList:
            if edgeId == e.__hash__():
                edge = e
        if edge is not None:
            print(self.edgeList)
            del self.nodeList[edge.source].edges[edge.destination]
            self.nodeList[edge.destination].parents.remove(edge.source)
            self.edgeList.remove(edge)
            print(self.edgeList)
            return True
        else:
            return False

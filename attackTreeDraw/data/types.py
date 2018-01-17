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
        self.cycleNode = None
        self.extended = False
        # @TODO: check if there is only one root / move to Tree()
        self.root = None
        self.meta = {}

    def addNode(self, node):
        if node.id in self.nodeList:
            return False
        if node.id is None:
            node.id = self.getNextID()
            if node.id is None:
                return False  # @TODO: Return error code?
        self.nodeList[node.id] = node
        return True

    def addEdge(self, source, destination, conjunction):
        fail = False
        if source not in self.nodeList:
            return False
        if destination not in self.nodeList:
            return False

        # @TODO: Check if source is C and dst is T,
        # @TODO: Add return value for error
        # @TODO: Add conjunction

        edge = Edge(source, destination, conjunction)

        for c in self.edgeList:
            if edge.__hash__() == c.__hash__():
                print('Edge %s to %s already exists' % (edge.source, edge.destination), file=sys.stderr)
                if edge.conjunction != c.conjunction:
                    print('Edge %s to %s not equal conjunctions' % (edge.source, edge.destination), file=sys.stderr)
                fail = True
                break
        if fail is not True and edge.source is not None:
            self.edgeList.append(edge)  # @TODO: Add addEdge() to tree
            self.nodeList[edge.source].edges[edge.destination] = edge
            self.nodeList[edge.destination].parents.append(edge.destination)
            return True
        else:
            return False

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

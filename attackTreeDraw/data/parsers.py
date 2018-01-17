from .types import *
import sys

# @TODO: Move to handler and rename to parser?


def parseExtendedConnection(tree, edge):
    if edge.get('source') in tree.nodeList.keys():
        source = edge.get('source')
        for dst in edge.iterchildren(tag='destination'):
            dstIn = False
            if dst.text in tree.nodeList.keys():
                fail = False
                for c in tree.edgeList:
                    if (source, dst.text) == c:
                        print(('Edge %s to %s already exists' % source, dst.text), file=sys.stderr)
                        fail = True
                        break
                if fail is not True and source is not None:
                    tree.addEdge(source, dst.text, edge.get('type'))
            else:
                print(('Destination node %s does not exist' % dst.text), file=sys.stderr)
    else:
        print(('Source node %s does not exist' % edge.get('source')), file=sys.stderr)


def parseExtendedNode(tree, node):
    # @TODO: app function parseNode(node) to reduce redundant code
    n = None
    if node.tag == 'threat':
        n = Threat()
        n.id = node.get('id')
    elif node.tag == 'countermeasure':
        n = Countermeasure()
        n.id = node.get('id')
    else:
        raise ValueError('Parsing failed for element %s' % node.tag)

    for a in node.findall('attribute'):
        n.attributes[a.get('key')] = a.text
    n.title = node.find('title').text
    n.description = node.find('description').text

    check = tree.addNode(n)
    if check is False:
        print(('Can\'t add node %s. NodeID exists' % n.id), file=sys.stderr)
        return None
    if n is None:
        print(('Can\'t add node %s.' % n.id), file=sys.stderr)
        return None
    return n


def parseSimpleNode(tree, node, parent=None):
    n = None
    if node.tag == 'threat':
        n = Threat()
        n.id = node.get('id')
    elif node.tag == 'countermeasure':
        n = Countermeasure()
        n.id = node.get('id')
    else:
        raise ValueError('Parsing failed for element %s' % node.tag)

    for a in node.findall('attribute'):
        n.attributes[a.get('key')] = a.text
    n.title = node.find('title').text
    n.description = node.find('description').text

    if parent is not None:
        n.parents.append(parent)
    else:
        n.isRoot = True
        tree.root = n.id
    check = tree.addNode(n)

    if node.find('subtree') is not None:
        conjunction = node.find('subtree')[0].tag
        for subNode in node.find('subtree')[0].iterchildren():
            subN = parseSimpleNode(tree, subNode, n.id)
            if subN is not None:
                tree.addEdge(n.id, subN.id, conjunction)

    if node.find('countermeasures') is not None:
        conjunction = node.find('countermeasures')[0].tag
        for subNode in node.find('countermeasures')[0].iterchildren():
            subN = parseSimpleNode(tree, subNode, n.id)
            if subN is not None:
                if not tree.addEdge(n.id, subN.id, conjunction):
                    print('Cant\'t add Edge %s to %s with %s' % (n.id, subN.id, conjunction), file=sys.stderr)

    if check is False:
        print(('Can\'t add node %s. NodeID exists' % n.id), file=sys.stderr)
        return None
    if n is None:
        print(('Can\'t add node %s.' % n.id), file=sys.stderr)
        return None

    return n

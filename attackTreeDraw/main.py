from attackTreeDraw.data.handler import Handler

if __name__ == "__main__":

    h = Handler()

    tree = h.buildFromXML('../doc/xml/exampleTreeSimple.xml')

    print(tree.nodeList)
    print(tree.edgeList)

    print(tree.checkCycle())
    print(tree.checkExtended())

    print(tree.meta)


    for n in tree.nodeList:
        tree.nodeList[n].toString()

    h.saveToXML(tree, 'test.xml')




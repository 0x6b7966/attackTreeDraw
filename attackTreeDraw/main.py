import sys
import traceback

from PyQt5.QtWidgets import QApplication
from gui.main import Main


from data.handler import Handler

if __name__ == "__main__":

#    h = Handler()
#    tree = h.buildFromXML('../doc/xml/exampleTreeSimple.xml')


#    print(tree.nodeList)
#    print(tree.edgeList)

#    print(tree.checkCycle())
#    print(tree.checkExtended())

#    print(tree.meta)


#    for n in tree.nodeList:
#        tree.nodeList[n].toString()

#    h.saveToXML(tree, 'test.xml')
    try:
        app = QApplication(sys.argv)
        ex = Main()
        sys.exit(app.exec_())
    except Exception as e:
        print(sys.exc_info())
        print(traceback.format_exc())
        exit(-1)



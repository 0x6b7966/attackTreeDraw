from PyQt5.QtWidgets import QWidget


class NodeEdit(QWidget):
    def __init__(self, node):
        QWidget.__init__(self)

        self.nodeItem = node

        self.resize(320, 240)
        self.setWindowTitle("Node: %s" % self.nodeItem.node.title)
        self.show()

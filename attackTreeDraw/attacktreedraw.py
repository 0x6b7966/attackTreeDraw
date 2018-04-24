import sys

import os
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from gui.main import Main

"""
Main entry point for attackTreeDraw
"""
if __name__ == "__main__":
    debug = True
    """
    Debug suppresses all console output
    """
    if debug is False:
        sys.stdout = os.devnull
        sys.stderr = os.devnull
    app = QApplication(sys.argv)
    includePath = os.path.dirname(os.path.abspath(__file__))
    app.setWindowIcon(QIcon(os.path.join(includePath, 'gui/assets/icons/logo.png')))
    ex = Main()
    sys.exit(app.exec_())

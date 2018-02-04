import sys
import traceback

from PyQt5.QtWidgets import QApplication
from gui.main import Main

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        ex = Main()
        sys.exit(app.exec_())
    except Exception as e:
        print(sys.exc_info())
        print(traceback.format_exc())
        exit(-1)



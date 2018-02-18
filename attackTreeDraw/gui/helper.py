import json
import pathlib

import os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor


class Configuration:
    colors = {
        'threat': {
            'node': {'background': QColor(Qt.white).name(), 'border': QColor(Qt.black).name(), 'font': QColor(Qt.black).name()},
            'composition': {'background': QColor(Qt.white).name(), 'border': QColor(Qt.black).name(), 'font': QColor(Qt.black).name()},
            'alternative': {'background': QColor(Qt.white).name(), 'border': QColor(Qt.black).name(), 'font': QColor(Qt.black).name()},
            'sequence': {'background': QColor(Qt.white).name(), 'border': QColor(Qt.black).name(), 'font': QColor(Qt.black).name()},
            'threshold': {'background': QColor(Qt.white).name(), 'border': QColor(Qt.black).name(), 'font': QColor(Qt.black).name()}
        },
        'countermeasure': {
            'node': {'background': QColor(Qt.white).name(), 'border': QColor(Qt.black).name(), 'font': QColor(Qt.black).name()},
            'composition': {'background': QColor(Qt.white).name(), 'border': QColor(Qt.black).name(), 'font': QColor(Qt.black).name()},
            'alternative': {'background': QColor(Qt.white).name(), 'border': QColor(Qt.black).name(), 'font': QColor(Qt.black).name()},
            'sequence': {'background': QColor(Qt.white).name(), 'border': QColor(Qt.black).name(), 'font': QColor(Qt.black).name()},
            'threshold': {'background': QColor(Qt.white).name(), 'border': QColor(Qt.black).name(), 'font': QColor(Qt.black).name()}
        },
        'default': {
            'node': {'background': QColor(Qt.white).name(), 'border': QColor(Qt.black).name(), 'font': QColor(Qt.black).name()},
            'composition': {'background': QColor(Qt.white).name(), 'border': QColor(Qt.black).name(), 'font': QColor(Qt.black).name()},
            'alternative': {'background': QColor(Qt.white).name(), 'border': QColor(Qt.black).name(), 'font': QColor(Qt.black).name()},
            'sequence': {'background': QColor(Qt.white).name(), 'border': QColor(Qt.black).name(), 'font': QColor(Qt.black).name()},
            'threshold': {'background': QColor(Qt.white).name(), 'border': QColor(Qt.black).name(), 'font': QColor(Qt.black).name()}
        },
    }
    font = None

    @staticmethod
    def checkConfigFile():
        pathlib.Path(os.path.join(pathlib.Path.home(), '.attackTreeDraw')).mkdir(parents=True, exist_ok=True)
        if not pathlib.Path(os.path.join(pathlib.Path.home(), '.attackTreeDraw/config.json')).is_file():
            Configuration.saveConfig()

    @staticmethod
    def loadConfigFile():
        Configuration.checkConfigFile()
        with open(os.path.join(pathlib.Path.home(), '.attackTreeDraw/config.json'), 'r') as fp:
            data = json.load(fp)
        Configuration.colors.update(data['colors'])
        Configuration.font = QFont(data['font'])

    @staticmethod
    def saveConfig():
        pathlib.Path(os.path.join(pathlib.Path.home(), '.attackTreeDraw')).mkdir(parents=True, exist_ok=True)
        data = {'colors': Configuration.colors, 'font': Configuration.font.key()}
        with open(os.path.join(pathlib.Path.home(), '.attackTreeDraw/config.json'), 'w') as fp:
            json.dump(data, fp)


import json
import pathlib

import os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor


class Configuration:
    """
    This class is the handler for the configuration.
    It holds the colors for the nodes and the font
    """

    """
    Dictionary for the colors
    """
    colors = {
        'threat': {
            'node': {'background': QColor(Qt.white).name(), 'border': QColor(Qt.black).name(),
                     'font': QColor(Qt.black).name()},
            'composition': {'background': QColor(Qt.white).name(), 'border': QColor(Qt.black).name(),
                            'font': QColor(Qt.black).name()},
            'alternative': {'background': QColor(Qt.white).name(), 'border': QColor(Qt.black).name(),
                            'font': QColor(Qt.black).name()},
            'sequence': {'background': QColor(Qt.white).name(), 'border': QColor(Qt.black).name(),
                         'font': QColor(Qt.black).name()},
            'threshold': {'background': QColor(Qt.white).name(), 'border': QColor(Qt.black).name(),
                          'font': QColor(Qt.black).name()}
        },
        'countermeasure': {
            'node': {'background': QColor(Qt.white).name(), 'border': QColor(Qt.black).name(),
                     'font': QColor(Qt.black).name()},
            'composition': {'background': QColor(Qt.white).name(), 'border': QColor(Qt.black).name(),
                            'font': QColor(Qt.black).name()},
            'alternative': {'background': QColor(Qt.white).name(), 'border': QColor(Qt.black).name(),
                            'font': QColor(Qt.black).name()},
            'sequence': {'background': QColor(Qt.white).name(), 'border': QColor(Qt.black).name(),
                         'font': QColor(Qt.black).name()},
            'threshold': {'background': QColor(Qt.white).name(), 'border': QColor(Qt.black).name(),
                          'font': QColor(Qt.black).name()}
        },
        'default': {
            'node': {'background': QColor(Qt.white).name(), 'border': QColor(Qt.black).name(),
                     'font': QColor(Qt.black).name()},
            'composition': {'background': QColor(Qt.white).name(), 'border': QColor(Qt.black).name(),
                            'font': QColor(Qt.black).name()},
            'alternative': {'background': QColor(Qt.white).name(), 'border': QColor(Qt.black).name(),
                            'font': QColor(Qt.black).name()},
            'sequence': {'background': QColor(Qt.white).name(), 'border': QColor(Qt.black).name(),
                         'font': QColor(Qt.black).name()},
            'threshold': {'background': QColor(Qt.white).name(), 'border': QColor(Qt.black).name(),
                          'font': QColor(Qt.black).name()}
        },
    }
    font = None

    @staticmethod
    def checkConfigFile():
        """
        Checks if there is a config file in $HOME/.attackTreeDraw
        If there is none an initial file will be created
        """
        pathlib.Path(os.path.join(pathlib.Path.home(), '.attackTreeDraw')).mkdir(parents=True, exist_ok=True)
        if not pathlib.Path(os.path.join(pathlib.Path.home(), '.attackTreeDraw/config.json')).is_file():
            Configuration.saveConfig()

    @staticmethod
    def loadConfigFile():
        """
        Loads the configuration from the config file
        Calls Configuration.checkConfigFile() before to be sure there is a file
        """
        Configuration.checkConfigFile()
        with open(os.path.join(pathlib.Path.home(), '.attackTreeDraw/config.json'), 'r') as fp:
            data = json.load(fp)
        Configuration.colors.update(data['colors'])
        Configuration.font = QFont()
        Configuration.font.fromString(data['font'])

    @staticmethod
    def saveConfig():
        """
        Saves the configuration to the config file at $HOME/.attackTreeDraw
        """
        pathlib.Path(os.path.join(pathlib.Path.home(), '.attackTreeDraw')).mkdir(parents=True, exist_ok=True)
        data = {'colors': Configuration.colors, 'font': Configuration.font.toString()}
        with open(os.path.join(pathlib.Path.home(), '.attackTreeDraw/config.json'), 'w') as fp:
            json.dump(data, fp)

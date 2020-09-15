import os
import sys

os.environ['QT_API'] = 'pyqt5'

from qtpy.QtWidgets import QApplication

from __test__ import mainFunction


if __name__ == '__main__':
    mainFunction()
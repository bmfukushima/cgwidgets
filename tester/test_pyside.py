import os
import sys

os.environ['QT_API'] = 'pyside2'

import qtpy

from qtpy.QtWidgets import QApplication

#from cgwidgets.tester.__test__ import mainFunction
from __test__ import mainFunction

if __name__ == '__main__':
    mainFunction()
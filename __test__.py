import unittest
import sys
import os

os.environ['QT_API'] = 'pyside2'

import qtpy
from qtpy.QtWidgets import QApplication

from cgwidgets.widgets import __test__ as test_widgets
from cgwidgets.delegates import __test__ as test_delegates


def testDelegates():
    test_delegates.mainFunction()


def testWidgets():
    test_widgets.mainFunction()


if __name__ == '__main__':
    print(
    '''
    QT_API == {}
    '''.format(qtpy.API)
    )
    app = QApplication(sys.argv)
    testDelegates()
    testWidgets()
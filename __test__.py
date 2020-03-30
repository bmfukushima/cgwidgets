import unittest
import sys

from qtpy.QtWidgets import QApplication

from cgwidgets.widgets import __test__ as test_widgets
from cgwidgets.delegates import __test__ as test_delegates


def testDelegates():
    test_delegates.mainFunction()


def testWidgets():
    test_widgets.mainFunction()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    testDelegates()
    testWidgets()
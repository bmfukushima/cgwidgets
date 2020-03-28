import unittest
import sys

from qtpy.QtWidgets import QLabel, QApplication
from qtpy.QtCore import QEvent, Qt
from qtpy.QtTest import QTest

from cgwidgets.widgets.LadderWidget import LadderWidget
from PyQt5.Qt import QApplication


class TestLadderWidget(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        TestLadderWidget.widget = LadderWidget()

    def setUp(self):
        self.ladder0 = LadderWidget()
        self.ladder1 = LadderWidget(
            value_list=[0.0001, 0.001, 0.01, 0.1],
            widget=QLabel(),
            user_input=QEvent.MouseButtonPress
        )

    def testPopUp(self):
        QTest.mouseClick(self.ladder0, Qt.LeftButton)
        QTest.mouseClick(self.ladder1, Qt.LeftButton)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    unittest.main()
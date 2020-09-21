"""
import sys
import math
import os
os.environ['QT_API'] = 'pyside2'
import qtpy

print(
"""
QT_API == {}
""".format(qtpy.API)
)

from qtpy.QtGui import *
from qtpy.QtWidgets import *
from qtpy.QtCore import *


print(dir(qtpy))


from cgwidgets.utils import installLadderDelegate 

class TestWidget(QLineEdit):
    def __init__(self, parent=None, value=0):
        super(TestWidget, self).__init__(parent)
        pos = QCursor().pos()
        self.setGeometry(pos.x(), pos.y(), 200, 100)
        value_list = [0.001, 0.01, 0.1, 1, 10, 100, 1000]
        #self.setText('0')
        #value_list = [0.0001, 0.001, 0.01, 0.1]
        pos = QCursor.pos()
        installLadderDelegate(
            self,
            user_input=QEvent.MouseButtonPress,
            value_list=value_list
        )

    def setValue(self, value):
        self.setText(str(value))



app = QApplication(sys.argv)
menu = TestWidget()
menu.show()
sys.exit(app.exec_())
"""
import unittest
import sys

from qtpy.QtWidgets import QApplication


def testLadderDelegate():
    from cgwidgets.delegates.LadderDelegate import test_LadderDelegate
    suite = unittest.TestLoader().loadTestsFromModule(test_LadderDelegate)
    unittest.TextTestRunner(verbosity=2).run(suite)


def mainFunction():
    testLadderDelegate()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainFunction()


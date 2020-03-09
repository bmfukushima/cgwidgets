import sys
import math

from qtpy.QtGui import *
from qtpy.QtWidgets import *
from qtpy.QtCore import *

from cgwidgets.__utils__ import installLadderDelegate 

""" TEST STUFF """


class TestWidget(QLineEdit):
    def __init__(self, parent=None, value=0):
        super(TestWidget, self).__init__(parent)
        pos = QCursor().pos()
        self.setGeometry(pos.x(), pos.y(), 200, 100)
        value_list = [0.001, 0.01, 0.1, 1, 10, 100, 1000]
        #self.setText('0')
        value_list = [0.0001, 0.001, 0.01, 0.1]
        pos = QCursor.pos()
        installLadderDelegate(
            self,
            user_input=QEvent.MouseButtonPress,
            value_list=value_list
        )

    def setValue(self, value):
        self.setText(str(value))

    '''
    def installLadderDelegate(self):
        ladder = LadderDelegate(
            parent=self,
            widget=self,
            #pos=self.pos(),
            value_list=self._value_list
        )
        self.installEventFilter(ladder)
    '''
    def mousePressEvent(self, event, *args, **kwargs):
        """
        trigger to active the popup menu
        """
        """
        if event.button() == Qt.MiddleButton:
            ladder = LadderDelegate(
                parent=self,
                widget=self,
                #pos=self.pos(),
                value_list=self._value_list
            )
            ladder.show()
        """
        return QLineEdit.mousePressEvent(self, event, *args, **kwargs)

'''
app = QApplication(sys.argv)
menu = TestWidget()
menu.show()
sys.exit(app.exec_())
'''


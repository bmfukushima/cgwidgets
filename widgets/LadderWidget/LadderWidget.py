import sys
import math

from qtpy.QtGui import *
from qtpy.QtWidgets import *
from qtpy.QtCore import *

from cgwidgets.__utils__ import installLadderDelegate 

class LadderWidget(QWidget):
    def __init__(
        self,
        parent=None,
        value_list = [0.0001, 0.001, 0.01, 0.1],
        widget=QLineEdit()
    ):
        super(LadderWidget, self).__init__(parent)
        # setup widget
        layout = QVBoxLayout(self)
        layout.addWidget(widget)
        
        # set up position
        pos = QCursor().pos()
        self.setGeometry(pos.x(), pos.y(), 200, 100)
        
        pos = QCursor.pos()
        
        # install ladder delegate
        installLadderDelegate(
            widget,
            user_input=QEvent.MouseButtonPress,
            value_list=value_list
        )

    def setValue(self, value):
        self.setText(str(value))

'''
app = QApplication(sys.argv)
label = QLabel('0')
menu = LadderWidget(widget=label)
menu.show()
sys.exit(app.exec_())
'''



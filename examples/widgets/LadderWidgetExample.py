import unittest
import sys
import math
from decimal import Decimal, getcontext

from qtpy.QtGui import *
from qtpy.QtWidgets import *
from qtpy.QtCore import *

from cgwidgets.utils import (
    checkNegative,
    checkIfValueInRange,
    getGlobalPos,
    installInvisibleCursorEvent,
    installInvisibleWidgetEvent,
    installStickyAdjustDelegate,
    installSlideDelegate,
    removeSlideDelegate,
    updateStyleSheet
)

from cgwidgets.delegates import SlideDelegate

from cgwidgets.settings.colors import (
    iColor
)

from cgwidgets.widgets import FloatInputWidget
from qtpy.QtWidgets import QLabel, QApplication


from cgwidgets.widgets.LadderWidget import LadderWidget


class LadderWidgetExample(QLabel):
    def __init__(self, parent=None):
        super(LadderWidgetExample, self).__init__(parent)

    def setValue(self, value):
        self.setText(str(value))



def main():
    import sys
    app = QApplication(sys.argv)

    from cgwidgets.utils import installLadderDelegate

    class TestWidget(QLineEdit):
        def __init__(self, parent=None, value=0):
            super(TestWidget, self).__init__(parent)
            pos = QCursor().pos()
            self.setGeometry(pos.x(), pos.y(), 200, 100)
            value_list = [0.001, 0.01, 0.1, 1, 10, 100, 1000]
            ladder = installLadderDelegate(
                self,
                user_input=QEvent.MouseButtonRelease,
                value_list=value_list
            )
            #ladder.setDiscreteDrag(True, alignment=Qt.AlignLeft, depth=10)


        def setValue(self, value):
            self.setText(str(value))

    mw = QWidget()

    ml = QVBoxLayout()
    mw.setLayout(ml)

    w2 = QWidget(mw)
    l2 = QVBoxLayout()
    w2.setLayout(l2)
    float_input = FloatInputWidget()
    float_input.setDoMath(True)
    ladder = installLadderDelegate(
        float_input
    )

    float_input.setText('12')
    #ladder.setInvisibleWidget(True)


    #ladder.setDiscreteDrag(True, alignment=Qt.AlignLeft, depth=10, display_widget=w2)
    # ladder.setDiscreteDrag(
    #     True,
    #     alignment=Qt.AlignBottom,
    #     depth=10,
    #     display_widget=w2
    #     )
    # ladder.setMiddleItemBorderColor((255, 0, 255))
    # ladder.setMiddleItemBorderWidth(2)
    # ladder.setItemHeight(50)
    # ladder.rgba_fg_slide = (255, 128, 32, 255)
    # ladder.rgba_bg_slide = (0, 128, 255, 255)

    l2.addWidget(float_input)
    l2.addWidget(QPushButton('BUTTTON'))
    l2.addWidget(QLabel('LABELLLLL'))

    ml.addWidget(w2)
    mw.show()
    mw.move(QCursor.pos())

    sys.exit(app.exec_())


if __name__ == '__main__':

    main()


    #help(LadderDelegate)

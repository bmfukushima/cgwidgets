"""
Inputs:
    No modifier:
        LMB = HUE / Value
        MMB = Value
        RMB = Saturation

    CTRL | ALT:
        LMB = Red
        MMB = Green
        RMB = Blue
"""

import sys

from qtpy.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from qtpy.QtCore import Qt
from qtpy.QtGui import QCursor

from cgwidgets.utils import attrs
from cgwidgets.widgets.InputWidgets.ColorInputWidget import ColorClockDelegate

# set up main widget
app = QApplication(sys.argv)
mw = QWidget()
l = QVBoxLayout(mw)
test_label = QLabel('lkjasdf')

# create user input event
def userInputEvent(widget, color):
    test_label.setText(repr(color.getRgb()))

# create widget
color_widget = ColorClockDelegate()

# set up custom user event
color_widget.setUserInput(userInputEvent)

# center of the circle
color_widget.setOffset(50)

# add widgets to main widget
l.addWidget(test_label)
l.addWidget(color_widget)

# show
mw.show()
mw.move(QCursor.pos())
sys.exit(app.exec_())









"""
# TODO
    - Value slider not updating properly
    - Values not left aligned
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

from cgwidgets.settings import attrs
from cgwidgets.widgets import ColorInputWidget

# set up main widget
app = QApplication(sys.argv)
mw = QWidget()
l = QVBoxLayout(mw)
test_label = QLabel('lkjasdf')

# create user input event
def userInputEvent(widget, color):
    test_label.setText(repr(color.getRgb()))

# create widget
color_widget = ColorInputWidget()

# set up custom user event
color_widget.setUserInput(userInputEvent)

# set position of header
color_widget.setHeaderPosition(position=attrs.NORTH)

# set direction of gradient slider
color_widget.setLinearCrosshairDirection(Qt.Horizontal)

# add widgets to main widget
l.addWidget(test_label)
l.addWidget(color_widget)

# show
mw.show()
mw.move(QCursor.pos())
sys.exit(app.exec_())









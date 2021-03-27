import sys, os
os.environ['QT_API'] = 'pyside2'
from qtpy import API_NAME
from qtpy.QtWidgets import QApplication

from __CreateFrame__ import createFrame

from cgwidgets.widgets import (
    BooleanInputWidget,
    ButtonInputWidget,
    StringInputWidget,
    FloatInputWidget,
    IntInputWidget,
    PlainTextInputWidget,
    ListInputWidget,
    LabelWidget
)

app = QApplication(sys.argv)

print(API_NAME)
widget = StringInputWidget()
widget.show()
sys.exit(app.exec_())
import sys, os
os.environ['QT_API'] = 'pyside2'
import qtpy
from qtpy.QtWidgets import QApplication

print(qtpy.API_NAME)
print(qtpy.PYSIDE2_API)
print(qtpy.PYSIDE_VERSION)

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


def test(widget):
    print ("test", widget)

widget = ButtonInputWidget(title="Test", user_clicked_event=test)

widget.show()
sys.exit(app.exec_())
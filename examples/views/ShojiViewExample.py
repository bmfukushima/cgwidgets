"""
TANSU VIEW

The Shoji View is essentially a QSplitter that has the option to
allow any widget inside of it to become full screen using the
the hotkey set with setSoloViewHotkey(), by default this is set to
tilda, "~", or 96 (note: right now 96 is hard coded as ~ seems to be
hard to get Qt to register in their Key_KEY shit).  Using the ALT modifier
when using multiple Shoji Views embedded inside each other will make
the current Shoji View full screen, rather than the widget that it is
hovering over.  The user can leave full screen by hitting the "ESC" key.

Widgets can be added/inserted with the kwarg "is_soloable", to stop the
widget from being able to be solo'd, or force it to be on in some
scenerios.  This kwarg controls an attribute "not_soloable" on the child widget.
Where if the attribute exists, the child will not be able to be solo'd, and if the
attribute does not exist, the child will be soloable.

NOTE:
    On systems using GNOME such as Ubuntu 20.04, you may need to disable
    the "Super/Alt+Tilda" system level hotkey which is normally set to
        "Switch windows of an application"
    Alt+Esc
        "Switch windows directly"
"""
import sys
from qtpy.QtWidgets import QApplication, QLabel
from qtpy.QtGui import QCursor
from qtpy.QtCore import Qt

from cgwidgets.views import ShojiView
from cgwidgets.widgets import StringInputWidget

app = QApplication(sys.argv)
class DisplayLabel(StringInputWidget):
    def __init__(self, parent=None):
        super(DisplayLabel, self).__init__(parent)
        self.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)

# create shoji
main_shoji_widget = ShojiView()
embedded_shoji_01 = ShojiView(orientation=Qt.Horizontal)
embedded_shoji_02 = ShojiView(orientation=Qt.Vertical)

# OPTIONAL | set handle length (if not set, by default this will be full length)
main_shoji_widget.setHandleLength(100)
main_shoji_widget.setHandleWidth(5)
main_shoji_widget.setIsHandleStatic(False)
main_shoji_widget.setIsSoloViewEnabled(True)
main_shoji_widget.setOrientation(Qt.Vertical)

# set up events
def toggleSoloEvent(enabled, widget):
    print(enabled, widget)

main_shoji_widget.setToggleSoloViewEvent(toggleSoloEvent)

# add regular widgets
for char in "SINE.":
    # main widget
    widget = DisplayLabel(char)
    main_shoji_widget.addWidget(widget, is_soloable=False)

    # embedded_shoji_02
    l = DisplayLabel(str(char))
    embedded_shoji_02.addWidget(l)

# add embedded Shoji Views
for x in range(3):
    l = DisplayLabel(str(x))
    embedded_shoji_01.addWidget(l)

embedded_shoji_01.addWidget(embedded_shoji_02)

# add shoji to shoji
main_shoji_widget.addWidget(embedded_shoji_01)

# show widget
main_shoji_widget.show()
main_shoji_widget.move(QCursor.pos())
main_shoji_widget.resize(512, 512)
sys.exit(app.exec_())


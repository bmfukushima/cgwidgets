"""
TANSU VIEW

The Tansu View is essentially a QSplitter that has the option to
allow any widget inside of it to become full screen using the
the hotkey set with setSoloViewHotkey(), by default this is set to
tilda, "~", or 96 (note: right now 96 is hard coded as ~ seems to be
hard to get Qt to register in their Key_KEY shit).  Using the ALT modifier
when using multiple Tansu Views embedded inside each other will make
the current Tansu View full screen, rather than the widget that it is
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

from cgwidgets.views import TansuView
from cgwidgets.widgets import StringInputWidget, FloatInputWidget
from cgwidgets.settings.colors import iColor

app = QApplication(sys.argv)
class DisplayLabel(StringInputWidget):
    def __init__(self, parent=None):
        super(DisplayLabel, self).__init__(parent)
        self.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)

# create tansu
main_tansu_widget = TansuView()
embedded_tansu_01 = TansuView(orientation=Qt.Horizontal)
embedded_tansu_02 = TansuView(orientation=Qt.Vertical)

# OPTIONAL | set handle length (if not set, by default this will be full length)
main_tansu_widget.setHandleLength(100)
main_tansu_widget.setHandleWidth(5)
main_tansu_widget.setIsHandleStatic(False)
main_tansu_widget.setIsSoloViewEnabled(True)
main_tansu_widget.setOrientation(Qt.Vertical)

# add regular widgets
for char in "SINE.":
    # main widget
    widget = DisplayLabel(char)
    main_tansu_widget.addWidget(widget, is_soloable=False)

    # embedded_tansu_02
    l = DisplayLabel(str(char))
    embedded_tansu_02.addWidget(l)

# add embedded Tansu Views
for x in range(3):
    l = DisplayLabel(str(x))
    embedded_tansu_01.addWidget(l)

embedded_tansu_01.addWidget(embedded_tansu_02)

# add tansu to tansu
main_tansu_widget.addWidget(embedded_tansu_01)
# show widget
main_tansu_widget.show()
main_tansu_widget.move(QCursor.pos())
main_tansu_widget.resize(512, 512)
sys.exit(app.exec_())


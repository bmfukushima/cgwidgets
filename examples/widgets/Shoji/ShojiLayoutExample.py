"""
SHOJI VIEW

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
from qtpy.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from qtpy.QtGui import QCursor
from qtpy.QtCore import Qt

from cgwidgets.widgets import ShojiLayout
from cgwidgets.widgets import StringInputWidget, LabelWidget

app = QApplication(sys.argv)
class DisplayLabel(StringInputWidget):
    def __init__(self, parent=None):
        super(DisplayLabel, self).__init__(parent)
        self.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)

# class DisplayLabel(LabelWidget):
#     def __init__(self, parent=None, text=None, image=None):
#         super(DisplayLabel, self).__init__(parent=parent, text=text, image=image)
#         self.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)

# create shoji
main_widget = ShojiLayout()
embedded_shoji_01 = ShojiLayout(orientation=Qt.Horizontal)
embedded_shoji_02 = ShojiLayout(orientation=Qt.Vertical)

# set custom base setyle sheet
# base_style_sheet = """
# {type}{{
#     background-color: rgba(0,255,0,255);
#     color: rgba(128,128,128,255);
#     border: 2px solid rgba(255,0,0,255);
# }}""".format(
#             type=type(main_widget).__name__,
#         )
# main_widget.setBaseStyleSheet(base_style_sheet)



# OPTIONAL | set handle length (if not set, by default this will be full length)
main_widget.setHandleLength(100)
main_widget.setHandleWidth(5)
main_widget.setIsHandleStatic(False)
main_widget.setIsSoloViewEnabled(True)
main_widget.setOrientation(Qt.Vertical)

# set up events
def toggleSoloEvent(enabled, widget):
    print(enabled, widget)

main_widget.setToggleSoloViewEvent(toggleSoloEvent)

# add regular widgets
for char in "SINE.":
    # main widget
    widget = DisplayLabel(char)
    main_widget.addWidget(widget, is_soloable=False)
    #widget.setStyleSheet("background-color: rgba(255,0,0,255)")
    widget.setContentsMargins(0,0,0,0)

    # embedded_shoji_02
    l = DisplayLabel(str(char))

    embedded_shoji_02.addWidget(l)

# add embedded Shoji Views
for x in range(3):
    l = DisplayLabel(str(x))

    embedded_shoji_01.addWidget(l)

embedded_shoji_01.addWidget(embedded_shoji_02)

# add shoji to shoji
main_widget.addWidget(embedded_shoji_01)

# show widget

main_widget.show()
main_widget.move(QCursor.pos())
main_widget.resize(512, 512)


sys.exit(app.exec_())


import sys
from qtpy.QtWidgets import QApplication, QLabel
from qtpy.QtGui import QCursor
from qtpy.QtCore import Qt
from cgwidgets.views import TansuView
from cgwidgets.widgets import TansuModelViewWidget

app = QApplication(sys.argv)

# create tansu
main_tansu_widget = TansuView()

# OPTIONAL | set handle length (if not set, by default this will be full length)
main_tansu_widget.setHandleLength(100)
main_tansu_widget.setHandleWidth(5)
main_tansu_widget.setIsHandleStatic(False)
main_tansu_widget.setIsSoloViewEnabled(True)
main_tansu_widget.setOrientation(Qt.Vertical)

# add widgets
for char in "SINE.":
    widget = QLabel(char)
    main_tansu_widget.addWidget(widget)
    widget.setStyleSheet("color: rgba(255,0,0,255)")

# create second tansu widget
tansu_widget_2 = TansuView(orientation=Qt.Horizontal)
tansu_widget_2.setObjectName("embed")

# add widgets
for x in range(3):
    l = QLabel(str(x))
    tansu_widget_2.addWidget(l)
    l.setStyleSheet("color: rgba(255,0,0,255)")

# add tansu to tansu
main_tansu_widget.addWidget(tansu_widget_2)

from cgwidgets.widgets import TansuGroupInputWidget, FloatInputWidget, LabelledInputWidget

def asdf(item, widget, value):
    return

# add model view
mvw = TansuGroupInputWidget()
inputs = ["cx", "cy", "fx", "fy", "radius"]  # , stops"""
for i in inputs:
    mvw.insertInputWidget(0, FloatInputWidget, i, asdf,
                           user_live_update_event=asdf, default_value=0.5)

labelled_input = LabelledInputWidget(name="test", widget_type=FloatInputWidget)

main_tansu_widget.addWidget(mvw)
main_tansu_widget.addWidget(labelled_input)
# show widget
main_tansu_widget.show()
main_tansu_widget.move(QCursor.pos())
main_tansu_widget.resize(512, 512)
sys.exit(app.exec_())


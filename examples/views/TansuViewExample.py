"""
TANSU VIEW

The Tansu View is essentially a QSplitter that has the option to
allow any widget inside of it to become full screen using the
the hotkey set with setSoloViewHotkey(), by default this is set to
tilda, "~", or 96 (note: right now 96 is hard coded as ~ seems to be
hard to get Qt to register in their Key_KEY shit)

The user can leave full screen by hitting the "ESC" key.

"""

import sys
from qtpy.QtWidgets import QApplication, QLabel
from qtpy.QtGui import QCursor
from qtpy.QtCore import Qt
from cgwidgets.views import TansuView
from cgwidgets.widgets import TansuModelViewWidget

app = QApplication(sys.argv)

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
    widget = QLabel(char)
    main_tansu_widget.addWidget(widget)
    widget.setStyleSheet("color: rgba(255,0,0,255)")

# add embedded Tansu Views
for x in range(3):
    l = QLabel(str(x))
    embedded_tansu_01.addWidget(l)
    l.setStyleSheet("color: rgba(255,0,0,255)")

    l = QLabel(str(x))
    embedded_tansu_02.addWidget(l)
    l.setStyleSheet("color: rgba(255,0,0,255)")

embedded_tansu_01.addWidget(embedded_tansu_02)

# add tansu to tansu
main_tansu_widget.addWidget(embedded_tansu_01)

# show widget
main_tansu_widget.show()
main_tansu_widget.move(QCursor.pos())
main_tansu_widget.resize(512, 512)
sys.exit(app.exec_())


from qtpy.QtCore import Qt

from cgwidgets.widgets import TansuModelViewWidget, TansuBaseWidget
from cgwidgets.utils import attrs

import sys
from qtpy.QtWidgets import QApplication, QLabel, QVBoxLayout
from qtpy.QtGui import QCursor

app = QApplication(sys.argv)

w = TansuModelViewWidget()
tab_1 = QLabel('hello')
tab_2 = QLabel('world')
tab_3 = TansuBaseWidget()
tab_3.setObjectName("main")
tab_3.addWidget(QLabel('a'))
tab_3.addWidget(QLabel('b'))
tab_3.addWidget(QLabel('c'))

# set attrs
w.setHeaderPosition(attrs.NORTH)
w.setMultiSelect(True)
w.setMultiSelectDirection(Qt.Vertical)

# insert tabs
w.insertTansuWidget(0, '<title> hello', widget=tab_1)
w.insertTansuWidget(0, '<title> world', widget=tab_2)
w.insertTansuWidget(0, '<title> tansu', widget=tab_3)

w.resize(500, 500)
w.delegateWidget().handle_length = 100

w.show()

w.move(QCursor.pos())
sys.exit(app.exec_())
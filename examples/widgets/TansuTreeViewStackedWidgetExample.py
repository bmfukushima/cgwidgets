from qtpy.QtCore import Qt

from cgwidgets.widgets import TansuModelViewWidget, TansuHeaderTreeView
from cgwidgets.utils import attrs

import sys
from qtpy.QtWidgets import QApplication, QLabel, QVBoxLayout
from qtpy.QtGui import QCursor

app = QApplication(sys.argv)

w = TansuModelViewWidget()

view = TansuHeaderTreeView()

w.setHeaderWidget(view)
w.setHeaderPosition(attrs.WEST)
w.setMultiSelect(True)
w.setMultiSelectDirection(Qt.Vertical)

view.setHeaderData(['name', 'one', 'two'])

for x in range(3):
    widget = QLabel(str(x))
    parent_item = w.insertTansuWidget(x, data={'name': str(x)}, widget=widget)

for y in range(0, 2):
    w.insertTansuWidget(y, data={'name': str(y)}, widget=widget, parent=parent_item)

w.resize(500, 500)
w.delegateWidget().handle_length = 100

w.show()

w.move(QCursor.pos())
sys.exit(app.exec_())
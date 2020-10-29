import sys

from qtpy.QtWidgets import QApplication, QLabel, QAbstractItemView
from qtpy.QtCore import Qt
from qtpy.QtGui import QCursor

from cgwidgets.widgets import TansuModelViewWidget, TansuHeaderTreeView
from cgwidgets.utils import attrs

app = QApplication(sys.argv)

# create widget
tansu_widget = TansuModelViewWidget()

# create view
view = TansuHeaderTreeView()

# setup header
tansu_widget.setHeaderWidget(view)
tansu_widget.setHeaderPosition(attrs.WEST)
tansu_widget.setMultiSelect(True)
tansu_widget.setMultiSelectDirection(Qt.Vertical)
tansu_widget.delegateWidget().handle_length = 100

# set header data
view.setHeaderData(['name', 'one', 'two'])

# insert widgets
for x in range(5):
    widget = QLabel(str(x))
    parent_item = tansu_widget.insertTansuWidget(x, column_data={'name': str(x)}, widget=widget)

# insert child widgets
for y in range(0, 2):
    tansu_widget.insertTansuWidget(y, column_data={'name': str(y), 'one': 'datttaaa'}, widget=widget, parent=parent_item)

# enable drag/drop
tansu_widget.setHeaderDragDropMode(QAbstractItemView.DragDropMode.InternalMove)

# show view
tansu_widget.resize(500, 500)
tansu_widget.show()
tansu_widget.move(QCursor.pos())
sys.exit(app.exec_())
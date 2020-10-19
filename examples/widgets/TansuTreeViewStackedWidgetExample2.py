from qtpy.QtCore import Qt

from cgwidgets.widgets import TansuModelViewWidget, TansuHeaderTreeView
from cgwidgets.utils import attrs

import sys
from qtpy.QtWidgets import QApplication, QLabel, QVBoxLayout, QAbstractItemView
from qtpy.QtCore import QItemSelectionModel, QItemSelection, QModelIndex
from qtpy.QtGui import QCursor

app = QApplication(sys.argv)
class SelectionModel(QItemSelectionModel):
    def __init__(self, parent=None):
        QItemSelectionModel.__init__(self, parent)

    def onModelItemsReordered(self):
        new_selection = QItemSelection()
        new_index = QModelIndex()
        for item in self.model().lastDroppedItems:
            row = self.model().rowForItem(item)
            if row is None:
                continue
            new_index = self.model().index(row, 0, QModelIndex())
            new_selection.select(new_index, new_index)

        self.clearSelection()
        flags = QItemSelectionModel.ClearAndSelect | \
                QItemSelectionModel.Rows | \
                QItemSelectionModel.Current
        self.select(new_selection, flags)
        self.setCurrentIndex(new_index, flags)

# create widget
w = TansuModelViewWidget()

# create view
view = TansuHeaderTreeView()
model = w.model()
selectionModel = SelectionModel(model)
model.dragDropFinished.connect(selectionModel.onModelItemsReordered)

view.setDragDropMode(QAbstractItemView.InternalMove)
view.setDragEnabled(True)
view.setAcceptDrops(True)
# setup custottrs
w.setHeaderWidget(view)
w.setHeaderPosition(attrs.WEST)
w.setMultiSelect(True)
w.setMultiSelectDirection(Qt.Vertical)
w.delegateWidget().handle_length = 100

# set header data
view.setHeaderData(['name', 'one', 'two'])

# insert widgets
for x in range(3):
    widget = QLabel(str(x))
    parent_item = w.insertTansuWidget(x, column_data={'name': str(x)}, widget=widget)

# insert child widgets
for y in range(0, 2):
    w.insertTansuWidget(y, column_data={'name': str(y)}, widget=widget, parent=parent_item)

w.resize(500, 500)

w.show()

w.move(QCursor.pos())
sys.exit(app.exec_())
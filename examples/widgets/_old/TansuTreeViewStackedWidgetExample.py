import sys

from qtpy.QtWidgets import QApplication, QLabel, QAbstractItemView
from qtpy.QtCore import Qt
from qtpy.QtGui import QCursor

from cgwidgets.widgets import ShojiModelViewWidget, ModelViewWidget
from cgwidgets.settings import attrs

app = QApplication(sys.argv)

# create widget
shoji_widget = ShojiModelViewWidget()
shoji_widget.setHeaderViewType(ModelViewWidget.TREE_VIEW)
# # create view
# view = ShojiHeaderTreeView()
#
# # setup header
# shoji_widget.setHeaderViewWidget(view)

# set header names
shoji_widget.setHeaderData(['name', 'one', 'two'])

# header position
shoji_widget.setHeaderPosition(attrs.WEST)

# setup multi selection
shoji_widget.setMultiSelect(True)
shoji_widget.setMultiSelectDirection(Qt.Vertical)

# set handle width
shoji_widget.delegateWidget().setHandleLength(100)


# insert widgets
for x in range(5):
    widget = QLabel(str(x))
    parent_item = shoji_widget.insertShojiWidget(x, column_data={'name': str(x)}, widget=widget)

# insert child widgets
for y in range(0, 2):
    widget = QLabel(str("SINE."))
    shoji_widget.insertShojiWidget(y, column_data={'name': str(y), 'one': 'datttaaa'}, widget=widget, parent=parent_item)

# enable drag/drop
shoji_widget.setHeaderItemIsDragEnabled(True)
shoji_widget.setHeaderItemIsDropEnabled(True)
shoji_widget.setHeaderItemIsEditable(False)

#print(shoji_widget.headerWidget().setPresetViewType(ModelViewWidget.TREE_VIEW))
#shoji_widget.setHeaderViewType(ModelViewWidget.TREE_VIEW)

# from qtpy.QtWidgets import QTreeView
# view = QTreeView()
# # setKeyPressEvent(function(QEvent.KeyPress))
# # createStyleSheet() returns StyleSheet
#
# # setup header
# shoji_widget.setHeaderViewWidget(view)

# show view
shoji_widget.resize(500, 500)
shoji_widget.show()
shoji_widget.move(QCursor.pos())
sys.exit(app.exec_())
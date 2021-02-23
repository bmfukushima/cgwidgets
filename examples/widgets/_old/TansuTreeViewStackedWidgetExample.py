import sys

from qtpy.QtWidgets import QApplication, QLabel, QAbstractItemView
from qtpy.QtCore import Qt
from qtpy.QtGui import QCursor

from cgwidgets.widgets import ShojiModelViewWidget, ModelViewWidget
from cgwidgets.utils import attrs

app = QApplication(sys.argv)

# create widget
tansu_widget = ShojiModelViewWidget()
tansu_widget.setHeaderViewType(ModelViewWidget.TREE_VIEW)
# # create view
# view = ShojiHeaderTreeView()
#
# # setup header
# tansu_widget.setHeaderViewWidget(view)

# set header names
tansu_widget.setHeaderData(['name', 'one', 'two'])

# header position
tansu_widget.setHeaderPosition(attrs.WEST)

# setup multi selection
tansu_widget.setMultiSelect(True)
tansu_widget.setMultiSelectDirection(Qt.Vertical)

# set handle width
tansu_widget.delegateWidget().setHandleLength(100)


# insert widgets
for x in range(5):
    widget = QLabel(str(x))
    parent_item = tansu_widget.insertShojiWidget(x, column_data={'name': str(x)}, widget=widget)

# insert child widgets
for y in range(0, 2):
    widget = QLabel(str("SINE."))
    tansu_widget.insertShojiWidget(y, column_data={'name': str(y), 'one': 'datttaaa'}, widget=widget, parent=parent_item)

# enable drag/drop
tansu_widget.setHeaderItemIsDragEnabled(True)
tansu_widget.setHeaderItemIsDropEnabled(True)
tansu_widget.setHeaderItemIsEditable(False)

#print(tansu_widget.headerWidget().setViewType(ModelViewWidget.TREE_VIEW))
#tansu_widget.setHeaderViewType(ModelViewWidget.TREE_VIEW)

# from qtpy.QtWidgets import QTreeView
# view = QTreeView()
# # setKeyPressEvent(function(QEvent.KeyPress))
# # createStyleSheet() returns StyleSheet
#
# # setup header
# tansu_widget.setHeaderViewWidget(view)

# show view
tansu_widget.resize(500, 500)
tansu_widget.show()
tansu_widget.move(QCursor.pos())
sys.exit(app.exec_())
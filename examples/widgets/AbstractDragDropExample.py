import sys
from qtpy.QtWidgets import (
    QApplication, QTreeView, QListView, QAbstractItemView)
from qtpy.QtGui import QCursor

from cgwidgets.views import (
    AbstractDragDropModel,
    AbstractDragDropModelDelegate,
    AbstractDragDropIndicator,
    AbstractDragDropTreeView,
    AbstractDragDropListView,
    AbstractDragDropAbstractView
)

app = QApplication(sys.argv)

# create event functions
def testDrag(indexes):
    print(indexes)

def testDrop(row, indexes, parent):
    print(row, indexes, parent)

def testEdit(item, old_value, new_value):
    print(item, old_value, new_value)

def testEnable(item, enabled):
    print(item.columnData()['name'], enabled)

def testDelete(item):
    print(item.columnData()['name'])

# create model
model = AbstractDragDropModel()

# create views
tree_view = AbstractDragDropTreeView()
tree_view.setModel(model)

list_view = AbstractDragDropListView()
list_view.setModel(model)

# insert indexes
for x in range(0, 4):
    model.insertNewIndex(x, str('node%s'%x))

# set model event
model.setDragStartEvent(testDrag)
model.setDropEvent(testDrop)
model.setTextChangedEvent(testEdit)
model.setItemEnabledEvent(testEnable)
model.setItemDeleteEvent(testDelete)

# set flags
tree_view.setIsRootDropEnabled(True)
tree_view.setIsEditable(True)
tree_view.setIsDragEnabled(True)
tree_view.setIsDropEnabled(True)
tree_view.setIsEnableable(True)
tree_view.setIsDeleteEnabled(True)

# set selection mode
tree_view.setSelectionMode(QAbstractItemView.MultiSelection)

# show
tree_view.move(QCursor.pos())
tree_view.show()
sys.exit(app.exec_())
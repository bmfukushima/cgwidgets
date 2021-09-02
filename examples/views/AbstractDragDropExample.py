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
def testDelete(item):
    print("DELETING --> -->", item.columnData()['name'])

def testDrag(items, model):
    print(items)
    print("DRAGGING -->", items)

def testDrop(data, indexes, self, row, parent_item):
    print("DROPPING -->", data, indexes, self, row, parent_item)

def testEdit(item, old_value, new_value):
    print("EDITING -->", item, old_value, new_value)

def testEnable(item, enabled):
    print("ENABLING -->", item.columnData()['name'], enabled)

def testSelect(item, enabled):
    print("SELECTING -->", item.columnData()['name'], enabled)


# create model
model = AbstractDragDropModel()

from cgwidgets.views import AbstractDragDropModel, AbstractDragDropModelItem
# model = AbstractDragDropModel()
# item_type = AbstractDragDropModelItem()
# model.setItemType(item_type)

# create views
tree_view = AbstractDragDropTreeView()
tree_view.setModel(model)

list_view = AbstractDragDropListView()
list_view.setModel(model)

# insert indexes
for x in range(0, 4):
    index = model.insertNewIndex(x, name=str('node%s'%x))
    for i, char in enumerate('abc'):
        model.insertNewIndex(i, name=char, parent=index)


# set model event
model.setDragStartEvent(testDrag)
model.setDropEvent(testDrop)
model.setTextChangedEvent(testEdit)
model.setItemEnabledEvent(testEnable)
model.setItemDeleteEvent(testDelete)
model.setItemSelectedEvent(testSelect)

# set flags
tree_view.setIsRootDroppable(True)
tree_view.setIsEditable(True)
tree_view.setIsDraggable(True)
tree_view.setIsDroppable(True)
tree_view.setIsEnableable(True)
tree_view.setIsDeletable(True)

# set selection mode
tree_view.setSelectionMode(QAbstractItemView.MultiSelection)

#list_view.setIndexSelected(index, True)
# show
# tree_view.move(QCursor.pos())
# tree_view.show()

###########################################
# new...
###########################################
from qtpy.QtWidgets import QWidget, QVBoxLayout, QPushButton

def testSelectToggle():
    """    match(const
    QModelIndex & start, int
    role, const
    QVariant & value, int
    hits = 1, Qt::MatchFlags
    flags = Qt::MatchFlags(Qt::MatchStartsWith | Qt::MatchWrap)) const"""

    from qtpy.QtCore import Qt, QVariant
    #from qtpy.QtGui import QVar
    #index = model.getIndexFromItem(item)
    # https://doc.qt.io/archives/qt-4.8/qt.html#MatchFlag-enum
    # , flags=Qt.MatchFlags(Qt.MatchContains)
    global model
    indexes = model.findItems('a')

    for index in indexes:
        item = index.internalPointer()
        print(item.columnData())
        tree_view.setIndexSelected(index, True)
    from cgwidgets.utils import updateStyleSheet
    #updateStyleSheet(tree_view)

# add context menu
def contextMenu(index, selected_indexes):
    print(index, selected_indexes)

tree_view.addContextMenuEvent('test', contextMenu)

w = QWidget()
button = QPushButton("SINE.")
button.clicked.connect(testSelectToggle)
l = QVBoxLayout(w)
l.addWidget(tree_view)
l.addWidget(button)

w.move(QCursor.pos())
w.show()

###########################################
# end new ...
###########################################

sys.exit(app.exec_())
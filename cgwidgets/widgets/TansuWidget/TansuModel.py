# https://doc.qt.io/qt-5/model-view-programming.html#model-view-classes

"""
TODO:
    *   Add drag/drop
    *   Add multiple columns
            rows --> TansuModelItem
                                | -- column list (holds data for each column of this row...)

"""

from qtpy.QtCore import (
    Qt, QModelIndex, QAbstractItemModel, QSize, QMimeData, QByteArray,
    QDataStream, QIODevice)
from qtpy.QtGui import (
    QBrush, QColor
)

import sys

from cgwidgets.views import AbstractDragDropModel

# https://doc.qt.io/qt-5/model-view-programming.html#model-view-classes
from cgwidgets.widgets.TansuWidget import (
    iTansuDynamicWidget
)

from cgwidgets.views import AbstractDragDropModelItem


class TansuModelItem(AbstractDragDropModelItem, iTansuDynamicWidget):
    """
    Attributes:
        delegate_widget (QWidget): Widget to be shown when this item is
            selected
        dynamic_widget_base_class (QWidget): Widget to be shown when this item is
            selected if the Tansu is in DYNAMIC mode.
    """
    def __init__(self, parent=None):
        #self._data = data
        self._column_data = {}
        self._children = []
        self._parent = parent
        self._delegate_widget = None
        self._dynamicWidgetFunction = None

        self._test = True
        #self._is_selected = False
        self._is_enabled = True
        self._isSelectable = True
        self._isDragEnabled = True
        self._isDropEnabled = True
        self._isEditable = True
        if parent is not None:
            parent.addChild(self)

    @property
    def test(self):
        return self._test

    @test.setter
    def test(self, test):
        self._test = test

    def delegateWidget(self):
        return self._delegate_widget

    def setDelegateWidget(self, _delegate_widget):
        self._delegate_widget = _delegate_widget


class TansuModel(AbstractDragDropModel):
    """
    Abstract model that is used for the Tansu.  This supports lists, and
    trees.

    Attributes:
        item_type (Item): Data item to be stored on each index.  By default this
            set to the TansuModelItem

    TODO:
        *   I dont think I need <header_type> anymore...
    """
    ITEM_HEIGHT = 35
    ITEM_WIDTH = 100

    def __init__(self, parent=None, root_item=None):
        super(TansuModel, self).__init__(parent, root_item=root_item)
        #self._header_type = ''
        self.setItemType(TansuModelItem)

    # @property
    # def header_type(self):
    #     return self._header_type
    #
    # @header_type.setter
    # def header_type(self, _header_type):
    #     self._header_type = _header_type


if __name__ == '__main__':
    from qtpy.QtWidgets import (
        QApplication, QTreeView, QListView, QTableView, QAbstractItemView)
    from qtpy.QtGui import QCursor
    app = QApplication(sys.argv)

    #QTreeView()

    model = TansuModel()
    for x in range(0, 4):
        model.insertNewIndex(x, str('node%s'%x))
    #model.insertRows(0, 3, QModelIndex())
    #index = model.index(0, 1, QModelIndex())
    #item = model.getItem(index)

    #parent_index = model.index(0, 1, QModelIndex())
    #parent_item = parent_index.internalPointer()
    #TansuModelItem("child", parent_item)

    tree_view = QTreeView()

    tree_view.move(QCursor.pos())
    tree_view.setDragEnabled(True)
    tree_view.setDragDropOverwriteMode(False)
    tree_view.setSelectionMode(QAbstractItemView.MultiSelection)
    # tree_view.viewport().setAcceptDrops(True)
    # tree_view.setDropIndicatorShown(True)

    tree_view.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
    tree_view.setModel(model)



    list_view = QListView()

    list_view.move(QCursor.pos())
    list_view.setDragDropOverwriteMode(False)
    list_view.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
    list_view.setDropIndicatorShown(True)
    list_view.setModel(model)

    # table_view = QTableView()
    # table_view.show()
    tree_view.show()
    #list_view.show()
    # table_view.setModel(model)

    sys.exit(app.exec_())
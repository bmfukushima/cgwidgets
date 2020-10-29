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

from cgwidgets.widgets.TansuWidget import TansuModelItem
from cgwidgets.views import AbstractDragDropModel


class TansuModel(AbstractDragDropModel):
    """
    Abstract model that is used for the Tansu.  This supports lists, and
    trees.

    Attributes:
        item_type (Item): Data item to be stored on each index.  By default this
            set to the TansuModelItem
    """
    ITEM_HEIGHT = 35
    ITEM_WIDTH = 100

    def __init__(self, parent=None, root_item=None):
        super(TansuModel, self).__init__(parent, root_item=root_item)
        self._header_type = ''
        self.setItemType(TansuModelItem)

    def flags(self, index):
        # List view handlers
        if 'List' in self.header_type:
            if not index.isValid():
                return Qt.ItemIsDropEnabled
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | \
                   Qt.ItemIsDragEnabled

        # Tree view handlers
        elif 'Tree' in self.header_type:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | \
                   Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled

        # I failed at something handlers
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | \
               Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled

    @property
    def header_type(self):
        return self._header_type

    @header_type.setter
    def header_type(self, _header_type):
        self._header_type = _header_type


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
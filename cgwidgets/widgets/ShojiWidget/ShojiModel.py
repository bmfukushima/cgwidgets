import sys

# https://doc.qt.io/qt-5/model-view-programming.html#model-view-classes
from cgwidgets.widgets import AbstractShojiModel, AbstractShojiModelItem


class ShojiModelItem(AbstractShojiModelItem):
    """
    Attributes:
        delegate_widget (QWidget): Widget to be shown when this item is
            selected
        dynamic_widget_base_class (QWidget): Widget to be shown when this item is
            selected if the Shoji is in DYNAMIC mode.
        image_path (str): path on disk to image to be displayed as overlay
        display_overlay (bool) determines if the overlay for this should be dispalyed
            or not.
    """
    def __init__(self, parent=None):
        super(ShojiModelItem, self).__init__(parent)


class ShojiModel(AbstractShojiModel):
    """
    Abstract model that is used for the Shoji.  This supports lists, and
    trees.

    Attributes:
        item_type (Item): Data item to be stored on each index.  By default this
            set to the ShojiModelItem
    """
    def __init__(self, parent=None, root_item=None):
        super(ShojiModel, self).__init__(parent, root_item=root_item)


if __name__ == '__main__':
    from qtpy.QtWidgets import (
        QApplication, QTreeView, QListView, QTableView, QAbstractItemView)
    from qtpy.QtGui import QCursor
    app = QApplication(sys.argv)

    #QTreeView()

    model = ShojiModel()
    for x in range(0, 4):
        model.insertNewIndex(x, str('node%s'%x))
    #model.insertRows(0, 3, QModelIndex())
    #index = model.index(0, 1, QModelIndex())
    #item = model.getItem(index)

    #parent_index = model.index(0, 1, QModelIndex())
    #parent_item = parent_index.internalPointer()
    #ShojiModelItem("child", parent_item)

    tree_view = QTreeView()

    tree_view.move(QCursor.pos())
    tree_view.setDraggable(True)
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
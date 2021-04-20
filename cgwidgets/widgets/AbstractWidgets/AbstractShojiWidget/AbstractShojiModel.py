# https://doc.qt.io/qt-5/model-view-programming.html#model-view-classes

"""
TODO:
    *   Add drag/drop
    *   Add multiple columns
            rows --> AbstractShojiModelItem
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
#from cgwidgets.widgets.ShojiWidget import (iShojiDynamicWidget)

from .iShojiDynamicWidget import iShojiDynamicWidget
from cgwidgets.views import AbstractDragDropModelItem


class AbstractShojiModelItem(AbstractDragDropModelItem, iShojiDynamicWidget):
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
        super(AbstractShojiModelItem, self).__init__(parent)
        #self._data = data
        self._column_data = {}
        self._children = []
        self._parent = parent
        self._delegate_widget = None
        self._dynamicWidgetFunction = None

        self._image_path = None
        self._display_overlay = False
        self._display_delegate_title = None
        self._text_color = None

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

    def textColor(self):
        return self._text_color

    def setTextColor(self, enabled):
        self._text_color = enabled

    def displayDelegateTitle(self):
        return self._display_delegate_title

    def setDisplayDelegateTitle(self, enabled):
        self._display_delegate_title = enabled

    def displayOverlay(self):
        return self._display_overlay

    def setDisplayOverlay(self, enabled):
        self._display_overlay = enabled

    def imagePath(self):
        return self._image_path

    def setImagePath(self, image_path):
        self._image_path = image_path

    def delegateWidget(self):
        return self._delegate_widget

    def setDelegateWidget(self, _delegate_widget):
        self._delegate_widget = _delegate_widget


class AbstractShojiModel(AbstractDragDropModel):
    """
    Abstract model that is used for the Shoji.  This supports lists, and
    trees.

    Attributes:
        item_type (Item): Data item to be stored on each index.  By default this
            set to the AbstractShojiModelItem

    TODO:
        *   I dont think I need <header_type> anymore...
    """
    ITEM_HEIGHT = 35
    ITEM_WIDTH = 100

    def __init__(self, parent=None, root_item=None):
        super(AbstractShojiModel, self).__init__(parent, root_item=root_item)
        #self._header_type = ''
        self.setItemType(AbstractShojiModelItem)


if __name__ == '__main__':
    from qtpy.QtWidgets import (
        QApplication, QTreeView, QListView, QTableView, QAbstractItemView)
    from qtpy.QtGui import QCursor
    app = QApplication(sys.argv)

    #QTreeView()

    model = AbstractShojiModel()
    for x in range(0, 4):
        model.insertNewIndex(x, str('node%s'%x))
    #model.insertRows(0, 3, QModelIndex())
    #index = model.index(0, 1, QModelIndex())
    #item = model.getItem(index)

    #parent_index = model.index(0, 1, QModelIndex())
    #parent_item = parent_index.internalPointer()
    #AbstractShojiModelItem("child", parent_item)

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
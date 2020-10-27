# https://doc.qt.io/qt-5/model-view-programming.html#model-view-classes

"""
TODO:
    *   Add drag/drop
    *   Add multiple columns
            rows --> TansuModelItem
                                | -- column list (holds data for each column of this row...)

"""

from qtpy.QtCore import (
    Qt, QModelIndex, QAbstractItemModel, QSize, QMimeData, QByteArray)
from qtpy.QtGui import (
    QBrush, QColor
)

import sys

from cgwidgets.widgets.TansuWidget import TansuModelItem
from cgwidgets.settings.colors import iColor


class TansuModel(QAbstractItemModel):
    """
    Abstract model that is used for the Tansu.  This supports tables, lists, and
    trees.  However not yet...
    TODO:
        - Drag/drop support
        - multi column support

    Attributes:
        item_type (Item): Data item to be stored on each index.  By default this
            set to the TansuModelItem
    """
    ITEM_HEIGHT = 35
    ITEM_WIDTH = 100

    def __init__(self, parent=None, root_item=None):
        super(TansuModel, self).__init__(parent)
        # set up default item type
        self._item_type = TansuModelItem
        self._item_height = TansuModel.ITEM_HEIGHT
        self._item_width = TansuModel.ITEM_WIDTH

        # set up root item
        if not root_item:
            root_item = TansuModelItem()
            root_item.setColumnData({"name":"root"})
        self._root_item = root_item

        # setup default attrs
        self._header_data = ['name']

    """ UTILS """
    def rowCount(self, parent):
        """
        INPUTS: QModelIndex
        OUTPUT: int
        """
        if not parent.isValid():
            parent_item = self._root_item
        else:
            parent_item = parent.internalPointer()

        return parent_item.childCount()

    def columnCount(self, parent):
        """
        INPUTS: QModelIndex
       OUTPUT: int
       """
        return len(self._header_data)

    def data(self, index, role):
        """
        This is the main display class for the model.  Setting different
        display roles inside of this class will determine how the views
        will handle the model data

        INPUTS: QModelIndex, int
        OUTPUT: QVariant, strings are cast to QString which is a QVariant
        """
        if not index.isValid():
            return None

        item = index.internalPointer()

        if role == Qt.DisplayRole or role == Qt.EditRole:
            for i in range(self.columnCount(item)):
                if index.column() == i:
                    try:
                        return_val = item.columnData()[self._header_data[i]]
                    except KeyError:
                        return_val = None
                    return return_val

        if role == Qt.SizeHintRole:
            return QSize(self.item_width, self.item_height)

        if role == Qt.BackgroundRole:
            return None
        # if role == Qt.BackgroundRole:
        #     if item.isSelected():
        #         return QBrush(QColor(*iColor.rgba_gray_selected))
        #     else:
        #         return QBrush(QColor(*iColor.rgba_background))

    def setData(self, index, value, role=Qt.EditRole):
        """
        INPUTS: QModelIndex, QVariant, int (flag)
        """
        if index.isValid():
            if role == Qt.EditRole:
                item = index.internalPointer()
                arg = self._header_data[index.column()]
                item.columnData()[arg] = value
                return True
        return False

    def headerData(self, column, orientation, role):
        """
        Sets the header data for each column
        INPUTS: int, Qt::Orientation, int
        OUTPUT: QVariant, strings are cast to QString which is a QVariant
        """
        if role == Qt.DisplayRole:
            return self._header_data[column]
            # if column == 0:
            #     return "Scenegraph"
            # else:
            #     return "Typeinfo"

    def setHeaderData(self, _header_data):
        self._header_data = _header_data

    # def flags(self, index):
    #     """
    #     INPUTS: QModelIndex
    #     OUTPUT: int (flag)
    #     """
    #     return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def parent(self, index):
        """
        INPUTS: QModelIndex
        OUTPUT: QModelIndex
        Should return the parent of the item with the given QModelIndex"""
        item = self.getItem(index)
        parent_item = item.parent()

        if parent_item == self._root_item:
            return QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def index(self, row, column, parent):
        """
        Returns the QModelIndex associated with a row/column/parent provided

        Args:
                row (int)
                column (int)
                parent (QModelIndex)

        Returns (QModelIndex)
        """
        parent_item = self.getItem(parent)
        child_item = parent_item.child(row)

        if child_item:
            return self.createIndex(row, column, child_item)
        else:
            return QModelIndex()

    def getItem(self, index):
        """
        Returns the item held by the index provided
        Args:
            index (QModelIndex)
        Returns (TansuModelItem)
        """
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item

        return self._root_item

    def getItemName(self, item):
        name = item.columnData()[self._header_data[0]]
        return name

    """ Create index/items"""
    def setItemType(self, item_type):
        self._item_type = item_type

    def itemType(self):
        return self._item_type

    def createNewItem(self, *args, **kwargs):
        """
        Creates a new item of the specified type
        """
        item_type = self.itemType()
        new_item = item_type(*args, **kwargs)

        return new_item

    def insertNewIndex(self, row, name="None", parent=QModelIndex()):
        self.insertRow(row, parent)
        new_index = self.index(row, 0, parent)
        item = new_index.internalPointer()
        item.setColumnData({self._header_data[0]:name})

        return new_index

    """ INSERT INDEXES """
    def insertRows(self, position, num_rows, parent=QModelIndex()):
        """
        INPUTS: int, int, QModelIndex
        """
        parent_item = self.getItem(parent)
        self.beginInsertRows(parent, position, position + num_rows - 1)

        for row in range(num_rows):
            childCount = parent_item.childCount()
            childNode = self.createNewItem()
            success = parent_item.insertChild(position, childNode)

        self.endInsertRows()

        return success

    def removeRows(self, position, num_rows, parent=QModelIndex()):
        """INPUTS: int, int, QModelIndex"""
        parent_item = self.getItem(parent)
        self.beginRemoveRows(parent, position, position + num_rows - 1)

        for row in range(num_rows):
            success = parent_item.removeChild(position)

        self.endRemoveRows()

        return success

    def getRootItem(self):
        return self._root_item

    def setRootItem(self, root_item):
        self._root_item = root_item

    """ PROPERTIES """
    @property
    def item_height(self):
        return self._item_height

    @item_height.setter
    def item_height(self, _item_height):
        self._item_height = _item_height

    @property
    def item_width(self):
        return self._item_width

    @item_width.setter
    def item_width(self, _item_width):
        self._item_width = _item_width

    """ DRAG / DROP"""
    def getParentIndexFromItem(self, item):
        parent_item = item.parent()
        if parent_item == self.getRootItem():
            parent_index = QModelIndex()
        elif not parent_item:
            parent_index = QModelIndex()
        else:
            parent_index = self.createIndex(parent_item.row(), 0, parent_item)
        return parent_index

    def supportedDropActions(self):
        return Qt.MoveAction

    def flags(self, index):
        # if not index.isValid():
        #     return Qt.ItemIsEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | \
               Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled

    def mimeTypes(self):
        return ['application/x-qabstractitemmodeldatalist']

    def mimeData(self, indexes):
        self.indexes = [index.internalPointer() for index in indexes]

        mimedata = QMimeData()
        mimedata.setData('application/x-qabstractitemmodeldatalist', QByteArray())
        return mimedata

    def dropMimeData(self, data, action, row, column, parent):

        # get parent item
        parent_item = parent.internalPointer()
        if not parent_item:
            parent_item = self.getRootItem()

        print("parent item == %s"%parent_item.columnData()['name'])
        indexes = self.indexes
        for item in indexes:
            print(item.columnData()['name'])
            old_parent_item = item.parent()
            old_parent_index = self.getParentIndexFromItem(item)

            self.beginRemoveRows(old_parent_index, item.row(), item.row()+1)
            old_parent_item.children().remove(item)
            #old_parent_item.removeChild(item.row())
            self.endRemoveRows()

            # insert item
            self.beginInsertRows(parent, 0, 1)
            parent_item.insertChild(0, item)
            self.endInsertRows()
        return True


if __name__ == '__main__':
    from qtpy.QtWidgets import (
        QApplication, QTreeView, QListView, QTableView, QAbstractItemView)
    from qtpy.QtGui import QCursor
    app = QApplication(sys.argv)

    #QTreeView()

    model = TansuModel()
    for x in range(0,4):
        model.insertNewIndex(x, str('node%s'%x))
    #model.insertRows(0, 3, QModelIndex())
    #index = model.index(0, 1, QModelIndex())
    #item = model.getItem(index)

    #parent_index = model.index(0, 1, QModelIndex())
    #parent_item = parent_index.internalPointer()
    #TansuModelItem("child", parent_item)

    tree_view = QTreeView()
    tree_view.setDragDropOverwriteMode(True)
    tree_view.show()
    tree_view.move(QCursor.pos())
    tree_view.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)



    # list_view = QListView()
    # list_view.show()

    # table_view = QTableView()
    # table_view.show()

    tree_view.setModel(model)
    # list_view.setModel(model)
    # table_view.setModel(model)

    sys.exit(app.exec_())
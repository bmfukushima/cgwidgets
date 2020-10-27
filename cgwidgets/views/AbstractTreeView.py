"""
#https://github.com/d1vanov/PyQt5-reorderable-list-model
#https://doc.qt.io/qt-5.12/model-view-programming.html#using-drag-and-drop-with-item-views
#https://doc.qt.io/qt-5.12/model-view-programming.html#model-subclassing-reference

Notes:
    *   internalPointer is defined during the createIndex call.  Where you have
            the args (row, column, ptr)

"""

import sys
import pickle

from qtpy.QtWidgets import QApplication, QListView, QTreeView, QAbstractItemView
from qtpy.QtCore import (
    QAbstractItemModel, QModelIndex,
    Qt, QDataStream, QIODevice, QByteArray, QMimeData, QVariant
)
from qtpy.QtGui import QCursor, QColor

class AbstractTreeItem(object):
    def __init__(self, name, parent=None):
        self.name = name
        self._parent = parent
        self._children = []

        if parent:
            parent.addChild(self)

    def child(self, index):
        try:
            return self.children()[index]
        except:
            return None

    def childByName(self, name):
        for child in self.children():
            if child.name == name:
                return child
        return None

    def childCount(self):
        return len(self.children())

    def children(self):
        return self._children

    def insertChild(self, position, child):
        if position < 0 or position > len(self._children):
            return False

        self._children.insert(position, child)
        child._parent = self
        return True

    def addChild(self, child):
        self.children().append(child)

    def parent(self):
        return self._parent

    def setParent(self, _parent):
        self._parent = _parent

    def row(self):
        if self.parent() is not None:
            return self.parent().children().index(self)

class AbstractTreeModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super(AbstractTreeModel, self).__init__(parent)
        self.root_item = AbstractTreeItem('root')
        #self.item_list = []
        for x in range(0, 5):
            item = AbstractTreeItem('item_{x}'.format(x=str(x)), parent=self.root_item)
            #self.item_list.append(item)
            for char in 'abc':
                child_item = AbstractTreeItem('item_{index}_{char}'.format(index=x,char=char), parent=item)

    def rowCount(self, parent):
        """
        Returns the number of rows under the given parent. When the parent is
        valid it means that rowCount is returning the number of children of parent.

        Args:
            parent (QModelIndex):  The current model index that is being evaluated
        """

        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()
        return parent_item.childCount()

    def columnCount(self, parent):
        return 1

    def parent(self, index):
        """
        Provides a model index corresponding to the parent of any given child item.
        If the model index specified corresponds to a top-level item in the model,
        or if there is no valid parent item in the model, the function must return an
        invalid model index, created with the empty QModelIndex() constructor.
        """
        item = self.getItem(index)
        parent_item = item.parent()
        if parent_item == self.root_item:
            return QModelIndex()
        if not parent_item:
            return QModelIndex()
        return self.createIndex(parent_item.row(), 0, parent_item)

    def index(self, row, column, parent):
        """
        Given a model index for a parent item, this function allows views and
        delegates to access children of that item. If no valid child item -
        corresponding to the specified row, column, and parent model index,
        can be found, the function must return QModelIndex(), which is an
        invalid model index.
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

        return self.root_item

    def getParentIndexFromItem(self, item):
        parent_item = item.parent()
        if parent_item == self.root_item:
            parent_index = QModelIndex()
        elif not parent_item:
            parent_index = QModelIndex()
        else:
            parent_index = self.createIndex(parent_item.row(), 0, parent_item)
        return parent_index

    def data(self, index, role):
        """
        https://doc.qt.io/qt-5.12/qt.html#ItemDataRole-enum
        :param index:
        :param role:
        :return:
        """
        if role == Qt.DisplayRole:
            item = index.internalPointer()
            return item.name

    """ DRAG / DROP"""
    def supportedDropActions(self):
        return Qt.MoveAction

    def flags(self, index):
        # if not index.isValid():
        #     return Qt.ItemIsEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | \
               Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled

    def insertRows(self, position, num_rows, parent=QModelIndex()):
        """
        INPUTS: int, int, QModelIndex
        """
        parent_item = self.getItem(parent)
        self.beginInsertRows(parent, position, position + num_rows - 1)

        indexes = self.indexes
        for index in indexes:
            item = index.internalPointer()
            parent_item.insertChild(position, item)
        self.endInsertRows()
        return True

    def removeRows(self, position, num_rows, parent=QModelIndex()):
        """INPUTS: int, int, QModelIndex"""
        print('remove ')
        parent_item = self.getItem(parent)
        self.beginRemoveRows(parent, position, position + num_rows - 1)

        for row in range(num_rows):
            success = parent_item.removeChild(position)

        self.endRemoveRows()

        return success

    def mimeTypes(self):
        return ['application/x-qabstractitemmodeldatalist']

    def mimeData(self, indexes):
        self.indexes = [index.internalPointer() for index in indexes]
        with open('data.bin', 'wb') as f:
            pickle.dump(self.indexes, f, pickle.HIGHEST_PROTOCOL)
        mimedata = QMimeData()
        mimedata.setData('application/x-qabstractitemmodeldatalist', QByteArray())
        return mimedata

    def dropMimeData(self, data, action, row, column, parent):
        # f = data.data("application/x-test-data-type")
        # print('=== %s'%f)
        # f.
        # mimedata = data.data('application/x-qabstractitemmodeldatalist')
        # print(type(mimedata), mimedata)
        #
        # stream = QDataStream(mimedata, QIODevice.ReadOnly)
        #
        # data_items = self.decode_data(mimedata)
        # print(data_items)
        # for item in data_items:
        #     for key in item:
        #         print(key)
        #         variant = item[key]
        #
        #         print(variant)
        #         #print(variant.toModelIndex())
        #
        # #QVariant().ModelIndex()
        # #print (data_items)
        #
        # # QByteArray
        # # encoded = qMimeData->data("application/x-qabstractitemmodeldatalist");
        # # QDataStream
        # # stream( & encoded, QIODevice::ReadOnly);
        # #
        # # while (!stream.atEnd())
        # # {
        # #     int
        # # row, col;
        # # QMap < int, QVariant > roleDataMap;
        # # stream >> row >> col >> roleDataMap;
        # #
        # # / *do
        # # something
        # # with the data * /
        # # }
        #
        # return True

        with open('data.bin', 'rb') as f:
            data = pickle.load(f)

        # get parent item
        parent_item = parent.internalPointer()
        if not parent_item:
            parent_item = self.root_item

        indexes = self.indexes
        for item in indexes:
            old_parent_item = item.parent()
            old_parent_index = self.getParentIndexFromItem(item)

            self.beginRemoveRows(old_parent_index, item.row(), item.row()+1)
            old_parent_item.children().remove(item)
            self.endRemoveRows()

            # insert item
            self.beginInsertRows(parent, 0, 1)
            parent_item.insertChild(0, item)
            self.endInsertRows()
        return True


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_widget = QTreeView()
    main_widget.setSelectionMode(QAbstractItemView.MultiSelection)
    main_widget.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
    main_widget.setDragDropOverwriteMode(True)
    model = AbstractTreeModel()
    main_widget.setModel(model)
    main_widget.show()
    main_widget.move(QCursor.pos())

    sys.exit(app.exec_())

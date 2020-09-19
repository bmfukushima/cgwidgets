# https://doc.qt.io/qt-5/model-view-programming.html#model-view-classes

from qtpy.QtWidgets import (
    QApplication, QTreeView)
from qtpy.QtCore import (
    Qt, QModelIndex, QAbstractItemModel)
from qtpy.QtGui import (
    QPixmap,
    QIcon,

)

import sys

from cgwidgets.widgets.Tansu import TansuModelItem


class TansuModel(QAbstractItemModel):
    """INPUTS: TansuModelItem, QObject"""

    def __init__(self, parent=None, root_item=None):
        super(TansuModel, self).__init__(parent)
        if not root_item:
            root_item = TansuModelItem('root_item')
        self._root_item = root_item

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
        return 1

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
            if index.column() == 0:
                return item.name()

        if role == Qt.DecorationRole:
            if index.column() == 0:
                pixmap = QPixmap(26, 26)
                icon = QIcon(pixmap)
                return icon

    def setData(self, index, value, role=Qt.EditRole):
        """
        INPUTS: QModelIndex, QVariant, int (flag)
        """
        if index.isValid():
            if role == Qt.EditRole:
                item = index.internalPointer()
                item.setName(value)
                return True
        return False

    def headerData(self, column, orientation, role):
        """
        Sets the header data for each column
        INPUTS: int, Qt::Orientation, int
        OUTPUT: QVariant, strings are cast to QString which is a QVariant
        """
        if role == Qt.DisplayRole:
            if column == 0:
                return "Scenegraph"
            else:
                return "Typeinfo"

    def flags(self, index):
        """
        INPUTS: QModelIndex
        OUTPUT: int (flag)
        """
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

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
        INPUTS: int, int, QModelIndex
        OUTPUT: QModelIndex
        Should return a QModelIndex that corresponds to the given row, column and parent item
        """
        parent_item = self.getItem(parent)
        childItem = parent_item.child(row)

        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def getItem(self, index):
        """
        CUSTOM
        INPUTS: QModelIndex
        """
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item

        return self._root_item

    def insertRows(self, position, rows, parent=QModelIndex()):
        """
        INPUTS: int, int, QModelIndex
        """
        parent_item = self.getItem(parent)
        self.beginInsertRows(parent, position, position + rows - 1)

        for row in range(rows):
            childCount = parent_item.childCount()
            childNode = TansuModelItem("untitled" + str(childCount))
            success = parent_item.insertChild(position, childNode)

        self.endInsertRows()

        return success

    def removeRows(self, position, rows, parent=QModelIndex()):
        """INPUTS: int, int, QModelIndex"""
        parent_item = self.getItem(parent)
        self.beginRemoveRows(parent, position, position + rows - 1)

        for row in range(rows):
            success = parent_item.removeChild(position)

        self.endRemoveRows()

        return success

    def getRootItem(self):
        return self._root_item

    def setRootItem(self, root_item):
        self._root_item = root_item


class TreeView(QTreeView):
    def __init__(self, parent=None):
        super(TreeView, self).__init__(parent)
        root_item = TansuModelItem("root")


        model = TansuModel(root_item=root_item)
        self.setModel(model)
        childNode1 = TansuModelItem("RightPirateLeg_END", root_item)
        childNode3 = TansuModelItem("LeftTibia", root_item)
        childNode4 = TansuModelItem("LeftFoot", root_item)

    def selectionChanged(self, selected, deselected):
        for index in selected.indexes():
            item = index.internalPointer()
            item.test()
        return QTreeView.selectionChanged(self, selected, deselected)


if __name__ == '__main__':
    app = QApplication(sys.argv)


    treeView = TreeView()
    treeView.show()



    sys.exit(app.exec_())
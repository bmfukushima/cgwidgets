import sys
import os
# os.environ['QT_API'] = 'pyside2'
from qtpy.QtWidgets import QApplication, QLabel, QTreeView
from qtpy.QtGui import QCursor
from qtpy.QtCore import Qt, QByteArray, QSortFilterProxyModel, QRegExp, QAbstractItemModel, QModelIndex

from cgwidgets.widgets import ModelViewWidget, AbstractLabelWidget
from cgwidgets.views import AbstractDragDropModel
from cgwidgets.settings import iColor
from cgwidgets.utils import centerWidgetOnCursor, setAsAlwaysOnTop

from PyQt5.QtCore import (QDate, QDateTime, QRegExp, QSortFilterProxyModel, Qt,
        QTime)
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateEdit,
        QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QTreeView,  QListView,
        QVBoxLayout, QWidget)

import sys
# https://doc.qt.io/qt-5/model-view-programming.html#model-view-classes
from qtpy.QtWidgets import (
    QStyledItemDelegate, QApplication, QWidget, QStyle, QStyleOptionViewItem)
from qtpy.QtCore import (
    Qt, QModelIndex, QAbstractItemModel, QItemSelectionModel,
    QSize, QMimeData, QByteArray, QPoint, QRect)
from qtpy.QtGui import QPainter, QColor, QPen, QBrush, QCursor, QPolygonF, QPainterPath


app = QApplication(sys.argv)


class ModelViewWidgetSubclass(ModelViewWidget):
    def __init__(self, parent=None):
        super(ModelViewWidgetSubclass, self).__init__(parent)
        self.setPresetViewType(ModelViewWidget.TREE_VIEW)

        self._source_model = self.model()
        self._proxy_model = QSortFilterProxyModel(self)
        self._proxy_model.setSourceModel(self._source_model)

        self.setModel(self._proxy_model)

        for x in range(0, 4):
            index = self._source_model.insertNewIndex(x, name=str('anode%s' % x))
            for i, char in enumerate('abc'):
                self._source_model.insertNewIndex(i, name=char, parent=index)

        regex = QRegExp("a")
        regex.setCaseSensitivity(Qt.CaseInsensitive)
        self._proxy_model.setRecursiveFilteringEnabled(True)
        self._proxy_model.setFilterRegExp(regex)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F5:
            print('key press')
            self._proxy_model = QSortFilterProxyModel(self)
            self._proxy_model.setSourceModel(self._source_model)
            self._proxy_model.setRecursiveFilteringEnabled(True)
            self.setModel(self._proxy_model)
            #self.setModel(self._source_model)
        return ModelViewWidget.keyPressEvent(self, event)

main_widget = ModelViewWidgetSubclass()

# show widget
main_widget.show()
centerWidgetOnCursor(main_widget)

# self.model().setItemEnabled(item, enabled)

sys.exit(app.exec_())
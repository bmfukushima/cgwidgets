import sys
import os
# os.environ['QT_API'] = 'pyside2'
from qtpy.QtWidgets import QApplication
from qtpy.QtGui import QCursor
from qtpy.QtCore import Qt, QRegExp

from cgwidgets.widgets import ModelViewWidget, ShojiModelViewWidget, ButtonInputWidget
from cgwidgets.views import AbstractDragDropFilterProxyModel
from cgwidgets.utils import centerWidgetOnCursor

import sys
# https://doc.qt.io/qt-5/model-view-programming.html#model-view-classes


app = QApplication(sys.argv)


class ModelViewWidgetSubclass(ModelViewWidget):
    def __init__(self, parent=None):
        super(ModelViewWidgetSubclass, self).__init__(parent)
        self.setPresetViewType(ModelViewWidget.TREE_VIEW)
        #self.headerWidget().setPresetViewType(ModelViewWidget.TREE_VIEW)
        self.makeModelFilterable()
        self.setHeaderData(["name", "test"])
        for x in range(0, 4):
            index = self.model().insertNewIndex(x, name=str('anode%s' % x))

            self.model().insertNewIndex(0, parent=index, column_data={"name":"a", "test":"f"})
            self.model().insertNewIndex(0, parent=index, column_data={"name":"b", "test":"a"})
            self.model().insertNewIndex(0, parent=index, column_data={"name":"c", "test":"f"})

        regex1 = QRegExp("a")
        regex1.setCaseSensitivity(Qt.CaseInsensitive)
        regex2 = QRegExp("f")
        regex2.setCaseSensitivity(Qt.CaseInsensitive)

        self.addFilter(regex1, name="1")
        self.addFilter(regex2, arg="test", name="2")


        self._updateButton = ButtonInputWidget(self, title="test", user_clicked_event=self.updateFilter)
        self.addDelegate([Qt.Key_Q], self._updateButton, modifier=Qt.NoModifier, focus=False, always_on=True)
        # self.addHeaderDelegateWidget([Qt.Key_Q], self._updateButton, modifier=Qt.NoModifier, focus=False, always_on=True)
        self._updateButton.show()

    def updateFilter(self, widget):
        self.updateFilterByName("c", "1")
        print(self.view().proxyModel().invalidateFilter())
        print(self.view().filters())
        # print(self.headerWidget().)


main_widget = ModelViewWidgetSubclass()

# show widget
main_widget.show()
centerWidgetOnCursor(main_widget)

sys.exit(app.exec_())
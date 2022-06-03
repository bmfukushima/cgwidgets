import sys
import os
# os.environ['QT_API'] = 'pyside2'
from qtpy.QtWidgets import QApplication
from qtpy.QtCore import Qt, QRegExp

from cgwidgets.widgets import ModelViewWidget
from cgwidgets.utils import centerWidgetOnCursor

import sys


app = QApplication(sys.argv)


class ModelViewWidgetSubclass(ModelViewWidget):
    def __init__(self, parent=None):
        super(ModelViewWidgetSubclass, self).__init__(parent)
        self.setPresetViewType(ModelViewWidget.TREE_VIEW)

        self.makeModelFilterable()
        self.setHeaderData(["name", "test"])

        # add indexes to model
        for x in range(0, 4):
            index = self.insertNewIndex(x, name=str('anode%s' % x))
            self.insertNewIndex(0, parent=index, column_data={"name":"a", "test":"f"})
            self.insertNewIndex(0, parent=index, column_data={"name":"b", "test":"a"})
            self.insertNewIndex(0, parent=index, column_data={"name":"c", "test":"f"})

        regex1 = QRegExp("a")
        regex1.setCaseSensitivity(Qt.CaseInsensitive)
        regex2 = QRegExp("f")
        regex2.setCaseSensitivity(Qt.CaseInsensitive)

        self.addFilter(regex1, name="1")
        self.addFilter(regex2, arg="test", name="2")

main_widget = ModelViewWidgetSubclass()

# show widget
main_widget.show()
centerWidgetOnCursor(main_widget)

sys.exit(app.exec_())
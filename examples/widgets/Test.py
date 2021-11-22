import sys
import os
os.environ['QT_API'] = 'pyside2'
from qtpy.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from qtpy.QtGui import QCursor
from qtpy.QtCore import Qt, QByteArray

from cgwidgets.widgets import ModelViewWidget, AbstractLabelWidget

from cgwidgets.utils import centerWidgetOnCursor, setAsAlwaysOnTop

app = QApplication(sys.argv)

# class TestA(ModelViewWidget):
#     def __init__(self, parent=None):
#         super(TestA, self).__init__(parent)
#         self.setPresetViewType(ModelViewWidget.TREE_VIEW)
#         print(self.view())
#         self.addContextMenuEvent("testa", self.testEvent)
#
#     # def contextMenuEvent(self, event):
#     #     from qtpy.QtWidgets import QMenu
#     #     context_menu = QMenu(self)
#     #     context_menu.addAction("test")
#     #
#     #     # Show/Execute menu
#     #     pos = event.globalPos()
#     #     context_menu.popup(pos)
#     #     action = context_menu.exec_(pos)
#     #
#     #     # get selected items / items under cursor
#     #     index_clicked = context_menu.item
#     #     selected_indexes = self.selectionModel().selectedRows(0)
#     #
#     #     # do user defined event
#     #     if action is not None:
#     #         self.testEvent()
#     #     return ModelViewWidget.contextMenuEvent(self, event)
#
#     def testEvent(self, *args):
#         print('test')
main_widget = QWidget()
main_layout = QVBoxLayout(main_widget)
widget = ModelViewWidget()
main_layout.addWidget(widget)

for x in range(3):
    widget.insertNewIndex(0, name=str(x))
#
def testContextEvent(item, items):
    print('test')

widget.addContextMenuEvent("test", testContextEvent)
setAsAlwaysOnTop(main_widget)
main_widget.show()
centerWidgetOnCursor(main_widget)

sys.exit(app.exec_())
import sys

from qtpy.QtWidgets import QApplication, QLabel
from qtpy.QtGui import QCursor
from qtpy.QtCore import Qt

from cgwidgets.widgets import ModelViewWidget

app = QApplication(sys.argv)

# create event functions
def testDelete(item):
    print("DELETING --> -->", item.columnData()['name'])

def testDrag(indexes):
    print(indexes)
    print("DRAGGING -->", indexes)

def testDrop(row, indexes, parent):
    print("DROPPING -->", row, indexes, parent)

def testEdit(item, old_value, new_value):
    print("EDITING -->", item, old_value, new_value)

def testEnable(item, enabled):
    print("ENABLING -->", item.columnData()['name'], enabled)

def testSelect(item, enabled, column=0):
    print("SELECTING -->", item.columnData()['name'], enabled)

def testDelegateToggle(event, widget, enabled):
    print("TOGGLING -{key}->".format(key=event.key()), widget, enabled)


# create main Model View Widget
main_widget = ModelViewWidget()
main_widget.setViewType(ModelViewWidget.TREE_VIEW)

# create delegates
delegate_widget = QLabel("F")
main_widget.addDelegate([Qt.Key_F], delegate_widget)

delegate_widget = QLabel("Q")
main_widget.addDelegate([Qt.Key_Q], delegate_widget)

# insert indexes
for x in range(0, 4):
    index = main_widget.model().insertNewIndex(x, name=str('node%s'%x))
    for i, char in enumerate('abc'):
        main_widget.model().insertNewIndex(i, name=char, parent=index)

# set model event
main_widget.setDragStartEvent(testDrag)
main_widget.setDropEvent(testDrop)
main_widget.setTextChangedEvent(testEdit)
main_widget.setItemEnabledEvent(testEnable)
main_widget.setItemDeleteEvent(testDelete)
main_widget.setItemSelectedEvent(testSelect)
#
# set flags
main_widget.setIsRootDropEnabled(False)
main_widget.setIsEditable(False)
main_widget.setIsDragEnabled(False)
main_widget.setIsDropEnabled(False)
main_widget.setIsEnableable(True)
main_widget.setIsDeleteEnabled(True)
main_widget.setDelegateToggleEvent(testDelegateToggle)

# set selection mode
main_widget.setMultiSelect(True)

main_widget.move(QCursor.pos())
main_widget.show()


sys.exit(app.exec_())
import sys
import os
# os.environ['QT_API'] = 'pyside2'
from qtpy.QtWidgets import QApplication, QLabel
from qtpy.QtGui import QCursor
from qtpy.QtCore import Qt

from cgwidgets.widgets import ModelViewWidget, AbstractLabelWidget

from cgwidgets.utils import centerWidgetOnCursor, setAsAlwaysOnTop

app = QApplication(sys.argv)

# create event functions
def testDelete(item):
    print("DELETING --> -->", item.columnData()['name'])

def testDrag(items, model):
    print("DRAGGING -->", items, model)
#data, indexes, self, row, parent_item
def testDrop(data, items, model, row, parent):
    print("""
DROPPING -->
    data --> {data}
    row --> {row}
    items --> {items}
    model --> {model}
    parent --> {parent}
        """.format(data=data, row=row, model=model, items=items, parent=parent)
          )

def testEdit(item, old_value, new_value):
    print("EDITING -->", item, old_value, new_value)

def testEnable(item, enabled):
    print("ENABLING -->", item.columnData()['name'], enabled)

def testSelect(item, enabled):
    print("SELECTING -->", item.columnData()['name'], enabled)

def testDelegateToggle(enabled, event, widget):
    print("TOGGLING -{key}->".format(key=event.key()), widget, enabled)

# SUBCLASS
class ModelViewWidgetSubclass(ModelViewWidget):
    def __init__(self, parent=None):
        super(ModelViewWidgetSubclass, self).__init__(parent)
        # self.model().setItemType(DisplayEditableOptionsItem)
        #
        # for x in range(0, 4):
        #     index = self.model().insertNewIndex(x, name=str('node%s' % x))
        #     for i, char in enumerate('abc'):
        #         self.model().insertNewIndex(i, name=char, parent=index)

main_widget = ModelViewWidgetSubclass()
# create main Model View Widget
#main_widget = ModelViewWidget()

# setup deletion warning
delete_warning_widget = AbstractLabelWidget(text="Are you sure you want to delete this?\n You cannot undo it...")
main_widget.setDeleteWarningWidget(delete_warning_widget)

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
    if x == 0:
        index.internalPointer().setIsEditable(True)
        index.internalPointer().setIsSelectable(True)
        index.internalPointer().setIsDroppable(False)
        index.internalPointer().setIsDraggable(True)

# set delete on drop...
""" This will make it so that when an item is dropped, it can be duplicated

setting the item will override the models settings.
"""
index.internalPointer().setDeleteOnDrop(False)
main_widget.model().setDeleteItemOnDrop(True)

# set model event
main_widget.setDragStartEvent(testDrag)
main_widget.setDropEvent(testDrop)
main_widget.setTextChangedEvent(testEdit)
main_widget.setItemEnabledEvent(testEnable)
main_widget.setItemDeleteEvent(testDelete)
main_widget.setIndexSelectedEvent(testSelect)
#
# set flags
main_widget.setIsRootDroppable(True)
main_widget.setIsEditable(True)
main_widget.setIsDraggable(True)
main_widget.setIsDroppable(True)
main_widget.setIsEnableable(True)
main_widget.setIsDeletable(True)
main_widget.setDelegateToggleEvent(testDelegateToggle)

indexes = main_widget.model().findItems("node1", Qt.MatchExactly)
for index in indexes:
    main_widget.setIndexSelected(index, True)
    index.internalPointer().setIsDroppable(False)
    index.internalPointer().setIsSelectable(False)
    index.internalPointer().setIsEditable(True)

# set selection mode
main_widget.setMultiSelect(True)

# add context menu
def contextMenu(index, selected_indexes):
    print(index, selected_indexes)

main_widget.addContextMenuEvent('test', contextMenu)

# # add mime data
from qtpy.QtCore import QByteArray
def addMimedata(mimedata, items):
    """ Adds the mimedata to the drag event

    Args:
        mimedata (QMimedata): from dragEvent
        items (list): of NodeViewWidgetItem"""

    #for index in indexes:
    ba = QByteArray()
    ba.append("test")

    mimedata.setData("something/something", ba)
    return mimedata
main_widget.setAddMimeDataFunction(addMimedata)


# show widget
main_widget.show()
centerWidgetOnCursor(main_widget)

class DropButton(QLabel):
    def __init__(self, parent=None):
        super(DropButton, self).__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        event.accept()
        return QLabel.dragEnterEvent(self, event)

    def dropEvent(self, event):
        for format in event.mimeData().formats():
            print(format, " == ", event.mimeData().data(format))
        return QLabel.dropEvent(self, event)

drop_widget = DropButton()
setAsAlwaysOnTop(drop_widget)
drop_widget.show()
drop_widget.resize(256, 256)
centerWidgetOnCursor(drop_widget)
# self.model().setItemEnabled(item, enabled)

sys.exit(app.exec_())
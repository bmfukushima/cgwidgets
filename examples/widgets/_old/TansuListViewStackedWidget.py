from qtpy.QtCore import Qt

from cgwidgets.widgets import ShojiModelViewWidget
from cgwidgets.delegates import ShojiLayout
from cgwidgets.settings import attrs

import sys
from qtpy.QtWidgets import QApplication, QLabel
from qtpy.QtGui import QCursor

def testDrag(indexes):
    """
    Initialized when the drag has started.  This triggers in the mimeData portion
    of the model.

    Args:
        indexes (list): of ShojiModelItems
    """
    print("---- DRAG EVENT ----")
    print(indexes)

def testDrop(row, indexes, parent):
    """
    Run when the user does a drop.  This is triggered on the dropMimeData funciton
    in the model.

    Args:
        indexes (list): of ShojiModelItems
        parent (ShojiModelItem): parent item that was dropped on

    """
    print("---- DROP EVENT ----")
    print(row, indexes, parent)

def testEdit(item, old_value, new_value):
    print("---- EDIT EVENT ----")
    print(item, old_value, new_value)

def testEnable(item, enabled):
    print(item.columnData()['example'], enabled)

def testDelete(item):
    print(item.columnData()['example'])

def testToggle(event, enabled):
    print('---- TOGGLE EVENT ----')
    print (event, enabled)

def testSelect(item, enabled):
    print("SELECTING -->", item.columnData(), enabled)

app = QApplication(sys.argv)

shoji_widget = ShojiModelViewWidget()
shoji_widget.setHeaderData(['example'])
tab_1 = QLabel('hello')
tab_2 = QLabel('world')
tab_3 = ShojiLayout()
tab_3.setObjectName("main")
tab_3.addWidget(QLabel('a'))
tab_3.addWidget(QLabel('b'))
tab_3.addWidget(QLabel('c'))

# set attrs
shoji_widget.setHeaderPosition(attrs.WEST)
#shoji_widget.setHeaderDelegateWidget(header_delegate_widget)
shoji_widget.setMultiSelectDirection(Qt.Vertical)
shoji_widget.delegateWidget().setHandleLength(100)

# insert tabs
shoji_widget.insertShojiWidget(0, column_data={'example' : '<title> hello'}, widget=tab_1)
shoji_widget.insertShojiWidget(0, column_data={'example' : '<title> world'}, widget=tab_2)
shoji_widget.insertShojiWidget(0, column_data={'example' : '<title> shoji'}, widget=tab_3)

# enable drag/drop
shoji_widget.setHeaderItemIsDropEnabled(False)
shoji_widget.setHeaderItemIsDragEnabled(True)
shoji_widget.setHeaderItemIsEditable(True)
shoji_widget.setHeaderItemIsEnableable(True)
shoji_widget.setHeaderItemIsDeleteEnabled(True)
shoji_widget.setHeaderItemEnabledEvent(testEnable)
shoji_widget.setHeaderItemDeleteEvent(testDelete)
shoji_widget.setHeaderDelegateToggleEvent(testToggle)

# setup drag/drop events
shoji_widget.setHeaderItemDragStartEvent(testDrag)
shoji_widget.setHeaderItemDropEvent(testDrop)
shoji_widget.setHeaderItemTextChangedEvent(testEdit)
shoji_widget.setHeaderItemSelectedEvent(testSelect)

#print('model == ', shoji_widget.model())
#shoji_widget.setDelegateTitleIsShown(False)

# display widget
shoji_widget.resize(500, 500)
shoji_widget.show()
shoji_widget.move(QCursor.pos())
sys.exit(app.exec_())
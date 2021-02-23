from qtpy.QtCore import Qt

from cgwidgets.widgets import ShojiModelViewWidget
from cgwidgets.delegates import ShojiView
from cgwidgets.utils import attrs

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

tansu_widget = ShojiModelViewWidget()
tansu_widget.setHeaderData(['example'])
tab_1 = QLabel('hello')
tab_2 = QLabel('world')
tab_3 = ShojiView()
tab_3.setObjectName("main")
tab_3.addWidget(QLabel('a'))
tab_3.addWidget(QLabel('b'))
tab_3.addWidget(QLabel('c'))

# set attrs
tansu_widget.setHeaderPosition(attrs.WEST)
#tansu_widget.setHeaderDelegateWidget(header_delegate_widget)
tansu_widget.setMultiSelectDirection(Qt.Vertical)
tansu_widget.delegateWidget().setHandleLength(100)

# insert tabs
tansu_widget.insertShojiWidget(0, column_data={'example' : '<title> hello'}, widget=tab_1)
tansu_widget.insertShojiWidget(0, column_data={'example' : '<title> world'}, widget=tab_2)
tansu_widget.insertShojiWidget(0, column_data={'example' : '<title> tansu'}, widget=tab_3)

# enable drag/drop
tansu_widget.setHeaderItemIsDropEnabled(False)
tansu_widget.setHeaderItemIsDragEnabled(True)
tansu_widget.setHeaderItemIsEditable(True)
tansu_widget.setHeaderItemIsEnableable(True)
tansu_widget.setHeaderItemIsDeleteEnabled(True)
tansu_widget.setHeaderItemEnabledEvent(testEnable)
tansu_widget.setHeaderItemDeleteEvent(testDelete)
tansu_widget.setHeaderDelegateToggleEvent(testToggle)

# setup drag/drop events
tansu_widget.setHeaderItemDragStartEvent(testDrag)
tansu_widget.setHeaderItemDropEvent(testDrop)
tansu_widget.setHeaderItemTextChangedEvent(testEdit)
tansu_widget.setHeaderItemSelectedEvent(testSelect)

#print('model == ', tansu_widget.model())
#tansu_widget.setDelegateTitleIsShown(False)

# display widget
tansu_widget.resize(500, 500)
tansu_widget.show()
tansu_widget.move(QCursor.pos())
sys.exit(app.exec_())
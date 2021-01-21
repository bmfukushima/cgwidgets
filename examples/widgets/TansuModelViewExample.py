"""
TODO:
    * custom model / items
    * Directions
        header delegates NESW
"""

from qtpy.QtCore import Qt

from cgwidgets.widgets import TansuModelViewWidget, ModelViewWidget
from cgwidgets.delegates import TansuDelegate
from cgwidgets.utils import attrs

import sys
from qtpy.QtWidgets import QApplication, QLabel, QLineEdit
from qtpy.QtGui import QCursor

def testDrag(indexes):
    """
    Initialized when the drag has started.  This triggers in the mimeData portion
    of the model.

    Args:
        indexes (list): of TansuModelItems
    """
    print("---- DRAG EVENT ----")
    print(indexes)

def testDrop(row, indexes, parent):
    """
    Run when the user does a drop.  This is triggered on the dropMimeData funciton
    in the model.

    Args:
        indexes (list): of TansuModelItems
        parent (TansuModelItem): parent item that was dropped on

    """
    print("---- DROP EVENT ----")
    print(row, indexes, parent)

def testEdit(item, old_value, new_value):
    print("---- EDIT EVENT ----")
    print(item, old_value, new_value)

def testEnable(item, enabled):
    print('---- ENABLE EVENT ----')
    print(item.columnData()['example'], enabled)

def testDelete(item):
    print('---- DELETE EVENT ----')
    print(item.columnData()['example'])

def testDelegateToggle(event, widget, enabled):
    print('---- TOGGLE EVENT ----')
    print (event, widget, enabled)

def testSelect(item, enabled):
    print('---- SELECT EVENT ----')
    print(item.columnData(), enabled)

app = QApplication(sys.argv)

# CREATE MAIN WIDGET
tansu_widget = TansuModelViewWidget()
tansu_widget.setHeaderViewType(ModelViewWidget.TREE_VIEW)

# Set column names
# note: when providing column data, the key in the dict with the 0th
# index is required, and is the text displayed to the user by default
tansu_widget.setHeaderData(['example'])

# CREATE ITEMS / TABS

# insert tabs
tansu_widget.insertTansuWidget(0, column_data={'example' : '<title> hello'}, widget=QLabel('hello'))
tansu_widget.insertTansuWidget(0, column_data={'example' : '<title> world'}, widget=QLabel('world'))

tansu_delegate = TansuDelegate()
for char in 'sinep':
    tansu_delegate.addWidget(QLineEdit(char))
tansu_delegate_item = tansu_widget.insertTansuWidget(0, column_data={'example' : '<title> tansu'}, widget=tansu_delegate)

# insert child tabs
# insert child widgets
for y in range(0, 2):
    widget = QLineEdit(str("sinep"))
    tansu_widget.insertTansuWidget(y, column_data={'example': str(y), 'one': 'datttaaa'}, widget=widget, parent=tansu_delegate_item)

# set attrs
tansu_widget.setHeaderPosition(attrs.WEST)
tansu_widget.setMultiSelect(True)
tansu_widget.setMultiSelectDirection(Qt.Vertical)
tansu_widget.delegateWidget().handle_length = 100
tansu_widget.setHeaderPosition(attrs.EAST)
# Flags
tansu_widget.setHeaderItemIsDropEnabled(False)
tansu_widget.setHeaderItemIsDragEnabled(True)
tansu_widget.setHeaderItemIsEditable(True)
tansu_widget.setHeaderItemIsEnableable(True)
tansu_widget.setHeaderItemIsDeleteEnabled(True)

# Setup Virtual Events
tansu_widget.setHeaderItemEnabledEvent(testEnable)
tansu_widget.setHeaderItemDeleteEvent(testDelete)
tansu_widget.setHeaderDelegateToggleEvent(testDelegateToggle)
tansu_widget.setHeaderItemDragStartEvent(testDrag)
tansu_widget.setHeaderItemDropEvent(testDrop)
tansu_widget.setHeaderItemTextChangedEvent(testEdit)
tansu_widget.setHeaderItemSelectedEvent(testSelect)

# Header Delegates
"""
In the Tree/List view this is a widget that will pop up when
the user presses a specific key/modifier combination
"""
delegate_widget = QLabel("Q")
tansu_widget.addHeaderDelegateWidget([Qt.Key_Q], delegate_widget, modifier=Qt.NoModifier)
tansu_widget.setHeaderDelegateDirection(Qt.Vertical, position=attrs.SOUTH)

#
#tansu_widget.setDelegate

# display widget
tansu_widget.resize(500, 500)
tansu_widget.show()
tansu_widget.move(QCursor.pos())
sys.exit(app.exec_())
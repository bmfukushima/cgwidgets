from qtpy.QtCore import Qt

from cgwidgets.widgets import TansuModelViewWidget, TansuBaseWidget
from cgwidgets.utils import attrs

import sys
from qtpy.QtWidgets import QApplication, QLabel
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

app = QApplication(sys.argv)

tansu_widget = TansuModelViewWidget()
tansu_widget.setHeaderData(['example'])
tab_1 = QLabel('hello')
tab_2 = QLabel('world')
tab_3 = TansuBaseWidget()
tab_3.setObjectName("main")
tab_3.addWidget(QLabel('a'))
tab_3.addWidget(QLabel('b'))
tab_3.addWidget(QLabel('c'))

# set attrs
tansu_widget.setHeaderPosition(attrs.WEST)
#tansu_widget.setMultiSelect(True)
tansu_widget.setMultiSelectDirection(Qt.Vertical)
tansu_widget.delegateWidget().handle_length = 100

# insert tabs
tansu_widget.insertTansuWidget(0, column_data={'example' : '<title> hello'}, widget=tab_1)
tansu_widget.insertTansuWidget(0, column_data={'example' : '<title> world'}, widget=tab_2)
tansu_widget.insertTansuWidget(0, column_data={'example' : '<title> tansu'}, widget=tab_3)

# enable drag/drop
tansu_widget.setHeaderItemIsDropEnabled(False)
tansu_widget.setHeaderItemIsDragEnabled(True)
tansu_widget.setHeaderItemIsEditable(True)
# setup drag/drop events
tansu_widget.setHeaderItemDragStartEvent(testDrag)
tansu_widget.setHeaderItemDropEvent(testDrop)
tansu_widget.setHeaderItemTextChangedEvent(testEdit)


# display widget
tansu_widget.resize(500, 500)
tansu_widget.show()
tansu_widget.move(QCursor.pos())
sys.exit(app.exec_())
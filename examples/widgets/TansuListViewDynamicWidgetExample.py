"""
You can also set the dynamic functions on the item.  Which will be called
instead of the primary ones if you want to do a per item override.

"""
from qtpy.QtCore import Qt

from cgwidgets.widgets import TansuModelViewWidget, FloatInputWidget
from cgwidgets.utils import attrs

import sys
from qtpy.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from qtpy.QtGui import QCursor

app = QApplication(sys.argv)

"""
Dynamic widget to be used for the Tansu.  This widget will be shown
everytime an item is selected in the Tansu, and the updateGUI function
will be run, every time an item is selected.
"""
class TabTansuDynamicWidgetExample(QWidget):
    """
    Simple example of overloaded class to be used as a dynamic widget for
    the TansuModelViewWidget.
    """
    def __init__(self, parent=None):
        super(TabTansuDynamicWidgetExample, self).__init__(parent)
        QVBoxLayout(self)
        self.label = QLabel('init')
        self.layout().addWidget(self.label)

    @staticmethod
    def updateGUI(parent, widget, item):
        """
        widget (TansuModelDelegateWidget)
        item (TansuModelItem)
        """
        if item:
            print ('------------- SHOW EVENT ---------------')
            print(parent, widget, item)
            name = parent.model().getItemName(item)
            widget.setName(name)
            widget.getMainWidget().label.setText(name)

"""
Custom widget which has overloaded functions/widget to be
displayed in the Tansu
"""
class CustomDynamicWidget(FloatInputWidget):
    def __init__(self, parent=None):
        super(CustomDynamicWidget, self).__init__(parent)

    @staticmethod
    def updateGUI(parent, widget, item):
        """
        parent (TansuModelViewWidget)
        widget (TansuModelDelegateWidget)
        item (TansuModelItem)
        self --> widget.getMainWidget()
        """
        print('custom event')
        print(parent, widget, item)
        this = widget.getMainWidget()
        this.setText('whatup')

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
    print(item.columnData()['name'], enabled)

# create tansu widget
tansu_widget = TansuModelViewWidget()

# set dynamic
tansu_widget.setDelegateType(
    TansuModelViewWidget.DYNAMIC,
    dynamic_widget=TabTansuDynamicWidgetExample,
    dynamic_function=TabTansuDynamicWidgetExample.updateGUI
)

for x in range(3):
    name = '<title {}>'.format(str(x))
    tansu_widget.insertTansuWidget(x, column_data={'name':name})

# # custom item
# custom_index = tansu_widget.insertTansuWidget(0, column_data={'name': 'Custom Handlers'})
# custom_index.internalPointer().setDynamicWidgetBaseClass(CustomDynamicWidget)
# custom_index.internalPointer().setDynamicUpdateFunction(CustomDynamicWidget.updateGUI)

# set attrs
# tansu_widget.setHeaderPosition(attrs.NORTH)
# tansu_widget.setMultiSelect(True)
# tansu_widget.setMultiSelectDirection(Qt.Vertical)
# tansu_widget.delegateWidget().handle_length = 100
#
# # enable drag/drop
# tansu_widget.setHeaderItemIsDropEnabled(False)
# tansu_widget.setHeaderItemIsDragEnabled(True)
#
# # setup drag/drop events
# tansu_widget.setHeaderItemDragStartEvent(testDrag)
# tansu_widget.setHeaderItemDropEvent(testDrop)
# tansu_widget.setHeaderItemTextChangedEvent(testEdit)
# tansu_widget.setHeaderItemEnabledEvent(testEnable)

# set size / show
tansu_widget.resize(500, 500)

delegate_widget = QLabel("Q")
tansu_widget.addHeaderDelegateWidget([Qt.Key_Q], delegate_widget)
tansu_widget.setDelegateHeaderIsShown(True)
tansu_widget.show()
tansu_widget.move(QCursor.pos())
sys.exit(app.exec_())
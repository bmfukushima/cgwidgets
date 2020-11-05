"""
You can also set the dynamic functions on the item.  Which will be called
instead of the primary ones if you want to do a per item override.

"""
from qtpy.QtCore import Qt

from cgwidgets.widgets import TansuModelViewWidget, FloatInputWidget
from cgwidgets.utils import attrs

import sys
from qtpy.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QAbstractItemView
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
            widget.setTitle(name)
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
    print(indexes)

def testDrop(indexes, parent):
    print(indexes, parent)

def testEdit(item, old_value, new_value):
    print(item, old_value, new_value)

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
tansu_widget.setHeaderPosition(attrs.NORTH)
tansu_widget.setMultiSelect(True)
tansu_widget.setMultiSelectDirection(Qt.Vertical)
tansu_widget.delegateWidget().handle_length = 100

# enable drag/drop
#tansu_widget.setHeaderDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
#tansu_widget.headerWidget().setDragDropOverwriteMode(False)

# setup drag/drop events
tansu_widget.setHeaderDragStartEvent(testDrag)
tansu_widget.setHeaderDropEvent(testDrop)
tansu_widget.setHeaderTextChangedEvent(testEdit)

# setup drag/drop flags
tansu_widget.setHeaderIsDropEnabled(False)
tansu_widget.setHeaderIsDragEnabled(True)
#tansu_widget.setIsDragDropEnabled(False)


# set size / show
tansu_widget.resize(500, 500)

tansu_widget.show()

tansu_widget.move(QCursor.pos())
sys.exit(app.exec_())
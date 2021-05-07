"""
You can also set the dynamic functions on the item.  Which will be called
instead of the primary ones if you want to do a per item override.
"""

import sys

from qtpy.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QAbstractItemView
from qtpy.QtCore import Qt
from qtpy.QtGui import QCursor

from cgwidgets.widgets import ShojiModelViewWidget, FloatInputWidget
from cgwidgets.settings import attrs

app = QApplication(sys.argv)

"""
Dynamic widget to be used for the Shoji.  This widget will be shown
everytime an item is selected in the Shoji, and the updateGUI function
will be run, every time an item is selected.
"""
class TabShojiDynamicWidgetExample(QWidget):
    """
    Simple example of overloaded class to be used as a dynamic widget for
    the ShojiModelViewWidget.
    """
    def __init__(self, parent=None):
        super(TabShojiDynamicWidgetExample, self).__init__(parent)
        QVBoxLayout(self)
        self.label = QLabel('init')
        self.layout().addWidget(self.label)

    @staticmethod
    def updateGUI(parent, widget, item):
        """
        widget (ShojiModelDelegateWidget)
        item (ShojiModelItem)
        """
        if item:
            print ('----------------------------')
            print(parent, widget, item)
            name = parent.model().getItemName(item)
            widget.setName(name)
            widget.getMainWidget().label.setText(name)


"""
Custom widget which has overloaded functions/widget to be
displayed in the Shoji
"""
class CustomDynamicWidget(FloatInputWidget):
    def __init__(self, parent=None):
        super(CustomDynamicWidget, self).__init__(parent)

    @staticmethod
    def updateGUI(parent, widget, item):
        """
        parent (ShojiModelViewWidget)
        widget (ShojiModelDelegateWidget)
        item (ShojiModelItem)
        self --> widget.getMainWidget()
        """
        print('custom event')
        print(parent, widget, item)
        this = widget.getMainWidget()
        this.setText('whatup')


# create shoji widget
shoji_widget = ShojiModelViewWidget()

#view = ShojiHeaderTreeView()

# setup header
#shoji_widget.setHeaderViewWidget(view)
shoji_widget.setHeaderPosition(attrs.WEST, header_view_position=attrs.SOUTH)
shoji_widget.setHeaderData(['name', 'test', 'three'])

# set dynamic
shoji_widget.setDelegateType(
    ShojiModelViewWidget.DYNAMIC,
    dynamic_widget=TabShojiDynamicWidgetExample,
    dynamic_function=TabShojiDynamicWidgetExample.updateGUI
)

for x in range(3):
    name = '<title {}>'.format(str(x))
    shoji_widget.insertShojiWidget(x, column_data={'name':name})

# custom item
custom_index = shoji_widget.insertShojiWidget(0, column_data={'name': 'Custom Handlers', 'test':'test'})
custom_index.internalPointer().setDynamicWidgetBaseClass(CustomDynamicWidget)
custom_index.internalPointer().setDynamicUpdateFunction(CustomDynamicWidget.updateGUI)

# set attrs
shoji_widget.setHeaderPosition(attrs.WEST, header_view_position=attrs.SOUTH)
shoji_widget.setMultiSelect(True)
shoji_widget.setMultiSelectDirection(Qt.Vertical)
#shoji_widget.setHeaderDelegateAlwaysOn(False)
shoji_widget.delegateWidget().setHandleLength(100)

# enable drag/drop
shoji_widget.setHeaderItemIsDropEnabled(True)
shoji_widget.setHeaderItemIsDragEnabled(True)

shoji_widget.setDelegateTitleIsShown(False)
# show view
shoji_widget.resize(500, 500)
shoji_widget.show()
shoji_widget.move(QCursor.pos())
sys.exit(app.exec_())
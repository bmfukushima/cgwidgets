"""
You can also set the dynamic functions on the item.  Which will be called
instead of the primary ones if you want to do a per item override.
"""

import sys

from qtpy.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QAbstractItemView
from qtpy.QtCore import Qt
from qtpy.QtGui import QCursor

from cgwidgets.widgets import ShojiModelViewWidget, FloatInputWidget
from cgwidgets.utils import attrs

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


# create tansu widget
tansu_widget = ShojiModelViewWidget()

#view = ShojiHeaderTreeView()

# setup header
#tansu_widget.setHeaderViewWidget(view)
tansu_widget.setHeaderPosition(attrs.WEST, header_view_position=attrs.SOUTH)
tansu_widget.setHeaderData(['name', 'test', 'three'])

# set dynamic
tansu_widget.setDelegateType(
    ShojiModelViewWidget.DYNAMIC,
    dynamic_widget=TabShojiDynamicWidgetExample,
    dynamic_function=TabShojiDynamicWidgetExample.updateGUI
)

for x in range(3):
    name = '<title {}>'.format(str(x))
    tansu_widget.insertShojiWidget(x, column_data={'name':name})

# custom item
custom_index = tansu_widget.insertShojiWidget(0, column_data={'name': 'Custom Handlers', 'test':'test'})
custom_index.internalPointer().setDynamicWidgetBaseClass(CustomDynamicWidget)
custom_index.internalPointer().setDynamicUpdateFunction(CustomDynamicWidget.updateGUI)

# set attrs
tansu_widget.setHeaderPosition(attrs.WEST, header_view_position=attrs.SOUTH)
tansu_widget.setMultiSelect(True)
tansu_widget.setMultiSelectDirection(Qt.Vertical)
#tansu_widget.setHeaderDelegateAlwaysOn(False)
tansu_widget.delegateWidget().setHandleLength(100)

# enable drag/drop
tansu_widget.setHeaderItemIsDropEnabled(True)
tansu_widget.setHeaderItemIsDragEnabled(True)

tansu_widget.setDelegateTitleIsShown(False)
# show view
tansu_widget.resize(500, 500)
tansu_widget.show()
tansu_widget.move(QCursor.pos())
sys.exit(app.exec_())
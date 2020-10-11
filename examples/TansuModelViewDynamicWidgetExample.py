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
    def updateGUI(widget, item):
        """
        widget (TansuModelDelegateWidget)
        item (TansuModelItem)
        """
        if item:
            widget.setTitle(item.name())
            widget.getMainWidget().label.setText(item.name())

"""
Custom widget which has overloaded functions/widget to be
displayed in the Tansu
"""
class CustomDynamicWidget(FloatInputWidget):
    def __init__(self, parent=None):
        super(CustomDynamicWidget, self).__init__(parent)

    @staticmethod
    def updateGUI(widget, item):
        """
        widget (TansuModelDelegateWidget)
        item (TansuModelItem)
        self --> widget.getMainWidget()
        """
        print('custom event')
        print(widget, item)
        this = widget.getMainWidget()
        this.setText('whatup')

# create tansu widget
tansu_widget = TansuModelViewWidget()

# set dynamic
tansu_widget.setDelegateType(
    TansuModelViewWidget.DYNAMIC,
    dynamic_widget=TabTansuDynamicWidgetExample,
    dynamic_function=TabTansuDynamicWidgetExample.updateGUI
)

for x in range(3):
    tansu_widget.insertTansuWidget(x, '<title {}>'.format(str(x)))

# custom item


custom_item = tansu_widget.insertTansuWidget(0, 'Custom Handlers')
custom_item.setDynamicWidgetBaseClass(CustomDynamicWidget)
custom_item.setDynamicUpdateFunction(CustomDynamicWidget.updateGUI)

# set attrs
tansu_widget.setHeaderPosition(attrs.NORTH)
tansu_widget.setMultiSelect(True)
tansu_widget.setMultiSelectDirection(Qt.Vertical)


tansu_widget.resize(500, 500)
tansu_widget.delegateWidget().handle_length = 100

tansu_widget.show()

tansu_widget.move(QCursor.pos())
sys.exit(app.exec_())
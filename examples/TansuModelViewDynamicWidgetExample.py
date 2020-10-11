"""

"""
from qtpy.QtCore import Qt

from cgwidgets.widgets import TansuModelViewWidget
from cgwidgets.utils import attrs

import sys
from qtpy.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from qtpy.QtGui import QCursor

app = QApplication(sys.argv)

""" Dynamic Display Widget"""
class TabTansuDynamicWidgetExample(QWidget):
    """
    TODO:
        turn this into an interface for creating dynamic tab widgets
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

# set attrs
tansu_widget.setHeaderPosition(attrs.NORTH)
tansu_widget.setMultiSelect(True)
tansu_widget.setMultiSelectDirection(Qt.Vertical)


tansu_widget.resize(500, 500)
tansu_widget.delegateWidget().handle_length = 100

tansu_widget.show()

tansu_widget.move(QCursor.pos())
sys.exit(app.exec_())
import sys
import math
import re

from qtpy.QtWidgets import (
    QApplication,
    QStackedWidget, QWidget, QVBoxLayout, QScrollArea,
    QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsItemGroup,
    QGraphicsLineItem, QLabel, QBoxLayout, QFrame, QGraphicsItem,
    QSizePolicy
)
from qtpy.QtCore import (Qt, QPoint, QEvent, QSize, QRectF)
from qtpy.QtGui import (
    QColor, QLinearGradient, QGradient, QBrush, QCursor, QPen
)

from cgwidgets.utils import attrs, draw, getWidgetAncestor, checkMousePos,  getWidgetAncestorByName
from cgwidgets.utils.draw import DualColoredLineSegment
from cgwidgets.widgets.InputWidgets import FloatInputWidget
from cgwidgets.widgets.AbstractWidgets import AbstractInputGroup
from cgwidgets.settings.colors import iColor

from cgwidgets.widgets.InputWidgets.ColorInputWidget import ColorPickerItem1D


class ColorHeaderWidgetItem(AbstractInputGroup):
    """
    Attributes:
        name (str)
        value (str)
        selected (bool)

    Widgets:
        | -- QBoxLayout
                | -- label_widget (QLabel)
                | -- divider_widget (AbstractLine)
                | -- value_widget (QLabel)
    """
    def __init__(self, parent=None, title='None', value='None'):
        super(ColorHeaderWidgetItem, self).__init__(parent, title)
        # setup attrs'
        self._color_arg = title
        self._value = value
        self._is_selected = False

        # setup GUI
        self.value_widget = FloatInputWidget()

        # setup ladder
        self.value_widget.setUseLadder(True, value_list=[0.0001, 0.001, 0.01, 0.1])
        self.setRange(True, 0, 1)
        self.value_widget.setAlignment(Qt.AlignLeft)
        self.insertWidget(1, self.value_widget)

    """ PROPERTIES """
    def setValue(self, value):
        self._value = value
        self.value_widget.setText(str(value))
        self.value_widget.setCursorPosition(0)

    def getValue(self):
        return self._value

    def setRange(self, enable, range_min, range_max):
        """
        Sets the range of the user input
        """
        self.value_widget.setRange(enable, range_min, range_max)

    def setAllowNegative(self, enabled):
        """
        Determines if the input will be allowed to go into negative numbers or
        not
        """
        self.value_widget.setAllowNegative(enabled)

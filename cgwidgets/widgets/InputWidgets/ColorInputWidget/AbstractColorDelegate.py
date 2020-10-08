import sys
import math

from qtpy.QtWidgets import (
    QApplication, QLabel, QVBoxLayout,
    QGraphicsView, QGraphicsScene, QGraphicsItemGroup, QGraphicsItem,
    QGraphicsEllipseItem,
    QGraphicsLineItem, QWidget, QFrame, QBoxLayout
)
from qtpy.QtCore import (Qt, QPoint, QRectF)
from qtpy.QtGui import (
    QColor, QCursor, QPen, QLinearGradient, QBrush
)

from cgwidgets.utils import (
    attrs, draw, getWidgetAncestor, getWidgetAncestorByName,
    getFontSize, installStickyValueAdjustItemDelegate
)
from cgwidgets.settings.colors import iColor, getHSVRGBAFloatFromColor
from cgwidgets.widgets.InputWidgets.ColorInputWidget import ColorHeaderWidgetItem


class AbstractColorDelegate(QWidget):
    """
    This is the cover that goes over the gradient so that it doesn't spam color at
    the user and hurt their precious precious eyes

    Attributes:
        color_header_items_dict (dict): of key pair values relating to the
            individual display values of each color arg
    """
    def __init__(self, parent=None):
        super(AbstractColorDelegate, self).__init__(parent=parent)
        # create scene
        QBoxLayout(QBoxLayout.TopToBottom, self)
        self._color = QColor(128, 128, 255)

    """ API """
    def color(self):
        return self._color

    def setColor(self, color):
        """
        Sets the color of this widget

        Args:
            color (QColor):
        """
        self._color = color
        # TODO will need this for the Clock Delegate
        self.updateDisplay()

    def setColorArgValue(self, arg, value):
        """

        arg (attrs.COLOR_ARG):
        value (float):
        """
        orig_color = self.color()
        selection_type = arg
        # saturation
        if selection_type == attrs.SATURATION:
            hue = orig_color.hueF()
            sat = value
            value = orig_color.valueF()
            orig_color.setHsvF(hue, sat, value)
        # hue
        elif selection_type == attrs.HUE:
            hue = value
            sat = orig_color.saturationF()
            value = orig_color.valueF()
            orig_color.setHsvF(hue, sat, value)
        # value
        elif selection_type == attrs.VALUE:
            # get HSV values
            hue = orig_color.hueF()
            sat = orig_color.saturationF()
            value = value
            orig_color.setHsvF(hue, sat, value)
        # red
        elif selection_type == attrs.RED:
            red = value
            orig_color.setRedF(red)
        # green
        elif selection_type == attrs.GREEN:
            green = value
            orig_color.setGreenF(green)
        # blue
        elif selection_type == attrs.BLUE:
            blue = value
            orig_color.setBlueF(blue)

        # set color from an arg value
        self.setColor(orig_color)

    def updateDisplay(self):
        """ This will need to be overwritten"""
        pass
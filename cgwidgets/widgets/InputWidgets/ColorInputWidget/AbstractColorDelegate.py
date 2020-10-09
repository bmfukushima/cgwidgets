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
        print('delegate update')
        self._color = color
        self.updateDisplay()

        # if parent... views need to inherit from something else?
        if self.parent():
            if self.parent().__name__() == "ColorInputWidget":
                self.parent().setColor(color)

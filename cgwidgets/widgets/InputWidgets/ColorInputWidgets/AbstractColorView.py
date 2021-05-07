import sys
import math

from qtpy.QtWidgets import (QWidget, QBoxLayout)
from qtpy.QtGui import (QColor)


class AbstractColorView(QWidget):
    """
    This is the cover that goes over the gradient so that it doesn't spam color at
    the user and hurt their precious precious eyes

    Attributes:
        color_header_items_dict (dict): of key pair values relating to the
            individual display values of each color arg
    """
    def __init__(self, parent=None):
        super(AbstractColorView, self).__init__(parent=parent)
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
        self.updateDisplay()

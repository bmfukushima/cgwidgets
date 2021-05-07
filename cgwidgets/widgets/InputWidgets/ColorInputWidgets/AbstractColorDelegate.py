import sys
import math

from qtpy.QtWidgets import (QWidget, QBoxLayout)
from qtpy.QtGui import QColor

from cgwidgets.utils import (getWidgetAncestorByName)


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
        self.updateDisplay()

        # if delegate, update main widget
        color_input_widget = getWidgetAncestorByName(self, "ColorInputWidget")
        if color_input_widget:
            self.parent().setColor(color)

        # set user input
        self.userInputFunction(self, color)


    """ VIRTUAL FUNCTION """
    def setUserInput(self, function):
        """
        Sets the function to be run everytime this widget updates:

        Args:
            function (function) that will be run every time that this input updates
                the color.  This function should take two args
                    QWidget, QColor
                where the QWidget will be the QWidget that is defined in this input
                as the current active widget

                NOTE:
                    widget isn't set up right now... but in theory is a place holder to return
                    the active widget.

        """
        self.__user_input_function = function

    def userInputFunction(self, widget, color):
        return self.__user_input_function(widget, color)

    def __user_input_function(self, widget, color):
        pass

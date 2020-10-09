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

from cgwidgets.utils import (
    attrs, draw, getWidgetAncestor, checkMousePos,  getWidgetAncestorByName,
    getFontSize
)

from cgwidgets.widgets.InputWidgets import FloatInputWidget
from cgwidgets.widgets.AbstractWidgets import AbstractInputGroup
from cgwidgets.settings.colors import iColor


class ColorGradientHeaderWidget(QScrollArea):
    """
    Widget that will contain all of the display values for the user.

    Attributes:
        widget_dict (dict): of DisplayLabels whose keys will be the title
            of the widget.  These will correspond with the
            ColorGraphicsScene.TYPE.  However, there will be no option
            for RGBA / rgba.  So don't use that...
        color (QColor): current color displayed.  This should call the delegates
            color property.

    Virtual Functions:
        headerItemChanged (widget, value): function to run when a header
            widget item has been changed.  This will be linked into the "live update"
            portion of the widget

    Widgets:
        | -- QScrollArea
                | -- QFrame
                        | -- QBoxLayout
                                | -* ColorHeaderWidgetItem

    """

    def __init__(self, delegate, parent=None, direction=QBoxLayout.LeftToRight):
        super(ColorGradientHeaderWidget, self).__init__(parent)
        self.setWidgetResizable(True)

        # setup default attrs
        self.item_height = getFontSize(QApplication) * 3 + 5
        self.item_width = 40
        self._delegate = delegate

        # setup GUI
        self._widget_dict = {}
        self.main_widget = QFrame(self)
        self.setWidget(self.main_widget)
        self.main_layout = QBoxLayout(direction, self.main_widget)

    def createHeaderItems(self, color_args_list, abbreviated_title=False):
        """
        Args:
            color_args_list (list): of attrs.COLOR_ARG, which will have a header
                item (ColorHeaderWidgetItem) craeted for it and stored in
                the dict color_header_items_dict as
                    color_arg : ColorHeaderWidgetItem
                    attrs.HUE: ColorHeaderWidgetItem
            abbreviated_title (bool): If true, the title will be displayed as the first
                letter of the color arg.
        """
        self._widget_dict = {}

        # create clock hands
        for index, color_arg in enumerate(color_args_list):
            # create header
            if abbreviated_title:
                title = color_arg[0]
            else:
                title = color_arg
            new_item = ColorHeaderWidgetItem(self, title=title, value=0)

            # setup header attrs
            new_item.setMinimumHeight(self.item_height)
            new_item.setMinimumWidth(self.item_width)
            new_item.value_widget.color_arg = color_arg

            # setup signals
            new_item.value_widget.setLiveInputEvent(self.headerItemChanged)

            # add to layout
            self._widget_dict[color_arg] = new_item
            self.main_widget.layout().addWidget(new_item)

    """ INPUT EVENT """
    def headerItemChanged(self, widget, value):
        """
        Updates the color based off of the specific input from the user
        widget (FloatInputWidget):
        value (str): string value set by the user

        """
        self.__header_item_changed(widget, value)

    def setHeaderItemChanged(self, function):
        self.__header_item_changed = function

    def __header_item_changed(self, widget, value):
        """
        color_arg = widget.color_arg
        main_widget = getWidgetAncestor(self, ClockDisplayWidget)
        main_widget.setColorArgValue(color_arg, float(value))
        """
        pass

    """ UTILS """
    def setColorArgValue(self, arg, value):
        """
        arg (attrs.COLOR_ARG):
        value (float):
        """

        orig_color = self.delegate().color()
        new_color = QColor(*orig_color.getRgb())
        selection_type = arg
        # saturation
        if selection_type == attrs.SATURATION:
            hue = new_color.hueF()
            sat = value
            value = new_color.valueF()
            new_color.setHsvF(hue, sat, value)
        # hue
        elif selection_type == attrs.HUE:
            hue = value
            sat = new_color.saturationF()
            value = new_color.valueF()
            new_color.setHsvF(hue, sat, value)
        # value
        elif selection_type == attrs.VALUE:
            # get HSV values
            hue = new_color.hueF()
            sat = new_color.saturationF()
            value = value
            new_color.setHsvF(hue, sat, value)
        # red
        elif selection_type == attrs.RED:
            red = value
            new_color.setRedF(red)
        # green
        elif selection_type == attrs.GREEN:
            green = value
            new_color.setGreenF(green)
        # blue
        elif selection_type == attrs.BLUE:
            blue = value
            new_color.setBlueF(blue)

        # set color from an arg value
        return new_color

    """ PROPERTIES"""
    def getWidgetDict(self):
        return self._widget_dict

    def delegate(self):
        return self._delegate

    def setDelegate(self, delegate):
        self._delegate = delegate

    def color(self):
        return self.delegate().color()

    def setColor(self, color):
        self.delegate()._color = color


class ColorHeaderWidgetItem(AbstractInputGroup):
    """
    Attributes:
        name (str)
        value (str)
        selected (bool)

    Widgets:
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

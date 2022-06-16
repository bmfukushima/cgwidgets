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
    draw, getWidgetAncestor, checkMousePos,  getWidgetAncestorByName,
    getFontSize
)

from cgwidgets.widgets.InputWidgets import FloatInputWidget
from cgwidgets.widgets.AbstractWidgets import AbstractInputGroup
from cgwidgets.settings.colors import updateColorFromArgValue
from cgwidgets.settings import attrs


class ColorHeaderWidget(QScrollArea):
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

    def __init__(self, parent=None, delegate=None, direction=QBoxLayout.LeftToRight):
        super(ColorHeaderWidget, self).__init__(parent)
        self.setWidgetResizable(True)

        # setup default attrs
        if not delegate:
            delegate = parent
        self._delegate = delegate
        self._header_item_type = ColorHeaderWidgetItem

        # setup GUI
        self._widget_dict = {}
        self.main_widget = QFrame(self)
        self.setWidget(self.main_widget)
        self.main_layout = QBoxLayout(direction, self.main_widget)

        # set signals
        self.setHeaderItemChanged(self.updateColorArg)

    """ UTILS """
    def createNewHeaderItem(self, title, value):
        header_item_type = self.headerItemType()
        new_item = header_item_type(self, title=title, value=value)
        return new_item

    def createHeaderItems(self, color_args_list, abbreviated_title=False):
        """ Creates all of the header items for adjusting RGBA/HSV

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

            new_item = self.createNewHeaderItem(title, 0)
            #new_item = ColorHeaderWidgetItem(self, title=title, value=0)

            # setup header attrs
            new_item.value_widget.color_arg = color_arg

            # setup signals
            new_item.value_widget.setLiveInputEvent(self.headerItemChanged)
            new_item.value_widget.setUserFinishedEditingEvent(self.headerItemChanged)
            # add to layout
            self._widget_dict[color_arg] = new_item
            self.main_widget.layout().addWidget(new_item)
            #self.layout().addWidget(new_item)

    def updateColorArg(self, widget, value):
        """
        Updates the color based off of the specific input from the user
        widget (FloatInputWidget):
        value (str): string value set by the user

        """
        # get attrs
        color_arg = widget.color_arg
        orig_color = self.delegate().color()
        new_color = updateColorFromArgValue(orig_color, color_arg, float(value))

        # check if updating
        _updating = True
        for color_arg in zip(orig_color.getRgb(), new_color.getRgb()):
            if color_arg[0] != color_arg[1]:
                _updating = False

        # update
        if _updating is False:
            self.delegate().setColor(new_color)

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
        widget
        value
        """
        pass

    """ PROPERTIES"""
    def headerItemType(self):
        return self._header_item_type

    def setHeaderItemType(self, _header_item_type):
        self._header_item_type = _header_item_type

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
        self.setRange(0.0, 1.0)
        self.value_widget.setAlignment(Qt.AlignLeft)
        self.insertWidget(1, self.value_widget)

    """ PROPERTIES """
    def setValue(self, value):
        self._value = value
        self.value_widget.setText(str(value))
        self.value_widget.setCursorPosition(0)

    def getValue(self):
        return self._value

    def setRange(self, range_min, range_max):
        """
        Sets the range of the user input
        """
        self.value_widget.setRange(range_min, range_max)

    def setAllowNegative(self, enabled):
        """
        Determines if the input will be allowed to go into negative numbers or
        not
        """
        self.value_widget.setAllowNegative(enabled)

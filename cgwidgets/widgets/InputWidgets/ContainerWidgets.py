"""
TODO
    AbstractInputGroup / ShojiInputWidgetContainer / LabelledInputWidget...
        Why do I have like 90 versions of this...
"""

import os

from qtpy.QtWidgets import (QSizePolicy)
from qtpy.QtCore import (QEvent, QDir)
from qtpy.QtWidgets import (QFileSystemModel, QCompleter, QApplication)
from qtpy.QtCore import Qt

from cgwidgets.widgets import (
    AbstractInputGroupFrame,
    AbstractFrameInputWidgetContainer,
    AbstractButtonInputWidgetContainer,
)

from cgwidgets.widgets import (
    ShojiModelViewWidget,
    ShojiModelItem
)
from cgwidgets.views import ShojiView
from cgwidgets.utils import (
    updateStyleSheet,
    attrs,
    getFontSize
)

try:
    from .InputWidgets import LabelledInputWidget, StringInputWidget, ListInputWidget, BooleanInputWidget
except ImportError:
    from InputWidgets import LabelledInputWidget, StringInputWidget, ListInputWidget, BooleanInputWidget


class ShojiInputWidgetContainerItem(ShojiModelItem):
    """
    widgetConstructor (widget): widget to build as based class
    value (str): current value set on this item

    """
    def getValue(self):
        return self._value

    def setValue(self, value):
        self._value = value

    """ Widget Type"""
    def widgetConstructor(self):
        return self._widget_constructor

    def setWidgetConstructor(self, widget_constructor):
        self._widget_constructor = widget_constructor

    """ setup user input event """
    def __userInputEvent(self, widget, value):
        return

    def setUserInputEvent(self, function):
        self.__userInputEvent = function

    def userInputEvent(self, widget, value):
        self.__userInputEvent(widget, value)

    def __userLiveInputEvent(self, widget, value):
        return

    def setUserLiveInputEvent(self, function):
        self.__userLiveInputEvent = function

    def userLiveInputEvent(self, widget, value):
        self.__userLiveInputEvent(self, widget, value)


class ShojiInputWidgetContainer(LabelledInputWidget):
    """
    A container for holding user parameters.  The default main
    widget is a ShojiWidget which can have the individual widgets
    added to it

    Widgets:
        ShojiInputWidgetContainer
            | -- getInputWidget() (AbstractShojiInputWidgetContainer)
                    | -- model
                    | -* (ShojiInputWidgetContainerItem)
    """
    def __init__(
        self,
        parent=None,
        name="None",
        note="None",
        direction=Qt.Vertical
    ):
        class AbstractShojiInputWidget(ShojiModelViewWidget):
            def __init__(self, parent=None):
                super(AbstractShojiInputWidget, self).__init__(parent)
                self.model().setItemType(ShojiInputWidgetContainerItem)
                self.setDelegateType(ShojiModelViewWidget.DYNAMIC)
                self.setHeaderPosition(attrs.WEST)
                self.setMultiSelect(True)
                self.setMultiSelectDirection(Qt.Vertical)

                # self.setHandleLength(50)
                self.delegateWidget().setHandleLength(50)
                self.setHeaderPosition(attrs.WEST, attrs.SOUTH)
                self.updateStyleSheet()

                self.setDelegateTitleIsShown(False)

        # inherit
        super(ShojiInputWidgetContainer, self).__init__(parent, name, direction=direction, widget_type=AbstractShojiInputWidget)

        self.setIsSoloViewEnabled(False)

        # setup main widget
        self.getInputWidget().setDelegateType(
            ShojiModelViewWidget.DYNAMIC,
            dynamic_widget=LabelledInputWidget,
            dynamic_function=self.updateGUI
        )

    @staticmethod
    def updateGUI(parent, widget, item):
        """
        widget (ShojiModelDelegateWidget)
        item (ShojiModelItem)
        """
        if item:
            # get attrs
            name = parent.model().getItemName(item)
            value = item.columnData()['value']
            labelled_widget = widget.getMainWidget()
            widget_constructor = item.widgetConstructor()

            # set attrs
            labelled_widget.setName(name)
            labelled_widget.setInputBaseClass(widget_constructor)
            input_widget = labelled_widget.getInputWidget()

            # update list inputs
            if isinstance(input_widget, ListInputWidget):
                item_list = item.columnData()['items_list']
                input_widget.populate(item_list)

            # update boolean inputs
            if isinstance(input_widget, BooleanInputWidget):
                # toggle
                widget.getMainWidget().getInputWidget().is_clicked = value
                updateStyleSheet(widget.getMainWidget().getInputWidget())
                return

            # set input widgets current value from item
            input_widget.setText(str(value))

            input_widget.setUserFinishedEditingEvent(item.userInputEvent)
            input_widget.setLiveInputEvent(item.userLiveInputEvent)

    def insertInputWidget(
            self,
            index,
            widget,
            name,
            user_input_event,
            user_live_update_event=None,
            data=None,
            display_data_type=False,
            default_value=''
        ):
        """
        Inserts a widget into the Main Widget

        index (int)
        widget (InputWidget)
        name (str)
        type (str):
        display_data_type (bool): determines if the data type will be displayed in the title
        user_input_event (function): should take two values widget, and value
            widget: widget that is currently being manipulated
            value: value being set
        value (str): current value if any should be set.  Boolean types will
            have this automatically overwritten to false in their constructor
        """
        # setup attrs
        if not data:
            data = {}

        if display_data_type:
            name = "{name}  |  {type}".format(name=name, type=widget.TYPE)

        if not 'name' in data:
            data['name'] = name
        if not 'value' in data:
            data['value'] = default_value

        # create item
        user_input_index = self.getInputWidget().insertShojiWidget(index, column_data=data)
        user_input_item = user_input_index.internalPointer()

        # setup new item
        user_input_item.setWidgetConstructor(widget)
        user_input_item.setUserInputEvent(user_input_event)
        user_input_item.setUserLiveInputEvent(user_live_update_event)

    def removeInputWidget(self, index):
        self.getInputWidget().removeTab(index)


""" CONTAINERS """
class FrameInputWidgetContainer(AbstractFrameInputWidgetContainer):
    def __init__(
        self,
        parent=None,
        name="None",
        note="None",
        direction=Qt.Horizontal
    ):
        # inherit
        super(FrameInputWidgetContainer, self).__init__(parent, name, note, direction)
        self.layout().setContentsMargins(0,0,0,0)


class ButtonInputWidgetContainer(AbstractButtonInputWidgetContainer):
    """
    Provides a multi button input widget.

    This widget should primarily be used for setting flags.

    Colors
    Hide Widget Handles?
    Args:
        buttons (list): of lists ["title", flag, virtualFunction]
        buttons (list): of lists ["title", flag, virtualFunction]
            The virtual  function needs to take one arg.  This arg
            will return the widget that is created to display this
            event

    Attributes:
        _buttons (dict): of clickable buttons
            name: button
        _current_buttons (List): of AbstractButtonInputWidget that are
            currently selected by the user
    """
    def __init__(self, parent=None, orientation=Qt.Horizontal):
        super(ButtonInputWidgetContainer, self).__init__(parent, orientation)


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication
    from cgwidgets.utils import centerWidgetOnCursor
    app = QApplication(sys.argv)

    def test(widget, value):
        print(widget, value)

    shoji_group_widget = ShojiInputWidgetContainer(parent=None, name='ShojiInputWidgetContainer')

    # add user inputs
    from cgwidgets.widgets import ButtonInputWidget, FloatInputWidget, IntInputWidget, BooleanInputWidget, StringInputWidget, ListInputWidget, PlainTextInputWidget
    shoji_group_widget.insertInputWidget(0, FloatInputWidget, 'Float', test)
    shoji_group_widget.insertInputWidget(0, IntInputWidget, 'Int', test)
    shoji_group_widget.insertInputWidget(0, ButtonInputWidget, 'Button', test)
    shoji_group_widget.insertInputWidget(0, BooleanInputWidget, 'Boolean', test)
    shoji_group_widget.insertInputWidget(0, StringInputWidget, 'String', test)
    #shoji_group_widget.insertInputWidget(0, ListInputWidget, 'List', test, data={'items_list': list_of_crap})
    shoji_group_widget.insertInputWidget(0, PlainTextInputWidget, 'Text', test)

    shoji_group_widget.display_background = False


    shoji_group_widget.show()
    centerWidgetOnCursor(shoji_group_widget)

    sys.exit(app.exec_())
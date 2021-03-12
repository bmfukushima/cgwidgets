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
    AbstractButtonInputWidget)

from cgwidgets.widgets import (
    ShojiModelViewWidget,
    ShojiModelItem,
    ShojiLayout)
from cgwidgets.utils import (
    updateStyleSheet,
    attrs,
    getFontSize)
from cgwidgets.settings.colors import iColor

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


class ButtonInputWidgetContainer(ShojiLayout):
    """
    Provides a multi button input widget.

    This widget will align all of the widgets that are currently selected
    higher up in the priority, ie insertWidget(0, widget), and those that
    are not selected further down in the priority ie. insertWidget(-1, widget).

    Note: that each of this widgets returns a flag

    Attributes:
        _buttons (dict): of clickable buttons
            name: button
        _current_buttons (List): of AbstractButtonInputWidget that are
            currently selected by the user
    """

    def __init__(self, parent=None, orientation=Qt.Horizontal):
        self._rgba_flag = iColor["rgba_selected_hover"]
        super(ButtonInputWidgetContainer, self).__init__(parent, orientation)
        self.setIsSoloViewEnabled(False)
        self.setIsHandleStatic(True)
        self.setHandleWidth(0)
        self.setHandleLength(-1)

        #
        self._buttons = {}
        self._is_multi_select = True
        self._current_buttons = []
        self._is_toggleable = True

        self.setIsHandleVisible(False)

    """ GET FLAGS """

    def flags(self):
        buttons = self.currentButtons()
        return [button.flag() for button in buttons]

    """ PROPERTIES """

    def isMultiSelect(self):
        return self._is_multi_select

    def setIsMultiSelect(self, enabled):
        self._is_multi_select = enabled

    def isToggleable(self):
        return self._is_toggleable

    def setIsToggleable(self, enabled):
        self._is_toggleable = enabled

    """ BUTTONS """

    def updateButtonSelection(self, selected_button, enabled=None):
        """
        Sets the button provided to either be enabled or disabled
        Args:
            selected_button (AbstractButtonInputWidget):
            enabled (bool):

        Returns:

        """
        if enabled is not None:
            self.setButtonAsCurrent(selected_button, enabled)
        else:
            if selected_button in self.currentButtons():
                self.setButtonAsCurrent(selected_button, False)
            else:
                self.setButtonAsCurrent(selected_button, True)

        # update display
        for button in self._buttons.values():
            if button not in self.currentButtons():
                button.setProperty("is_selected", False)
                updateStyleSheet(button)
        self.normalizeWidgetSizes()

    def currentButtons(self):
        return self._current_buttons

    def setButtonAsCurrent(self, current_button, enabled):
        """
        Sets the button provided as enabled/disabled.

        Args:
            current_button (AbstractButtonInputWidget): to enable/disable
            enabled (bool):
        """
        current_button.setParent(None)
        # multi select
        if self.isMultiSelect():
            # add to list
            if enabled:
                self._current_buttons.append(current_button)
                self.insertWidget(len(self.currentButtons()) - 1, current_button)

            # remove from list
            else:
                if current_button in self._current_buttons:
                    self._current_buttons.remove(current_button)
                self.insertWidget(len(self.currentButtons()), current_button)

        # single select
        else:
            self._current_buttons = [current_button]
            self.insertWidget(0, current_button)

        # setup button style
        if enabled:
            current_button.is_selected = True

        self.update()

    def addButton(self, title, flag, user_clicked_event=None, enabled=False, image=None):
        """
        Adds a button to this widget

        Args:
            title (str): display name
            enabled (bool): determines the default status of the button
            flag (arbitrary): flag to be returned to denote that this button is selected
            user_clicked_event (function): to run when the user clicks
            image:

        Returns (AbstractButtonInputWidget): newly created button
        Note:
            image is not currently setup.  This kwarg is merely a place holder.
        Todo: setup image
        """
        button = AbstractButtonInputWidget(self, user_clicked_event=user_clicked_event, title=title, flag=flag,
                                           is_toggleable=self.isToggleable())
        self.updateButtonSelection(button, enabled)
        self._buttons[title] = button
        self.addWidget(button)
        return button

    """ EVENTS """

    def showEvent(self, event):
        """
        Reorganizes widgets into correct order
        """
        for button in self._current_buttons:
            self.insertWidget(0, button)
        return ShojiLayout.showEvent(self, event)


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
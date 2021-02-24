"""
TODO
    AbstractInputGroup / ShojiGroupInputWidget / LabelledInputWidget...
        Why do I have like 90 versions of this...
"""

import os

from qtpy.QtWidgets import (QSizePolicy)
from qtpy.QtCore import (QEvent, QDir)
from qtpy.QtWidgets import (QFileSystemModel, QCompleter, QApplication)
from qtpy.QtCore import Qt

from cgwidgets.widgets import (
    AbstractInputGroup,
    AbstractInputGroupFrame,
    AbstractFrameGroupInputWidget,
    AbstractFloatInputWidget,
    AbstractIntInputWidget,
    AbstractStringInputWidget,
    AbstractBooleanInputWidget,
    AbstractOverlayInputWidget,
    AbstractVLine,
    AbstractHLine,
    AbstractComboListInputWidget,
    AbstractListInputWidget,
    AbstractInputPlainText,
    AbstractMultiButtonInputWidget,
    AbstractButtonInputWidget
)

from cgwidgets.widgets import (
    ShojiModelViewWidget,
    ShojiModelDelegateWidget,
    ShojiModelItem
)
from cgwidgets.views import ShojiView
from cgwidgets.utils import (
    getWidgetAncestor,
    updateStyleSheet,
    attrs,
    installCompleterPopup,
    getFontSize
)
from cgwidgets.settings.colors import iColor


class ShojiInputWidgetItem(ShojiModelItem):
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
        self.__userInputEvent(self, widget, value)

    def __userLiveInputEvent(self, widget, value):
        return

    def setUserLiveInputEvent(self, function):
        self.__userLiveInputEvent = function

    def userLiveInputEvent(self, widget, value):
        self.__userLiveInputEvent(self, widget, value)


class iShojiGroupInput(object):
    """
    Interface for group input objects.  This is added to all of the input
    widget types so that they will be compatible with the GroupInputWidgets
    user_input_event (function): function to be run when editing has completed
    live_input_event (function); function to be run every time the text has changed
    """
    def __init__(self):
        self.setUserFinishedEditingEvent(self.updateUserInputItem)

    """ VIRTUAL EVENTS """
    def __user_finished_editing_event(self, *args, **kwargs):
        pass

    def setUserFinishedEditingEvent(self, function):
        """
        Sets the function that should be triggered everytime
        the user finishes editing this widget

        This function should take two args
        widget/item, value
        """
        self.__user_finished_editing_event = function

    def userFinishedEditingEvent(self, *args, **kwargs):
        """
        Internal event to run everytime the user triggers an update.  This
        will need to be called on every type of widget.
        """
        self.__user_finished_editing_event(*args, **kwargs)

    def __live_input_event(self, *args, **kwargs):
        pass

    def setLiveInputEvent(self, function):
        self.__live_input_event = function

    def liveInputEvent(self, *args, **kwargs):
        self.__live_input_event(*args, **kwargs)

    """ TANSU UPDATE """
    def updateUserInputItem(self, *args):
        """
        When the user inputs text, this will update the model item
        """
        # print('args')
        # for arg in args:
        #     print (arg)
        try:
            widget = getWidgetAncestor(self, ShojiModelDelegateWidget)
            widget.item().columnData()['value'] = self.getInput()
            widget.item().userInputEvent(args[0], self.getInput())
            #widget.item().userInputEvent(self, self.getInput())
        except AttributeError:
            pass

        # add user input event

    @staticmethod
    def updateDynamicWidget(parent, widget, item):
        """
        When the dynamic widget is created.  This will set
        the display text to the user
        """
        #value = item.getArg('value')
        value = item.columnData()['value']
        widget.getMainWidget().getInputWidget().setText(str(value))


class OverlayInputWidget(AbstractOverlayInputWidget):
    """
    Input widget with a display delegate overlaid.  This delegate will dissapear
    when the user first hover enters.

    Args:
        input_widget (QWidget): Widget for user to input values into
        title (string): Text to display when the widget is shown
            for the first time.

    Attributes:
        input_widget:
        overlay_widget:
    """
    def __init__(
            self,
            parent=None,
            input_widget=None,
            title=""
    ):
        super(OverlayInputWidget, self).__init__(parent, input_widget=input_widget, title=title)


class ButtonInputWidget(AbstractButtonInputWidget):
    def __init__(self, parent=None,  user_clicked_event=None, title=None, flag=None, is_toggleable=False):
        super(ButtonInputWidget, self).__init__(parent, is_toggleable=is_toggleable, user_clicked_event=user_clicked_event, title=title, flag=flag)


class FloatInputWidget(AbstractFloatInputWidget, iShojiGroupInput):
    def __init__(self, parent=None):
        super(FloatInputWidget, self).__init__(parent)
        self.setDoMath(True)


class IntInputWidget(AbstractIntInputWidget, iShojiGroupInput):
    def __init__(self, parent=None):
        super(IntInputWidget, self).__init__(parent)


class StringInputWidget(AbstractStringInputWidget, iShojiGroupInput):
    def __init__(self, parent=None):
        super(StringInputWidget, self).__init__(parent)


class PlainTextInputWidget(AbstractInputPlainText, iShojiGroupInput):
    def __init__(self, parent=None):
        super(PlainTextInputWidget, self).__init__(parent)


class BooleanInputWidget(AbstractBooleanInputWidget, iShojiGroupInput):
    def __init__(self, parent=None, text=None, is_selected=False):
        super(BooleanInputWidget, self).__init__(parent, is_selected=is_selected, text=text)
        self.setUserFinishedEditingEvent(self.updateUserInputItem)
        #self.setupStyleSheet()

    def updateUserInputItem(self, *args):
        """
        When the user clicks on this
        """
        try:
            widget = getWidgetAncestor(self, ShojiModelDelegateWidget)
            widget.item().columnData()['value'] = self.is_clicked
            self.is_clicked = self.is_clicked

            # add user input event
            widget.item().userInputEvent(self.is_clicked)
        except AttributeError:
            pass

    # @staticmethod
    # def updateDynamicWidget(parent, widget, item):
    #     """
    #     When the dynamic widget is created.  This will set
    #     the display text to the user
    #     # get default value
    #     # this is because the default value is set as '' during the constructor in
    #     # ShojiGroupInputWidget --> insertInputWidget
    #     """
    #     # get value
    #     try:
    #         value = item.columnData()['value']
    #     except:
    #         value = False
    #
    #     # toggle
    #     widget.getMainWidget().getInputWidget().is_clicked = value
    #     updateStyleSheet(widget.getMainWidget().getInputWidget())


class ComboListInputWidget(AbstractComboListInputWidget, iShojiGroupInput):
    TYPE = "list"
    def __init__(self, parent=None):
        super(ComboListInputWidget, self).__init__(parent)
        self.setUserFinishedEditingEvent(self.updateUserInputItem)
        #self.editingFinished.connect(self.userFinishedEditing)

    def userFinishedEditing(self):
        #self.userFinishedEditingEvent(self, self.currentText())
        return AbstractComboListInputWidget.userFinishedEditing(self)

    def updateUserInputItem(self, *args):
        try:
            widget = getWidgetAncestor(self, ShojiModelDelegateWidget)
            widget.item().setValue(self.currentText())

            # add user input event
            widget.item().userInputEvent(self.currentText())

        except AttributeError:

            pass

    @staticmethod
    def updateDynamicWidget(parent, widget, item):
        item_list = item.getArg('items_list')
        widget.getMainWidget().getInputWidget().populate(item_list)
        # print(widget, item)


class ListInputWidget(AbstractListInputWidget, iShojiGroupInput):
    def __init__(self, parent=None, item_list=[]):
        super(ListInputWidget, self).__init__(parent)
        self.populate(item_list)
        self.setUserFinishedEditingEvent(self.updateUserInputItem)
        #self.editingFinished.connect(self.userFinishedEditing)

    def userFinishedEditing(self):
        #self.userFinishedEditingEvent(self, self.currentText())
        return AbstractListInputWidget.userFinishedEditing(self)

    def updateUserInputItem(self, *args):
        try:
            widget = getWidgetAncestor(self, ShojiModelDelegateWidget)
            widget.item().columnData()['value'] = self.text()

            # add user input event
            widget.item().userInputEvent(self.text())

        except AttributeError:
            pass

    # @staticmethod
    # def updateDynamicWidget(parent, widget, item):
    #     item_list = item.columnData()['items_list']
    #     value = item.columnData()['value']
    #
    #     widget.getMainWidget().getInputWidget().populate(item_list)
    #     widget.getMainWidget().getInputWidget().setText(value)
    #     # print(widget, item)


class FileBrowserInputWidget(AbstractListInputWidget, iShojiGroupInput):
    def __init__(self, parent=None):
        super(FileBrowserInputWidget, self).__init__(parent=parent)

        # setup model
        self.model = QFileSystemModel()
        self.model.setRootPath('/home/')
        filters = self.model.filter()
        self.model.setFilter(filters | QDir.Hidden)

        # setup completer
        completer = QCompleter(self.model, self)
        self.setCompleter(completer)
        installCompleterPopup(completer)

        self.setCompleter(completer)
        completer.setCaseSensitivity(Qt.CaseInsensitive)

        self.autoCompleteList = []

    def checkDirectory(self):
        directory = str(self.text())
        if os.path.isdir(directory):
            self.model.setRootPath(str(self.text()))

    def event(self, event, *args, **kwargs):
        # I think this is the / key... lol
        if (event.type() == QEvent.KeyRelease) and event.key() == 47:
            self.checkDirectory()
            #self.completer().popup().show()
            self.completer().complete()

        return AbstractListInputWidget.event(self, event, *args, **kwargs)
# TODO move these under one architecture...
# abstract input group
# AbstractInputGroupBox
# TODO Move to one architecture

""" CONTAINERS """
class LabelledInputWidget(ShojiView, AbstractInputGroupFrame):
    """
    A single input widget.  This inherits from the ShojiView,
    to provide a slider for the user to expand/contract the editable area
    vs the view label.

    Note:
        Needs parent to be provided in order for the default size to be
        displayed correctly
    """
    def __init__(
        self,
        parent=None,
        name="None",
        note="None",
        direction=Qt.Horizontal,
        widget_type=StringInputWidget
    ):
        super(LabelledInputWidget, self).__init__(parent, direction)
        AbstractInputGroupFrame.__init__(self, parent, name, note, direction)

        # set up attrs
        self._input_widget = None #hack to make the setInputBaseClass update work
        self._default_label_length = 50
        self._separator_length = -1
        self._separator_width = 5
        self.__splitter_event_is_paused = False
        self.setInputBaseClass(widget_type)

        # create base widget
        self._input_widget = widget_type(self)
        self._input_widget.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.Preferred
        )

        # add widgets
        self.addWidget(self._label)
        self.addWidget(self._input_widget)

        # set size hints
        font_size = getFontSize(QApplication)
        self._input_widget.setMinimumSize(1, int(font_size*2.5))
        self._label.setMinimumSize(font_size*2, int(font_size*2.5))
        #
        self.setStretchFactor(0, 0)
        self.setStretchFactor(1, 1)
        self.resetSliderPositionToDefault()

        # setup style
        self.splitterMoved.connect(self.__splitterMoved)

        self.setIsSoloViewEnabled(False)

    """ HANDLE GROUP FRAME MOVING"""

    def __splitterMoved(self, pos, index):
        modifiers = QApplication.keyboardModifiers()

        if modifiers in [Qt.AltModifier]:
            return
        else:
            if not self.__splitter_event_is_paused:
                self.setAllHandlesToPos(pos)

    @staticmethod
    def getAllParrallelWidgets(labelled_input_widget):
        """
        Returns a list of all of the parallel LabelledInputWidgets

        Args:
            labelled_input_widget (LabelledInputWidgets)
        """
        parent = labelled_input_widget.parent()
        handles_list = []
        if isinstance(parent, FrameGroupInputWidget):
            widget_list = parent.getInputWidgets()
            for widget in widget_list:
                handles_list.append(widget)

        return handles_list

    def setAllHandlesToPos(self, pos):
        """
        Sets all of the handles to the pos provided

        Args:
            pos (int): value offset of the slider
        Attributes:
            __splitter_event_is_paused (bool): blocks events from updating
        :param pos:
        :return:
        """
        self.__splitter_event_is_paused = True
        widgets_list = LabelledInputWidget.getAllParrallelWidgets(self)

        for widget in widgets_list:
            widget.moveSplitter(pos, 1)

        self.__splitter_event_is_paused = False
        # todo
        # how to handle ShojiGroups?
        #ShojiGroupInputWidget

    def getHandlePosition(self):
        """
        Need to figure out how to return the handles position...

        :return:
        """
        return

    def setInputWidget(self, _input_widget):
        # remove previous input widget
        if self.getInputWidget():
            self.getInputWidget().setParent(None)

        # create new input widget
        self._input_widget = _input_widget
        self._input_widget.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding
        )

    def getInputWidget(self):
        return self._input_widget

    def setInputBaseClass(self, _input_widget_base_class):

        self._input_widget_base_class = _input_widget_base_class

        if self.getInputWidget():
            self.getInputWidget().setParent(None)

            # create new input widget
            self._input_widget = _input_widget_base_class(self)
            self._input_widget.setMinimumSize(1, 1)
            self._input_widget.setSizePolicy(
                QSizePolicy.MinimumExpanding, QSizePolicy.Preferred
            )
            # reset splitter
            self.addWidget(self._input_widget)
            self._input_widget.show()
            self.resetSliderPositionToDefault()

    def getInputBaseClass(self):
        return self._input_widget_base_class

    def setSeparatorLength(self, length):
        self.setHandleLength(length)
        self._separator_length = length

    def setSeparatorWidth(self, width):
        self.setHandleWidth(width)
        self._separator_width = width

    def setDirection(self, direction, update_defaults=False):
        """

        Args:
            direction (Qt.DIRECITON):
            update_defaults (bool): If enabled will automagically update
                the display of the splitter to correctly display the default sizes.

        Returns:

        """
        # preflight
        if direction not in [Qt.Horizontal, Qt.Vertical]: return

        # set direction
        self.setOrientation(direction)

        # setup minimum sizes
        font_size = getFontSize(QApplication)
        if direction == Qt.Vertical:
            # hide handle?
            self.setHandleMarginOffset(0)
            self.setIsHandleVisible(False)
            self.setIsHandleStatic(True)
            self.setMinimumSize(font_size*4, font_size*6)
        elif direction == Qt.Horizontal:
            self.setHandleMarginOffset(15)
            self.setIsHandleVisible(True)
            self.setIsHandleStatic(False)
            self.setMinimumSize(font_size*12, int(font_size*2.5))

        # update defaults
        if update_defaults:
            if direction == Qt.Horizontal:
                self.setDefaultLabelLength(50)
                self.setSeparatorWidth(30)
            elif direction == Qt.Vertical:
                self.setDefaultLabelLength(30)
            self.resetSliderPositionToDefault()

        # update label
        return AbstractInputGroupFrame.setDirection(self, direction)

    def defaultLabelLength(self):
        return self._default_label_length

    def setDefaultLabelLength(self, length):
        self._default_label_length = length

    """ EVENTS """
    def resetSliderPositionToDefault(self):
        #print(self.defaultLabelLength())
        self.moveSplitter(self.defaultLabelLength(), 1)

    def setUserFinishedEditingEvent(self, function):
        self._input_widget.setUserFinishedEditingEvent(function)

    def showEvent(self, event):
        super(LabelledInputWidget, self).showEvent(event)
        self.resetSliderPositionToDefault()
        return ShojiView.showEvent(self, event)

    def resizeEvent(self, event):
        super(LabelledInputWidget, self).resizeEvent(event)
        self.resetSliderPositionToDefault()
        return ShojiView.resizeEvent(self, event)


class FrameGroupInputWidget(AbstractFrameGroupInputWidget):
    def __init__(
        self,
        parent=None,
        name="None",
        note="None",
        direction=Qt.Horizontal
    ):
        # inherit
        super(FrameGroupInputWidget, self).__init__(parent, name, note, direction)


class ShojiGroupInputWidget(LabelledInputWidget):
    """
    A container for holding user parameters.  The default main
    widget is a ShojiWidget which can have the individual widgets
    added to it

    Widgets:
        ShojiGroupInputWidget
            | -- getInputWidget() (AbstractShojiGroupInputWidget)
                    | -- model
                    | -* (ShojiInputWidgetItem)
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
                self.model().setItemType(ShojiInputWidgetItem)
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
        super(ShojiGroupInputWidget, self).__init__(parent, name, direction=direction, widget_type=AbstractShojiInputWidget)

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
            #labelled_widget.setIsSoloViewEnabled(False)
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

            #input_widget.setUserFinishedEditingEvent(item.userInputEvent)
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

    # def keyPressEvent(self, event):
    #     return
        # print('shoji group input?')
        # if self.getInputWidget():
        #     return self.getInputWidget().keyPressEvent(event)


class MultiButtonInputWidget(AbstractMultiButtonInputWidget):
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
    def __init__(self, parent=None, buttons=None, orientation=Qt.Horizontal):
        super(MultiButtonInputWidget, self).__init__(parent, buttons, orientation)


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication, QWidget, QVBoxLayout
    from qtpy.QtGui import QCursor

    import sys, inspect

    app = QApplication(sys.argv)
    # def userEvent(widget):
    #     print("user input...", widget)
    #
    #
    # def asdf(item, widget, value):
    #     return
    #
    #
    # @staticmethod
    # def liveEdit(item, widget, value):
    #     return
    #
    #
    # widget = ShojiGroupInputWidget(name="test")
    # inputs = ["cx", "cy", "fx", "fy", "radius"]  # , stops"""
    # for i in inputs:
    #     widget.insertInputWidget(0, FloatInputWidget, i, asdf,
    #                            user_live_update_event=asdf, default_value=0.5)

    def test(widget):
        print("testing == ", widget)
    widget = ButtonInputWidget(user_clicked_event=test, title="None", flag=False, is_toggleable=False)
    widget.setIsToggleable(False)
    #test_labelled_embed = LabelledInputWidget(name="embed", widget_type=FloatInputWidget)
    #labelled_input = LabelledInputWidget(name="test", widget_type=test_labelled_embed)

    widget.move(QCursor.pos())
    widget.show()
    #widget.resize(256, 256)
    widget.resize(500, 500)
    widget.show()
    #w.move(QCursor.pos())
    sys.exit(app.exec_())

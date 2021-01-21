"""
TODO
    AbstractInputGroup / TansuGroupInputWidget / LabelledInputWidget...
        Why do I have like 90 versions of this...
"""

import os

from qtpy.QtWidgets import (
    QComboBox, QLineEdit, QCompleter, QSizePolicy
)

from qtpy.QtGui import(
    QStandardItem, QStandardItemModel
)
from qtpy.QtCore import (
    QEvent, Qt, QSortFilterProxyModel, Qt, QEvent, QDir
)

from qtpy.QtWidgets import (
    QSplitter, QLabel, QFrame, QBoxLayout, QLineEdit, QWidget, QLineEdit, QFileSystemModel, QApplication, QCompleter, QListView, QStyledItemDelegate)
from qtpy.QtCore import Qt

from cgwidgets.widgets import (
    AbstractInputGroup,
    AbstractInputGroupFrame,
    AbstractFrameGroupInputWidget,
    AbstractFloatInputWidget,
    AbstractIntInputWidget,
    AbstractStringInputWidget,
    AbstractBooleanInputWidget,
    AbstractVLine,
    AbstractHLine,
    AbstractComboListInputWidget,
    AbstractListInputWidget,
    AbstractInputPlainText,
)

from cgwidgets.widgets import (
    TansuModelViewWidget,
    TansuModelDelegateWidget,
    TansuModelItem
)
from cgwidgets.delegates import TansuDelegate
from cgwidgets.utils import (
    getWidgetAncestor,
    updateStyleSheet,
    attrs,
    installCompleterPopup,
    getFontSize
)
from cgwidgets.settings.colors import iColor


class TansuInputWidgetItem(TansuModelItem):
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
    def __userInputEvent(self, value):
        return

    def setUserInputEvent(self, function):
        self.__userInputEvent = function

    def userInputEvent(self, value):
        self.__userInputEvent(self, value)


class iTansuGroupInput(object):
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
        try:
            widget = getWidgetAncestor(self, TansuModelDelegateWidget)
            widget.item().columnData()['value'] = self.getInput()
            widget.item().userInputEvent(self.getInput())
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


class FloatInputWidget(AbstractFloatInputWidget, iTansuGroupInput):
    def __init__(self, parent=None):
        super(FloatInputWidget, self).__init__(parent)
        self.setDoMath(True)


class IntInputWidget(AbstractIntInputWidget, iTansuGroupInput):
    def __init__(self, parent=None):
        super(IntInputWidget, self).__init__(parent)


class StringInputWidget(AbstractStringInputWidget, iTansuGroupInput):
    def __init__(self, parent=None):
        super(StringInputWidget, self).__init__(parent)


class PlainTextInputWidget(AbstractInputPlainText, iTansuGroupInput):
    def __init__(self, parent=None):
        super(PlainTextInputWidget, self).__init__(parent)


class BooleanInputWidget(AbstractBooleanInputWidget, iTansuGroupInput):
    def __init__(self, parent=None, is_clicked=False):
        super(BooleanInputWidget, self).__init__(parent, is_clicked=is_clicked)
        self.setUserFinishedEditingEvent(self.updateUserInputItem)
        self.setupStyleSheet()

    def updateUserInputItem(self, *args):
        """
        When the user clicks on this
        """
        try:
            widget = getWidgetAncestor(self, TansuModelDelegateWidget)
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
    #     # TansuGroupInputWidget --> insertInputWidget
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


class ComboListInputWidget(AbstractComboListInputWidget, iTansuGroupInput):
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
            widget = getWidgetAncestor(self, TansuModelDelegateWidget)
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


class ListInputWidget(AbstractListInputWidget, iTansuGroupInput):
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
            widget = getWidgetAncestor(self, TansuModelDelegateWidget)
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


class FileBrowserInputWidget(AbstractListInputWidget, iTansuGroupInput):
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
class LabelledInputWidget(TansuDelegate, AbstractInputGroupFrame):
    """
    A single input widget.  This inherits from the TansuDelegate,
    to provide a slider for the user to expand/contract the editable area
    vs the view label.
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
        self._default_label_length = 125
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
        self._input_widget.setMinimumSize(1, font_size*2.5)
        self._label.setMinimumSize(font_size*2, font_size*2.5)
        #
        self.setStretchFactor(0, 0)
        self.setStretchFactor(1, 1)

        self.resetSliderPositionToDefault()

        # setup style
        self.rgba_background = iColor['rgba_gray_1']

        self.splitterMoved.connect(self.__splitterMoved)

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
        # how to handle TansuGroups?
        #TansuGroupInputWidget

    def getHandlePosition(self):
        """
        Need to figure out how to return the handles position...

        :return:
        """
        return

    # ?
    def getHandleOffset(self):
        pass

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

        # remove input widget and rebuild
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
            # todo
            # I'm guesseing this never does what I'm expecting...

    def getInputBaseClass(self):
        return self._input_widget_base_class

    def setSeparatorLength(self, length):
        self.handle_length = length
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
            self.setMinimumSize(font_size*4, font_size*6)
        else:
            self.setMinimumSize(font_size*12, font_size*2.5)

        # update defaults
        if update_defaults:
            if direction == Qt.Horizontal:
                self.setDefaultLabelLength(100)
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
        self.moveSplitter(self.defaultLabelLength(), 1)
        #self.moveSplitter(100, 1)
        #self.setSizes([1, 1000])

    def setUserFinishedEditingEvent(self, function):
        self._input_widget.setUserFinishedEditingEvent(function)

    def showEvent(self, event):

        super(LabelledInputWidget, self).showEvent(event)
        self.resetSliderPositionToDefault()
        return TansuDelegate.showEvent(self, event)
        #return return_val

    def resizeEvent(self, event):
        super(LabelledInputWidget, self).resizeEvent(event)
        self.resetSliderPositionToDefault()
        return TansuDelegate.resizeEvent(self, event)


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


class TansuGroupInputWidget(AbstractFrameGroupInputWidget):
    """
    A container for holding user parameters.  The default main
    widget is a TansuWidget which can have the individual widgets
    added to it

    Widgets:
        TansuGroupInputWidget
            | -- main_widget (AbstractTansuGroupInputWidget)
                    | -- model
                    | -* (TansuInputWidgetItem)
    """
    def __init__(
        self,
        parent=None,
        name="None",
        note="None",
        direction=Qt.Vertical
    ):
        # inherit
        super(TansuGroupInputWidget, self).__init__(parent, name, note, direction)

        # setup main widget
        self.main_widget = AbstractTansuInputWidget(self)
        self.layout().addWidget(self.main_widget)

        # set default orientation
        self.setDirection(Qt.Vertical)

        self.main_widget.setDelegateType(
            TansuModelViewWidget.DYNAMIC,
            dynamic_widget=LabelledInputWidget,
            dynamic_function=self.updateGUI
        )

    @staticmethod
    def updateGUI(parent, widget, item):
        """
        widget (TansuModelDelegateWidget)
        item (TansuModelItem)
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

    def insertInputWidget(self, index, widget, name, user_input_event, data=None):
        """
        Inserts a widget into the Main Widget

        index (int)
        widget (InputWidget)
        name (str)
        type (str):
        user_input_event (function): should take two values widget, and value
            widget: widget that is currently being manipulated
            value: value being set
        value (str): current value if any should be set.  Boolean types will
            have this automatically overwritten to false in their constructor
        """
        # setup attrs
        if not data:
            data = {}
        name = "{name}  |  {type}".format(name=name, type=widget.TYPE)
        if not 'name' in data:
            data['name'] = name
        if not 'value' in data:
            data['value'] = ''

        # create item
        user_input_index = self.main_widget.insertTansuWidget(index, column_data=data)
        user_input_item = user_input_index.internalPointer()

        # setup new item
        # TODO something...
        # hide tansu header for widgets...
        # use a frameInputGroupWidget thingy as the widget base class?
        #input_frame = LabelledInputWidget(name=name, widget_type=widget)

        #user_input_item.setDynamicWidgetBaseClass(input_frame)
        # tansu update?
        #user_input_item.setDynamicUpdateFunction(widget.updateDynamicWidget)
        user_input_item.setWidgetConstructor(widget)
        user_input_item.setUserInputEvent(user_input_event)

    def removeInputWidget(self, index):
        self.main_widget.removeTab(index)


class AbstractTansuInputWidget(TansuModelViewWidget):
    def __init__(self, parent=None):
        super(AbstractTansuInputWidget, self).__init__(parent)
        self.model().setItemType(TansuInputWidgetItem)
        self.setDelegateType(TansuModelViewWidget.DYNAMIC)
        self.setHeaderPosition(attrs.WEST)
        self.setMultiSelect(True)
        self.setMultiSelectDirection(Qt.Vertical)

        self.handle_length = 50
        self.delegateWidget().handle_length = 50
        self.updateStyleSheet()

        self.setDelegateTitleIsShown(False)

"""
TODO
    it all seems to be working...
        When it goes over a certain length... ~50, then it will take up the entire width
        and when its under a certain width... it will auto magically be removed
"""


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import (
        QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox)
    from qtpy.QtGui import QCursor
    app = QApplication(sys.argv)

    """ Group Widget"""
    frame_group_input_widget = FrameGroupInputWidget(name='Frame Input Widgets', direction=Qt.Vertical)

    # set header editable / Display
    frame_group_input_widget.setIsHeaderEditable(True)
    frame_group_input_widget.setIsHeaderShown(True)

    # Add widgets
    label_widgets = {
        "float": FloatInputWidget,
        "int": IntInputWidget,
        "bool": BooleanInputWidget,
        "str": StringInputWidget,
        "list": ListInputWidget,
        "text": PlainTextInputWidget
    }

    for arg in label_widgets:
        # create widget
        widget_type = label_widgets[arg]
        input_widget = LabelledInputWidget(name=arg, widget_type=widget_type)

        # set widget orientation
        input_widget.setDirection(Qt.Horizontal)

        # add to group layout
        frame_group_input_widget.addInputWidget(input_widget)

    LabelledInputWidget.getAllParrallelWidgets(input_widget)



    frame_group_input_widget.show()
    frame_group_input_widget.move(QCursor.pos())

    #input_widget.offsetAllHandles(5)
    #input_widget.offsetAllHandles(5)

    sys.exit(app.exec_())

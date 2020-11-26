"""
TODO
    AbstractInputGroup / GroupInputWidget / FrameInputWidget...
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
    AbstractFloatInputWidget,
    AbstractIntInputWidget,
    AbstractStringInputWidget,
    AbstractBooleanInputWidget,
    AbstractVLine,
    AbstractHLine,
    AbstractComboListInputWidget,
    AbstractListInputWidget,
    AbstractInputPlainText
)

from cgwidgets.widgets import (
    TansuModelViewWidget,
    TansuModelDelegateWidget,
    TansuModelItem,
    TansuBaseWidget
)
from cgwidgets.utils import getWidgetAncestor, updateStyleSheet, attrs, installCompleterPopup
from cgwidgets.settings.colors import iColor


class UserInputItem(TansuModelItem):
    def getValue(self):
        return self._value

    def setValue(self, value):
        self._value = value

    """ setup user input event """
    def __userInputEvent(self, value):
        return

    def setUserInputEvent(self, function):
        self.__userInputEvent = function

    def userInputEvent(self, value):
        self.__userInputEvent(self, value)

    # """ args """
    # def setArgs(self, args):
    #     self._args = args
    #
    # def getArgs(self):
    #     return self._args
    #
    # def getArg(self, arg):
    #     return self.getArgs()[arg]
    #
    # def addArg(self, arg, value):
    #     self.getArgs()[arg] = value
    #
    # def removeArg(self, arg):
    #     del self.getArgs()[arg]


class GroupInputWidget(AbstractInputGroup):
    """
    A container for holding user parameters.  The default main
    widget is a TansuWidget which can have the individual widgets
    added to it

    Widgets:
        GroupInputWidget
            | -- main_widget (GroupInputTansuWidget)
                    | -- model
                    | -* (UserInputItem)
    """
    def __init__(self, parent=None, title=None):

        super(GroupInputWidget, self).__init__(parent, title)

        # setup main widget
        self.group_box.main_widget = GroupInputTansuWidget(self)
        self.group_box.layout().addWidget(self.group_box.main_widget)

    def insertInputWidget(self, index, widget, name, userInputEvent, data=None):
        """
        Inserts a widget into the Main Widget

        index (int)
        widget (InputWidget)
        name (str)
        type (str):
        userInputEvent (fun)
        value (str): current value if any should be set.  Bolean types will
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
        user_input_index = self.group_box.main_widget.insertTansuWidget(index, column_data=data)
        user_input_item = user_input_index.internalPointer()

        # setup new item
        user_input_item.setDynamicWidgetBaseClass(widget)
        user_input_item.setDynamicUpdateFunction(widget.updateDynamicWidget)
        user_input_item.setUserInputEvent(userInputEvent)

    def removeInputWidget(self, index):
        self.group_box.main_widget.removeTab(index)


class GroupInputTansuWidget(TansuModelViewWidget):
    def __init__(self, parent=None):
        super(GroupInputTansuWidget, self).__init__(parent)
        self.model().setItemType(UserInputItem)
        self.setDelegateType(TansuModelViewWidget.DYNAMIC)
        self.setHeaderPosition(attrs.WEST)
        self.setMultiSelect(True)
        self.setMultiSelectDirection(Qt.Vertical)

        self.handle_length = 50
        self.delegateWidget().handle_length = 50
        self.updateStyleSheet()


class iGroupInput(object):
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
        widget.getMainWidget().setText(str(value))


class FloatInputWidget(AbstractFloatInputWidget, iGroupInput):
    def __init__(self, parent=None):
        super(FloatInputWidget, self).__init__(parent)
        self.setDoMath(True)


class IntInputWidget(AbstractIntInputWidget, iGroupInput):
    def __init__(self, parent=None):
        super(IntInputWidget, self).__init__(parent)


class StringInputWidget(AbstractStringInputWidget, iGroupInput):
    def __init__(self, parent=None):
        super(StringInputWidget, self).__init__(parent)


class PlainTextInputWidget(AbstractInputPlainText, iGroupInput):
    def __init__(self, parent=None):
        super(PlainTextInputWidget, self).__init__(parent)


class BooleanInputWidget(AbstractBooleanInputWidget, iGroupInput):
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

    @staticmethod
    def updateDynamicWidget(parent, widget, item):
        """
        When the dynamic widget is created.  This will set
        the display text to the user
        # get default value
        # this is because the default value is set as '' during the constructor in
        # GroupInputWidget --> insertInputWidget
        """
        # get value
        try:
            value = item.columnData()['value']
        except:
            value = False

        # toggle
        widget.getMainWidget().is_clicked = value
        updateStyleSheet(widget.getMainWidget())


class ComboListInputWidget(AbstractComboListInputWidget, iGroupInput):
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
        widget.getMainWidget().populate(item_list)
        # print(widget, item)


class ListInputWidget(AbstractListInputWidget, iGroupInput):
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

    @staticmethod
    def updateDynamicWidget(parent, widget, item):
        item_list = item.columnData()['items_list']
        value = item.columnData()['value']
        widget.getMainWidget().populate(item_list)
        widget.getMainWidget().setText(value)
        # print(widget, item)


class FileBrowserInputWidget(AbstractListInputWidget, iGroupInput):
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


class FrameInputWidget(TansuBaseWidget, AbstractInputGroupFrame):
    """
    A single input widget.  This inherits from the TansuBaseWidget,
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
        super(FrameInputWidget, self).__init__(parent, direction)
        AbstractInputGroupFrame.__init__(self, parent, name, note, direction)

        # set up attrs
        self._default_label_length = 50
        self.setInputBaseClass(widget_type)

        # create base widget
        self._input_widget = widget_type(self)
        self._input_widget.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.Preferred
        )
        self.addWidget(self._label)
        self.addWidget(self._input_widget)

        #
        self.setStretchFactor(0, 0)
        self.setStretchFactor(1, 1)

        self.rgba_background = iColor['rgba_gray_1']

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

    def getInputBaseClass(self):
        return self._input_widget_base_class

    def setSeparatorLength(self, length):
        self.handle_length = length
        self._separator_length = length

    def setSeparatorWidth(self, width):
        self.setHandleWidth(width)
        self._separator_width = width

    def setDirection(self, direction):
        # preflight
        if direction not in [Qt.Horizontal, Qt.Vertical]: return

        # set direction
        self.setOrientation(direction)

        # update label
        return AbstractInputGroupFrame.setDirection(self, direction)

    def defaultLabelLength(self):
        return self._default_label_length

    def setDefaultLabelLength(self, length):
        self._default_label_length = length

    """ EVENTS """
    def setUserFinishedEditingEvent(self, function):
        self._input_widget.setUserFinishedEditingEvent(function)
    #
    def showEvent(self, event):
        self.moveSplitter(self.defaultLabelLength(), 1)
        return TansuBaseWidget.showEvent(self, event)


class FrameGroupInputWidget(AbstractInputGroupFrame):
    """
    Stylized input group.  This has a base of a TansuBaseWidget,
    I'm not really sure why this is different than the InputGroupWidget...
    """
    def __init__(
        self,
        parent=None,
        name="None",
        note="None",
        direction=Qt.Horizontal
    ):
        # inherit
        super(FrameGroupInputWidget, self).__init__(parent, name, note, direction)

        # create separator
        self._separator = AbstractVLine(self)

        # add widgets to main layout
        self.layout().insertWidget(0, self._label)
        self.layout().addWidget(self._separator)

    def setSeparatorLength(self, length):
        self._separator.setLength(length)
        self._separator_length = length

    def setSeparatorWidth(self, width):
        self._separator.setLineWidth(width)
        self._separator_width = width

    def setDirection(self, direction):
        """
        Sets the direction this input will be displayed as.

        Args:
            direction (Qt.DIRECTION)
        """
        # preflight
        if direction not in [Qt.Horizontal, Qt.Vertical]: return

        # set direction
        self._direction = direction

        # update separator
        if direction == Qt.Vertical:
            # direction
            self.layout().setDirection(QBoxLayout.TopToBottom)

            # separator
            self.updateSeparator(direction)

            # update alignment
            self._label.setAlignment(Qt.AlignCenter)
            self.layout().setAlignment(Qt.AlignCenter)
            self.layout().setSpacing(5)

            # update label
            self._label.setSizePolicy(
                QSizePolicy.MinimumExpanding, QSizePolicy.Preferred
            )

        elif direction == Qt.Horizontal:
            # set layout direction
            self.layout().setDirection(QBoxLayout.LeftToRight)

            # update separator
            self.updateSeparator(direction)

            # alignment
            self.layout().setAlignment(Qt.AlignLeft)
            self.layout().setSpacing(50)

            # update label
            self._label.setSizePolicy(
                QSizePolicy.Fixed, QSizePolicy.Preferred
            )

        return AbstractInputGroupFrame.setDirection(self, direction)

    def updateSeparator(self, direction):
        # remove existing separator
        if hasattr(self, '_separator'):
            self._separator.setParent(None)

        # create new separator
        if direction == Qt.Vertical:
            self._separator = AbstractHLine()
        elif direction == Qt.Horizontal:
            self._separator = AbstractVLine()

        # update separator
        self.setSeparatorWidth(self._separator_width)
        self.setSeparatorLength(self._separator_length)
        self.layout().insertWidget(1, self._separator)

    def addInputWidget(self, widget, finished_editing_function=None):
        if finished_editing_function:
            widget.setUserFinishedEditingEvent(finished_editing_function)
        self.layout().addWidget(widget)

    def getInputWidgets(self):
        input_widgets = []
        for index in self.layout().count()[2:]:
            widget = self.layout().itemAt(index).widget()
            input_widgets.append(widget)

        return input_widgets


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import (
        QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox)
    from qtpy.QtGui import QCursor
    app = QApplication(sys.argv)

    # testwidget = QLabel()
    # testwidget.setText('init')
    # l.addWidget(testwidget)
    list_of_crap = [
        ['a', (0, 0, 0, 255)], ['b', (0, 0, 0, 255)], ['c', (0, 0, 0, 255)], ['d', (0, 0, 0, 255)], ['e', (0, 0, 0, 255)],
        ['aa', (255, 0, 0, 255)], ['bb', (0, 255, 0, 255)], ['cc', (0, 0, 255, 255)], ['dd'], ['ee'],
        ['aba'], ['bcb'], ['cdc'], ['ded'], ['efe']
    ]
    l2 = [['a', (255, 0, 0, 255)], ['b'], ['c'], ['aa'], ['bb'], ['cc']]

    def test(widget, value):
        #print('setting value to... ', value)
        #print(widget, value)
        pass
        #widget.setText(str(value))

    """ group insert """
    group_widget_layout = QVBoxLayout()
    gw = GroupInputWidget(parent=None, title='cool stuff')

    # add user inputs
    gw.insertInputWidget(0, FloatInputWidget, 'Float', test)
    gw.insertInputWidget(0, IntInputWidget, 'Int', test)
    gw.insertInputWidget(0, BooleanInputWidget, 'Boolean', test)
    gw.insertInputWidget(0, StringInputWidget, 'String', test)
    gw.insertInputWidget(0, ListInputWidget, 'List', test, data={'items_list':list_of_crap})
    gw.insertInputWidget(0, PlainTextInputWidget, 'Plain Text', test, data={'items_list':list_of_crap})

    gw.display_background = False
    group_widget_layout.addWidget(gw)

    """ normal widgets """
    normal_widget = QGroupBox()
    normal_widget.setTitle("Normal Widgets")
    normal_widget_layout = QVBoxLayout(normal_widget)

    float_input_widget = FloatInputWidget()
    float_input_widget.setUseLadder(True)
    int_input_widget = IntInputWidget()
    int_input_widget.setUseLadder(True, value_list=[1, 2, 3, 4, 5])
    boolean_input_widget = BooleanInputWidget()
    string_input_widget = StringInputWidget()
    list_input_widget = ListInputWidget(item_list=list_of_crap)

    normal_widget_layout.addWidget(float_input_widget)
    normal_widget_layout.addWidget(int_input_widget)
    normal_widget_layout.addWidget(boolean_input_widget)
    normal_widget_layout.addWidget(string_input_widget)
    normal_widget_layout.addWidget(list_input_widget)

    float_input_widget.setUserFinishedEditingEvent(test)
    int_input_widget.setUserFinishedEditingEvent(test)
    boolean_input_widget.setUserFinishedEditingEvent(test)
    string_input_widget.setUserFinishedEditingEvent(test)
    list_input_widget.setUserFinishedEditingEvent(test)

    # """ Label widgets """
    # horizontal_label_widget = QGroupBox()
    # horizontal_label_widget.setTitle("Frame Widgets (Horizontal)")
    # horizontal_label_widget_layout = QVBoxLayout(horizontal_label_widget)
    #
    # u_float_input_widget = FrameInputWidget(name="float", widget_type=FloatInputWidget)
    # u_int_input_widget = FrameInputWidget(name="int", widget_type=IntInputWidget)
    # u_boolean_input_widget = FrameInputWidget(name="bool", widget_type=BooleanInputWidget)
    # u_string_input_widget = FrameInputWidget(name='str', widget_type=StringInputWidget)
    # u_list_input_widget = FrameInputWidget(name='list', widget_type=ListInputWidget)
    # u_list_input_widget.getInputWidget().populate(list_of_crap)
    # u_list_input_widget.getInputWidget().display_item_colors = True
    #
    # horizontal_label_widget_layout.addWidget(u_float_input_widget)
    # horizontal_label_widget_layout.addWidget(u_int_input_widget)
    # horizontal_label_widget_layout.addWidget(u_boolean_input_widget)
    # horizontal_label_widget_layout.addWidget(u_string_input_widget)
    # horizontal_label_widget_layout.addWidget(u_list_input_widget)
    #
    # u_float_input_widget.setUserFinishedEditingEvent(test)
    # u_int_input_widget.setUserFinishedEditingEvent(test)
    # u_boolean_input_widget.setUserFinishedEditingEvent(test)
    # u_string_input_widget.setUserFinishedEditingEvent(test)
    # u_list_input_widget.setUserFinishedEditingEvent(test)

    """ Label widgets ( Vertical )"""
    vertical_label_widget = QGroupBox()
    vertical_label_widget.setTitle("Frame Widgets ( Vertical )")
    vertical_label_widget_layout = QVBoxLayout(vertical_label_widget)

    u_text_input_widget = FrameInputWidget(name="text", widget_type=PlainTextInputWidget)

    #u_float_input_widget.setSeparatorLength(100)
    #u_float_input_widget.setSeparatorWidth(3)
    u_int_input_widget = FrameInputWidget(name="float", widget_type=FloatInputWidget)
    u_int_input_widget = FrameInputWidget(name="int", widget_type=IntInputWidget)
    u_boolean_input_widget = FrameInputWidget(name="bool", widget_type=BooleanInputWidget)
    u_string_input_widget = FrameInputWidget(name='str', widget_type=StringInputWidget)
    u_list_input_widget = FrameInputWidget(name='list', widget_type=ListInputWidget)
    u_list_input_widget.getInputWidget().populate(list_of_crap)
    u_list_input_widget.getInputWidget().display_item_colors = True
    #
    #u_float_input_widget.setDirection(Qt.Vertical)
    u_int_input_widget.setDirection(Qt.Vertical)
    u_boolean_input_widget.setDirection(Qt.Vertical)
    u_string_input_widget.setDirection(Qt.Vertical)
    u_list_input_widget.setDirection(Qt.Vertical)
    #
    vertical_label_widget_layout.addWidget(u_text_input_widget)
    vertical_label_widget_layout.addWidget(u_int_input_widget)
    vertical_label_widget_layout.addWidget(u_boolean_input_widget)
    vertical_label_widget_layout.addWidget(u_string_input_widget)
    vertical_label_widget_layout.addWidget(u_list_input_widget)

    #u_float_input_widget.setUserFinishedEditingEvent(test)
    u_int_input_widget.setUserFinishedEditingEvent(test)
    u_boolean_input_widget.setUserFinishedEditingEvent(test)
    u_string_input_widget.setUserFinishedEditingEvent(test)
    u_list_input_widget.setUserFinishedEditingEvent(test)

    """ FRAME GROUP """

    """ Main Widget"""
    main_widget = QWidget()
    main_layout = QHBoxLayout(main_widget)
    main_layout.addLayout(group_widget_layout)
    main_layout.addWidget(normal_widget)
    main_layout.addWidget(vertical_label_widget)
    #main_layout.addWidget(horizontal_label_widget)

    main_widget.resize(500, 500)
    main_widget.show()
    main_widget.move(QCursor.pos())

    sys.exit(app.exec_())

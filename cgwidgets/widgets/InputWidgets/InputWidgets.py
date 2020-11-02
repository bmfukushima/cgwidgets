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
    AbstractFloatInputWidget,
    AbstractIntInputWidget,
    AbstractStringInputWidget,
    AbstractBooleanInputWidget,
    AbstractVLine,
    AbstractHLine,
    AbstractComboListInputWidget,
    AbstractListInputWidget
)

from cgwidgets.widgets import TansuModelViewWidget, TansuModelDelegateWidget, TansuModelItem
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

    """ args """
    def setArgs(self, args):
        self._args = args

    def getArgs(self):
        return self._args

    def getArg(self, arg):
        return self.getArgs()[arg]

    def addArg(self, arg, value):
        self.getArgs()[arg] = value

    def removeArg(self, arg):
        del self.getArgs()[arg]


class GroupInputWidget(AbstractInputGroup):
    def __init__(self, parent=None, title=None):
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
        super(GroupInputWidget, self).__init__(parent, title)

        # setup main widget
        self.group_box.main_widget = GroupInputTansuWidget(self)
        self.group_box.layout().addWidget(self.group_box.main_widget)

    def insertInputWidget(self, index, widget, name, userInputEvent, data={}):
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
        name = "{name}  |  {type}".format(name=name, type=widget.TYPE)
        data['value'] = ''
        # create item
        user_input_index = self.group_box.main_widget.insertTansuWidget(index, column_data={'name': name})
        user_input_item = user_input_index.internalPointer()

        # setup new item
        user_input_item.setArgs(data)
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
            widget.item().setValue(self.getInput())
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
        value = item.getArg('value')
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
            widget.item().setValue(self.is_clicked)
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
            value = item.getArg['value']
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

class FrameInputWidget(QFrame):
    """
    name (str): the name displayed to the user
    input_widget (InputWidgetInstance): The instance of the input widget type
        that is displayed to the user for manipulation
    input_widget_base_class (InputWidgetClass): The type of input widget that this is
        displaying to the user
            Options are:
                BooleanInputWidget
                StringInputWidget
                IntInputWidget
                FloatInputWidget
                ListInputWidget
    """
    def __init__(
        self,
        parent=None,
        name="None",
        note="None",
        widget_type=StringInputWidget,
        direction=Qt.Horizontal
    ):
        super(FrameInputWidget, self).__init__(parent)
        QBoxLayout(QBoxLayout.LeftToRight, self)

        # set up attrs
        self.setInputBaseClass(widget_type)

        # setup layout
        self._label = QLabel(name)
        self._separator = AbstractVLine()
        self._input_widget = widget_type(self)
        self._input_widget.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.Preferred
        )

        self.layout().addWidget(self._label)
        self.layout().addWidget(self._separator)
        self.layout().addWidget(self._input_widget)

        # set up display
        self.setToolTip(note)
        self.setLabelWidth(50)
        self.setupStyleSheet()
        self.setDirection(direction)

    def setupStyleSheet(self):
        style_sheet_args = iColor.style_sheet_args
        style_sheet = """
        QLabel{{color: rgba{rgba_text}}}
        FrameInputWidget{{background-color: rgba{rgba_gray_1}}}
        """.format(
            **style_sheet_args
        )
        self.setStyleSheet(style_sheet)
        # self._label.setStyleSheet(
        #     self._label.styleSheet() + 'color: rgba{rgba_text}'.format(
        #         rgba_text=iColor.rgba_text))

    def setToolTip(self, tool_tip):
        self._label.setToolTip(tool_tip)

    """ Set Direction of input"""
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
            self.__updateSeparator(direction)

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
            self.__updateSeparator(direction)

            # alignment
            self.layout().setAlignment(Qt.AlignLeft)
            self.layout().setSpacing(50)

            # update label
            self._label.setSizePolicy(
                QSizePolicy.Fixed, QSizePolicy.Preferred
            )

    def __updateSeparator(self, direction):
        self._separator.setParent(None)
        if direction == Qt.Vertical:
            self._separator = AbstractHLine()
        elif direction == Qt.Horizontal:
            self._separator = AbstractVLine()
        self._separator.setLineWidth(5)
        self.layout().insertWidget(1, self._separator)

    """ PROPERTIES """
    def setName(self, name):
        self._label.setText(name)

    def getName(self):
        return self._label.text()

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

    def labelWidth(self):
        return self._label_width

    def setLabelWidth(self, width):
        self._label_width = width
        self._label.setMinimumWidth(width)

    """ EVENTS """
    def setUserFinishedEditingEvent(self, function):
        self._input_widget.setUserFinishedEditingEvent(function)


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
    l2 = [['a', (255,0,0, 255)], ['b'], ['c'], ['aa'], ['bb'], ['cc']]

    def test(widget, value):
        print(widget, value)
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

    gw.display_background = False
    group_widget_layout.addWidget(gw)

    """ normal widgets """
    normal_widget = QGroupBox()
    normal_widget.setTitle("Normal Widgets")
    normal_widget_layout = QVBoxLayout(normal_widget)

    float_input_widget = FloatInputWidget()
    float_input_widget.setUseLadder(True)
    int_input_widget = IntInputWidget()
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


    """ Label widgets """
    vertical_label_widget = QGroupBox()
    vertical_label_widget.setTitle("Frame Widgets (Horizontal)")
    vertical_label_widget_layout = QVBoxLayout(vertical_label_widget)

    u_float_input_widget = FrameInputWidget(name="float", widget_type=FloatInputWidget)
    u_int_input_widget = FrameInputWidget(name="int", widget_type=IntInputWidget)
    u_boolean_input_widget = FrameInputWidget(name="bool", widget_type=BooleanInputWidget)
    u_string_input_widget = FrameInputWidget(name='str', widget_type=StringInputWidget)
    u_list_input_widget = FrameInputWidget(name='list', widget_type=ListInputWidget)
    u_list_input_widget.getInputWidget().populate(list_of_crap)
    u_list_input_widget.getInputWidget().display_item_colors = True

    vertical_label_widget_layout.addWidget(u_float_input_widget)
    vertical_label_widget_layout.addWidget(u_int_input_widget)
    vertical_label_widget_layout.addWidget(u_boolean_input_widget)
    vertical_label_widget_layout.addWidget(u_string_input_widget)
    vertical_label_widget_layout.addWidget(u_list_input_widget)

    u_float_input_widget.setUserFinishedEditingEvent(test)
    u_int_input_widget.setUserFinishedEditingEvent(test)
    u_boolean_input_widget.setUserFinishedEditingEvent(test)
    u_string_input_widget.setUserFinishedEditingEvent(test)
    u_list_input_widget.setUserFinishedEditingEvent(test)

    """ FRAME INPUT WIDGETS"""
    q = FrameInputWidget(name="Float", widget_type=FloatInputWidget)
    q.setDirection(Qt.Vertical)
    e = FrameInputWidget(name="List", widget_type=ListInputWidget)
    e.getInputWidget().populate(list_of_crap)
    e.setDirection(Qt.Vertical)
    t = FrameInputWidget(name="Bool", widget_type=BooleanInputWidget)
    t.setDirection(Qt.Vertical)
    # l.addWidget(q)
    # l.addWidget(t)
    # l.addWidget(e)
    # main_widget = ListInputWidget()
    # main_widget.populate(['a','b','c','d'])
    #main_widget.setInputBaseClass(ListInputWidget)

    """ Main Widget"""
    main_widget = QWidget()
    main_layout = QHBoxLayout(main_widget)
    main_layout.addLayout(group_widget_layout)
    main_layout.addWidget(normal_widget)
    main_layout.addWidget(label_widget)

    main_widget.resize(500, 500)
    main_widget.show()
    main_widget.move(QCursor.pos())

    sys.exit(app.exec_())

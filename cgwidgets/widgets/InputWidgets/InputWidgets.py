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
    AbstractInputGroup,
    AbstractInputGroupFrame,
    AbstractFrameInputWidgetContainer,
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
    AbstractButtonInputWidget
)

from cgwidgets.widgets import (
    ShojiModelViewWidget,
    ShojiModelDelegateWidget,
    ShojiModelItem
)
from cgwidgets.widgets import ShojiLayout
from cgwidgets.utils import (
    getWidgetAncestor,
    updateStyleSheet,
    attrs,
    installCompleterPopup,
    getFontSize
)
from cgwidgets.settings.colors import iColor


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


class FloatInputWidget(AbstractFloatInputWidget):
    def __init__(self, parent=None):
        super(FloatInputWidget, self).__init__(parent)
        self.setDoMath(True)


class IntInputWidget(AbstractIntInputWidget):
    def __init__(self, parent=None):
        super(IntInputWidget, self).__init__(parent)


class StringInputWidget(AbstractStringInputWidget):
    def __init__(self, parent=None):
        super(StringInputWidget, self).__init__(parent)


class PlainTextInputWidget(AbstractInputPlainText):
    def __init__(self, parent=None):
        super(PlainTextInputWidget, self).__init__(parent)


class BooleanInputWidget(AbstractBooleanInputWidget):
    def __init__(self, parent=None, text=None, is_selected=False):
        super(BooleanInputWidget, self).__init__(parent, is_selected=is_selected, text=text)
        self.setUserFinishedEditingEvent(self.updateUserInputItem)

    def updateUserInputItem(self, *args):
        """
        When the user clicks on this
        """
        try:
            widget = getWidgetAncestor(self, ShojiModelDelegateWidget)
            widget.item().columnData()['value'] = self.is_selected
            self.is_selected = self.is_selected

            # add user input event
            widget.item().userInputEvent(self, self.is_selected)

        except AttributeError:
            pass


class ComboListInputWidget(AbstractComboListInputWidget):
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


class ListInputWidget(AbstractListInputWidget):
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


class LabelledInputWidget(ShojiLayout, AbstractInputGroupFrame):
    """
    A single input widget.  This inherits from the ShojiLayout,
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

        # todo this blocks hover display...
        self.setIsSoloViewEnabled(False)
        #self._input_widget.setProperty("hover_display", True)

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
        from .ContainerWidgets import FrameInputWidgetContainer
        parent = labelled_input_widget.parent()
        handles_list = []
        if isinstance(parent, FrameInputWidgetContainer):
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
        #ShojiInputWidgetContainer

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
        #self._input_widget.setProperty("hover_display", True)
        #if self._input_widget has
        #self.addHoverDisplay(self._input_widget)

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
        return ShojiLayout.showEvent(self, event)

    def resizeEvent(self, event):
        super(LabelledInputWidget, self).resizeEvent(event)
        self.resetSliderPositionToDefault()
        return ShojiLayout.resizeEvent(self, event)


class FileBrowserInputWidget(AbstractListInputWidget):
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
    # widget = ShojiInputWidgetContainer(name="test")
    # inputs = ["cx", "cy", "fx", "fy", "radius"]  # , stops"""
    # for i in inputs:
    #     widget.insertInputWidget(0, FloatInputWidget, i, asdf,
    #                            user_live_update_event=asdf, default_value=0.5)


    test_labelled_embed = LabelledInputWidget(name="embed", widget_type=FloatInputWidget)
    #labelled_input = LabelledInputWidget(name="test", widget_type=test_labelled_embed)

    test_labelled_embed.move(QCursor.pos())
    test_labelled_embed.show()
    #test_labelled_embed.resize(256, 256)
    test_labelled_embed.resize(500, 500)
    test_labelled_embed.show()
    #w.move(QCursor.pos())
    sys.exit(app.exec_())

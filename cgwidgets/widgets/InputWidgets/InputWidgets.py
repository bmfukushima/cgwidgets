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
    AbstractLabelledInputWidget,
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
            delegate_widget=None,
            image_path=None,
            title="",
            display_mode=4
    ):
        super(OverlayInputWidget, self).__init__(
            parent,
            delegate_widget=delegate_widget,
            image_path=image_path,
            title=title,
            display_mode=display_mode)


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


class LabelledInputWidget(AbstractLabelledInputWidget):
    """
    A single input widget.  This inherits from the ShojiLayout,
    to provide a slider for the user to expand/contract the editable area
    vs the view label.

    Args:
        name (str):
        note (str):
        direction (Qt.ORIENTATION):
        default_label_length (int): default length to display labels when showing this widget
        widget_type (QWidget): Widget type to be constructed for as the delegate widget

    Hierarchy:
        |- ViewWidget --> AbstractOverlayInputWidget
        |- DelegateWidget --> QWidget

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
        default_label_length=50,
        delegate_widget=None
    ):
        super(LabelledInputWidget, self).__init__(
            parent,
            name=name,
            note=note,
            default_label_length=default_label_length,
            direction=direction,
            delegate_widget=delegate_widget
        )


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


    test_labelled_embed = LabelledInputWidget(name="embed", delegate_widget=FloatInputWidget())
    #labelled_input = LabelledInputWidget(name="test", delegate_widget=test_labelled_embed)

    test_labelled_embed.move(QCursor.pos())
    test_labelled_embed.show()
    #test_labelled_embed.resize(256, 256)
    test_labelled_embed.resize(500, 500)
    test_labelled_embed.show()
    #w.move(QCursor.pos())
    sys.exit(app.exec_())

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
    AbstractCommandsInputWidget,
    AbstractInputGroup,
    AbstractInputGroupFrame,
    AbstractFrameInputWidgetContainer,
    AbstractFloatInputWidget,
    AbstractIntInputWidget,
    AbstractStringInputWidget,
    AbstractBooleanInputWidget,
    AbstractOverlayInputWidget,
    AbstractLabelWidget,
    AbstractVLine,
    AbstractHLine,
    AbstractListInputWidget,
    AbstractInputPlainText,
    AbstractButtonInputWidget
)

from cgwidgets.widgets import (ShojiModelDelegateWidget)
from cgwidgets.utils import (
    getWidgetAncestor,
    installCompleterPopup
)


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


class LabelWidget(AbstractLabelWidget):
    def __init__(self, parent=None, text=None, image=None):
        super(LabelWidget, self).__init__(parent=parent, text=text, image=image)


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


class CommandsInputWidget(AbstractCommandsInputWidget):
    def __init__(self, parent=None):
        super(CommandsInputWidget, self).__init__(parent)


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
        note=None,
        direction=Qt.Horizontal,
        default_label_length=50,
        delegate_widget=None,
        delegate_constructor=None,
        view_as_read_only=True,
    ):
        super(LabelledInputWidget, self).__init__(
            parent,
            name=name,
            note=note,
            default_label_length=default_label_length,
            direction=direction,
            delegate_widget=delegate_widget,
            delegate_constructor=delegate_constructor,
            view_as_read_only=view_as_read_only,
        )


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
    label_widget = LabelWidget(text="lakjsdf")
    label_widget.show()

    #w.move(QCursor.pos())
    sys.exit(app.exec_())

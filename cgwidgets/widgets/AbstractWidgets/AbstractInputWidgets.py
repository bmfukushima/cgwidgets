"""
Input Group
    AbstractInputGroupBox (QGroupBox)
        | -- TabShojiWidget
                | -* InputWidget

Input Widgets
    iAbstractInputWidget (QLineEdit)
        | -- AbstractStringInputWidget
        | -- AbstractNumberInputWidget
                | -- AbstractFloatInputWidget
                | -- AbstractIntInputWidget
    BooleanInputWidget (QLabel)
"""
import re

from qtpy.QtWidgets import (
    QLineEdit, QLabel, QPlainTextEdit, QStackedWidget, QApplication
)
from qtpy.QtCore import Qt, QEvent


from cgwidgets.settings.colors import iColor
from cgwidgets.settings.keylist import NUMERICAL_INPUT_KEYS, MATH_KEYS
from cgwidgets.utils import (
    installLadderDelegate, getFontSize, checkIfValueInRange,
    checkNegative, setAsTransparent, updateStyleSheet
)

from cgwidgets.settings.icons import icons
from cgwidgets.settings.stylesheets import input_widget_ss
from cgwidgets.settings.hover_display import installHoverDisplaySS, removeHoverDisplay


class iAbstractInputWidget(object):
    """
    Base class for users to input data into.

    Attributes:
        orig_value (str): the previous value set by the user
        key_list (list): of Qt.Key_KEY.  List of keys that are currently
            valid for this widget.
        updating (bool): Flag to determine if this widget should be Continuously updating
            or not.  Most noteably this flag will be toggled during sticky drag events.
        rgba_background (rgba): value of rgba_background transparency
        rgba_border (rgba): color of the border...
        rgba_text (rgba): color of text
    """

    def __init__(self):
        super(iAbstractInputWidget, self).__init__()
        # setup default args
        self._key_list = []
        self._orig_value = None
        self._updating = False

        # set up style
        self.rgba_border = iColor["rgba_outline"]
        self.rgba_background = iColor["rgba_background_00"]
        self.rgba_text = iColor["rgba_text"]
        self.rgba_selected_hover = iColor["rgba_selected_hover"]

        # setup properties
        self.setProperty("input_hover", True)

        self.updateStyleSheet()

        font_size = getFontSize(QApplication)
        self.setMinimumSize(font_size*2, font_size*2)

    def updateStyleSheet(self):
        style_sheet_args = iColor.style_sheet_args
        style_sheet_args.update({
            "rgba_background": repr(self.rgba_background),
            "rgba_border": repr(self.rgba_border),
            "rgba_text": repr(self.rgba_text),
            "rgba_selected_hover": repr(self.rgba_selected_hover),
            "rgba_invisble": iColor["rgba_invisible"],
            "rgba_selected_background": iColor["rgba_selected_background"],
            "gradient_background": icons["gradient_background"],
            "type": type(self).__name__
        })
        style_sheet = """
            {input_widget_ss}
        """.format(input_widget_ss=input_widget_ss.format(**style_sheet_args))
        self.setStyleSheet(style_sheet)

        # add hover display
        hover_type_flags = {
            'focus':{'input_hover':True},
            'hover_focus':{'input_hover':True},
            'hover':{'input_hover':True},
        }
        installHoverDisplaySS(
            self,
            name="INPUT WIDGETS",
            hover_type_flags=hover_type_flags)

    """ UTILS """
    def setValidateInputFunction(self, function):
        """
        Sets the function that will validate the users input.  This function
        should take no args, and will need to return True/False.  This will be the
        check to determine if the users input is valid or not.
        """
        self._validate_user_input = function

    def checkInput(self):
        """
        Determines if the users input is valid.  If no validation function is provided,
        then this will return true
        """
        try:
            validation = self._validate_user_input()
        except AttributeError:
            validation = True
        return validation

    def getInput(self):
        """
        Evaluates the users input, this is important
        when using numbers
        """
        return self.text()

    """ SIGNALS / EVENTS """
    def userFinishedEditing(self):
        """
        When the user has finished editing.  This will do a check to see
        if the input is valid, and then if it is, do something with that value
        if it isn't then it will return it to the previous value.
        """
        is_valid = self.checkInput()

        if is_valid:
            self.setText(self.getInput())
            try:
                self.userFinishedEditingEvent(self, self.getInput())
            except AttributeError:
                pass

        else:
            self.setText(self.getOrigValue())

    def userContinuousEditing(self):
        """
        This will run when the value is changed.  This is to do Continuous manipulations
        """
        is_valid = self.checkInput()
        if self._updating is True:
            if is_valid:
                try:
                    self.setText(self.getInput())
                    self.liveInputEvent(self, self.getInput())
                except AttributeError:
                    pass

            else:
                self.setText(self.getOrigValue())

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

    """ PROPERTIES """
    def appendKey(self, key):
        self.getKeyList().append(key)

    def removeKey(self, key):
        self.getKeyList().remove(key)

    def getKeyList(self):
        return self._key_list

    def setKeyList(self, _key_list):
        self._key_list = _key_list

    def setOrigValue(self, _orig_value):
        self._orig_value = _orig_value

    def getOrigValue(self):
        return self._orig_value


class AbstractInputLineEdit(QLineEdit, iAbstractInputWidget):
    def __init__(self, parent=None):
        super(AbstractInputLineEdit, self).__init__(parent)
        # set up signals
        self.editingFinished.connect(self.userFinishedEditing)
        self.textChanged.connect(self.userContinuousEditing)

    def focusInEvent(self, *args, **kwargs):
        """
        Sets the initial value on re-enter event.  This is mainly valid for
        ladder widgets?
        """
        self.setOrigValue(self.text())
        #self.setProperty("is_focused", True)
        return QLineEdit.focusInEvent(self, *args, **kwargs)

    def mousePressEvent(self, event, *args, **kwargs):
        """
        Blocks the middle mouse button from pasting in Linux
        """
        if event.button() == Qt.MiddleButton:
            return
        return QLineEdit.mousePressEvent(self, event, *args, **kwargs)


class AbstractInputPlainText(QPlainTextEdit, iAbstractInputWidget):
    TYPE = "text"
    def __init__(self, parent=None):
        super(AbstractInputPlainText, self).__init__()
        self.setMinimumSize(10, 10)

    def text(self):
        return self.toPlainText()

    def setText(self, text):
        self.setPlainText(text)

    def focusInEvent(self, event):
        self.setOrigValue(self.text())
        return QPlainTextEdit.focusInEvent(self, event)

    def focusOutEvent(self, event):
        # set up signals
        self.userFinishedEditing()
        return QPlainTextEdit.focusOutEvent(self, event)


class AbstractNumberInputWidget(AbstractInputLineEdit):
    """
    Base class for number based widgets.  The float
    and int input widgets will both inherit from this.

    Attributes:
        allow_negative (bool): determines if this will accept
            This is not currently set up
        do_math (bool): determines if this widget will support
            mathematical functions.  This is run by a simple eval(user_input).
    """
    def __init__(
        self, parent=None, allow_negative=True, do_math=True
    ):
        super(AbstractNumberInputWidget, self).__init__(parent)

        self.setKeyList(NUMERICAL_INPUT_KEYS)
        self.setDoMath(do_math)
        self.setRange(False)
        self.setAllowNegative(True)

    """ LADDER """
    def setValue(self, value):
        """
        This is only used for the ladder if it is setup
        """
        self.setText(str(value))

    def setUseLadder(
            self,
            _use_ladder_delegate,
            user_input=QEvent.MouseButtonRelease,
            value_list=[0.01, 0.1, 1, 10],
            alignment=Qt.AlignLeft
    ):
        """

        Args:
            _use_ladder_delegate (bool): enables/disables ladder
            user_input (QEvent.MouseButton): input event to display the ladder
            value_list (list): of values to adjust with
            alignment:

        Returns:

        """
        # create ladder
        if _use_ladder_delegate is True:
            self.ladder = installLadderDelegate(
                self,
                user_input=user_input,
                value_list=value_list
            )
            self.ladder.setRange(self.range_enabled, self.range_min, self.range_max)
            self.ladder.setAllowNegative(self.getAllowNegative())

        self._use_ladder_delegate = _use_ladder_delegate

    def getUseLadder(self):
        return self._use_ladder_delegate

    """ PROPERTIES """
    def setAllowNegative(self, enabled):
        self._allow_negative = enabled

        if hasattr(self, 'ladder'):
            self.ladder.setAllowNegative(enabled)

    def getAllowNegative(self):
        return self._allow_negative

    def setDoMath(self, _do_math):
        self._do_math = _do_math

        # add key to key list
        if _do_math is True:
            for key in MATH_KEYS:
                self.appendKey(key)
        else:
            for key in MATH_KEYS:
                self.removeKey(key)

    def getDoMath(self):
        return self._do_math

    def setRange(self, enabled, range_min=0, range_max=1):
        """
        Determines if this widget has a specified range.  Going over this
        range will clip values into that range
        """
        # setup default attrs
        self.range_enabled = enabled
        self.range_min = range_min
        self.range_max = range_max

        # set up ladder
        if hasattr(self, 'ladder'):
            self.ladder.setRange(enabled, range_min, range_max)

    def validateEvaluation(self):
        # evaluate if math
        if self.getDoMath() is True:
            try:
                eval(self.text())
                return True
            except:
                return False

    """ EVENTS """
    def keyPressEvent(self, event, *args, **kwargs):
        modifiers = event.modifiers()
        # add control modifiers back
        if modifiers:
            # user control operations (copy/paste/etc)
            if modifiers == Qt.ControlModifier:
                return QLineEdit.keyPressEvent(self, event, *args, **kwargs)
            # doing math operations
            if modifiers == Qt.ShiftModifier:
                if event.key() in self.getKeyList():
                    return QLineEdit.keyPressEvent(self, event, *args, **kwargs)

            # allow number pad shenanigans
            if modifiers == Qt.KeypadModifier:
                if event.key() in self.getKeyList():
                    return QLineEdit.keyPressEvent(self, event, *args, **kwargs)

        # default action
        else:
            if event.key() in self.getKeyList():
                return QLineEdit.keyPressEvent(self, event, *args, **kwargs)

    def focusOutEvent(self, event):
        return_val = QLineEdit.focusOutEvent(self, event)
        self.setCursorPosition(0)
        return return_val


class AbstractFloatInputWidget(AbstractNumberInputWidget):
    TYPE = 'float'
    def __init__(
        self, parent=None, allow_negative=True, do_math=True
    ):
        super(AbstractFloatInputWidget, self).__init__(
            parent, allow_negative, do_math
        )
        self.appendKey(Qt.Key_Period)
        self.setValidateInputFunction(self.validateInput)

    def validateInput(self):
        """
        Check to see if the users input is valid or not
        """
        if not self.validateEvaluation(): return

        # check if float
        user_input = self.getInput()
        try:
            float(user_input)
            return True
        except ValueError:
            return False

    def getInput(self):
        """
        Evaluates the users input, this is important
        when using numbers
        """
        value = eval(self.text())
        value = checkNegative(self.getAllowNegative(), value)
        value = checkIfValueInRange(self.range_enabled, value, self.range_min, self.range_max)
        return str(value)


class AbstractIntInputWidget(AbstractNumberInputWidget):
    TYPE = 'int'
    def __init__(
        self, parent=None, allow_negative=True, do_math=True
    ):
        super(AbstractIntInputWidget, self).__init__(
            parent, allow_negative, do_math
        )
        self.setValidateInputFunction(self.validateInput)

    def validateInput(self):
        """
        Check to see if the users input is valid or not
        """
        if not self.validateEvaluation(): return

        # check if int
        user_input = self.getInput()

        try:
            int(float(user_input))
            return True
        except ValueError:
            return False

    def getInput(self):
        """
        Evaluates the users input, this is important
        when using numbers
        """
        value = eval(self.text())
        value = checkNegative(self.getAllowNegative(), value)
        value = checkIfValueInRange(self.range_enabled, value, self.range_min, self.range_max)
        return str(int(value))


class AbstractStringInputWidget(AbstractInputLineEdit):
    TYPE = 'string'
    def __init__(self, parent=None):
        super(AbstractStringInputWidget, self).__init__(parent)
        self.setValidateInputFunction(self.validateInput)

    def validateInput(self):
        return True


class AbstractLabelWidget(QLabel, iAbstractInputWidget):
    """
    Display label
    """
    TYPE = 'label'

    def __init__(self, parent=None, text=None):
        super(AbstractLabelWidget, self).__init__(parent)

        if text:
            self.setText(text)

        # setup style

        # remove hover display (overwritten by image)
        style_sheet = removeHoverDisplay(self.styleSheet(), "INPUT WIDGETS")
        self.setStyleSheet(style_sheet)

        # set text alignment
        self.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)

    def setImage(self, image_path):
        """
        sets a background image
        Args:
            image_path (str): path to image on disk

        Returns:

        """
        self.removeImage()

        style_sheet = """
/* << BACKGROUND IMAGE START >> */
border-radius: 10px;
background-color: rgba{rgba_background};
color: rgba{rgba_text};
border-image: url({image_path}) 0 0 0 0 stretch stretch;
/* << BACKGROUND IMAGE END >> */""".format(
            image_path=image_path,
            rgba_background=iColor["rgba_background_00"],
            rgba_text=iColor["rgba_text"])

        style_sheet += self.styleSheet()

        self.setStyleSheet(style_sheet)

    def removeImage(self):
        style_sheet = self.styleSheet()

        # todo update image
        style_sheet = re.sub(
            "(/\* << BACKGROUND IMAGE START >> \*/)([^\$]+)(/\* << BACKGROUND IMAGE END >> \*/)",
            "",
            style_sheet)

        self.setStyleSheet(style_sheet)


class AbstractBooleanInputWidget(QLabel, iAbstractInputWidget):
    TYPE = 'bool'
    def __init__(self, parent=None, text=None, is_selected=False):
        super(AbstractBooleanInputWidget, self).__init__(parent)
        self.is_selected = is_selected
        self.setProperty("input_hover", True)
        if text:
            self.setText(text)
        self.updateStyleSheet()

        self.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)

    """ EVENTS """
    def mouseReleaseEvent(self, event):
        self.is_selected = not self.is_selected

        # run user triggered event
        try:
            self.userFinishedEditingEvent(self, self.is_selected)
        except AttributeError:
            pass

        return QLabel.mouseReleaseEvent(self, event)

    """ PROPERTIES """
    @property
    def is_selected(self):
        return self._is_selected

    @is_selected.setter
    def is_selected(self, is_selected):
        self._is_selected = is_selected
        self.setProperty('is_selected', is_selected)
        updateStyleSheet(self)


class AbstractOverlayInputWidget(QStackedWidget, iAbstractInputWidget):
    """
    Input widget with a display delegate overlaid.  This delegate will disappear
    when the user first hover enters.

    Args:
        display_mode (AbstractOverlayInputWidget.DISPLAYMODE): Trigger that will
            determine if/when the editor is displayed to the user.
        delegate_widget (QWidget): Widget for user to input values into
        image (str): path on disk to image
        title (string): Text to display when the widget is shown
            for the first time.

    Attributes:
        delegate_widget (QWidget): Editor widget that will be displayed when the user
            triggers it with the DisplayMode
        view_widget (AbstractLabelInputWidget): Label to be displayed when the user
            is not hovered over the widget

    Virtual Events:
        hide_delegate_event (Virtual Event): runs when the editor is being closed
        show_delegate_event (Virtual Event): runs when the editor is being opened
    """
    # Display Modes
    DISABLED = 1
    ENTER = 2
    RELEASE = 4
    def __init__(
            self,
            parent=None,
            editor_widget=None,
            image=None,
            title="",
            display_mode=4
    ):
        super(AbstractOverlayInputWidget, self).__init__(parent)

        # create widgets
        class ViewWidget(AbstractLabelWidget):
            def __init__(self, parent=None, title=""):
                super(ViewWidget, self).__init__(parent, title)

            """ EVENTS """

            def mouseReleaseEvent(self, event):
                # enable editor
                if self.parent().displayMode() == AbstractOverlayInputWidget.RELEASE:
                    if self.parent().currentIndex() == 0:
                        self.parent().showDelegate()
                        self.parent().editorWidget().setFocus()

                return AbstractLabelWidget.mouseReleaseEvent(self, event)

            def enterEvent(self, event):
                # enable editor
                if self.parent().displayMode() == AbstractOverlayInputWidget.ENTER:
                    self.parent().showDelegate()
                    AbstractLabelWidget.enterEvent(self, event)
                    self.parent().editorWidget().setFocus()
                return AbstractLabelWidget.enterEvent(self, event)

        view_widget = ViewWidget(self, title)
        self.setViewWidget(view_widget)

        if not editor_widget:
            editor_widget = AbstractStringInputWidget(self)
        self.setEditorWidget(editor_widget)

        # setup style
        self.setDisplayMode(display_mode)

        if image:
            self.setImage(image)

        # style_sheet = removeHoverDisplay(self.styleSheet(), "INPUT WIDGETS")
        # self.setStyleSheet(style_sheet)
        # self.viewWidget().updateStyleSheet()

    """ WIDGETS """
    def editorWidget(self):

        return self._editor_widget

    def setEditorWidget(self, widget):
        # remove old input widget
        if hasattr(self, "_editor_widget"):
            self._editor_widget.setParent(None)

        # add new input widget
        self.addWidget(widget)

        # setup attr
        self._editor_widget = widget

        style_sheet = removeHoverDisplay(widget.styleSheet(), "INPUT WIDGETS")
        widget.setStyleSheet(style_sheet)

    def viewWidget(self):
        return self._view_widget

    def setViewWidget(self, view_widget):
        if hasattr(self, "_view_widget"):
            self._view_widget.setParent(None)
        self._view_widget = view_widget
        self.insertWidget(0, self._view_widget)
        # self._view_widget.installEventFilter(self)

    """ DELEGATE DISPLAY """
    def displayMode(self):
        return self._display_mode

    def setDisplayMode(self, display_mode):
        """
        Sets when the editor will be displayed to the user

        Args:
            display_mode (AbstractOverlayInputWidget.DISPLAYMODE): Trigger that will
                determine if/when the editor is displayed to the user.
        """
        self._display_mode = display_mode

        if display_mode == AbstractOverlayInputWidget.DISABLED:
            style_sheet = removeHoverDisplay(self.styleSheet(), "INPUT WIDGETS")
            self.setStyleSheet(style_sheet)

        else:
            self.updateStyleSheet()

    def showDelegate(self):
        self.setCurrentIndex(1)
        self.releaseMouse()

        # run user event
        self.showDelegateEvent()

    def hideDelegate(self):
        self.setCurrentIndex(0)

        # run user event
        self.hideDelegateEvent()

    """ VIRTUAL FUNCTIONS """
    def title(self):
        return self.viewWidget().text()

    def setTitle(self, title):
        self.viewWidget().setText(title)

    def setImage(self, image_path):
        self.viewWidget().setImage(image_path)

    def removeImage(self):
        self.viewWidget().removeImage()

    """ VIRTUAL EVENTS """
    def _show_delegate_event(self):
        pass

    def setShowDelegateEvent(self, event):
        self._show_delegate_event = event

    def showDelegateEvent(self):
        self._show_delegate_event()

    def _hide_delegate_event(self):
        pass

    def setHideDelegateEvent(self, event):
        self._hide_delegate_event = event

    def hideDelegateEvent(self):
        self._hide_delegate_event()

    """ EVENTS """
    def leaveEvent(self, event):
        if self.currentIndex() == 1:
            self.hideDelegate()

        return QStackedWidget.leaveEvent(self, event)


class AbstractButtonInputWidget(AbstractBooleanInputWidget):
    """
    Toggleable button designed to work with the AbstractButtonInputWidgetContainer.

    Args:
        title (str): display name
        flag (arbitrary): flag to be returned to denote that this button is selected
        user_clicked_event (function): to run when the user clicks
        image:

    Attributes:
        flag (object): if toggleable, this will be the flag that is set.
        is_toggleable (bool): determines if this widget can be toggle on/off

    """
    def __init__(self, parent, user_clicked_event=None, title="CLICK ME", flag=None, is_toggleable=False):
        super(AbstractButtonInputWidget, self).__init__(parent)

        # setup style
        # self.rgba_background = iColor["rgba_invisible"]
        self.updateStyleSheet()

        # setup defaults
        self.setIsToggleable(is_toggleable)
        self.setText(title)
        self.setFlag(flag)
        if user_clicked_event:
            self.setUserClickedEvent(user_clicked_event)

    def isToggleable(self):
        return self._is_toggleable

    def setIsToggleable(self, enabled):
        self._is_toggleable = enabled

        # update selected property
        if enabled:
            self.setProperty("is_selected", False)
        else:
            self.setProperty("is_selected", None)

    def flag(self):
        return self._flag

    def setFlag(self, flag):
        self._flag = flag

    """ VIRTUAL FUNCTIONS """
    def setUserClickedEvent(self, function):
        self._user_clicked_event = function

    def userClickedEvent(self):
        if hasattr(self, "_user_clicked_event"):
            self._user_clicked_event(self)

    """ EVENTS """
    def mouseReleaseEvent(self, event):
        """ TODO this can probably be updated to use the AbstractBooleanInputWidget default
            mouse release event
        """
        # update selection
        if hasattr(self.parent(), "updateButtonSelection"):
            self.parent().updateButtonSelection(self)
            self.parent().normalizeWidgetSizes()

        # update style
        #self.setProperty("input_hover", False)
        updateStyleSheet(self)

        # user events
        self.userClickedEvent()

        # run user triggered event
        try:
            self.userFinishedEditingEvent(self, self.is_selected)
        except AttributeError:
            pass

        #print(self.parent().flags())
        #return AbstractBooleanInputWidget.mouseReleaseEvent(self, event)
    #
    # def leaveEvent(self, event):
    #     self.setProperty("input_hover", True)


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication, QWidget, QVBoxLayout
    from qtpy.QtGui import QCursor

    import sys, inspect

    app = QApplication(sys.argv)


    class CustomDynamicWidgetExample(AbstractOverlayInputWidget):
        """
        Custom dynamic widget example.  This is a base example of the OverlayInputWidget
        as well.
        """

        def __init__(self, parent=None):
            super(CustomDynamicWidgetExample, self).__init__(parent, title="Hello")

    # Construct
    editor_widget = AbstractBooleanInputWidget(text="yolo")
    overlay_widget = AbstractOverlayInputWidget(
        title="title",
        display_mode=AbstractOverlayInputWidget.RELEASE,
        editor_widget=editor_widget,
        image="/home/brian/Pictures/test.png")

    # main_widget = CustomDynamicWidgetExample()
    #overlay_widget.setDisplayMode(AbstractOverlayInputWidget.DISABLED)
    #overlay_widget.setDisplayMode(AbstractOverlayInputWidget.ENTER)
    main_widget = QWidget()
    main_layout = QVBoxLayout(main_widget)
    main_layout.addWidget(overlay_widget)
    main_layout.addWidget(QLabel("klajdflasjkjfklasfjsl"))

    main_widget.move(QCursor.pos())
    main_widget.show()
    main_widget.resize(500, 500)
    main_widget.show()
    #print ('\n\n========================\n\n')
    #print(main_widget.styleSheet())
    #w.move(QCursor.pos())
    sys.exit(app.exec_())
    #
    # def print_classes():
    #     for name, obj in inspect.getmembers(sys.modules[__name__]):
    #         if inspect.isclass(obj):
    #             print(obj)
    #
    # print(__name__)
    # print_classes()

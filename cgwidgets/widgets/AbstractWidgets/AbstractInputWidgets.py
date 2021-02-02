"""
Input Group
    AbstractInputGroupBox (QGroupBox)
        | -- TabTansuWidget
                | -* InputWidget

Input Widgets
    iAbstractInputWidget (QLineEdit)
        | -- AbstractStringInputWidget
        | -- AbstractNumberInputWidget
                | -- AbstractFloatInputWidget
                | -- AbstractIntInputWidget
    BooleanInputWidget (QLabel)
"""

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
from cgwidgets.views import TansuView, TansuViewHandle
from cgwidgets.settings.icons import icons


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
        self.rgba_background = iColor["rgba_gray_2"]
        self.rgba_text = iColor["rgba_text"]
        self.rgba_selected_hover = iColor["rgba_selected_hover"]

        # setup properties
        self.setProperty("hover_display", True)

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
            #"rgba_gray": iColor["rgba_gray_3"],
            "rgba_invisble": iColor["rgba_invisible"],
            "rgba_selected_background": iColor["rgba_selected_background"],
            "gradient_background": icons["gradient_background"],
            "type": type(self).__name__
        })
        style_sheet = """
        /* DEFAULT */
        {type}{{
            border: 1px dotted rgba{rgba_gray_4};
            border-radius: 10px;
            background-color: rgba{rgba_background};
            color: rgba{rgba_text};
            selection-background-color: rgba{rgba_selected_background};
        }}

        /* SELECTION */
        {type}[is_selected=true]{{
            background: qradialgradient(
                radius: 0.9,
                cx:0.50, cy:0.50,
                fx:0.5, fy:0.5,
                stop:0.5 rgba{rgba_background},
                stop:0.75 rgba{rgba_accept});
            }}
        {type}[is_selected=false]{{
            background: qradialgradient(
                radius: 0.9,
                cx:0.50, cy:0.50,
                fx:0.5, fy:0.5,
                stop:0.5 rgba{rgba_background},
                stop:0.75 rgba{rgba_cancel});
            }}
        {type}:focus{{
            background: qradialgradient(
                radius: 0.9,
                cx:0.50, cy:0.50,
                fx:0.5, fy:0.5,
                stop:0.5 rgba{rgba_background},
                stop:0.75 rgba{rgba_selected_background});
            }}
        {type}::hover[hover_display=true]{{
            background: qradialgradient(
                radius: 0.9,
                cx:0.50, cy:0.50,
                fx:0.5, fy:0.5,
                stop:0.5 rgba{rgba_background},
                stop:0.75 rgba{rgba_selected_hover});
            }}
        {type}::hover:focus{{
            background: qradialgradient(
                radius: 0.9,
                cx:0.50, cy:0.50,
                fx:0.5, fy:0.5,
                stop:0.5 rgba{rgba_background},
                stop:0.75 rgba{rgba_selected_background});
            }}

        """.format(**style_sheet_args)

        self.setStyleSheet(style_sheet)

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
            #TODO This doesn't exist in this ffunctino... moved to iTansuGroupInput
            # or somewhere more logical...
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
                #TODO This doesn't exist in this ffunctino... moved to iTansuGroupInput
                # or somewhere more logical...
                try:
                        self.setText(self.getInput())
                        self.liveInputEvent(self, self.getInput())
                        #self.setCursorPosition(0)
                except AttributeError:
                    pass

            else:
                self.setText(self.getOrigValue())

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
    #
    # def focusOutEvent(self, event):
    #     self.setProperty("is_focused", False)
    #     return QLineEdit.focusOutEvent(self, event)

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
        # create ladder
        if _use_ladder_delegate is True:
            self.ladder = installLadderDelegate(
                self,
                user_input=user_input,
                value_list=value_list
            )
            self.ladder.setRange(self.range_enabled, self.range_min, self.range_max)
            self.ladder.setAllowNegative(self.getAllowNegative())

        #     # set up ladder discrete drag
        #     self.ladder.setDiscreteDrag(True, alignment=Qt.AlignLeft, depth=10)
        #     self.ladder.setDiscreteDrag(
        #         True,
        #         alignment=alignment,
        #         depth=10,
        #         display_widget=self.parent()
        #         )
        #     # set up outline on ladder
        #     base_group = getWidgetAncestor(self, AbstractInputGroupBox)
        #     if base_group:
        #         outline_color = base_group.rgba_border
        #     else:
        #         outline_color = iColor["rgba_outline"]
        #     self.ladder.setStyleSheet("""
        #     AbstractNumberInputWidget{{border: 1px solid rgba{outline_color}}}
        #     """.format(
        #         outline_color=repr(outline_color))
        #     )
        # else:
        #     if hasattr(self, 'ladder'):
        #         self.ladder.setParent(None)
        # pass
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


class AbstractLabelInputWidget(AbstractStringInputWidget):
    """
    Essentially a QLabel with a QLineEdit delegate on it.

    This line edit will automatically toggle the display state from read only
    to editable depending on the focus.  It will be seen as a QLabel,
    but has the handler that when clicked on is editable

    Attributes:
        isEditable (boolean): determines if this display can be edited or not
            by clicking on it.
    Virtual:
        userFinishedEditingEvent (widget, value): when the user finishes editing.
            This is a copy/paste from the iTansuGroupInput to set up the registry
            for user input.
    """
    def __init__(self, parent=None):
        super(AbstractLabelInputWidget, self).__init__(parent)
        self.editingFinished.connect(self.disableDelegate)

        # set up editable
        self.__setReadOnly(True)
        self.setEditable(False)

        self.setupStyleSheet()

    def setupStyleSheet(self):
        style_sheet_args = iColor.style_sheet_args
        style_sheet = """
        /* MAIN */
        AbstractLabelInputWidget{{
            border: 1px solid rgba{rgba_gray_2};
            background-color: rgba{rgba_gray_2};
            color: rgba{rgba_text};
            selection-background-color: rgba{rgba_selected};
        }}
        /* Border if widget can be editted */
        AbstractLabelInputWidget[editable=true]{{
            border: 1px solid rgba{rgba_gray_3};
        }}
        /* Border during edit operation */
        AbstractLabelInputWidget[readonly=false]{{
            border: 1px solid rgba{rgba_selected};
        }}
        """.format(**style_sheet_args)
        self.setStyleSheet(style_sheet)

    """ API """
    def isEditable(self):
        return self._is_editable

    def setEditable(self, enabled):
        self._is_editable = enabled
        self.setProperty('editable', enabled)

    # TODO duplicate code
    """ VIRTUAL (copy / paste from iTansuGroupInput"""
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

    def disableDelegate(self):
        if self.isEditable():
            self.__setReadOnly(True)

    def __setReadOnly(self, enabled):
        """
        Overloading the setReadOnly with a wrapper

        Args:
            enabled (bool): determines if this widget is current set to read only
                mode or edit mode.
        """
        self.setProperty('readonly', enabled)
        self.setReadOnly(enabled)
        updateStyleSheet(self)
        pass

    """ EVENTS """
    def focusOutEvent(self, event):
        if self.isEditable():
            self.__setReadOnly(True)
        return AbstractStringInputWidget.focusOutEvent(self, event)

    def mousePressEvent(self, event):
        if self.isEditable():
            self.__setReadOnly(False)
        return AbstractStringInputWidget.mousePressEvent(self, event)


class AbstractBooleanInputWidget(QLabel, iAbstractInputWidget):
    TYPE = 'bool'
    def __init__(self, parent=None, text=None, is_selected=False):
        super(AbstractBooleanInputWidget, self).__init__(parent)
        self.is_selected = is_selected
        self.setProperty("hover_display", True)
        if text:
            self.setText(text)
        self.updateStyleSheet()

        self.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)

    # def setupStyleSheet(self):
    #     style_sheet_args = iColor.style_sheet_args
    #     style_sheet_args['name'] = type(self).__name__
    #     style_sheet = """
    #     QLabel{{background-color: rgba{rgba_gray_2}}}
    #     QLabel[is_selected=true]{{
    #         border: 3px solid rgba{rgba_accept}
    #     }}
    #     QLabel[is_selected=false]{{
    #         border: 3px solid rgba{rgba_cancel};
    #     }};
    #     """.format(
    #         **style_sheet_args
    #     )
    #     self.setStyleSheet(style_sheet)

    """ EVENTS """
    def enterEvent(self, event):
        self.setProperty("hover_display", True)
        updateStyleSheet(self)
        return QLabel.enterEvent(self, event)

    def mouseReleaseEvent(self, event):
        self.is_selected = not self.is_selected

        # run user triggered event
        try:
            self.userFinishedEditingEvent(self, self.is_selected)
        except AttributeError:
            pass

        self.setProperty("hover_display", False)
        updateStyleSheet(self)

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
        super(AbstractOverlayInputWidget, self).__init__(parent)

        # create widgets
        self.overlay_widget = AbstractLabelInputWidget(title)
        if not input_widget:
            input_widget = AbstractStringInputWidget(self)
        self.input_widget = input_widget

        # add widgets
        self.addWidget(self.overlay_widget)
        self.addWidget(self.input_widget)

        # setup style
        #setAsTransparent(self.overlay_widget)
        self.overlay_widget.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)

    def enterEvent(self, event):
        self.setCurrentIndex(1)
        QStackedWidget.enterEvent(self, event)
        self.input_widget.setFocus()


class AbstractMultiButtonInputWidget(TansuView):
    """
    Provides a multi button input widget.

    Colors
    Hide Widget Handles?
    Args:
        buttons (list): of lists ["title": virtualFunction]
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
        self._rgba_flag = iColor["rgba_selected_hover"]
        super(AbstractMultiButtonInputWidget, self).__init__(parent, orientation)
        self.setIsSoloViewEnabled(False)
        self.setIsHandleStatic(True)
        self.setHandleWidth(0)
        self.setHandleLength(-1)

        #
        self._buttons = {}
        self._is_multi_select = True
        self._current_buttons = []

        #
        if buttons:
            for button in buttons:
                self.addButton(*button)

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

    """ BUTTONS """
    def updateButtonSelection(self, selected_button):
        if selected_button in self.currentButtons():
            self.setButtonAsCurrent(selected_button, False)
        else:
            self.setButtonAsCurrent(selected_button, True)

        # update display
        for button in self._buttons.values():
            if button not in self.currentButtons():
                button.setProperty("is_selected", False)
                updateStyleSheet(button)
        self.setAllWidgetsToUniformSize()

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
        if self.isMultiSelect():
            if enabled:
                self._current_buttons.append(current_button)
                self.insertWidget(len(self.currentButtons()) - 1, current_button)
            else:
                self._current_buttons.remove(current_button)
                self.insertWidget(len(self.currentButtons()), current_button)
        else:
            self._current_buttons = [current_button]
            self.insertWidget(0, current_button)

        # setup button style
        current_button.is_selected = True

        self.update()

    def addButton(self, title, flag, user_clicked_event, image=None):
        """
        Adds a button to this widget

        Args:
            title (str): display name
            flag (arbitrary): flag to be returned to denote that this button is selected
            user_clicked_event (function): to run when the user clicks
            image:

        Note:
            image is not currently setup.  This kwarg is merely a place holder.
        Todo: setup image
        """
        button = AbstractButtonInputWidget(self, user_clicked_event=user_clicked_event, title=title, flag=flag)
        self._buttons[title] = button
        self.addWidget(button)


class AbstractButtonInputWidget(AbstractBooleanInputWidget):
    """
    Toggleable button designed to work with the AbstractMultiButtonInputWidget.

    Args:
        title (str): display name
        flag (arbitrary): flag to be returned to denote that this button is selected
        user_clicked_event (function): to run when the user clicks
        image:
    """
    def __init__(self, parent, user_clicked_event=None, title="CLICK ME", flag=None):
        super(AbstractButtonInputWidget, self).__init__(parent)

        # setup style
        # self.rgba_background = iColor["rgba_invisible"]
        self.updateStyleSheet()

        # setup defaults
        self.setText(title)
        self.setFlag(flag)
        if user_clicked_event:
            self.setUserClickedEvent(user_clicked_event)

    def flag(self):
        return self._flag

    def setFlag(self, flag):
        self._flag = flag

    """ VIRTUAL FUNCTIONS """
    def setUserClickedEvent(self, function):
        self._user_clicked_event = function

    def userClickedEvent(self):
        self._user_clicked_event(self)

    def mouseReleaseEvent(self, event):
        """ TODO this can probably be updated to use the AbstractBooleanInputWidget default
            mouse release event
        """
        # update selection
        self.parent().updateButtonSelection(self)
        self.userClickedEvent()
        self.parent().setAllWidgetsToUniformSize()

        # update style
        self.setProperty("hover_display", False)
        updateStyleSheet(self)

        # run user triggered event
        try:
            self.userFinishedEditingEvent(self, self.is_selected)
        except AttributeError:
            pass

        print(self.parent().flags())
        #return AbstractBooleanInputWidget.mouseReleaseEvent(self, event)


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication, QWidget, QVBoxLayout
    from qtpy.QtGui import QCursor

    import sys, inspect

    app = QApplication(sys.argv)
    def userEvent(widget):
        print("user input...", widget)

    buttons = []
    for x in range(3):
        flag = x
        buttons.append(["button_"+str(x), flag, userEvent])

    widget = AbstractMultiButtonInputWidget(buttons=buttons, orientation=Qt.Horizontal)
    # widget.setIsHandleVisible(False)
    # updateStyleSheet(widget)

    widget.move(QCursor.pos())
    widget.show()
    widget.resize(256, 256)
    widget.resize(500, 500)
    widget.show()
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

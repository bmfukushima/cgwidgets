"""
TODO:
    Group Box
        *   Dynamic text size
                QApplication.font()
        *   Rounded vs straight corners?
        *   Expose orientation?
                That's a lot of work...

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

from cgwidgets.utils import (
    updateStyleSheet, clearLayout, installLadderDelegate, getWidgetAncestor,
    getFontSize, checkIfValueInRange, checkNegative, setAsTransparent
)
from cgwidgets.settings.colors import iColor
from cgwidgets.settings.keylist import NUMERICAL_INPUT_KEYS, MATH_KEYS
from cgwidgets.widgets.AbstractWidgets import AbstractInputGroupBox, AbstractInputGroup


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
        self.rgba_background = iColor["rgba_gray_0"]
        self.rgba_text = iColor["rgba_text"]

        self.updateStyleSheet()

        font_size = getFontSize(QApplication)
        self.setMinimumSize(font_size*2, font_size*2)

    def updateStyleSheet(self):
        style_sheet_args = iColor.style_sheet_args
        style_sheet_args.update({
            "rgba_gray_0": repr(self.rgba_background),
            "rgba_border": repr(self.rgba_border),
            "rgba_text": repr(self.rgba_text)
        })
        style_sheet = """
            border: None;
            background-color: rgba{rgba_gray_0};
            color: rgba{rgba_text}
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

    @property
    def rgba_border(self):
        return self._rgba_border

    @rgba_border.setter
    def rgba_border(self, _rgba_border):
        self._rgba_border = _rgba_border

    @property
    def rgba_background(self):
        return self._rgba_background

    @rgba_background.setter
    def rgba_background(self, _rgba_background):
        self._rgba_background = _rgba_background
        #self.updateStyleSheet()

    @property
    def rgba_text(self):
        return self._rgba_text

    @rgba_text.setter
    def rgba_text(self, _rgba_text):
        self._rgba_text = _rgba_text
        #self.updateStyleSheet()


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
            border: 1px solid rgba{rgba_gray_1};
            background-color: rgba{rgba_gray_1};
            color: rgba{rgba_text};
            selection-background-color: rgba{rgba_selected};
        }}
        /* Border if widget can be editted */
        AbstractLabelInputWidget[editable=true]{{
            border: 1px solid rgba{rgba_gray_2};
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


class AbstractBooleanInputWidget(QLabel):
    TYPE = 'bool'
    def __init__(self, parent=None, is_clicked=False):
        super(AbstractBooleanInputWidget, self).__init__(parent)
        self.is_clicked = is_clicked

    def setupStyleSheet(self):
        style_sheet_args = iColor.style_sheet_args
        style_sheet_args['name'] = type(self).__name__
        style_sheet = """
        QLabel{{background-color: rgba{rgba_gray_0}}}
        QLabel[is_clicked=true]{{
            border: 3px solid rgba{rgba_accept}
        }}
        QLabel[is_clicked=false]{{
            border: 3px solid rgba{rgba_cancel};
        }};
        """.format(
            **style_sheet_args
        )
        self.setStyleSheet(style_sheet)

    """ EVENTS """
    def mouseReleaseEvent(self, event):
        self.is_clicked = not self.is_clicked

        # run user triggered event
        try:
            self.userFinishedEditingEvent(self, self.is_clicked)
        except AttributeError:
            pass
        return QLabel.mouseReleaseEvent(self, event)

    """ PROPERTIES """
    @property
    def is_clicked(self):
        return self._is_clicked

    @is_clicked.setter
    def is_clicked(self, is_clicked):
        self._is_clicked = is_clicked
        self.setProperty('is_clicked', is_clicked)
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
        self.overlay_widget = QLabel(title)
        if not input_widget:
            input_widget = AbstractStringInputWidget(self)
        self.input_widget = input_widget

        # add widgets
        self.addWidget(self.overlay_widget)
        self.addWidget(self.input_widget)

        # setup style
        setAsTransparent(self.overlay_widget)
        self.overlay_widget.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)

    def enterEvent(self, event):
        self.setCurrentIndex(1)
        QStackedWidget.enterEvent(self, event)
        self.input_widget.setFocus()


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication, QWidget, QVBoxLayout
    from qtpy.QtGui import QCursor

    import sys, inspect

    app = QApplication(sys.argv)
    input_widget = AbstractStringInputWidget()
    title = "yolo bolo"
    w = AbstractOverlayInputWidget(input_widget=input_widget, title=title)

    print(AbstractIntInputWidget.mro())
    w.resize(500, 500)
    w.show()
    #w.move(QCursor.pos())
    sys.exit(app.exec_())

    def print_classes():
        for name, obj in inspect.getmembers(sys.modules[__name__]):
            if inspect.isclass(obj):
                print(obj)

    print(__name__)
    print_classes()

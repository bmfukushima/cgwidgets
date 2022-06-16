"""
ToDo:
    StyleSheets
        AbstractLabelWidget
            Hierarchy is wrong.  Setting on itself wont set, need to set on parent?
            Add another level?
                QWidget --> QStackedWidget
            or set on stacked widget
        Hover Display:
            Append border to original, to support a default border
                or
            Don't even create the border... or set a flag to enable/disable default border?

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

from qtpy import API_NAME
from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import (
    QLineEdit, QLabel, QPlainTextEdit, QWidget, QStackedLayout, QFrame
)
from qtpy.QtCore import Qt, QEvent

from cgwidgets.settings import iColor
from cgwidgets.settings.keylist import NUMERICAL_INPUT_KEYS, MATH_KEYS, ACCEPT_KEYS
from cgwidgets.utils import (
    installLadderDelegate, checkIfValueInRange,
    checkNegative, updateStyleSheet
)

from cgwidgets.settings.hover_display import removeHoverDisplay, installHoverDisplaySS
from cgwidgets.widgets.AbstractWidgets.AbstractInputInterface import iAbstractInputWidget


class AbstractInputLineEdit(QLineEdit, iAbstractInputWidget):
    def __init__(self, parent=None):
        super(AbstractInputLineEdit, self).__init__(parent)
        # print(API_NAME, type(API_NAME))
        if API_NAME == "PySide2":
            iAbstractInputWidget.__init__(self) #pyside2 forces us to do this import

        # set up signals
        self.editingFinished.connect(self.userFinishedEditing)
        self.textChanged.connect(self.userContinuousEditing)

    def setText(self, text):
        self.setOrigValue(text)
        return QLineEdit.setText(self, text)

    def keyPressEvent(self, event):
        if event.key() in ACCEPT_KEYS:
            self.userFinishedEditing()
        if event.key() == 96:
            return self.parent().keyPressEvent(event)
        return QLineEdit.keyPressEvent(self, event)

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
        if API_NAME == "PySide2":
            iAbstractInputWidget.__init__(self) #pyside2 forces us to do this import
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
        self, parent=None, allow_negative=True, allow_zero=True, do_math=True
    ):
        super(AbstractNumberInputWidget, self).__init__(parent)
        self.setOrigValue("0")
        self.setText("0")
        self.setKeyList(NUMERICAL_INPUT_KEYS)
        self.setDoMath(do_math)
        self.range_min = None
        self.range_max = None
        self.setAllowNegative(allow_negative)
        self.setAllowZero(allow_zero)

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
            range_min=None,
            range_max=None
    ):
        """

        Args:
            _use_ladder_delegate (bool): enables/disables ladder
            user_input (QEvent.MouseButton): input event to display the ladder
            value_list (list): of values to adjust with
            range_min (float):
            range_max (float):

        Returns:
        """
        # create ladder
        if _use_ladder_delegate is True:
            range_min = self.range_min or range_min
            range_max = self.range_max or range_max
            self.ladder = installLadderDelegate(
                self,
                user_input=user_input,
                value_list=value_list,
                range_min=range_min,
                range_max=range_max,
                allow_negative_values=self.getAllowNegative(),
                allow_zero_value=self.getAllowZero()
            )

        self._use_ladder_delegate = _use_ladder_delegate

    def getUseLadder(self):
        return self._use_ladder_delegate

    """ UTILS """
    def getRangeMin(self):
        """ Gets the lower bound of any number input based off of the
        range_min, getAllowNegative, getAllowZero handlers"""
        range_min = self.range_min
        if range_min:
            if not self.getAllowNegative() and range_min < 0:
                range_min = 0
            if not self.getAllowZero() and range_min == 0:
                if self.TYPE == "int":
                    range_min = 1
                if self.TYPE == "float":
                    range_min = 0.001
        else:
            if not self.getAllowNegative():
                range_min = 0
            if not self.getAllowZero():
                if self.TYPE == "int":
                    range_min = 1
                if self.TYPE == "float":
                    range_min = 0.001

        return range_min

    """ PROPERTIES """
    def setAllowNegative(self, enabled):
        self._allow_negative = enabled

        if hasattr(self, 'ladder'):
            self.ladder.setAllowNegative(enabled)

    def getAllowNegative(self):
        return self._allow_negative

    def setAllowZero(self, enabled):
        self._allow_zero = enabled

        if hasattr(self, 'ladder'):
            self.ladder.setAllowZero(enabled)

    def getAllowZero(self):
        return self._allow_zero

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

    def setRange(self, range_min=None, range_max=None):
        """
        Determines if this widget has a specified range.  Going over this
        range will clip values into that range
        """
        # setup default attrs
        self.range_min = range_min
        self.range_max = range_max

        # set up ladder
        if hasattr(self, 'ladder'):
            self.ladder.setRange(range_min, range_max)

    def validateEvaluation(self):
        # evaluate if math
        if self.getDoMath() is True:
            try:
                text = self.text().strip("0")
                eval(text)
                return True
            except:
                return False

    def getInputHelper(self):
        """
        Helper function for the FLOAT/INT widgets to call to check
        to ensure the value entered is valid.  This will resolve for
        getAllowZero, getAllowNegative, getDoMath

        Returns (str):
        """
        text = self.text()

        try:
            value = eval(text)
            value = checkNegative(self.getAllowNegative(), value)
            range_min = self.getRangeMin()
            value = checkIfValueInRange(value, range_min, self.range_max)
        except SyntaxError:
            value = self.getOrigValue()

        return value

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
        self, parent=None, allow_negative=True, allow_zero=True, do_math=True
    ):
        super(AbstractFloatInputWidget, self).__init__(
            parent, allow_negative, allow_zero, do_math
        )
        self.appendKey(Qt.Key_Period)
        self.setValidateInputFunction(self.validateInput)

    def getInput(self):
        """
        Evaluates the users input, this is important
        when using numbers
        """
        # if value is 0
        value = self.getInputHelper()
        return str(float(value))

    def validateInput(self):
        """
        Check to see if the users input is valid or not
        """
        return True
        # if not self.validateEvaluation(): return
        #
        # # check if float
        # user_input = self.getInput()
        # try:
        #     float(user_input)
        #     return True
        # except ValueError:
        #     return False


class AbstractIntInputWidget(AbstractNumberInputWidget):
    TYPE = 'int'
    def __init__(
        self, parent=None, allow_negative=True, allow_zero=True, do_math=True
    ):
        super(AbstractIntInputWidget, self).__init__(
            parent, allow_negative, allow_zero, do_math
        )
        self.setValidateInputFunction(self.validateInput)

    def validateInput(self):
        """
        Check to see if the users input is valid or not
        """
        if not self.validateEvaluation(): return True

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
        # if value is not 0
        try:
            value = self.getInputHelper()
            return str(int(value))

        # is zero
        except ValueError:
            return str("0")


class AbstractStringInputWidget(AbstractInputLineEdit):
    TYPE = 'string'
    def __init__(self, parent=None):
        super(AbstractStringInputWidget, self).__init__(parent)
        self.setValidateInputFunction(self.validateInput)

    def validateInput(self):
        return True


class AbstractLabelWidget(QFrame, iAbstractInputWidget):
    """
    Display label

    Args:
        text (str): text to be displayed as the title
        image (str): path on disk to image

    Attributes:
        widget_resize_mode (Qt.AspectRatioMode): How the image should be resized


    Hierarchy:
        |-- QStackedLayout (StackAll)
            |- imageWidget --> QLabel
            |- textWidget --> QLabel

    Signals:
        resizeEvent --> timer --> resize image
            When the widget is resized, the current pixmap will be scaled up/down to fit
            the current pixmap.  When the user stops resizing, after a period of 500ms the
            image will fully resize based off of the original size.
    """
    TYPE = 'label'

    def __init__(self, parent=None, text=None, image=None):
        super(AbstractLabelWidget, self).__init__(parent=parent)
        if API_NAME == "PySide2":
            iAbstractInputWidget.__init__(self) #pyside2 forces us to do this import
        # setup layout
        QStackedLayout(self)
        self.layout().setStackingMode(QStackedLayout.StackAll)

        # initialize widgets
        self._image_widget = QLabel(self)
        self.pixmap = QPixmap()
        self._image_widget.setPixmap(self.pixmap)
        self._text_widget = QLabel(self)

        # setup default attrs
        self._image_path = None
        self._image_resize_mode = Qt.KeepAspectRatio

        if text:
            self.setText(text)

        if image:
            self.setImage(image)

        # setup style
        """remove hover display (overwritten by image)"""
        # self.setStyleSheet("AbstractLabelWidget{border: 5px solid rgba(255,0,0,255);}")
        # style_sheet = removeHoverDisplay(self.styleSheet(), "INPUT WIDGETS")
        # self.setStyleSheet(style_sheet)

        # self.updateTextColor()


        # set text alignment
        self.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
        # self.textWidget().setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
        self.imageWidget().setAlignment(Qt.AlignCenter)

        self.layout().addWidget(self.textWidget())
        self.layout().addWidget(self.imageWidget())

    """ UTILS """
    def setAlignment(self, alignment):
        """
        Sets the alignment of the text and image widgets
        Args:
            alignment (Qt.Alignment): how the widgets text/image should be aligned
                 ie. (Qt.AlignCenter | Qt.AlignHCenter)

        Returns:

        """
        self.textWidget().setAlignment(alignment)
        self.imageWidget().setAlignment(alignment)

    """ TEXT """
    def textWidget(self):
        return self._text_widget

    def text(self):
        return self.textWidget().text()

    def setText(self, text):
        """
        Sets the display text of the widget
        Args:
            text (str):  text to be displayed
        """
        self.textWidget().setText(text)

    def textColor(self):
        return self.rgba_text

    def setTextColor(self, color):
        """
        Sets the color of the displayed text

        Args:
            color (RGBA): Tuple of RGBA(255) values
        """
        self.rgba_text = color
        self.updateStyleSheet()

    def textBackgroundColor(self):

        return self.rgba_background

    def setTextBackgroundColor(self, color):
        """
        Sets the color of the displayed text_background

        Args:
            color (RGBA): Tuple of RGBA(255) values
        """
        self.rgba_background = color
        self.updateStyleSheet()

    def setWordWrap(self, enabled):
        self.textWidget().setWordWrap(enabled)

    """ IMAGE  """
    def imageWidget(self):
        return self._image_widget

    def setImage(self, image_path):
        """
        Sets a background image

        Args:
            image_path (str): path to image on disk

        Note: Todo: no idea if setting this to None will clear...
            probably not lol, I should prob fix this... w/e not like
            anyone is ever going to use this repo.
        """
        if image_path is None:
            self.setImagePath(None)
            return
        self.setImagePath(image_path)
        self.pixmap = QPixmap(image_path)
        self._image_widget.setPixmap(self.pixmap)
        self.resizeImage()
        self.updateStyleSheet()
        self._image_widget.setAlignment(Qt.AlignCenter)
        #self.updateTextColor()
        # self.removeImage()

    def imagePath(self):
        return self._image_path

    def setImagePath(self, image_path):
        self._image_path = image_path

    def isImageVisible(self):
        return self.imageWidget().isVisible()

    def showImage(self, enabled):
        """
        Determines whether or not the background image will be displayed to the user

        Args:
            enabled (bool):
        """
        if enabled:
            self.imageWidget().show()
        if not enabled:
            self.imageWidget().hide()

    def imageResizeMode(self):
        return self._image_resize_mode

    def setImageResizeMode(self, resize_mode):
        """
        Determines how the image should be resized.
        Args:
            resize_mode (Qt.RESIZE_MODE):  Qt.KeepAspectRatio | Qt.IgnoreAspectRatio
        """
        self._image_resize_mode = resize_mode

    def resizeImage(self):
        """ Main function for resizing the image."""
        # get height/width
        # todo figure out correct offset
        """ Currently using an arbitrary offset to accommodate border width for all DCC's """
        offset = 4
        width = self.frameGeometry().width() - offset
        height = self.frameGeometry().height() - offset
        # set sized
        self.imageWidget().setFixedSize(width, height)

        # resize pixmap
        if not self.pixmap.isNull():
            self.pixmap = self.pixmap.scaled(width, height, self.imageResizeMode())
            self.imageWidget().setPixmap(self.pixmap)
            self.imageWidget().setAlignment(Qt.AlignCenter)

    """ EVENTS """
    def time(self):
        """
        Util function for the timer event that is running while the user resizes.  This timer
        is being run so that after the user finishes resizing, more updates can happen.
        """
        self.setImage(self.imagePath())
        delattr(self, "_timer")
        self.resizeImage()

    def resizeEvent(self, event):
        """
        After the user has finished resizing, after 1 second, this will fire an update
        signal to have the display fully updated.
        """
        # preflight

        if not self._image_path: return QFrame.resizeEvent(self, event)
        if not self.isImageVisible(): return QFrame.resizeEvent(self, event)

        # Todo for some reason this causes a slow down when resizing in PySide2
        # only happens in Nuke/Houdini and not in the example
        self.resizeTimerEvent(100, self.time)

        return QFrame.resizeEvent(self, event)

    def showEvent(self, event):
        return_val = QFrame.showEvent(self, event)
        self.setImage(self.imagePath())
        self.resizeImage()
        return return_val


class AbstractBooleanInputWidget(AbstractLabelWidget):
    TYPE = 'bool'
    def __init__(self, parent=None, text=None, image=None, is_selected=False):
        super(AbstractBooleanInputWidget, self).__init__(parent, text=text, image=image)
        if API_NAME == "PySide2":
            iAbstractInputWidget.__init__(self) #pyside2 forces us to do this import

        # override label defaults

        self.is_selected = is_selected
        self.setProperty("input_hover", True)
        if text:
            self.setText(text)
        # self.updateStyleSheet()

        self.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)

    """ EVENTS """
    def mouseReleaseEvent(self, event):
        self.is_selected = not self.is_selected

        # run user triggered event
        try:
            self.userFinishedEditingEvent(self, self.is_selected)
        except AttributeError:
            pass

        return AbstractLabelWidget.mouseReleaseEvent(self, event)

    """ PROPERTIES """
    @property
    def is_selected(self):
        return self._is_selected

    @is_selected.setter
    def is_selected(self, is_selected):
        self._is_selected = is_selected
        self.setProperty('is_selected', is_selected)
        updateStyleSheet(self)

    def setIsSelected(self, is_selected):
        self._is_selected = is_selected
        self.setProperty('is_selected', is_selected)
        updateStyleSheet(self)


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
    TYPE = 'button'
    def __init__(self, parent=None, user_clicked_event=None, title="CLICK ME", flag=None, is_toggleable=False):
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
        # run user triggered event
        if self.isToggleable():
            self.is_selected = not self.is_selected

        # update selection
        if hasattr(self.parent(), "updateButtonSelection"):
            self.parent().updateButtonSelection(self)
            self.parent().normalizeWidgetSizes()

        # update style
        updateStyleSheet(self)

        # user events

        # user press event
        self.userClickedEvent()

        # editing event
        try:
            self.userFinishedEditingEvent(self, self.is_selected)
        except AttributeError:
            pass

        # return AbstractBooleanInputWidget.mouseReleaseEvent(self, event)


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication, QWidget, QVBoxLayout
    from qtpy.QtGui import QCursor
    from cgwidgets.settings import icons
    import sys, inspect

    app = QApplication(sys.argv)


    # Construct
    string_test = AbstractStringInputWidget()

    boolean_test = AbstractBooleanInputWidget(text="boolean", image=None, is_selected=False)
    boolean_test.setImage(icons["example_image_01"])
    label_test = AbstractLabelWidget(text="label")
    label_test.setImage("/media/ssd01/dev/katana/KatanaWidgets/Icons/iconGSV.png")
    # button_test = AbstractButtonInputWidget(title="yolo", is_toggleable=True)
    # label_test = AbstractLabelWidget(text="test")
    #
    # string_test = AbstractStringInputWidget()

    main_widget = QWidget()
    main_layout = QVBoxLayout(main_widget)
    #main_layout.addWidget(boolean_test)
    main_layout.addWidget(label_test)
    #main_layout.addWidget(string_test)

    main_widget.move(QCursor.pos())
    main_widget.show()
    main_widget.resize(256, 256)
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

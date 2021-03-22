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
from cgwidgets.widgets.AbstractWidgets.AbstractInputInterface import iAbstractInputWidget


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

from qtpy.QtWidgets import QWidget, QSizePolicy, QStackedLayout
from qtpy.QtGui import QPixmap
from cgwidgets.settings.icons import icons

class AbstractLabelWidget(QWidget, iAbstractInputWidget):
    """
    Display label

    Args:
        text (str): text to be displayed as the title
        image (str): path on disk to image

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
        super(AbstractLabelWidget, self).__init__(parent)
        # setup layout
        QStackedLayout(self)
        self.layout().setStackingMode(QStackedLayout.StackAll)

        # initialize widgets
        self._image_widget = QLabel(self)
        self.pixmap = QPixmap()
        self._image_widget.setPixmap(self.pixmap)
        self._text_widget = QLabel(self)

        # setup default attrs
        self._image_resize_mode = Qt.KeepAspectRatio

        if text:
            self.setText(text)
            self.setTextColor(iColor["rgba_text"])

        if image:
            self.setImage(image)


        # setup style

        # remove hover display (overwritten by image)
        style_sheet = removeHoverDisplay(self.styleSheet(), "INPUT WIDGETS")
        self.setStyleSheet(style_sheet)

        # set text alignment
        self.textWidget().setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
        self.imageWidget().setAlignment(Qt.AlignCenter | Qt.AlignHCenter)

        self.layout().addWidget(self.textWidget())
        self.layout().addWidget(self.imageWidget())

    """ TEXT """
    def textWidget(self):
        return self._text_widget

    def setText(self, text):
        """
        Sets the display text of the widget
        Args:
            text (str):  text to be displayed
        """
        self.textWidget().setText(text)

    def setTextColor(self, color):
        """
        Sets the color of the displayed text

        Args:
            color (RGBA): Tuple of RGBA(255) values
        """
        self.textWidget().setStyleSheet("color: rgba{color}".format(color=repr(color)))

    """ IMAGE  """
    def imageWidget(self):
        return self._image_widget

    def setImage(self, image_path):
        """
        Sets a background image

        Args:
            image_path (str): path to image on disk
        """
        self.setImagePath(image_path)
        self.pixmap = QPixmap(image_path)
        self.resizeImage()
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
        """
        Main function for resizing the image.
        """
        self.imageWidget().setFixedSize(self.width(), self.height())
        if not self.pixmap.isNull():
            self.pixmap = self.pixmap.scaled(self.width(), self.height(), self.imageResizeMode())
            self.imageWidget().setPixmap(self.pixmap)

    """ EVENTS """
    def time(self):
        """
        Util function for the timer event that is running while the user resizes.  This timer
        is being run so that after the user finishes resizing, more updates can happen.
        """
        self.setImage(self.imagePath())
        delattr(self, "_timer")

    def resizeEvent(self, event):
        """
        After the user has finished resizing, after 1 second, this will fire an update
        signal to have the display fully updated.
        """
        # preflight
        if not hasattr(self, "_image_path"): return QWidget.resizeEvent(self, event)
        if not self.isImageVisible(): return QWidget.resizeEvent(self, event)

        # start _timer
        from qtpy.QtCore import QTimer
        if hasattr(self, "_timer"):
            self._timer.stop()

        self._timer = QTimer()
        self._timer.timeout.connect(self.time)
        self._timer.start(500)

        # resize image
        self.resizeImage()

        return QWidget.resizeEvent(self, event)


#         style_sheet = """
# /* << BACKGROUND IMAGE START >> */
# border-radius: 10px;
# background-color: rgba{rgba_background};
# color: rgba{rgba_text};
# /*border-image: url({image_path}) 0 0 0 0 stretch repeat;*/
# background-image: url({image_path} auto auto);
# /* << BACKGROUND IMAGE END >> */""".format(
#             image_path=image_path,
#             rgba_background=iColor["rgba_background_00"],
#             rgba_text=iColor["rgba_text"])
#         #border-image: url({image_path}) 0 0 0 0 stretch stretch;
#         style_sheet += self.styleSheet()
#
#         self.setStyleSheet(style_sheet)
#
#         # from qtpy.QtGui import QPixmap
#         # from cgwidgets.settings.icons import icons
#         # pixmap = QPixmap(icons["example_image_01"])
#         # self.setPixmap(pixmap)

    # def removeImage(self):
    #     style_sheet = self.styleSheet()
    #
    #     # todo update image
    #     style_sheet = re.sub(
    #         "(/\* << BACKGROUND IMAGE START >> \*/)([^\$]+)(/\* << BACKGROUND IMAGE END >> \*/)",
    #         "",
    #         style_sheet)
    #
    #     self.setStyleSheet(style_sheet)


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
    delegate_widget = AbstractBooleanInputWidget(text="yolo")
    overlay_widget = AbstractOverlayInputWidget(
        title="title",
        display_mode=AbstractOverlayInputWidget.RELEASE,
        delegate_widget=delegate_widget,
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

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

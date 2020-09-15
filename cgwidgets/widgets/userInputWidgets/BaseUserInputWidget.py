"""
TODO:
    Group Box
        *   Expose middle line color
        *   Dynamic text size
                QApplication.font()
        *   Add Widget to group box
                Multiple?
                    Would need another labelling device?
        *   Rounded vs straight corners?
        *   Expose orientation?
                That's a lot of work...
    User Input:
        *   Add ladder widget to numbers
        *   Ladder widget... center widget... needs to just be the input...

"""

from qtpy.QtWidgets import (
    QLineEdit, QLabel, QGroupBox, QBoxLayout, QSizePolicy
)
from qtpy.QtCore import Qt

from cgwidgets.utils import updateStyleSheet
from cgwidgets.settings.colors import RGBA_OUTLINE


class BaseUserInputWidget(QLineEdit):
    """
    Base class for users to input data into.

    Attributes:
        orig_value (str): the previous value set by the user
    """
    RGBA_BORDER_COLOR = RGBA_OUTLINE

    def __init__(self, parent=None):
        super(BaseUserInputWidget, self).__init__(parent)
        self._key_list = []
        self.rgba_border = BaseUserInputWidget.RGBA_BORDER_COLOR
        self.updateStyleSheet()
        self.editingFinished.connect(self.finishUserInput)

    def updateStyleSheet(self):
        self.setStyleSheet("""
            border: 2px solid rgba{border_color};
            border-right: None;
            border-left: None;
            border-bottom: None;
            background-color: rgba(0,0,0,0);
            padding-top: 5px;
            margin-top: 10px
            """.format(border_color=self._rgba_border))

    ''' PROPERTIES '''
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

    def getUserInput(self):
        """
        Evaluates the users input, this is important
        when using numbers
        """
        return str(eval(self.text()))

    @property
    def rgba_border(self):
        return self._rgba_border

    @rgba_border.setter
    def rgba_border(self, _rgba_border):
        self._rgba_border = _rgba_border
    """ UTILS """
    def setValidateUserInputFunction(self, function):
        """
        Sets the function that will validate the users input.  This function
        should take no args, and will need to return True/False.  This will be the
        check to determine if the users input is valid or not.
        """
        self._validate_user_input = function

    def checkUserInput(self):
        """
        Determines if the users input is valid
        """
        validation = self._validate_user_input()
        return validation

    ''' SIGNALS / EVENTS '''
    def focusInEvent(self, *args, **kwargs):
        self.setOrigValue(self.text())
        return QLineEdit.focusInEvent(self, *args, **kwargs)

    def finishUserInput(self):
        is_valid = self.checkUserInput()

        if is_valid:
            self.setText(self.getUserInput())
        else:
            self.setText(self.getOrigValue())

        # elif data_type == 'color':
        #     try:
        #         rgb = filter(None, text.split(' '))
        #         if len(rgb) != 3:
        #             self.setText(orig_value)
        #             return
        #         else:
        #             for value in rgb:
        #                 float(value)
        #
        #     except:
        #         self.setText(orig_value)
        #     pass

    def mousePressEvent(self, event, *args, **kwargs):
        if event.button() == Qt.MiddleButton:
            return
        return QLineEdit.mousePressEvent(self, event, *args, **kwargs)

    def keyPressEvent(self, event, *args, **kwargs):
        if event.key() in self.getKeyList():
            return QLineEdit.keyPressEvent(self, event, *args, **kwargs)


class BaseUserInputGroup(QGroupBox):
    RGBA_BORDER_COLOR = RGBA_OUTLINE
    PADDING = 3

    def __init__(self, parent=None):
        super(BaseUserInputGroup, self).__init__(parent)
        QBoxLayout(QBoxLayout.TopToBottom, self)
        self.layout().setAlignment(Qt.AlignTop)
        self.setTitle("lkasjdlfjaf")
        self.rgba_border = BaseUserInputGroup.RGBA_BORDER_COLOR
        self.padding = 3
        self.alpha = 48
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.updateStyleSheet()

    def updateStyleSheet(self):
        style_sheet = """
            QGroupBox::title{{
            subcontrol-origin: margin;
            subcontrol-position: top center; 
            padding: -{padding}px {paddingX2}px;
            }}
            QGroupBox[display_background=true]{{
                background-color: rgba(0,0,0,{alpha});
                border-width: 1px;
                border-radius: {paddingX2};
                border-style: solid;
                border-color: rgba{border_color};
                margin-top: 1ex;
                margin-bottom: {padding};
                margin-left: {padding};
                margin-right:  {padding};
            }}
            QGroupBox[display_background=false]{{
                background-color: rgba(0,0,0,0);
                border: None;
                margin-top: 1ex;
                margin-bottom: {padding};
                margin-left: {padding};
                margin-right:  {padding};
            }}
        """.format(
            padding=self.padding,
            paddingX2=(self.padding*2),
            alpha=self.alpha,
            border_color=repr(self.rgba_border)
        )
        self.setStyleSheet(style_sheet)

    """PROPERTIES"""
    @property
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, _alpha):
        self._alpha = _alpha

    @property
    def display_background(self):
        return self._display_background

    @display_background.setter
    def display_background(self, _display_background):
        self._display_background = _display_background
        self.setProperty('display_background', _display_background)
        updateStyleSheet(self)

    @property
    def padding(self):
        return self._padding

    @padding.setter
    def padding(self, _padding):
        self._padding = _padding

    @property
    def rgba_border(self):
        return self._rgba_border

    @rgba_border.setter
    def rgba_border(self, _rgba_border):
        self._rgba_border = _rgba_border


class NumberUserInputWidget(BaseUserInputWidget):
    """
    Base class for number based widgets.  The float
    and int input widgets will both inherit from this.

    Attributes:
        allow_negative (bool): determines if this will accept
            This is not currently set up
        do_math (bool): determines if this widget will support
            mathematical functions.  This is run by a simple eval(user_input).
    """
    KEY_LIST = [
        Qt.Key_0,
        Qt.Key_1,
        Qt.Key_2,
        Qt.Key_3,
        Qt.Key_4,
        Qt.Key_5,
        Qt.Key_6,
        Qt.Key_7,
        Qt.Key_8,
        Qt.Key_9,
        Qt.Key_Left,
        Qt.Key_Right,
        Qt.Key_Up,
        Qt.Key_Down,
        Qt.Key_Delete,
        Qt.Key_Backspace,
        Qt.Key_Return,
        Qt.Key_Enter,
        Qt.Key_CapsLock
    ]
    MATH_KEYS = [
        Qt.Key_V,
        Qt.Key_Plus,
        Qt.Key_plusminus,
        Qt.Key_Minus,
        Qt.Key_multiply,
        Qt.Key_Asterisk,
        Qt.Key_Slash
    ]

    def __init__(self, parent=None, allow_negative=False, do_math=False):
        super(NumberUserInputWidget, self).__init__(parent)
        self.setKeyList(NumberUserInputWidget.KEY_LIST)
        self._do_math = do_math
        self._allow_negative = allow_negative

    def setAllowNegative(self, _allow_negative):
        self._allow_negative = _allow_negative

    def getAllowNegative(self):
        return self._allow_negative

    def setDoMath(self, _do_math):
        self._do_math = _do_math

        # add key to key list
        if _do_math is True:
            for key in NumberUserInputWidget.MATH_KEYS:
                self.appendKey(key)
        else:
            for key in NumberUserInputWidget.MATH_KEYS:
                self.removeKey(key)

    def getDoMath(self):
        return self._do_math

    def validateEvaluation(self):
        # evaluate if math
        if self.getDoMath() is True:
            try:
                eval(self.text())
                return True
            except:
                return False


class FloatUserInputWidget(NumberUserInputWidget):
    def __init__(self, parent=None):
        super(FloatUserInputWidget, self).__init__(parent)
        self.appendKey(Qt.Key_Period)
        self.setValidateUserInputFunction(self.validateUserInput)
        self.setDoMath(True)

    def validateUserInput(self):
        """
        Check to see if the users input is valid or not
        """
        if not self.validateEvaluation(): return

        # check if float
        user_input = self.text()
        try:
            float(user_input)
            return True
        except ValueError:
            return False


class IntUserInputWidget(NumberUserInputWidget):
    def __init__(self, parent=None):
        super(IntUserInputWidget, self).__init__(parent)
        self.setValidateUserInputFunction(self.validateUserInput)
        self.setDoMath(True)

    def validateUserInput(self):
        """
        Check to see if the users input is valid or not
        """
        if not self.validateEvaluation(): return

        # check if float
        user_input = self.text()
        try:
            int(user_input)
            return True
        except ValueError:
            return False


class StringUserInputWidget(BaseUserInputWidget):
    def __init__(self, parent=None):
        super(StringUserInputWidget, self).__init__(parent)


class BooleanUserInputWidget(QLabel):
    def __init__(self, parent=None):
        super(BooleanUserInputWidget, self).__init__(parent)
        style_sheet = """
        QLabel[is_clicked=true]{background-color: rgba{clicked_color};
        QLabel
        """

    @property
    def is_clicked(self, is_clicked):
        return self._is_clicked

    @is_clicked.setter
    def is_clicked(self, is_clicked):
        self._is_clicked = is_clicked
        self.setProperty('is_clicked', is_clicked)
        updateStyleSheet(self)


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication, QWidget, QVBoxLayout
    from qtpy.QtGui import QCursor
    app = QApplication(sys.argv)
    w = QWidget()
    l = QVBoxLayout(w)

    gw = BaseUserInputGroup()
    gw.display_background = False
    l.addWidget(gw)

    input_widget = IntUserInputWidget()
    gw.layout().addWidget(input_widget)

    w.resize(500, 500)
    w.show()
    w.move(QCursor.pos())
    sys.exit(app.exec_())

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
    AbstractInputWidget (QLineEdit)
        | -- AbstractStringInputWidget
        | -- AbstractNumberInputWidget
                | -- AbstractFloatInputWidget
                | -- AbstractIntInputWidget
    BooleanInputWidget (QLabel)
"""

from qtpy.QtWidgets import (
    QLineEdit, QLabel, QApplication
)
from qtpy.QtCore import Qt, QEvent

from cgwidgets.utils import (
    updateStyleSheet, clearLayout, installLadderDelegate, getWidgetAncestor,
    getFontSize
)
from cgwidgets.settings.colors import iColor

from cgwidgets.widgets.AbstractWidgets import AbstractInputGroupBox, AbstractInputGroup


class AbstractInputWidget(QLineEdit):
    """
    Base class for users to input data into.

    Attributes:
        orig_value (str): the previous value set by the user
        key_list (list): of Qt.Key_KEY.  List of keys that are currently
            valid for this widget.
        rgba_background (rgba): value of rgba_background transparency
        rgba_border (rgba): color of the border...
        rgba_text (rgba): color of text
    """

    def __init__(self, parent=None):
        super(AbstractInputWidget, self).__init__(parent)
        # setup default args
        self._key_list = []

        # set up style
        self.rgba_border = iColor["rgba_outline"]
        self.rgba_background = iColor["rgba_gray_0"]
        self.rgba_text = iColor["rgba_text"]

        self.updateStyleSheet()

        # set up signals
        self.editingFinished.connect(self.userFinishedEditing)

    def updateStyleSheet(self):
        #style_sheet = getTopBorderStyleSheet(self._rgba_border, 2)
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
        Determines if the users input is valid
        """
        validation = self._validate_user_input()
        return validation

    def getInput(self):
        """
        Evaluates the users input, this is important
        when using numbers
        """
        return self.text()

    """ SIGNALS / EVENTS """
    def focusInEvent(self, *args, **kwargs):
        self.setOrigValue(self.text())
        return QLineEdit.focusInEvent(self, *args, **kwargs)

    def userFinishedEditing(self):
        """
        When the user has finished editing.  This will do a check to see
        if the input is valid, and then if it is, do something with that value
        if it isn't then it will return it to the previous value.
        """
        is_valid = self.checkInput()

        if is_valid:
            self.setText(self.getInput())
            #TODO This doesn't exist in this ffunctino... moved to iGroupInput
            # or somewhere more logical...
            try:
                self.userFinishedEditingEvent(self, self.getInput())
            except AttributeError:
                pass

        else:
            self.setText(self.getOrigValue())

    def mousePressEvent(self, event, *args, **kwargs):
        if event.button() == Qt.MiddleButton:
            return
        return QLineEdit.mousePressEvent(self, event, *args, **kwargs)


class AbstractNumberInputWidget(AbstractInputWidget):
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
        Qt.Key_Plus,
        Qt.Key_plusminus,
        Qt.Key_Minus,
        Qt.Key_multiply,
        Qt.Key_Asterisk,
        Qt.Key_Slash
    ]

    def __init__(
        self, parent=None, allow_negative=True, do_math=True
    ):
        super(AbstractNumberInputWidget, self).__init__(parent)
        self.setKeyList(AbstractNumberInputWidget.KEY_LIST)
        self.setDoMath(do_math)
        self.setAllowNegative(allow_negative)

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
    def setAllowNegative(self, _allow_negative):
        self._allow_negative = _allow_negative

    def getAllowNegative(self):
        return self._allow_negative

    def setDoMath(self, _do_math):
        self._do_math = _do_math

        # add key to key list
        if _do_math is True:
            for key in AbstractNumberInputWidget.MATH_KEYS:
                self.appendKey(key)
        else:
            for key in AbstractNumberInputWidget.MATH_KEYS:
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
        # default action
        else:
            if event.key() in self.getKeyList():
                return QLineEdit.keyPressEvent(self, event, *args, **kwargs)


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
        return str(eval(self.text()))


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
        return str(int(eval(self.text())))


class AbstractStringInputWidget(AbstractInputWidget):
    TYPE = 'string'
    def __init__(self, parent=None):
        super(AbstractStringInputWidget, self).__init__(parent)
        self.setValidateInputFunction(self.validateInput)

    def validateInput(self):
        return True


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

    # """ TRIGGER """
    # """
    # Im being lazy, this is a copy and paste from the AbstractInputWidget
    # """
    # def __user_input_event(self, *args, **kwargs):
    #     pass
    #
    # def setUserFinishedEditingEvent(self, function):
    #     """
    #     Sets the function that should be triggered everytime
    #     the user finishes editing this widget
    #     """
    #     self.__user_input_event = function
    #
    # def userFinishedEditingEvent(self, *args, **kwargs):
    #     """
    #     Internal event to run everytime the user triggers an update.  This
    #     will need to be called on every type of widget.
    #     """
    #     self.__user_input_event(*args, **kwargs)

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


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication, QWidget, QVBoxLayout
    from qtpy.QtGui import QCursor
    app = QApplication(sys.argv)
    # w = QWidget()
    # l = QVBoxLayout(w)
    # l.setAlignment(Qt.AlignTop)
    # input_widget = AbstractFloatInputWidget()
    # gw = AbstractInputGroup(title='cool stuff')
    # gw.layout().addWidget(input_widget)
    #
    #
    # asdf = AbstractInputGroupBox(title='not cool')
    # i2 = AbstractFloatInputWidget()
    # asdf.layout().addWidget(i2)
    # #gw.display_background = False
    # l.addWidget(gw)
    # l.addWidget(asdf)

    w = AbstractIntInputWidget()
    w.setDoMath(True)
    w.resize(500, 500)
    w.show()
    w.move(QCursor.pos())
    sys.exit(app.exec_())

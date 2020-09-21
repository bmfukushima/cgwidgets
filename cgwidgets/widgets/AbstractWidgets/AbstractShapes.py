# https://doc.qt.io/qt-5/qframe.html#Shape-enum
from qtpy.QtWidgets import (
    QFrame, QGroupBox, QBoxLayout, QVBoxLayout, QSizePolicy, QApplication,
    QWidget, QSplitter
)
from qtpy.QtCore import Qt

from cgwidgets.settings.colors import iColor
from cgwidgets.utils import (
    updateStyleSheet, getFontSize
)


class AbstractLine(QFrame):
    def __init__(self, parent=None):
        super(AbstractLine, self).__init__(parent)
        self.setStyleSheet("""
            margin: 30px;
        """)


class AbstractHLine(AbstractLine):
    def __init__(self, parent=None):
        super(AbstractHLine, self).__init__(parent)
        self.setFrameShape(QFrame.HLine)


class AbstractVLine(AbstractLine):
    def __init__(self, parent=None):
        super(AbstractVLine, self).__init__(parent)
        self.setFrameShape(QFrame.VLine)


class AbstractInputGroup(QFrame):
    """
    Main container widget for the QGroupBox container type.

    Most functions on this are for interacting with the internal
    group box.

    Widgets:
        AbstractInputGroup
            | -- QVBoxLayout
                    | -- AbstractInputGroupBox
                            | -- QBoxLayout
                                    |-* AbstractUserInputContainer
                                            | -- QBoxLayout
                                                | -- QLabel
                                                | -- UserInputWidget
    """
    def __init__(self, parent=None, title='None'):
        super(AbstractInputGroup, self).__init__(parent)
        QVBoxLayout(self)
        self.group_box = AbstractInputGroupBox(parent=parent, title=title)
        self.layout().addWidget(self.group_box)
        self.group_box.display_background = False

    def setTitle(self, title):
        self.group_box.setTitle(title)

    def insertWidget(self, index, widget):
        self.group_box.layout().insertWidget(index, widget)

    def removeWidgetByIndex(self, index):
        widget = self.group_box.layout().itemAt(index).widget()
        widget.setParent(None)

    def getWidgetList(self):
        """
        Returns all of the widgets inside of this container
        """
        widget_list = []
        for index in range(self.group_box.layout().childCount()):
            widget = self.group_box.layout().itemAt(index).widget()
            widget_list.append(widget)
        return widget_list


class AbstractInputGroupBox(QGroupBox):
    """
    Group box containing the user input parameters widgets.
    """
    RGBA_BORDER_COLOR = iColor.rgba_outline
    PADDING = 3
    BACKGROUND_COLOR = iColor.rgba_background

    def __init__(self, parent=None, title=None):
        super(AbstractInputGroupBox, self).__init__(parent)
        # setup main layout
        QBoxLayout(QBoxLayout.TopToBottom, self)
        self.layout().setAlignment(Qt.AlignTop)

        # create separator
        self.separator = AbstractHLine(self)
        self.separator.setStyleSheet("""
            background-color: rgba{rgba_text_color};
            margin: 30px;
            """.format(rgba_text_color=repr(iColor.rgba_text_color)))
        self.layout().addWidget(self.separator)

        # set up default attrs
        if title:
            self.setTitle(title)
        self._rgba_border = AbstractInputGroupBox.RGBA_BORDER_COLOR
        self._padding = AbstractInputGroupBox.PADDING
        self._rgba_background = AbstractInputGroupBox.BACKGROUND_COLOR

        # setup display styles
        self.display_background = True
        self.updateStyleSheet()

        font_size = getFontSize(QApplication)
        self.layout().setContentsMargins(self.padding*3, font_size*2, self.padding*3, font_size)
        self.layout().setSpacing(font_size)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

    def updateStyleSheet(self):
        font_size = getFontSize(QApplication)
        style_sheet = """
            QGroupBox::title{{
            subcontrol-origin: margin;
            subcontrol-position: top center; 
            padding: -{padding}px {paddingX2}px;
            }}
            QGroupBox[display_background=true]{{
                background-color: rgba{rgba_background};
                border-width: 1px;
                border-radius: {paddingX2};
                border-style: solid;
                border-color: rgba{border_color};
                margin-top: {font_size};
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
            font_size=font_size,
            padding=self.padding,
            paddingX2=(self.padding*2),
            rgba_background=repr(self.rgba_background),
            border_color=repr(self.rgba_border)
        )
        self.setStyleSheet(style_sheet)

    """PROPERTIES"""
    @property
    def rgba_background(self):
        return self._rgba_background

    @rgba_background.setter
    def rgba_background(self, _rgba_background):
        self._rgba_background = _rgba_background

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
        self.updateStyleSheet()

    """ COLORS """
    @property
    def rgba_border(self):
        return self._rgba_border

    @rgba_border.setter
    def rgba_border(self, _rgba_border):
        self._rgba_border = _rgba_border
        self.user_input_widget.rgba_border = _rgba_border

        self.updateStyleSheet()
        self.user_input_widget.updateStyleSheet()


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication, QLabel
    from PyQt5.QtGui import QCursor
    app = QApplication(sys.argv)

    sys.exit(app.exec_())

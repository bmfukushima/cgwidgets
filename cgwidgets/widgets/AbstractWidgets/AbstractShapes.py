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

        self.setStyleSheet("background-color: rgba{rgba_gray_0}".format(**iColor.style_sheet_args))

    """ PROPERTIES """
    def isSelected(self):
        return self._is_selected

    def setSelected(self, selected):
        self._is_selected = selected
        self.setProperty("is_selected", selected)
        self.group_box.setSelected(selected)

    def getTitle(self):
        return self.group_box.title()

    def setTitle(self, title):
        self.group_box.setTitle(title)

    """ INSERT WIDGETS """
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
    PADDING = 3

    def __init__(self, parent=None, title=None):
        super(AbstractInputGroupBox, self).__init__(parent)
        # setup main layout
        QBoxLayout(QBoxLayout.TopToBottom, self)
        self.layout().setAlignment(Qt.AlignTop)

        # create separator
        self.separator = AbstractHLine(self)
        self.separator.setStyleSheet("""
            background-color: rgba{rgba_text};
            margin: 30px;
            """.format(rgba_text=repr(iColor["rgba_text"])))
        self.layout().addWidget(self.separator)

        # set up default attrs
        if title:
            self.setTitle(title)
        self._rgba_border = iColor["rgba_outline"]
        self._padding = AbstractInputGroupBox.PADDING
        self._rgba_background = iColor["rgba_gray_0"]
        self._rgba_text = iColor["rgba_text"]

        # setup display styles
        self.display_background = True
        self.updateStyleSheet()

        font_size = getFontSize(QApplication)
        self.layout().setContentsMargins(self.padding*3, font_size*2, self.padding*3, font_size)
        self.layout().setSpacing(font_size)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

    def updateStyleSheet(self, args={}):
        font_size = getFontSize(QApplication)
        style_sheet_args = iColor.style_sheet_args
        style_sheet_args.update({
            "font_size" : font_size,
            "padding" : self.padding,
            "paddingX2" : (self.padding * 2),
            "rgba_gray_0" : repr(self.rgba_background),
            "border_color" : repr(self.rgba_border),
            "color" : repr(self.rgba_text)
        })
        style_sheet_args.update(args)

        style_sheet = """
            QGroupBox::title{{
                subcontrol-origin: margin;
                subcontrol-position: top center; 
                padding: -{padding}px {paddingX2}px;
                color: rgba{rgba_text};
            }}
            QGroupBox[is_selected=true]::title{{
                subcontrol-origin: margin;
                subcontrol-position: top center; 
                padding: -{padding}px {paddingX2}px;
                color: rgba{rgba_selected};
            }}
            QGroupBox[display_background=true]{{
                background-color: rgba{rgba_gray_0};
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
            **style_sheet_args
        )
        self.setStyleSheet(style_sheet)

    """PROPERTIES"""
    def isSelected(self):
        return self._is_selected

    def setSelected(self, selected):
        self._is_selected = selected
        self.setProperty("is_selected", selected)
        updateStyleSheet(self)

    @property
    def rgba_background(self):
        return self._rgba_background

    @rgba_background.setter
    def rgba_background(self, _rgba_background):
        self._rgba_background = _rgba_background

    @property
    def rgba_text(self):
        return self._rgba_text

    @rgba_text.setter
    def rgba_text(self, _rgba_text):
        self._rgba_text = _rgba_text
        #self.updateStyleSheet()

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

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

#


class AbstractLine(QFrame):
    def __init__(self, parent=None):
        super(AbstractLine, self).__init__(parent)
        self._length = -1

    def getMargin(self):
        if self.parent():
            if self.length() == -1:
                return 0
            parent_length = self.parent().width()
            margin = (parent_length - self.length()) * 0.5
        else:
            margin = 0
        return margin

    def setLength(self, length):
        """
        Sets the length of the line.  Note that width is already used
        """
        self._length = length
        self.update()

    def length(self):
        return self._length

    def update(self):
        margin = self.getMargin()
        self.setStyleSheet("""
            margin: {margin}px;
        """.format(margin=margin))

    def showEvent(self, event):
        self.update()
        return QFrame.showEvent(self, event)

    def resizeEvent(self, event):
        self.update()
        return QFrame.resizeEvent(self, event)


class AbstractHLine(AbstractLine):
    def __init__(self, parent=None):
        super(AbstractHLine, self).__init__(parent)
        self.setFrameShape(QFrame.HLine)


class AbstractVLine(AbstractLine):
    def __init__(self, parent=None):
        super(AbstractVLine, self).__init__(parent)
        self.setFrameShape(QFrame.VLine)


class AbstractInputGroupFrame(QFrame):
    """
    name (str): the name displayed to the user
    input_widget (InputWidgetInstance): The instance of the input widget type
        that is displayed to the user for manipulation
    input_widget_base_class (InputWidgetClass): The type of input widget that this is
        displaying to the user
            Options are:
                BooleanInputWidget
                StringInputWidget
                IntInputWidget
                FloatInputWidget
                ListInputWidget

    Virtual
        headerTextChanged (widget, value): event that is run every time the user
            finishes editing the header widget.
    """
    def __init__(
        self,
        parent=None,
        name="None",
        note="None",
        direction=Qt.Horizontal
    ):
        super(AbstractInputGroupFrame, self).__init__(parent)
        QBoxLayout(QBoxLayout.LeftToRight, self)

        # default attrs
        self._separator_length = -1
        self._separator_width = 3
        self._is_header_shown = True

        # setup layout
        from cgwidgets.widgets.AbstractWidgets.AbstractInputWidgets import AbstractLabelInputWidget
        self._label = AbstractLabelInputWidget(self)
        self._label.setUserFinishedEditingEvent(self.headerTextChanged)
        self._label.setText(name)

        # set up display
        self.setToolTip(note)
        self.setupStyleSheet()
        self.setDirection(direction)

    """ API """
    def isHeaderEditable(self):
        return self._label.isEditable()

    def setIsHeaderEditable(self, enabled):
        """
        Determines if the header can be edited or not
        """
        self._label.setEditable(enabled)

    def isHeaderShown(self):
        return self._is_header_shown

    def setIsHeaderShown(self, enabled):
        """
        Determines if the header should be shown

        The header is the QLabel with the text name, and the
        separator (QFrame).
        """
        self._is_header_shown = enabled
        if enabled:
            self._label.show()
            self._separator.show()
        else:
            self._label.hide()
            self._separator.hide()

    """ VIRTUAL """
    def __headerTextChanged(self, widget, value):
        pass

    def headerTextChanged(self, widget, value):
        self.__headerTextChanged(widget, value)

    def setHeaderTextChangedEvent(self, function):
        self.__headerTextChanged = function

    """ STYLE """
    def setupStyleSheet(self):
        style_sheet_args = iColor.style_sheet_args
        style_sheet = """
            QLabel{{color: rgba{rgba_text}}}
            LabelledInputWidget{{background-color: rgba{rgba_gray_3}}}
            FrameGroupInputWidget{{background-color: rgba{rgba_gray_3}}}
        """.format(
            **style_sheet_args
        )
        self.setStyleSheet(style_sheet)
        # self._label.setStyleSheet(
        #     self._label.styleSheet() + 'color: rgba{rgba_text}'.format(
        #         rgba_text=iColor.rgba_text))

    def setToolTip(self, tool_tip):
        self._label.setToolTip(tool_tip)

    """ Set Direction of input"""
    def setDirection(self, direction):
        if direction == Qt.Vertical:
            # update alignment
            self._label.setAlignment(Qt.AlignCenter)

            # update label
            self._label.setSizePolicy(
                QSizePolicy.MinimumExpanding, QSizePolicy.Preferred
            )

        elif direction == Qt.Horizontal:
            # update label
            self._label.setSizePolicy(
                QSizePolicy.Fixed, QSizePolicy.Preferred
            )

    def setSeparatorLength(self, length):
        self._separator.setLength(length)
        self._separator_length = length

    def setSeparatorWidth(self, width):
        self._separator.setLineWidth(width)
        self._separator_width = width

    """ PROPERTIES """
    def setName(self, name):
        self._label.setText(name)

    def getName(self):
        return self._label.text()

    # def labelWidth(self):
    #     return self._label_width
    #
    # def setLabelWidth(self, width):
    #     self._label_width = width
    #     self._label.setMinimumWidth(width)


class AbstractFrameGroupInputWidget(AbstractInputGroupFrame):
    """
    Stylized input group.  This has a base of a ShojiView,
    I'm not really sure why this is different than the InputGroupWidget...
    """
    def __init__(
        self,
        parent=None,
        name="None",
        note="None",
        direction=Qt.Horizontal
    ):
        # inherit
        super(AbstractFrameGroupInputWidget, self).__init__(parent, name, note, direction)

        # setup default attrs
        self._is_header_shown = True

        # create separator
        #self._separator = AbstractVLine(self)

        # add widgets to main layout
        self.layout().insertWidget(0, self._label)
        #self.layout().addWidget(self._separator)

        # setup defaults
        self.setIsHeaderShown(True)
        self.setIsHeaderEditable(False)

    """ API """
    def addInputWidget(self, widget, finished_editing_function=None):
        if finished_editing_function:
            widget.setUserFinishedEditingEvent(finished_editing_function)
        self.layout().addWidget(widget)

    def getInputWidgets(self):
        input_widgets = []
        # todo FAIL
        # this might fail due to separator hiding/parenting?
        for index in range(2, self.layout().count()):
            widget = self.layout().itemAt(index).widget()
            input_widgets.append(widget)

        return input_widgets

    """ STYLE """
    def setSeparatorLength(self, length):
        self._separator.setLength(length)
        self._separator_length = length

    def setSeparatorWidth(self, width):
        self._separator.setLineWidth(width)
        self._separator_width = width

    def setDirection(self, direction):
        """
        Sets the direction this input will be displayed as.

        Args:
            direction (Qt.DIRECTION)
        """
        # preflight
        if direction not in [Qt.Horizontal, Qt.Vertical]: return

        # set direction
        self._direction = direction

        # update separator
        if direction == Qt.Vertical:
            # direction
            self.layout().setDirection(QBoxLayout.TopToBottom)

            # separator
            self.updateSeparator(direction)

            # update alignment
            self._label.setAlignment(Qt.AlignCenter)
            self.layout().setAlignment(Qt.AlignTop)
            self.layout().setSpacing(5)

            # update label
            self._label.setSizePolicy(
                QSizePolicy.MinimumExpanding, QSizePolicy.Preferred
            )

        elif direction == Qt.Horizontal:
            # set layout direction
            self.layout().setDirection(QBoxLayout.LeftToRight)

            # update separator
            self.updateSeparator(direction)

            # alignment
            self.layout().setAlignment(Qt.AlignLeft)
            #self.layout().setSpacing(50)

            # update label
            self._label.setSizePolicy(
                QSizePolicy.MinimumExpanding, QSizePolicy.Preferred
            )

        return AbstractInputGroupFrame.setDirection(self, direction)

    def updateSeparator(self, direction):
        # remove existing separator
        if hasattr(self, '_separator'):
            self._separator.setParent(None)

        # create new separator
        if direction == Qt.Vertical:
            self._separator = AbstractHLine()
        elif direction == Qt.Horizontal:
            self._separator = AbstractVLine()

        # update separator
        self.setSeparatorWidth(self._separator_width)
        self.setSeparatorLength(self._separator_length)
        self.layout().insertWidget(1, self._separator)

        # return if there is no header to be displayed
        if not self.isHeaderShown():
            self._separator.hide()

"""
These are only being used in the Color Widget
"""
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
                                                | -- LabelledInputWidget
    """
    def __init__(self, parent=None, title='None'):
        super(AbstractInputGroup, self).__init__(parent)
        QVBoxLayout(self)
        self.group_box = AbstractInputGroupBox(parent=parent, title=title)
        self.layout().addWidget(self.group_box)
        self.group_box.display_background = False

        self.setStyleSheet("background-color: rgba{rgba_background_00}".format(**iColor.style_sheet_args))

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
        self._rgba_background = iColor["rgba_background_00"]
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
            "rgba_background_00" : repr(self.rgba_background),
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
                background-color: rgba{rgba_background_00};
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
                margin-right: {padding};
            }}
        """.format(
            **style_sheet_args
        )
        self.setStyleSheet(style_sheet)

    """PROPERTIES"""
    def displaySeparator(self, display):
        if display is True:
            self.separator.show()
        elif display is False:
            self.separator.hide()

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
    from qtpy.QtWidgets import QApplication, QLabel
    from qtpy.QtGui import QCursor
    app = QApplication(sys.argv)
    widget = QWidget()
    layout = QVBoxLayout(widget)
    for x in range(2):
        frame = AbstractVLine()
        layout.addWidget(frame)
    frame.hide()
    widget.show()
    sys.exit(app.exec_())

# https://doc.qt.io/qt-5/qframe.html#Shape-enum
from qtpy.QtWidgets import (
    QFrame, QGroupBox, QBoxLayout, QVBoxLayout, QSizePolicy, QApplication,
    QWidget, QSplitter
)
from qtpy.QtCore import Qt

from cgwidgets.widgets.AbstractWidgets.AbstractShojiLayout import AbstractShojiLayout
from cgwidgets.settings.colors import iColor
from cgwidgets.utils import (
    updateStyleSheet, getFontSize
)


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
        title="Name",
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
        from cgwidgets.widgets.AbstractWidgets.AbstractBaseInputWidgets import AbstractStringInputWidget
        from cgwidgets.widgets.AbstractWidgets.AbstractOverlayInputWidget import AbstractOverlayInputWidget
        delegate_widget = AbstractStringInputWidget(self)
        header_widget = AbstractOverlayInputWidget(
            self,
            title=title,
            display_mode=AbstractOverlayInputWidget.RELEASE,
            delegate_widget=delegate_widget)
        self.setHeaderWidget(header_widget)

        # set up display
        self.setToolTip(note)
        self.setDirection(direction)

    """ API """
    def isHeaderEditable(self):
        from cgwidgets.widgets import AbstractOverlayInputWidget
        if self.headerWidget.displayMode() != AbstractOverlayInputWidget.DISABLED:
            return True
        else:
            return False

    def setIsHeaderEditable(self, enabled, display_mode=None):
        """
        Determines if the header can be edited or not

        Args:
            enabled (bool): determines if the header should be editable or not
            display_mode (AbstractOverlayInputWidget.DISPLAY_MODE): determines what the display mode
                should be.  By default, this is set to AbstractOverlayInputWidget.RELEASE
        """
        from cgwidgets.widgets.AbstractWidgets.AbstractOverlayInputWidget import AbstractOverlayInputWidget

        # get display mode
        if enabled:
            if not display_mode:
                display_mode = AbstractOverlayInputWidget.RELEASE

        else:
            display_mode = AbstractOverlayInputWidget.DISABLED

        # set display mode
        self.headerWidget().setDisplayMode(display_mode)

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
            self.headerWidget().show()
            self._separator.show()
        else:
            self.headerWidget().hide()
            self._separator.hide()

    """ HEADER WIDGET """
    def headerWidget(self):
        return self._header_widget

    def setHeaderWidget(self, header_widget):
        if hasattr(self, "_header_widget"):
            self._header_widget.setParent(None)
        self._header_widget = header_widget
        self.layout().insertWidget(0, header_widget)

    def label(self):
        return self.headerWidget().viewWidget()

    """ VIRTUAL """
    def __headerTextChanged(self, widget, value):
        pass

    def headerTextChanged(self, widget, value):
        self.__headerTextChanged(widget, value)

    def setHeaderTextChangedEvent(self, function):
        self.__headerTextChanged = function

    """ STYLE """
    def setToolTip(self, tool_tip):
        self.headerWidget().setToolTip(tool_tip)

    """ Set Direction of input"""
    def direction(self):
        return self._direction

    def setDirection(self, direction):
        self._direction = direction
        if direction == Qt.Vertical:
            # update alignment
            # self.label().setAlignment(Qt.AlignCenter)

            # update label
            self.headerWidget().setSizePolicy(
                QSizePolicy.MinimumExpanding, QSizePolicy.Fixed
            )

        elif direction == Qt.Horizontal:
            # update alignment
            # self.label().setAlignment(Qt.AlignLeft)

            # update label
            self.headerWidget().setSizePolicy(
                QSizePolicy.Fixed, QSizePolicy.Preferred
            )

    def setSeparatorLength(self, length):
        self._separator.setLength(length)
        self._separator_length = length

    def setSeparatorWidth(self, width):
        self._separator.setLineWidth(width)
        self._separator_width = width

    """ PROPERTIES """
    def setTitle(self, title):
        self.headerWidget().setTitle(title)

    def getTitle(self):
        return self.headerWidget().title()


class AbstractFrameInputWidgetContainer(AbstractInputGroupFrame):
    """
    Stylized input group.  This has a base of a ShojiLayout,
    I'm not really sure why this is different than the InputGroupWidget...
    """
    def __init__(
        self,
        parent=None,
        title="None",
        note="None",
        direction=Qt.Horizontal
    ):
        # inherit
        super(AbstractFrameInputWidgetContainer, self).__init__(parent, title, note, direction)

        # setup default attrs
        self._is_header_shown = True
        self._frame_container = True

        # setup defaults
        self.setIsHeaderShown(True)
        # self.setIsHeaderEditable(False)

    """ API """
    def addInputWidget(self, widget, finished_editing_function=None):
        if finished_editing_function:
            widget.setUserFinishedEditingEvent(finished_editing_function)
        self.layout().addWidget(widget)

    def delegateWidgets(self):
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
            self.layout().setAlignment(Qt.AlignTop)
            self.layout().setSpacing(5)

            # update label
            self.label().setSizePolicy(
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
            self.label().setSizePolicy(
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


class AbstractButtonInputWidgetContainer(AbstractShojiLayout):
    """
    Provides a multi button input widget.

    This widget will align all of the widgets that are currently selected
    higher up in the priority, ie insertWidget(0, widget), and those that
    are not selected further down in the priority ie. insertWidget(-1, widget).

    Note: that each of this widgets returns a flag

    Attributes:
        _buttons (dict): of clickable buttons
            name: button
        _current_buttons (List): of AbstractButtonInputWidget that are
            currently selected by the user
    """

    def __init__(self, parent=None, orientation=Qt.Horizontal):
        self._rgba_flag = iColor["rgba_selected_hover"]
        super(AbstractButtonInputWidgetContainer, self).__init__(parent, orientation)
        self.setIsSoloViewEnabled(False)
        self.setIsHandleStatic(True)
        self.setHandleWidth(0)
        self.setHandleLength(-1)

        #
        self._buttons = {}
        self._is_multi_select = True
        self._current_buttons = []
        self._is_toggleable = True

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

    def isToggleable(self):
        return self._is_toggleable

    def setIsToggleable(self, enabled):
        self._is_toggleable = enabled

    """ BUTTONS """

    def updateButtonSelection(self, selected_button, enabled=None):
        """
        Sets the button provided to either be enabled or disabled
        Args:
            selected_button (AbstractButtonInputWidget):
            enabled (bool):

        Returns:

        """
        if enabled is not None:
            self.setButtonAsCurrent(selected_button, enabled)
        else:
            if selected_button in self.currentButtons():
                self.setButtonAsCurrent(selected_button, False)
            else:
                self.setButtonAsCurrent(selected_button, True)

        # update display
        for button in self._buttons.values():
            if button not in self.currentButtons():
                button.setProperty("is_selected", False)
                updateStyleSheet(button)
        self.normalizeWidgetSizes()

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
        # multi select
        if self.isMultiSelect():
            # add to list
            if enabled:
                self._current_buttons.append(current_button)
                self.insertWidget(len(self.currentButtons()) - 1, current_button)

            # remove from list
            else:
                if current_button in self._current_buttons:
                    self._current_buttons.remove(current_button)
                self.insertWidget(len(self.currentButtons()), current_button)

        # single select
        else:
            self._current_buttons = [current_button]
            self.insertWidget(0, current_button)

        # setup button style
        if enabled:
            current_button.is_selected = True

        self.update()

    def addButton(self, title, flag, user_clicked_event=None, enabled=False, image=None):
        """
        Adds a button to this widget

        Args:
            title (str): display name
            enabled (bool): determines the default status of the button
            flag (arbitrary): flag to be returned to denote that this button is selected
            user_clicked_event (function): to run when the user clicks
            image:

        Returns (AbstractButtonInputWidget): newly created button
        Note:
            image is not currently setup.  This kwarg is merely a place holder.
        Todo: setup image
        """
        from cgwidgets.widgets import AbstractButtonInputWidget
        button = AbstractButtonInputWidget(self, user_clicked_event=user_clicked_event, title=title, flag=flag,
                                           is_toggleable=self.isToggleable())
        self.updateButtonSelection(button, enabled)
        self._buttons[title] = button
        self.addWidget(button)
        return button

    """ EVENTS """

    def showEvent(self, event):
        """
        Reorganizes widgets into correct order
        """
        for button in self._current_buttons:
            self.insertWidget(0, button)
        return AbstractShojiLayout.showEvent(self, event)


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

        self.setStyleSheet("background-color: rgba{rgba_background_01}".format(**iColor.style_sheet_args))

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
    from cgwidgets.utils import centerWidgetOnCursor
    from qtpy.QtGui import QCursor
    app = QApplication(sys.argv)
    widget = AbstractButtonInputWidgetContainer()
    for x in range(0, 5):
        widget.addButton(str(x), str(x))
    widget.setIsToggleable(False)
    # for x in range(0, 5):
    #     temp = QLabel(str(x))
    #     widget.addInputWidget(temp)

    widget.show()
    centerWidgetOnCursor(widget)
    sys.exit(app.exec_())

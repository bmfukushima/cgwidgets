"""
TODO:
    *   Full Screen mode
    *   Better Displays...
            Has been added to TabTansu... add to this one?

"""

from qtpy.QtWidgets import QSplitter, qApp
from qtpy.QtCore import Qt
from qtpy.QtGui import QCursor

from cgwidgets.settings.colors import(
    RGBA_TANSU_FLAG,
    RGBA_TANSU_HANDLE,
    RGBA_TANSU_HANDLE_HOVER
)

from cgwidgets.utils import updateStyleSheet


class BaseTansuWidget(QSplitter):
    """
    Splitter widget that has advanced functionality.  This serves as a base
    class for everything that will be used through this library.

    Attributes:
        isSoloView (bool): If this is in full screen mode.  Full screen mode
            allows the user to press a hotkey to make a widget take up the
            entire space of this splitter.  The default hotkey for this is ~ but can be
            set with the setSoloViewHotkey() call.
        rgba_handle (rgba): color of the handle
        rgba_handle_hover (rgba): color of the handle when hovered over
        # not used... but I set them up anyways lol
        currentIndex (int): The current index
        currentWidget (widget): The current widget

    Class Attributes:
        HANDLE_WIDTH: Default size of the handle
        FULLSCREEN_HOTKEY: Default hotkey for toggling full screen mode
    """
    HANDLE_WIDTH = 2
    FULLSCREEN_HOTKEY = 96
    HANDLE_COLOR = RGBA_TANSU_HANDLE
    HANDLE_COLOR_HOVER = RGBA_TANSU_HANDLE_HOVER
    FLAG_COLOR = RGBA_TANSU_FLAG

    def __init__(self, parent=None, orientation=Qt.Vertical):
        super(BaseTansuWidget, self).__init__(parent)
        # set default attrs
        self._current_index = None
        self._current_widget = None
        self._is_solo_view = False
        self._solo_view_hotkey = BaseTansuWidget.FULLSCREEN_HOTKEY

        # set colors
        self._rgba_handle = BaseTansuWidget.HANDLE_COLOR
        self._rgba_handle_hover = BaseTansuWidget.HANDLE_COLOR_HOVER
        self._rgba_flag = BaseTansuWidget.FLAG_COLOR
        self.setOrientation(orientation)

        # set up handle defaults
        self.setHandleWidth(BaseTansuWidget.HANDLE_WIDTH)
        self.updateStyleSheet()

    """ UTILS """
    def updateStyleSheet(self):
        """
        Sets the color of the handle based off of the two provided

        Args:
            color (rgba): color to display when not hovering over handle
            hover_color (rgba): color to display when hover over handle
        """
        style_sheet = """
            BaseTansuWidget[is_solo_view=true]{{
                border: 3px solid rgba{rgba_flag}; 
            }}
            QSplitter::handle {{
                border: 1px double rgba{rgba_handle};
            }}
            QSplitter::handle:hover {{
                border: 2px double rgba{rgba_handle_hover};
            }}
        """.format(
            rgba_flag=repr(self.rgba_flag),
            rgba_handle=repr(self.rgba_handle),
            rgba_handle_hover=repr(self.rgba_handle_hover)
        )

        self.setStyleSheet(style_sheet)

    def displayAllWidgets(self, value):
        """
        Hides/shows all of the widgets in this splitter.  This is a utility function
        for toggling inbetween full screen modes.

        Args:
            value (bool): If True this will show all the widgets, if False,
                this will hide everythign.
        """
        for index in range(self.count()):
            widget = self.widget(index)
            if value:
                widget.show()
            else:
                widget.hide()

    def clear(self, exclusion_list=[]):
        """
        Removes all the widgets

        Args:
            exclusion_list (list): of widgets.  If widget is in this list,
                it will not be removed during this operation
        """
        for index in reversed(range(self.count())):
            widget = self.widget(index)
            if widget not in exclusion_list:
                widget.setParent(None)

    @staticmethod
    def getIndexOfWidget(widget):
        """
        Recursive function to find the index of this widget's parent widget
        that is a child of the main splitter, and then return that widgets index
        under the main splitter.

        Args:
            widget (QWidget): Widget to set searching from, this is set
                to the current widget under the cursor
        Returns (int, widget):
            if returns None, then bypass everything.
        """
        if widget.parent():
            if isinstance(widget.parent(), BaseTansuWidget):
                return widget.parent().indexOf(widget), widget
            else:
                return BaseTansuWidget.getIndexOfWidget(widget.parent())
        else:
            return None, None

    def toggleSoloViewView(self):
        """
        Toggles between the full view of either the parameters
        or the creation portion of this widget.  This is to help
        to try and provide more screen real estate to this widget
        which already does not have enough
        """
        # toggle attrs
        self.toggleIsSoloView(not self.isSoloView())

    def keyPressEvent(self, event):
        if event.key() == self.soloViewHotkey():
            self.toggleIsSoloView(True)
            return
        elif event.key() == Qt.Key_Escape:
            self.toggleIsSoloView(False)
            return
        return QSplitter.keyPressEvent(self, event)

    def isolateWidgets(self, widget_list):
        """
        Shows only the widgets provided to the widget list
        """
        self.displayAllWidgets(False)
        for widget in widget_list:
            widget.show()

    """ SOLO VIEW """
    def isSoloView(self):
        return self._is_solo_view

    @staticmethod
    def setIsSoloView(tansu_widget, _is_solo_view):
        tansu_widget._is_solo_view = _is_solo_view
        tansu_widget.setProperty('is_solo_view', _is_solo_view)
        updateStyleSheet(tansu_widget)

    def toggleIsSoloView(self, is_solo_view, widget=None):
        """
        Sets the widget that the mouse is currently over to take up
        all of the space inside of the splitter by hiding the rest of the
        widgets.

        If it is already taking up all of the space, it will look for the next
        AbstractSplitter and set that one to take up the entire space.  It
        will continue doing this recursively both up/down until there it is
        either fully expanded or fully collapsed.

        TODO:
            This works... but really needs to be cleaned up...
        """

        # get the current splitter
        if not widget:
            widget = qApp.widgetAt(QCursor.pos())
        current_index, current_widget = self.getIndexOfWidget(widget)
        current_splitter = current_widget.parent()

        # enter full screen
        if is_solo_view is True:
            # adjust parent widget
            if current_splitter.isSoloView() is True:
                current_index1, current_widget1 = self.getIndexOfWidget(current_splitter)
                if current_widget1:
                    parent_splitter = current_widget.parent()
                    parent_splitter.toggleIsSoloView(True, current_splitter)
                    BaseTansuWidget.setIsSoloView(parent_splitter, True)
                    parent_splitter.setFocus()

            # adjust current widget
            elif current_splitter.isSoloView() is False:
                current_splitter.displayAllWidgets(False)
                current_widget.show()
                BaseTansuWidget.setIsSoloView(current_splitter, True)
                current_widget.setFocus()
                #return
        # exit full screen
        else:
            # adjust current widget
            if current_splitter.isSoloView() is True:
                current_splitter.displayAllWidgets(True)
                BaseTansuWidget.setIsSoloView(current_splitter, False)
                current_widget.setFocus()
                #return
            # adjust parent widget
            elif current_splitter.isSoloView() is False:
                current_index1, current_widget1 = self.getIndexOfWidget(current_splitter)
                if current_widget1:
                    parent_splitter = current_widget.parent()
                    parent_splitter.toggleIsSoloView(False, current_splitter)

                    BaseTansuWidget.setIsSoloView(parent_splitter, False)
                    parent_splitter.setFocus()
                    current_widget1.setFocus()

        # set attrs

        current_splitter.setCurrentIndex(current_index)
        current_splitter.setCurrentWidget(current_widget)

    def soloViewHotkey(self):
        return self._solo_view_hotkey

    def setSoloViewHotkey(self, solo_view_hotkey):
        self._solo_view_hotkey = solo_view_hotkey

    """ PROPERTIES """
    def getCurrentWidget(self):
        return self._current_widget

    def setCurrentWidget(self, widget):
        self._current_widget = widget

    def getCurrentIndex(self):
        return self._current_index

    def setCurrentIndex(self, current_index):
        self._current_index = current_index

    @property
    def handle_width(self):
        return self._handle_width

    @handle_width.setter
    def handle_width(self, _handle_width):
        self._handle_width = _handle_width
        self.setHandleWidth(_handle_width)

    """ COLORS """
    @property
    def rgba_handle(self):
        return self._rgba_handle

    @rgba_handle.setter
    def rgba_handle(self, _rgba_handle):
        self._rgba_handle = _rgba_handle
        self.updateStyleSheet()

    @property
    def rgba_handle_hover(self):
        return self._rgba_handle_hover

    @rgba_handle_hover.setter
    def rgba_handle_hover(self, _rgba_handle_hover):
        self._rgba_handle_hover = _rgba_handle_hover
        self.updateStyleSheet()

    @property
    def rgba_flag(self):
        return self._rgba_flag

    @rgba_flag.setter
    def rgba_flag(self, _rgba_flag):
        self._rgba_flag = _rgba_flag
        self.updateStyleSheet()


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication, QLabel
    from PyQt5.QtGui import QCursor
    app = QApplication(sys.argv)

    main_splitter = BaseTansuWidget()
    main_splitter.setObjectName("main")
    main_splitter.addWidget(QLabel('a'))
    main_splitter.addWidget(QLabel('b'))
    main_splitter.addWidget(QLabel('c'))

    splitter1 = BaseTansuWidget(orientation=Qt.Horizontal)
    splitter1.setObjectName("embed")
    for x in range(3):
        l = QLabel(str(x))
        splitter1.addWidget(l)

    main_splitter.addWidget(splitter1)
    main_splitter.show()
    main_splitter.setFixedSize(400, 400)
    main_splitter.move(QCursor.pos())
    sys.exit(app.exec_())


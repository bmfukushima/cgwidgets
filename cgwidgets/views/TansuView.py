"""
TODO:
    *   Full Screen mode
    *   Better Displays...
            Has been added to TabTansu... add to this one?

"""

from qtpy.QtWidgets import QSplitter, QSplitterHandle, qApp
from qtpy.QtCore import Qt
from qtpy.QtGui import QCursor

from cgwidgets.settings.colors import iColor
from cgwidgets.settings.stylesheets import splitter_handle_ss

from cgwidgets.utils import updateStyleSheet


class TansuView(QSplitter):
    """
    Splitter widget that has advanced functionality.  This serves as a base
    class for everything that will be used through this library.

    Attributes:
        isSoloView (bool): If this is in full screen mode.  Full screen mode
            allows the user to press a hotkey to make a widget take up the
            entire space of this splitter.  The default hotkey for this is ~ but can be
            set with the setSoloViewHotkey() call.
        is_handle_static (bool): determines if the handles are adjustable or not.
            This is mainly used for reusing the tansu view as bidirectional layout
        rgba_handle (rgba): color of the handle
        rgba_handle_hover (rgba): color of the handle when hovered over
        # not used... but I set them up anyways lol
        currentIndex (int): The current index
        currentWidget (widget): The current widget
        handle_width (int): width of the handle
        handle_length (int): length of handle:
            if set to -1, this will returen the entire length
        handle_margin (int, int): offset from sides of each handle.  This will only
            work when the length is set to -1
        handle_margin_offset (int): offset for handle margin towards widgets

    Class Attributes:
        HANDLE_WIDTH: Default size of the handle
        FULLSCREEN_HOTKEY: Default hotkey for toggling full screen mode

    Note:
        When solo'ing arbitrary widgets.  Setting an attribute called "not_soloable"
        will cause this widget to not be able to be solo'd (hopefully)
    """
    HANDLE_WIDTH = 2
    FULLSCREEN_HOTKEY = 96

    def __init__(self, parent=None, orientation=Qt.Vertical):
        super(TansuView, self).__init__(parent)

        # set colors
        self._rgba_handle = iColor["rgba_outline"]
        self._rgba_handle_hover = iColor["rgba_selected_hover"]
        self._rgba_flag = iColor["rgba_selected"]
        self._rgba_background = iColor["rgba_gray_2"]
        self._rgba_text = iColor["rgba_text"]

        # set default attrs
        self._current_index = None
        self._current_widget = None
        self._is_solo_view_enabled = True
        self.setProperty("is_solo_view_enableable", True)

        self._is_solo_view = False
        self._solo_view_hotkey = TansuView.FULLSCREEN_HOTKEY
        self._is_handle_static = False
        self.setProperty("is_handle_static", False)
        self._is_handle_visible = True
        self.setProperty("is_handle_visible", True)
        self.setOrientation(orientation)

        # set up handle defaults
        self._handle_margin_offset = 0
        self.setHandleWidth(TansuView.HANDLE_WIDTH)
        self.setHandleLength(-1)

    """ UTILS """
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

    def setAllWidgetsToUniformSize(self):
        """
        Sets all of the widgets to a uniform size.

        This will be done, by setting all of the handle positions to a
        value relative to the handles index and the width/height of this
        TansuView.

        Note:
            Handle at 0 index is ALWAYs invisible

        """
        num_handles = len(self.getAllHandles())
        # get offset
        if self.orientation() == Qt.Vertical:
            offset = self.height() / (num_handles)
        elif self.orientation() == Qt.Horizontal:
            offset = self.width() / (num_handles)

        for i in range(1, num_handles):
            self.moveSplitter(int(offset * (i)) - 1, i)

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
        if widget:
            if widget.parent():
                if isinstance(widget.parent(), TansuView):
                    return widget.parent().indexOf(widget), widget
                else:
                    return TansuView.getIndexOfWidget(widget.parent())
            else:
                return None, None

    def getFirstSoloableWidget(self, widget):
        """
        Gets the first widget that is capable of being soloable

        Currently this is hard  coded to the "not_soloable" attribute...
        Args:
            widget (QWidget): widget to start searching from to be solo'd
        """
        if hasattr(widget, "not_soloable"):
            if widget.parent():
                return self.getFirstSoloableWidget(widget.parent())
            else:
                return None
        else:
            return widget

    """ EVENTS """
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
        """
        """
        # preflight
        if not self.isSoloViewEnabled(): QSplitter.keyPressEvent(self, event)

        # solo view
        if event.key() == self.soloViewHotkey():
            # preflight
            pos = QCursor.pos()
            widget_pressed = qApp.widgetAt(pos)
            if isinstance(widget_pressed, QSplitterHandle): return

            # toggle solo view
            widget_soloable = self.getFirstSoloableWidget(widget_pressed)
            self.toggleIsSoloView(True, widget=widget_soloable)
            return

        # unsolo view
        elif event.key() == Qt.Key_Escape:
            self.toggleIsSoloView(False)
            return

        # something else
        return QSplitter.keyPressEvent(self, event)

    def isolateWidgets(self, widget_list):
        """
        Shows only the widgets provided to the widget list
        """
        self.displayAllWidgets(False)
        for widget in widget_list:
            widget.show()

    def resizeEvent(self, event):
        """TODO why was I resizing here..."""
        #pass
        self.updateStyleSheet()

    """ SOLO VIEW """
    def isSoloViewEnabled(self):
        return self._is_solo_view_enabled

    def setIsSoloViewEnabled(self, enabled):
        """
        Determines is this widget can be set to Solo view or not.

        Args:
            enabled:
        """
        self._is_solo_view_enabled = enabled
        self.setProperty("is_solo_view_enableable", enabled)

    def isSoloView(self):
        return self._is_solo_view

    @staticmethod
    def setIsSoloView(tansu_widget, _is_solo_view):
        tansu_widget._is_solo_view = _is_solo_view
        tansu_widget.setProperty('is_solo_view', _is_solo_view)
        updateStyleSheet(tansu_widget)
        #print('setting is solo ', _is_solo_view)

    def toggleIsSoloView(self, is_solo_view, widget=None):
        """
        Toggles how much space a widget should take up relative to its parent.

        Sets the widget that the mouse is currently over to take up
        all of the space inside of the splitter by hiding the rest of the
        widgets.

        If it is already taking up all of the space, it will look for the next
        AbstractSplitter and set that one to take up the entire space.  It
        will continue doing this recursively both up/down until there it is
        either fully expanded or fully collapsed.

        Note:
            solo view hotkey (~) may need to be re implemented as a key event
        """

        # get the current splitter
        if not widget:
            widget = qApp.widgetAt(QCursor.pos())
        if not widget:
            return
        current_index, current_widget = self.getIndexOfWidget(widget)
        if not current_widget: return
        current_splitter = current_widget.parent()

        # enter full screen
        if is_solo_view is True:
            # adjust parent widget
            if current_splitter.isSoloView() is True:
                current_index1, current_widget1 = self.getIndexOfWidget(current_splitter)
                if current_widget1:
                    parent_splitter = current_widget.parent()
                    parent_splitter.toggleIsSoloView(True, current_splitter)
                    TansuView.setIsSoloView(parent_splitter, True)
                    parent_splitter.setFocus()

            # adjust current widget
            elif current_splitter.isSoloView() is False:
                current_splitter.displayAllWidgets(False)
                current_widget.show()
                TansuView.setIsSoloView(current_splitter, True)
                current_widget.setFocus()

        # exit full screen
        else:
            # adjust current widget
            if current_splitter.isSoloView() is True:
                current_splitter.displayAllWidgets(True)
                TansuView.setIsSoloView(current_splitter, False)
                current_widget.setFocus()
                #return
            # adjust parent widget
            elif current_splitter.isSoloView() is False:
                current_index1, current_widget1 = self.getIndexOfWidget(current_splitter)
                if current_widget1:
                    parent_splitter = current_widget.parent()
                    parent_splitter.toggleIsSoloView(False, current_splitter)

                    TansuView.setIsSoloView(parent_splitter, False)
                    parent_splitter.setFocus()
                    current_widget1.setFocus()

    def soloViewHotkey(self):
        return self._solo_view_hotkey

    def setSoloViewHotkey(self, solo_view_hotkey):
        self._solo_view_hotkey = solo_view_hotkey

    """ HANDLE """
    def isHandleVisible(self):
        return self._is_handle_visible

    def setIsHandleVisible(self, enabled):
        self._is_handle_visible = enabled
        self.setProperty("is_handle_visible", enabled)
        updateStyleSheet(self)

    def isHandleStatic(self):
        return self._is_handle_static

    def setIsHandleStatic(self, enabled):
        self._is_handle_static = enabled
        self.setProperty("is_handle_static", enabled)
        updateStyleSheet(self)

    def createHandle(self):
        handle = TansuViewHandle(self.orientation(), self)
        return handle

    def getAllHandles(self):
        """
        Returns (list): of all handles in this TansuView

        """
        _handles = []
        for i, child in enumerate(self.children()):
            if isinstance(child, TansuViewHandle):
                _handles.append(child)
        return _handles

    def handleLength(self):
        return self._handle_length

    def setHandleLength(self, _handle_length):
        self._handle_length = _handle_length
        self.updateStyleSheet()

    def handleMarginOffset(self):
        return self._handle_margin_offset

    def setHandleMarginOffset(self, _handle_margin_offset):
        self._handle_margin_offset = _handle_margin_offset
        #self.updateStyleSheet()

    def getHandleLengthMargin(self):
        """
        Gets the length of the margins for the style sheet.
        This will determine how far the margins for each handle should be
        in order to constrain the handle to a static size.

        Returns (str): <margin>px <margin>px
            ie 10px 10px
        """
        if self.handleLength() < 0:
            return "{x}px {y}px".format(x=self.handleMarginOffset(), y=self.handleMarginOffset())

        if self.orientation() == Qt.Vertical:
            length = self.width()
            margin = (length - self.handleLength()) * 0.5
            margins = "{margin_offset}px {margin}px".format(margin=margin, margin_offset=self.handleMarginOffset())

        elif self.orientation() == Qt.Horizontal:
            length = self.height()
            margin = (length - self.handleLength()) * 0.5
            margins = "{margin}px {margin_offset}px".format(margin=margin, margin_offset=self.handleMarginOffset())

        return margins

    """ PROPERTIES """
    def getCurrentWidget(self):
        return self._current_widget

    def setCurrentWidget(self, widget):
        self._current_widget = widget

    def getCurrentIndex(self):
        return self._current_index

    def setCurrentIndex(self, current_index):
        self._current_index = current_index

    """ COLORS """
    def updateStyleSheet(self):
        """
        Sets the color of the handle based off of the two provided

        Args:
            color (rgba): color to display when not hovering over handle
            hover_color (rgba): color to display when hover over handle
        """

        style_sheet_args = iColor.style_sheet_args

        style_sheet_args.update({
            'rgba_flag': repr(self.rgba_flag),
            'rgba_handle': repr(self.rgba_handle),
            'rgba_handle_hover': repr(self.rgba_handle_hover),
            'rgba_background': repr(self.rgba_background),
            'rgba_text': repr(self.rgba_text),
            'handle_length_margin': self.getHandleLengthMargin(),
            'type': type(self).__name__,
        })
        style_sheet = """
        /* VIEW */
            {type}{{
                background-color: rgba{rgba_background};
                color: rgba{rgba_text};
            }}
            {type}[is_solo_view_enableable=true]{{
                border: 2px solid rgba{rgba_background};
            }}
            {type}[is_solo_view=true]{{
                border: 2px dotted rgba{rgba_flag}; 
            }}
        /* HANDLE ;*/
            {splitter_handle_ss}
        """.format(
            **style_sheet_args,
            splitter_handle_ss=splitter_handle_ss.format(**style_sheet_args)
        )

        self.setStyleSheet(style_sheet)

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

    @property
    def rgba_background(self):
        return self._rgba_background

    @rgba_background.setter
    def rgba_background(self, _rgba_background):
        self._rgba_background = _rgba_background
        self.updateStyleSheet()

    @property
    def rgba_text(self):
        return self._rgba_text

    @rgba_text.setter
    def rgba_text(self, _rgba_text):
        self._rgba_text = _rgba_text
        self.updateStyleSheet()


class TansuViewHandle(QSplitterHandle):
    def __init__(self, orientation, parent=None):
        super(TansuViewHandle, self).__init__(orientation, parent)

    def mouseMoveEvent(self, event):
        if self.parent().isHandleStatic():
            return
        else:
            return QSplitterHandle.mouseMoveEvent(self, event)


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication, QLabel
    from qtpy.QtGui import QCursor
    app = QApplication(sys.argv)

    main_splitter = TansuView()
    main_splitter.setOrientation(Qt.Horizontal)
    main_splitter.setIsHandleVisible(False)
    main_splitter.setHandleLength(100)
    main_splitter.setObjectName("main")

    label = QLabel('a')
    main_splitter.addWidget(label)
    main_splitter.addWidget(QLabel('b'))
    main_splitter.addWidget(QLabel('c'))
    label.setStyleSheet("color: rgba(255,0,0,255)")
    splitter1 = TansuView(orientation=Qt.Horizontal)
    splitter1.setObjectName("embed")
    for x in range(3):
        l = QLabel(str(x))
        l.setStyleSheet("color: rgba(255,0,0,255)")
        splitter1.addWidget(l)

    main_splitter.addWidget(splitter1)


    main_splitter.show()
    #main_splitter.updateStyleSheet()
    #splitter1.updateStyleSheet()
    #main_splitter.setFixedSize(400, 400)
    main_splitter.move(QCursor.pos())
    sys.exit(app.exec_())


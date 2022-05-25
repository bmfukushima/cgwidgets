"""
SHOJI LAYOUT

The Shoji View is essentially a QSplitter that has the option to
allow any widget inside of it to become full screen using the
the hotkey set with setSoloViewHotkey(), by default this is set to
tilda, "~", or 96 (note: right now 96 is hard coded as ~ seems to be
hard to get Qt to register in their Key_KEY shit).  Using the ALT modifier
when using multiple Shoji Views embedded inside each other will make
the current Shoji View full screen, rather than the widget that it is
hovering over.  The user can leave full screen by hitting the "ESC" key.

Widgets can be added/inserted with the kwarg "is_soloable", to stop the
widget from being able to be solo'd, or force it to be on in some
scenerios.  This sets a property "is_soloable" on any child widget, and the main
ShojiLayout to determine if each widget is soloable.

HIERARCHY:

SIGNALS:
    Solo View Display: When a user hovers over a widget that can be solo'd a display pops
    up.  This display is driven by a dynamic style sheet, with the properties "hover_display"
    "is_soloable" (needs to be moved to style sheet...)


NOTE:
    On systems using GNOME such as Ubuntu 20.04, you may need to disable
    the "Super/Alt+Tilda" system level hotkey which is normally set to
        "Switch windows of an application"
    Alt+Esc
        "Switch windows directly"

TODO:
    *   Double press ESC / Tilda
            Full Screen / Collapse All
"""

from qtpy.QtWidgets import QSplitter, QSplitterHandle, QApplication
from qtpy.QtCore import Qt, QEvent
from qtpy.QtGui import QCursor

from cgwidgets.settings import iColor
from cgwidgets.settings.stylesheets import splitter_handle_ss
from cgwidgets.settings.hover_display import installHoverDisplaySS
from cgwidgets.utils import updateStyleSheet, getWidgetUnderCursor, getWidgetsDescendants, isWidgetDescendantOfInstance

from cgwidgets.widgets.AbstractWidgets.AbstractSplitterWidget import AbstractSplitterWidget


class AbstractShojiLayout(AbstractSplitterWidget):
    """
    Splitter widget that has advanced functionality.  This serves as a base
    class for everything that will be used through this library.

    Attributes:
        isSoloView (bool): If this is in full screen mode.  Full screen mode
            allows the user to press a hotkey to make a widget take up the
            entire space of this splitter.  The default hotkey for this is ~ but can be
            set with the setSoloViewHotkey() call.
        is_solo_view_enabled (bool): determines if this Shoji can enter full screen mode.
        is_handle_static (bool): determines if the handles are adjustable or not.
            This is mainly used for reusing the shoji view as bidirectional layout
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
        SOLO_VIEW_HOTKEY: Default hotkey for toggling full screen mode
        SOLOEVENTACTIVE (bool): Determines if a solo view event is active
            This is used to stop ShojiLayouts embedded recursively from calling
            the events multiple times.
    Note:
        When solo'ing arbitrary widgets.  Setting an attribute called "not_soloable"
        will cause this widget to not be able to be solo'd (hopefully)
    """
    HANDLE_WIDTH = 2
    SOLO_VIEW_HOTKEY = [Qt.Key_Space, 96]
    UNSOLO_VIEW_HOTKEY = [Qt.Key_Escape]
    MODIFIER = Qt.AltModifier
    SOLOEVENTACTIVE = False

    def __init__(self, parent=None, orientation=Qt.Vertical):
        super(AbstractShojiLayout, self).__init__(parent)

        # set colors
        self._rgba_handle = iColor["rgba_outline"]
        self._rgba_handle_hover = iColor["rgba_selected_hover"]
        self._rgba_flag = iColor["rgba_selected"]
        self._rgba_background = iColor["rgba_background_00"]
        self._rgba_text = iColor["rgba_text"]
        self._base_style_sheet = """
{type}{{
    background-color: rgba{rgba_background};
    color: rgba{rgba_text};
}}""".format(
            rgba_background=repr(self.rgba_background),
            rgba_text=repr(self.rgba_text),
            type=type(self).__name__,
        )

        # set default attrs
        self._current_index = None
        self._current_widget = None
        self._is_solo_view_enabled = True
        self.setProperty("is_soloable", True)

        self._is_solo_view = False
        self._solo_view_hotkey = AbstractShojiLayout.SOLO_VIEW_HOTKEY
        self._unsolo_view_hotkey = AbstractShojiLayout.UNSOLO_VIEW_HOTKEY
        self._is_handle_static = False
        self.setProperty("is_handle_static", False)
        self._is_handle_visible = True
        self.setProperty("is_handle_visible", True)
        self.setOrientation(orientation)

        # set up handle defaults
        self._handle_margin_offset = 0
        self.setHandleWidth(AbstractShojiLayout.HANDLE_WIDTH)
        self.setHandleLength(-1)

    """ UTILS """
    def isShojiMVW(self):
        """ Determines if this is a child of a ShojiModelViewWidget"""
        from .AbstractShojiWidget import AbstractShojiModelViewWidget
        widget = getWidgetUnderCursor()
        while widget.parent():
            if isinstance(widget.parent(),  AbstractShojiModelViewWidget):
                return True
            widget = widget.parent()

        return False

    def setFocusWidget(self):
        """
        Attempting to suppress signals from the base widgets
        so that they don't lose focus while doing random shit

        Args:
            event:

        Returns:

        """

        # hack to ensure Katana gets the focus on the right widget...
        widget_under_cursor = getWidgetUnderCursor()
        self.setFocus()
        return
        if widget_under_cursor:
            # need to import here to avoid circular import
            from .AbstractShojiWidget import AbstractShojiModelDelegateWidget
            from cgwidgets.utils import isWidgetDescendantOfInstance
            if isWidgetDescendantOfInstance(widget_under_cursor, widget_under_cursor.parent(), AbstractShojiModelDelegateWidget):
                layout_widget = self.getChildWidgetFromGrandchild(widget_under_cursor)
                if isinstance(layout_widget, AbstractShojiModelDelegateWidget):
                    layout_widget.getMainWidget().setFocus()
                else:
                    self.setFocus()
        else:
            self.setFocus()

    def getChildWidgetFromGrandchild(self, widget):
        """ Assuming the widget is a grandchild of this widget, this will return the child

        Args:
            widget (QWidget): to start searching from"""
        if widget.parent() == self:
            return widget
        else:
            if widget.parent():
                return self.getChildWidgetFromGrandchild(widget.parent())

    def displayAllWidgets(self, value):
        """
        Hides/shows all of the widgets in this splitter.  This is a utility function
        for toggling in between full screen modes.

        Args:
            value (bool): If True this will show all the widgets, if False,
                this will hide all widgets.
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

    def normalizeWidgetSizes(self):
        """
        Sets all of the widgets to a uniform size.

        This will be done, by setting all of the handle positions to a
        value relative to the handles index and the width/height of this
        AbstractShojiLayout.

        Note:
            Handle at 0 index is ALWAYs invisible

        """
        self.show()

        num_handles = len(self.getAllHandles())
        if 0 < num_handles:
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
                if isinstance(widget.parent(), AbstractShojiLayout):
                    return widget.parent().indexOf(widget), widget
                else:
                    return AbstractShojiLayout.getIndexOfWidget(widget.parent())
            else:
                return None, None

    """ VIRTUAL EVENTS """
    def setToggleSoloViewEvent(self, function):
        """
        Sets the event to be run after the soloHotkey has been pressed.

        This virtual function will take one argument

        Args:
            function (function)
        """
        self.__toggleSoloViewEvent = function

    def toggleSoloViewEvent(self, enabled, widget):
        """
        Event that is run after a solo/unsolo operation has happened.

        Args:
            enabled (bool): if True, widget is being solo, if False,
                widget is being unsolod
            widget (QWidget): First soloable widget that was pressed.

        Returns:

        """
        self.__toggleSoloViewEvent(enabled, widget)

    def __toggleSoloViewEvent(self, enabled, widget):
        pass

    """ EVENTS """
    @staticmethod
    def isSoloViewEventActive():
        return AbstractShojiLayout.SOLOEVENTACTIVE

    @staticmethod
    def setIsSoloViewEventActive(enabled):
        if enabled:
            AbstractShojiLayout.SOLOEVENTACTIVE = True
        if not enabled:
            AbstractShojiLayout.SOLOEVENTACTIVE = False

    def __soloViewHotkeyPressed(self, event):
        """
        Helper function for when the "soloViewHotkey()" is pressed.

        This provides the primary functionality for when the user presses the
        hotkey to go into solo view on a widget.

        Args:
            event (QEvent): Key press event
        """
        # preflight
        pos = QCursor.pos()
        widget_pressed = QApplication.instance().widgetAt(pos)

        # bypass handles
        if isinstance(widget_pressed, QSplitterHandle): return

        # Press solo view hotkey
        widget_soloable = self.getFirstSoloableWidget(widget_pressed)

        # preflight
        if not widget_soloable: return
        # stop from recursing to higher ShojiLayouts
        if isinstance(widget_soloable, AbstractShojiLayout) and not widget_soloable.property("is_soloable"): return

        # toggle solo view ( shoji view )
        from .AbstractShojiWidget.AbstractShojiModelViewWidget import AbstractShojiMainDelegateWidget
        is_shoji_mvw = isinstance(self, AbstractShojiMainDelegateWidget)

        # toggle parent widget
        if event.modifiers() == AbstractShojiLayout.MODIFIER or (is_shoji_mvw and self.count() == 2):
            shoji_layout = self.getFirstShojiLayoutWidget(widget_pressed)
            if shoji_layout:
                self.toggleIsSoloView(True, widget=shoji_layout)
        # toggle solo view (individual widget )
        else:
            self.toggleIsSoloView(True, widget=widget_soloable)

    def enterEvent(self, event):
        self.setFocusWidget()
        return QSplitter.enterEvent(self, event)

    def keyPressEvent(self, event):
        """
        """
        # preflight
        if not self.isSoloViewEnabled():
            return QSplitter.keyPressEvent(self, event)

        # solo view
        if event.key() in self.soloViewHotkeys():
            if not AbstractShojiLayout.SOLOEVENTACTIVE:
                if self.isSoloViewEnabled():
                    AbstractShojiLayout.setIsSoloViewEventActive(True)
                    self.__soloViewHotkeyPressed(event)
                    return

        # unsolo view
        elif event.key() in self.unsoloViewHotkeys():
            if not AbstractShojiLayout.SOLOEVENTACTIVE:
                AbstractShojiLayout.setIsSoloViewEventActive(True)
                if event.modifiers() == AbstractShojiLayout.MODIFIER:
                    self.unsoloAll(self)
                else:
                    self.toggleIsSoloView(False)
                return

        # something else
        return QSplitter.keyPressEvent(self, event)

    def keyReleaseEvent(self, event):
        """ Disable solo view event flag """
        if event.key() in self.soloViewHotkeys():
            AbstractShojiLayout.setIsSoloViewEventActive(False)
        elif event.key() in self.unsoloViewHotkeys():
            AbstractShojiLayout.setIsSoloViewEventActive(False)

        return QSplitter.keyReleaseEvent(self, event)

    def resizeEvent(self, event):
        """TODO why was I resizing here..."""
        #pass
        self.updateStyleSheet()
        return QSplitter.resizeEvent(self, event)

    def eventFilter(self, obj, event):
        # enable activity
        if event.type() == QEvent.KeyPress:
            # preflight
            if not AbstractShojiLayout.SOLOEVENTACTIVE:
                if event.key() in self.soloViewHotkeys():
                    if self.isSoloViewEnabled():
                        AbstractShojiLayout.setIsSoloViewEventActive(True)
                        self.__soloViewHotkeyPressed(event)
                        return True
                if event.key() in self.unsoloViewHotkeys():
                    AbstractShojiLayout.setIsSoloViewEventActive(False)
                    if event.modifiers() == AbstractShojiLayout.MODIFIER:
                        self.unsoloAll(self)
                    else:
                        self.toggleIsSoloView(False)
                    return True

        # disable activity on release
        if event.type() == QEvent.KeyRelease:
            if AbstractShojiLayout.SOLOEVENTACTIVE:
                if event.key() in self.unsoloViewHotkeys() + self.soloViewHotkeys():
                    AbstractShojiLayout.setIsSoloViewEventActive(False)
        if event.type() == QEvent.Enter:
            self.setFocusWidget()
        return False

    """ WIDGETS """
    def installHoverDisplay(self, widget):
        """
        Installs the hover display mechanisn on child widgets
        Args:
            widget (QWidget): child to have hover display installed on.

        Returns:

        """
        # widget.installEventFilter(self)
        hover_type_flags = {
            'focus':{'hover_display':True, 'is_soloable':True},
            'hover_focus':{'hover_display':True, 'is_soloable':True},
            'hover':{'hover_display':True, 'is_soloable':True},
        }
        installHoverDisplaySS(
            widget,
            name="SHOJI VIEW",
            hover_type_flags=hover_type_flags)

    def isolateWidgets(self, widget_list):
        """
        Shows only the widgets provided to the widget list

        Args:
            widget_list (list): of widgets to be displayed
        """
        self.displayAllWidgets(False)
        for widget in widget_list:
            widget.show()

    def __insertShojiWidget(self, widget, is_soloable=None, override=True):
        """ Add a widget to the GUI

       This utility function is run everytime an addWidget or insertWidget
       is called.  Its primary responsibility is to setup the hover display,
       and the ability for a widget to be soloable

        Args:
            widget (QWidget): Widget to add to the GUI
            is_soloable (bool): determines if this item is able to be solo'd
            override (bool): determines if the is_soloable property should be overwritten
        """

        if is_soloable is None:
            if widget.property("is_soloable") is None:
                self.setChildSoloable(self.isSoloViewEnabled(), widget)
            elif override:
                self.setChildSoloable(self.isSoloViewEnabled(), widget)
        else:
            #self.setChildSoloable(is_soloable, widget)
            self.setChildSoloable(is_soloable, widget)

        descendants = getWidgetsDescendants(widget.layout())
        descendants.append(widget)
        for w in descendants:
            w.installEventFilter(self)
        self.installHoverDisplay(widget)

    # good use case for a decorator?
    def addWidget(self, widget, is_soloable=None, override=True):
        """ Add a widget to the GUI

        Args:
            widget (QWidget): Widget to add to the GUI
            is_soloable (bool): determines if this item is able to be solo'd
            override (bool): determines if the is_soloable property should be overwritten
        """
        self.__insertShojiWidget(widget, is_soloable=is_soloable, override=override)
        return QSplitter.addWidget(self, widget)

    def insertWidget(self, index, widget, is_soloable=None, override=True):
        """ Add a widget to the GUI

        Args:
            index (int): Index to insert widget at
            widget (QWidget): Widget to add to the GUI
            is_soloable (bool): determines if this item is able to be solo'd
            override (bool): determines if the is_soloable property should be overwritten
        """
        self.__insertShojiWidget(widget, is_soloable=is_soloable, override=override)
        return QSplitter.insertWidget(self, index, widget)

    """ SOLO VIEW """
    def getFirstShojiLayoutWidget(self, widget):
        """
        Gets the first soloable shoji layout widget

        Args:
            widget (QWidget): widget to start searching from to be solo'd
        """
        from cgwidgets.widgets import AbstractModelViewWidget
        while widget.parent():
            # add special condition to ignore model view widgets
            if isinstance(widget, AbstractModelViewWidget):
                widget = widget.parent()
                continue
            if isinstance(widget, AbstractShojiLayout) and widget.property("is_soloable"):
                return widget
            widget = widget.parent()

        return None

    def getFirstSoloableWidget(self, widget):
        """
        Gets the first widget that is capable of being soloable

        Currently this is hard  coded to the "is_soloable" Qt property
        Args:
            widget (QWidget): widget to start searching from to be solo'd
        """
        if not widget: return None

        while widget.parent():
            if widget.property("is_soloable"):
                return widget
            # todo not sure if this is necessary
            # stop from recursing to higher ShojiLayouts
            # if isinstance(widget, AbstractShojiLayout):
            #     if widget.property("is_soloable"):
            #         return widget
            widget = widget.parent()

        return None

    def isSoloView(self):
        return self._is_solo_view

    def setIsSoloView(self, shoji_view, _is_solo_view):
        """
        Determines whether or not the view should be set to solo mode or not.

        This is a helper function called by "toggleIsSoloView"

        Args:
            shoji_view (AbstractShojiLayout):
            _is_solo_view (bool):
        """

        shoji_view._is_solo_view = _is_solo_view
        shoji_view.setProperty('is_solo_view', _is_solo_view)
        updateStyleSheet(shoji_view)

        # run solo view event
        shoji_view.toggleSoloViewEvent(_is_solo_view, shoji_view)

    def unsoloAll(self, widget):
        """
        Unsolo's the current widget provided, and then recurses up the hierarchy
        and unsolo's all available widgets.

        Args:
            widget (QWidget): Widget to start recursively searching up from
        """
        if hasattr(widget, "toggleIsSoloView"):
            widget.toggleIsSoloView(False)
        if widget.parent():
            return self.unsoloAll(widget.parent())

    def setChildSoloable(self, enabled, child):
        """
        Determines if the child widget provided can enter a "solo" view state
        Args:
            enabled (bool):
            child (widget):
        """
        child.setProperty('hover_display', True)
        child.setProperty('is_soloable', enabled)

    def isSoloViewEnabled(self):
        return self._is_solo_view_enabled

    def setIsSoloViewEnabled(self, enabled, override_children=True):
        """
        Determines is this widget can be set to Solo view or not.

        Args:
            enabled (bool): determines if this layout can be set to a soloview or not
            override_children (bool): determines if the children should inherit the enabled value provided
        """
        self._is_solo_view_enabled = enabled
        self.setProperty("is_soloable", enabled)

        if override_children:
            for child in self.children():
                self.setChildSoloable(enabled, child)

    def toggleIsSoloView(self, is_solo_view, widget=None, current_shoji=None):
        """
        Toggles how much space a widget should take up relative to its parent.

        Sets the widget that the mouse is currently over to take up
        all of the space inside of the splitter by hiding the rest of the
        widgets.

        If it is already taking up all of the space, it will look for the next
        AbstractShojiLayout and set that one to take up the entire space.  It
        will continue doing this recursively both up/down until there it is
        either fully expanded or fully collapsed.

        Note:
            solo view hotkey (~) may need to be re implemented as a key event
        """

        # pre flight
        if not widget:
            widget = QApplication.instance().widgetAt(QCursor.pos())
        if not widget:
            return
        current_index, current_widget = self.getIndexOfWidget(widget)
        if not current_widget:
            return

        if not current_shoji:
            current_shoji = current_widget.parent()

        # check to ensure shoji view has solo mode enabled
        if hasattr(widget, "isSoloViewEnabled"):
            if not current_shoji.isSoloViewEnabled():
                if current_shoji.parent():
                    return self.toggleIsSoloView(is_solo_view, widget=current_shoji.parent())
                else:
                    return

        # enter full screen
        if is_solo_view is True:
            # adjust parent widget
            if current_shoji.isSoloView():
                current_index1, current_widget1 = self.getIndexOfWidget(current_shoji)
                if current_widget1:
                    parent_shoji = current_widget.parent()
                    parent_shoji.toggleIsSoloView(True, current_shoji)

                    self.setIsSoloView(parent_shoji, True)
                    self.setFocusWidget()

            # adjust current widget
            else:
                current_shoji.displayAllWidgets(False)
                current_widget.show()
                self.setIsSoloView(current_shoji, True)
                self.setFocusWidget()

        # exit full screen
        else:
            # adjust current widget
            if current_shoji.isSoloView() is True:
                current_shoji.displayAllWidgets(True)
                self.setIsSoloView(current_shoji, False)
                self.setFocusWidget()

            # adjust parent widget
            elif current_shoji.isSoloView() is False:
                current_index1, current_widget1 = self.getIndexOfWidget(current_shoji)
                if current_widget1:
                    parent_shoji = current_widget1.parent()
                    parent_shoji.toggleIsSoloView(False, current_shoji)

                    self.setIsSoloView(parent_shoji, False)
                    self.setFocusWidget()

    def soloViewHotkeys(self):
        return self._solo_view_hotkey

    def setSoloViewHotkeys(self, solo_view_hotkey):
        self._solo_view_hotkey = solo_view_hotkey

    def unsoloViewHotkeys(self):
        return self._unsolo_view_hotkey

    def setUnsoloViewHotkeys(self, unsolo_view_hotkey):
        self._unsolo_view_hotkey = unsolo_view_hotkey

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
        handle = AbstractShojiLayoutHandle(self.orientation(), self)
        return handle

    def getAllHandles(self):
        """
        Returns (list): of all handles in this AbstractShojiLayout

        """
        _handles = []
        for i, child in enumerate(self.children()):
            if isinstance(child, AbstractShojiLayoutHandle):
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

    """ COLORS """
    def baseStyleSheet(self):
        return self._base_style_sheet

    def setBaseStyleSheet(self, _base_style_sheet):
        self._base_style_sheet = _base_style_sheet

    def updateStyleSheet(self):
        """
        Sets the color of the handle based off of the two provided

        Args:
            color (rgba): color to display when not hovering over handle
            hover_color (rgba): color to display when hover over handle

        ToDo: Style display bug
            Since this isnt resizing the handle sizes wont update anymore...
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
        style_sheet_args.update({
            'splitter_handle_ss': splitter_handle_ss.format(**style_sheet_args),
            'base_style_sheet': self.baseStyleSheet()
        })
        # TODO is_solo_view causing pixel issue
        style_sheet = """
/* VIEW */

{base_style_sheet}

/* HANDLE */
{splitter_handle_ss}
        """.format(**style_sheet_args)

        # update hover display property
        # for child in self.children():
        #     if child.property("is_soloable"):
        #         child.setProperty("hover_display", True)
        #     else:
        #         child.setProperty("hover_display", False)

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


class AbstractShojiLayoutHandle(QSplitterHandle):
    def __init__(self, orientation, parent=None):
        super(AbstractShojiLayoutHandle, self).__init__(orientation, parent)

    def mouseMoveEvent(self, event):
        if self.parent().isHandleStatic():
            return
        else:
            return QSplitterHandle.mouseMoveEvent(self, event)


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication, QLabel
    from qtpy.QtGui import QCursor

    from cgwidgets.settings.hover_display import installHoverDisplaySS
    app = QApplication(sys.argv)

    main_splitter = AbstractShojiLayout()
    main_splitter.setOrientation(Qt.Vertical)
    main_splitter.setIsHandleVisible(False)
    main_splitter.setHandleLength(100)
    main_splitter.setObjectName("main")
    #main_splitter.setIsSoloViewEnabled(False)
    label = QLabel('a')
    main_splitter.addWidget(label)
    main_splitter.addWidget(QLabel('b'))
    main_splitter.addWidget(QLabel('c'))
    main_splitter.setStyleSheet("border: 5px solid rgba(0,255,0,255)")
    splitter1 = AbstractShojiLayout(orientation=Qt.Horizontal)
    installHoverDisplaySS(splitter1, "TEST")
    splitter1.setObjectName("embed")
    for x in range(3):
        l = QLabel(str(x))
        #l.setStyleSheet("color: rgba(255,0,0,255)")
        splitter1.addWidget(l)
    splitter1.setChildSoloable(False, l)
    main_splitter.setChildSoloable(False, label)
    main_splitter.addWidget(splitter1)

    def test(pos, index):
        print (pos, index)

    # main_splitter.addDelayedSplitterMovedEvent()



    main_splitter.show()
    #main_splitter.updateStyleSheet()
    #splitter1.updateStyleSheet()
    #main_splitter.setFixedSize(400, 400)
    main_splitter.move(QCursor.pos())
    sys.exit(app.exec_())
#

# import sys
# from qtpy.QtWidgets import QApplication, QLabel
# from qtpy.QtGui import QCursor
# app = QApplication(sys.argv)
#
# import inspect
#
#
# def is_relevant(obj):
#     """Filter for the inspector to filter out non user defined functions/classes"""
#     if hasattr(obj, '__name__') and obj.__name__ == 'type':
#         return False
#
#     if inspect.isfunction(obj) or inspect.isclass(obj) or inspect.ismethod(obj):
#         return True
#
#
# def print_docs(module):
#     default = 'No doc string provided' # Default if there is no docstring, can be removed if you want
#     flag = True
#
#     for child in inspect.getmembers(module, is_relevant):
#         if not flag: print('\n\n\n')
#         flag = False # To avoid the newlines at top of output
#         doc = inspect.getdoc(child[1])
#         if not doc:
#             doc = default
#         print(child[0], doc, sep = '\n')
#
#         if inspect.isclass(child[1]):
#             for grandchild in inspect.getmembers(child[1], is_relevant):
#                 doc = inspect.getdoc(grandchild[1])
#                 if doc:
#                     doc = doc.replace('\n', '\n    ')
#                 else:
#                     doc = default
#                 print('\n    ' + grandchild[0], doc, sep = '\n    ')
#
#

#
#print_docs(AbstractShojiLayout)
# for child in inspect.getmembers(AbstractShojiLayout, is_relevant)[:10]:
#     module = inspect.getmodule(child[1])
#     if module.__name__ == "__main__":
#         print ('========================')
#         name = child[0]
#         doc_string = inspect.getdoc(child[1])
#         args = inspect.getfullargspec(child[1])[0]
#         args_string = ', '.join(args)
#         #print(type(args), args)
#         if doc_string:
#             doc_string = "\t" + doc_string.replace('\n', '\n\t')
#         else:
#             doc_string = '\t ffs dude, do a better job'
#         print ("{name} ({args})\n\t{doc}\n\n".format(name=name, args=args_string, doc=doc_string))
#
# sys.exit(app.exec_())
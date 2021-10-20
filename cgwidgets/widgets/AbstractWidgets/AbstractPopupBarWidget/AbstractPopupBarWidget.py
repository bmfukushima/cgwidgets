""" TODO
    * How am I doing the popups... I can't find a setWindowFlags =\
        I know I did it... I just don't know where it went lol
    Attributes:
        direction
        num_widgets:
            should just be able to get the count of the mini viewer widget...
        enlargedScale
            Needs to be moved from the AbstractPiPWidget to the Taskbar widget
"""

import json
from collections import OrderedDict
import os

from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSplitter, QSplitterHandle, QApplication)
from qtpy.QtCore import QEvent, Qt, QPoint

from cgwidgets.utils import (
    getWidgetUnderCursor,
    isWidgetDescendantOf,
    isCursorOverWidget,
    getWidgetAncestor,
    getJSONData,
    runDelayedEvent,
    setAsTool)

from cgwidgets.settings import attrs

from cgwidgets.widgets.AbstractWidgets.AbstractLabelledInputWidget import AbstractLabelledInputWidget
from cgwidgets.widgets.AbstractWidgets.AbstractOverlayInputWidget import AbstractOverlayInputWidget


from cgwidgets.widgets import (AbstractSplitterWidget)


class AbstractPopupBarWidget(AbstractSplitterWidget):
    """
    Widget that contains all of the PiPWidgets.

    This widget is an overlay of the MainWidget, and sits at a parallel hierarchy to the PiPMainViewer

    Attributes:
        direction (attrs.DIRECTION): direction that the popup will be displayed on
        display_mode (AbstractPopupBarWidget.TYPE): Determines what type of widget this should be displayed as
            valid options are
                PIP | PIPTASKBAR | TASKBAR
            The PIP mode will be displayed over an existing widget.  While the TASKBAR mode will be displayed
            as a standalone widget.
        is_dragging (bool): determines if this widget is currently in a drag/drop operation
        is_enlarged (bool): If there is currently an widget enlarged.
            Widgets are enlarged by the user hovering over them.  And closed
            be pressing "esc" or having the mouse exit the boundries of the widget.
        if_frozen (bool): Determines if events should be handled or not.
        is_overlay_displayed (bool): determines if the overlay is currently displayed.  If set to
            True, this will display the "acronym", if False, will display the delegate widget.
        enlarged_widget (QWidget): The widget that is currently enlarged
        overlay_widget (QWidget): Widget to overlay the popup over.  If none is specified,
            then this will return the main window.
        popup_widget (QWidget): The widget that is displayed if the enlarged widget
            has opened a subwidget (popup) menu.
        spacer_widget (QLabel): Widget that holds the space in the QSplitter where
            the currently enlarged widget normally lives.
        __temp_sizes (list): of ints, that are the sizes of the individual widgets.
            This is normally gotten through the "sizes()" call, but needs a temp one,
            for swapping the spacer widget in/out.
        __last_object_entered (AbstractPopupBarItemWidget): placeholder to determine the last object
            that was entered.  This is mainly used when enlarging widgets to ensure that the
            enlarged widget can be entered, as if the bounds are not great enough, you can enter
            the Main Viewer, thus closing the enlarged widget.
        widgets (list): Of AbstractPopupBarWidget widgets that are currently displayed.
            This does not include the currently enlarged widget
    """

    def __init__(self, parent=None, direction=attrs.EAST, orientation=Qt.Vertical, overlay_widget=None):
        super(AbstractPopupBarWidget, self).__init__(parent, orientation)

        self._is_frozen = False
        self._is_dragging = False
        self._is_enlarged = False
        self._is_overlay_enabled = True
        self._is_standalone = True
        self._enlarged_scale = 0.85
        self._enlarged_size = 500
        self._filepath = ""
        self._direction = direction
        self._display_mode = AbstractPopupBarDisplayWidget.STANDALONETASKBAR

        self._enlarged_widget = None
        self._createSpacerWidget()
        if overlay_widget:
            self._overlay_widget = overlay_widget

        self.setHandleWidth(15)
        self.__last_object_entered = None
        self.addDelayedSplitterMovedEvent("set_temp_sizes", self.__splitterMoved, 100)

    def _createSpacerWidget(self):
        """ Creates the invisible widget that will be swapped in/out when a widget is enlarged"""
        self._spacer_widget = QLabel("")
        self._spacer_widget.setParent(self.parent())
        self._spacer_widget.hide()
        self._spacer_widget.installEventFilter(self)
        self._spacer_widget.setAcceptDrops(True)

    """ PROPERTIES """
    def getTopMostPiPDisplay(self, widget, parent, pip_display_widget=None):
        """ Gets the top most pip display

        This should only be used if the widgets displayMode is set to PIP"""
        from .AbstractPiPWidget import AbstractPiPDisplayWidget
        if isinstance(widget, AbstractPiPDisplayWidget):
            pip_display_widget = widget

        if parent:
            return self.getTopMostPiPDisplay(widget.parent(), parent.parent(), pip_display_widget)

        if not parent:
            return pip_display_widget

    def direction(self):
        return self._direction

    def setDirection(self, direction):
        self._direction = direction
        if direction in [attrs.EAST, attrs.WEST]:
            self.setOrientation(Qt.Vertical)
        elif direction in [attrs.NORTH, attrs.SOUTH]:
            self.setOrientation(Qt.Horizontal)

    def displayMode(self):
        return self._display_mode

    def setDisplayMode(self, display_mode):
        self._display_mode = display_mode
        if display_mode == AbstractPopupBarDisplayWidget.PIP:
            self.setIsOverlayEnabled(False)
        if display_mode == AbstractPopupBarDisplayWidget.PIPTASKBAR:
            self.setIsOverlayEnabled(True)
        if display_mode == AbstractPopupBarDisplayWidget.STANDALONETASKBAR:
            self.setIsOverlayEnabled(True)

    def enlargedScale(self):
        return self._enlarged_scale

    def setEnlargedScale(self, enlarged_scale):
        self._enlarged_scale = enlarged_scale

    def enlargedSize(self):
        return self._enlarged_size

    def setEnlargedSize(self, enlarged_size):
        self._enlarged_size = enlarged_size

    def enlargedWidget(self):
        return self._enlarged_widget

    def setEnlargedWidget(self, widget):
        self._enlarged_widget = widget

    def filepath(self):
        return self._filepath

    def setFilepath(self, filepath):
        self._filepath = filepath

    def isDisplayNamesShown(self):
        return self._are_widget_names_shown

    def setIsDisplayNamesShown(self, enabled):
        self._are_widget_names_shown = enabled
        for widget in self.widgets():
            if enabled:
                widget.headerWidget().show()
            else:
                widget.headerWidget().hide()

    def isOverlayEnabled(self):
        return self._is_overlay_enabled

    def setIsOverlayEnabled(self, enabled):
        self._is_overlay_enabled = enabled
        self.setIsOverlayDisplayed(enabled)
        # if self.displayMode() == AbstractPopupBarDisplayWidget.PIP:
        #     self.setWidgetOverlayDisplay(True)
        # elif self.displayMode() == AbstractPopupBarDisplayWidget.PIPTASKBAR:
        #     self.setWidgetOverlayDisplay(False)
        # elif self.displayMode() == AbstractPopupBarDisplayWidget.STANDALONETASKBAR:
        #     self.setWidgetOverlayDisplay(False)

    def setWidgetOverlayDisplay(self, enabled):
        for widget in self.widgets():
            widget.setCurrentIndex(enabled)

    def setIsOverlayDisplayed(self, enabled):
        for widget in self.widgets():
            widget.setIsOverlayEnabled(enabled)
            if widget != self.enlargedWidget():
                widget.setIsOverlayDisplayed(enabled)

    def isDragging(self):
        return self.getTopMostPiPDisplay(self, self.parent()).isDragging()

    def setIsDragging(self, _pip_widget_is_dragging):
        if self.displayMode() == AbstractPopupBarDisplayWidget.PIP:
            self.getTopMostPiPDisplay(self, self.parent()).setIsDragging(_pip_widget_is_dragging)

    def isEnlarged(self):
        return self._is_enlarged

    def setIsEnlarged(self, enabled):
        self._is_enlarged = enabled

    def isFrozen(self):
        """ TODO no idea why I need this bypass
        Its for an initialization error..."""
        try:
            return self._is_frozen
        except AttributeError:
            return False

    def setIsFrozen(self, frozen):
        self._is_frozen = frozen

    def spacerWidget(self):
        return self._spacer_widget

    """ UTILS """
    # def _swappingToFastCheck(self, widget):
    #     if widget == self.widget(widget.index()): return True
    #     if not self.widget(widget.index()): return True
    #     if widget.parent() == self.widget(widget.index()).parent(): return True
    #
    #     return False

    def _resetSpacerWidget(self):
        """ Places the enlarged widget back into its original index.

        It does this by swapping out the spacer widget, with the currently
        enlarged widget.  This swap is done when closing the enlarged view."""
        widget = self.enlargedWidget()
        # preflight
        if not self.isEnlarged(): return
        if not widget: return
        if widget == self.widget(widget.index()): return True
        if not self.widget(widget.index()): return True
        if widget.parent() == self.widget(widget.index()).parent(): return True
        setAsTool(self.enlargedWidget(), False)

        # swap widgets
        self.replaceWidget(widget.index(), widget)
        self.spacerWidget().setParent(self.parent())
        self.widgets().append(widget)
        self.setSizes(self.__temp_sizes)

    def updateWidgetIndexes(self):
        """ Updates all of the widget indexes to their current position """
        # update indexes
        for i, widget in enumerate(self.widgets()):
            widget.setIndex(i)

    def settings(self):
        """ returns a dict of the current settings which can be set with updateSettings()"""
        return {
            "Enlarged Scale": self.enlargedScale(),
            "Enlarged Size": self.enlargedSize(),
            "Display Titles": self.isDisplayNamesShown(),
            "Direction": self.direction(),
            "Display Mode": self.displayMode(),
            "Overlay Text": self.currentWidget().title(),
            "Overlay Image": self.currentWidget().overlayImage(),
            "sizes": self.popupBarWidget().sizes()
        }

    def updateSettings(self, settings):
        """ Updates all of the settings from the settings provided.

        Note that you may need to call "resizePopupBar" afterwards in order
        to trigger a display update.

        Args:
            settings (dict): of {setting_name (str): value}
        """
        # self.setPiPScale(settings["PiP Scale"])
        self.setEnlargedScale(float(settings["Enlarged Scale"]))
        self.setEnlargedSize(float(settings["Enlarged Size"]))
        self.setIsDisplayNamesShown(settings["Display Titles"])
        self.setDirection(settings["Direction"])
        self.setDisplayMode(settings["Display Mode"])
        if "sizes" in list(settings.keys()):
            self.setSizes(settings["sizes"])

    def installDragMoveMonkeyPatch(self, widget):
        """ Monkey patch for bug with widgets that already have drag/drop enabled.

        This bypasses a bug/limitation of Qt, where EventFilters will not work on
        widgets that have already had their drag/drop enabled, and are probably
        exiting the event queue early.

        Args:
            widget (QWidget): to install pseudoevent on"""
        def _dragMoveEvent(event):
            widget._old_dragMoveEvent(event)
            self.__dragMoveEvent(getWidgetAncestor(widget, AbstractPopupBarItemWidget))
        if not hasattr(widget, "_old_dragMoveEvent"):
            widget._old_dragMoveEvent = widget.dragMoveEvent
        widget.dragMoveEvent = _dragMoveEvent

    def installDragEnterMonkeyPatch(self, widget):
        """ Monkey patch for bug with widgets that already have drag/drop enabled.

        This bypasses a bug/limitation of Qt, where EventFilters will not work on
        widgets that have already had their drag/drop enabled, and are probably
        exiting the event queue early.

        Args:
            widget (QWidget): to install pseudoevent on"""
        def _dragEnterEvent(event):
            # event.accept()
            widget._old_dragEnterEvent(event)
            self.__dragEnterEvent(getWidgetAncestor(widget, AbstractPopupBarItemWidget))
        if not hasattr(widget, "_old_dragEnterEvent"):
            widget._old_dragEnterEvent = widget.dragEnterEvent
        widget.dragEnterEvent = _dragEnterEvent

    """ EVENTS """
    def eventFilter(self, obj, event):
        """ Event handler for ALL AbstractPopupBarWidgetWIdgets

        Args:
            obj (AbstractPopupBarItemWidget):
            event (QEvent):

        Note:
            _is_frozen (bool): flag to determine if the UI should be frozen for updates
            _enlarged_object (AbstractPopupBarItemWidget): when exiting, this is the current object that has
                been enlarged for use.
            _entered_object (AbstractPopupBarItemWidget): when exiting, this is the object that is under the cursor
                if the user exits into the PopupBarWidget
                will be set to None
            _is_dragging (bool): determines if a drag operation is currently happening
            Signals:
                DragLeave:
                    isDragging holds attribute to determine if this widget is currently in a drag/drop operation.
                    This is reset when the user hover enters a new mini widget.  When the drag leave enters a
                    widget that is in the bounds of the enlargedWidget, it will do nothing.
        """
        # preflight
        if self.isFrozen(): return True
        if self.__eventFilterSpacerWidget(obj, event): return True

        if self.__dragEvent(obj, event): return True

        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Escape:
                self.closeEnlargedView()

        if event.type() == QEvent.Enter:
            """
            If the user exits on the first widget, or a widget that will be the enlarged widget,
            it will recurse back and enlarge itself.  This will block that recursion
            """
            self.__last_object_entered = obj
            #
            if self.isEnlarged():
                # Block from re-enlarging itself
                if self.enlargedWidget() == obj:
                    obj.setFocus()
                    return True
                elif obj.isMainViewerWidget():
                    return True
                # Has just enlarged the widget, but the cursor never entered it
                else:
                    # reset display label
                    self._resetSpacerWidget()
                    self.enlargedWidget().setIsOverlayDisplayed(True)
                    # reset widget to default params
                    self.setIsDragging(False)

                    # enlarge widget
                    self.enlargeWidget(obj)

            # Enlarge PopupBarWidget
            else:
                if not obj.isMainViewerWidget():
                    # reset widget to default params
                    self.setIsDragging(False)

                    # enlarge widget
                    self.enlargeWidget(obj)
            return True

        if event.type() == QEvent.Leave:
            # leaves over mini viewer widget
            """ Check to see if the cursor is over the object, because the drag
            events will trigger a leave event"""
            if not isCursorOverWidget(obj):
                if obj == self.enlargedWidget():
                    self.closeEnlargedView()
            return True

        return False

    def __eventFilterSpacerWidget(self, obj, event):
        """ Event Filter that is run when entering the spacer widget

        When the user enters/leaves a AbstractPopupBarItemWidget, if it exits from
        the self.spacerWidget() into the Main Viewer, it will auto close
        the enlarged widget.

        This will block that auto close, when leaving
        the spacer widget, and entering the Main Viewer Widget.

        Args:
            obj (AbstractPopupBarItemWidget)
            event (QEvent)
        """

        if event.type() in [QEvent.Enter, QEvent.DragEnter]:
            if obj == self.spacerWidget():
                # just entered spacer widget
                if obj == self.spacerWidget():
                    self.__last_object_entered = self.spacerWidget()
                    return True
            if obj.isMainViewerWidget():
                if self.__last_object_entered == self.spacerWidget():
                    return True
        else:
            return False

    def __dragMoveEvent(self, obj):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.AltModifier:
            obj.pipPopupBarWidget().closeEnlargedView()
            return True
        if not self.isDragging():
            self.setIsDragging(True)
            # self.setIsFrozen(True)
            obj.pipPopupBarWidget().closeEnlargedView()
            return True

    def __dragEnterEvent(self, obj):
        self.__last_object_entered = obj
        if self.isEnlarged():
            # Block from re-enlarging itself
            if self.enlargedWidget() == obj:
                return True
            # Has just enlarged the widget, but the cursor never entered it
            elif obj.isMainViewerWidget():
                self.closeEnlargedView()
            else:
                # reset display label
                self._resetSpacerWidget()

                # reset widget to default params
                self.setIsDragging(False)

                # enlarge widget
                self.enlargeWidget(obj)
        # Enlarge PopupBarWidget
        else:
            # enlarge widget
            if not obj.isMainViewerWidget():
                obj.pipPopupBarWidget().closeEnlargedView()
                self.enlargeWidget(obj)

    def __dragEvent(self, obj, event):
        """ Handles the event filter's Drag Leave Event
        Args:
            obj (QWidget):
            event (QEvent):
        """
        if event.type() == QEvent.DragEnter:
            self.__dragEnterEvent(obj)

        if event.type() == QEvent.DragMove:
            self.__dragMoveEvent(obj)

        # on drop, close and reset
        if event.type() == QEvent.Drop:
            self.setIsDragging(False)
            obj.pipPopupBarWidget().closeEnlargedView()

    def __splitterMoved(self, *args):
        """ Sets the __temp_sizes list after the splitter has finished moving

        This ensures that when the widget is enlarged, that if the widgets
        are resized, they will be restored back to the new sizes"""
        # prelight
        if not self.isEnlarged(): return

        # User finished dragging splitter
        self.__temp_sizes = self.sizes()

    def enlargeWidget(self, widget):
        """
        Enlarges the widget provided to be covering most of the main display area.

        Args:
            widget (AbstractPopupBarItemWidget): Widget to be enlarged
        """
        # preflight
        if not widget: return
        if not self.widget(widget.index()): return
        if self.widget(widget.index()) == self.spacerWidget(): return
        if self.widget(widget.index()).parent() == self.spacerWidget().parent(): return
        self.setIsFrozen(True)

        from .AbstractPiPWidget import AbstractPiPOrganizerWidget
        _organizer_widget = getWidgetAncestor(self, AbstractPiPOrganizerWidget)

        # set/get attrs
        self.setIsEnlarged(True)
        self.setEnlargedWidget(widget)
        self.__temp_sizes = self.sizes()

        # Swap spacer widget
        self.replaceWidget(widget.index(), self.spacerWidget())
        self.spacerWidget().show()

        # reparent widget, and set as tool
        """ As it will be displayed outside of the boundries of the current widget.
        It needs to be set as a tool, so incase it is displayed outside the boundries
        of the main application."""
        widget.setParent(self.parent())
        setAsTool(widget, True)
        widget.show()

        # enlarge widget based on the current display mode
        if self.displayMode() == AbstractPopupBarDisplayWidget.PIP:
            pos, width, height = self.__enlargePiPWidget()

        if self.displayMode() == AbstractPopupBarDisplayWidget.PIPTASKBAR:
            widget.setIsOverlayDisplayed(False)
            pos, width, height = self.__enlargePiPWidget()

        if self.displayMode() == AbstractPopupBarDisplayWidget.STANDALONETASKBAR:
            widget.setIsOverlayDisplayed(False)
            pos, width, height = self.__enlargeTaskbar()

        # move / resize enlarged widget
        widget.resize(int(width), int(height))
        widget.move(pos)

        #
        self.insertWidget(widget.index(), self._spacer_widget)
        self.setSizes(self.__temp_sizes)
        self.setIsFrozen(False)

    def __enlargeTaskbar(self):
        """ Popups the widget when it is in taskbar mode

        returns (QPoint, width, height)"""
        scale = self.enlargedScale()
        negative_space = 1 - scale
        half_neg_space = negative_space * 0.5

        if self.direction() in [attrs.NORTH, attrs.SOUTH]:
            width = self.width() - (self.width() * negative_space)
            height = self.enlargedSize()

            if self.direction() == attrs.NORTH:
                top_left = self.parent().mapToGlobal(self.geometry().topLeft())
                ypos = top_left.y() - height
                xpos = top_left.x() + (self.width() * half_neg_space)

            if self.direction() == attrs.SOUTH:
                bot_left = self.parent().mapToGlobal(self.geometry().bottomLeft())
                ypos = bot_left.y()
                xpos = bot_left.x() + (self.width() * half_neg_space)

        if self.direction() in [attrs.EAST, attrs.WEST]:
            height = self.height() - (self.height() * negative_space)
            width = self.enlargedSize()

            if self.direction() == attrs.EAST:

                top_right = self.parent().mapToGlobal(self.geometry().topRight())
                xpos = top_right.x()
                ypos = top_right.y() + (self.height() * half_neg_space)

            if self.direction() == attrs.WEST:
                top_left = self.parent().mapToGlobal(self.geometry().topLeft())
                xpos = top_left.x() - width
                ypos = top_left.y() + (self.height() * half_neg_space)

        return QPoint(xpos, ypos), width, height

    def __enlargePiPWidget(self):
        """ Popups up the widget when it is in PiPMode

        returns (QPoint, width, height)"""
        from .AbstractPiPWidget import AbstractPiPDisplayWidget

        # get attrs
        scale = self.enlargedScale()
        negative_space = 1 - scale
        half_neg_space = negative_space * 0.5

        # special case for only one mini viewer widget
        pip_display_widget = getWidgetAncestor(self, AbstractPiPDisplayWidget)
        offset = int(min(pip_display_widget.width(), pip_display_widget.height()) * half_neg_space)
        num_widgets = self.count()
        if num_widgets == 1:
            width = int(pip_display_widget.width() - offset)
            height = int(pip_display_widget.height() - offset)

            # NORTH WEST
            if self.direction() == attrs.SOUTH:
                xpos = 0
                ypos = 0
            # SOUTH EAST
            if self.direction() == attrs.NORTH:
                xpos = offset
                ypos = offset
            # NORTH EAST
            if self.direction() == attrs.WEST:
                xpos = offset
                ypos = 0
            # SOUTH WEST
            if self.direction() == attrs.EAST:
                xpos = 0
                ypos = offset

        # if there are 2 or more mini viewer widgets
        if 1 < num_widgets:
            # get widget position / size
            if self.direction() in [attrs.EAST, attrs.WEST]:
                height = int(pip_display_widget.height() - (offset * 2))
                ypos = int(offset)
                width = int(pip_display_widget.width() - offset - self.width())
                if self.direction() == attrs.WEST:
                    xpos = offset
                if self.direction() == attrs.EAST:
                    xpos = self.width()

            if self.direction() in [attrs.NORTH, attrs.SOUTH]:
                xpos = int(pip_display_widget.width() * half_neg_space)
                width = int(pip_display_widget.width() * scale)
                height = int(
                    pip_display_widget.height()
                    - self.height()
                    - offset)
                if self.direction() == attrs.SOUTH:
                    ypos = self.height()
                if self.direction() == attrs.NORTH:
                    ypos = offset

        return self.parent().mapToGlobal(QPoint(xpos, ypos)), width, height

    def closeEnlargedView(self):
        """Closes the enlarged viewer, and returns it back to normal PiP mode"""

        # preflight
        if not self.isEnlarged(): return
        if self.enlargedWidget().isMainViewerWidget(): return

        # setup attrs
        self.setIsFrozen(True)
        widget_under_cursor = getWidgetUnderCursor()

        # exitted out of widget
        if not widget_under_cursor:
            self._resetSpacerWidget()
            self.setIsEnlarged(False)
            if self.displayMode() in AbstractPopupBarDisplayWidget.TASKBARS:
                self.enlargedWidget().setIsOverlayDisplayed(True)
            else:
                self.enlargedWidget().setIsOverlayDisplayed(False)

        # exited over the mini viewer
        elif isWidgetDescendantOf(widget_under_cursor, widget_under_cursor.parent(), self):
            if widget_under_cursor == self._spacer_widget:
                pass
            elif isinstance(widget_under_cursor, QSplitterHandle):
                pass
            # exit over valid option
            else:
                # reset display label
                self.__temp_sizes = self.sizes()

                self._resetSpacerWidget()

                """ Enable different display modes based off of the type of widget.
                
                Need to check if this has exitted over a PiPWidget, as if it has, this can
                cause issues determining which widget to resolve due to recursion."""
                # Todo might cause recursion later
                from .AbstractPiPWidget import AbstractPiPDisplayWidget, PiPMainViewer
                # enlarge mini viewer
                display_widget = getWidgetAncestor(widget_under_cursor, AbstractPiPDisplayWidget)
                popup_bar_widget = getWidgetAncestor(widget_under_cursor, AbstractPopupBarItemWidget)
                # taskbar
                if not display_widget:
                    self.enlargedWidget().setIsOverlayDisplayed(True)
                    self.enlargeWidget(popup_bar_widget)
                # pip
                elif display_widget.isPopupBarWidget():
                    # exit over recursive mini viewer
                    if isinstance(popup_bar_widget.parent(), AbstractPiPDisplayWidget):
                        display_widget.popupBarWidget().closeEnlargedView()
                        self.enlargeWidget(getWidgetAncestor(display_widget, AbstractPopupBarItemWidget))

                    # exit over recursive main viewer
                    elif isinstance(popup_bar_widget.parent(), PiPMainViewer):
                        self.enlargeWidget(getWidgetAncestor(display_widget, AbstractPopupBarItemWidget))
                else:
                    # exit over normal widget
                    self.enlargedWidget().setIsOverlayDisplayed(True)
                    self.enlargeWidget(popup_bar_widget)

        # exited over main viewer
        else:
            # reset display label
            self._resetSpacerWidget()
            self.setIsEnlarged(False)
            self.enlargedWidget().setIsOverlayDisplayed(True)

        # self.setIsFrozen(False)
        # show mini viewer widgets
        # if self.enlargedWidget().isPiPWidget():
        #     # pip_display_widget = getWidgetAncestor(self.enlargedWidget(), AbstractPiPDisplayWidget)
        #     self.enlargedWidget().delegateWidget().setIsPopupBarShown(False)

        """ Unfreezing as a delayed event to help to avoid the segfaults that occur
        when PyQt tries to do things to fast..."""
        # self.setEnlargedWidget(None)

        runDelayedEvent(self, self.unfreeze, delay_amount=10)

    def unfreeze(self):
        self.setIsFrozen(False)

    """ WIDGETS """
    def addWidget(self, widget, name="", is_pip_widget=False, index=0):
        if widget == self.spacerWidget():
            return
        if not isinstance(widget, AbstractPopupBarItemWidget):
            widget = self.createNewWidget(widget, index=index, is_pip_widget=is_pip_widget, name=name)
        if isinstance(widget, AbstractPopupBarItemWidget):
            widget.installEventFilter(self)
            self.installDragEnterMonkeyPatch(widget.delegateWidget())
            self.installDragMoveMonkeyPatch(widget.delegateWidget())
            widget.delegateWidget().setAcceptDrops(True)
            return QSplitter.addWidget(self, widget)
        else:
            print("{widget_type} is not valid.".format(widget_type=type(widget)))
            return

    def createNewWidget(self, widget, name="", is_pip_widget=False, index=0):
        """
        Creates a new widget in the mini widget.  This is only when a new widget needs to be instantiated.

        Args:
            is_pip_widget (bool): determines if this is a PiPWidget
            widget:
            name:

        Returns (AbstractPopupBarItemWidget):
        """
        mini_widget = AbstractPopupBarItemWidget(self, direction=Qt.Vertical, delegate_widget=widget, is_pip_widget=is_pip_widget, name=name)

        mini_widget.setIsOverlayEnabled(self.isOverlayEnabled())
        if self.displayMode() == AbstractPopupBarDisplayWidget.PIP:
            mini_widget.setIsOverlayDisplayed(self.isOverlayEnabled())
        elif self.displayMode() in [AbstractPopupBarDisplayWidget.PIPTASKBAR, AbstractPopupBarDisplayWidget.STANDALONETASKBAR]:
            pass
        # self.installDragEnterMonkeyPatch(mini_widget.delegateWidget())
        # self.installDragLeaveMonkeyPatch(mini_widget.delegateWidget())
        # self.installDragMoveMonkeyPatch(mini_widget.delegateWidget())
        mini_widget.installEventFilter(self)
        mini_widget.delegateWidget().setAcceptDrops(True)

        self.insertWidget(index, mini_widget)

        self.updateWidgetIndexes()
        return mini_widget

    def insertWidget(self, index, widget, name="", is_pip_widget=False):
        if widget == self.spacerWidget():
            return
        if not isinstance(widget, AbstractPopupBarItemWidget):
            widget = self.createNewWidget(widget, index=index, is_pip_widget=is_pip_widget, name=name)
        if isinstance(widget, AbstractPopupBarItemWidget):
            widget.installEventFilter(self)
            self.installDragEnterMonkeyPatch(widget.delegateWidget())
            self.installDragMoveMonkeyPatch(widget.delegateWidget())
            widget.delegateWidget().setAcceptDrops(True)
            return QSplitter.insertWidget(self, index, widget)

        else:
            print ("{widget_type} is not valid.".format(widget_type=type(widget)))
            return

    def removeWidget(self, widget):
        if widget:
            widget.setParent(None)
            if not isinstance(widget, QSplitterHandle):
                widget.removeEventFilter(self)

    def removeAllWidgets(self):
        for i in reversed(range(self.count())):
            self.widget(i).removeEventFilter(self)
            self.widget(i).setParent(None)

    def widgets(self):
        _widgets = []
        for i in range(self.count()):
            widget = self.widget(i)
            if isinstance(widget, AbstractPopupBarItemWidget):
                _widgets.append(widget)
        return _widgets


class AbstractPopupBarItemWidget(AbstractOverlayInputWidget):
    """
    One PiP Widget that is displayed in the AbstractPopupBarWidget

    Args:
        acronym (string): text to be displayed if the overlay is enabled
        delegate_widget (QWidget): Widget to be used as popup

    Attributes:
        is_overlay_enabled (bool): determines if the overlay is displayed.  This is used with
            the PopupBar to show text instead of the widget to the user.
        is_overlay_displayed (bool): determines if the overlay is currently displayed.  If set to
            True, this will display the "acronym", if False, will display the delegate widget.
        is_pip_widget (bool): determines if this widgets delegate widget is inherited from the
            AbstractPiPDisplayWidget.  This is for handling recursive viewing
        Overlay Image (str): Relative path on disk to file path.

            This can start with a ../ to denote that the image is located in the same directory
                as the current PiPWidget json file
        index (int): current index in model
        item (AbstractPopupBarWidgetOrganizerItem)
    """
    def __init__(
        self,
        parent=None,
        name="None",
        direction=Qt.Horizontal,
        delegate_widget=None,
        is_pip_widget=False,
        is_overlay_enabled=True,
        acronym=None
    ):
        if not acronym:
            acronym = name
        super(AbstractPopupBarItemWidget, self).__init__(parent, title=acronym)

        self._is_overlay_enabled = is_overlay_enabled
        self._is_pip_widget = is_pip_widget
        self._is_main_viewer_widget = False
        self._name = name
        self._overlay_image = ""
        self._index = 0

        # create delegate widget
        delegate_widget = AbstractLabelledInputWidget(
            self, name=name, direction=direction, delegate_widget=delegate_widget)

        self.setDelegateWidget(delegate_widget)

        # Todo find all of these handlers and remove them?
        # this is just a forced override for now
        # disable editable header
        delegate_widget.viewWidget().setDisplayMode(AbstractOverlayInputWidget.DISABLED)
        # self.setDisplayMode(AbstractOverlayInputWidget.DISABLED)
        self.setAcceptDrops(True)

    # def updateItemDisplayName(self, widget, value):
    #     """
    #     Updates the display name of this label
    #     Args:
    #         widget:
    #         value:
    #     """
    #     self.item().columnData()['name'] = value
    #     self.headerWidget().viewWidget().hideDelegate()
    #     self.headerWidget().setName(value)

    """ WIDGETS """
    # def mainWidget(self):
    #     return self._main_widget
    #
    def headerWidget(self):
        return self.delegateWidget().viewWidget()
    #
    # def delegateWidget(self):
    #     return self.mainWidget().delegateWidget()

    def pipPopupBarWidget(self):
        from .AbstractPiPWidget import AbstractPiPDisplayWidget
        return getWidgetAncestor(self, AbstractPiPDisplayWidget).popupBarWidget()

    """ PROPERTIES """
    def isPiPWidget(self):
        return self._is_pip_widget

    def setIsPiPWidget(self, is_pip_widget):
        self._is_pip_widget = is_pip_widget

    def isOverlayEnabled(self):
        return self._is_overlay_enabled

    def setIsOverlayEnabled(self, enabled):
        self._is_overlay_enabled = enabled

    def isOverlayDisplayed(self):
        return self.isOverlayDisplayed()

    def setIsOverlayDisplayed(self, enabled):
        """ Sets if the overlay is currently displayed or not.


        """
        if self.isOverlayEnabled():
            self._is_overlay_displayed = enabled
            self.setCurrentIndex(not enabled)
        else:
            self.setCurrentIndex(1)

    def isMainViewerWidget(self):
        return self._is_main_viewer_widget

    def setIsMainViewerWidget(self, _is_main_viewer_widget):
        self._is_main_viewer_widget = _is_main_viewer_widget

    def item(self):
        return self._item

    def setItem(self, item):
        self._item = item

    def index(self):
        return self._index

    def setIndex(self, index):
        self._index = index

    def name(self):
        return self._name
        # return self.item().columnData()["name"]

    def setName(self, name):
        self._name = name
        self.item().columnData()["name"] = name
        self.headerWidget().viewWidget().setText(name)

    # setTitle
    # setImage

    # def overlayName(self):
    #     return self._overlay_name
    #
    # def setOverlayName(self, overlay_name):
    #     self._overlay_name = overlay_name
    #
    def overlayImage(self):
        return self._overlay_image

    def setOverlayImage(self, image_path):
        # get current directory
        self._overlay_image = image_path
        if image_path:
            if image_path.startswith("../"):
                popup_bar_widget = getWidgetAncestor(self, AbstractPopupBarWidget)
                if popup_bar_widget:
                    filepath = "/".join(popup_bar_widget.filepath().split("/")[:-1])
                else:
                    from .AbstractPiPWidget import AbstractPiPDisplayWidget
                    main_widget = getWidgetAncestor(self, AbstractPiPDisplayWidget)
                    filepath = "/".join(main_widget.filepath().split("/")[:-1])
                image_path = image_path.replace("../", filepath + "/")
        self.setImage(image_path)


class AbstractPopupBarDisplayWidget(QWidget):
    """ Abstract class for displaying all PopupWidget types (PIP | PIPTASKBAR | TASKBAR)

    Note:
        This is acting as an abstraction layer right now.
        Todo: need to clean up the underlying API for these calls?

    Attributes:
        display_mode (AbstractPopupBarDisplayWidget.DISPLAYMODE): what mode should
            be displayed
        display_widget (AbstractPopupBarWidget | AbstractPiPDisplayWidget): The current popup widget
        popup_bar_widget (AbstractPopupBarWidget):
        widgets (list): of AbstractPopupBarItemWidget's.
    """

    PIP = "PIP"
    PIPTASKBAR = "PIP TASKBAR"
    STANDALONETASKBAR = "STANDALONE TASKBAR"
    TASKBARS = [PIPTASKBAR, STANDALONETASKBAR]
    PIPDISPLAYS = [PIP, PIPTASKBAR]

    def __init__(self, parent=None, display_mode=STANDALONETASKBAR):
        super(AbstractPopupBarDisplayWidget, self).__init__(parent)

        # setup default attrs
        self._display_widget = AbstractPopupBarWidget()
        self._popup_bar_widget = self._display_widget
        self._widgets = []

        # setup layout
        QVBoxLayout(self)
        self.layout().addWidget(self._display_widget)

        self.setContentsMargins(0, 0, 0, 0)
        self.layout().setContentsMargins(0, 0, 0, 0)

        # set display mode
        """ Needs to be set after all of the layout/attrs are created
         as it will need to call these to set the display mode"""
        self.setDisplayMode(display_mode)

    """ WIDGETS """
    def displayWidget(self):
        return self._display_widget

    def popupBarWidget(self):
        return self._popup_bar_widget

    def widgets(self):
        return self.displayWidget().widgets()
        # return self._widgets

    """ UTILS """
    def addWidget(self, widget, name="", is_pip_widget=False, index=0):
        # Setup attrs for creation
        """ Needs to do this as different modes will require different attributes"""
        if self.displayMode() in AbstractPopupBarDisplayWidget.PIPDISPLAYS:
            if self.displayMode() == AbstractPopupBarDisplayWidget.PIP:
                is_overlay_enabled = False
            if self.displayMode() == AbstractPopupBarDisplayWidget.PIPTASKBAR:
                is_overlay_enabled = True
        elif self.displayMode() == AbstractPopupBarDisplayWidget.STANDALONETASKBAR:
            is_overlay_enabled = True

        # create widget if it isn't a popup bar item
        if not isinstance(widget, AbstractPopupBarItemWidget):
            widget = self.displayWidget().createNewWidget(
                widget, is_pip_widget=is_pip_widget, name=name, index=index)
        else:
            # todo direct add into display widget
            self.displayWidget().addWidget(widget)
            pass
        return widget
        # self.widgets().append(widget)

    def insertWidget(self, index, widget, name="", is_pip_widget=False):
        self.addWidget(widget, index=index, name=name, is_pip_widget=is_pip_widget)

    def removeAllWidgets(self):
        self.displayWidget().removeAllWidgets()

    def numWidgets(self):
        return self.popupBarWidget().count()

    def resizePopupBar(self):
        if self.displayMode() in AbstractPopupBarDisplayWidget.PIPDISPLAYS:
            self.displayWidget().resizePopupBar()

    """ WIDGETS (CREATE) """
    def createWidgetFromConstructorCode(self, constructor_code):
        """ Creates a new widget from the code provided

        Note:
            Duplicate code from AbstractPiPWidget.AbstractPiPDisplayWidget
        Args:
            self (QWidget): to be passed as arg to constructor.
                This is imported as the local var "self"
            constructor_code (code):

        Returns (QWidget): created by code"""
        loc = {}
        loc['self'] = self

        exec(compile(constructor_code, "constructor_code", "exec"), globals(), loc)
        widget = loc['widget']
        return widget

    def createNewWidget(self, widget, name="", resize_popup_bar=True, is_pip_widget=False, index=0):
        """ Creates a new widget

        Args:
            widget (QWidget):
            name (str):
            resize_popup_bar (bool): Determines if the Popupbar should be resized
                only valid if displayMode() is set to PIPDISPLAYS
            is_pip_widget (bool): Determines if this is a PiPWidget
                only valid if displayMode() is set to STANDALONETASKBAR
            index (int): The index to insert the widget at
                only valid if displayMode() is set to STANDALONETASKBAR

        Returns (AbstractPopupBarItemWidget):

        """
        if self.displayMode() == AbstractPopupBarDisplayWidget.STANDALONETASKBAR:
            return self.displayWidget().createNewWidget(widget, name=name, is_pip_widget=is_pip_widget, index=index)
        elif self.displayMode() in AbstractPopupBarDisplayWidget.PIPDISPLAYS:
            return self.displayWidget().createNewWidget(widget, name=name, resize_popup_bar=resize_popup_bar)

    """ LOAD (file)"""
    def loadPopupDisplayFromFile(self, filepath, pip_name, organizer=False):
        """ Loads the PiPWidget from the file/name provided

        Args:
            filepath (str): path on disk to pipfile to load
            pip_name (str): name of pip in filepath to load
            organizer (bool): determines if this is loading from the organizer widget
        """
        data = getJSONData(filepath)[pip_name]
        display_mode = data["settings"]["Display Mode"]
        self.setDisplayMode(display_mode)
        self.removeAllWidgets()
        # load stand alone taskbar
        if display_mode == AbstractPopupBarDisplayWidget.STANDALONETASKBAR:
            self.__loadStandaloneTaskbar(data, organizer=organizer)

        # load pip/piptaskbar
        elif display_mode in AbstractPopupBarDisplayWidget.PIPDISPLAYS:
            self.__loadPiPWidget(data, filepath, pip_name, organizer=organizer)

        # load settings
        self.popupBarWidget().updateSettings(data["settings"])

    def __loadStandaloneTaskbar(self, data, organizer=False):
        """ Loads a standalone taskbar from the data provided

        Args:
            data (dict): An individual PopupBar widgets data located in the
                JSON file.
                    ie: getJSONData(filepath)[pip_name]"""
        # load widgets
        for widget_name, widget_data in data["widgets"].items():
            widget = self.createWidgetFromConstructorCode(widget_data["code"])
            widget = self.addWidget(widget, name=widget_name)

            # create popup bar items
            if organizer:
                from .AbstractPiPWidget import AbstractPiPOrganizerWidget
                organizer_widget = getWidgetAncestor(self, AbstractPiPOrganizerWidget)
                index = organizer_widget.popupBarOrganizerWidget().model().insertNewIndex(0, name=widget_name)

                item = index.internalPointer()
                item.setWidget(widget)
                item.setConstructorCode(widget_data["code"])

                # widget.setIndex(0)
                widget.setItem(item)

                # update indexes
                organizer_widget.popupBarWidget().updateWidgetIndexes()
            # todo create organizer widgets

    def __loadPiPWidget(self, data, filepath, pip_name, organizer=False):
        """ Loads a PiP Widget from the data provided

        Args:
            data (dict): An individual PopupBar widgets data located in the
                JSON file.
                    ie: getJSONData(filepath)[pip_name]
            filepath (str): path on disk to JSON file
            pip_name (str: name of PiPWidget to load
            organizer (bool): determines if this is loading from the organizer widget"""
        self.displayWidget().loadPiPWidgetFromFile(filepath, pip_name, organizer=organizer)

    """ PROPERTIES"""
    def direction(self):
        return self.popupBarWidget().direction()

    def setDirection(self, direction):
        self.popupBarWidget().setDirection(direction)

    def displayMode(self):
        return self.popupBarWidget().displayMode()

    def setDisplayMode(self, display_mode):
        """ Sets the display mode to the one provided

        Args:
            display_mode (AbstractPopupBarDisplayWidget.DISPLAY_MODE):"""
        # preflight
        if display_mode not in [
            AbstractPopupBarDisplayWidget.PIP,
            AbstractPopupBarDisplayWidget.PIPTASKBAR,
            AbstractPopupBarDisplayWidget.STANDALONETASKBAR
        ]:
            print(display_mode, "is not a valid option.")
            return
        if display_mode == self.displayMode(): return

        from .AbstractPiPWidget import AbstractPiPDisplayWidget

        # create new display widget
        if display_mode in [AbstractPopupBarDisplayWidget.PIPTASKBAR, AbstractPopupBarDisplayWidget.PIP]:
            _display_widget = AbstractPiPDisplayWidget()
            _popup_bar_widget = _display_widget.popupBarWidget()
            _display_widget.setPopupBarWidget(_popup_bar_widget)
        elif display_mode == AbstractPopupBarDisplayWidget.STANDALONETASKBAR:
            _display_widget = AbstractPopupBarWidget()
            _popup_bar_widget = _display_widget

        # update
        if display_mode == AbstractPopupBarDisplayWidget.PIP:
            _popup_bar_widget.setIsOverlayEnabled(False)
        elif display_mode in AbstractPopupBarDisplayWidget.TASKBARS:
            _popup_bar_widget.setIsOverlayEnabled(True)

        self.layout().addWidget(_display_widget)

        # reparent existing widgets
        for widget in reversed(self.widgets()):
            _display_widget.addWidget(widget)
        self.displayWidget().setParent(None)

        # update attrs
        self._display_widget = _display_widget
        self._popup_bar_widget = _popup_bar_widget
        self._popup_bar_widget.setDisplayMode(display_mode)

    def enlargedScale(self):
        return self.popupBarWidget().enlargedScale()

    def setEnlargedScale(self, _enlarged_scale):
        self.popupBarWidget().setEnlargedScale(_enlarged_scale)

    def enlargedSize(self):
        return self.popupBarWidget().enlargedSize()

    def setEnlargedSize(self, enlarged_size):
        self.popupBarWidget().setEnlargedSize(enlarged_size)

    def filepath(self):
        return self.popupBarWidget().filepath()

    def setFilepath(self, filepath):
        self.popupBarWidget().setFilepath(filepath)

    def isDisplayNamesShown(self):
        return self.popupBarWidget().isDisplayNamesShown()

    def setIsDisplayNamesShown(self, enabled):
        self.popupBarWidget().setIsDisplayNamesShown(enabled)
        for widget in self.widgets():
            if enabled:
                widget.headerWidget().show()
            else:
                widget.headerWidget().hide()

    """ PROPERTIES (PIP)"""
    def pipScale(self):
        if self.displayMode() in AbstractPopupBarDisplayWidget.PIPDISPLAYS:
            return self.displayWidget().pipScale()

    def setPiPScale(self, pip_scale):
        if self.displayMode() in AbstractPopupBarDisplayWidget.PIPDISPLAYS:
            self.displayWidget().setPiPScale(pip_scale)

    def taskbarSize(self):
        if self.displayMode() in AbstractPopupBarDisplayWidget.PIPDISPLAYS:
            return self.displayWidget().taskbarSize()

    def setTaskbarSize(self, taskbar_size):
        if self.displayMode() in AbstractPopupBarDisplayWidget.PIPDISPLAYS:
            self.displayWidget().setTaskbarSize(taskbar_size)

    def currentWidget(self):
        if self.displayMode() in AbstractPopupBarDisplayWidget.PIPDISPLAYS:
            return self.displayWidget().currentWidget()

    def setCurrentWidget(self, current_widget):
        if self.displayMode() in AbstractPopupBarDisplayWidget.PIPDISPLAYS:
            self.displayWidget().setCurrentWidget(current_widget)

    def previousWidget(self):
        if self.displayMode() in AbstractPopupBarDisplayWidget.PIPDISPLAYS:
            return self.displayWidget().previousWidget()

    def setPreviousWidget(self, previous_widget):
        if self.displayMode() in AbstractPopupBarDisplayWidget.PIPDISPLAYS:
            self.displayWidget().setPreviousWidget(previous_widget)


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication, QLabel, QHBoxLayout
    from cgwidgets.utils import centerWidgetOnCursor, setAsAlwaysOnTop, centerWidgetOnScreen

    app = QApplication(sys.argv)

    # create popup bar
    popup_bar_widget = AbstractPopupBarWidget()
    for x in range(3):
        label = QLabel(str(x))
        popup_bar_widget.createNewWidget(label, name=str(x))

    # create main widget
    main_widget = QWidget()
    main_layout = QVBoxLayout(main_widget)
    other_widget = QLabel("Something Else")
    main_layout.addWidget(popup_bar_widget)
    main_layout.addWidget(other_widget)

    # set popup bar widget
    popup_bar_widget.setFixedWidth(50)
    popup_bar_widget.setDisplayMode(AbstractPopupBarDisplayWidget.PIP)
    # popup_bar_widget.setDirection(attrs.SOUTH)

    # show widget
    setAsAlwaysOnTop(main_widget)
    main_widget.show()
    centerWidgetOnScreen(main_widget)


    sys.exit(app.exec_())

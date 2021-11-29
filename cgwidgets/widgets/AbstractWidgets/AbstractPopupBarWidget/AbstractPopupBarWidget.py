""" Todo:
        *   Check multiple recursion...
                Specifically in STANDALONE TASKBAR
        *   Enable swapping of STANDALONE TASKBAR when in PiPView (1989, 23)
        *   Drag Leave causing segfaults with STANDALONE TASKBAR (538, 11)
        *   Delays when enlarging (584, 11)
        *   AbstractPiPDisplayWidget change is_standalone to is_organizer (1513, 15)
"""
import json
from collections import OrderedDict
import os

from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSplitter, QSplitterHandle, QApplication)
from qtpy.QtCore import QEvent, Qt, QPoint

from cgwidgets.utils import (
    isWidgetDescendantOf,
    isCursorOverWidget,
    getWidgetAncestor,
    getJSONData,
    getWidgetUnderCursor,
    runDelayedEvent,
    setAsTool,
    installResizeEventFinishedEvent)

from cgwidgets.settings import attrs

from cgwidgets.widgets.AbstractWidgets.AbstractLabelledInputWidget import AbstractLabelledInputWidget
from cgwidgets.widgets.AbstractWidgets.AbstractOverlayInputWidget import AbstractOverlayInputWidget


from cgwidgets.widgets import (AbstractSplitterWidget)

import time


class AbstractPopupBarWidget(AbstractSplitterWidget):
    """
    Widget that contains all of the PiPWidgets.

    This widget is an overlay of the MainWidget, and sits at a parallel hierarchy to the PiPMainViewer

    Attributes:
        are_widget_names_shown (bool): Determines if the titles are shown above the items
        current_widget (AbstractPopupBarItemWidget): Current widget being displayed full screen in this widget.
            This is only active if the display mode is set to:
                PIP | PIPTASKBAR
        direction (attrs.DIRECTION): direction that the popup will be displayed on
        display_mode (AbstractPopupBarWidget.TYPE): Determines what type of widget this should be displayed as
            valid options are
                PIP | PIPTASKBAR | TASKBAR
            The PIP mode will be displayed over an existing widget.  While the TASKBAR mode will be displayed
            as a standalone widget.
        enlarged_offset (float): the amount of offset (pixels) displayed when the widget is enlarged and the
            displayMode() is set to STANDALONETASKBAR
        enlarged_scale (float): the amount of space (percent) the widget takes up when it is enlarged and the
            displayMode() is set to a PIP DISPLAY (PIP | PIPTASKBAR)
        enlarged_size (float): How far the widget extends (pixels) when the widget is enlarged and the
            displayMode() is set to STANDALONETASKBAR
        is_dragging (bool): determines if this widget is currently in a drag/drop operation
        is_enlarged (bool): If there is currently an widget enlarged.
            Widgets are enlarged by the user hovering over them.  And closed
            be pressing "esc" or having the mouse exit the boundries of the widget.
        if_frozen (bool): Determines if events should be handled or not.
        is_overlay_enabled (bool): determines if the overlay is currently displayed.  If set to
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
        self._are_widget_names_shown = True
        self._is_standalone = True
        self._enlarged_scale = 0.85
        self._enlarged_size = 500
        self._enlarged_offset = 50.0
        self._filepath = ""
        self._pip_name = ""
        self._direction = direction
        self._display_mode = AbstractPopupBarDisplayWidget.STANDALONETASKBAR
        self._current_widget = None
        self._enlarged_widget = None
        # self._is_popup_enabled = False

        self.__createSpacerWidget()
        if overlay_widget:
            self._overlay_widget = overlay_widget

        self.setHandleWidth(15)
        self.__last_object_entered = None
        self.addDelayedSplitterMovedEvent("set_temp_sizes", self.__splitterMoved, 100)

    def __createSpacerWidget(self):
        """ Creates the invisible widget that will be swapped in/out when a widget is enlarged"""
        self._spacer_widget = QLabel("")
        self._spacer_widget.setParent(self.parent())
        self._spacer_widget.hide()
        self._spacer_widget.installEventFilter(self)
        self._spacer_widget.setAcceptDrops(True)

    """ PROPERTIES """
    def getTopMostPopupBarDisplay(self, widget, parent, pip_display_widget=None):
        """ Gets the top most PopupBarDisplay

        This should only be used if the widgets displayMode is set to PIP"""
        if isinstance(widget, AbstractPopupBarDisplayWidget):
            pip_display_widget = widget

        if parent:
            return self.getTopMostPopupBarDisplay(widget.parent(), parent.parent(), pip_display_widget)

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
            if self.currentWidget():
                self.currentWidget().setIsOverlayDisplayed(False)
        if display_mode == AbstractPopupBarDisplayWidget.STANDALONETASKBAR:
            self.setIsOverlayEnabled(True)

    def currentWidget(self):
        if self.displayMode() in AbstractPopupBarDisplayWidget.PIPDISPLAYS:
            return self._current_widget
        return None

    def setCurrentWidget(self, current_widget):
        self._current_widget = current_widget

    def enlargedOffset(self):
        return self._enlarged_offset

    def setEnlargedOffset(self, _enlarged_offset):
        self._enlarged_offset = _enlarged_offset

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

    def pipName(self):
        return self._pip_name

    def setPiPName(self, pip_name):
        self._pip_name = pip_name

    def isDisplayNamesShown(self):
        return self._are_widget_names_shown

    def setIsDisplayNamesShown(self, enabled):
        self._are_widget_names_shown = enabled
        for widget in self.widgets():
            widget.setIsDisplayNameShown(enabled)

        if isinstance(self.parent(), AbstractPiPDisplayWidget):
            if self.parent().currentWidget():
                self.parent().currentWidget().setIsDisplayNameShown(False)

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

    # def setWidgetOverlayDisplay(self, enabled):
    #     """ Sets all of the widgets to either show or hide the overlay
    #
    #     Args:
    #         enabled (bool): If True, will show the delegate, if False, will show the overlay"""
    #     for widget in self.widgets():
    #         widget.setCurrentIndex(enabled)

    def setIsOverlayDisplayed(self, enabled):
        """ Determines if the overlay is displayed for each child widget

        Args:
            enabled (bool): If True, will show the overlays, if False, will show the delegates.

        """
        for widget in self.widgets():
            widget.setIsOverlayEnabled(enabled)
            if widget != self.enlargedWidget():
                widget.setIsOverlayDisplayed(enabled)

    def isDragging(self):
        return self.getTopMostPopupBarDisplay(self, self.parent()).isDragging()

    def setIsDragging(self, _pip_widget_is_dragging):
        if self.displayMode() == AbstractPopupBarDisplayWidget.PIP:
            self.getTopMostPopupBarDisplay(self, self.parent()).setIsDragging(_pip_widget_is_dragging)

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

    def isPopupEnabled(self):
        #return self._is_popup_enabled
        return self.getTopMostPopupBarDisplay(self, self.parent()).isPopupEnabled()

    def setIsPopupEnabled(self, _is_popup_enabled):
        #self._is_popup_enabled = _is_popup_enabled
        self.getTopMostPopupBarDisplay(self, self.parent()).setIsPopupEnabled(_is_popup_enabled)

    def spacerWidget(self):
        return self._spacer_widget

    """ UTILS """
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
        setAsTool(widget, False)
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
        if self.currentWidget():
            overlay_text = self.currentWidget().title()
            overlay_image = self.currentWidget().overlayImage()
        else:
            overlay_text = ""
            overlay_image = ""
        # try:
        #     sizes = self.sizes()
        # except AttributeError:
        #     sizes = []
        return {
            "Enlarged Scale": self.enlargedScale(),
            "Enlarged Size": self.enlargedSize(),
            "Display Titles": self.isDisplayNamesShown(),
            "Direction": self.direction(),
            "Display Mode": self.displayMode(),
            "Overlay Text": overlay_text,
            "Overlay Image": overlay_image,
            "sizes": self.sizes()
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
        self.setDisplayMode(settings["Display Mode"])
        self.setIsDisplayNamesShown(settings["Display Titles"])
        self.setDirection(settings["Direction"])
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
            #event.accept()
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

        if self.__popupEvent(obj, event): return True

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
                elif obj.isCurrentWidget():
                    return True
                # Has just enlarged the widget, but the cursor never entered it
                else:
                    # reset display label
                    self._resetSpacerWidget()
                    """ Need to reset the display here, or somewhere to handle
                    the enter/leave dynamic nature."""
                    self.enlargedWidget().setIsOverlayDisplayed(True)
                    # reset widget to default params
                    self.setIsDragging(False)

                    # enlarge widget
                    self.enlargeWidget(obj)

            # Enlarge PopupBarWidget
            else:
                if not obj.isCurrentWidget():
                    # reset widget to default params
                    self.setIsDragging(False)

                    # enlarge widget
                    self.enlargeWidget(obj)

            return True

        if event.type() == QEvent.Leave:
            if not isCursorOverWidget(obj):
                if obj != self.currentWidget():
                    widget_under_cursor = getWidgetUnderCursor()
                    if widget_under_cursor != self.spacerWidget():
                        # left widget, but cursor is under another widget
                        if widget_under_cursor:
                            if not isWidgetDescendantOf(widget_under_cursor, widget_under_cursor.parent(), obj):
                                if obj == self.enlargedWidget():
                                    self.closeEnlargedView()

                        # left widget and entire application
                        else:
                            if obj == self.enlargedWidget():
                                self.closeEnlargedView()

            return True
        return False

    def __popupEvent(self, obj, event):
        if event.type() == QEvent.Enter:
            if self.isEnlarged():
                if self.isPopupEnabled():
                    self.setIsPopupEnabled(False)
                    return True

        if event.type() == QEvent.Leave:
            if self.isPopupEnabled():
                return True
            # left by entering a popup widget
            if self.isEnlarged():
                if isCursorOverWidget(self.enlargedWidget()):
                    self.setIsPopupEnabled(True)
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
            if obj.isCurrentWidget():
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
            # obj.pipPopupBarWidget().closeEnlargedView()
            return True

    def __dragEnterEvent(self, obj):
        self.__last_object_entered = obj
        if self.isEnlarged():
            # Block from re-enlarging itself
            if self.enlargedWidget() == obj:
                return True
            # Has just enlarged the widget, but the cursor never entered it
            elif obj.isCurrentWidget():
                self.closeEnlargedView()
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
            # enlarge widget
            if not obj.isCurrentWidget():
                obj.pipPopupBarWidget().closeEnlargedView()
                self.enlargeWidget(obj)

    def __dragEvent(self, obj, event):
        """ Handles the event filter's Drag Leave Event
        Args:
            obj (QWidget):
            event (QEvent):
        """
        # todo (538, 11) for some reason this is causing segfaults...
        # if event.type() == QEvent.DragLeave:
        #     print("drag leave", obj.name())
        #     if self.displayMode() == AbstractPopupBarDisplayWidget.STANDALONETASKBAR:
        #         widget_under_cursor = getWidgetUnderCursor()
        #         if widget_under_cursor != self.spacerWidget():
        #             self.closeEnlargedView()
        #             return True
        #     pass

        if event.type() == QEvent.DragEnter:
            # print('enter')
            #event.accept()
            self.__dragEnterEvent(obj)

        if event.type() == QEvent.DragMove:
            # print('move')
            self.__dragMoveEvent(obj)

        # on drop, close and reset
        if event.type() == QEvent.Drop:
            # print('drop')
            self.setIsDragging(False)
            obj.pipPopupBarWidget().closeEnlargedView()

            # print('drag leave')

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
        # todo (584, 11) Major delays occur in the show/resize
        """ Seems like a lot of the delay is coming from the show/resize of the widget
        that is being enlarged.
        
        There is a minor delay associated with reparenting, and setting the widget as a tool."""
        # self._start = time.time()
        # print("0", (time.time() - self._start) * 1000)
        if not widget: return
        if not self.widget(widget.index()): return
        if self.widget(widget.index()) == self.spacerWidget(): return
        if self.widget(widget.index()).parent() == self.spacerWidget().parent(): return

        # widget.setIsOverlayDisplayed(True)
        self.setIsFrozen(True)
        # from .AbstractPopupBarOrganizerWidget import AbstractPopupBarOrganizerWidget
        # _organizer_widget = getWidgetAncestor(self, AbstractPopupBarOrganizerWidget)

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
            pos, width, height = self.__enlargePiPWidget()
        if self.displayMode() == AbstractPopupBarDisplayWidget.STANDALONETASKBAR:
            pos, width, height = self.__enlargeStandaloneTaskbar()

        # move / resize enlarged widget
        widget.resize(int(width), int(height))
        widget.move(pos)

        #
        self.insertWidget(widget.index(), self._spacer_widget)
        self.setSizes(self.__temp_sizes)
        self.setIsFrozen(False)
        widget.setIsOverlayDisplayed(False)

    def __enlargeStandaloneTaskbar(self):
        """ Popups the widget when it is in taskbar mode

        returns (QPoint, width, height)"""
        # scale = self.enlargedScale()
        # negative_space = 1 - scale
        # half_neg_space = negative_space * 0.5
        negative_space = self.enlargedOffset() * 2
        half_neg_space = self.enlargedOffset()
        if self.direction() in [attrs.NORTH, attrs.SOUTH]:
            width = self.width() - negative_space
            height = self.enlargedSize()

            if self.direction() == attrs.NORTH:
                top_left = self.parent().mapToGlobal(self.geometry().topLeft())
                ypos = top_left.y() - height
                xpos = top_left.x() + half_neg_space

            if self.direction() == attrs.SOUTH:
                bot_left = self.parent().mapToGlobal(self.geometry().bottomLeft())
                ypos = bot_left.y()
                xpos = bot_left.x() + half_neg_space

        if self.direction() in [attrs.EAST, attrs.WEST]:
            height = self.height() - negative_space
            width = self.enlargedSize()

            if self.direction() == attrs.EAST:

                top_right = self.parent().mapToGlobal(self.geometry().topRight())
                xpos = top_right.x()
                ypos = top_right.y() + half_neg_space

            if self.direction() == attrs.WEST:
                top_left = self.parent().mapToGlobal(self.geometry().topLeft())
                xpos = top_left.x() - width
                ypos = top_left.y() + half_neg_space

        return QPoint(xpos, ypos), width, height

    def __enlargePiPWidget(self):
        """ Popups up the widget when it is in PiPMode

        returns (QPoint, width, height)"""
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
        if self.enlargedWidget().isCurrentWidget(): return

        # setup attrs
        self.setIsFrozen(True)
        widget_under_cursor = getWidgetUnderCursor()
        _enlarged_widget = self.enlargedWidget()
        # close children
        """ If this is stuck in recursion, this will close all child views.  Note this is
        only valid when closing a Standalone Taskbar
        # todo for some reason this doesn't appear to put the widget back...
        """
        if _enlarged_widget.isPopupWidget():
            if _enlarged_widget.popupWidget().isEnlarged():
                if _enlarged_widget.popupWidget().displayMode() == AbstractPopupBarDisplayWidget.STANDALONETASKBAR:
                    _enlarged_widget.popupWidget().closeEnlargedView()

        # update overlay displays
        if self.displayMode() in AbstractPopupBarDisplayWidget.TASKBARS:
            self.enlargedWidget().setIsOverlayDisplayed(True)
        else:
            self.enlargedWidget().setIsOverlayDisplayed(False)

        # exitted out of widget
        if not widget_under_cursor:
            self._resetSpacerWidget()
            self.setIsEnlarged(False)

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
                # enlarge mini viewer
                display_widget = getWidgetAncestor(widget_under_cursor, AbstractPiPDisplayWidget)
                popup_bar_widget = getWidgetAncestor(widget_under_cursor, AbstractPopupBarItemWidget)
                # taskbar
                if not display_widget:
                    # self.enlargedWidget().setIsOverlayDisplayed(True)
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
                    # self.enlargedWidget().setIsOverlayDisplayed(True)
                    self.enlargeWidget(popup_bar_widget)

        # exited over main viewer
        else:
            # reset display label
            self._resetSpacerWidget()
            self.setIsEnlarged(False)

        # unfreeze
        """ Unfreezing as a delayed event to help to avoid the segfaults that occur
        when PyQt tries to do things to fast..."""
        # self.setIsFrozen(False)
        runDelayedEvent(self, self.unfreeze, delay_amount=10)

    def unfreeze(self):
        self.setIsFrozen(False)

    """ WIDGETS """
    def addWidget(self, widget, name="", index=0):
        if widget == self.spacerWidget():
            return
        if not isinstance(widget, AbstractPopupBarItemWidget):
            widget = self.createNewWidget(widget, index=index, name=name)
        if isinstance(widget, AbstractPopupBarItemWidget):
            widget.installEventFilter(self)
            self.installDragEnterMonkeyPatch(widget.popupWidget())
            self.installDragMoveMonkeyPatch(widget.popupWidget())
            widget.delegateWidget().setAcceptDrops(True)
            return QSplitter.addWidget(self, widget)
        else:
            print("{widget_type} is not valid.".format(widget_type=type(widget)))
            return

    def createNewWidget(self, widget, name="", index=0):
        """
        Creates a new widget in the mini widget.  This is only when a new widget needs to be instantiated.

        Args:
            widget:
            name:

        Returns (AbstractPopupBarItemWidget):
        """
        mini_widget = AbstractPopupBarItemWidget(self, direction=Qt.Vertical, delegate_widget=widget, name=name)

        mini_widget.setIsOverlayEnabled(self.isOverlayEnabled())
        if self.displayMode() == AbstractPopupBarDisplayWidget.PIP:
            mini_widget.setIsOverlayDisplayed(self.isOverlayEnabled())
        elif self.displayMode() in [AbstractPopupBarDisplayWidget.PIPTASKBAR, AbstractPopupBarDisplayWidget.STANDALONETASKBAR]:
            pass
        # self.installDragEnterMonkeyPatch(mini_widget.delegateWidget())
        # self.installDragLeaveMonkeyPatch(mini_widget.delegateWidget())
        # self.installDragMoveMonkeyPatch(mini_widget.delegateWidget())
        # mini_widget.installEventFilter(self)
        mini_widget.delegateWidget().setAcceptDrops(True)

        self.insertWidget(index, mini_widget)

        self.updateWidgetIndexes()
        return mini_widget

    def insertWidget(self, index, widget, name=""):
        if widget == self.spacerWidget():
            return
        if not isinstance(widget, AbstractPopupBarItemWidget):
            widget = self.createNewWidget(widget, index=index, name=name)
        if isinstance(widget, AbstractPopupBarItemWidget):
            widget.installEventFilter(self)
            self.installDragEnterMonkeyPatch(widget.popupWidget())
            self.installDragMoveMonkeyPatch(widget.popupWidget())
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
        is_current_widget (bool): Determines if this widget is currently the widget displayed
            in the main viewer.  Note, this is only valid if the displayMode() is set to
                PIP | PIPTASKBAR
        is_overlay_enabled (bool): determines if the overlay is displayed.  This is used with
            the PopupBar to show text instead of the widget to the user.
        is_overlay_displayed (bool): determines if the overlay is currently displayed.  If set to
            True, this will display the "acronym", if False, will display the delegate widget.
        is_pip_widget (bool): determines if this widgets delegate widget is inherited from the
            AbstractPopupBarDisplayWidget.  This is for handling recursive viewing
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
        is_overlay_enabled=True,
        acronym=None
    ):
        if not acronym:
            acronym = name
        super(AbstractPopupBarItemWidget, self).__init__(parent, title=acronym)

        self._is_overlay_enabled = is_overlay_enabled
        self._is_current_widget = False
        self._name = name
        self._is_display_name_shown = True
        self._overlay_image = ""
        self._index = 0

        # create delegate widget
        delegate_widget = AbstractLabelledInputWidget(
            self, name=name, direction=direction, delegate_widget=delegate_widget)

        self.setDelegateWidget(delegate_widget)

        # Todo find all of these handlers and remove them?
        # this is just a forced override for now
        # disable editable header
        self._is_shown = False
        delegate_widget.viewWidget().setDisplayMode(AbstractOverlayInputWidget.DISABLED)
        self.setAcceptDrops(True)
    #     self.popupWidget().installEventFilter(self)
    #
    # def eventFilter(self, obj, event):
    #     if event.type() == QEvent.KeyPress:
    #         print('key press', event.text())
    #         return True
    #     if event.type() in [QEvent.Show, QEvent.Resize]:
    #         #if event.type() == QEvent.Resize:
    #         if self._is_shown:
    #             print('returning true', obj)
    #             return True
    #         else:
    #             print('first show')
    #             self._is_shown = True
    #     return False

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
    def popupWidget(self):
        return self.delegateWidget().delegateWidget()

    def pipPopupBarWidget(self):
        return getWidgetAncestor(self, AbstractPopupBarDisplayWidget).popupBarWidget()

    """ PROPERTIES """
    def isPopupWidget(self):
        """ Determines if this item is a popup widget.

        This is done by
            Checking to see if it is a subclass of "AbstractPopupBarDisplayWidget"
                or
            If it has the attr "_is_popup_widget" """
        if isinstance(self.popupWidget(), AbstractPopupBarDisplayWidget):
            return True
        elif hasattr(self.popupWidget(), "_is_popup_widget"):
            return True
        else:
            return False

    def isDisplayNameShown(self):
        return self._is_display_name_shown

    def setIsDisplayNameShown(self, is_shown):
        self._is_display_name_shown = is_shown
        if is_shown:
            self.headerWidget().show()
        else:
            self.headerWidget().hide()

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

    def isCurrentWidget(self):
        return self._is_current_widget

    def setIsCurrentWidget(self, _is_current_widget):
        self._is_current_widget = _is_current_widget

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
                    main_widget = getWidgetAncestor(self, AbstractPiPDisplayWidget)
                    filepath = "/".join(main_widget.filepath().split("/")[:-1])
                image_path = image_path.replace("../", filepath + "/")
            if image_path.startswith("$"):
                envar = image_path[1:image_path.index("/")]
                if os.path.isdir(os.environ[envar]):
                    image_path = os.environ[envar] + image_path[image_path.index("/"):]
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

    Attributes (class):
        PIP | PIPTASKBAR | STANDALONETASKBAR (string): flags to determine the display mode
        TASKBARS | PIPDISPLAYS (list): of flags (PIP | PIPTASKBAR | STANDALONETASKBAR) which
            act as containers for easier calling of different modes.
        _is_popup_display (bool): flag to say this is a popup display widget
            This is more useful when subclassing
        _is_popup_enabled (bool): Determines if the user has opened a popup of an enlarged widget.
    """
    PIP = "PIP"
    PIPTASKBAR = "PIP TASKBAR"
    STANDALONETASKBAR = "STANDALONE TASKBAR"
    TASKBARS = [PIPTASKBAR, STANDALONETASKBAR]
    PIPDISPLAYS = [PIP, PIPTASKBAR]
    _is_popup_widget = True
    def __init__(self, parent=None, display_mode=STANDALONETASKBAR):
        super(AbstractPopupBarDisplayWidget, self).__init__(parent)

        # setup default attrs
        self._display_widget = AbstractPopupBarWidget(parent=self)
        self._popup_bar_widget = self._display_widget
        self._widgets = []
        self._is_dragging = False
        self._is_popup_enabled = False

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
        # todo is this correct?
        # this does not look correct...
        return self.displayWidget().widgets()
        # return self._widgets

    def mainViewerWidget(self):
        if self.displayMode() in AbstractPopupBarDisplayWidget.PIPDISPLAYS:
            return self.displayWidget().mainViewerWidget()

    """ UTILS """
    def addWidget(self, widget, name="", index=0):
        # create widget if it isn't a popup bar item
        if not isinstance(widget, AbstractPopupBarItemWidget):
            widget = self.displayWidget().createNewWidget(
                widget, name=name, index=index)
        else:
            self.displayWidget().addWidget(widget)
        return widget
        # self.widgets().append(widget)

    def insertWidget(self, index, widget, name=""):
        self.addWidget(widget, index=index, name=name)

    def removeAllWidgets(self):
        self.displayWidget().removeAllWidgets()

    def numWidgets(self):
        return self.popupBarWidget().count()

    def closeEnlargedView(self):
        self.popupBarWidget().closeEnlargedView()

    def enlargeWidget(self, widget):
        self.popupBarWidget().enlargeWidget(widget)

    """ UTILS (PIP)"""
    def resizePopupBar(self):
        if self.displayMode() in AbstractPopupBarDisplayWidget.PIPDISPLAYS:
            self.displayWidget().resizePopupBar()

    def settings(self):
        return self.displayWidget().settings()

    def updateSettings(self, settings):
        self.displayWidget().updateSettings(settings)

    """ WIDGETS (CREATE) """
    def createWidgetFromConstructorCode(self, constructor_code):
        """ Creates a new widget from the code provided

        Note:
            Duplicate code from AbstractPopupBarOrganizerWidget.AbstractPiPDisplayWidget
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

    def createNewWidget(self, widget, name="", resize_popup_bar=True, index=0):
        """ Creates a new widget

        Args:
            widget (QWidget):
            name (str):
            resize_popup_bar (bool): Determines if the Popupbar should be resized
                only valid if displayMode() is set to PIPDISPLAYS
            index (int): The index to insert the widget at
                only valid if displayMode() is set to STANDALONETASKBAR

        Returns (AbstractPopupBarItemWidget):

        """
        if self.displayMode() == AbstractPopupBarDisplayWidget.STANDALONETASKBAR:
            return self.displayWidget().createNewWidget(widget, name=name, index=index)
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
        self.setPiPName(pip_name)
        self.setFilepath(filepath)
        self.setDisplayMode(display_mode)

        self.removeAllWidgets()
        # load stand alone taskbar
        if display_mode == AbstractPopupBarDisplayWidget.STANDALONETASKBAR:
            self.__loadStandaloneTaskbar(data, organizer=organizer)

        # load pip/piptaskbar
        elif display_mode in AbstractPopupBarDisplayWidget.PIPDISPLAYS:
            self.__loadPiPWidget(filepath, pip_name, organizer=organizer)

        # load settings
        self.popupBarWidget().updateSettings(data["settings"])

    def __loadStandaloneTaskbar(self, data, organizer=False):
        """ Loads a standalone taskbar from the data provided

        Args:
            data (dict): An individual PopupBar widgets data located in the
                JSON file.
                    ie: getJSONData(filepath)[pip_name]"""

        # clear popupbar organizer
        if organizer:
            from .AbstractPopupBarOrganizerWidget import AbstractPopupBarOrganizerWidget
            organizer_widget = getWidgetAncestor(self, AbstractPopupBarOrganizerWidget)
            organizer_widget.clearPopupBarOrganizerIndexes()

        # load widgets
        reversed_widgets = OrderedDict(reversed(list(data["widgets"].items())))
        #for widget_name, widget_data in data["widgets"].items():
        for widget_name, widget_data in reversed_widgets.items():
            widget = self.createWidgetFromConstructorCode(widget_data["code"])
            widget = self.addWidget(widget, name=widget_name)

            # create popup bar items
            if organizer:
                from .AbstractPopupBarOrganizerWidget import AbstractPopupBarOrganizerWidget
                organizer_widget = getWidgetAncestor(self, AbstractPopupBarOrganizerWidget)
                index = organizer_widget.popupBarOrganizerWidget().model().insertNewIndex(0, name=widget_name)

                item = index.internalPointer()
                item.setWidget(widget)
                item.setConstructorCode(widget_data["code"])

                # widget.setIndex(0)
                widget.setItem(item)

                # update indexes
                organizer_widget.popupBarWidget().updateWidgetIndexes()

    def __loadPiPWidget(self, filepath, pip_name, organizer=False):
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

        This works by creating a new AbstractPiPDisplayWidget or AbstractPopupBarWidget
        which is then reparented into this widget as the displayWidget() and popupBarWidget().
        All of the existing children of the popupBarWidget(), are reparented into the newly
        created AbstractPopupBarWidget.

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

        self.closeEnlargedView()
        _sizes = self.popupBarWidget().sizes()

        # create new display widget
        if display_mode in [AbstractPopupBarDisplayWidget.PIPTASKBAR, AbstractPopupBarDisplayWidget.PIP]:
            _display_widget = AbstractPiPDisplayWidget(parent=self)
            _popup_bar_widget = _display_widget.popupBarWidget()
            _display_widget.setPopupBarWidget(_popup_bar_widget)
        elif display_mode == AbstractPopupBarDisplayWidget.STANDALONETASKBAR:
            _display_widget = AbstractPopupBarWidget(parent=self)
            _popup_bar_widget = _display_widget

        # update layout
        for widget in self.widgets():
            widget.setIsCurrentWidget(False)
            _display_widget.addWidget(widget)

        # update settings
        settings = self.popupBarWidget().settings()
        settings["sizes"] = _sizes
        _popup_bar_widget.updateSettings(settings)
        _popup_bar_widget.setDisplayMode(display_mode)
        """ This won't work for a double toggle, ie if the use goes from PiP --> Taskbar --> PiP"""
        if isinstance(self.displayWidget(), AbstractPiPDisplayWidget):
            if isinstance(_display_widget, AbstractPiPDisplayWidget):
                _display_widget.setPiPScale(self.pipScale())
                _display_widget.setTaskbarSize(self.taskbarSize())
        _popup_bar_widget.updateWidgetIndexes()

        self.layout().addWidget(_display_widget)
        self.displayWidget().setParent(None)

        # update attrs
        self._display_widget = _display_widget
        self._popup_bar_widget = _popup_bar_widget

        """need to reset the current widget here to make sure the correct event handler is installed
        If this is not done, the old popupBarWidget() will be installed onto the handlers, which will
        break things."""
        if self.currentWidget():
            self.setCurrentWidget(self.currentWidget())

    def isEnlarged(self):
        return self.popupBarWidget().isEnlarged()

    def enlargedSize(self):
        return self.popupBarWidget().enlargedSize()

    def setEnlargedSize(self, enlarged_size):
        self.popupBarWidget().setEnlargedSize(enlarged_size)

    def enlargedOffset(self):
        return self.popupBarWidget().enlargedOffset()

    def setEnlargedOffset(self, _enlarged_offset):
        self.popupBarWidget().setEnlargedOffset(_enlarged_offset)

    def filepath(self):
        return self.popupBarWidget().filepath()

    def setFilepath(self, filepath):
        self.popupBarWidget().setFilepath(filepath)

    def pipName(self):
        return self.popupBarWidget().pipName()

    def setPiPName(self, pip_name):
        self.popupBarWidget().setPiPName(pip_name)

    def isPopupEnabled(self):
        return self._is_popup_enabled

    def setIsPopupEnabled(self, _is_popup_enabled):
        self._is_popup_enabled = _is_popup_enabled

    def isDragging(self):
        return self._is_dragging

    def setIsDragging(self, dragging):
        self._is_dragging = dragging

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
    def enlargedScale(self):
        if self.displayMode() in AbstractPopupBarDisplayWidget.PIPDISPLAYS:
            return self.popupBarWidget().enlargedScale()

    def setEnlargedScale(self, _enlarged_scale):
        if self.displayMode() in AbstractPopupBarDisplayWidget.PIPDISPLAYS:
            self.popupBarWidget().setEnlargedScale(_enlarged_scale)

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

    def sizes(self):
        if self.displayMode() in AbstractPopupBarDisplayWidget.PIPDISPLAYS:
            return self.popupBarWidget().sizes()

    def setSizes(self, sizes):
        if self.displayMode() in AbstractPopupBarDisplayWidget.PIPDISPLAYS:
            self.popupBarWidget().setSizes(sizes)


class AbstractPiPDisplayWidget(QWidget):
    """The PiPWidget is designed to display multiple widgets simultaneously to the user.

    Similar to the function that was provided to TV's in the mid 1970's.  This widget is
    designed to allow the user to create multiple hot swappable widgets inside of the same
    widget.

    Attributes:
        current_widget (QWidget): the widget that is currently set as the main display
        main_viewer_widget (PiPMainViewer):
        display_mode (AbstractPopupBarWidget.DISPLAYMODE): how this PiPWidget should be displayed
            PIP | PIPTASKBAR
        direction (attrs.DIRECTION): what side of the widget the popup will be displayed on
        enlarged_scale (float): size of widget (percent) when enlarged in PiP Mode
        enlarged_size (float): size of widget (pixels) when enlarged in Taskbar mode
        hotkey_swap_key (list): of Qt.Key that will swap to the corresponding widget in the popupBarWidget().

            The index of the Key in the list, is the index of the widget that will be swapped to.
        filepath (str): the current filepath that has been used to load this widget
        is_popup_bar_widget (bool): determines if this is a child of a PopupBarWidget.
        is_popup_bar_shown (bool): if the mini viewer is currently visible.
            This is normally toggled with the "Q" key
        is_standalone (bool): determines if this is a child of the PiPAbstractOrganizer or if it
            is an individual PiPDisplay.  This is necessary as the PiPAbstractOrganizer and the PiPDisplay
            have slightly different constructors.

            If True, this means that this display is a standalone..
            # todo (1513, 15) change this to "is_organizer"
        is_taskbar_standalone (bool): When set to taskbar, determines if it is in Standalone mode, or
            if it will be the child of a PiPWidget.
        pip_scale ((float, float)):  fractional percentage of the amount of space that
            the mini viewer will take up in relation to the overall size of the widget.
        swap_key (Qt.KEY): this key will trigger the popup
        taskbar_size (int): The size of the collapsed widgets when in TASKBAR mode.
        widgets (list): of widgets
    """

    def __init__(self, parent=None, is_popup_bar_widget=False):
        super(AbstractPiPDisplayWidget, self).__init__(parent)

        # setup attrs
        self._num_widgets = 0
        self._is_frozen = True
        self._current_widget = None
        self._previous_widget = None
        self._pip_scale = (0.35, 0.35)
        # self._display_mode = AbstractPopupBarDisplayWidget.PIP
        self._taskbar_size = 100.0
        self._is_taskbar_standalone = False
        self._filepath = ""

        self._popup_bar_min_size = (100, 100)
        self._is_popup_bar_shown = True
        self._is_popup_bar_widget = is_popup_bar_widget

        self._swap_key = Qt.Key_Space
        self._hotkey_swap_keys = [Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4, Qt.Key_5]

        # create widgets
        self._main_viewer_widget = PiPMainViewer(self)
        self._popup_bar_widget = AbstractPopupBarWidget(self)
        self._popup_bar_widget.setDisplayMode(AbstractPopupBarDisplayWidget.PIP)

        # create layout
        """Not using a stacked layout as the enter/leave events get borked"""
        # QStackedLayout(self)
        QVBoxLayout(self)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        self.layout().addWidget(self.mainViewerWidget())

        self._is_frozen = False

    """ UTILS (SWAP) """

    def swapMainViewer(self, new_display_widget):
        """ Swaps the PiPMainViewerWidget from the AbstractPopupBarItemWidget provided

        Note: The AbstractPopupBarItemWidget MUST be a AbstractPiPDisplayWidget

        Args:
            popup_bar_widget (AbstractPopupBarItemWidget):
        """
        #new_display_widget = popup_bar_widget.popupWidget()

        # swap current widgets
        self.mainViewerWidget().setWidget(new_display_widget.currentWidget())
        new_display_widget.mainViewerWidget().setWidget(self._current_widget)

        # reset currentWidget meta data
        self.setPreviousWidget(None)
        new_display_widget.setPreviousWidget(None)

        _temp = self._current_widget
        self._current_widget = new_display_widget.currentWidget()
        new_display_widget.displayWidget()._current_widget = _temp

    def swapPopupBar(self, popup_bar_widget):
        """ Swaps the AbstractPopupBarWidget from the AbstractPopupBarItemWidget provided.

        Note: The AbstractPopupBarItemWidget MUST be a AbstractPiPDisplayWidget

        Args:
            popup_bar_widget (AbstractPopupBarItemWidget):
        """
        new_display_widget = popup_bar_widget.popupWidget()

        # preflight
        if not isinstance(new_display_widget, AbstractPopupBarDisplayWidget): return

        # get temp attrs
        _temp_num_widgets = new_display_widget.numWidgets()

        # set main mini viewer
        for mini_widget in reversed(new_display_widget.popupBarWidget().widgets()):
            new_display_widget.popupBarWidget().removeWidget(mini_widget)
            # new_display_widget.popupBarWidget().removeWidget(mini_widget)
            self.popupBarWidget().insertWidget(0, mini_widget)

        # set docked mini viewer
        for i in reversed(range(_temp_num_widgets, self.numWidgets())):
            if i != popup_bar_widget.index() + _temp_num_widgets:
                mini_widget = self.popupBarWidget().widget(i)
                self.popupBarWidget().removeWidget(mini_widget)
                new_display_widget.popupBarWidget().insertWidget(0, mini_widget)

        # reset mini viewer widget indexes
        self.popupBarWidget().updateWidgetIndexes()
        new_display_widget.popupBarWidget().updateWidgetIndexes()

    def swapSettings(self, popup_bar_widget):
        """ Swaps the settings from the AbstractPopupBarItemWidget provided.

        Note: The AbstractPopupBarItemWidget MUST be a AbstractPiPDisplayWidget

        Args:
            popup_bar_widget (AbstractPopupBarItemWidget):
        """
        _old_settings = self.settings()
        _new_settings = popup_bar_widget.settings()
        self.updateSettings(_new_settings)
        popup_bar_widget.updateSettings(_old_settings)

    def swapWidgets(self):
        """
        Swaps the previous widget with the current widget.

        This allows the user to quickly swap between two widgets.
        """
        if self.previousWidget():
            self.setCurrentWidget(self.previousWidget())

    def settings(self):
        """ returns a dict of the current settings which can be set with updateSettings()"""
        popupbar_settings = self.popupBarWidget().settings()
        current_settings = {
            "PiP Scale": self.pipScale(),
            "Taskbar Size": self.taskbarSize(),
            "Overlay Text": self.currentWidget().title(),
            "Overlay Image": self.currentWidget().overlayImage(),
        }
        popupbar_settings.update(current_settings)

        return popupbar_settings
        # return {**popupbar_settings, **current_settings}

    def updateSettings(self, settings):
        """ Updates all of the settings from the settings provided.

        Note that you may need to call "resizePopupBar" afterwards in order
        to trigger a display update.

        Args:
            settings (dict): of {setting_name (str): value}
        """
        self.setPiPScale(settings["PiP Scale"])

        self.setTaskbarSize(float(settings["Taskbar Size"]))
        self.popupBarWidget().updateSettings(settings)

    """ PROPERTIES """

    def filepath(self):
        return self.popupBarWidget().filepath()

    def setFilepath(self, filepath):
        self.popupBarWidget().setFilepath(filepath)

    def pipScale(self):
        return self._pip_scale

    def setPiPScale(self, pip_scale):
        if isinstance(pip_scale, str):
            pip_scale = float(pip_scale)
        # this will probably fail in python 3...
        try:
            # python 2.7
            if isinstance(pip_scale, unicode):
                pip_scale = float(pip_scale)
        except NameError:
            # python 3+
            pass
        if isinstance(pip_scale, float):
            pip_scale = (pip_scale, pip_scale)
        if isinstance(pip_scale, tuple):
            pip_scale = (float(pip_scale[0]), float(pip_scale[1]))

        self._pip_scale = pip_scale
        self.resizePopupBar()

    def hotkeySwapKeys(self):
        return self._hotkey_swap_keys

    def setHotkeySwapKeys(self, hotkey_swap_keys):
        self._hotkey_swap_keys = hotkey_swap_keys

    def isFrozen(self):
        return self._is_frozen

    def setIsFrozen(self, is_frozen):
        self._is_frozen = is_frozen

    def isOverlayEnabled(self):
        return self.popupBarWidget().isOverlayEnabled()

    def setIsOverlayEnabled(self, enabled):
        self.popupBarWidget().setIsOverlayEnabled(enabled)

    def isPopupBarShown(self):
        return self._is_popup_bar_shown

    def setIsPopupBarShown(self, enabled):
        self._is_popup_bar_shown = enabled
        if enabled:
            self.popupBarWidget().show()
        else:
            self.popupBarWidget().hide()

    def isPopupBarWidget(self):
        return self._is_popup_bar_widget

    def setIsPopupBarWidget(self, is_popup_bar_widget):
        self._is_popup_bar_widget = is_popup_bar_widget

    def taskbarSize(self):
        return self._taskbar_size

    def setTaskbarSize(self, taskbar_size):
        if isinstance(taskbar_size, str):
            taskbar_size = float(taskbar_size)
        # this will probably fail in python 3...
        try:
            # python 2.7
            if isinstance(taskbar_size, unicode):
                taskbar_size = float(taskbar_size)
        except NameError:
            # python 3+
            pass
        self._taskbar_size = taskbar_size

    def popupBarMinSize(self):
        return self._popup_bar_min_size

    def setPopupBarMinimumSize(self, size):
        """
        Sets the minimum size the mini viewer can go to

        Args:
            size (tuple): (x, y)

        """
        self._popup_bar_min_size = size
        self.popupBarWidget().setMinimumSize(size)

    def swapKey(self):
        return self._swap_key

    def setSwapKey(self, key):
        self._swap_key = key

    def numWidgets(self):
        """ Number of widgets currently in this PiPDisplay"""
        return self.popupBarWidget().count()

    """ WIDGETS ( CREATION )"""

    def createWidgetFromConstructorCode(self, constructor_code):
        """ Creates a new widget from the code provided

        Args:
            constructor_code (code):

        Returns (QWidget): created by code"""
        loc = {}
        loc['self'] = self

        exec(compile(constructor_code, "constructor_code", "exec"), globals(), loc)
        widget = loc['widget']
        return widget

    def createNewWidgetFromConstructorCode(self, constructor_code, name="", resize_popup_bar=True):
        """
        Retuns a QWidget from the constructor code provided.

        The widget returned will be the variable "widget" from the constructor code
        Args:
            constructor_code (code):

        Returns (AbstractPopupBarItemWidget):
        """

        widget = self.createWidgetFromConstructorCode(constructor_code)
        popup_bar_widget = self.createNewWidget(widget, name, resize_popup_bar)
        return popup_bar_widget

    def createNewWidget(self, widget, name="", resize_popup_bar=True):
        """ Creates a new widget from the constructor code provided.

        This widget is inserted into the AbstractPopupBarWidget

        Args:
            constructor_code (str):
            name (str):
            resize_popup_bar (bool): if the popupBarWidget should be updated or not

        Returns (AbstractPopupBarItemWidget):
        """

        # create widget from constructor code
        # widget = self.createNewWidgetFromConstructorCode(constructor_code)
        # setup recursion for PiPWidgets
        from .AbstractPopupBarOrganizerWidget import AbstractPopupBarOrganizerWidget
        if isinstance(widget, AbstractPopupBarOrganizerWidget) or isinstance(widget, AbstractPiPDisplayWidget):
            widget.setIsPopupBarWidget(True)

        # create mini viewer widgets
        if self.currentWidget():
            popup_bar_widget = self.popupBarWidget().createNewWidget(widget, name=name)

        # create main widget
        else:
            popup_bar_widget = AbstractPopupBarItemWidget(
                self.mainViewerWidget(), direction=Qt.Vertical, delegate_widget=widget, name=name,
                is_overlay_enabled=self.isOverlayEnabled())
            # if self.popupBarWidget().displayMode() == AbstractPopupBarDisplayWidget.PIPTASKBAR:
            #     popup_bar_widget.setIsOverlayDisplayed(False)
            # else:
            popup_bar_widget.setIsOverlayDisplayed(self.isOverlayEnabled())
            self.setCurrentWidget(popup_bar_widget)

        # TODO This is probably causing some slowness on loading
        # as it is resizing the mini viewer EVERY time a widget is created
        if resize_popup_bar:
            self.resizePopupBar()

        # update indexes
        self.popupBarWidget().updateWidgetIndexes()

        return popup_bar_widget

    def addWidget(self, widget, resize_popup_bar=True):
        """ Adds a widget to the PiPDisplay

        Args:
            widget (AbstractPopupBarItemWidget):
            resize_popup_bar (bool):

        Returns:

        """
        # create mini viewer widgets
        if self.currentWidget():
            self.popupBarWidget().addWidget(widget)

        # create main widget
        else:
            self.setCurrentWidget(widget)

        # TODO This is probably causing some slowness on loading
        # as it is resizing the mini viewer EVERY time a widget is created
        if resize_popup_bar:
            self.resizePopupBar()

        # update indexes
        self.popupBarWidget().updateWidgetIndexes()

    def removeAllWidgets(self):
        if self.mainViewerWidget().widget():
            self.mainViewerWidget().widget().setParent(None)
        self.popupBarWidget().removeAllWidgets()

    def loadPiPWidgetFromFile(self, filepath, pip_name, organizer=False):
        """ Loads the PiPWidget from the file/name provided

        Args:
            filepath (str): path on disk to pipfile to load
            pip_name (str): name of pip in filepath to load
            organizer (bool): determines if this is loading from the organizer widget
        """
        # load json data
        self._filepath = filepath
        data = getJSONData(filepath)
        self.popupBarWidget().setFilepath(filepath)
        # preflight
        if not pip_name in data.keys():
            print("{pip_name} not find in {filepath}".format(pip_name=pip_name, filepath=filepath))
            return
        # update pip display
        self.removeAllWidgets()
        self.loadPiPWidgetFromData(
            data[pip_name]["widgets"],
            data[pip_name]["settings"],
            organizer=organizer)

    def loadPiPWidgetFromData(self, widgets, settings, organizer=False):
        """ Loads the PiPWidget from the data provided.

        Args:
            widgets (dict): of {widget_name(str): constructor_code(str)}
            settings (dict): of {setting (str): value}
            organizer (bool): determines if this is loading from the organizer widget
        """
        reversed_widgets = OrderedDict(reversed(list(widgets.items())))

        self.setIsFrozen(True)

        # clear pip view
        self.removeAllWidgets()
        if organizer:
            from .AbstractPopupBarOrganizerWidget import AbstractPopupBarOrganizerWidget
            organizer_widget = getWidgetAncestor(self, AbstractPopupBarOrganizerWidget)
            organizer_widget.clearPopupBarOrganizerIndexes()
            # clear all items from the view

        # reset previous widget
        self.clearPreviousWidget()
        self.clearCurrentWidget()

        # populate pip view
        # load widgets
        for widget_name, widget_data in reversed_widgets.items():
            constructor_code = widget_data["code"]
            if organizer:
                from .AbstractPopupBarOrganizerWidget import AbstractPopupBarOrganizerWidget
                organizer_widget = getWidgetAncestor(self, AbstractPopupBarOrganizerWidget)
                index = organizer_widget.createNewWidgetFromConstructorCode(
                    constructor_code, name=widget_name, resize_popup_bar=False)
                widget = index.internalPointer().widget()
            else:
                widget = self.createNewWidgetFromConstructorCode(
                    constructor_code, name=widget_name, resize_popup_bar=False)

            # update widget overlay text/image if set in Taskbar mode
            if settings["Display Mode"] == AbstractPopupBarDisplayWidget.PIPTASKBAR:
                widget.setTitle(widget_data["Overlay Text"])
                widget.setOverlayImage(widget_data["Overlay Image"])

        # update settings
        self.updateSettings(settings)

        # restore mini widget sizes
        self.setIsFrozen(False)

        # resize
        self.resizePopupBar()
        if "sizes" in list(settings.keys()):
            self.popupBarWidget().setSizes(settings["sizes"])

    """ WIDGETS """

    def mainViewerWidget(self):
        return self._main_viewer_widget

    def setMainViewerWidget(self, widget):
        self._main_viewer_widget = widget

    def popupBarWidget(self):
        return self._popup_bar_widget

    def setPopupBarWidget(self, widget):
        self._popup_bar_widget = widget

    def currentWidget(self):
        return self._current_widget

    def setCurrentWidget(self, widget):
        """
        Sets the current full screen widget

        Args:
            widget (QPopupBarWidget): widget to be set as full screen
        """
        # todo multi recursive swapping cleanup
        if widget.isPopupWidget():
            from .AbstractPopupBarOrganizerWidget import AbstractPopupBarOrganizerWidget
            if isinstance(widget.popupWidget(), AbstractPopupBarOrganizerWidget):
                print("multi recursive swapping is disabled for OrganizerWidgets")
                # won't be supporting this probably
                pass

            elif isinstance(widget.popupWidget(), AbstractPopupBarDisplayWidget):
                if widget.popupWidget().displayMode() == AbstractPopupBarDisplayWidget.STANDALONETASKBAR:
                    # todo (1989, 23) setup swapping for standalone taskbars
                    """ This should in theory swap this to a PiPTaskbar"""
                    print("Cannot swap standalone taskbars.")
                    return
                # update settings
                """ sizes doesn't swap... probably due to the add/remove of widgets
                Is not calculating the fact that the mini viewer widget will have
                one widget removed, and one added

                Going to fullscreen = sizes + 1
                going to minimized = sizes - 1
                """
                # get sizes info
                new_display_widget = widget.popupWidget()
                old_sizes = self.popupBarWidget().sizes()
                new_sizes = new_display_widget.popupBarWidget().sizes()
                del old_sizes[widget.index()]
                new_sizes.append(50)

                self.swapMainViewer(new_display_widget)
                self.swapPopupBar(widget)
                self.swapSettings(new_display_widget)

                # resize mini viewers
                self.popupBarWidget().setSizes(new_sizes)
                new_display_widget.popupBarWidget().setSizes(old_sizes)
                self.resizePopupBar()

                # update overlays
                if self.displayMode() == AbstractPopupBarDisplayWidget.PIPTASKBAR:
                    if self.previousWidget():
                        self.previousWidget().setIsOverlayDisplayed(True)
                    self.currentWidget().setIsOverlayDisplayed(False)
            return

        self.popupBarWidget().setIsFrozen(True)
        sizes = self.popupBarWidget().sizes()
        # reset current widget
        if self._current_widget:
            # Close enlarged widget
            """ Need to ensure the spacer is swapped out"""
            if self.popupBarWidget().isEnlarged():
                self.popupBarWidget()._resetSpacerWidget()
                self.popupBarWidget().setIsEnlarged(False)

            # setup mini viewer widget
            self.popupBarWidget().insertWidget(widget.index(), self._current_widget)
            self._current_widget.setIndex(widget.index())

            # update previous widget
            self.setPreviousWidget(self._current_widget)
            self._current_widget.setIsCurrentWidget(False)
            self._current_widget.removeEventFilter(self)

        else:
            """ If no current widget is set, this will install the drag patches for the widget 
            This is needed for the first time, as this does not get installed when added
            to the popup bar widget"""
            self.popupBarWidget().installDragEnterMonkeyPatch(widget.popupWidget())
            self.popupBarWidget().installDragMoveMonkeyPatch(widget.popupWidget())
        # set widget as current
        self._current_widget = widget
        self.mainViewerWidget().setWidget(widget)
        self._current_widget.installEventFilter(self.popupBarWidget())
        self._current_widget.installEventFilter(self)
        self.popupBarWidget().setCurrentWidget(widget)

        # update mini viewer widget
        self.popupBarWidget().setSizes(sizes)
        self.popupBarWidget().setIsFrozen(False)

        # update overlays
        if self.popupBarWidget().displayMode() == AbstractPopupBarDisplayWidget.PIPTASKBAR:
            if self.previousWidget():
                self.previousWidget().setIsOverlayDisplayed(True)
            self.currentWidget().setIsOverlayDisplayed(False)

    def clearCurrentWidget(self):
        self._current_widget = None

    def previousWidget(self):
        return self._previous_widget

    def setPreviousWidget(self, widget):
        self._previous_widget = widget

    def clearPreviousWidget(self):
        self._previous_widget = None

    def widgets(self):
        """ Returns a list of all child widgets

        This list will include the currently viewed main widget, aswell
        as all of the widgets in the popupBarWidget()"""
        widgets = []
        if self.mainViewerWidget().widget():
            widgets.append(self.mainViewerWidget().widget())
        widgets += self.popupBarWidget().widgets()

        return widgets

    """ DIRECTION """

    def direction(self):
        return self.popupBarWidget().direction()

    def setDirection(self, direction):
        self.popupBarWidget().setDirection(direction)

    """ EVENTS """
    def hotkeySwapEvent(self, key):
        """ Swaps the widgets when a hotkey (1-5) is pressed.

        Args:
            key (Qt.Key): Valid inputs are 1-5
        """
        try:
            # select user input
            for i, swap_key in enumerate(self.hotkeySwapKeys()):
                if swap_key == key:
                    widget = self.popupBarWidget().widget(i)

            # swap with enlarged widget
            if self.popupBarWidget().isEnlarged():
                if widget != self.popupBarWidget().enlargedWidget():
                    self.popupBarWidget().closeEnlargedView()
                    self.popupBarWidget().enlargeWidget(widget)

            # swap with main widget
            else:
                self.setCurrentWidget(widget)

        except AttributeError:
            # not enough widgets
            pass

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            # swap between this and previous
            if event.key() == self.swapKey():
                self.swapEvent()
                return True

            # hotkey swapping
            if event.key() in self.hotkeySwapKeys():
                self.hotkeySwapEvent(event.key())
                return True

            # hide PiP
            if event.key() == Qt.Key_Q:
                if not self.popupBarWidget().isEnlarged():
                    self.setIsPopupBarShown(not self.isPopupBarShown())
                    return True

            # escape
            if event.key() == Qt.Key_Escape:
                # close this mini viewer
                if self.popupBarWidget().isEnlarged():
                    self.popupBarWidget().closeEnlargedView()
                    return True

                # close parent mini viewer (if open recursively)
                if self.isPopupBarWidget():
                    parent_main_widget = getWidgetAncestor(self.parent(), AbstractPiPDisplayWidget)
                    parent_main_widget.popupBarWidget().closeEnlargedView()
                return True
        return False

    # def keyPressEvent(self, event):
    #     # swap between this and previous
    #     if event.key() == self.swapKey():
    #         self.swapEvent()
    #         return
    #
    #     # hotkey swapping
    #     if event.key() in self.hotkeySwapKeys():
    #         self.hotkeySwapEvent(event.key())
    #         return
    #
    #     # hide PiP
    #     if event.key() == Qt.Key_Q:
    #         if not self.popupBarWidget().isEnlarged():
    #             self.setIsPopupBarShown(not self.isPopupBarShown())
    #             return
    #
    #     # escape
    #     if event.key() == Qt.Key_Escape:
    #         # close this mini viewer
    #         if self.popupBarWidget().isEnlarged():
    #             self.popupBarWidget().closeEnlargedView()
    #             return
    #
    #         # close parent mini viewer (if open recursively)
    #         if self.isPopupBarWidget():
    #             parent_main_widget = getWidgetAncestor(self.parent(), AbstractPiPDisplayWidget)
    #             parent_main_widget.popupBarWidget().closeEnlargedView()
    #         return
    #
    #     return QWidget.keyPressEvent(self, event)

    def leaveEvent(self, event):
        """ Blocks the error that occurs when switching between different PiPDisplays"""
        if self.popupBarWidget().isEnlarged():
            if not isCursorOverWidget(self):
                if not self.popupBarWidget().isPopupEnabled():
                    # print("leave event")
                    self.popupBarWidget().closeEnlargedView()
        return QWidget.leaveEvent(self, event)

    def resizeEvent(self, event):
        """ After a delay in the resize, this will update the display"""

        def updateDisplay():
            self.resizePopupBar()
            self.popupBarWidget().closeEnlargedView()

        installResizeEventFinishedEvent(self, 100, updateDisplay, '_timer')
        return QWidget.resizeEvent(self, event)

    def resizePopupBar(self):
        """
        Main function for resizing the mini viewer

        The core of this function is to set the
            xpos | ypos | width | height
        of the mini viewer, based off of the number of widgets, and its current location on screen.
        """

        if self.isFrozen(): return True
        if not self.popupBarWidget(): return True
        if self.popupBarWidget().displayMode() == AbstractPopupBarDisplayWidget.PIP:
            xpos, ypos, width, height = self.__resizePiP()
        elif self.popupBarWidget().displayMode() == AbstractPopupBarDisplayWidget.PIPTASKBAR:
            xpos, ypos, width, height = self.__resizeTaskbar()
        else:
            xpos, ypos, width, height = self.__resizeTaskbar()
        # move/resize mini viewer
        self.popupBarWidget().move(int(xpos), int(ypos))
        self.popupBarWidget().resize(int(width), int(height))

    def __resizePiP(self):
        """ Resizes the PiP view when a resize event has occurred on the parent widget"""
        num_widgets = self.numWidgets()

        # preflight
        if num_widgets < 1:
            # Need to return xpos, ypos, size, width here to ensure valid options are returned
            return 0, 0, 500, 500

        # get xpos, ypos, width, height

        # special case for only one widget
        if num_widgets == 1:
            # get height / width
            width = self.width() * self.pipScale()[0]
            height = self.height() * self.pipScale()[1]

            # check for min size
            if width < self.popupBarMinSize()[0]:
                width = self.popupBarMinSize()[0]
            if height < self.popupBarMinSize()[1]:
                height = self.popupBarMinSize()[1]

            if self.direction() in [attrs.EAST, attrs.WEST]:
                # NORTH EAST
                if self.direction() == attrs.WEST:
                    ypos = 0
                    xpos = self.width() * (1 - self.pipScale()[0])
                    # check minimums
                    if (self.width() - xpos) < self.popupBarMinSize()[0]:
                        xpos = self.width() - self.popupBarMinSize()[0]

                # SOUTH WEST
                if self.direction() == attrs.EAST:
                    ypos = self.height() * (1 - self.pipScale()[1])
                    xpos = 0
                    if (self.height() - ypos) < self.popupBarMinSize()[1]:
                        ypos = self.height() - self.popupBarMinSize()[1]

            if self.direction() in [attrs.NORTH, attrs.SOUTH]:
                # SOUTH EAST
                if self.direction() == attrs.NORTH:
                    xpos = self.width() * (1 - self.pipScale()[0])
                    ypos = self.height() * (1 - self.pipScale()[1])

                    # check minimums
                    if (self.width() - xpos) < self.popupBarMinSize()[0]:
                        xpos = self.width() - self.popupBarMinSize()[0]

                    if (self.height() - ypos) < self.popupBarMinSize()[1]:
                        ypos = self.height() - self.popupBarMinSize()[1]

                # NORTH WEST
                if self.direction() == attrs.SOUTH:
                    xpos = 0
                    ypos = 0

        # more than one widget
        if 1 < num_widgets:
            pip_offset = 1 - self.pipScale()[0]

            # get xpos/ypos/height/width
            if self.direction() in [attrs.EAST, attrs.WEST]:
                height = self.height()
                width = self.width() * self.pipScale()[0]
                if self.direction() == attrs.WEST:
                    ypos = 0
                    xpos = self.width() * pip_offset
                    # check minimum size...
                    if (self.width() - xpos) < self.popupBarMinSize()[0]:
                        xpos = self.width() - self.popupBarMinSize()[0]
                        width = self.popupBarMinSize()[0]

                if self.direction() == attrs.EAST:
                    ypos = 0
                    xpos = 0

            if self.direction() in [attrs.NORTH, attrs.SOUTH]:
                height = self.height() * self.pipScale()[1]
                width = self.width()
                if self.direction() == attrs.SOUTH:
                    xpos = 0
                    ypos = 0
                if self.direction() == attrs.NORTH:
                    xpos = 0
                    ypos = self.height() * pip_offset
                    # check minimum size...
                    if (self.height() - ypos) < self.popupBarMinSize()[1]:
                        ypos = self.height() - self.popupBarMinSize()[1]
                        height = self.popupBarMinSize()[1]

        return xpos, ypos, width, height

    def __resizeTaskbar(self):
        """ Resizes the PiPTaskbar when a resize event has occurred on the parent widget"""
        size = self.taskbarSize()
        handle_width = self.popupBarWidget().handleWidth()
        total_size = (self.popupBarWidget().count() * size) + ((self.popupBarWidget().count() - 1) * handle_width)

        if self.direction() in [attrs.NORTH, attrs.SOUTH]:
            offset = (self.width() - total_size) * 0.5
            xpos = offset
            width = total_size
            height = size
            if self.direction() == attrs.NORTH:
                ypos = self.height() - size
            if self.direction() == attrs.SOUTH:
                ypos = 0

        if self.direction() in [attrs.EAST, attrs.WEST]:
            offset = (self.height() - total_size) * 0.5
            ypos = offset
            height = total_size
            width = size
            if self.direction() == attrs.EAST:
                xpos = 0
            if self.direction() == attrs.WEST:
                xpos = self.width() - size

        return xpos, ypos, width, height

    def swapEvent(self):
        """ Swaps the widget that is being displayed.

        This occurs when the swapKey() is pressed.
        If there is currently a widget enlarged, the enlarged widget will become the one
        that is currently being displayed.

        If there is no widget currently enlarged, then it will swap the main widget, with
        the previously enlarged widget."""
        # pre flight
        widget = getWidgetUnderCursor()
        if widget == self.popupBarWidget(): return
        if isWidgetDescendantOf(widget, widget.parent(), self.popupBarWidget()): return
        if widget == self.popupBarWidget().spacerWidget(): return
        if isinstance(widget, QSplitterHandle): return

        # set currently enlarged widget as the main widget
        """Freezing here to avoid the cursor being over the PopupBarWidget
        If this happens, it will close, then try to enlarge, then get stuck in
        Qts event queue and have unexpected behavior"""
        self.popupBarWidget().setIsFrozen(True)

        if self.popupBarWidget().isEnlarged():
            self.setCurrentWidget(self.popupBarWidget().enlargedWidget())
            self.popupBarWidget().setIsEnlarged(False)

        # swap previous widget widgets
        else:
            self.swapWidgets()

        self.popupBarWidget().setIsFrozen(False)


class PiPMainViewer(QWidget):
    def __init__(self, parent=None):
        super(PiPMainViewer, self).__init__(parent)
        QVBoxLayout(self)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self._widget = None

    def widget(self):
        return self._widget

    def setWidget(self, widget):
        self._widget = widget
        self.layout().addWidget(widget)
        widget.setIsCurrentWidget(True)
        widget.layout().setContentsMargins(0, 0, 0, 0)

    def removeWidget(self):
        self.widget().setParent(None)
        # self.widget().deleteLater()


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

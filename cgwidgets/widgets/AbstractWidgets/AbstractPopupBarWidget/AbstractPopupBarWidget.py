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
from qtpy.QtCore import QEvent, Qt

from cgwidgets.utils import (
    getWidgetUnderCursor,
    isWidgetDescendantOf,
    isCursorOverWidget,
    getWidgetAncestor,
    runDelayedEvent)

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
    PIP = "PIP"
    PIPTASKBAR = "TASKBAR"
    TASKBAR = "TASKBAR_STANDALONE"

    def __init__(self, parent=None, direction=attrs.EAST, orientation=Qt.Vertical, overlay_widget=None):
        super(AbstractPopupBarWidget, self).__init__(parent, orientation)

        self._is_frozen = False
        self._is_dragging = False
        self._is_enlarged = False
        self._is_overlay_enabled = True
        self._is_standalone = True
        self._enlarged_scale = 0.85
        self._direction = direction
        self._display_mode = AbstractPopupBarWidget.TASKBAR

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
        if display_mode == AbstractPopupBarWidget.PIP:
            self.setIsOverlayEnabled(False)
        if display_mode == AbstractPopupBarWidget.PIPTASKBAR:
            self.setIsOverlayEnabled(True)
        if display_mode == AbstractPopupBarWidget.TASKBAR:
            self.setIsOverlayEnabled(True)

    def enlargedScale(self):
        return self._enlarged_scale

    def setEnlargedScale(self, enlarged_scale):
        self._enlarged_scale = enlarged_scale

    def enlargedWidget(self):
        return self._enlarged_widget

    def setEnlargedWidget(self, widget):
        self._enlarged_widget = widget

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
        for widget in self.widgets():
            widget.setIsOverlayEnabled(enabled)
            if widget != self.enlargedWidget():
                widget.setIsOverlayDisplayed(enabled)

    def isDragging(self):
        return self.getTopMostPiPDisplay(self, self.parent()).isDragging()

    def setIsDragging(self, _pip_widget_is_dragging):
        if self.displayMode() == AbstractPopupBarWidget.PIP:
            self.getTopMostPiPDisplay(self, self.parent()).setIsDragging(_pip_widget_is_dragging)

    def isEnlarged(self):
        return self._is_enlarged

    def setIsEnlarged(self, enabled):
        self._is_enlarged = enabled

    def isFrozen(self):
        return self._is_frozen

    def setIsFrozen(self, frozen):
        self._is_frozen = frozen

    def isStandalone(self):
        return self._is_standalone

    def setIsStandalone(self, enabled):
        self._is_standalone = enabled

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
                    self.enlargedWidget().setIsOverlayDisplayed(False)
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

        # set/get attrs
        self.setIsEnlarged(True)
        self.setEnlargedWidget(widget)

        """temp sizes holds the current size of widgets
        so that they can be added/removed and restored to their original state"""
        self.__temp_sizes = self.sizes()

        # enlarge widget based on the current display mode
        if self.displayMode() == AbstractPopupBarWidget.PIP:
            xpos, ypos, width, height = self.__enlargePiPWidget()

        elif self.displayMode() == AbstractPopupBarWidget.PIPTASKBAR:
            """ This is just a clone of the pip widget atm.
            Not sure if you'll even need another handler... as the 
            pip handler might work fine here... and its merely the resize
            display which needs the handling"""
            widget.setIsOverlayDisplayed(True)
            xpos, ypos, width, height = self.__enlargePiPWidget()

        elif self.displayMode() == AbstractPopupBarWidget.TASKBAR:
            widget.setIsOverlayDisplayed(True)
            xpos, ypos, width, height = self.__enlargeTaskbar()

        # Swap spacer widget
        self.replaceWidget(widget.index(), self.spacerWidget())
        self.spacerWidget().show()

        # reparent widget
        widget.setParent(self.parent())
        widget.show()

        # move / resize enlarged widget
        widget.resize(int(width), int(height))
        widget.move(int(xpos), int(ypos))

        #
        self.insertWidget(widget.index(), self._spacer_widget)
        self.setSizes(self.__temp_sizes)

        # show mini viewer widgets
        # if widget.isPiPWidget():
        #     widget.delegateWidget().setIsPopupBarShown(True)

        self.setIsFrozen(False)

    def __enlargeTaskbar(self):
        """ Popups the widget when it is in taskbar mode """
        scale = self.enlargedScale()
        negative_space = 1 - scale
        half_neg_space = negative_space * 0.5

        if self.direction() == attrs.NORTH:
            top_left = self.geometry().topLeft()
            ypos = top_left.y() - self.overlayWidget().height() + (self.overlayWidget().height() * negative_space)
            xpos = top_left.x() + (self.overlayWidget().width() * half_neg_space)

        if self.direction() == attrs.SOUTH:
            bot_left = self.geometry().bottomLeft()
            ypos = bot_left.y()
            xpos = bot_left.x() + (self.overlayWidget().width() * half_neg_space)

        if self.direction() == attrs.EAST:
            top_right = self.geometry().topRight()
            xpos = top_right.x()
            ypos = top_right.y() + (self.overlayWidget().height() * half_neg_space)

        if self.direction() == attrs.WEST:
            top_left = self.geometry().topLeft()
            xpos = top_left.x() - self.overlayWidget().width() + (self.overlayWidget().width() * negative_space)
            ypos = top_left.y() + (self.overlayWidget().height() * half_neg_space)

        width = self.overlayWidget().width() - (self.overlayWidget().width() * negative_space)
        height = self.overlayWidget().height() - (self.overlayWidget().height() * negative_space)

        return xpos, ypos, width, height

    def __enlargePiPWidget(self):
        """ Popups up the widget when it is in PiPMode"""
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

        return xpos, ypos, width, height

    def __enlargePiPTaskbar(self):
        pass

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
                if not display_widget:
                    self.enlargeWidget(popup_bar_widget)
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
                    self.enlargeWidget(popup_bar_widget)

        # exited over main viewer
        else:
            # reset display label
            self._resetSpacerWidget()
            self.setIsEnlarged(False)
            self.enlargedWidget().setIsOverlayDisplayed(False)

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
    def createNewWidget(self, widget, name="", is_pip_widget=False, index=0, is_overlay_enabled=True):
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
        if self.displayMode() == AbstractPopupBarWidget.PIP:
            mini_widget.setIsOverlayDisplayed(self.isOverlayEnabled())
        elif self.displayMode() in [AbstractPopupBarWidget.PIPTASKBAR, AbstractPopupBarWidget.TASKBAR]:
            pass
        # self.installDragEnterMonkeyPatch(mini_widget.delegateWidget())
        # self.installDragLeaveMonkeyPatch(mini_widget.delegateWidget())
        # self.installDragMoveMonkeyPatch(mini_widget.delegateWidget())
        mini_widget.installEventFilter(self)
        mini_widget.delegateWidget().setAcceptDrops(True)

        self.insertWidget(index, mini_widget)

        self.updateWidgetIndexes()
        return mini_widget

    def addWidget(self, widget):
        if isinstance(widget, AbstractPopupBarItemWidget):
            widget.installEventFilter(self)
            self.installDragEnterMonkeyPatch(widget.delegateWidget())
            self.installDragMoveMonkeyPatch(widget.delegateWidget())
            widget.delegateWidget().setAcceptDrops(True)
            return QSplitter.addWidget(self, widget)
        elif widget == self.spacerWidget():
            return
        else:
            print("{widget_type} is not valid.".format(widget_type=type(widget)))
            return

    def insertWidget(self, index, widget):
        if isinstance(widget, AbstractPopupBarItemWidget):
            widget.installEventFilter(self)
            self.installDragEnterMonkeyPatch(widget.delegateWidget())
            self.installDragMoveMonkeyPatch(widget.delegateWidget())
            widget.delegateWidget().setAcceptDrops(True)
            return QSplitter.insertWidget(self, index, widget)
        elif widget == self.spacerWidget():
            pass
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

    def overlayWidget(self):
        if not hasattr(self, "_overlay_widget"):
            return self.window()
        else:
            return self._overlay_widget

    def setOverlayWidget(self, overlay_widget):
        self._overlay_widget = overlay_widget


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
            self.setCurrentIndex(enabled)
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


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication, QLabel, QHBoxLayout
    from cgwidgets.utils import centerWidgetOnCursor, setAsAlwaysOnTop, centerWidgetOnScreen

    app = QApplication(sys.argv)

    # create popup bar
    popup_bar_widget = AbstractPopupBarWidget()
    for x in range(3):
        label = QLabel(str(x))
        popup_bar_widget.createNewWidget(label, str(x))

    # create main widget
    main_widget = QWidget()
    main_layout = QVBoxLayout(main_widget)
    other_widget = QLabel("Something Else")
    main_layout.addWidget(popup_bar_widget)
    main_layout.addWidget(other_widget)

    # set popup bar widget

    popup_bar_widget.setOverlayWidget(other_widget)
    popup_bar_widget.setFixedWidth(50)
    popup_bar_widget.setDirection(attrs.SOUTH)

    # show widget
    setAsAlwaysOnTop(main_widget)
    main_widget.show()
    centerWidgetOnScreen(main_widget)


    sys.exit(app.exec_())

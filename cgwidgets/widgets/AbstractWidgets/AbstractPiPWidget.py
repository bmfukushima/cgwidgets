"""
Todo:
    * Minimum sizing/offsets?
    * Overall cleanup / organization
        mainWidget --> AbstractPiPWidget?
    * Expose settings to user?
    * Organizer...
        - Settup API
        - Save/Load JSON's
            - how does this even work...
    * PiPMiniViewerWidget --> Borders... styles not working???
        - base style sheet added to ShojiLayout...
            in general the shoji layout needs to be more flexible

"""
import json
from collections import OrderedDict
import os

from qtpy.QtWidgets import (
    QStackedLayout, QWidget, QBoxLayout, QVBoxLayout, QLabel, QSizePolicy, QSplitter, QHBoxLayout)
from qtpy.QtCore import QEvent, Qt, QPoint
from qtpy.QtGui import QCursor

from cgwidgets.views import AbstractDragDropModelItem
from cgwidgets.utils import attrs, getWidgetUnderCursor, isWidgetDescendantOf, getWidgetAncestor, getDefaultSavePath, getJSONData

from cgwidgets.settings.hover_display import installHoverDisplaySS, removeHoverDisplay
from cgwidgets.settings.colors import iColor
from cgwidgets.settings import keylist

from cgwidgets.widgets.AbstractWidgets.AbstractLabelledInputWidget import AbstractLabelledInputWidget
from cgwidgets.widgets.AbstractWidgets.AbstractOverlayInputWidget import AbstractOverlayInputWidget
from cgwidgets.widgets.AbstractWidgets.AbstractModelViewWidget import AbstractModelViewWidget
from cgwidgets.widgets.AbstractWidgets.AbstractShojiLayout import AbstractShojiLayout
from cgwidgets.widgets import (
    AbstractListInputWidget,
    AbstractButtonInputWidget,
    AbstractStringInputWidget,
    AbstractLabelWidget,
    AbstractButtonInputWidgetContainer)


class AbstractPiPWidget(AbstractShojiLayout):
    """
    The PiPWidget is designed to display multiple widgets simultaneously to the user.

    Similar to the function that was provided to TV's in the mid 1970's.  This widget is
    designed to allow the user to create multiple hot swappable widgets inside of the same
    widget.

    Args:

    Attributes:
        current_widget (QWidget): the widget that is currently set as the main display
        direction (attrs.DIRECTION): what side the mini viewer will be displayed on.
        pip_scale ((float, float)):  fractional percentage of the amount of space that
            the mini viewer will take up in relation to the overall size of the widget.
        swap_key (Qt.KEY): this key will trigger the popup
        widgets (list): of widgets

    Hierarchy:
        |- PiPMainWidget --> QWidget
        |    |- QVBoxLayout
        |    |    |- PiPDisplayFlagsWidget --> AbstractButtonInputWidgetContainer
        |    |    |- PiPMainViewer --> QWidget
        |    |    |- PiPPanelCreatorWidget --> AbstractListInputWidget
        |    |- MiniViewer (QWidget)
        |        |- QBoxLayout
        |            |-* PiPMiniViewerWidget --> QWidget
        |                    |- QVBoxLayout
        |                    |- AbstractLabelledInputWidget
        |- LocalOrganizerWidget --> AbstractModelViewWidget
        |- CreatorWidget (Extended...)
        |- GlobalOrganizerWidget --> AbstractModelViewWidget

    Signals:
        Swap (Enter):
            Upon user cursor entering a widget, that widget becomes the main widget

            PiPMiniViewer --> EventFilter --> EnterEvent
                - swap widget
                - freeze swapping (avoid recursion)
            PiPMiniViewer --> LeaveEvent
                - unfreeze swapping
        Swap (Key Press):
            Upon user key press on widget, that widget becomces the main widget
            PiPMainWidget --> keyPressEvent --> setCurrentWidget
        Swap Previous (Key Press)
            Press ~, main widget is swapped with previous main widget
            PiPMainWidget --> keyPressEvent --> setCurrentWidget
        Quick Drag ( Drag Enter ):
            Upon user drag enter, the mini widget becomes large to allow easier dropping
            PiPMiniViewer --> EventFilter --> Drag Enter
                                          --> Enter
                                          --> Drop
                                          --> Drag Leave
                                          --> Leave
        HotSwap (Key Press 1-5):
            PiPMainWidget --> keyPressEvent --> setCurrentWidget
        Toggle previous widget
            PiPMainWidget --> keyPressEvent --> swapWidgets
        Toggle Organizer Widget (Q):
            keyPressEvent --> toggleLocalOrganizerVisibility
        Create New Widget -->
        Delete Widget -->
        TempWidgets
            Temp widgets will be created and destroyed when the total number of widgets is
            less than the minimum number needed to properly displayed the PiPWidget (2).
            These widgets will then act as place holders for the display, which cannot
            be removed.
                createTempWidget()
                tempWidgets()
                removeTempWidget()

        PanelCreatorWidget:
            show (c):
                keyPressEvent --> toggleCreatorVisibility --> show
            hide (esc)
    """
    def __init__(self, parent=None, widget_types=None):
        super(AbstractPiPWidget, self).__init__(parent)
        # setup default attrs
        self.setOrientation(Qt.Horizontal)
        self._temp_widgets = []
        if not widget_types:
            widget_types = []

        # create widgets
        # create main pip widget
        self._main_widget = PiPMainWidget(self, widget_types)

        # setup local organizer widget
        self._local_organizer_widget = PiPLocalOrganizerWidget(self)
        self._is_local_organizer_visible = False
        self._local_organizer_widget.hide()

        # setup global organizer widget
        self._global_organizer_widget = PiPGlobalOrganizerWidget(self)
        self._is_global_organizer_visible = False
        #self._global_organizer_widget.hide()

        # setup creator widget visibility
        self._is_panel_creator_visible = False

        # add widgets
        self.addWidget(self._main_widget)
        self.addWidget(self._local_organizer_widget)

        # Disable Shoji full screen stuff...
        self.setChildSoloable(False, self.mainWidget())
        self.setChildSoloable(False, self.localOrganizerWidget())
        self.setChildSoloable(False, self.globalOrganizerWidget())

        # create temp widget
        self.createTempWidget()
        self.createTempWidget()

    """ UTILS """
    def numWidgets(self):
        return len(self.widgets())

    def widgets(self):
        return [index.internalPointer().widget() for index in self.localOrganizerWidget().model().getAllIndexes() if hasattr(index.internalPointer(), "_widget")]

    def items(self):
        return [index.internalPointer() for index in self.localOrganizerWidget().model().getAllIndexes() if hasattr(index.internalPointer(), "_widget")]

    """ WIDGETS (DISPLAY)"""
    def mainWidget(self):
        return self._main_widget

    def miniViewerWidget(self):
        return self.mainWidget().mini_viewer

    def mainViewerWidget(self):
        return self.mainWidget().main_viewer

    def localOrganizerWidget(self):
        return self._local_organizer_widget

    def globalOrganizerWidget(self):
        return self._global_organizer_widget

    def panelCreatorWidget(self):
        return self.mainWidget().panel_creator_widget

    """ WIDGETS """
    def createNewWidget(self, constructor_code, name=""):
        """

        Args:
            widget:
            name:

        Returns:

        """

        # create widget from constructor code
        loc = {}
        loc['self'] = self
        exec(constructor_code, globals(), loc)
        widget = loc['widget']

        # insert widget into layout
        if 0 < self.numWidgets():
            mini_widget = self.miniViewerWidget().createNewWidget(widget, name=name)
        else:
            mini_widget = PiPMiniViewerWidget(self, direction=Qt.Vertical, delegate_widget=widget, name=name)
            self.mainWidget().setCurrentWidget(mini_widget)

        # create new index
        index = self.localOrganizerWidget().model().insertNewIndex(0, name=name)

        item = index.internalPointer()
        item.setWidget(mini_widget)
        item.setConstructorCode(constructor_code)

        mini_widget.setIndex(0)
        mini_widget.setItem(item)

        # update indexes
        self.updateWidgetIndexes()

        # # destroy temp widgets
        if 2 < self.numWidgets():
            if name != "":
                self.removeTempWidget()
        #
        # print (self.tempWidgets())

        self.mainWidget().resizeMiniViewer()
        return index

    def updateWidgetIndexes(self):
        """
        Runs through all of the widgets and resets their indexes.

        This will need to be done every time a new widget is added
        """
        for index in self.localOrganizerWidget().model().getAllIndexes():
            item = index.internalPointer()
            if hasattr(item, "_widget"):
                item.widget().setIndex(index.row())

    def removeAllWidgets(self):
        """ Clears all of the widgets from the current AbstractPiPWidget"""
        for item in self.localOrganizerWidget().model().getRootItem().children():
            item.widget().setParent(None)
            item.widget().deleteLater()
        self.localOrganizerWidget().model().clearModel()

    """ WIDGETS (TEMP)"""
    def createTempWidget(self):
        constructor_code = """
from cgwidgets.widgets import AbstractLabelWidget
text = \"\"\"
Press (A)
Open widget organizer, to create new widgets, save widgets, etc \"\"\"
widget = AbstractLabelWidget(self, text)
widget.setWordWrap(True)
        """

        index = self.createNewWidget(constructor_code, "")

        # setup item
        item = index.internalPointer()
        item.setIsSelectable(False)
        item.setIsDragEnabled(False)
        item.setIsEnabled(False)

        # setup widget
        item.widget().main_widget.viewWidget().setDisplayMode(AbstractOverlayInputWidget.DISABLED)

    def removeTempWidget(self):
        """
        Removes the first temp widget from the tempWidgets list
        """
        model = self.localOrganizerWidget().model()
        indexes = model.findItems("", match_type=Qt.MatchExactly)
        if 0 < len(indexes):
            model.deleteItem(indexes[0].internalPointer(), event_update=True)

    """ SAVE (VIRTUAL) """
    def setSavePath(self, file_path):
        self.localOrganizerWidget().saveWidget().setSaveFilePath(file_path)

    """ VIRTUAL FUNCTIONS (MAIN WIDGET)"""
    def direction(self):
        return self.mainWidget().direction()

    def setDirection(self, direction):
        self.mainWidget().setDirection(direction)

    def swapKey(self):
        return self.mainWidget().swapKey()

    def setSwapKey(self, key):
        self.mainWidget().setSwapKey(key)

    def pipScale(self):
        return self.mainWidget().pipScale()

    def setPiPScale(self, pip_scale):
        self.mainWidget().setPiPScale(pip_scale)

    def enlargedScale(self):
        return self.mainWidget().enlargedScale()

    def setEnlargedScale(self, _enlarged_scale):
        self.mainWidget().setEnlargedScale(_enlarged_scale)

    def showWidgetDisplayNames(self, enabled):
        self.mainWidget().showWidgetDisplayNames(enabled)

    def currentWidget(self):
        return self.mainWidget().currentWidget()

    def setCurrentWidget(self, current_widget):
        self.mainWidget().setCurrentWidget(current_widget)

    def previousWidget(self):
        return self.mainWidget().previousWidget()

    def setPreviousWidget(self, previous_widget):
        self.mainWidget().setPreviousWidget(previous_widget)

    """ ORGANIZER / CREATOR """
    def isLocalOrganizerVisible(self):
        return self._is_local_organizer_visible

    def setIsLocalOrganizerVisible(self, visible):
        self._is_local_organizer_visible = visible

    def toggleLocalOrganizerVisibility(self):
        """
        Toggles whether or not the organizer widget is visible to the user

        Note: This is currently hard coded to "Q"
        """

        # if self.miniViewerWidget()._is_frozen:
        if self.miniViewerWidget().isEnlarged():
            obj = getWidgetUnderCursor(QCursor.pos())
            widget = getWidgetAncestor(obj, PiPMiniViewerWidget)
            self.miniViewerWidget().closeEnlargedView(widget)

        self._is_local_organizer_visible = not self.isLocalOrganizerVisible()
        if self.isLocalOrganizerVisible():
            self.localOrganizerWidget().show()
        else:
            self.localOrganizerWidget().hide()

    def isGlobalOrganizerVisible(self):
        return self._is_global_organizer_visible

    def setIsGlobalOrganizerVisible(self, visible):
        self._is_global_organizer_visible = visible

    def toggleGlobalOrganizerVisibility(self):
        """
        Toggles whether or not the organizer widget is visible to the user

        Note: This is currently hard coded to "Q"
        """

        # if self.miniViewerWidget()._is_frozen:
        if self.miniViewerWidget().isEnlarged():
            obj = getWidgetUnderCursor(QCursor.pos())
            widget = getWidgetAncestor(obj, PiPMiniViewerWidget)
            self.miniViewerWidget().closeEnlargedView(widget)

        self._is_global_organizer_visible = not self.isGlobalOrganizerVisible()
        if self.isGlobalOrganizerVisible():
            self.globalOrganizerWidget().show()
        else:
            self.globalOrganizerWidget().hide()

    def isPanelCreatorVisible(self):
        return self._is_panel_creator_visible

    def setIsPanelCreatorVisible(self, visible):
        self._is_panel_creator_visible = visible

    def toggleCreatorVisibility(self):
        """
        Toggles whether or not the organizer widget is visible to the user

        Note: This is currently hard coded to "Q"
        """

        # if self.miniViewerWidget()._is_frozen:
        if not self.isPanelCreatorVisible():
            if self.miniViewerWidget().isEnlarged():
                obj = getWidgetUnderCursor(QCursor.pos())
                widget = getWidgetAncestor(obj, PiPMiniViewerWidget)
                self.miniViewerWidget().closeEnlargedView(widget)

            self._is_panel_creator_visible = not self.isPanelCreatorVisible()
            if self.isPanelCreatorVisible():
                self.panelCreatorWidget().show()
                self.panelCreatorWidget().setFocus()

    """ EVENTS """
    def keyPressEvent(self, event):
        print('abstract')
        if event.key() == Qt.Key_A:
            self.toggleGlobalOrganizerVisibility()

        if event.key() == Qt.Key_F:
            self.toggleLocalOrganizerVisibility()

        if event.key() == Qt.Key_C:
            self.toggleCreatorVisibility()

        return QSplitter.keyPressEvent(self, event)


class PiPMainWidget(QWidget):
    """
    The PiPWidget is designed to display multiple widgets simultaneously to the user.

    Similar to the function that was provided to TV's in the mid 1970's.  This widget is
    designed to allow the user to create multiple hot swappable widgets inside of the same
    widget.

    Args:

    Attributes:
        current_widget (QWidget): the widget that is currently set as the main display
        direction (attrs.DIRECTION): what side the mini viewer will be displayed on.
        pip_scale ((float, float)):  fractional percentage of the amount of space that
            the mini viewer will take up in relation to the overall size of the widget.
        swap_key (Qt.KEY): this key will trigger the popup
        widgets (list): of widgets

    """

    def __init__(self, parent=None, widget_types=None):
        super(PiPMainWidget, self).__init__(parent)

        # setup attrs
        self._widgets = []
        if not widget_types:
            widget_types = []
        self._current_widget = None
        self._previous_widget = None
        self._pip_scale = (0.35, 0.35)
        self._enlarged_scale = 0.55
        self._mini_viewer_min_size = (100, 100)
        self._direction = attrs.SOUTH
        self._swap_key = 96

        # create widgets
        self.main_viewer = PiPMainViewer(self)
        # self.main_viewer.setStyleSheet("background-color: rgba(255,255,0,255);")
        self.mini_viewer = PiPMiniViewer(self)
        self.panel_creator_widget = PiPPanelCreatorWidget(self, widget_types=widget_types)
        self.panel_creator_widget.hide()

        self._display_flags_widget = PiPDisplayFlagsWidget(self)
        self._display_flags_widget.hide()
        # self._display_flags_widget.hide()
        # create layout
        """
        Not using a stacked layout as the enter/leave events get borked
        """
        #QStackedLayout(self)
        QVBoxLayout(self)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        #self.layout().addWidget(self.mini_viewer)
        self.layout().addWidget(self._display_flags_widget)
        self.layout().addWidget(self.main_viewer)
        self.layout().addWidget(self.panel_creator_widget)

    """ UTILS (SWAP) """
    def swapWidgets(self):
        """
        Swaps the previous widget with the current widget.

        This allows the user to quickly swap between two widgets.
        """
        if self.previousWidget():
            self.setCurrentWidget(self.previousWidget())

    def swapKey(self):
        return self._swap_key

    def setSwapKey(self, key):
        self._swap_key = key

    """ UTILS """
    def pipScale(self):
        return self._pip_scale

    def setPiPScale(self, pip_scale):
        if isinstance(pip_scale, float):
            pip_scale = (pip_scale, pip_scale)

        self._pip_scale = pip_scale
        self.resizeMiniViewer()

    def enlargedScale(self):
        return self._enlarged_scale

    def setEnlargedScale(self, _enlarged_scale):
        self._enlarged_scale = _enlarged_scale

    def miniViewerMinSize(self):
        return self._mini_viewer_min_size

    def setMiniViewerMinimumSize(self, size):
        """
        Sets the minimum size the mini viewer can go to

        Args:
            size (tuple): (x, y)

        """
        self._mini_viewer_min_size = size
        self.mini_viewer.setMinimumSize(size)

    def resizeMiniViewer(self):
        """
        Main function for resizing the mini viewer

        The core of this function is to set the
            xpos | ypos | width | height
        of the mini viewer, based off of the number of widgets, and its current location on screen.
        """

        # get attrs
        main_widget = getWidgetAncestor(self, AbstractPiPWidget)
        num_widgets = main_widget.numWidgets()

        # preflight
        if num_widgets < 2: return

        # get xpos, ypos, width, height

        # special case for only one widget
        if num_widgets == 2:
            # get height / width
            width = self.width() * self.pipScale()[0]
            height = self.height() * self.pipScale()[1]

            # check for min size
            if width < self.miniViewerMinSize()[0]:
                width = self.miniViewerMinSize()[0]
            if height < self.miniViewerMinSize()[1]:
                height = self.miniViewerMinSize()[1]

            if self.direction() in [attrs.EAST, attrs.WEST]:
                # NORTH EAST
                if self.direction() == attrs.EAST:
                    ypos = 0
                    xpos = self.width() * (1 - self.pipScale()[0])
                    # check minimums
                    if (self.width() - xpos) < self.miniViewerMinSize()[0]:
                        xpos = self.width() - self.miniViewerMinSize()[0]

                # SOUTH WEST
                if self.direction() == attrs.WEST:
                    ypos = self.height() * (1 - self.pipScale()[1])
                    xpos = 0
                    if (self.height() - ypos) < self.miniViewerMinSize()[1]:
                        ypos = self.height() - self.miniViewerMinSize()[1]

            if self.direction() in [attrs.NORTH, attrs.SOUTH]:
                # SOUTH EAST
                if self.direction() == attrs.SOUTH:
                    xpos = self.width() * (1 - self.pipScale()[0])
                    ypos = self.height() * (1 - self.pipScale()[1])

                    # check minimums
                    if (self.width() - xpos) < self.miniViewerMinSize()[0]:
                        xpos = self.width() - self.miniViewerMinSize()[0]

                    if (self.height() - ypos) < self.miniViewerMinSize()[1]:
                        ypos = self.height() - self.miniViewerMinSize()[1]

                # NORTH WEST
                if self.direction() == attrs.NORTH:
                    xpos = 0
                    ypos = 0

        # more than one widget
        if 2 < num_widgets:
            pip_offset = 1 - self.pipScale()[0]

            # get xpos/ypos/height/width
            if self.direction() in [attrs.EAST, attrs.WEST]:
                height = self.height()
                width = self.width() * self.pipScale()[0]
                if self.direction() == attrs.EAST:
                    ypos = 0
                    xpos = self.width() * pip_offset
                    # check minimum size...
                    if (self.width() - xpos) < self.miniViewerMinSize()[0]:
                        xpos = self.width() - self.miniViewerMinSize()[0]
                        width = self.miniViewerMinSize()[0]

                if self.direction() == attrs.WEST:
                    ypos = 0
                    xpos = 0

            if self.direction() in [attrs.NORTH, attrs.SOUTH]:
                height = self.height() * self.pipScale()[1]
                width = self.width()
                if self.direction() == attrs.NORTH:
                    xpos = 0
                    ypos = 0
                if self.direction() == attrs.SOUTH:
                    xpos = 0
                    ypos = self.height() * pip_offset
                    # check minimum size...
                    if (self.height() - ypos) < self.miniViewerMinSize()[1]:
                        ypos = self.height() - self.miniViewerMinSize()[1]
                        height = self.miniViewerMinSize()[1]

        # move/resize mini viewer
        self.mini_viewer.move(int(xpos), int(ypos))
        self.mini_viewer.resize(int(width), int(height))

    def areWidgetNamesShown(self):
        return self._are_widget_names_shown

    def showWidgetDisplayNames(self, enabled):
        self._are_widget_names_shown = enabled
        for widget in self.parent().widgets():
            if enabled:
                widget.main_widget.viewWidget().show()
            else:
                widget.main_widget.viewWidget().hide()

    """ WIDGETS """
    def removeWidget(self, widget):
        #self.widgets().remove(widget)
        widget.setParent(None)
        widget.deleteLater()

    def currentWidget(self):
        return self._current_widget

    def setCurrentWidget(self, widget):
        """
        Sets the current full screen widget

        Args:
            widget (QWidget): widget to be set as full screen
        """
        # reset current widget
        if self._current_widget:
            self._current_widget.setParent(None)
            self.mini_viewer.addWidget(self._current_widget)
            self.setPreviousWidget(self._current_widget)

        # set widget as current
        self._current_widget = widget
        self.mini_viewer.removeWidget(widget)
        self.main_viewer.setWidget(widget)

    def previousWidget(self):
        return self._previous_widget

    def setPreviousWidget(self, widget):
        self._previous_widget = widget

    """ DIRECTION """
    def direction(self):
        return self._direction

    def setDirection(self, direction):
        self._direction = direction
        if direction in [attrs.EAST, attrs.WEST]:
            self.mini_viewer.setDirection(QBoxLayout.TopToBottom)
        elif direction in [attrs.NORTH, attrs.SOUTH]:
            self.mini_viewer.setDirection(QBoxLayout.LeftToRight)

    """ EVENTS """
    def resizeEvent(self, event):
        self.resizeMiniViewer()

        return QWidget.resizeEvent(self, event)

    def keyPressEvent(self, event):
        print('main')
        # swap between this and previous
        if event.key() == 96:
            # pre flight
            widget = getWidgetUnderCursor()
            if widget == self.mini_viewer: return

            # swap previous widget widgets
            is_descendant_of_main_viewer = isWidgetDescendantOf(widget, self.currentWidget())
            if widget == self or is_descendant_of_main_viewer:
                self.swapWidgets()
                return QWidget.keyPressEvent(self, event)

            # set widget under cursor as current
            is_descendant_of_main_widget = isWidgetDescendantOf(widget, self)
            if is_descendant_of_main_widget:
                swap_widget = getWidgetAncestor(widget, PiPMiniViewerWidget)
                self.setCurrentWidget(swap_widget)
                self.mini_viewer.setIsEnlarged(False)
                return QWidget.keyPressEvent(self, event)

        # hotkey swapping
        if event.key() in [Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4, Qt.Key_5]:
            try:
                if event.key() == Qt.Key_1:
                    widget = self.mini_viewer.layout().itemAt(0).widget()
                if event.key() == Qt.Key_2:
                    widget = self.mini_viewer.layout().itemAt(1).widget()
                if event.key() == Qt.Key_3:
                    widget = self.mini_viewer.layout().itemAt(2).widget()
                if event.key() == Qt.Key_4:
                    widget = self.mini_viewer.layout().itemAt(3).widget()
                if event.key() == Qt.Key_5:
                    widget = self.mini_viewer.layout().itemAt(4).widget()
                self.setCurrentWidget(widget)

            except AttributeError:
                # not enough widgets
                pass

        # hide PiP
        if event.key() == Qt.Key_Space:
            self.mini_viewer.hide()
            return

        # escape
        if event.key() == Qt.Key_Escape:
            if self.mini_viewer.isEnlarged():
                obj = getWidgetUnderCursor(QCursor.pos())
                widget = getWidgetAncestor(obj, PiPMiniViewerWidget)
                self.mini_viewer.closeEnlargedView(widget)
                # self.mini_viewer.setIsEnlarged(False)

        return QWidget.keyPressEvent(self, event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.mini_viewer.show()
            return
        return QWidget.keyReleaseEvent(self, event)


class PiPMainViewer(QWidget):
    def __init__(self, parent=None):
        super(PiPMainViewer, self).__init__(parent)
        self.setStyleSheet("background-color: rgba(0,0,255,255)")

        QVBoxLayout(self)
        self.layout().setContentsMargins(0, 0, 0, 0)

    def widget(self):
        return self._widget

    def setWidget(self, widget):
        self._widget = widget
        self.layout().addWidget(widget)
        widget.layout().setContentsMargins(0, 0, 0, 0)


class PiPMiniViewer(QWidget):
    """
    Widget that contains all of the PiPWidgets.

    This widget is an overlay of the MainWidget, and sits at a parallel hierarchy to the PiPMainViewer

    Attributes:
        is_enlarged (bool): if this widget currently has a widget enlarged by a user hover entering over it.
    """
    def __init__(self, parent=None):
        super(PiPMiniViewer, self).__init__(parent)
        self.setStyleSheet("background-color: rgba(0,255,0,255)")

        #QBoxLayout(QBoxLayout.LeftToRight, self)
        QVBoxLayout(self)
        self.layout().setContentsMargins(10, 10, 10, 10)

        # self.setMinimumSize(100, 100)
        self._widgets = []
        self._is_frozen = False
        self._is_exiting = False
        self._is_enlarged = False
        self._temp = False

        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

    def isEnlarged(self):
        return self._is_enlarged

    def setIsEnlarged(self, enabled):
        self._is_enlarged = enabled

    def enlargeWidget(self, widget):
        main_widget = getWidgetAncestor(self, PiPMainWidget)
        self.setIsEnlarged(True)
        # freeze
        self._is_frozen = True

        # set/get attrs
        scale = main_widget.enlargedScale()
        negative_space = 1 - scale
        half_neg_space = negative_space * 0.5
        num_widgets = main_widget.parent().numWidgets()

        # reparent widget
        widget.setParent(main_widget)

        # get widget position / size
        if main_widget.direction() in [attrs.EAST, attrs.WEST]:
            offset = int(self.width() * 0.75)
            ypos = int(main_widget.height() * half_neg_space)
            widget.resize(
                int(main_widget.width() * (scale + half_neg_space)) - offset,
                int(main_widget.height() * scale))

            if main_widget.direction() == attrs.EAST:
                xpos = int(main_widget.width() * (negative_space - half_neg_space))

            if main_widget.direction() == attrs.WEST:
                xpos = 0 + offset

        if main_widget.direction() in [attrs.NORTH, attrs.SOUTH]:
            offset = int(self.height() * 0.75)
            xpos = int(main_widget.width() * half_neg_space)
            widget.resize(
                int(main_widget.width() * scale),
                int(main_widget.height() * (scale + half_neg_space)) - offset)

            if main_widget.direction() == attrs.NORTH:
                ypos = 0 + offset
            if main_widget.direction() == attrs.SOUTH:
                ypos = int(main_widget.height() * (negative_space - half_neg_space))

        # check minimums??

        # show widget
        widget.show()

        # move
        widget.move(xpos, ypos)

        # move cursor
        if main_widget.direction() in [attrs.NORTH, attrs.WEST]:
            if 2 < num_widgets:
                QCursor.setPos(self.mapToGlobal(
                    QPoint(
                        xpos + int(main_widget.width() * scale * 0.5),
                        ypos + int(main_widget.height() * scale * 0.5))))

            if num_widgets == 2 and main_widget.direction() == attrs.WEST:
                QCursor.setPos(self.mapToGlobal(
                    QPoint(
                        xpos + int(main_widget.width() * scale * 0.5),
                        ypos - int(main_widget.height() * scale * 0.5))))
            if num_widgets == 2 and main_widget.direction() == attrs.NORTH:
                QCursor.setPos(self.mapToGlobal(
                    QPoint(
                        xpos + int(main_widget.width() * scale * 0.5),
                        ypos + int(main_widget.height() * scale * 0.5))))

        if main_widget.direction() == attrs.SOUTH:
            # if only one mini viewer widget
            if num_widgets == 2:
                QCursor.setPos(self.mapToGlobal(
                    QPoint(
                        xpos - int(main_widget.width() * scale * 0.5),
                        ypos - int(main_widget.height() * scale * 0.5))))
            # if more than one mini viewer widget
            if 2 < num_widgets:
                QCursor.setPos(self.mapToGlobal(
                    QPoint(
                        xpos + int(main_widget.width() * scale * 0.5),
                        ypos - int(main_widget.height() * scale * 0.5))))

        if main_widget.direction() == attrs.EAST:
            QCursor.setPos(self.mapToGlobal(
                QPoint(
                    xpos - int(main_widget.width() * scale * 0.5),
                    ypos + int(main_widget.height() * scale * 0.5))))

        # unfreeze
        self._is_frozen = False

    """ EVENTS """
    def eventFilter(self, obj, event):
        """

        Args:
            obj:
            event:

        Returns:

        Note:
            _is_frozen (bool): flag to determine if the UI should be frozen for updates
            _temp (bool): flag to determine if this is exiting into a widget that will be moved,
                and then another widget will be in its place.
            _enlarged_object (PiPMiniViewerWidget): when exiting, this is the current object that has
                been enlarged for use.
            _entered_object (PiPMiniViewerWidget): when exiting, this is the object that is under the cursor
                if the user exits into the MiniViewerWidget

        """
        if event.type() in [QEvent.DragEnter, QEvent.Enter]:
            # catch a double exit.
            """
            If the user exits on the first widget, or a widget that will be the enlarged widget,
            it will recurse back and enlarge itself.  This will block that recursion
            """

            # enlarge widget
            if not self._is_frozen:
                self.enlargeWidget(obj)
                # # drag enter
                if event.type() == QEvent.DragEnter:
                    event.accept()

        elif event.type() in [QEvent.Drop, QEvent.DragLeave, QEvent.Leave]:
            self.closeEnlargedView(obj)
        return False

    def closeEnlargedView(self, obj):
        """
        Closes the enlarged viewer, and returns it back to normal PiP mode

        Args:
            obj:

        Returns:
        """

        # exiting
        if not self._is_frozen:
            self._is_frozen = True
            self.addWidget(obj)
            self._is_frozen = False

            # disable enlarged view
            self.setIsEnlarged(False)

    """ DIRECTION """
    def setDirection(self, direction):
        self.layout().setDirection(direction)

    """ WIDGETS """
    def addWidget(self, widget):
        self.layout().insertWidget(widget.index(), widget)
        widget.installEventFilter(self)

        # installHoverDisplaySS(
        #     widget,
        #     name="PIP")

    def createNewWidget(self, widget, name=""):
        """
        Creates a new widget in the mini widget.  This is only when a new widget needs to be instantiated.

        Args:
            widget:
            name:

        Returns (PiPMiniViewerWidget):
        """
        mini_widget = PiPMiniViewerWidget(self, direction=Qt.Vertical, delegate_widget=widget, name=name)
        self.layout().insertWidget(0, mini_widget)
        mini_widget.installEventFilter(self)
        return mini_widget

    def removeWidget(self, widget):
        self.layout().removeWidget(widget)
        widget.removeEventFilter(self)


class PiPMiniViewerWidget(QWidget):
    """
    One PiP Widget that is displayed in the PiPMiniViewer

    Attributes:
        index (int): current index in model
        item (PiPLocalOrganizerItem)
    """
    def __init__(
        self,
        parent=None,
        name="None",
        direction=Qt.Horizontal,
        delegate_widget=None,
    ):
        super(PiPMiniViewerWidget, self).__init__(parent)
        QVBoxLayout(self)
        # self.setStyleSheet("background-color: rgba(255,0,0,255)")
        self._index = 0

        self.main_widget = AbstractLabelledInputWidget(self, name=name, direction=direction, delegate_widget=delegate_widget)
        self.main_widget.viewWidget().delegateWidget().setUserFinishedEditingEvent(self.updateItemDisplayName)

        self.layout().addWidget(self.main_widget)
        self.layout().setContentsMargins(0, 0, 0, 0)
        base_style_sheet = """
        {type}{{
            background-color: rgba{rgba_background};
            color: rgba{rgba_text};
            border: 2px solid rgba{rgba_border};
        }}""".format(
            rgba_background=repr(self.main_widget.rgba_background),
            rgba_border=iColor["rgba_background_01"],
            rgba_text=repr(self.main_widget.rgba_text),
            type=type(self.main_widget).__name__,
        )
        self.main_widget.setBaseStyleSheet(base_style_sheet)

        self.setAcceptDrops(True)

        #self.setMinimumSize(80, 80)
        # installHoverDisplaySS(self, "TEST")

    def updateItemDisplayName(self, widget, value):
        """
        Updates the display name of this label
        Args:
            widget:
            value:
        """
        self.item().columnData()['name'] = value
        self.main_widget.viewWidget().hideDelegate()
        self.main_widget.setName(value)

    def item(self):
        return self._item

    def setItem(self, item):
        self._item = item

    def index(self):
        return self._index

    def setIndex(self, index):
        self._index = index


class PiPDisplayFlagsWidget(AbstractButtonInputWidgetContainer):
    """
    This widget will display all of the optional tabs that the user can display.
        PiPGlobalOrganizerWidget | PiPLocalOrganizerWidget | Settings

    """
    def __init__(self, parent=None, orientation=Qt.Horizontal):
        super(PiPDisplayFlagsWidget, self).__init__(parent, orientation)
        #
        self.setIsMultiSelect(True)

        global_organizer = self.addButton("Global Organizer", "global")
        global_organizer.setUserFinishedEditingEvent(self.toggleGlobalOrganizerWidget)

        local_organizer = self.addButton("Local Organizer", "local")
        local_organizer.setUserFinishedEditingEvent(self.toggleLocalOrganizerWidget)

    def toggleGlobalOrganizerWidget(self, widget, value):
        main_widget = getWidgetAncestor(self, AbstractPiPWidget)
        main_widget.toggleGlobalOrganizerVisibility()

    def toggleLocalOrganizerWidget(self, widget, value):
        main_widget = getWidgetAncestor(self, AbstractPiPWidget)
        main_widget.toggleLocalOrganizerVisibility()


""" ORGANIZER (GLOBAL) """
class PiPGlobalOrganizerItem(AbstractDragDropModelItem):
    """

    Attributes:
        widgetsList (list): of widgets in the format
            [{"widget_name", "constructor_code"},
            {"widget_name", "constructor_code"},
            {"widget_name", "constructor_code"},
            ]
    """
    def __init__(self, parent=None):
        super(PiPGlobalOrganizerItem, self).__init__(parent=parent)


    def widgetsList(self):
        return self._widgets

    def setWidgetsList(self, widgets):
        self._widgets = widgets


class PiPGlobalOrganizerWidget(AbstractModelViewWidget):
    """
    This widget will read all of the AbstractPiPWidgets that the user has created.

    The user can then select an item from this list to have their gui updated.

    Todo:
        populate model
        dynamic updates
        Allow grouping?
        Custom model item?
    """
    def __init__(self, parent=None, widget_types=None):
        super(PiPGlobalOrganizerWidget, self).__init__(parent=parent)

        self.model().setItemType(PiPGlobalOrganizerItem)

        # create save widget
        self._save_widget = PiPOrganizerSaveWidget(self)
        self.addDelegate([], self._save_widget)
        self._save_widget.show()

        # populate
        self.populate()

        self.setIndexSelectedEvent(self.loadPiPWidgetFromSelection)

    def populate(self):
        pip_widgets = self.loadPiPWidgets()
        for widget_name in pip_widgets.keys():
            index = self.model().insertNewIndex(0, name=widget_name)
            item = index.internalPointer()
            item.setWidgetsList(pip_widgets[widget_name])

    def loadPiPWidgetFromSelection(self, item, enabled):
        """
        When an item is selected, this will update the AbstractPiPWidget to the item
        that has been selected
        Args:
            item (PiPGlobalOrganizerItem):
            enabled (bool):
        """
        if enabled:
            pip_name = item.columnData()['name']
            widgets = item.widgetsList()

            main_widget = getWidgetAncestor(self, AbstractPiPWidget)

            # clear pip view
            main_widget.removeAllWidgets()

            # populate pip view
            for widget_name, constructor_code in widgets.items():
                main_widget.createNewWidget(constructor_code, name=widget_name)

            # todo resize not working when single widget...
            # main_widget.mainWidget().resizeMiniViewer()

    def getAllPiPWidgetsNames(self):
        return self.saveWidget().getAllPiPWidgetsNames()

    def loadPiPWidgets(self):
        return self.saveWidget().loadPiPWidgets()

    """ SAVE """
    def saveWidget(self):
        return self._save_widget

    """ SAVE (VIRTUAL) """
    def saveFilePath(self):
        return self.saveWidget().saveFilePath()

    def setSaveFilePath(self, file_path):
        self.saveWidget().setSaveFilePath(file_path)


""" ORGANIZER (LOCAL) """
class PiPLocalOrganizerItem(AbstractDragDropModelItem):
    def __init__(self, parent=None):
        super(PiPLocalOrganizerItem, self).__init__(parent)

    def widget(self):
        return self._widget

    def setWidget(self, widget):
        self._widget = widget

    def constructorCode(self):
        return self._constructor_code

    def setConstructorCode(self, constructor_code):
        self._constructor_code = constructor_code


class PiPLocalOrganizerWidget(AbstractModelViewWidget):
    """
    This widget is in charge of organizing widgets that will be visible in the AbstractPiPWidget
        Abilities include:
            Delete | Rename | Reorder

    Attributes:
        widget_types (dict): of widget names / constructors
            {"name": constructor,
            "QLabel": QLabel,
            "QPushButton":QPushButton}

    Signals:
        Create New Widget -->
        Delete Widget -->
    """
    def __init__(self, parent=None):
        super(PiPLocalOrganizerWidget, self).__init__(parent=parent)

        # setup model
        self.model().setItemType(PiPLocalOrganizerItem)

        # install events
        self.setItemDeleteEvent(self.deleteWidget)
        self.setTextChangedEvent(self.editWidget)
        self.setDropEvent(self.itemReordered)

    """ EVENTS """
    def itemReordered(self, data, items, model, row, parent):
        """
        When an item is drag/dropped, this will update the widget indexes, and reinsert
        the widget into the mini viewer if it is not currently the active widget.
        """
        # get default attrs
        main_widget = getWidgetAncestor(self, AbstractPiPWidget)
        mini_viewer = main_widget.miniViewerWidget()
        widget = items[0].widget()

        # if in mini viewer
        # reset parent and insert back into mini viewer
        if widget.parent() == mini_viewer:
            widget.setParent(None)
            widget.setIndex(row)
            mini_viewer.addWidget(widget)

        # update all widget indexes
        main_widget.updateWidgetIndexes()

    def editWidget(self, item, old_value, new_value):
        item.widget().main_widget.setName(new_value)

    def deleteWidget(self, item):
        """
        When an item is deleted, the corresponding widget is removed from the PiPViewer.

        If the item deleted is the currently viewed item, the previously viewed item will
        automatically be set as the currently viewed item, and if that doesn't exist,
        it will set it to the first widget it can find.

        Args:
            item (to be deleted):
        """
        # get widget
        widget = item.widget()

        # get current widget
        main_widget = getWidgetAncestor(self, AbstractPiPWidget)

        # if current widget
        current_widget = main_widget.currentWidget()
        if widget == current_widget:
            # get first useable widget
            first_widget = main_widget.widgets()[0]
            if first_widget == widget:
                first_widget = main_widget.widgets()[1]

            # set current widget
            if main_widget.previousWidget():
                main_widget.setCurrentWidget(main_widget.previousWidget())
            else:
                main_widget.setCurrentWidget(first_widget)

            # remove previous widget
            main_widget.setPreviousWidget(None)

        # create temp widget
        if main_widget.numWidgets() < 3:
            main_widget.createTempWidget()

        # delete widget
        # if item.widget():
        item.widget().setParent(None)
        item.widget().deleteLater()
        # resize
        main_widget.mainWidget().resizeMiniViewer()

        # print("removing widget -->", item.columnData()['name'])

    """ EVENTS """
    def showEvent(self, event):
        main_widget = getWidgetAncestor(self, AbstractPiPWidget)
        main_widget.setIsLocalOrganizerVisible(True)
        self.setFocus()
        AbstractModelViewWidget.showEvent(self, event)

    def hideEvent(self, event):
        main_widget = getWidgetAncestor(self, AbstractPiPWidget)
        main_widget.setIsLocalOrganizerVisible(False)
        main_widget.setFocus()
        AbstractModelViewWidget.hideEvent(self, event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.hide()
        return AbstractModelViewWidget.keyPressEvent(self, event)


class PiPOrganizerSaveWidget(QWidget):
    """
    constructor is a required arg in the constructor code
    {PiPName: [
        {"widget name": "constructor code"},
        {"widget name": "constructor code"},
        {"widget name": "constructor code"}],
    PiPName: [
        {"widget name": "constructor code"},
        {"widget name": "constructor code"},
        {"widget name": "constructor code"}]
    }
    """
    def __init__(self, parent=None):
        super(PiPOrganizerSaveWidget, self).__init__(parent)
        QVBoxLayout(self)
        # todo name needs to be a list delegate and load all of the current names
        name_list = AbstractListInputWidget(self)
        name_list.dynamic_update = True
        name_list.setCleanItemsFunction(self.getAllPiPWidgetsNames)
        self._name_widget = AbstractLabelledInputWidget(name="Name", delegate_widget=name_list)
        self._save_button = AbstractButtonInputWidget(self, title="Save")

        self.layout().addWidget(self._name_widget)
        self.layout().addWidget(self._save_button)

        # setup save file path
        self._file_path = getDefaultSavePath() + '/.PiPWidgets.json'

        # if doesnt exist create empty JSON
        if not os.path.exists(self.saveFilePath()):
            # Writing JSON data
            with open(self.saveFilePath(), 'w') as f:
                json.dump({}, f)

        # dcc name
        # pip name
        self._save_button.setUserClickedEvent(self.savePiPWidget)

    def nameWidget(self):
        return self._name_widget

    def nameList(self):
        return self._name_list

    def name(self):
        return self._name_widget.delegateWidget().text()

    def getAllPiPWidgetsNames(self):
        widgets_list = [[name] for name in list(self.loadPiPWidgets().keys())]

        return widgets_list

    def loadPiPWidgets(self):
        """
        Loads all of the PiPWidgets as JSON Data


        Returns (dict):
            {PiPName: [
                {"widget name": "constructor code"},
                {"widget name": "constructor code"},
                {"widget name": "constructor code"},]
            }
        """
        return getJSONData(self.saveFilePath())

    def savePiPWidget(self, this):
        """
        When the "Save" button is pressed, this will save the current PiPWidget to the master
        PiPDictionary located at self.saveFilePath()

        Args:
            this (AbstractButtonInputWidget): being pressed

        Returns:

        """
        main_widget = getWidgetAncestor(self, AbstractPiPWidget)
        main_widget.items()
        name = self._name_widget.delegateWidget().text()
        pip_widgets = self.loadPiPWidgets()

        # create pip save dict
        #pip_save_file = {}

        pip_widgets[name] = OrderedDict()
        for item in main_widget.items():
            item_name = item.columnData()['name']
            item_code = item.constructorCode()
            pip_widgets[name][item_name] = item_code

        # save pip file
        if self.saveFilePath():
            # Writing JSON data
            with open(self.saveFilePath(), 'w') as f:
                json.dump(pip_widgets, f)

        print('saving to... ', self.saveFilePath())
        print(pip_widgets)

    def saveFilePath(self):
        """ Returns the current save path for cgwigdets. The default is
                $HOME/.cgwidgets/.PiPWidgets.json
        """
        return self._file_path

    def setSaveFilePath(self, file_path):
        self._file_path = file_path


class PiPPanelCreatorWidget(AbstractListInputWidget):
    def __init__(self, parent=None, widget_types=None):
        super(PiPPanelCreatorWidget, self).__init__(parent)

        self._widget_types = widget_types
        self.populate([[key] for key in widget_types.keys()])
        #self.setUserFinishedEditingEvent(self.createNewWidget)

    def widgetTypes(self):
        return self._widget_types

    def setWidgetTypes(self, widget_types):
        self._widget_types = widget_types

    def createNewWidget(self):
        # preflight
        value = self.text()

        if value not in self.widgetTypes().keys(): return
        main_widget = getWidgetAncestor(self, AbstractPiPWidget)

        # get constructor
        # loc = {}
        # exec(self.widgetTypes()[value], globals(), loc)
        # constructor = loc['constructor']
        #
        # widget_type = constructor(self)
        main_widget.createNewWidget(self.widgetTypes()[value], name=str(value))
        # widget = index.internalPointer().widget()

        # reset widget
        self.setText('')
        self.hide()
        self.clearFocus()

    """ EVENTS """
    def focusOutEvent(self, event):
        self.hide()
        return AbstractListInputWidget.focusOutEvent(self, event)

    def showEvent(self, event):
        main_widget = getWidgetAncestor(self, AbstractPiPWidget)
        main_widget.setIsPanelCreatorVisible(True)
        self.setFocus()
        AbstractListInputWidget.showEvent(self, event)

    def hideEvent(self, event):
        main_widget = getWidgetAncestor(self, AbstractPiPWidget)
        main_widget.setIsPanelCreatorVisible(False)
        main_widget.setFocus()
        AbstractListInputWidget.hideEvent(self, event)

    def keyPressEvent(self, event):

        if event.key() in keylist.ACCEPT_KEYS:
            self.createNewWidget()
        if event.key() == Qt.Key_Escape:
            self.hide()
        return AbstractListInputWidget.keyPressEvent(self, event)


if __name__ == '__main__':
    import sys
    from qtpy.QtWidgets import (QApplication, QListWidget, QAbstractItemView, QPushButton)
    from cgwidgets.utils import centerWidgetOnCursor
    app = QApplication(sys.argv)

    # PiP Widget
    widget_types = {
        "QLabel": """
from qtpy.QtWidgets import QLabel
widget = QLabel(\"TEST\") """,
        "QPushButton":"""
from qtpy.QtWidgets import QPushButton
widget = QPushButton(\"TESTBUTTON\") """
    }
    pip_widget = AbstractPiPWidget(widget_types=widget_types)

#     for x in ("SINE"):
#         child = QLabel(str(x))
#         child.setAlignment(Qt.AlignCenter)
#         child.setStyleSheet("color: rgba(255,255,255,255);")
#         pip_widget.createNewWidget(child, """
# from qtpy.QtWidgets import QLabel
# constructor = QLabel""", name=str(x))

    pip_widget.setPiPScale((0.5, 0.5))
    pip_widget.setEnlargedScale(0.75)
    pip_widget.setDirection(attrs.EAST)
    #pip_widget.showWidgetDisplayNames(False)

    #

    # Drag/Drop Widget
    # drag_drop_widget = QListWidget()
    # drag_drop_widget.setDragDropMode(QAbstractItemView.DragDrop)
    # drag_drop_widget.addItems(['a', 'b', 'c', 'd'])
    # drag_drop_widget.setFixedWidth(100)

    # Main Widget
    main_widget = QWidget()

    main_layout = QHBoxLayout(main_widget)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.addWidget(pip_widget)
    #main_layout.addWidget(drag_drop_widget)

    main_widget.show()
    centerWidgetOnCursor(main_widget)
    main_widget.resize(512, 512)

    sys.exit(app.exec_())
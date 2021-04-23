"""
Todo:
    * Overall cleanup / organization
        mainWidget --> AbstractPiPWidget?
    * Window popup handler
        when a user clicks a popup when in the Mini Viewer, it will register as a
        leave event and leave the current widget
    *
"""
import json
from collections import OrderedDict
import os

from qtpy.QtWidgets import (
    QWidget, QBoxLayout, QVBoxLayout, QSizePolicy, QHBoxLayout, QScrollArea)
from qtpy.QtCore import QEvent, Qt, QPoint
from qtpy.QtGui import QCursor

from cgwidgets.views import AbstractDragDropModelItem
from cgwidgets.utils import attrs, getWidgetUnderCursor, isWidgetDescendantOf, getWidgetAncestor, getDefaultSavePath, getJSONData, showWarningDialogue

from cgwidgets.settings.colors import iColor
from cgwidgets.settings import keylist

from cgwidgets.widgets.AbstractWidgets.AbstractLabelledInputWidget import AbstractLabelledInputWidget
from cgwidgets.widgets.AbstractWidgets.AbstractOverlayInputWidget import AbstractOverlayInputWidget
from cgwidgets.widgets.AbstractWidgets.AbstractModelViewWidget import AbstractModelViewWidget
from cgwidgets.widgets.AbstractWidgets.AbstractShojiWidget.AbstractShojiModelViewWidget import AbstractShojiModelViewWidget


from cgwidgets.widgets import (
    AbstractFrameInputWidgetContainer,
    AbstractListInputWidget,
    AbstractButtonInputWidget,
    AbstractFloatInputWidget,
    AbstractStringInputWidget,
    AbstractLabelWidget,
    AbstractButtonInputWidgetContainer)


class AbstractPiPWidget(AbstractShojiModelViewWidget):
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
        |- SettingsWidget --> FrameInputWidgetContainer

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

    CREATE = 0
    DISPLAY = 1

    def __init__(self, parent=None, save_data=None, widget_types=None):
        super(AbstractPiPWidget, self).__init__(parent)

        # setup default attrs
        self._creation_mode = AbstractPiPWidget.CREATE
        self.setHeaderPosition(attrs.NORTH)
        self.setMultiSelectDirection(Qt.Horizontal)
        self.setMultiSelect(True)
        self.setHeaderItemIsEditable(False)
        self.setHeaderItemIsDragEnabled(False)
        self._temp_widgets = []
        if not widget_types:
            widget_types = []

        """ create widgets """
        # create main pip widget
        self._main_widget = PiPMainWidget(self)

        # setup local organizer widget
        self._local_organizer_widget = PiPLocalOrganizerWidget(self, widget_types)
        self._is_local_organizer_visible = False

        # setup global organizer widget
        self._global_organizer_widget = PiPGlobalOrganizerWidget(self, save_data=save_data)
        self._is_global_organizer_visible = False

        # settings widget
        self._settings_widget = SettingsWidget(self)
        self._is_settings_visible = False

        # help widget
        self._help_widget = PiPHelpWidget(self)

        self.insertShojiWidget(0, column_data={'name': 'Help'}, widget=self._help_widget)
        self.insertShojiWidget(0, column_data={'name': 'Settings'}, widget=self._settings_widget)
        self.insertShojiWidget(0, column_data={'name': 'Organizer'}, widget=self._global_organizer_widget)
        self.insertShojiWidget(0, column_data={'name': 'Views'}, widget=self._local_organizer_widget)
        self.insertShojiWidget(0, column_data={'name': 'PiP'}, widget=self._main_widget)

        # create temp widget
        self.createTempWidget()
        self.createTempWidget()

    def showEvent(self, event):
        indexes = self.model().findItems("PiP", Qt.MatchExactly)
        for index in indexes:
            self.setIndexSelected(index, True)
        return AbstractShojiModelViewWidget.showEvent(self, event)

    """ UTILS """
    def numWidgets(self):
        return len(self.widgets())

    def widgets(self):
        return [index.internalPointer().widget() for index in self.localOrganizerWidget().model().getAllIndexes() if hasattr(index.internalPointer(), "_widget")]

    def items(self):
        """
        Gets all of the items (widgets) from the local organizer

        Returns (list)
        """

        model = self.localOrganizerWidget().model()
        root_item = model.getRootItem()
        return root_item.children()

    def creationMode(self):
        return self._creation_mode

    def setCreationMode(self, mode):
        """
        Sets the current display mode.  If this is set to DISPLAY, then all of the organizers at the top will
        be hidden.  If this is set to DISPLAY, then all of the organizers will be shown to the user.

        The default mode is CREATE

        Args:
            mode (AbstractPiPWidget.MODE):
                DISPLAY | CREATE
        """
        self._creation_mode = mode
        if mode == AbstractPiPWidget.DISPLAY:
            self.headerWidget().hide()
            for widget in self.widgets():
                widget.main_widget.viewWidget().setDisplayMode(AbstractOverlayInputWidget.DISABLED)

        if mode == AbstractPiPWidget.CREATE:
            self.headerWidget().show()
            for widget in self.widgets():
                widget.main_widget.viewWidget().setDisplayMode(AbstractOverlayInputWidget.RELEASE)

    def setDisplayWidget(self, file_name, widget_name):
        """
        Sets the current display widget to the parameters provided.

        This should be used with setCreationMode(PiPWidget.DISPLAY) to setup a default
        display widget.

        Args:
            file_name (str): name of save file to search in
            widget_name  (str): name of widget to find

        Returns:

        """
        model = self.globalOrganizerWidget().model()

        # for each file
        for pip_file_item in model.getRootItem().children():
            # match file name
            if model.getItemName(pip_file_item) == file_name:
                # for each PiPWidget in file
                for pip_widget_item in pip_file_item.children():
                    # match PiPWidget name
                    if model.getItemName(pip_widget_item) == widget_name:
                        # get index
                        index = model.getIndexFromItem(pip_widget_item)
                        self.globalOrganizerWidget().view().clearItemSelection()

                        # set index
                        self.globalOrganizerWidget().view().setIndexSelected(index, True)
                        return

        print('No widgets found in {file_name} --> {widget_name}'.format(file_name=file_name, widget_name=widget_name))

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

    def settingsWidget(self):
        return self._settings_widget

    """ WIDGETS """
    def createNewWidgetFromConstructorCode(self, constructor_code):
        """
        Retuns a QWidget from the constructor code provided.

        The widget returned will be the variable "widget" from the constructor code
        Args:
            constructor_code (code):

        Returns (QWidget):
        """
        loc = {}
        loc['self'] = self
        exec(constructor_code, globals(), loc)
        widget = loc['widget']

        return widget

    def createNewWidget(self, constructor_code, name=""):
        """

        Args:
            widget:
            name:

        Returns:

        """

        # create widget from constructor code
        widget = self.createNewWidgetFromConstructorCode(constructor_code)

        # insert widget into layout
        mini_widget = self.miniViewerWidget().createNewWidget(widget, name=name)

        # set title editable
        if self.creationMode() == AbstractPiPWidget.CREATE:
            mini_widget.main_widget.viewWidget().setDisplayMode(AbstractOverlayInputWidget.RELEASE)
        elif self.creationMode() == AbstractPiPWidget.DISPLAY:
            mini_widget.main_widget.viewWidget().setDisplayMode(AbstractOverlayInputWidget.DISABLED)

        if self.numWidgets() < 1:
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
Views:
Open PiP Widget Organizer.  This will allow you to create/delete
widgets for the current view (the one that you're looking at now).

Organizer:
Global PiPWidget Organizer.  In this tab, you'll be able to save/load
PiPWidgets for future use.

Settings:
Most likely where the settings are

Help:
If you can't figure this out, I can't help you.
\"\"\"
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
    def setSavePath(self, file_paths):
        self.localOrganizerWidget().saveWidget().setPiPSaveData(file_paths)

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
    def toggleItemVisibility(self, item_name, visibility):
        indexes = self.model().findItems(item_name, Qt.MatchExactly)
        for index in indexes:
            self.setIndexSelected(index, visibility)

    def isLocalOrganizerVisible(self):
        return self._is_local_organizer_visible

    def setIsLocalOrganizerVisible(self, visible):
        self._is_local_organizer_visible = visible

    def toggleLocalOrganizerVisibility(self):
        """
        Toggles whether or not the organizer widget is visible to the user

        Note: This is currently hard coded to "Q"
        """

        # if self.miniViewerWidget().__is_frozen:
        if self.miniViewerWidget().isEnlarged():
            obj = getWidgetUnderCursor(QCursor.pos())
            widget = getWidgetAncestor(obj, PiPMiniViewerWidget)
            self.miniViewerWidget().closeEnlargedView(widget)

        # toggle visibility
        self._is_local_organizer_visible = not self.isLocalOrganizerVisible()
        self.toggleItemVisibility("Views", self.isLocalOrganizerVisible())

    def isGlobalOrganizerVisible(self):
        return self._is_global_organizer_visible

    def setIsGlobalOrganizerVisible(self, visible):
        self._is_global_organizer_visible = visible

    def toggleGlobalOrganizerVisibility(self):
        """
        Toggles whether or not the organizer widget is visible to the user

        Note: This is currently hard coded to "Q"
        """

        # if self.miniViewerWidget().__is_frozen:
        if self.miniViewerWidget().isEnlarged():
            obj = getWidgetUnderCursor(QCursor.pos())
            widget = getWidgetAncestor(obj, PiPMiniViewerWidget)
            self.miniViewerWidget().closeEnlargedView(widget)

        # toggle visibility
        self._is_global_organizer_visible = not self.isGlobalOrganizerVisible()
        self.toggleItemVisibility("Organizer", self.isGlobalOrganizerVisible())

    def isSettingsVisible(self):
        return self._is_settings_visible

    def setIsSettingsVisible(self, visible):
        self._is_settings_visible = visible

    def toggleSettingsVisibility(self):
        """
        Toggles whether or not the organizer widget is visible to the user

        Note: This is currently hard coded to "Q"
        """

        if self.miniViewerWidget().isEnlarged():
            obj = getWidgetUnderCursor(QCursor.pos())
            widget = getWidgetAncestor(obj, PiPMiniViewerWidget)
            self.miniViewerWidget().closeEnlargedView(widget)

        # toggle visibility
        self._is_settings_visible = not self.isSettingsVisible()
        self.toggleItemVisibility("Settings", self.isSettingsVisible())

    """ EVENTS """
    def keyPressEvent(self, event):
        # these are registering???
        # if event.key() == Qt.Key_F:
        #     self.toggleLocalOrganizerVisibility()
        # if event.key() == Qt.Key_G:
        #     self.toggleGlobalOrganizerVisibility()
        # if event.key() == Qt.Key_S:
        #     self.toggleSettingsVisibility()
        return AbstractShojiModelViewWidget.keyPressEvent(self, event)


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

    def __init__(self, parent=None):
        super(PiPMainWidget, self).__init__(parent)

        # setup attrs
        self._current_widget = None
        self._previous_widget = None
        self._pip_scale = (0.35, 0.35)
        self._enlarged_scale = 0.55
        self._mini_viewer_min_size = (100, 100)
        self._direction = attrs.SOUTH
        self._swap_key = Qt.Key_Space

        # create widgets
        self.main_viewer = PiPMainViewer(self)
        self.mini_viewer = PiPMiniViewer(self)

        # create layout
        """
        Not using a stacked layout as the enter/leave events get borked
        """
        #QStackedLayout(self)
        QVBoxLayout(self)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        self.layout().addWidget(self.main_viewer)

        #self.layout().addWidget(self.panel_creator_widget)

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
        for widget in getWidgetAncestor(self, AbstractPiPWidget).widgets():
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
        # swap between this and previous
        if event.key() == self.swapKey():
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
        if event.key() == Qt.Key_Q:
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
        if event.key() == Qt.Key_Q:
            self.mini_viewer.show()
            return
        return QWidget.keyReleaseEvent(self, event)


class PiPMainViewer(QWidget):
    def __init__(self, parent=None):
        super(PiPMainViewer, self).__init__(parent)

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

        QVBoxLayout(self)
        self.layout().setContentsMargins(10, 10, 10, 10)

        # self.setMinimumSize(100, 100)
        self._widgets = []
        self.__is_frozen = False
        self._is_exiting = False
        self._is_enlarged = False
        self._temp = False

        self.__popup_widget = None
        self._enlarged_widget = None

        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

    def isEnlarged(self):
        return self._is_enlarged

    def setIsEnlarged(self, enabled):
        self._is_enlarged = enabled

    def enlargedWidget(self):
        return self._enlarged_widget

    def setEnlargedWidget(self, widget):
        self._enlarged_widget = widget

    def enlargeWidget(self, widget):
        main_widget = getWidgetAncestor(self, PiPMainWidget)
        self.setIsEnlarged(True)
        self.setEnlargedWidget(widget)
        # freeze
        self.__is_frozen = True

        # set/get attrs
        scale = main_widget.enlargedScale()
        negative_space = 1 - scale
        half_neg_space = negative_space * 0.5
        num_widgets = getWidgetAncestor(widget, AbstractPiPWidget).numWidgets()

        # reparent widget
        widget.setParent(main_widget)

        # special case for only one mini viewer widget
        if num_widgets == 2:
            xoffset = int(main_widget.width() * negative_space)
            yoffset = int(main_widget.width() * negative_space)
            width = int(main_widget.width() - xoffset)
            height = int(main_widget.height() - yoffset)

            # NORTH WEST
            if main_widget.direction() == attrs.NORTH:
                xpos = 0
                ypos = 0
            # SOUTH EAST
            if main_widget.direction() == attrs.SOUTH:
                xpos = xoffset
                ypos = yoffset
            # NORTH EAST
            if main_widget.direction() == attrs.EAST:
                xpos = xoffset
                ypos = 0
            # SOUTH WEST
            if main_widget.direction() == attrs.WEST:
                xpos = 0
                ypos = yoffset

        # if there are 2 or more mini viewer widgets
        if 2 < num_widgets:
            # get widget position / size
            if main_widget.direction() in [attrs.EAST, attrs.WEST]:
                xoffset = int(main_widget.width() * negative_space)
                yoffset = int(main_widget.width() * negative_space)

                height = int(main_widget.height() - (yoffset * 2))
                ypos = int(yoffset)

                if main_widget.direction() == attrs.EAST:
                    width = int(main_widget.width() - xoffset - self.width() + self.layout().contentsMargins().right())
                    xpos = int(xoffset)

                if main_widget.direction() == attrs.WEST:
                    width = int(main_widget.width() - xoffset - self.width())
                    xpos = self.width() - self.layout().contentsMargins().left()

            if main_widget.direction() in [attrs.NORTH, attrs.SOUTH]:
                offset = int(self.height() * 0.75)
                xpos = int(main_widget.width() * half_neg_space)
                width = int(main_widget.width() * scale)
                height = int(main_widget.height() * (scale + half_neg_space) - offset)

                if main_widget.direction() == attrs.NORTH:
                    ypos = 0 + offset
                if main_widget.direction() == attrs.SOUTH:
                    ypos = int(main_widget.height() * (negative_space - half_neg_space))

        # show enlarged widget
        widget.show()

        # move / resize enlarged widget
        widget.resize(width, height)
        widget.move(xpos, ypos)

        # move cursor to center of enlarged widget
        xcursor = xpos + int(width * 0.5)
        ycursor = ypos + int(height * 0.5)
        QCursor.setPos(main_widget.mapToGlobal(QPoint(xcursor, ycursor)))

        # unfreeze
        self.__is_frozen = False

    """ EVENTS """
    def eventFilter(self, obj, event):
        """

        Args:
            obj:
            event:

        Returns:

        Note:
            __is_frozen (bool): flag to determine if the UI should be frozen for updates
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
            if not self.__is_frozen:
                self.enlargeWidget(obj)
                # # drag enter
                if event.type() == QEvent.DragEnter:
                    event.accept()

            else:
                self.__is_frozen = False

        elif event.type() in [QEvent.Drop, QEvent.DragLeave, QEvent.Leave]:

            new_object = getWidgetUnderCursor()
            # exit popup widget (shown from enlarged widget)
            if obj == self.__popup_widget:
                main_widget = getWidgetAncestor(self, PiPMainWidget)
                enlarged_widget = self.enlargedWidget()
                xpos, ypos = enlarged_widget.pos().x(), enlarged_widget.pos().y()
                width, height = enlarged_widget.width(), enlarged_widget.height()
                xcursor = xpos + (width * 0.5)
                ycursor = ypos + (height * 0.5)
                QCursor.setPos(main_widget.mapToGlobal(QPoint(xcursor, ycursor)))
                self.__popup_widget = None
                self.__is_frozen = True
                return True

            # exit object
            if not isWidgetDescendantOf(new_object, obj):
                self.closeEnlargedView(obj)

            # exit popup
            else:
                self.__popup_widget = obj

        # elif event.type() == QEvent.KeyPress:
        #     print("event filter???")
        return False

    def closeEnlargedView(self, obj):
        """
        Closes the enlarged viewer, and returns it back to normal PiP mode

        Args:
            obj:

        Returns:
        """

        # exiting
        if not self.__is_frozen:
            self.__is_frozen = True
            self.addWidget(obj)
            self.__is_frozen = False

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


""" SETTINGS """
class SettingsWidget(AbstractFrameInputWidgetContainer):
    """
    The user settings for the PiP Widget.

    This will be stored during the Save operation on the master PiPWidget file.

    Attributes:
        widgets (dict): a dictionary of all of the GUI widgets
            {"widget name": widget}
    """
    DEFAULT_SETTINGS = {
        "PiP Scale": {
            "type": attrs.FLOAT,
            "value": 0.5,
            "value_list": [0.01, 0.025, 0.05, 0.1],
            "range": [True, 0.1, 1],
            "code": """main_widget.setPiPScale(float(value))"""},
        "Enlarged Scale": {
            "type": attrs.FLOAT,
            "value": 0.5,
            "value_list": [0.01, 0.025, 0.05, 0.1],
            "range": [True, 0.1, 0.9],
            "code": """main_widget.setEnlargedScale(float(value))"""},
        "Display Titles": {
            "type": attrs.BOOLEAN,
            "value": True,
            "code": """main_widget.showWidgetDisplayNames(value)"""},
        "Direction": {
            "type": attrs.LIST,
            "value": attrs.SOUTH,
            "items": [[attrs.NORTH], [attrs.SOUTH], [attrs.EAST], [attrs.WEST]],
            "code": """
main_widget.setDirection(value)
main_widget.mainWidget().resizeMiniViewer()"""}
    }

    def __init__(self, parent=None):
        # inherit
        super(AbstractFrameInputWidgetContainer, self).__init__(parent, title="Settings", direction=Qt.Vertical)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setIsHeaderEditable(False)

        # create settings dictionary
        self._settings = SettingsWidget.DEFAULT_SETTINGS

        # create all settings widgets
        self._widgets = {}
        for name, setting in self.settings().items():
            input_widget = self.createSettingWidget(name, setting)
            self.widgets()[name] = input_widget

    def widgets(self):
        return self._widgets

    def createSettingWidget(self, name, setting):
        """
        Creates a new setting widget for the values provided
        Args:
            name (str):
            default_value (str):

        """
        from cgwidgets.widgets import AbstractBooleanInputWidget
        # create the user input widget
        if setting['type'] == attrs.FLOAT:
            delegate_widget = AbstractFloatInputWidget(self)
            delegate_widget.setRange(*setting['range'])
            delegate_widget.setText(str(setting['value']))
            delegate_widget.setUseLadder(True, value_list=setting['value_list'])
            delegate_widget.setLiveInputEvent(self.userUpdate)

        elif setting['type'] == attrs.BOOLEAN:
            delegate_widget = AbstractBooleanInputWidget(self)
            delegate_widget.is_selected = setting["value"]

        elif setting['type'] == attrs.LIST:
            delegate_widget = AbstractListInputWidget(self, item_list=setting['items'])
            delegate_widget.setText(setting["value"])
            # delegate_widget.setUserFinishedEditingEvent(self.userUpdate)

        input_widget = AbstractLabelledInputWidget(name=name, delegate_widget=delegate_widget)
        input_widget.viewWidget().setDisplayMode(AbstractOverlayInputWidget.DISABLED)
        input_widget.setDefaultLabelLength(125)

        # add entry into this widget
        self.addInputWidget(input_widget, finished_editing_function=self.userUpdate)

        return input_widget

    def userUpdate(self, widget, value):
        """
        When the user updates a setting, this function will send the signal and call the setting setter.

        Args:
            widget (AbstractFloatInputWidget):
            value (str):

        Returns:
        """
        # get attrs
        name = widget.parent().name()
        self.setSetting(name, value)

    def setSetting(self, name, value):
        """
        Sets the setting value
        Args:
            name (str): of setting to update
            value (str): new value of setting

        Returns:

        """
        # get attrs
        setting = self.settings()[name]
        code = setting['code']
        main_widget = getWidgetAncestor(self, AbstractPiPWidget)

        # prepare local scope
        loc = {}
        loc['self'] = self
        loc['main_widget'] = main_widget
        loc['value'] = value

        # run update
        exec(code, globals(), loc)

        # update local settings dictionary
        self.settings()[name]["value"] = value

    def getSetting(self, name):
        """
        returns the value of one setting
        """
        pass

    def loadSettings(self, settings):
        """
        Loads the settings from a previously stored dictionary

        Args:
            settings (dict): from self.settings()
        """
        # set settings
        for name, value in settings.items():
            # convert values
            # if type(value) == float:
            #     value = str(value)

            # update widget settings
            self.setSetting(name, value)

            # update display settings
            if type(value) == bool:
                self.widgets()[name].delegateWidget().is_selected = value
            else:
                if type(value) == float:
                    value = str(value)
                self.widgets()[name].delegateWidget().setText(str(value))

    def settings(self):
        """
        Returns a dictionary of key pair values representing all of the settings.
        Returns:

        """
        return self._settings

    """ EVENTS """
    def showEvent(self, event):
        main_widget = getWidgetAncestor(self, AbstractPiPWidget)
        main_widget.setIsSettingsVisible(True)
        AbstractFrameInputWidgetContainer.showEvent(self, event)

    def hideEvent(self, event):
        main_widget = getWidgetAncestor(self, AbstractPiPWidget)
        main_widget.setIsSettingsVisible(False)
        main_widget.setFocus()
        AbstractFrameInputWidgetContainer.hideEvent(self, event)


""" ORGANIZER (GLOBAL) """
class PiPGlobalOrganizerItem(AbstractDragDropModelItem):
    """

    Attributes:
        widgetsList (list): of widgets in the format
            [{"widget_name", "constructor_code"},
            {"widget_name", "constructor_code"},
            {"widget_name", "constructor_code"},
            ]
        settings (dict) of settings in form of
            "settings": {"setting name": "value"}},
    """
    GROUP = 0
    PIP = 1
    def __init__(self, parent=None):
        super(PiPGlobalOrganizerItem, self).__init__(parent=parent)
        self._file_path = None
        self._is_locked = False

    def isLocked(self):
        return self._is_locked

    def setIsLocked(self, _is_locked):
        self._is_locked = _is_locked
        self.setIsDropEnabled(False)
        # todo KATANA UPDATE NEEDED
        """ the drag handler can be removed, to allow for drag/drop out of locked items for duplication
        note that also the Views --> AbstractDragDropModel --> dropMimeData will need to be uncommented..."""
        self.setIsDragEnabled(not _is_locked)
        self.setIsEditable(not _is_locked)
        self.setDeleteOnDrop(not _is_locked)

    def filePath(self):
        return self._file_path

    def setFilePath(self, file_path):
        self._file_path = file_path

    def itemType(self):
        return self._item_type

    def setItemType(self, _item_type):
        self._item_type = _item_type

    def settings(self):
        return self._settings

    def setSettings(self, _settings):
        self._settings = _settings

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
    def __init__(self, parent=None, save_data=None):
        super(PiPGlobalOrganizerWidget, self).__init__(parent=parent)
        self.setPresetViewType(AbstractModelViewWidget.TREE_VIEW)
        self.model().setItemType(PiPGlobalOrganizerItem)

        # create save widget
        self._save_widget = PiPSaveWidget(self, save_data=save_data)
        self.addDelegate([], self._save_widget)
        self._save_widget.show()

        # populate
        self.populate()

        # setup events
        self.setItemDeleteEvent(self.deleteItemEvent)
        self.setIndexSelectedEvent(self.loadPiPWidgetFromSelection)
        self.setDropEvent(self.duplicateItemOnDrop)

        # setup deletion warning
        delete_warning_widget = AbstractLabelWidget(text="Are you sure you want to delete this?\n You cannot undo it...")
        self.setDeleteWarningWidget(delete_warning_widget)

        # set flags
        self.setIsRootDropEnabled(False)

    def populate(self):
        # get all data
        all_pip_data = self.getAllPiPData()

        # for each PiP Resource in data
        for name, data in all_pip_data.items():
            # get data
            pip_data = data['data']
            locked = data['locked']
            file_path = data['file_path']

            # Create Group
            parent_index = self.createNewPiPGroupIndex(name, locked, file_path)

            # Create PiP Widgets as children of Group
            for widget_name in reversed(pip_data.keys()):
                self.createNewPiPIndex(
                    widget_name,
                    pip_data[widget_name]["widgets"],
                    pip_data[widget_name]["settings"],
                    parent_index)

    def createNewPiPGroupIndex(self, name, locked, file_path):
        """
        Creates a new Group for
        Args:
            name (str):
            locked (bool): whether or not this group can be manipulated by the user
            file_path (str): path on disk to resource

        Returns:

        """
        # create index
        container_index = self.model().insertNewIndex(0, name=name)
        container_item = container_index.internalPointer()
        container_item.setItemType(PiPGlobalOrganizerItem.GROUP)
        container_item.setFilePath(file_path)

        # setup flags
        container_item.setIsDragEnabled(False)
        if locked:
            container_item.setIsLocked(True)

        return container_index

    def createNewPiPIndex(self, widget_name, widgets, settings, parent, index=0):
        """
        Creates a new PiP Index
        Args:
            widget_name:
            widgets:
            settings:
            index:
            parent:

        Returns:

        """
        index = self.model().insertNewIndex(index, name=widget_name, parent=parent)
        item = index.internalPointer()
        item.setWidgetsList(widgets)
        item.setSettings(settings)
        item.setItemType(PiPGlobalOrganizerItem.PIP)

        # set flags
        item.setIsDropEnabled(False)
        if index.parent().internalPointer().isLocked():
            item.setIsLocked(True)
            #item.setIsEditable(False)

        return item

    """ SAVE ( VIRTUAL ) """
    def getAllPiPWidgetsNames(self):
        return self.saveWidget().getAllPiPWidgetsNames()

    def getAllPiPData(self):
        return self.saveWidget().getAllPiPData()

    def currentPiPFileData(self):
        return self.saveWidget().currentPiPFileData()

    def currentSaveFilePath(self):
        return self.saveWidget().currentSaveFilePath()

    def getPiPSaveData(self):
        return self.saveWidget().getPiPSaveData()

    def setPiPSaveData(self, file_paths):
        self.saveWidget().setPiPSaveData(file_paths)

    """ SAVE """
    def saveWidget(self):
        return self._save_widget

    """ EVENTS """
    def loadPiPWidgetFromSelection(self, item, enabled):
        """
        When an item is selected, this will update the AbstractPiPWidget to the item
        that has been selected
        Args:
            item (PiPGlobalOrganizerItem):
            enabled (bool):
        """
        if enabled:
            if item.itemType() == PiPGlobalOrganizerItem.PIP:
                self.saveWidget().loadPiPWidgetFromItem(item)

            # toggle save button lock
            is_locked = item.isLocked()
            self.saveWidget().updateSaveButtonText(is_locked=is_locked)

    def deleteItemEvent(self, item):
        """
        When the user deletes an item, this will remove the index and the entry
        into the saved PiPFile

        Args:
            item (PiPGlobalOrganizerItem): currently selected by the user to be deleted

        Returns:

        """
        # remove from JSON
        if item.itemType() == PiPGlobalOrganizerItem.PIP:
            # todo
            pip_data = self.currentPiPFileData()
            name = item.columnData()['name']
            del pip_data[name]

            # save json PiP File
            save_widget = self.saveWidget()
            save_widget.dumpPiPDataToJSON(self.currentSaveFilePath(), pip_data)

    def duplicateItemOnDrop(self, data, items, model, row, parent):
        for item in items:
            if not item.deleteOnDrop():
                item.setIsLocked(False)

    def showEvent(self, event):
        main_widget = getWidgetAncestor(self, AbstractPiPWidget)
        main_widget.setIsGlobalOrganizerVisible(True)
        AbstractModelViewWidget.showEvent(self, event)

    def hideEvent(self, event):
        main_widget = getWidgetAncestor(self, AbstractPiPWidget)
        main_widget.setIsGlobalOrganizerVisible(False)
        main_widget.setFocus()
        AbstractModelViewWidget.hideEvent(self, event)


class PiPSaveButtonWidget(AbstractButtonInputWidget):

    SAVE = 0
    UPDATE = 1
    LOCKED = 2
    def __init__(self, parent=None, title="UPDATE"):
        super(PiPSaveButtonWidget, self).__init__(parent=parent, title=title)
        self._mode = PiPSaveButtonWidget.UPDATE

    def setMode(self, _mode):
        self._mode = _mode
        self.updateText()

    def mode(self):
        return self._mode

    def updateText(self):
        """
        When the mode is set, this will update the display text of the button
        """
        if self.mode() == PiPSaveButtonWidget.SAVE:
            self.setText("SAVE")
            return
        if self.mode() == PiPSaveButtonWidget.UPDATE:
            self.setText("UPDATE")
            return
        if self.mode() == PiPSaveButtonWidget.LOCKED:
            self.setText("LOCKED")
            return


class PiPSaveWidget(QWidget):
    """
    constructor is a required arg in the constructor code

    Signals:
        save
            user_button_press
                --> save
                    --> savePiPWidgetItem
                        --> updatePiPWidgetItemInFile
                        --> savePiPWidgetItemToFile
                    --> savePiPGroupItem --> dumpPiPDataToJSON
        load

    Data Structure (Resources):
        getAllPiPData()
            {PiPName: {
                file_path: str,
                locked: bool
                data: {PiPData}},
            PiPName2: {
                file_path: str,
                locked: bool,
                data: {PiPData}}
            }

    Data Structure (PiPData Singular File):
        currentPiPFileData()
            {"PiPName": {
                "widgets": [
                    {"widget name": "constructor code"},
                    {"widget name": "constructor code"},
                    {"widget name": "constructor code"}],
                "settings": {"setting name": "value"}},
            "PiPName2": {
                "widgets": [
                    {"widget name": "constructor code"},
                    {"widget name": "constructor code"},
                    {"widget name": "constructor code"}],
                "settings": {"setting name": "value"}}
            }

    """
    def __init__(self, parent=None, save_data=None):
        super(PiPSaveWidget, self).__init__(parent)
        QVBoxLayout(self)

        # create name list widget
        self._name_list = AbstractListInputWidget(self)
        self._name_list.dynamic_update = True
        self._name_list.setCleanItemsFunction(self.getAllPiPWidgetsNames)
        self._name_list.setUserFinishedEditingEvent(self.updateSaveButtonText)

        # create name widget
        self._name_widget = AbstractLabelledInputWidget(name="Name", delegate_widget=self._name_list)
        self._save_button_widget = PiPSaveButtonWidget(self, title="UPDATE")

        # setup layout
        self.layout().addWidget(self._name_widget)
        self.layout().addWidget(self._save_button_widget)

        # setup save data
        if not save_data:
            save_data = {
                "Default": {
                    "file_path": getDefaultSavePath() + '/.PiPWidgets.json',
                    "locked": True}
            }
        self._save_data = save_data

        # if doesnt exist create empty JSON
        for path, data in self.getPiPSaveData().items():
            file_path = data['file_path']
            if not os.path.exists(file_path):
                # Writing JSON data
                with open(file_path, 'w') as f:
                    json.dump({}, f)

        # setup save event
        self._save_button_widget.setUserClickedEvent(self.save)

    """ WIDGETS """
    def saveButtonWidget(self):
        return self._save_button_widget

    def nameWidget(self):
        return self._name_widget

    """ NAMES """
    def nameList(self):
        return self._name_list

    def name(self):
        return self._name_widget.delegateWidget().text()

    def getAllPiPWidgetsNames(self):
        """
        returns a list for populating the names list
        """
        widgets_list = [[name] for name in sorted(self.getAllPiPWidgetsNamesAsList())]

        return widgets_list

    def getAllPiPWidgetsNamesAsList(self):
        """
        Returns a list of all of the current PiP Widgets in the current container
        that the user is looking at.

        If there is no selection, this will return a list of ALL the PiP Widgets
        """
        widgets_list = []

        # Display Child PiPWidgets of Selection
        if self.currentSaveFilePath():
            for name in self.currentPiPFileData().keys():
                widgets_list.append(name)

        # Display ALL PiPWidgets
        else:
            for key, data in self.getAllPiPData().items():
                data = getJSONData(data['file_path'])
                for name in data.keys():
                    widgets_list.append(name)

        return widgets_list

    """ LOAD """
    def loadPiPWidgetFromItem(self, item):
        """
        Updates the main display to the meta data of the PiPWidget that was selected

        Args:
            item (PiPGlobalOrganizerItem): selected

        Returns:

        """
        widgets = item.widgetsList()
        reversed_widgets = OrderedDict(reversed(list(widgets.items())))

        main_widget = getWidgetAncestor(self, AbstractPiPWidget)

        # clear pip view
        main_widget.removeAllWidgets()

        # populate pip view
        # load widgets
        for widget_name, constructor_code in reversed_widgets.items():
            main_widget.createNewWidget(constructor_code, name=widget_name)

        # load settings
        main_widget.settingsWidget().loadSettings(item.settings())

        # reset previous widget
        main_widget.mainWidget().setPreviousWidget(None)

    def getAllPiPData(self):
        """
        Loads all of the PiPData as JSON Data from ALL of the PiP resource locations

        Returns (dict):
            {PiPName: {
                file_path: str,
                locked: bool
                data: {PiPData}},
            PiPName2: {
                file_path: str,
                locked: bool,
                data: {PiPData}}
            }

        Note: see class notes for PiPData data structure
        """
        pip_data = {}
        for pip_file_name, data in self.getPiPSaveData().items():
            pip_data[pip_file_name] = {}
            pip_data[pip_file_name]["data"] = getJSONData(data['file_path'])
            pip_data[pip_file_name]["locked"] = data["locked"]
            pip_data[pip_file_name]["file_path"] = data["file_path"]
        return pip_data

    def getPiPSaveData(self):
        """Returns the current save data
        "Default": {
            "file_path": getDefaultSavePath() + '/.PiPWidgets.json',
            "locked": True},
        "User": {
            "file_path": getDefaultSavePath() + '/.PiPWidgets_02.json',
            "locked": False}. The default is
        $HOME/.cgwidgets/.PiPWidgets.json
        """
        return self._save_data

    def setPiPSaveData(self, _save_data):
        self._save_data = _save_data

    """ SAVE (UTILS)"""
    def updateSaveButtonText(self, *args, **kwargs):
        # LOCK setting to locked on user selection changed
        if "is_locked" in list(kwargs.keys()):
            is_locked = kwargs["is_locked"]
            if is_locked:
                self.saveButtonWidget().setMode(PiPSaveButtonWidget.LOCKED)
                return

        # if already locked then bypass
        elif self.saveButtonWidget().mode() == PiPSaveButtonWidget.LOCKED:
            return

        # UPDATE if no text
        if not self.name():
            self.saveButtonWidget().setMode(PiPSaveButtonWidget.UPDATE)

        # UPDATE if name exists
        elif self.name() in self.getAllPiPWidgetsNamesAsList():
            self.saveButtonWidget().setMode(PiPSaveButtonWidget.UPDATE)

        # SAVE new
        else:
            self.saveButtonWidget().setMode(PiPSaveButtonWidget.SAVE)

    def getPiPWidgetItemDict(self):
        """
        Gets the dictionary for a singular PiPWidgetItem to be saved as entry in the
        master PiPFile located at saveFilePath
        Returns (OrderedDict):
            "PiPName": {
                "widgets": [
                    {"widget name": "constructor code"},
                    {"widget name": "constructor code"},
                    {"widget name": "constructor code"}],
                "settings": {"setting name": "value"}
            }
        """
        main_widget = getWidgetAncestor(self, AbstractPiPWidget)

        # create pip save dict
        item_dict = OrderedDict()

        # store widgets in dict
        item_dict["widgets"] = OrderedDict()
        for item in main_widget.items():
            item_name = item.columnData()['name']
            item_code = item.constructorCode()
            item_dict["widgets"][item_name] = item_code

        # store settings in dict
        settings = {}
        for setting in main_widget.settingsWidget().settings().keys():
            settings[setting] = main_widget.settingsWidget().settings()[setting]["value"]

        item_dict["settings"] = settings

        return item_dict

    def dumpPiPDataToJSON(self, file_path, data):
        if file_path:
            # Writing JSON data
            with open(file_path, 'w') as f:
                json.dump(data, f)

    def currentSaveFilePath(self):
        """
        Gets the current PiPSaveFilePath

        Returns:
        """
        global_organizer = getWidgetAncestor(self, PiPGlobalOrganizerWidget)
        indexes = global_organizer.getAllSelectedIndexes()

        if 0 < len(indexes):
            # get item
            item = indexes[0].internalPointer()

            # return if GROUP
            """ Can't save/update an entire group as only one item is selectable at a time..."""
            if item.itemType() == PiPGlobalOrganizerItem.PIP:
                item = item.parent()

            # get file path
            file_path = item.filePath()

            return file_path

        # return none to bypass if I failed miserably at coding stuff
        return None

    def currentPiPFileData(self):
        """
        Gets the current PiPFiles data
        Returns (dict):
        {"PiPName": {
            "widgets": [
                {"widget name": "constructor code"},
                {"widget name": "constructor code"},
                {"widget name": "constructor code"}],
            "settings": {"setting name": "value"}},
        "PiPName2": {
            "widgets": [
                {"widget name": "constructor code"},
                {"widget name": "constructor code"},
                {"widget name": "constructor code"}],
            "settings": {"setting name": "value"}}
        }
        """
        return getJSONData(self.currentSaveFilePath())

    """ SAVE """
    def save(self, this):
        """
        When the user clicks the save Button, depending on the current name
        this will choose to either SAVE or UPDATE the PiPFile

        Args:
            this (AbstractButtonInputWidget): being pressed
            _exists (bool): determines if the item should be deleted or not
        """
        # preflight
        if self.saveButtonWidget().mode() == PiPSaveButtonWidget.LOCKED: return

        file_path = self.currentSaveFilePath()
        if not file_path: return
        main_widget = getWidgetAncestor(self, AbstractPiPWidget)
        selection = main_widget.globalOrganizerWidget().getAllSelectedIndexes()
        if len(selection) == 0: return

        # get item
        item = selection[0].internalPointer()

        # Save / Update PiPFile
        if item.itemType() == PiPGlobalOrganizerItem.GROUP:
            if not self.nameWidget().delegateWidget().text():
                self.updatePiPGroupItem(item)
            # Save / Update PiPWidgetItem if Group Selected
            else:
                self.savePiPWidgetItem()

        # Save / Update PiPWidgetItem
        if item.itemType() == PiPGlobalOrganizerItem.PIP:
            self.savePiPWidgetItem()

    def updatePiPGroupItem(self, parent_item):
        """
        Updates the current PiPFile, this could need to happen if:
            - new items have been drag/dropped in from a locked one
            - An item has been rearranged via drag/drop

        Args:
            parent_item (PiPGlobalOrganizerItem): Currently selected by user, must have an itemType() of GROUP

        {"PiPName": {
        "widgets": [
            {"widget name": "constructor code"},
            {"widget name": "constructor code"},
            {"widget name": "constructor code"}],
        "settings": {"setting name": "value"}},
        """

        # create new dictionary...
        pip_data = {}

        # run through each item in parent
        for child in parent_item.children():
            name = child.columnData()['name']
            widgets = child.widgetsList()
            settings = child.settings()

            # store dictionary
            pip_data[name] = {}
            pip_data[name]["widgets"] = widgets
            pip_data[name]["settings"] = settings

        # store as dictionary entry...
        self.dumpPiPDataToJSON(self.currentSaveFilePath(), pip_data)

    def savePiPWidgetItem(self):
        """
        Saves a singular PiPItem in the GlobalOrganizer to the master PiPDictionary
        located at self.currentSaveFilePath()
        """
        main_widget = getWidgetAncestor(self, AbstractPiPWidget)

        # update
        if self.saveButtonWidget().mode() == PiPSaveButtonWidget.UPDATE:
            _exists = True
            new_item, orig_item = self.updatePiPWidgetItemInFile()

        # save
        elif self.saveButtonWidget().text() == PiPSaveButtonWidget.SAVE:
            _exists = False
            row = 0
            name = self.nameWidget().delegateWidget().text()

            # get row
            """ If the PiP Widget exists, this will get the row so that
            a new item can be created, and then destroy the old one"""
            if name in self.getAllPiPWidgetsNamesAsList():
                _exists = True

                # get parent of current index to search from
                selected_indexes = main_widget.globalOrganizerWidget().getAllSelectedIndexes()
                if 0 < len(selected_indexes):
                    selected_index = selected_indexes[0]
                    selected_item = selected_index.internalPointer()
                    if selected_item.itemType() == PiPGlobalOrganizerItem.GROUP:
                        parent_index = selected_index
                    elif selected_item.itemType() == PiPGlobalOrganizerItem.PIP:
                        parent_index = selected_index.parent()

                    # find row
                    indexes = main_widget.globalOrganizerWidget().model().findItems(name, index=parent_index)
                    for index in indexes:
                        orig_item = index.internalPointer()
                        row = index.row()
                else:
                    print("Select something...")

            # create new widget
            new_item = self.savePiPWidgetItemToFile(index=row)

        # remove old widget
        if _exists:
            main_widget.globalOrganizerWidget().deleteItem(orig_item)

        # reselect index
        index = main_widget.globalOrganizerWidget().model().getIndexFromItem(new_item)
        main_widget.globalOrganizerWidget().view().clearItemSelection()
        main_widget.globalOrganizerWidget().view().setIndexSelected(index, True)

    def savePiPWidgetItemToFile(self, index=0):
        """
        When the "Save" button is pressed, this will save the current PiPWidgetItem to the
        master PiPFile

        Returns:
        """

        name = self.nameWidget().delegateWidget().text()
        pip_data = self.currentPiPFileData()

        # save pip file
        pip_data[name] = self.getPiPWidgetItemDict()
        self.dumpPiPDataToJSON(self.currentSaveFilePath(), pip_data)

        # create new index
        main_widget = getWidgetAncestor(self, AbstractPiPWidget)

        # get parent index (if Group/PiP is selected)
        selected_index = main_widget.globalOrganizerWidget().getAllSelectedIndexes()[0]
        if selected_index.internalPointer().itemType() == PiPGlobalOrganizerItem.PIP:
            parent_index = selected_index.parent()
        else:
            parent_index = selected_index
        item = main_widget.globalOrganizerWidget().createNewPiPIndex(
            name, pip_data[name]["widgets"], pip_data[name]["settings"], parent_index, index=index)

        # reset text
        self.nameWidget().delegateWidget().setText('')
        self.updateSaveButtonText()

        print('saving to... ', self.getPiPSaveData())
        return item

    def updatePiPWidgetItemInFile(self):
        """
        Updates the currently selected PiPWidgetItem if the user has made changes.
        This will only work, if the current text is empty in the name widget.
        """
        main_widget = getWidgetAncestor(self, AbstractPiPWidget)
        selected_indexes = main_widget.globalOrganizerWidget().getAllSelectedIndexes()

        # get name
        name = None
        for index in selected_indexes:
            orig_item = index.internalPointer()
            name = orig_item.columnData()['name']

        if name:
            self.nameWidget().delegateWidget().setText(name)
            new_item = self.savePiPWidgetItemToFile(index=index.row())

        return new_item, orig_item


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
    def __init__(self, parent=None, widget_types=None):
        super(PiPLocalOrganizerWidget, self).__init__(parent=parent)

        # setup model
        self.model().setItemType(PiPLocalOrganizerItem)

        # install events
        self.setItemDeleteEvent(self.deleteWidget)
        self.setTextChangedEvent(self.editWidget)
        self.setDropEvent(self.itemReordered)

        # panel creator widget
        if not widget_types:
            widget_types = {}

        self.panel_creator_widget = PiPPanelCreatorWidget(self, widget_types=widget_types)
        self.addDelegate([Qt.Key_C], self.panel_creator_widget, modifier=Qt.AltModifier, focus=True)
        self.panel_creator_widget.show()

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
        AbstractModelViewWidget.showEvent(self, event)

    def hideEvent(self, event):
        main_widget = getWidgetAncestor(self, AbstractPiPWidget)
        main_widget.setIsLocalOrganizerVisible(False)
        main_widget.setFocus()
        AbstractModelViewWidget.hideEvent(self, event)


class PiPPanelCreatorWidget(AbstractListInputWidget):
    def __init__(self, parent=None, widget_types=None):
        super(PiPPanelCreatorWidget, self).__init__(parent)

        self._widget_types = widget_types
        self.populate([[key] for key in sorted(widget_types.keys())])
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
        main_widget.createNewWidget(self.widgetTypes()[value], name=str(value))

        # reset widget
        self.setText('')
        self.setFocus()

    def keyPressEvent(self, event):
        if event.key() in keylist.ACCEPT_KEYS:
            self.createNewWidget()

        return AbstractListInputWidget.keyPressEvent(self, event)


""" HELP """
class PiPHelpWidget(QScrollArea):
    def __init__(self, parent=None):
        super(PiPHelpWidget, self).__init__(parent)

        # create help widget
        self.help_widget = AbstractLabelWidget(self)

        # setup help widget attrs
        self.help_widget.textWidget().setIndent(20)
        self.help_widget.textWidget().setAlignment(Qt.AlignLeft)
        self.help_widget.setWordWrap(True)
        self.help_widget.setText("""Views:
Widgets that will exist in the PiP View you can create more widgets using the empty field at the bottom of this widget

Organizer:
PiPWidgets can be saved/loaded through this tab.  This Tab Shows all of the PiPWidgets, selecting an organizer will load that PiPWidget setup.

Any changes made will require you to hit the save/update button at the bottom to store these changes to disk.  By default this button will save/update the selected item.  If a Group is selected, then this will update the entire Group, while if an individual item is selected, it will update that singular entry. 

Hotkeys:
< Q >Hold to hide all widgets

< Space >
Swap current display widget with previously displayed widget.  If this is pressed when the MiniViewer is active, then the widget that is currently enlarged will be set as the actively displayed widget.

< 1 | 2 | 3 | 4 | 5 >
Sets the current display widget relative to the number pressed, and the widget available to be viewed in the Mini Viewer.
""")

        # setup scroll area
        self.setWidget(self.help_widget)
        self.setWidgetResizable(True)


if __name__ == '__main__':
    import sys
    import os

    os.environ['QT_API'] = 'pyside2'
    from qtpy import API_NAME

    from qtpy.QtWidgets import (QApplication, QListWidget, QAbstractItemView, QPushButton)
    from cgwidgets.utils import centerWidgetOnCursor
    app = QApplication(sys.argv)

    # PiP Widget
    save_data = {
        "Foo": {
            "file_path": getDefaultSavePath() + '/.PiPWidgets.json',
            "locked": True},
        "Bar": {
            "file_path": getDefaultSavePath() + '/.PiPWidgets_02.json',
            "locked": False}
    }
    widget_types = {
        "QLabel": """
from qtpy.QtWidgets import QLabel
widget = QLabel(\"TEST\") """,
        "QPushButton":"""
from qtpy.QtWidgets import QPushButton
widget = QPushButton(\"TESTBUTTON\") """
    }
    pip_widget = AbstractPiPWidget(save_data=save_data, widget_types=widget_types)

    pip_widget.setPiPScale((0.25, 0.25))
    pip_widget.setEnlargedScale(0.75)
    pip_widget.setDirection(attrs.WEST)
    #pip_widget.showWidgetDisplayNames(False)

    #

    # Drag/Drop Widget
    # drag_drop_widget = QListWidget()
    # drag_drop_widget.setDragDropMode(QAbstractItemView.DragDrop)
    # drag_drop_widget.addItems(['a', 'b', 'c', 'd'])
    # drag_drop_widget.setFixedWidth(100)

    # Main Widget

    # pip main widget
    main_widget = QWidget()

    main_layout = QHBoxLayout(main_widget)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.addWidget(pip_widget)

    # test splitter
    # from qtpy.QtWidgets import QSplitter, QLabel
    # splitter = QSplitter()
    # splitter.addWidget(QLabel("test"))
    # splitter.addWidget(QLabel("this"))
    # main_layout.addWidget(splitter)

    main_widget.show()
    centerWidgetOnCursor(main_widget)
    main_widget.resize(512, 512)


    # setup display widget
    pip_widget.setDisplayWidget("Bar", "test02")
    # pip_widget.setCreationMode(AbstractPiPWidget.DISPLAY)

    sys.exit(app.exec_())
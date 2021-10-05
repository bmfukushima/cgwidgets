"""
The PiPWidget is designed to display multiple widgets simultaneously to the user.

Similar to the function that was provided to TV's in the mid 1970's.  This widget is
designed to allow the user to create multiple hot swappable widgets inside of the same
widget.

Hierarchy:
    AbstractPiPOrganizerWidget --> (AbstractShojiModelViewWidget)
        |- AbstractPiPDisplayWidget --> (QWidget)
        |    |- QVBoxLayout
        |    |    |- PiPMainViewer --> (QWidget)
        |    |    |- PiPMiniViewerWidgetCreator --> (AbstractListInputWidget)
        |    |- spacer_widget (QLabel)
        |    |- MiniViewer (QWidget)
        |        |- QBoxLayout
        |            |-* AbstractPopupBarItemWidget --> QWidget
        |                    |- QVBoxLayout
        |                    |- AbstractLabelledInputWidget
        |- miniViewerOrganizerWidget --> AbstractModelViewWidget
        |- CreatorWidget (Extended...)
        |- GlobalOrganizerWidget --> AbstractModelViewWidget
        |- SettingsWidget --> FrameInputWidgetContainer

Data Structure (save widget):
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

Signals:
    Swap (Enter):
        Upon user cursor entering a widget, that widget becomes the main widget

        AbstractPopupBarWidget --> EventFilter --> EnterEvent
        AbstractPopupBarWidget --> EventFilter --> LeaveEvent

    Swap (Key Press):
        Upon user key press on widget, that widget becomes the main widget.
        If the key is pressed over a MiniViewerWidget, it will become the main widget.
        If it is pressed over the MainWidget, it will swap it with the previous widget

        Default is "Space"

        AbstractPiPDisplayWidget --> keyPressEvent --> setCurrentWidget, swapWidgets

    Swap Previous (Key Press)
        Press ~, main widget is swapped with previous main widget
        AbstractPiPDisplayWidget --> keyPressEvent --> setCurrentWidget
    Quick Drag ( Drag Enter ):
        Upon user drag enter, the mini widget becomes large to allow easier dropping
        AbstractPopupBarWidget --> EventFilter --> Drag Enter
                                      --> Enter
                                      --> Drop
                                      --> Drag Leave
                                      --> Leave
    HotSwap (Key Press 1-5):
        AbstractPiPDisplayWidget --> keyPressEvent --> setCurrentWidget
    Toggle previous widget
        AbstractPiPDisplayWidget --> keyPressEvent --> swapWidgets
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

    miniViewerCreatorWidget:
        show (c):
            keyPressEvent --> toggleCreatorVisibility --> show
        hide (esc)
"""
""" TODO
    * Organizer has issues selecting/reselecting/saving?
        mini viewer doesn't exist?
    * Delete (Global Organizer)
        After delete, wrong widget is displayed in the PiPView

    * Mouse moving to fast bug
        AbstractPopupBarWidget --> enlargeWidget | closeEnlargedView
        Can potentially add a flag on the enlarged/closed, so that if the flag is active
        for the other one, then it will recursively call itself until the flag has been deactivated.
        This would ensure that double events don't happen...
        
        Currently has a timer set in the close closeEnlargedView() to block the signal from going to fast...
    * Clean up mini viewer resize
        PiPGlobalOrganizerWidget --> loadPiPWidgetFromSelection ( This runs twice for some reason)
        PiPSaveWidget --> loadPiPWidgetFromItem
        AbstractPiPOrganizerWidget --> createNewWidget --> resizeMiniViewer
    * Display Name (bug)
        When display names is active, when leaving the mini viewer, the widgets
        will "wobble" for a few seconds.  This is only when display names is active...
        
        Potentially a resize in the actual labelled widget?
    * Display Name
        Remove ability to adjust display name in MiniViewerWidgets
            .headerWidget().setName(new_value) ?
            MiniViewerWidget --> headerWidget()
        For now this is just force disabled, I think
"""
import json
from collections import OrderedDict
import os

from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QSplitter, QSplitterHandle, QApplication)
from qtpy.QtCore import QEvent, Qt

from cgwidgets.views import AbstractDragDropModelItem
from cgwidgets.utils import (
    getWidgetUnderCursor,
    isWidgetDescendantOf,
    isCursorOverWidget,
    getWidgetAncestor,
    getDefaultSavePath,
    getJSONData,
    installResizeEventFinishedEvent,
    runDelayedEvent)

from cgwidgets.settings import attrs, iColor, keylist

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
    AbstractButtonInputWidgetContainer,
    AbstractSplitterWidget
    )

from .AbstractPopupBarWidget import AbstractPopupBarWidget, AbstractPopupBarItemWidget


class AbstractPiPOrganizerWidget(AbstractShojiModelViewWidget):
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

    CREATE = 0
    DISPLAY = 1

    def __init__(self, parent=None, save_data=None, widget_types=None):
        super(AbstractPiPOrganizerWidget, self).__init__(parent)

        # setup default attrs
        self._creation_mode = AbstractPiPOrganizerWidget.CREATE
        self.setHeaderPosition(attrs.NORTH)
        self.setMultiSelectDirection(Qt.Horizontal)
        self.setMultiSelect(True)
        self.setHeaderItemIsEditable(False)
        self.setHeaderItemIsDraggable(False)
        self.setHeaderItemIsDroppable(False)
        self.setHeaderItemIsDeletable(False)
        self.setHeaderItemIsEnableable(False)

        self._temp_widgets = []
        if not widget_types:
            widget_types = []

        """ create widgets """
        # create main pip widget
        self._pip_display_widget = AbstractPiPDisplayWidget(self)
        self._pip_display_widget.setIsStandalone(False)
        # setup local organizer widget
        self._local_organizer_widget = PiPMiniViewerOrganizerWidget(self, widget_types)
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
        self.insertShojiWidget(0, column_data={'name': 'PiP'}, widget=self._pip_display_widget)

        # create temp widget
        self.createTempWidget()
        self.createTempWidget()

    def showEvent(self, event):
        indexes = self.model().findItems("PiP", Qt.MatchExactly)
        for index in indexes:
            self.setIndexSelected(index, True)
        return AbstractShojiModelViewWidget.showEvent(self, event)

    """ UTILS """
    def widgets(self):
        return self.miniViewerOrganizerWidget().widgets()

    def items(self):
        """
        Gets all of the items (widgets) from the local organizer

        Returns (list)
        """

        model = self.miniViewerOrganizerWidget().model()
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
            mode (AbstractPiPOrganizerWidget.MODE):
                DISPLAY | CREATE
        """
        self._creation_mode = mode
        if mode == AbstractPiPOrganizerWidget.DISPLAY:
            self.headerWidget().hide()
            for widget in self.widgets():
                widget.headerWidget().setDisplayMode(AbstractOverlayInputWidget.DISABLED)

        if mode == AbstractPiPOrganizerWidget.CREATE:
            self.headerWidget().show()
            for widget in self.widgets():
                widget.headerWidget().setDisplayMode(AbstractOverlayInputWidget.RELEASE)

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
    def pipDisplayWidget(self):
        return self._pip_display_widget

    def miniViewerWidget(self):
        return self.pipDisplayWidget().miniViewerWidget()

    def mainViewerWidget(self):
        return self.pipDisplayWidget().mainViewerWidget()

    def miniViewerOrganizerWidget(self):
        return self._local_organizer_widget

    def globalOrganizerWidget(self):
        return self._global_organizer_widget

    def miniViewerCreatorWidget(self):
        return self.pipDisplayWidget()._panel_creator_widget

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
        return self.pipDisplayWidget().createNewWidgetFromConstructorCode(constructor_code)

    def createNewWidget(self, constructor_code, name="", resize_mini_viewer=True):
        """
        Args:
            constructor_code (str):
            name (str):
            resize_mini_viewer (bool): if the miniViewerWidget should be updated or not

        Returns (QModelIndex):

        """
        # create mini viewer widget
        mini_viewer_widget = self.pipDisplayWidget().createNewWidget(constructor_code, name, resize_mini_viewer)

        # create new index
        index = self.miniViewerOrganizerWidget().model().insertNewIndex(0, name=name)

        item = index.internalPointer()
        item.setWidget(mini_viewer_widget)
        item.setConstructorCode(constructor_code)

        # mini_viewer_widget.setIndex(0)
        mini_viewer_widget.setItem(item)

        # update indexes
        self.miniViewerWidget().updateWidgetIndexes()
        # self.updateWidgetIndexes()

        # # destroy temp widgets
        if 1 < self.pipDisplayWidget().numWidgets():
            if name != "":
                self.removeTempWidget()

        return index

    def updateWidgetIndexes(self):
        """
        Runs through all of the widgets and resets their indexes.

        This will need to be done every time a new widget is added
        """
        for index in self.miniViewerOrganizerWidget().model().getAllIndexes():
            item = index.internalPointer()
            if hasattr(item, "_widget"):
                item.widget().setIndex(index.row())

    def removeAllWidgets(self):
        """ Clears all of the widgets from the current AbstractPiPOrganizerWidget"""
        self.pipDisplayWidget().removeAllWidgets()
        self.miniViewerOrganizerWidget().model().clearModel()

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
        item.setIsDraggable(False)
        item.setIsEnabled(False)
        # item.setIsEditable(False)

        # setup widget
        item.widget().headerWidget().setDisplayMode(AbstractOverlayInputWidget.DISABLED)

    def removeTempWidget(self):
        """
        Removes the first temp widget from the tempWidgets list
        """
        model = self.miniViewerOrganizerWidget().model()
        indexes = model.findItems("", match_type=Qt.MatchExactly)
        if 0 < len(indexes):
            model.deleteItem(indexes[0].internalPointer(), event_update=True)

    """ PROPERTIES """
    def isMiniViewerWidget(self):
        return self.pipDisplayWidget().isMiniViewerWidget()

    def setIsMiniViewerWidget(self, is_mini_viewer_widget):
        self.pipDisplayWidget().setIsMiniViewerWidget(is_mini_viewer_widget)

    """ VIRTUAL PROPERTIES """
    def setSavePath(self, file_paths):
        self.miniViewerOrganizerWidget().saveWidget().setPiPSaveData(file_paths)

    def direction(self):
        return self.pipDisplayWidget().direction()

    def setDirection(self, direction):
        self.pipDisplayWidget().setDirection(direction)

    def swapKey(self):
        return self.pipDisplayWidget().swapKey()

    def setSwapKey(self, key):
        self.pipDisplayWidget().setSwapKey(key)

    def pipScale(self):
        return self.pipDisplayWidget().pipScale()

    def setPiPScale(self, pip_scale):
        self.pipDisplayWidget().setPiPScale(pip_scale)

    def enlargedScale(self):
        return self.pipDisplayWidget().enlargedScale()

    def setEnlargedScale(self, _enlarged_scale):
        self.pipDisplayWidget().setEnlargedScale(_enlarged_scale)

    def setIsDisplayNamesShown(self, enabled):
        self.pipDisplayWidget().setIsDisplayNamesShown(enabled)

    def currentWidget(self):
        return self.pipDisplayWidget().currentWidget()

    def setCurrentWidget(self, current_widget):
        self.pipDisplayWidget().setCurrentWidget(current_widget)

    def previousWidget(self):
        return self.pipDisplayWidget().previousWidget()

    def setPreviousWidget(self, previous_widget):
        self.pipDisplayWidget().setPreviousWidget(previous_widget)

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

        # if self.miniViewerWidget()._is_frozen:
        # if self.miniViewerWidget().isEnlarged():
        # close enlarged view
        # obj = getWidgetUnderCursor(QCursor.pos())
        # widget = getWidgetAncestor(obj, AbstractPopupBarItemWidget)
        # self.miniViewerWidget().closeEnlargedView(widget)
        self.miniViewerWidget().closeEnlargedView()

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

        # if self.miniViewerWidget()._is_frozen:
        # if self.miniViewerWidget().isEnlarged():
        # obj = getWidgetUnderCursor(QCursor.pos())
        # widget = getWidgetAncestor(obj, AbstractPopupBarItemWidget)
        # self.miniViewerWidget().closeEnlargedView(widget)
        self.miniViewerWidget().closeEnlargedView()

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

        # if self.miniViewerWidget().isEnlarged():
        #     obj = getWidgetUnderCursor(QCursor.pos())
        #     widget = getWidgetAncestor(obj, AbstractPopupBarItemWidget)
        #     self.miniViewerWidget().closeEnlargedView(widget)
        self.miniViewerWidget().closeEnlargedView()

        # toggle visibility
        self._is_settings_visible = not self.isSettingsVisible()
        self.toggleItemVisibility("Settings", self.isSettingsVisible())

    """ EVENTS """
    def keyPressEvent(self, event):
        # if event.key() == self.swapKey():
        #     self.pipDisplayWidget().swapWidgets()
        # these are registering???
        # if event.key() == Qt.Key_F:
        #     self.toggleLocalOrganizerVisibility()
        # if event.key() == Qt.Key_G:
        #     self.toggleGlobalOrganizerVisibility()
        # if event.key() == Qt.Key_S:
        #     self.toggleSettingsVisibility()
        return AbstractShojiModelViewWidget.keyPressEvent(self, event)


class AbstractPiPDisplayWidget(QWidget):
    """The PiPWidget is designed to display multiple widgets simultaneously to the user.

    Similar to the function that was provided to TV's in the mid 1970's.  This widget is
    designed to allow the user to create multiple hot swappable widgets inside of the same
    widget.

    Attributes:
        current_widget (QWidget): the widget that is currently set as the main display
        direction (attrs.DIRECTION): what side the mini viewer will be displayed on.
        hotkey_swap_key (list): of Qt.Key that will swap to the corresponding widget in the miniViewerWidget().

            The index of the Key in the list, is the index of the widget that will be swapped to.
        is_mini_viewer_widget (bool): determines if this is a child of a MiniViewerWidget.
        is_mini_viewer_shown (bool): if the mini viewer is currently visible.
            This is normally toggled with the "Q" key
        is_standalone (bool): determines if this is a child of the PiPAbstractOrganizer.
            If True, this means that this display is a standalone..
        pip_scale ((float, float)):  fractional percentage of the amount of space that
            the mini viewer will take up in relation to the overall size of the widget.
        swap_key (Qt.KEY): this key will trigger the popup
        widgets (list): of widgets
    """

    def __init__(self, parent=None, is_mini_viewer_widget=False):
        super(AbstractPiPDisplayWidget, self).__init__(parent)

        # setup attrs
        self._num_widgets = 0
        self._is_frozen = True
        self._current_widget = None
        self._previous_widget = None
        self._pip_scale = (0.35, 0.35)

        #self._enlarged_scale = 0.55
        self._mini_viewer_min_size = (100, 100)
        self._is_dragging = True
        self._is_mini_viewer_shown = True
        self._is_mini_viewer_widget = is_mini_viewer_widget
        self._is_standalone = True
        self._direction = attrs.SOUTH
        self._swap_key = Qt.Key_Space
        self._hotkey_swap_keys = [Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4, Qt.Key_5]

        # create widgets
        self._main_viewer_widget = PiPMainViewer(self)
        self._mini_viewer_widget = AbstractPopupBarWidget(self)
        self._mini_viewer_widget.setDisplayMode(AbstractPopupBarWidget.PIP)

        # create layout
        """Not using a stacked layout as the enter/leave events get borked"""
        #QStackedLayout(self)
        QVBoxLayout(self)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        self.layout().addWidget(self.mainViewerWidget())

        self._is_frozen = False

    """ UTILS (SWAP) """
    def swapMainViewer(self, mini_viewer_widget):
        """ Swaps the PiPMainViewerWidget from the AbstractPopupBarItemWidget provided

        Note: The AbstractPopupBarItemWidget MUST be a AbstractPiPDisplayWidget

        Args:
            mini_viewer_widget (AbstractPopupBarItemWidget):
        """
        new_display_widget = mini_viewer_widget.delegateWidget()

        # swap current widgets
        self.mainViewerWidget().setWidget(new_display_widget.currentWidget())
        new_display_widget.mainViewerWidget().setWidget(self._current_widget)

        # reset currentWidget meta data
        self.setPreviousWidget(None)
        new_display_widget.setPreviousWidget(None)
        _temp = self._current_widget
        self._current_widget = new_display_widget.currentWidget()
        new_display_widget._current_widget = _temp

    def swapMiniViewer(self, mini_viewer_widget):
        """ Swaps the AbstractPopupBarWidget from the AbstractPopupBarItemWidget provided.

        Note: The AbstractPopupBarItemWidget MUST be a AbstractPiPDisplayWidget

        Args:
            mini_viewer_widget (AbstractPopupBarItemWidget):
        """
        new_display_widget = mini_viewer_widget.delegateWidget()

        # preflight
        if not isinstance(new_display_widget, AbstractPiPDisplayWidget): return

        # get temp attrs
        _temp_num_widgets = new_display_widget.numWidgets()

        # set main mini viewer
        for mini_widget in reversed(new_display_widget.miniViewerWidget().widgets()):
            new_display_widget.miniViewerWidget().removeWidget(mini_widget)
            # new_display_widget.miniViewerWidget().removeWidget(mini_widget)
            self.miniViewerWidget().insertWidget(0, mini_widget)

        # set docked mini viewer
        for i in reversed(range(_temp_num_widgets, self.numWidgets())):
            if i != mini_viewer_widget.index() + _temp_num_widgets:
                mini_widget = self.miniViewerWidget().widget(i)
                self.miniViewerWidget().removeWidget(mini_widget)
                new_display_widget.miniViewerWidget().insertWidget(0, mini_widget)

        # reset mini viewer widget indexes
        self.miniViewerWidget().updateWidgetIndexes()
        new_display_widget.miniViewerWidget().updateWidgetIndexes()

    def swapSettings(self, mini_viewer_widget):
        """ Swaps the settings from the AbstractPopupBarItemWidget provided.

        Note: The AbstractPopupBarItemWidget MUST be a AbstractPiPDisplayWidget

        Args:
            mini_viewer_widget (AbstractPopupBarItemWidget):
        """
        new_display_widget = mini_viewer_widget.delegateWidget()
        _old_settings = self.settings()
        _new_settings = new_display_widget.settings()
        self.updateSettings(_new_settings)
        new_display_widget.updateSettings(_old_settings)

    def swapWidgets(self):
        """
        Swaps the previous widget with the current widget.

        This allows the user to quickly swap between two widgets.
        """
        if self.previousWidget():
            self.setCurrentWidget(self.previousWidget())

    def settings(self):
        """ returns a dict of the current settings which can be set with updateSettings()"""
        return {
            "PiP Scale": self.pipScale(),
            "Enlarged Scale": self.enlargedScale(),
            "Display Titles": self.isDisplayNamesShown(),
            "Direction": self.direction(),
            "sizes": self.miniViewerWidget().sizes()
        }

    def updateSettings(self, settings):
        """ Updates all of the settings from the settings provided.

        Note that you may need to call "resizeMiniViewer" afterwards in order
        to trigger a display update.

        Args:
            settings (dict): of {setting_name (str): value}
        """
        self.setPiPScale(settings["PiP Scale"])
        self.setEnlargedScale(float(settings["Enlarged Scale"]))
        self.setIsDisplayNamesShown(settings["Display Titles"])
        self.setDirection(settings["Direction"])
        if "sizes" in list(settings.keys()):
            self.miniViewerWidget().setSizes(settings["sizes"])

    """ PROPERTIES """
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
        self.resizeMiniViewer()

    def enlargedScale(self):
        return self.miniViewerWidget().enlargedScale()

    def setEnlargedScale(self, _enlarged_scale):
        self.miniViewerWidget().setEnlargedScale(_enlarged_scale)

    def hotkeySwapKeys(self):
        return self._hotkey_swap_keys

    def setHotkeySwapKeys(self, hotkey_swap_keys):
        self._hotkey_swap_keys = hotkey_swap_keys

    def isDragging(self):
        return self._is_dragging

    def setIsDragging(self, dragging):
        self._is_dragging = dragging

    def isFrozen(self):
        return self._is_frozen

    def setIsFrozen(self, is_frozen):
        self._is_frozen = is_frozen

    def isMiniViewerShown(self):
        return self._is_mini_viewer_shown

    def setIsMiniViewerShown(self, enabled):
        self._is_mini_viewer_shown = enabled
        if enabled:
            self.miniViewerWidget().show()
        else:
            self.miniViewerWidget().hide()

    def isMiniViewerWidget(self):
        return self._is_mini_viewer_widget

    def setIsMiniViewerWidget(self, is_mini_viewer_widget):
        self._is_mini_viewer_widget = is_mini_viewer_widget

    def isStandalone(self):
        return self._is_standalone

    def setIsStandalone(self, is_standalone):
        self._is_standalone = is_standalone

    def miniViewerMinSize(self):
        return self._mini_viewer_min_size

    def setMiniViewerMinimumSize(self, size):
        """
        Sets the minimum size the mini viewer can go to

        Args:
            size (tuple): (x, y)

        """
        self._mini_viewer_min_size = size
        self.miniViewerWidget().setMinimumSize(size)

    def swapKey(self):
        return self._swap_key

    def setSwapKey(self, key):
        self._swap_key = key

    def numWidgets(self):
        """ Number of widgets currently in this PiPDisplay"""
        return self.miniViewerWidget().count()

    def isDisplayNamesShown(self):
        return self._are_widget_names_shown

    def setIsDisplayNamesShown(self, enabled):
        self._are_widget_names_shown = enabled
        for widget in self.widgets():
            if enabled:
                widget.headerWidget().show()
            else:
                widget.headerWidget().hide()

    """ WIDGETS ( CREATION )"""
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

        exec(compile(constructor_code, "constructor_code", "exec"), globals(), loc)
        widget = loc['widget']

        return widget

    def createNewWidget(self, constructor_code, name="", resize_mini_viewer=True):
        """ Creates a new widget from the constructor code provided.

        This widget is inserted into the AbstractPopupBarWidget

        Args:
            constructor_code (str):
            name (str):
            resize_mini_viewer (bool): if the miniViewerWidget should be updated or not

        Returns (QModelIndex):

        """

        # create widget from constructor code
        widget = self.createNewWidgetFromConstructorCode(constructor_code)
        # setup recursion for PiPWidgets
        if isinstance(widget, AbstractPiPOrganizerWidget) or isinstance(widget, AbstractPiPDisplayWidget):
            widget.setIsMiniViewerWidget(True)

        """ Note: This can't install in the MiniViewer then remove.  It will still register
        in the count, even if you process the events."""
        # create main widget
        if self.currentWidget():
            mini_viewer_widget = self.miniViewerWidget().createNewWidget(widget, name=name)

        # create mini viewer widgets
        else:
            mini_viewer_widget = AbstractPopupBarItemWidget(self.mainViewerWidget(), direction=Qt.Vertical, delegate_widget=widget, name=name)
            self.setCurrentWidget(mini_viewer_widget)

        # TODO This is probably causing some slowness on loading
        # as it is resizing the mini viewer EVERY time a widget is created
        if resize_mini_viewer:
            self.resizeMiniViewer()

        # update indexes
        self.miniViewerWidget().updateWidgetIndexes()

        return mini_viewer_widget

    def removeAllWidgets(self):
        if self.mainViewerWidget().widget():
            self.mainViewerWidget().widget().setParent(None)
        self.miniViewerWidget().removeAllWidgets()

    def loadPiPWidgetFromFile(self, filepath, pip_name):
        """ Loads the PiPWidget from the file/name provided

        Args:
            filepath (str): path on disk to pipfile to load
            pip_name (str): name of pip in filepath to load
        """
        # load json data
        data = getJSONData(filepath)

        # preflight
        if not pip_name in data.keys():
            print("{pip_name} not find in {filepath}".format(pip_name=pip_name, filepath=filepath))

        # update pip display
        self.removeAllWidgets()
        self.loadPiPWidgetFromData(
            data[pip_name]["widgets"],
            data[pip_name]["settings"])

    def loadPiPWidgetFromData(self, widgets, settings):
        """ Loads the PiPWidget from the data provided.

        Args:
            widgets (dict): of {widget_name(str): constructor_code(str)}
            settings (dict): of {setting (str): value}
        """
        reversed_widgets = OrderedDict(reversed(list(widgets.items())))

        self.setIsFrozen(True)

        # clear pip view
        self.removeAllWidgets()

        # reset previous widget
        self.clearPreviousWidget()
        self.clearCurrentWidget()

        # populate pip view
        # load widgets
        for widget_name, constructor_code in reversed_widgets.items():
            if self.isStandalone():
                self.createNewWidget(constructor_code, name=widget_name, resize_mini_viewer=False)
            else:
                organizer_widget = getWidgetAncestor(self, AbstractPiPOrganizerWidget)
                organizer_widget.createNewWidget(constructor_code, name=widget_name, resize_mini_viewer=False)

        # update settings
        self.updateSettings(settings)

        # restore mini widget sizes
        self.setIsFrozen(False)

        # resize
        self.resizeMiniViewer()
        if "sizes" in list(settings.keys()):
            self.miniViewerWidget().setSizes(settings["sizes"])

    """ WIDGETS """
    def mainViewerWidget(self):
        return self._main_viewer_widget

    def setMainViewerWidget(self, widget):
        self._main_viewer_widget = widget

    def miniViewerWidget(self):
        return self._mini_viewer_widget

    def setMiniViewerWidget(self, widget):
        self._mini_viewer_widget = widget

    def currentWidget(self):
        return self._current_widget

    def setCurrentWidget(self, widget):
        """
        Sets the current full screen widget

        Args:
            widget (QMiniViewerWidget): widget to be set as full screen
        """
        # todo multi recursive swapping cleanup
        if widget.isPiPWidget():
            if isinstance(widget.delegateWidget(), AbstractPiPOrganizerWidget):
                print("multi recursive swapping is disabled for OrganizerWidgets")
                # won't be supporting this probably
                pass
            elif isinstance(widget.delegateWidget(), AbstractPiPDisplayWidget):
                # update settings
                """ sizes doesn't swap... probably due to the add/remove of widgets
                Is not calculating the fact that the mini viewer widget will have
                one widget removed, and one added
                
                Going to fullscreen = sizes + 1
                going to minimized = sizes - 1
                """
                # get sizes info
                new_display_widget = widget.delegateWidget()
                old_sizes = self.miniViewerWidget().sizes()
                new_sizes = new_display_widget.miniViewerWidget().sizes()
                del old_sizes[widget.index()]
                new_sizes.append(50)

                self.swapMainViewer(widget)

                self.swapMiniViewer(widget)

                self.swapSettings(widget)

                # resize mini viewers
                self.miniViewerWidget().setSizes(new_sizes)
                new_display_widget.miniViewerWidget().setSizes(old_sizes)
                self.resizeMiniViewer()
            return

        self.miniViewerWidget().setIsFrozen(True)
        sizes = self.miniViewerWidget().sizes()
        # reset current widget
        if self._current_widget:
            # Close enlarged widget
            """ Need to ensure the spacer is swapped out"""
            if self.miniViewerWidget().isEnlarged():
                self.miniViewerWidget()._resetSpacerWidget()
                self.miniViewerWidget().setIsEnlarged(False)

            # setup mini viewer widget
            self.miniViewerWidget().insertWidget(widget.index(), self._current_widget)
            self._current_widget.setIndex(widget.index())
            # self._current_widget.removeEventFilter(self)

            # update previous widget
            self.setPreviousWidget(self._current_widget)
            self._current_widget.setIsMainViewerWidget(False)

        # set widget as current
        self._current_widget = widget

        #self.miniViewerWidget().removeWidget(widget)
        #widget.removeEventFilter(self.miniViewerWidget())
        self.mainViewerWidget().setWidget(widget)
        self._current_widget.installEventFilter(self.miniViewerWidget())

        # update mini viewer widget
        self.miniViewerWidget().setSizes(sizes)
        self.miniViewerWidget().setIsFrozen(False)

    def clearCurrentWidget(self):
        self._current_widget = None

    def previousWidget(self):
        return self._previous_widget

    def setPreviousWidget(self, widget):
        self._previous_widget = widget

    def clearPreviousWidget(self):
        self._previous_widget = None

    def widgets(self):
        """ Returns a list of all child widgtes

        This list will include the currently viewed main widget, aswell
        as all of the widgets in the miniViewerWidget()"""
        widgets = []
        if self.mainViewerWidget().widget():
            widgets.append(self.mainViewerWidget().widget())
        widgets += self.miniViewerWidget().widgets()

        return widgets

    """ DIRECTION """
    def direction(self):
        return self._direction

    def setDirection(self, direction):
        self._direction = direction
        if direction in [attrs.EAST, attrs.WEST]:
            self.miniViewerWidget().setOrientation(Qt.Vertical)
        elif direction in [attrs.NORTH, attrs.SOUTH]:
            self.miniViewerWidget().setOrientation(Qt.Horizontal)

    """ EVENTS """
    # def eventFilter(self, obj, event):
    #     if event.type() == QEvent.DragEnter:
    #         event.accept()
    #     return False

    def hotkeySwapEvent(self, key):
        """ Swaps the widgets when a hotkey (1-5) is pressed.

        Args:
            key (Qt.Key): Valid inputs are 1-5
        """
        try:
            # select user input
            for i, swap_key in enumerate(self.hotkeySwapKeys()):
                if swap_key == key:
                    widget = self.miniViewerWidget().widget(i)

            # swap with enlarged widget
            if self.miniViewerWidget().isEnlarged():
                # Todo for some reason the PRINT makes it so that the IF clause below actually works... tf
                # print(widget.name(), self.miniViewerWidget().enlargedWidget().name())
                if widget != self.miniViewerWidget().enlargedWidget():
                    self.miniViewerWidget().closeEnlargedView()
                    self.miniViewerWidget().enlargeWidget(widget)

            # swap with main widget
            else:
                self.setCurrentWidget(widget)

        except AttributeError:
            # not enough widgets
            pass

    def keyPressEvent(self, event):
        # swap between this and previous
        if event.key() == self.swapKey():
            self.swapEvent()
            return

        # hotkey swapping
        if event.key() in self.hotkeySwapKeys():
            self.hotkeySwapEvent(event.key())
            return

        # hide PiP
        if event.key() == Qt.Key_Q:
            if not self.miniViewerWidget().isEnlarged():
                self.setIsMiniViewerShown(not self.isMiniViewerShown())
                return

        # escape
        if event.key() == Qt.Key_Escape:
            # close this mini viewer
            if self.miniViewerWidget().isEnlarged():
                self.miniViewerWidget().closeEnlargedView()
                return

            # close parent mini viewer (if open recursively)
            if self.isMiniViewerWidget():
                parent_main_widget = getWidgetAncestor(self.parent(), AbstractPiPDisplayWidget)
                parent_main_widget.miniViewerWidget().closeEnlargedView()
            return

        return QWidget.keyPressEvent(self, event)

    def leaveEvent(self, event):
        """ Blocks the error that occurs when switching between different PiPDisplays"""
        if self.miniViewerWidget().isEnlarged():
            if not isCursorOverWidget(self):
                self.miniViewerWidget().closeEnlargedView()
        return QWidget.leaveEvent(self, event)

    def resizeEvent(self, event):
        """ After a delay in the resize, this will update the display"""
        def updateDisplay():
            self.resizeMiniViewer()
            self.miniViewerWidget().closeEnlargedView()
        installResizeEventFinishedEvent(self, 100, updateDisplay, '_timer')
        return QWidget.resizeEvent(self, event)

    def resizeMiniViewer(self):
        """
        Main function for resizing the mini viewer

        The core of this function is to set the
            xpos | ypos | width | height
        of the mini viewer, based off of the number of widgets, and its current location on screen.
        """

        if self.isFrozen(): return True
        if not self.miniViewerWidget(): return True
        # todo this is 1 greater than the actual number during load?
        num_widgets = self.numWidgets()

        # preflight
        if num_widgets < 1:
            return

        # get xpos, ypos, width, height

        # special case for only one widget
        if num_widgets == 1:
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
        if 1 < num_widgets:
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
        self.miniViewerWidget().move(int(xpos), int(ypos))
        self.miniViewerWidget().resize(int(width), int(height))

    def swapEvent(self):
        """ Swaps the widget that is being displayed.

        This occurs when the swapKey() is pressed.
        If there is currently a widget enlarged, the enlarged widget will become the one
        that is currently being displayed.

        If there is no widget currently enlarged, then it will swap the main widget, with
        the previously enlarged widget."""
        # pre flight
        widget = getWidgetUnderCursor()
        if widget == self.miniViewerWidget(): return
        if isWidgetDescendantOf(widget, widget.parent(), self.miniViewerWidget()): return
        if widget == self.miniViewerWidget().spacerWidget(): return
        if isinstance(widget, QSplitterHandle): return

        # set currently enlarged widget as the main widget
        """Freezing here to avoid the cursor being over the MiniViewerWidget
        If this happens, it will close, then try to enlarge, then get stuck in
        Qts event queue and have unexpected behavior"""
        self.miniViewerWidget().setIsFrozen(True)

        if self.miniViewerWidget().isEnlarged():
            self.setCurrentWidget(self.miniViewerWidget().enlargedWidget())
            self.miniViewerWidget().setIsEnlarged(False)

        # swap previous widget widgets
        else:
            self.swapWidgets()

        self.miniViewerWidget().setIsFrozen(False)


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
        widget.setIsMainViewerWidget(True)
        widget.layout().setContentsMargins(0, 0, 0, 0)

    def removeWidget(self):
        self.widget().setParent(None)
        #self.widget().deleteLater()


# class AbstractPopupBarWidget(AbstractSplitterWidget):
#     """
#     Widget that contains all of the PiPWidgets.
#
#     This widget is an overlay of the MainWidget, and sits at a parallel hierarchy to the PiPMainViewer
#
#     Attributes:
#         is_dragging (bool): determines if this widget is currently in a drag/drop operation
#         is_enlarged (bool): If there is currently an widget enlarged.
#             Widgets are enlarged by the user hovering over them.  And closed
#             be pressing "esc" or having the mouse exit the boundries of the widget.
#         if_frozen (bool): Determines if events should be handled or not.
#         enlarged_widget (QWidget): The widget that is currently enlarged
#         popup_widget (QWidget): The widget that is displayed if the enlarged widget
#             has opened a subwidget (popup) menu.
#         spacer_widget (QLabel): Widget that holds the space in the QSplitter where
#             the currently enlarged widget normally lives.
#         __temp_sizes (list): of ints, that are the sizes of the individual widgets.
#             This is normally gotten through the "sizes()" call, but needs a temp one,
#             for swapping the spacer widget in/out.
#         __last_object_entered (AbstractPopupBarItemWidget): placeholder to determine the last object
#             that was entered.  This is mainly used when enlarging widgets to ensure that the
#             enlarged widget can be entered, as if the bounds are not great enough, you can enter
#             the Main Viewer, thus closing the enlarged widget.
#         widgets (list): Of AbstractPopupBarWidget widgets that are currently displayed.
#             This does not include the currently enlarged widget
#
#     """
#     def __init__(self, parent=None, orientation=Qt.Vertical):
#         super(AbstractPopupBarWidget, self).__init__(parent, orientation)
#
#         self._is_frozen = False
#         self._is_dragging = False
#         self._is_enlarged = False
#
#         self._enlarged_widget = None
#         self._createSpacerWidget()
#
#         self.setHandleWidth(15)
#         self.__last_object_entered = None
#         self.addDelayedSplitterMovedEvent("set_temp_sizes", self.__splitterMoved, 100)
#
#     def _createSpacerWidget(self):
#         """ Creates the invisible widget that will be swapped in/out when a widget is enlarged"""
#         self._spacer_widget = QLabel("")
#         self._spacer_widget.setParent(self.parent())
#         self._spacer_widget.hide()
#         self._spacer_widget.installEventFilter(self)
#         self._spacer_widget.setAcceptDrops(True)
#
#     """ PROPERTIES """
#     def getTopMostPiPDisplay(self, widget, parent, pip_display_widget=None):
#         """ Gets the top most pip display..."""
#         if isinstance(widget, AbstractPiPDisplayWidget):
#             pip_display_widget = widget
#
#         if parent:
#             return self.getTopMostPiPDisplay(widget.parent(), parent.parent(), pip_display_widget)
#
#         if not parent:
#             return pip_display_widget
#
#     def isDragging(self):
#         return self.getTopMostPiPDisplay(self, self.parent()).isDragging()
#
#     def setIsDragging(self, _pip_widget_is_dragging):
#         self.getTopMostPiPDisplay(self, self.parent()).setIsDragging(_pip_widget_is_dragging)
#
#     def isEnlarged(self):
#         return self._is_enlarged
#
#     def setIsEnlarged(self, enabled):
#         self._is_enlarged = enabled
#
#     def isFrozen(self):
#         return self._is_frozen
#
#     def setIsFrozen(self, frozen):
#         self._is_frozen = frozen
#
#     def enlargedWidget(self):
#         return self._enlarged_widget
#
#     def setEnlargedWidget(self, widget):
#         self._enlarged_widget = widget
#
#     def spacerWidget(self):
#         return self._spacer_widget
#
#     """ UTILS """
#     # def _swappingToFastCheck(self, widget):
#     #     if widget == self.widget(widget.index()): return True
#     #     if not self.widget(widget.index()): return True
#     #     if widget.parent() == self.widget(widget.index()).parent(): return True
#     #
#     #     return False
#
#     def _resetSpacerWidget(self):
#         """ Places the enlarged widget back into its original index.
#
#         It does this by swapping out the spacer widget, with the currently
#         enlarged widget.  This swap is done when closing the enlarged view."""
#         widget = self.enlargedWidget()
#
#         # preflight
#         if not self.isEnlarged(): return
#         if not widget: return
#         if widget == self.widget(widget.index()): return True
#         if not self.widget(widget.index()): return True
#         if widget.parent() == self.widget(widget.index()).parent(): return True
#
#         # swap widgets
#         self.replaceWidget(widget.index(), widget)
#         self.spacerWidget().setParent(self.parent())
#         self.widgets().append(widget)
#         self.setSizes(self.__temp_sizes)
#
#     def updateWidgetIndexes(self):
#         """ Updates all of the widget indexes to their current position """
#         # update indexes
#         for i, widget in enumerate(self.widgets()):
#             widget.setIndex(i)
#
#     def installDragMoveMonkeyPatch(self, widget):
#         """ Monkey patch for bug with widgets that already have drag/drop enabled.
#
#         This bypasses a bug/limitation of Qt, where EventFilters will not work on
#         widgets that have already had their drag/drop enabled, and are probably
#         exiting the event queue early.
#
#         Args:
#             widget (QWidget): to install pseudoevent on"""
#         def _dragMoveEvent(event):
#             widget._old_dragMoveEvent(event)
#             self.__dragMoveEvent(getWidgetAncestor(widget, AbstractPopupBarItemWidget))
#         if not hasattr(widget, "_old_dragMoveEvent"):
#             widget._old_dragMoveEvent = widget.dragMoveEvent
#         widget.dragMoveEvent = _dragMoveEvent
#
#     def installDragEnterMonkeyPatch(self, widget):
#         """ Monkey patch for bug with widgets that already have drag/drop enabled.
#
#         This bypasses a bug/limitation of Qt, where EventFilters will not work on
#         widgets that have already had their drag/drop enabled, and are probably
#         exiting the event queue early.
#
#         Args:
#             widget (QWidget): to install pseudoevent on"""
#         def _dragEnterEvent(event):
#             # event.accept()
#             widget._old_dragEnterEvent(event)
#             self.__dragEnterEvent(getWidgetAncestor(widget, AbstractPopupBarItemWidget))
#         if not hasattr(widget, "_old_dragEnterEvent"):
#             widget._old_dragEnterEvent = widget.dragEnterEvent
#         widget.dragEnterEvent = _dragEnterEvent
#
#     """ EVENTS """
#     def eventFilter(self, obj, event):
#         """ Event handler for ALL PiPMiniViewerWIdgets
#
#         Args:
#             obj (AbstractPopupBarItemWidget):
#             event (QEvent):
#
#         Note:
#             _is_frozen (bool): flag to determine if the UI should be frozen for updates
#             _enlarged_object (AbstractPopupBarItemWidget): when exiting, this is the current object that has
#                 been enlarged for use.
#             _entered_object (AbstractPopupBarItemWidget): when exiting, this is the object that is under the cursor
#                 if the user exits into the MiniViewerWidget
#                 will be set to None
#             _is_dragging (bool): determines if a drag operation is currently happening
#             Signals:
#                 DragLeave:
#                     isDragging holds attribute to determine if this widget is currently in a drag/drop operation.
#                     This is reset when the user hover enters a new mini widget.  When the drag leave enters a
#                     widget that is in the bounds of the enlargedWidget, it will do nothing.
#         """
#
#         # preflight
#         if self.isFrozen(): return True
#         if self.__eventFilterSpacerWidget(obj, event): return True
#
#         if self.__dragEvent(obj, event): return True
#
#         if event.type() == QEvent.Enter:
#             """
#             If the user exits on the first widget, or a widget that will be the enlarged widget,
#             it will recurse back and enlarge itself.  This will block that recursion
#             """
#             self.__last_object_entered = obj
#             #
#             if self.isEnlarged():
#                 # Block from re-enlarging itself
#                 if self.enlargedWidget() == obj:
#                     return True
#                 elif obj.isMainViewerWidget():
#                     return True
#                 # Has just enlarged the widget, but the cursor never entered it
#                 else:
#                     # reset display label
#                     self._resetSpacerWidget()
#
#                     # reset widget to default params
#                     self.setIsDragging(False)
#
#                     # enlarge widget
#                     self.enlargeWidget(obj)
#
#             # Enlarge MiniViewerWidget
#             else:
#                 if not obj.isMainViewerWidget():
#                     # reset widget to default params
#                     self.setIsDragging(False)
#
#                     # enlarge widget
#                     self.enlargeWidget(obj)
#             return True
#
#         if event.type() == QEvent.Leave:
#             # leaves over mini viewer widget
#             """ Check to see if the cursor is over the object, because the drag
#             events will trigger a leave event"""
#             if not isCursorOverWidget(obj):
#                 if obj == self.enlargedWidget():
#                     self.closeEnlargedView()
#             return True
#
#         return False
#
#     def __eventFilterSpacerWidget(self, obj, event):
#         """ Event Filter that is run when entering the spacer widget
#
#         When the user enters/leaves a AbstractPopupBarItemWidget, if it exits from
#         the self.spacerWidget() into the Main Viewer, it will auto close
#         the enlarged widget.
#
#         This will block that auto close, when leaving
#         the spacer widget, and entering the Main Viewer Widget.
#
#         Args:
#             obj (AbstractPopupBarItemWidget)
#             event (QEvent)
#         """
#
#         if event.type() in [QEvent.Enter, QEvent.DragEnter]:
#             if obj == self.spacerWidget():
#                 # just entered spacer widget
#                 if obj == self.spacerWidget():
#                     self.__last_object_entered = self.spacerWidget()
#                     return True
#             if obj.isMainViewerWidget():
#                 if self.__last_object_entered == self.spacerWidget():
#                     return True
#         else:
#             return False
#
#     def __dragMoveEvent(self, obj):
#         modifiers = QApplication.keyboardModifiers()
#         if modifiers == Qt.AltModifier:
#             obj.pipMiniViewerWidget().closeEnlargedView()
#             return True
#         if not self.isDragging():
#             self.setIsDragging(True)
#             # self.setIsFrozen(True)
#             obj.pipMiniViewerWidget().closeEnlargedView()
#             return True
#
#     def __dragEnterEvent(self, obj):
#         self.__last_object_entered = obj
#         if self.isEnlarged():
#             # Block from re-enlarging itself
#             if self.enlargedWidget() == obj:
#                 return True
#             # Has just enlarged the widget, but the cursor never entered it
#             elif obj.isMainViewerWidget():
#                 self.closeEnlargedView()
#             else:
#                 # reset display label
#                 self._resetSpacerWidget()
#
#                 # reset widget to default params
#                 self.setIsDragging(False)
#
#                 # enlarge widget
#                 self.enlargeWidget(obj)
#         # Enlarge MiniViewerWidget
#         else:
#             # enlarge widget
#             if not obj.isMainViewerWidget():
#                 obj.pipMiniViewerWidget().closeEnlargedView()
#                 self.enlargeWidget(obj)
#
#     def __dragEvent(self, obj, event):
#         """ Handles the event filter's Drag Leave Event
#         Args:
#             obj (QWidget):
#             event (QEvent):
#         """
#         # if event.type() == QEvent.KeyPress:
#         #     if self.isDragging():
#         #         if event.key() == Qt.Key_Escape:
#         #             self.closeEnlargedView()
#         #             return True
#         # print(obj.name(), event.type())
#         # if event.type() == QEvent.DragLeave:
#         #     print ("drag leave == ", obj.name())
#         # if event.type() == QEvent.DragEnter:
#         #     event.accept()
#         #     print ("drag enter == ", obj.name())
#         # if event.type() == QEvent.DragMove:
#         #     print ("drag move == ", obj.name())
#
#         if event.type() == QEvent.DragEnter:
#             # event.accept()
#             self.__dragEnterEvent(obj)
#         #
#         if event.type() == QEvent.DragMove:
#             self.__dragMoveEvent(obj)
#
#         # on drop, close and reset
#         if event.type() == QEvent.Drop:
#             self.setIsDragging(False)
#             obj.pipMiniViewerWidget().closeEnlargedView()
#
#     def __splitterMoved(self, *args):
#         """ Sets the __temp_sizes list after the splitter has finished moving
#
#         This ensures that when the widget is enlarged, that if the widgets
#         are resized, they will be restored back to the new sizes"""
#         # prelight
#         if not self.isEnlarged(): return
#
#         # User finished dragging splitter
#         self.__temp_sizes = self.sizes()
#
#     def enlargeWidget(self, widget):
#         """
#         Enlarges the widget provided to be covering most of the main display area.
#
#         Args:
#             widget (AbstractPopupBarItemWidget): Widget to be enlarged
#         """
#
#         # preflight
#         if not widget: return
#         if not self.widget(widget.index()): return
#         if self.widget(widget.index()) == self.spacerWidget(): return
#         if self.widget(widget.index()).parent() == self.spacerWidget().parent(): return
#         #if not getWidgetAncestor(widget, AbstractPiPOrganizerWidget): return
#         self.setIsFrozen(True)
#
#         # set/get attrs
#         pip_display_widget = getWidgetAncestor(self, AbstractPiPDisplayWidget)
#         self.setIsEnlarged(True)
#         self.setEnlargedWidget(widget)
#         scale = pip_display_widget.enlargedScale()
#         negative_space = 1 - scale
#         half_neg_space = negative_space * 0.5
#         num_widgets = pip_display_widget.numWidgets()
#         offset = int(min(pip_display_widget.width(), pip_display_widget.height()) * half_neg_space)
#         """temp sizes holds the current size of widgets
#         so that they can be added/removed and restored to their original state"""
#         self.__temp_sizes = self.sizes()
#
#         # special case for only one mini viewer widget
#         if num_widgets == 1:
#             #yoffset = int(pip_display_widget.width() * negative_space)
#             width = int(pip_display_widget.width() - offset)
#             height = int(pip_display_widget.height() - offset)
#
#             # NORTH WEST
#             if pip_display_widget.direction() == attrs.NORTH:
#                 xpos = 0
#                 ypos = 0
#             # SOUTH EAST
#             if pip_display_widget.direction() == attrs.SOUTH:
#                 xpos = offset
#                 ypos = offset
#             # NORTH EAST
#             if pip_display_widget.direction() == attrs.EAST:
#                 xpos = offset
#                 ypos = 0
#             # SOUTH WEST
#             if pip_display_widget.direction() == attrs.WEST:
#                 xpos = 0
#                 ypos = offset
#
#         # if there are 2 or more mini viewer widgets
#         if 1 < num_widgets:
#             # get widget position / size
#             if pip_display_widget.direction() in [attrs.EAST, attrs.WEST]:
#                 height = int(pip_display_widget.height() - (offset * 2))
#                 ypos = int(offset)
#                 width = int(pip_display_widget.width() - offset - self.width())
#                 if pip_display_widget.direction() == attrs.EAST:
#                     xpos = offset
#                 if pip_display_widget.direction() == attrs.WEST:
#                     xpos = self.width()
#
#             if pip_display_widget.direction() in [attrs.NORTH, attrs.SOUTH]:
#                 xpos = int(pip_display_widget.width() * half_neg_space)
#                 width = int(pip_display_widget.width() * scale)
#                 height = int(
#                     pip_display_widget.height()
#                     - self.height()
#                     - offset)
#                 if pip_display_widget.direction() == attrs.NORTH:
#                     ypos = self.height()
#                 if pip_display_widget.direction() == attrs.SOUTH:
#                     ypos = offset
#
#         # Swap spacer widget
#         self.replaceWidget(widget.index(), self.spacerWidget())
#         self.spacerWidget().show()
#
#         # reparent widget
#         widget.setParent(self.parent())
#         widget.show()
#
#         # move / resize enlarged widget
#         widget.resize(width, height)
#         widget.move(xpos, ypos)
#
#         #
#         self.insertWidget(widget.index(), self._spacer_widget)
#         self.setSizes(self.__temp_sizes)
#
#         # show mini viewer widgets
#         # if widget.isPiPWidget():
#         #     widget.delegateWidget().setIsMiniViewerShown(True)
#
#         self.setIsFrozen(False)
#
#     def closeEnlargedView(self):
#         """Closes the enlarged viewer, and returns it back to normal PiP mode"""
#
#         # preflight
#         if not self.isEnlarged(): return
#
#         if self.enlargedWidget().isMainViewerWidget(): return
#
#         # setup attrs
#         self.setIsFrozen(True)
#         widget_under_cursor = getWidgetUnderCursor()
#
#         # exitted out of widget
#         if not widget_under_cursor:
#             self._resetSpacerWidget()
#             self.setIsEnlarged(False)
#         # exited over the mini viewer
#         elif isWidgetDescendantOf(widget_under_cursor, widget_under_cursor.parent(), self):
#             if widget_under_cursor == self._spacer_widget:
#                 pass
#             elif isinstance(widget_under_cursor, QSplitterHandle):
#                 pass
#             else:
#                 # reset display label
#                 self.__temp_sizes = self.sizes()
#                 self._resetSpacerWidget()
#
#                 # enlarge mini viewer
#                 display_widget = getWidgetAncestor(widget_under_cursor, AbstractPiPDisplayWidget)
#                 mini_viewer_widget = getWidgetAncestor(widget_under_cursor, AbstractPopupBarItemWidget)
#
#                 if display_widget.isMiniViewerWidget():
#                     # exit over recursive mini viewer
#                     if isinstance(mini_viewer_widget.parent(), AbstractPiPDisplayWidget):
#                         display_widget.miniViewerWidget().closeEnlargedView()
#                         self.enlargeWidget(getWidgetAncestor(display_widget, AbstractPopupBarItemWidget))
#
#                     # exit over recursive main viewer
#                     elif isinstance(mini_viewer_widget.parent(), PiPMainViewer):
#                         self.enlargeWidget(getWidgetAncestor(display_widget, AbstractPopupBarItemWidget))
#                 else:
#                     # exit over normal widget
#                     self.enlargeWidget(mini_viewer_widget)
#
#         # exited over main viewer
#         else:
#             # reset display label
#             self._resetSpacerWidget()
#             self.setIsEnlarged(False)
#
#         # self.setIsFrozen(False)
#         # show mini viewer widgets
#         # if self.enlargedWidget().isPiPWidget():
#         #     # pip_display_widget = getWidgetAncestor(self.enlargedWidget(), AbstractPiPDisplayWidget)
#         #     self.enlargedWidget().delegateWidget().setIsMiniViewerShown(False)
#
#         """ Unfreezing as a delayed event to help to avoid the segfaults that occur
#         when PyQt tries to do things to fast..."""
#         # self.setEnlargedWidget(None)
#         runDelayedEvent(self, self.unfreeze, delay_amount=10)
#
#     def unfreeze(self):
#         self.setIsFrozen(False)
#
#     """ WIDGETS """
#     def createNewWidget(self, widget, name=""):
#         """
#         Creates a new widget in the mini widget.  This is only when a new widget needs to be instantiated.
#
#         Args:
#             widget:
#             name:
#
#         Returns (AbstractPopupBarItemWidget):
#         """
#         mini_widget = AbstractPopupBarItemWidget(self, direction=Qt.Vertical, delegate_widget=widget, name=name)
#         # self.installDragEnterMonkeyPatch(mini_widget.delegateWidget())
#         # self.installDragLeaveMonkeyPatch(mini_widget.delegateWidget())
#         # self.installDragMoveMonkeyPatch(mini_widget.delegateWidget())
#         mini_widget.installEventFilter(self)
#         mini_widget.delegateWidget().setAcceptDrops(True)
#
#         self.insertWidget(0, mini_widget)
#         return mini_widget
#
#     def addWidget(self, widget):
#         if isinstance(widget, AbstractPopupBarItemWidget):
#             widget.installEventFilter(self)
#             self.installDragEnterMonkeyPatch(widget.delegateWidget())
#             self.installDragMoveMonkeyPatch(widget.delegateWidget())
#             widget.delegateWidget().setAcceptDrops(True)
#             return QSplitter.addWidget(self, widget)
#         elif widget == self.spacerWidget():
#             return
#         else:
#             print("{widget_type} is not valid.".format(widget_type=type(widget)))
#             return
#
#     def insertWidget(self, index, widget):
#         if isinstance(widget, AbstractPopupBarItemWidget):
#             widget.installEventFilter(self)
#             self.installDragEnterMonkeyPatch(widget.delegateWidget())
#             self.installDragMoveMonkeyPatch(widget.delegateWidget())
#             widget.delegateWidget().setAcceptDrops(True)
#             return QSplitter.insertWidget(self, index, widget)
#         elif widget == self.spacerWidget():
#             pass
#         else:
#             print ("{widget_type} is not valid.".format(widget_type=type(widget)))
#             return
#
#     def removeWidget(self, widget):
#         if widget:
#             widget.setParent(None)
#             if not isinstance(widget, QSplitterHandle):
#                 widget.removeEventFilter(self)
#
#     def removeAllWidgets(self):
#         for i in reversed(range(self.count())):
#             self.widget(i).removeEventFilter(self)
#             self.widget(i).setParent(None)
#
#     def widgets(self):
#         _widgets = []
#         for i in range(self.count()):
#             widget = self.widget(i)
#             if isinstance(widget, AbstractPopupBarItemWidget):
#                 _widgets.append(widget)
#         return _widgets
#
#
# class AbstractPopupBarItemWidget(QWidget):
#     """
#     One PiP Widget that is displayed in the AbstractPopupBarWidget
#
#     Attributes:
#         index (int): current index in model
#         item (PiPMiniViewerOrganizerItem)
#     """
#     def __init__(
#         self,
#         parent=None,
#         name="None",
#         direction=Qt.Horizontal,
#         delegate_widget=None
#     ):
#         super(AbstractPopupBarItemWidget, self).__init__(parent)
#         QVBoxLayout(self)
#
#         # setup flag for if this is a pip widget (for recursive purposes
#         if isinstance(delegate_widget, AbstractPiPOrganizerWidget) or isinstance(delegate_widget, AbstractPiPDisplayWidget):
#             self._is_pip_widget = True
#         else:
#             self._is_pip_widget = False
#
#         self._is_main_viewer_widget = False
#         self._name = name
#         self._index = 0
#         self._main_widget = AbstractLabelledInputWidget(
#             self, name=name, direction=direction, delegate_widget=delegate_widget)
#         #self._main_widget.viewWidget().delegateWidget().setUserFinishedEditingEvent(self.updateItemDisplayName)
#
#         self.layout().addWidget(self._main_widget)
#         self.layout().setContentsMargins(0, 0, 0, 0)
#
#         # Todo find all of these handlers and remove them?
#         # this is just a forced override for now
#         # disable editable header
#         self.headerWidget().setDisplayMode(AbstractOverlayInputWidget.DISABLED)
#
#         #
#         self.setAcceptDrops(True)
#
#
#     # def updateItemDisplayName(self, widget, value):
#     #     """
#     #     Updates the display name of this label
#     #     Args:
#     #         widget:
#     #         value:
#     #     """
#     #     self.item().columnData()['name'] = value
#     #     self.headerWidget().viewWidget().hideDelegate()
#     #     self.headerWidget().setName(value)
#
#     """ WIDGETS """
#     def mainWidget(self):
#         return self._main_widget
#
#     def headerWidget(self):
#         return self.mainWidget().viewWidget()
#
#     def delegateWidget(self):
#         return self.mainWidget().delegateWidget()
#
#     def pipMiniViewerWidget(self):
#         return getWidgetAncestor(self, AbstractPiPDisplayWidget).miniViewerWidget()
#
#     """ PROPERTIES """
#     def isPiPWidget(self):
#         return self._is_pip_widget
#
#     def setIsPiPWidget(self, is_pip_widget):
#         self._is_pip_widget = is_pip_widget
#
#     def isMainViewerWidget(self):
#         return self._is_main_viewer_widget
#
#     def setIsMainViewerWidget(self, _is_main_viewer_widget):
#         self._is_main_viewer_widget = _is_main_viewer_widget
#
#     def item(self):
#         return self._item
#
#     def setItem(self, item):
#         self._item = item
#
#     def index(self):
#         return self._index
#
#     def setIndex(self, index):
#         self._index = index
#
#     def name(self):
#         return self._name
#         # return self.item().columnData()["name"]
#
#     def setName(self, name):
#         self._name = name
#         self.item().columnData()["name"] = name
#         self.headerWidget().viewWidget().setText(name)


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
            "value": 0.25,
            "value_list": [0.01, 0.025, 0.05, 0.1],
            "range": [True, 0.1, 1],
            "code": """organizer_widget.pipDisplayWidget().setPiPScale(float(value))"""},
        "Enlarged Scale": {
            "type": attrs.FLOAT,
            "value": 0.8,
            "value_list": [0.01, 0.025, 0.05, 0.1],
            "range": [True, 0.1, 0.9],
            "code": """organizer_widget.pipDisplayWidget().setEnlargedScale(float(value))"""},
        "Display Titles": {
            "type": attrs.BOOLEAN,
            "value": True,
            "code": """organizer_widget.pipDisplayWidget().setIsDisplayNamesShown(value)"""},
        "Direction": {
            "type": attrs.LIST,
            "value": attrs.SOUTH,
            "items": [[attrs.NORTH], [attrs.SOUTH], [attrs.EAST], [attrs.WEST]],
            "code": """
#print(organizer_widget)
#print(organizer_widget.pipDisplayWidget())
organizer_widget.pipDisplayWidget().setDirection(value)
organizer_widget.pipDisplayWidget().resizeMiniViewer()"""}
    }

    def __init__(self, parent=None):
        # inherit
        super(AbstractFrameInputWidgetContainer, self).__init__(parent=parent, title="Settings", direction=Qt.Vertical)

        # for some reason this isn't carring over from the AbstractFrameInputWidgetContainer...
        self._frame_container = True

        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setIsHeaderShown(False)

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
            delegate_widget.filter_results = False
            # delegate_widget.setUserFinishedEditingEvent(self.userUpdate)

        input_widget = AbstractLabelledInputWidget(parent=self, name=name, delegate_widget=delegate_widget)
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
        labelled_input_widget = getWidgetAncestor(widget, AbstractLabelledInputWidget)
        name = labelled_input_widget.name()

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
        organizer_widget = getWidgetAncestor(self, AbstractPiPOrganizerWidget)

        # prepare local scope
        loc = {}
        loc['self'] = self
        loc['organizer_widget'] = organizer_widget
        loc['value'] = value

        # run update
        exec(compile(code, "code", "exec"), globals(), loc)

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
            # preflight
            if name in ["sizes"]: continue

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
        main_widget = getWidgetAncestor(self, AbstractPiPOrganizerWidget)
        main_widget.setIsSettingsVisible(True)
        AbstractFrameInputWidgetContainer.showEvent(self, event)

    def hideEvent(self, event):
        main_widget = getWidgetAncestor(self, AbstractPiPOrganizerWidget)
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
        self.setIsDroppable(False)
        self.setIsDraggable(not _is_locked)
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
    This widget will read all of the AbstractPiPOrganizerWidgets that the user has created.

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
        self.setIsRootDroppable(False)

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
        """ Creates a new Group for index which stores PiPWidgets
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
        container_item.setIsDraggable(False)
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
        item.setIsDroppable(False)
        if index.parent().internalPointer().isLocked():
            item.setIsLocked(True)

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
        """ When an item is selected, this will update the AbstractPiPOrganizerWidget to the item
        that has been selected

        Args:
            item (PiPGlobalOrganizerItem):
            enabled (bool):
        """
        if enabled:
            if item.itemType() == PiPGlobalOrganizerItem.PIP:
                organizer_widget = getWidgetAncestor(self, AbstractPiPOrganizerWidget)
                organizer_widget.removeAllWidgets()
                organizer_widget.pipDisplayWidget().loadPiPWidgetFromData(item.widgetsList(), item.settings())

                # load settings
                organizer_widget.settingsWidget().loadSettings(item.settings())

            # toggle save button lock
            is_locked = item.isLocked()
            self.saveWidget().updateSaveButtonText(is_locked=is_locked)

    def deleteItemEvent(self, item):
        """
        When the user deletes an item, this will remove the index and the entry
        into the saved PiPFile

        Args:
            item (PiPGlobalOrganizerItem): currently selected by the user to be deleted
        """
        # remove from JSON
        if item.itemType() == PiPGlobalOrganizerItem.PIP:
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
        main_widget = getWidgetAncestor(self, AbstractPiPOrganizerWidget)
        main_widget.setIsGlobalOrganizerVisible(True)
        AbstractModelViewWidget.showEvent(self, event)

    def hideEvent(self, event):
        main_widget = getWidgetAncestor(self, AbstractPiPOrganizerWidget)
        main_widget.setIsGlobalOrganizerVisible(False)
        main_widget.setFocus()
        AbstractModelViewWidget.hideEvent(self, event)


class PiPSaveButtonWidget(AbstractButtonInputWidget):
    """ Save Button located in the GlobalOrganizerWidget"""
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
        """Gets the dictionary for a singular PiPWidgetItem.

        This data is saved as an entry in the master PiPFile located at saveFilePath()
        Returns (OrderedDict):
            "PiPName": {
                "widgets": [
                    {"widget name": "constructor code"},
                    {"widget name": "constructor code"},
                    {"widget name": "constructor code"}],
                "settings": {"setting name": "value"}
            }
        """
        main_widget = getWidgetAncestor(self, AbstractPiPOrganizerWidget)

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

        # store sizes from AbstractPopupBarWidget
        settings["sizes"] = main_widget.miniViewerWidget().sizes()

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
        main_widget = getWidgetAncestor(self, AbstractPiPOrganizerWidget)
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
        main_widget = getWidgetAncestor(self, AbstractPiPOrganizerWidget)

        # update
        if self.saveButtonWidget().mode() == PiPSaveButtonWidget.UPDATE:
            _exists = True
            new_item, orig_item = self.updatePiPWidgetItemInFile()

        # save
        elif self.saveButtonWidget().mode() == PiPSaveButtonWidget.SAVE:
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
        """This will save the current PiPWidgetItem to the master PiPFile.

        This is activated when the "Save" button is pressed"
        """

        name = self.nameWidget().delegateWidget().text()
        pip_data = self.currentPiPFileData()

        # save pip file
        pip_data[name] = self.getPiPWidgetItemDict()
        self.dumpPiPDataToJSON(self.currentSaveFilePath(), pip_data)

        # create new index
        main_widget = getWidgetAncestor(self, AbstractPiPOrganizerWidget)

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
        main_widget = getWidgetAncestor(self, AbstractPiPOrganizerWidget)
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
class PiPMiniViewerOrganizerItem(AbstractDragDropModelItem):
    def __init__(self, parent=None):
        super(PiPMiniViewerOrganizerItem, self).__init__(parent)

    def widget(self):
        return self._widget

    def setWidget(self, widget):
        self._widget = widget

    def constructorCode(self):
        return self._constructor_code

    def setConstructorCode(self, constructor_code):
        self._constructor_code = constructor_code


class PiPMiniViewerOrganizerWidget(AbstractModelViewWidget):
    """
    This widget is in charge of organizing widgets that will be visible in the AbstractPiPOrganizerWidget
        Abilities include:
            Create | Delete | Rename | Reorder

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
        super(PiPMiniViewerOrganizerWidget, self).__init__(parent=parent)

        # setup model
        self.model().setItemType(PiPMiniViewerOrganizerItem)

        # install events
        self.setItemDeleteEvent(self.deleteWidget)
        self.setTextChangedEvent(self.editWidget)
        self.setDropEvent(self.itemReordered)

        # panel creator widget
        if not widget_types:
            widget_types = {}

        self._panel_creator_widget = PiPMiniViewerWidgetCreator(self, widget_types=widget_types)
        self.addDelegate([Qt.Key_C], self._panel_creator_widget, modifier=Qt.AltModifier, focus=True)
        self._panel_creator_widget.show()

    """ UTILS """
    def widgets(self):
        return [index.internalPointer().widget() for index in self.model().getAllIndexes() if hasattr(index.internalPointer(), "_widget")]

    """ EVENTS """
    def itemReordered(self, data, items, model, row, parent):
        """When an item is drag/dropped, this will update the widget indexes, and reinsert
        the widget into the mini viewer if it is not currently the active widget.

        # todo this will probably need work...
        """
        # get default attrs

        main_widget = getWidgetAncestor(self, AbstractPiPOrganizerWidget)
        mini_viewer = main_widget.miniViewerWidget()
        widget = items[0].widget()

        # if in mini viewer
        # reset parent and insert back into mini viewer
        if widget.parent() == mini_viewer:
            widget.setParent(None)
            widget.setIndex(row)
            mini_viewer.addWidget(widget)

        # update all widget indexes
        mini_viewer.updateWidgetIndexes()
        # main_widget.updateWidgetIndexes()

    def editWidget(self, item, old_value, new_value):
        item.widget().setName(new_value)

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
        organizer_widget = getWidgetAncestor(self, AbstractPiPOrganizerWidget)

        # if current widget
        current_widget = organizer_widget.currentWidget()
        if widget == current_widget:
            # get first useable widget
            first_widget = organizer_widget.widgets()[0]
            if first_widget == widget:
                first_widget = organizer_widget.widgets()[1]

            # set current widget
            if organizer_widget.previousWidget():
                organizer_widget.setCurrentWidget(organizer_widget.previousWidget())
            else:
                organizer_widget.setCurrentWidget(first_widget)

            # remove previous widget
            organizer_widget.setPreviousWidget(None)

        # create temp widget
        if organizer_widget.pipDisplayWidget().numWidgets() < 2:
            organizer_widget.createTempWidget()

        # delete widget
        item.widget().setParent(None)
        item.widget().deleteLater()
        # resize
        organizer_widget.pipDisplayWidget().resizeMiniViewer()

    """ EVENTS """
    def showEvent(self, event):
        main_widget = getWidgetAncestor(self, AbstractPiPOrganizerWidget)
        main_widget.setIsLocalOrganizerVisible(True)
        AbstractModelViewWidget.showEvent(self, event)

    def hideEvent(self, event):
        main_widget = getWidgetAncestor(self, AbstractPiPOrganizerWidget)
        main_widget.setIsLocalOrganizerVisible(False)
        main_widget.setFocus()
        AbstractModelViewWidget.hideEvent(self, event)


class PiPMiniViewerWidgetCreator(AbstractListInputWidget):
    """ Creates the widgets that are available in the current AbstractPiPDisplayWidget"""
    def __init__(self, parent=None, widget_types=None):
        super(PiPMiniViewerWidgetCreator, self).__init__(parent)

        self._widget_types = widget_types
        self.populate([[key] for key in sorted(widget_types.keys())])

    def widgetTypes(self):
        return self._widget_types

    def setWidgetTypes(self, widget_types):
        self._widget_types = widget_types

    def createNewWidget(self):
        # preflight
        value = self.text()

        if value not in self.widgetTypes().keys(): return
        main_widget = getWidgetAncestor(self, AbstractPiPOrganizerWidget)

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
    from cgwidgets.utils import centerWidgetOnCursor, setAsAlwaysOnTop
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
widget = QPushButton(\"TESTBUTTON\") """,
        "List":"""
from qtpy.QtWidgets import QListWidget, QAbstractItemView
widget = QListWidget()
widget.setDragDropMode(QAbstractItemView.DragDrop)
widget.setAcceptDrops(True)
widget.addItems(['a', 'b', 'c', 'd'])
# widget.setFixedWidth(100)
""",
        "Recursion":"""
widget = AbstractPiPDisplayWidget()
widget.loadPiPWidgetFromFile(
        getDefaultSavePath() + '/.PiPWidgets_02.json',
        "test02"
    )
""",
        "Popup":"""
import string
from qtpy.QtWidgets import QWidget, QVBoxLayout, QComboBox
from qtpy.QtGui import QCursor

pos = QCursor().pos()
widget = QWidget()
l = QVBoxLayout(widget)
b = QComboBox()
b.addItems([char for char in string.ascii_letters])
l.addWidget(b)
"""
    }
    pip_widget = AbstractPiPOrganizerWidget(save_data=save_data, widget_types=widget_types)

    pip_widget.setPiPScale((0.25, 0.25))
    pip_widget.setEnlargedScale(0.75)
    pip_widget.setDirection(attrs.WEST)
    #pip_widget.setIsDisplayNamesShown(False)

    #

    # Drag/Drop Widget
    # drag_drop_widget = QListWidget()
    # drag_drop_widget.setDragDropMode(QAbstractItemView.DragDrop)
    # drag_drop_widget.addItems(['a', 'b', 'c', 'd'])
    # drag_drop_widget.setFixedWidth(100)

    # Main Widget

    # pip main widget
    class MainWidget(QWidget):
        def __init__(self, parent=None):
            super(MainWidget, self).__init__(parent)
    main_widget = MainWidget()

    main_layout = QHBoxLayout(main_widget)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.addWidget(pip_widget)

    # test splitter
    # from qtpy.QtWidgets import QSplitter, QLabel
    # splitter = QSplitter()
    # splitter.addWidget(QLabel("test"))
    # splitter.addWidget(QLabel("this"))
    # main_layout.addWidget(splitter)

    setAsAlwaysOnTop(main_widget)
    main_widget.show()

    #main_widget.move(2000,700)
    centerWidgetOnCursor(main_widget)
    main_widget.resize(512, 512)

    # setup display widget
    # pip_widget.setDisplayWidget("Bar", "recursion")
    # pip_widget.setDelegateTitleIsShown(True)
    # pip_widget.setCreationMode(AbstractPiPOrganizerWidget.DISPLAY)

    # display test
    display_test = AbstractPiPDisplayWidget()
    display_test.loadPiPWidgetFromFile(
        getDefaultSavePath() + '/.PiPWidgets_02.json',
        "test02"
    )
    centerWidgetOnCursor(display_test)
    display_test.resize(1024, 1024)
    #setAsAlwaysOnTop(display_test)
    display_test.show()



    sys.exit(app.exec_())
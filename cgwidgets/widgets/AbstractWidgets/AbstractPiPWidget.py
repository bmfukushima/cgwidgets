"""
The PiPWidget is designed to display multiple widgets simultaneously to the user.

Similar to the function that was provided to TV's in the mid 1970's.  This widget is
designed to allow the user to create multiple hot swappable widgets inside of the same
widget.

Hierarchy:
    AbstractPiPOrganizerWidget --> (AbstractShojiModelViewWidget)
        |- PiPDisplayWidget --> (QWidget)
        |    |- QVBoxLayout
        |    |    |- PiPMainViewer --> (QWidget)
        |    |    |- PiPMiniViewerWidgetCreator --> (AbstractListInputWidget)
        |    |- spacer_widget (QLabel)
        |    |- MiniViewer (QWidget)
        |        |- QBoxLayout
        |            |-* PiPMiniViewerWidget --> QWidget
        |                    |- QVBoxLayout
        |                    |- AbstractLabelledInputWidget
        |- miniViewerOrganizerWidget --> AbstractModelViewWidget
        |- CreatorWidget (Extended...)
        |- GlobalOrganizerWidget --> AbstractModelViewWidget
        |- SettingsWidget --> FrameInputWidgetContainer

Signals:
    Swap (Enter):
        Upon user cursor entering a widget, that widget becomes the main widget

        PiPMiniViewer --> EventFilter --> EnterEvent
        PiPMiniViewer --> EventFilter --> LeaveEvent

    Swap (Key Press):
        Upon user key press on widget, that widget becomes the main widget.
        If the key is pressed over a MiniViewerWidget, it will become the main widget.
        If it is pressed over the MainWidget, it will swap it with the previous widget

        Default is "Space"

        PiPDisplayWidget --> keyPressEvent --> setCurrentWidget, swapWidgets

    Swap Previous (Key Press)
        Press ~, main widget is swapped with previous main widget
        PiPDisplayWidget --> keyPressEvent --> setCurrentWidget
    Quick Drag ( Drag Enter ):
        Upon user drag enter, the mini widget becomes large to allow easier dropping
        PiPMiniViewer --> EventFilter --> Drag Enter
                                      --> Enter
                                      --> Drop
                                      --> Drag Leave
                                      --> Leave
    HotSwap (Key Press 1-5):
        PiPDisplayWidget --> keyPressEvent --> setCurrentWidget
    Toggle previous widget
        PiPDisplayWidget --> keyPressEvent --> swapWidgets
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
    * Recursive PiPs
        - MiniViewer
            PiPDisplayWidget --> setCurrentWidget
            Needs to make it so that the PIPWidget that is displayed, is the one that is 
            selected, and the current pip widget is set in the mini viewer... With the PiPViewer
            that was selected removed from the miniviewer...
            1.) Make selected PiPDisplayWidget/AbstractPiPOrganizerWidget the currently displayed PiPWidget
                    - How to get/store this data?
            2.) Take old PiPDisplayWidget/AbstractPiPOrganizerWidget and insert it as the first index
                    in the new PiPDisplayWidget/AbstractPiPOrganizerWidget
    * Move AbstractPiPOrganizerWidget to AbstractPiPOrganizerWidgetOrganizer
        - AbstractPiPOrganizerWidget then becomes a display only PiPWidget
            so that it doesn't have to keep creating a ton of extra widgets...
    * Delete (Global Organizer)
        After delete, wrong widget is displayed in the PiPView


    * Clean up mini viewer resize
        PiPGlobalOrganizerWidget --> loadPiPWidgetFromSelection ( This runs twice for some reason)
        PiPSaveWidget --> loadPiPWidgetFromItem
        AbstractPiPOrganizerWidget --> createNewWidget --> resizeMiniViewer
    * Move MiniViewer to QSplitter?
        - Weird bug in replaceWidget() call... that sometimes will cause it not to work
            this seems to happen if you move the cursor super fast, and make it go in/out
            of the widget.
        - 5.6 doesnt have replaceWidget()... GG Katana...
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
    QWidget, QBoxLayout, QVBoxLayout, QSizePolicy, QHBoxLayout, QLabel, QScrollArea, QSplitter, QSplitterHandle)
from qtpy.QtCore import QEvent, Qt, QPoint, QTimer
from qtpy.QtGui import QCursor

from cgwidgets.views import AbstractDragDropModelItem
from cgwidgets.utils import (
    getWidgetUnderCursor,
    isWidgetDescendantOf,
    getWidgetAncestor,
    getDefaultSavePath,
    getJSONData,
    installResizeEventFinishedEvent)

from cgwidgets.settings import attrs, iColor, keylist

from cgwidgets.widgets.AbstractWidgets.AbstractLabelledInputWidget import AbstractLabelledInputWidget
from cgwidgets.widgets.AbstractWidgets.AbstractOverlayInputWidget import AbstractOverlayInputWidget
from cgwidgets.widgets.AbstractWidgets.AbstractModelViewWidget import AbstractModelViewWidget
from cgwidgets.widgets.AbstractWidgets.AbstractShojiWidget.AbstractShojiModelViewWidget import AbstractShojiModelViewWidget
#from cgwidgets.widgets.AbstractWidgets.AbstractSplitterWidget import AbstractSplitterWidget

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
        self.setHeaderItemIsDragEnabled(False)
        self.setHeaderItemIsDropEnabled(False)
        self.setHeaderItemIsDeleteEnabled(False)
        self.setHeaderItemIsEnableable(False)

        self._temp_widgets = []
        if not widget_types:
            widget_types = []

        """ create widgets """
        # create main pip widget
        self._main_widget = PiPDisplayWidget(self)

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
    def mainWidget(self):
        return self._main_widget

    def miniViewerWidget(self):
        return self.mainWidget().miniViewerWidget()

    def mainViewerWidget(self):
        return self.mainWidget().mainViewerWidget()

    def miniViewerOrganizerWidget(self):
        return self._local_organizer_widget

    def globalOrganizerWidget(self):
        return self._global_organizer_widget

    def miniViewerCreatorWidget(self):
        return self.mainWidget()._panel_creator_widget

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
        return self.mainWidget().createNewWidgetFromConstructorCode(constructor_code)

    def createNewWidget(self, constructor_code, name="", resize_mini_viewer=True):
        """
        Args:
            constructor_code (str):
            name (str):
            resize_mini_viewer (bool): if the miniViewerWidget should be updated or not

        Returns (QModelIndex):

        """
        # create mini viewer widget
        mini_viewer_widget = self.mainWidget().createNewWidget(constructor_code, name, resize_mini_viewer)
        # print("num_widgets ==", self.mainWidget().numWidgets())
        # create new index
        index = self.miniViewerOrganizerWidget().model().insertNewIndex(0, name=name)

        item = index.internalPointer()
        item.setWidget(mini_viewer_widget)
        item.setConstructorCode(constructor_code)

        mini_viewer_widget.setIndex(0)
        mini_viewer_widget.setItem(item)

        # update indexes
        self.updateWidgetIndexes()

        # # destroy temp widgets
        if 1 < self.mainWidget().numWidgets():
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
        # todo merge this in with the pip display widget?
        for item in self.miniViewerOrganizerWidget().model().getRootItem().children():
            item.widget().setParent(None)
            item.widget().deleteLater()
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
        item.setIsDragEnabled(False)
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
        return self.mainWidget().isMiniViewerWidget()

    def setIsMiniViewerWidget(self, is_mini_viewer_widget):
        self.mainWidget().setIsMiniViewerWidget(is_mini_viewer_widget)

    """ VIRTUAL PROPERTIES """
    def setSavePath(self, file_paths):
        self.miniViewerOrganizerWidget().saveWidget().setPiPSaveData(file_paths)

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

        # if self.miniViewerWidget()._is_frozen:
        # if self.miniViewerWidget().isEnlarged():
        # close enlarged view
        # obj = getWidgetUnderCursor(QCursor.pos())
        # widget = getWidgetAncestor(obj, PiPMiniViewerWidget)
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
        # widget = getWidgetAncestor(obj, PiPMiniViewerWidget)
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
        #     widget = getWidgetAncestor(obj, PiPMiniViewerWidget)
        #     self.miniViewerWidget().closeEnlargedView(widget)
        self.miniViewerWidget().closeEnlargedView()

        # toggle visibility
        self._is_settings_visible = not self.isSettingsVisible()
        self.toggleItemVisibility("Settings", self.isSettingsVisible())

    """ EVENTS """
    def keyPressEvent(self, event):
        # if event.key() == self.swapKey():
        #     self.mainWidget().swapWidgets()
        # these are registering???
        # if event.key() == Qt.Key_F:
        #     self.toggleLocalOrganizerVisibility()
        # if event.key() == Qt.Key_G:
        #     self.toggleGlobalOrganizerVisibility()
        # if event.key() == Qt.Key_S:
        #     self.toggleSettingsVisibility()
        return AbstractShojiModelViewWidget.keyPressEvent(self, event)


class PiPDisplayWidget(QWidget):
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
        pip_scale ((float, float)):  fractional percentage of the amount of space that
            the mini viewer will take up in relation to the overall size of the widget.
        swap_key (Qt.KEY): this key will trigger the popup
        widgets (list): of widgets
    """

    def __init__(self, parent=None, is_mini_viewer_widget=False):
        super(PiPDisplayWidget, self).__init__(parent)

        # setup attrs
        self._num_widgets = 0
        self._is_frozen = True
        self._current_widget = None
        self._previous_widget = None
        self._pip_scale = (0.35, 0.35)
        self._enlarged_scale = 0.55
        self._mini_viewer_min_size = (100, 100)
        self._is_mini_viewer_shown = True
        self._is_mini_viewer_widget = is_mini_viewer_widget
        self._direction = attrs.SOUTH
        self._swap_key = Qt.Key_Space
        self._hotkey_swap_keys = [Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4, Qt.Key_5]

        # create widgets
        self._main_viewer_widget = PiPMainViewer(self)
        self._mini_viewer_widget = PiPMiniViewer(self)

        # create layout
        """Not using a stacked layout as the enter/leave events get borked"""
        #QStackedLayout(self)
        QVBoxLayout(self)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        self.layout().addWidget(self.mainViewerWidget())

        self._is_frozen = False

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

    def hotkeySwapKeys(self):
        return self._hotkey_swap_keys

    def setHotkeySwapKeys(self, hotkey_swap_keys):
        self._hotkey_swap_keys = hotkey_swap_keys

    """ PROPERTIES """
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

    def numWidgets(self):
        """ Number of widgets currently in this PiPDisplay"""
        return self.miniViewerWidget().count()

    """ UTILS """
    def areWidgetNamesShown(self):
        return self._are_widget_names_shown

    def showWidgetDisplayNames(self, enabled):
        self._are_widget_names_shown = enabled
        for widget in getWidgetAncestor(self, AbstractPiPOrganizerWidget).widgets():
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
        exec(constructor_code, globals(), loc)
        widget = loc['widget']

        return widget

    def createNewWidget(self, constructor_code, name="", resize_mini_viewer=True):
        """ Creates a new widget from the constructor code provided.

        This widget is inserted into the PiPMiniViewer

        Args:
            constructor_code (str):
            name (str):
            resize_mini_viewer (bool): if the miniViewerWidget should be updated or not

        Returns (QModelIndex):

        """

        # create widget from constructor code
        widget = self.createNewWidgetFromConstructorCode(constructor_code)
        # setup recursion for PiPWidgets
        if isinstance(widget, AbstractPiPOrganizerWidget) or isinstance(widget, PiPDisplayWidget):
            widget.setIsMiniViewerWidget(True)

        """ Note: This can't install in the MiniViewer then remove.  It will still register
        in the count, even if you process the events."""
        # create main widget
        if self.currentWidget():
            mini_viewer_widget = self.miniViewerWidget().createNewWidget(widget, name=name)

        # create mini viewer widgets
        else:
            mini_viewer_widget = PiPMiniViewerWidget(self.mainViewerWidget(), direction=Qt.Vertical, delegate_widget=widget, name=name)
            self.setCurrentWidget(mini_viewer_widget)

        # TODO This is probably causing some slowness on loading
        # as it is resizing the mini viewer EVERY time a widget is created
        if resize_mini_viewer:
            self.resizeMiniViewer()
        return mini_viewer_widget

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
            widget (QWidget): widget to be set as full screen
        """

        # todo multi recursive swapping
        if widget.isPiPWidget():
            if isinstance(widget.delegateWidget(), AbstractPiPOrganizerWidget):
                # create new pip widget
                # new_pip_widget = PiPDisplayWidget(self)
                # new_pip_widget.setMainViewerWidget(PiPMainViewer(self))
                # new_pip_widget.setMiniViewerWidget(self.miniViewerWidget())
                # self.miniViewerWidget().setParent(new_pip_widget)
                # self.mainViewerWidget().setParent(new_pip_widget)
                # new_pip_widget.setCurrentWidget(self._current_widget)
                # new_pip_widget.show()

                # update this widget
                # new_main_widget = widget.delegateWidget().mainWidget()
                # print(new_main_widget.miniViewerWidget())
                # self.setMiniViewerWidget(new_main_widget.miniViewerWidget())
                # self.setMainViewerWidget(new_main_widget.mainViewerWidget())
                # widget.miniViewerWidget()
                # do pip organize
                pass
            elif isinstance(widget.delegateWidget(), PiPDisplayWidget):
                # do pip widget swap
                pass
            print("multi recursive swapping is currently disabled... because I haven\'t set it up yet")
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
            self._current_widget.removeEventFilter(self)

            # update previous widget
            self.setPreviousWidget(self._current_widget)

        # set widget as current
        self._current_widget = widget
        self.miniViewerWidget().removeWidget(widget)
        self.mainViewerWidget().setWidget(widget)
        self._current_widget.installEventFilter(self)

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
    def eventFilter(self, obj, event):
        if event.type() == QEvent.DragEnter:
            event.accept()
        # if event.type() == QEvent.KeyPress:
        #     print('key press2 ')
        #     if event.key() == self.swapKey():
        #         if obj == self.currentWidget():
        #             print('swap1')
        #             self.swapWidgets()
        #             return True
        # elif event.type() == QEvent.Drop:
        #     print("drop???")
        #     # todo figure out how to handle this for suppressed
        #     # the event from being passed on
        #     self.miniViewerWidget().setIsDragging(False)
        #     self.miniViewerWidget().setPopupWidget(None)
        return False

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
                parent_main_widget = getWidgetAncestor(self.parent(), PiPDisplayWidget)
                parent_main_widget.miniViewerWidget().closeEnlargedView()
            return

        return QWidget.keyPressEvent(self, event)

    def leaveEvent(self, event):
        """ Blocks the error that occurs when switching between different PiPDisplays"""
        if self.miniViewerWidget().isEnlarged():
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
        if isWidgetDescendantOf(widget, self.miniViewerWidget()): return
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
        widget.layout().setContentsMargins(0, 0, 0, 0)


class PiPMiniViewer(AbstractSplitterWidget):
    """
    Widget that contains all of the PiPWidgets.

    This widget is an overlay of the MainWidget, and sits at a parallel hierarchy to the PiPMainViewer

    Attributes:
        is_dragging (bool): determines if this widget is currently in a drag/drop operation
        is_enlarged (bool): If there is currently an widget enlarged.
            Widgets are enlarged by the user hovering over them.  And closed
            be pressing "esc" or having the mouse exit the boundries of the widget.
        if_frozen (bool): Determines if events should be handled or not.
        enlarged_widget (QWidget): The widget that is currently enlarged
        popup_widget (QWidget): The widget that is displayed if the enlarged widget
            has opened a subwidget (popup) menu.
        spacer_widget (QLabel): Widget that holds the space in the QSplitter where
            the currently enlarged widget normally lives.
        _temp_sizes (list): of ints, that are the sizes of the individual widgets.
            This is normally gotten through the "sizes()" call, but needs a temp one,
            for swapping the spacer widget in/out.
        widgets (list): Of PiPMiniViewer widgets that are currently displayed.
            This does not include the currently enlarged widget

    """
    def __init__(self, parent=None, orientation=Qt.Vertical):
        super(PiPMiniViewer, self).__init__(parent, orientation)

        self._is_frozen = False
        self._is_dragging = False
        self._is_enlarged = False

        self._popup_widget = None
        self._enlarged_widget = None
        self._spacer_widget = QLabel("")
        self._spacer_widget.setParent(self.parent())
        self._spacer_widget.hide()
        self.setHandleWidth(15)

        self.addDelayedSplitterMovedEvent("set_temp_sizes", self._splitterMoved, 100)

    """ PROPERTIES """
    def isDragging(self):
        return self._is_dragging

    def setIsDragging(self, is_dragging):
        self._is_dragging = is_dragging

    def isEnlarged(self):
        return self._is_enlarged

    def setIsEnlarged(self, enabled):
        self._is_enlarged = enabled

    def isFrozen(self):
        return self._is_frozen

    def setIsFrozen(self, frozen):
        self._is_frozen = frozen

    def enlargedWidget(self):
        return self._enlarged_widget

    def setEnlargedWidget(self, widget):
        self._enlarged_widget = widget

    def popupWidget(self):
        return self._popup_widget

    def setPopupWidget(self, popup_widget):
        self._popup_widget = popup_widget

    def spacerWidget(self):
        return self._spacer_widget

    """ UTILS """
    def _swappingToFastCheck(self, widget):
        if widget == self.widget(widget.index()): return True
        if not self.widget(widget.index()): return True
        if widget.parent() == self.widget(widget.index()).parent(): return True

        return False

    def _resetSpacerWidget(self):
        """ Swaps (removes) the spacer widget with the one provided

        This swap is done when opening/closing the enlarged view.
        The spacer widget (self._spacer_widget) is used as a place
        holder.

        Args:
            widget (PiPMiniViewerWidget): to be swapped in/out
        """
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
        self.setSizes(self._temp_sizes)

    def _isCursorOverEnlargedWidget(self):
        """ Determines if the cursor is over the enlarged widget or not

        This is mainly used in the DragLeave event to determine what kind
        of leave is happening"""
        global_event_pos = QCursor.pos()
        xpos = global_event_pos.x()
        ypos = global_event_pos.y()
        top_left = self.enlargedWidget().parent().mapToGlobal(self.enlargedWidget().geometry().topLeft())
        x = top_left.x()
        y = top_left.y()
        w = self.enlargedWidget().geometry().width()
        h = self.enlargedWidget().geometry().height()
        if (x < xpos and xpos < (x + w)) and (y < ypos and ypos < (y + h)):
            return True
        else:
            return False

    """ EVENTS """
    def eventFilter(self, obj, event):
        """
        Args:
            obj:
            event:

        Note:
            _is_frozen (bool): flag to determine if the UI should be frozen for updates
            _enlarged_object (PiPMiniViewerWidget): when exiting, this is the current object that has
                been enlarged for use.
            _entered_object (PiPMiniViewerWidget): when exiting, this is the object that is under the cursor
                if the user exits into the MiniViewerWidget
            _popup_widget (QWidget): submenu that is currently open, if there are no submenu's open, this
                will be set to None
            _is_dragging (bool): determines if a drag operation is currently happening
            Signals:
                PopupWidgets:
                    When activated, this will cause a leave event, and when closed, will cause another leave event.
                    Due to how this algorithm works, it will detect the widget under the cursor, which conflicts
                    with the drag leave events =/
                DragLeave:
                    isDragging holds attribute to determine if this widget is currently in a drag/drop operation.
                    This is reset when the user hover enters a new mini widget.  When the drag leave enters a
                    widget that is in the bounds of the enlargedWidget, it will do nothing.
        """
        # if event.type() == QEvent.KeyPress:
        #     if event.key() == Qt.Key_Escape:
        #         if obj == self.enlargedWidget():
        #             self.closeEnlargedView()

        # preflight
        if self.isFrozen(): return True
        if self._popupWidgetEvent(obj, event): return True
        if self._dragEvent(obj, event): return True

        if event.type() == QEvent.Enter:
            """
            If the user exits on the first widget, or a widget that will be the enlarged widget,
            it will recurse back and enlarge itself.  This will block that recursion
            """
            if self.isEnlarged():
                # Block from re-enlarging itself
                if self.enlargedWidget() == obj:
                    return True
                # Has just enlarged the widget, but the cursor never entered it
                else:
                    # reset display label
                    self._resetSpacerWidget()

                    # reset widget to default params
                    self.setIsDragging(False)
                    self.setPopupWidget(None)

                    # enlarge widget
                    self.enlargeWidget(obj)

            # Enlarge MiniViewerWidget
            else:
                # reset widget to default params
                self.setIsDragging(False)
                self.setPopupWidget(None)

                # enlarge widget
                self.enlargeWidget(obj)
            return True

        if event.type() == QEvent.Leave:

            if obj == self.enlargedWidget():
                self.closeEnlargedView()
            return True

        return False

    def _dragEvent(self, obj, event):
        """ Handles the event filter's Drag Leave Event
        Args:
            obj (QWidget):
            event (QEvent):
        """
        if event.type() == QEvent.DragEnter:
            # enlarge widget
            if not self.isFrozen():
                # blocked recursion
                """ This will mess with the mouse position handlers """
                if not self.isEnlarged():
                    # print(" ENTER (NOT FROZEN)")
                    self.enlargeWidget(obj)
            else:
                # print(" ENTER (FROZEN)")
                self.setIsFrozen(False)
                #
            event.accept()

        if event.type() == QEvent.DragMove:
            if not self.isDragging():
                self.setPopupWidget(None)
                self.setIsDragging(True)
                self.closeEnlargedView()
                return True

        # on drop, close and reset
        if event.type() == QEvent.Drop:
            self.setIsDragging(False)
            self.setPopupWidget(None)
            self.closeEnlargedView()

        # on drag leave, if the drag leave enters a widget that
        # is a child of the current enlargedWidget, then do nothing
        if event.type() == QEvent.DragLeave:

            if self._isCursorOverEnlargedWidget():
                # print(" LEAVE (OVER)")
                # event.ignore()
                return True
            else:
                # print(" LEAVE (NOT OVER)")
                self.closeEnlargedView()
                return True

    def _popupWidgetEvent(self, obj, event):
        """ Handles the event filter for popup widgets in the enlarged view

        Args:
            obj (QWidget):
            event (QEvent):
        """
        if event.type() in [QEvent.Drop, QEvent.Leave]:

            new_object = getWidgetUnderCursor()

            # exit popup widget (shown from enlarged widget)
            if obj == self.popupWidget():
                # set cursor position to center of enlarged widget
                """ This is to make it so that a leave event is not created"""
                main_widget = getWidgetAncestor(self, PiPDisplayWidget)
                enlarged_widget = self.enlargedWidget()
                xpos, ypos = enlarged_widget.pos().x(), enlarged_widget.pos().y()
                width, height = enlarged_widget.width(), enlarged_widget.height()
                xcursor = int(xpos + (width * 0.5))
                ycursor = int(ypos + (height * 0.5))
                QCursor.setPos(main_widget.mapToGlobal(QPoint(xcursor, ycursor)))

                # reset attrs
                self.setPopupWidget(None)
                self.setIsFrozen(True)

                # ignore event
                event.ignore()
                return True

            # leave widget and enter popup widget
            if isWidgetDescendantOf(new_object, obj):
                self.setPopupWidget(obj)
                return True

    def _splitterMoved(self, *args):
        """ Sets the _temp_sizes list after the splitter has finished moving

        This ensures that when the widget is enlarged, that if the widgets
        are resized, they will be restored back to the new sizes"""
        # prelight
        if not self.isEnlarged(): return

        # User finished dragging splitter
        self._temp_sizes = self.sizes()

    def enlargeWidget(self, widget):
        """
        Enlarges the widget provided to be covering most of the main display area.

        Args:
            widget (PiPMiniViewerWidget): Widget to be enlarged
        """

        # preflight
        if not widget: return
        if not self.widget(widget.index()): return
        if self.widget(widget.index()) == self.spacerWidget(): return
        if self.widget(widget.index()).parent() == self.spacerWidget().parent():return
        if not getWidgetAncestor(widget, AbstractPiPOrganizerWidget): return
        # freeze
        self.setIsFrozen(True)

        # set/get attrs
        main_widget = getWidgetAncestor(self, PiPDisplayWidget)
        self.setIsEnlarged(True)
        self.setEnlargedWidget(widget)
        """temp sizes holds the current size of widgets
        so that they can be added/removed and restored to their original state"""
        self._temp_sizes = self.sizes()
        scale = main_widget.enlargedScale()
        negative_space = 1 - scale
        half_neg_space = negative_space * 0.5
        num_widgets = main_widget.numWidgets()
        # special case for only one mini viewer widget
        if num_widgets == 1:
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
        if 1 < num_widgets:
            # get widget position / size
            if main_widget.direction() in [attrs.EAST, attrs.WEST]:
                xoffset = int(main_widget.width() * negative_space)
                yoffset = int(main_widget.width() * negative_space)

                height = int(main_widget.height() - (yoffset * 2))
                ypos = int(yoffset)

                margins = 25
                if main_widget.direction() == attrs.EAST:
                    width = int(main_widget.width() - xoffset - self.width() + margins)
                    xpos = int(xoffset)

                if main_widget.direction() == attrs.WEST:
                    width = int(main_widget.width() - xoffset - self.width())
                    xpos = self.width() - margins

            if main_widget.direction() in [attrs.NORTH, attrs.SOUTH]:
                offset = int(self.height() * 0.75)
                xpos = int(main_widget.width() * half_neg_space)
                width = int(main_widget.width() * scale)
                height = int(main_widget.height() * (scale + half_neg_space) - offset)

                if main_widget.direction() == attrs.NORTH:
                    ypos = 0 + offset
                if main_widget.direction() == attrs.SOUTH:
                    ypos = int(main_widget.height() * (negative_space - half_neg_space))

        # Swap spacer widget
        self.replaceWidget(widget.index(), self.spacerWidget())
        self.spacerWidget().show()

        # reparent widget
        widget.setParent(self.parent())
        widget.show()

        # move / resize enlarged widget
        widget.resize(width, height)
        widget.move(xpos, ypos)

        #
        self.insertWidget(widget.index(), self._spacer_widget)
        self.setSizes(self._temp_sizes)
        self.setIsFrozen(False)

    def closeEnlargedView(self, enlarged_widget=None):
        """
        Closes the enlarged viewer, and returns it back to normal PiP mode

        Args:
            enlarged_widget (PiPMiniViewerWidget):
        """

        # preflight
        if not self.isEnlarged(): return

        # setup attrs
        self.setIsFrozen(True)
        if not enlarged_widget:
            enlarged_widget = self.enlargedWidget()
        widget_under_cursor = getWidgetUnderCursor()

        # exitted over the mini viewer
        if isWidgetDescendantOf(widget_under_cursor, self):
            if widget_under_cursor == self._spacer_widget:
                pass
            elif isinstance(widget_under_cursor, QSplitterHandle):
                pass
            else:
                # reset display label
                self._temp_sizes = self.sizes()
                self._resetSpacerWidget()

                # enlarge mini viewer
                mini_viewer_widget = getWidgetAncestor(widget_under_cursor, PiPMiniViewerWidget)
                self.enlargeWidget(mini_viewer_widget)

        else:
            # reset display label
            self._resetSpacerWidget()
            self.setIsEnlarged(False)

        self.setIsFrozen(False)

    """ WIDGETS """
    def createNewWidget(self, widget, name=""):
        """
        Creates a new widget in the mini widget.  This is only when a new widget needs to be instantiated.

        Args:
            widget:
            name:

        Returns (PiPMiniViewerWidget):
        """
        mini_widget = PiPMiniViewerWidget(self, direction=Qt.Vertical, delegate_widget=widget, name=name)
        self.insertWidget(0, mini_widget)
        return mini_widget

    def addWidget(self, widget):
        if isinstance(widget, PiPMiniViewerWidget):
            widget.installEventFilter(self)
            return QSplitter.addWidget(self, widget)
        elif widget == self.spacerWidget():
            return
        else:
            print("{widget_type} is not valid.".format(widget_type=type(widget)))
            return

    def insertWidget(self, index, widget):
        if isinstance(widget, PiPMiniViewerWidget):
            widget.installEventFilter(self)
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

    def widgets(self):
        _widgets = []
        for i in range(self.count()):
            widget = self.widget(i)
            if isinstance(widget, PiPMiniViewerWidget):
                _widgets.append(widget)
        return _widgets


class PiPMiniViewerWidget(QWidget):
    """
    One PiP Widget that is displayed in the PiPMiniViewer

    Attributes:
        index (int): current index in model
        item (PiPMiniViewerOrganizerItem)
    """
    def __init__(
        self,
        parent=None,
        name="None",
        direction=Qt.Horizontal,
        delegate_widget=None
    ):
        super(PiPMiniViewerWidget, self).__init__(parent)
        QVBoxLayout(self)

        # setup flag for if this is a pip widget (for recursive purposes
        if isinstance(delegate_widget, AbstractPiPOrganizerWidget) or isinstance(delegate_widget, PiPDisplayWidget):
            self._is_pip_widget = True
        else:
            self._is_pip_widget = False

        self._index = 0
        self._main_widget = AbstractLabelledInputWidget(
            self, name=name, direction=direction, delegate_widget=delegate_widget)
        #self._main_widget.viewWidget().delegateWidget().setUserFinishedEditingEvent(self.updateItemDisplayName)

        self.layout().addWidget(self._main_widget)
        self.layout().setContentsMargins(0, 0, 0, 0)

        # Todo find all of these handlers and remove them?
        # this is just a forced override for now
        # disable editable header
        self.headerWidget().setDisplayMode(AbstractOverlayInputWidget.DISABLED)

        #
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
    def mainWidget(self):
        return self._main_widget

    def headerWidget(self):
        return self.mainWidget().viewWidget()

    def delegateWidget(self):
        return self.mainWidget().delegateWidget()

    """ PROPERTIES """
    def isPiPWidget(self):
        return self._is_pip_widget

    def setIsPiPWidget(self, is_pip_widget):
        self._is_pip_widget = is_pip_widget

    def item(self):
        return self._item

    def setItem(self, item):
        self._item = item

    def index(self):
        return self._index

    def setIndex(self, index):
        self._index = index

    def name(self):
        return self.item().columnData()["name"]


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
            "code": """main_widget.mainWidget().setPiPScale(float(value))"""},
        "Enlarged Scale": {
            "type": attrs.FLOAT,
            "value": 0.8,
            "value_list": [0.01, 0.025, 0.05, 0.1],
            "range": [True, 0.1, 0.9],
            "code": """main_widget.mainWidget().setEnlargedScale(float(value))"""},
        "Display Titles": {
            "type": attrs.BOOLEAN,
            "value": True,
            "code": """main_widget.mainWidget().showWidgetDisplayNames(value)"""},
        "Direction": {
            "type": attrs.LIST,
            "value": attrs.SOUTH,
            "items": [[attrs.NORTH], [attrs.SOUTH], [attrs.EAST], [attrs.WEST]],
            "code": """
#print(main_widget)
#print(main_widget.mainWidget())
main_widget.mainWidget().setDirection(value)
main_widget.mainWidget().resizeMiniViewer()"""}
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
        main_widget = getWidgetAncestor(self, AbstractPiPOrganizerWidget)

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
        self.setIsDropEnabled(False)
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
    def loadPiPWidgetFromItem(self, item):
        """
        Updates the main display to the meta data of the PiPWidget that was selected

        Args:
            item (PiPGlobalOrganizerItem): selected

        Returns:

        """
        widgets = item.widgetsList()
        reversed_widgets = OrderedDict(reversed(list(widgets.items())))

        organizer_widget = getWidgetAncestor(self, AbstractPiPOrganizerWidget)
        main_widget = organizer_widget.mainWidget()
        main_widget.setIsFrozen(True)

        # clear pip view
        organizer_widget.removeAllWidgets()
        # reset previous widget
        main_widget.clearPreviousWidget()
        main_widget.clearCurrentWidget()

        # populate pip view
        # load widgets
        for widget_name, constructor_code in reversed_widgets.items():
            # print("widget_name == ", widget_name)
            organizer_widget.createNewWidget(constructor_code, name=widget_name, resize_mini_viewer=False)

        # load settings
        organizer_widget.settingsWidget().loadSettings(item.settings())

        # restore mini widget sizes
        main_widget.setIsFrozen(False)

        # todo count is wrong... for some reason...
        main_widget.resizeMiniViewer()
        # for i in range(main_widget.miniViewerWidget().count()):
        #     print("name === ", main_widget.miniViewerWidget().widget(i).name())

        if "sizes" in list(item.settings().keys()):
            organizer_widget.miniViewerWidget().setSizes(item.settings()["sizes"])

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

        # store sizes from PiPMiniViewer
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
        """
        When an item is drag/dropped, this will update the widget indexes, and reinsert
        the widget into the mini viewer if it is not currently the active widget.
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
        main_widget.updateWidgetIndexes()

    def editWidget(self, item, old_value, new_value):
        item.widget().headerWidget().setName(new_value)

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
        if organizer_widget.mainWidget().numWidgets() < 2:
            organizer_widget.createTempWidget()

        # delete widget
        item.widget().setParent(None)
        item.widget().deleteLater()
        # resize
        organizer_widget.mainWidget().resizeMiniViewer()

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
    """ """
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
from qtpy.QtWidgets import QListWidget
widget = QListWidget()
widget.setDragDropMode(QAbstractItemView.DragDrop)
widget.addItems(['a', 'b', 'c', 'd'])
# widget.setFixedWidth(100)
""",
        "Recursion":"""

save_data = {
    "Foo": {
        "file_path": getDefaultSavePath() + '/.PiPWidgets.json',
        "locked": True},
    "Bar": {
        "file_path": getDefaultSavePath() + '/.PiPWidgets_02.json',
        "locked": False}
}
widget = AbstractPiPOrganizerWidget(save_data=save_data)
widget.setDisplayWidget("Bar", "test02")
widget.setCreationMode(AbstractPiPOrganizerWidget.DISPLAY)
"""
    }
    pip_widget = AbstractPiPOrganizerWidget(save_data=save_data, widget_types=widget_types)

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
    #pip_widget.setDisplayWidget("Bar", "recursion")
    # pip_widget.setDelegateTitleIsShown(True)
    # pip_widget.setCreationMode(AbstractPiPOrganizerWidget.DISPLAY)

    sys.exit(app.exec_())
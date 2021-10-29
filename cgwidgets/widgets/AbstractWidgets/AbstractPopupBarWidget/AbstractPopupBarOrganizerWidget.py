"""
The PiPWidget is designed to display multiple widgets simultaneously to the user.

Similar to the function that was provided to TV's in the mid 1970's.  This widget is
designed to allow the user to create multiple hot swappable widgets inside of the same
widget.

Hierarchy:
    AbstractPopupBarOrganizerWidget --> (AbstractShojiModelViewWidget)
        |- AbstractPopupBarDisplayWidget
        |    |- AbstractPopupBarWidget
        |    |      or
        |    |- AbstractPiPDisplayWidget --> (QWidget)
        |        |- QVBoxLayout
        |        |    |- PiPMainViewer --> (QWidget)
        |        |    |- PiPPopupBarWidgetCreator --> (AbstractListInputWidget)
        |        |- spacer_widget (QLabel)
        |        |- AbstractPopupBarWidget (QWidget)
        |            |- QBoxLayout
        |                |-* AbstractPopupBarItemWidget --> AbstractOverlayInputWidget
        |                        |- QVBoxLayout
        |                        |- AbstractLabelledInputWidget
        |- popupBarOrganizerWidget --> AbstractModelViewWidget
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
                    {"widget name": {
                        "code": "constructor_code",
                        "Overlay Text": "text",
                        "Overlay Image": "path/on/disk/to/image"},
                    {"widget name": {
                        "code": "constructor_code",
                        "Overlay Text": "text",
                        "Overlay Image": "path/on/disk/to/image"},
                    ],
                "settings": {"setting name": "value"}},
            "PiPName2": {
                "widgets": [
                    {"widget name": {
                        "code": "constructor_code",
                        "Overlay Text": "text",
                        "Overlay Image": "path/on/disk/to/image"},
                    {"widget name": {
                        "code": "constructor_code",
                        "Overlay Text": "text",
                        "Overlay Image": "path/on/disk/to/image"},
                    ],
                "settings": {"setting name": "value"}}
            }

Signals:
    Swap (Enter):
        Upon user cursor entering a widget, that widget becomes the main widget

        AbstractPopupBarWidget --> EventFilter --> EnterEvent
        AbstractPopupBarWidget --> EventFilter --> LeaveEvent

    Swap (Key Press):
        Upon user key press on widget, that widget becomes the main widget.
        If the key is pressed over a PopupBarWidget, it will become the main widget.
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

    popupBarCreatorWidget:
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
        AbstractPopupBarOrganizerWidget --> createNewWidget --> resizePopupBar
    * Display Name (bug)
        When display names is active, when leaving the mini viewer, the widgets
        will "wobble" for a few seconds.  This is only when display names is active...
        
        Potentially a resize in the actual labelled widget?
    * Display Name
        Remove ability to adjust display name in PopupBarWidgets
            .headerWidget().setName(new_value) ?
            PopupBarWidget --> headerWidget()
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

from .AbstractPopupBarWidget import AbstractPopupBarWidget, AbstractPopupBarItemWidget, AbstractPopupBarDisplayWidget


class AbstractPopupBarOrganizerWidget(AbstractShojiModelViewWidget):
    """
    The PiPWidget is designed to display multiple widgets simultaneously to the user.

    Similar to the function that was provided to TV's in the mid 1970's.  This widget is
    designed to allow the user to create multiple hot swappable widgets inside of the same
    widget.

    Args:

    Attributes:
        current_widget (QWidget): the widget that is currently set as the main display
        direction (attrs.DIRECTION): what direction/side the popup will be displayed on
        pip_scale ((float, float)):  fractional percentage of the amount of space that
            the mini viewer will take up in relation to the overall size of the widget.
        swap_key (Qt.KEY): this key will trigger the popup
        widgets (list): of widgets

    """

    def __init__(self, parent=None, save_data=None, widget_types=None):
        super(AbstractPopupBarOrganizerWidget, self).__init__(parent)

        # setup default attrs
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
        self._popup_bar_display_widget = AbstractPopupBarDisplayWidget(self, display_mode=AbstractPopupBarDisplayWidget.PIP)

        # setup local organizer widget
        self._local_organizer_widget = PiPPopupBarOrganizerWidget(self, widget_types)
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
        self.insertShojiWidget(0, column_data={'name': 'Widget'}, widget=self._popup_bar_display_widget)

        # create temp widget
        self.createTempWidget()
        self.createTempWidget()

    def showEvent(self, event):
        indexes = self.model().findItems("Widget", Qt.MatchExactly)
        for index in indexes:
            self.setIndexSelected(index, True)
        return AbstractShojiModelViewWidget.showEvent(self, event)

    """ UTILS """
    def widgets(self):
        return self.popupBarOrganizerWidget().widgets()

    def items(self):
        """
        Gets all of the items (widgets) from the local organizer

        Returns (list)
        """

        model = self.popupBarOrganizerWidget().model()
        root_item = model.getRootItem()
        return root_item.children()

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

    def clearPopupBarOrganizerIndexes(self):
        self.popupBarOrganizerWidget().clearModel()

    """ WIDGETS (DISPLAY)"""
    def popupBarDisplayWidget(self):
        return self._popup_bar_display_widget

    def popupBarWidget(self):
        return self.popupBarDisplayWidget().popupBarWidget()

    def mainViewerWidget(self):
        return self.popupBarDisplayWidget().mainViewerWidget()

    def popupBarOrganizerWidget(self):
        return self._local_organizer_widget

    def globalOrganizerWidget(self):
        return self._global_organizer_widget

    def popupBarCreatorWidget(self):
        return self.popupBarDisplayWidget()._panel_creator_widget

    def settingsWidget(self):
        return self._settings_widget

    """ WIDGETS """
    def createNewWidgetFromConstructorCode(self, constructor_code, name="", resize_popup_bar=True):
        """
        Retuns a QWidget from the constructor code provided.

        The widget returned will be the variable "widget" from the constructor code
        Args:
            constructor_code (code):

        Returns (QModelIndex):
        """
        widget = self.popupBarDisplayWidget().createWidgetFromConstructorCode(constructor_code)
        index = self.createNewWidget(widget, name=name, resize_popup_bar=resize_popup_bar)
        index.internalPointer().setConstructorCode(constructor_code)
        return index

    def createNewWidget(self, widget, name="", resize_popup_bar=True):
        """
        Args:
            constructor_code (str):
            name (str):
            resize_popup_bar (bool): if the popupBarWidget should be updated or not

        Returns (QModelIndex):

        """
        # create mini viewer widget
        popup_bar_widget = self.popupBarDisplayWidget().createNewWidget(widget, name=name, resize_popup_bar=resize_popup_bar)

        # create new index
        index = self.popupBarOrganizerWidget().model().insertNewIndex(0, name=name)

        item = index.internalPointer()
        item.setWidget(popup_bar_widget)
        #item.setConstructorCode(constructor_code)

        # popup_bar_widget.setIndex(0)
        popup_bar_widget.setItem(item)

        # update indexes
        self.popupBarWidget().updateWidgetIndexes()
        # self.updateWidgetIndexes()

        # # destroy temp widgets
        if 1 < self.popupBarDisplayWidget().numWidgets():
            if name != "":
                self.removeTempWidget()

        return index

    def updateWidgetIndexes(self):
        """
        Runs through all of the widgets and resets their indexes.

        This will need to be done every time a new widget is added
        """
        for index in self.popupBarOrganizerWidget().model().getAllIndexes():
            item = index.internalPointer()
            if hasattr(item, "_widget"):
                item.widget().setIndex(index.row())

    def removeAllWidgets(self):
        """ Clears all of the widgets from the current AbstractPopupBarOrganizerWidget"""
        self.popupBarDisplayWidget().removeAllWidgets()
        self.popupBarOrganizerWidget().model().clearModel()

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

        index = self.createNewWidgetFromConstructorCode(constructor_code, "")

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
        model = self.popupBarOrganizerWidget().model()
        indexes = model.findItems("", match_type=Qt.MatchExactly)
        if 0 < len(indexes):
            model.deleteItem(indexes[0].internalPointer(), event_update=True)

    """ PROPERTIES """
    def isPopupBarWidget(self):
        return self.popupBarDisplayWidget().isPopupBarWidget()

    def setIsPopupBarWidget(self, is_popup_bar_widget):
        self.popupBarDisplayWidget().setIsPopupBarWidget(is_popup_bar_widget)

    """ VIRTUAL PROPERTIES """
    def setSavePath(self, file_paths):
        self.popupBarOrganizerWidget().saveWidget().setPiPSaveData(file_paths)

    def direction(self):
        return self.popupBarDisplayWidget().direction()

    def setDirection(self, direction):
        self.popupBarDisplayWidget().setDirection(direction)

    def swapKey(self):
        return self.popupBarDisplayWidget().swapKey()

    def setSwapKey(self, key):
        self.popupBarDisplayWidget().setSwapKey(key)

    def pipScale(self):
        return self.popupBarDisplayWidget().pipScale()

    def setPiPScale(self, pip_scale):
        self.popupBarDisplayWidget().setPiPScale(pip_scale)

    def enlargedScale(self):
        return self.popupBarDisplayWidget().enlargedScale()

    def setEnlargedScale(self, _enlarged_scale):
        self.popupBarDisplayWidget().setEnlargedScale(_enlarged_scale)

    def setIsDisplayNamesShown(self, enabled):
        self.popupBarDisplayWidget().setIsDisplayNamesShown(enabled)

    def currentWidget(self):
        return self.popupBarDisplayWidget().currentWidget()

    def setCurrentWidget(self, current_widget):
        self.popupBarDisplayWidget().setCurrentWidget(current_widget)

    def previousWidget(self):
        return self.popupBarDisplayWidget().previousWidget()

    def setPreviousWidget(self, previous_widget):
        self.popupBarDisplayWidget().setPreviousWidget(previous_widget)

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

        # if self.popupBarWidget()._is_frozen:
        # if self.popupBarWidget().isEnlarged():
        # close enlarged view
        # obj = getWidgetUnderCursor(QCursor.pos())
        # widget = getWidgetAncestor(obj, AbstractPopupBarItemWidget)
        # self.popupBarWidget().closeEnlargedView(widget)
        self.popupBarWidget().closeEnlargedView()

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

        # if self.popupBarWidget()._is_frozen:
        # if self.popupBarWidget().isEnlarged():
        # obj = getWidgetUnderCursor(QCursor.pos())
        # widget = getWidgetAncestor(obj, AbstractPopupBarItemWidget)
        # self.popupBarWidget().closeEnlargedView(widget)
        self.popupBarWidget().closeEnlargedView()

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

        # if self.popupBarWidget().isEnlarged():
        #     obj = getWidgetUnderCursor(QCursor.pos())
        #     widget = getWidgetAncestor(obj, AbstractPopupBarItemWidget)
        #     self.popupBarWidget().closeEnlargedView(widget)
        self.popupBarWidget().closeEnlargedView()

        # toggle visibility
        self._is_settings_visible = not self.isSettingsVisible()
        self.toggleItemVisibility("Settings", self.isSettingsVisible())


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
        "Display Titles": {
            "type": attrs.BOOLEAN,
            "value": True,
            "code": """organizer_widget.popupBarDisplayWidget().setIsDisplayNamesShown(value)""",
            "help": "Determines if the titles will be displayed or not"},
        "Direction": {
            "type": attrs.LIST,
            "value": attrs.SOUTH,
            "items": [[attrs.NORTH], [attrs.SOUTH], [attrs.EAST], [attrs.WEST]],
            "code": """
organizer_widget.popupBarDisplayWidget().closeEnlargedView()
organizer_widget.popupBarDisplayWidget().setDirection(value)
organizer_widget.popupBarDisplayWidget().resizePopupBar()""",
            "help": "Which direction the popup will occur."},
        "Display Mode":{
            "type": attrs.LIST,
            "value": AbstractPopupBarDisplayWidget.PIPTASKBAR,
            "items": [
                [AbstractPopupBarDisplayWidget.PIP],
                [AbstractPopupBarDisplayWidget.PIPTASKBAR],
                [AbstractPopupBarDisplayWidget.STANDALONETASKBAR]
            ],
            "code": """
organizer_widget.popupBarDisplayWidget().setDisplayMode(value)       

# hide/show all widgets
from cgwidgets.widgets import PopupBarDisplayWidget

# todo get all widgets to show / hide
all_widgets = [
    organizer_widget.settingsWidget().widgets()["Enlarged Scale"],
    organizer_widget.settingsWidget().widgets()["Enlarged Size"],
    organizer_widget.settingsWidget().widgets()["Overlay Text"],
    organizer_widget.settingsWidget().widgets()["Overlay Image"],
    organizer_widget.settingsWidget().widgets()["PiP Scale"],
    organizer_widget.settingsWidget().widgets()["Taskbar Size"],
]

taskbar_widgets = [
    organizer_widget.settingsWidget().widgets()["Enlarged Scale"],
    organizer_widget.settingsWidget().widgets()["Enlarged Size"],
    organizer_widget.settingsWidget().widgets()["Overlay Text"],
    organizer_widget.settingsWidget().widgets()["Overlay Image"],
]

pip_widgets = [
    organizer_widget.settingsWidget().widgets()["Enlarged Scale"],
    organizer_widget.settingsWidget().widgets()["PiP Scale"]
]

pip_taskbar_widgets = [
    organizer_widget.settingsWidget().widgets()["Enlarged Scale"],
    organizer_widget.settingsWidget().widgets()["Taskbar Size"],
    organizer_widget.settingsWidget().widgets()["Overlay Text"],
    organizer_widget.settingsWidget().widgets()["Overlay Image"],
]

# hide all
for widget in all_widgets:
    widget.hide()
# show widget
if value == PopupBarDisplayWidget.PIP:
    # show widgets
    for pip_widget in pip_widgets:
        pip_widget.show()
    # update settings
    pip_scale = organizer_widget.settingsWidget().widgets()["PiP Scale"].delegateWidget().text()
    organizer_widget.popupBarDisplayWidget().setPiPScale(float(pip_scale))

if value == PopupBarDisplayWidget.PIPTASKBAR:
    # show widgets
    for pip_taskbar_widget in pip_taskbar_widgets:
        pip_taskbar_widget.show()
    
    # update settings
    taskbar_size = organizer_widget.settingsWidget().widgets()["Taskbar Size"].delegateWidget().text()
    organizer_widget.popupBarDisplayWidget().setTaskbarSize(float(taskbar_size))
    
if value == PopupBarDisplayWidget.STANDALONETASKBAR:
    for taskbar_widget in taskbar_widgets:
        taskbar_widget.show()

# update popup bar size

organizer_widget.popupBarDisplayWidget().resizePopupBar()
            """,
            "help": "The type of display that this will use"},
        "PiP Scale": {
            "type": attrs.FLOAT,
            "value": 0.25,
            "value_list": [0.01, 0.025, 0.05, 0.1],
            "range": [True, 0.1, 1],
            "code": """organizer_widget.popupBarDisplayWidget().setPiPScale(float(value))""",
            "help": "The amount of space the PiPWidget will take up when not enlarged"},
        "Enlarged Scale": {
            "type": attrs.FLOAT,
            "value": 0.8,
            "value_list": [0.01, 0.025, 0.05, 0.1],
            "range": [True, 0.1, 0.95],
            "code": """organizer_widget.popupBarDisplayWidget().setEnlargedScale(float(value))""",
            "help": "The amount of space (percent) the PiPWidget will take when enlarged"},
        "Enlarged Size": {
            "type": attrs.FLOAT,
            "value": 500.0,
            "value_list": [1, 5, 10, 25, 50],
            "range": [False],
            "code": """organizer_widget.popupBarDisplayWidget().setEnlargedSize(float(value))""",
            "help": """The size (pixels) in the expanding direction of the enlarged widget.
    ie. if the expanding direction is set to East, this will be the width in pixels"""
        },
        "Taskbar Size": {
            "type": attrs.FLOAT,
            "value": 100.00,
            "value_list": [1, 5, 10, 25],
            "range": [False],
            "code": """
organizer_widget.popupBarDisplayWidget().setTaskbarSize(float(value))
organizer_widget.popupBarDisplayWidget().resizePopupBar()
            """,
            "help": "The size (pixels) of the taskbar when not enlarged"},
        "Overlay Text": {
            "type": attrs.STRING,
            "value": "",
            "code": """
items = organizer_widget.popupBarOrganizerWidget().getAllSelectedItems()
if 0 < len(items):
    items[0].setOverlayText(value)
# update overlay text
                """,
            "help": """The text to be overlaid while not enlarged.
This will set the overlay text for the item currently selected in the views tab"""},
        "Overlay Image": {
            "type": attrs.STRING,
            "value": "",
            "code": """
items = organizer_widget.popupBarOrganizerWidget().getAllSelectedItems()
if 0 < len(items):
    items[0].setOverlayImage(value)
            """,
            "help": """The overlay image while not enlarged.
This will set the overlay image for the item currently selected in the views tab.
You can use ../ to access the current directory"""}
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

        self.widgets()["PiP Scale"].hide()

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

        elif setting["type"] == attrs.STRING:
            delegate_widget = AbstractStringInputWidget(self)

        input_widget = AbstractLabelledInputWidget(parent=self, name=name, delegate_widget=delegate_widget)
        input_widget.viewWidget().setDisplayMode(AbstractOverlayInputWidget.DISABLED)
        input_widget.setDefaultLabelLength(125)
        input_widget.setToolTip(setting["help"])

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
        organizer_widget = getWidgetAncestor(self, AbstractPopupBarOrganizerWidget)

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
        main_widget = getWidgetAncestor(self, AbstractPopupBarOrganizerWidget)
        main_widget.setIsSettingsVisible(True)
        AbstractFrameInputWidgetContainer.showEvent(self, event)

    def hideEvent(self, event):
        main_widget = getWidgetAncestor(self, AbstractPopupBarOrganizerWidget)
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

    def filepath(self):
        return self._file_path

    def setFilepath(self, file_path):
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
    This widget will read all of the AbstractPopupBarOrganizerWidgets that the user has created.

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
        self.addContextMenuEvent("Get File Path", self.printFilepath)

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
                    file_path,
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
        container_item.setFilepath(file_path)

        # setup flags
        container_item.setIsDraggable(False)
        if locked:
            container_item.setIsLocked(True)

        return container_index

    def createNewPiPIndex(self, widget_name, file_path, widgets, settings, parent, index=0):
        """
        Creates a new PiP Index
        Args:
            file_path (str):
            widget_name (str):
            widgets ():
            settings ():
            index (int):
            parent:

        Returns:

        """
        index = self.model().insertNewIndex(index, name=widget_name, parent=parent)
        item = index.internalPointer()
        item.setWidgetsList(widgets)
        item.setSettings(settings)
        item.setItemType(PiPGlobalOrganizerItem.PIP)
        item.setFilepath(file_path)

        # set flags
        item.setIsDroppable(False)
        if index.parent().internalPointer().isLocked():
            item.setIsLocked(True)

        return item

    def printFilepath(self, index, selected_indexes):
        """ Prints the filepath of the currently selected item"""
        print(index.internalPointer().filepath())

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
        """ When an item is selected, this will update the AbstractPopupBarOrganizerWidget to the item
        that has been selected

        Args:
            item (PiPGlobalOrganizerItem):
            enabled (bool):
        """
        if enabled:
            """ All items are of type PIP except for the groups"""
            if item.itemType() == PiPGlobalOrganizerItem.PIP:
                organizer_widget = getWidgetAncestor(self, AbstractPopupBarOrganizerWidget)
                organizer_widget.popupBarDisplayWidget().popupBarWidget().closeEnlargedView()

                # load file
                organizer_widget.popupBarDisplayWidget().setFilepath(item.filepath())
                organizer_widget.popupBarDisplayWidget().loadPopupDisplayFromFile(item.filepath(), item.name(), organizer=True)

                # load settings
                organizer_widget.settingsWidget().loadSettings(item.settings())
                organizer_widget.settingsWidget().widgets()["Overlay Text"].delegateWidget().setText("")
                organizer_widget.settingsWidget().widgets()["Overlay Image"].delegateWidget().setText("")

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
        main_widget = getWidgetAncestor(self, AbstractPopupBarOrganizerWidget)
        main_widget.setIsGlobalOrganizerVisible(True)
        AbstractModelViewWidget.showEvent(self, event)

    def hideEvent(self, event):
        main_widget = getWidgetAncestor(self, AbstractPopupBarOrganizerWidget)
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
    """ The widget that will be handling the saving.

    This has the list of names of the individual items, as well
    as the save button.

    Note:
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
                    {"widget name": {
                        "code": "constructor_code",
                        "Overlay Text": "text",
                        "Overlay Image": "path/on/disk/to/image"},
                    {"widget name": {
                        "code": "constructor_code",
                        "Overlay Text": "text",
                        "Overlay Image": "path/on/disk/to/image"},
                    ],
                "settings": {"setting name": "value"}},
            "PiPName2": {
                "widgets": [
                    {"widget name": {
                        "code": "constructor_code",
                        "Overlay Text": "text",
                        "Overlay Image": "path/on/disk/to/image"},
                    {"widget name": {
                        "code": "constructor_code",
                        "Overlay Text": "text",
                        "Overlay Image": "path/on/disk/to/image"},
                    ],
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
        main_widget = getWidgetAncestor(self, AbstractPopupBarOrganizerWidget)

        # create pip save dict
        item_dict = OrderedDict()

        # store widgets in dict
        item_dict["widgets"] = OrderedDict()
        for item in main_widget.items():
            item_name = item.columnData()['name']
            item_code = item.constructorCode()

            item_dict["widgets"][item_name] = {}
            item_dict["widgets"][item_name]["code"] = item_code
            item_dict["widgets"][item_name]["Overlay Text"] = item.overlayText()
            item_dict["widgets"][item_name]["Overlay Image"] = item.overlayImage()

        # store settings in dict
        settings = {}
        for setting in main_widget.settingsWidget().settings().keys():
            if setting not in ["Overlay Text", "Overlay Image"]:
                settings[setting] = main_widget.settingsWidget().settings()[setting]["value"]

        # store sizes from AbstractPopupBarWidget
        settings["sizes"] = main_widget.popupBarWidget().sizes()

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
            file_path = item.filepath()

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
        main_widget = getWidgetAncestor(self, AbstractPopupBarOrganizerWidget)
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
        main_widget = getWidgetAncestor(self, AbstractPopupBarOrganizerWidget)

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
        main_widget = getWidgetAncestor(self, AbstractPopupBarOrganizerWidget)

        # get parent index (if Group/PiP is selected)
        selected_index = main_widget.globalOrganizerWidget().getAllSelectedIndexes()[0]
        if selected_index.internalPointer().itemType() == PiPGlobalOrganizerItem.PIP:
            parent_index = selected_index.parent()
        else:
            parent_index = selected_index
        item = main_widget.globalOrganizerWidget().createNewPiPIndex(
            name, self.currentSaveFilePath(), pip_data[name]["widgets"], pip_data[name]["settings"], parent_index, index=index)

        # reset text
        self.nameWidget().delegateWidget().setText('')
        self.updateSaveButtonText()

        # log
        parent_name = parent_index.internalPointer().name()
        print("saving ", parent_name + "/" + name, "to", self.currentSaveFilePath())
        #print('saving to... ', self.getPiPSaveData())
        return item

    def updatePiPWidgetItemInFile(self):
        """
        Updates the currently selected PiPWidgetItem if the user has made changes.
        This will only work, if the current text is empty in the name widget.
        """
        main_widget = getWidgetAncestor(self, AbstractPopupBarOrganizerWidget)
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
class PiPPopupBarOrganizerItem(AbstractDragDropModelItem):
    def __init__(self, parent=None):
        super(PiPPopupBarOrganizerItem, self).__init__(parent)

    def widget(self):
        return self._widget

    def setWidget(self, widget):
        self._widget = widget

    def overlayText(self):
        return self.widget().title()

    def setOverlayText(self, text):
        self.widget().setTitle(text)

    def overlayImage(self):
        return self.widget().overlayImage()

    def setOverlayImage(self, image_path):
        self.widget().setOverlayImage(image_path)

    def constructorCode(self):
        return self._constructor_code

    def setConstructorCode(self, constructor_code):
        self._constructor_code = constructor_code


class PiPPopupBarOrganizerWidget(AbstractModelViewWidget):
    """
    This widget is in charge of organizing widgets that will be visible in the AbstractPopupBarOrganizerWidget
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
        super(PiPPopupBarOrganizerWidget, self).__init__(parent=parent)

        # setup model
        self.model().setItemType(PiPPopupBarOrganizerItem)

        # install events
        self.setItemDeleteEvent(self.deleteWidget)
        self.setTextChangedEvent(self.editWidget)
        self.setDropEvent(self.itemReordered)
        self.setIndexSelectedEvent(self.updateGlobalSettings)

        # panel creator widget
        if not widget_types:
            widget_types = {}

        self._panel_creator_widget = PiPPopupBarWidgetCreator(self, widget_types=widget_types)
        self.addDelegate([Qt.Key_C], self._panel_creator_widget, modifier=Qt.AltModifier, focus=True)
        self._panel_creator_widget.show()

    """ UTILS """
    def widgets(self):
        return [index.internalPointer().widget() for index in self.model().getAllIndexes() if hasattr(index.internalPointer(), "_widget")]

    """ EVENTS """
    def updateGlobalSettings(self, item, enabled):
        if enabled:
            organizer_widget = getWidgetAncestor(self, AbstractPopupBarOrganizerWidget)
            settings_widget = organizer_widget.settingsWidget()
            settings_widget.widgets()["Overlay Text"].delegateWidget().setText(item.overlayText())
            settings_widget.widgets()["Overlay Image"].delegateWidget().setText(item.overlayImage())

    def itemReordered(self, data, items, model, row, parent):
        """When an item is drag/dropped, this will update the widget indexes, and reinsert
        the widget into the mini viewer if it is not currently the active widget.

        # todo this will probably need work...
        """
        # get default attrs

        main_widget = getWidgetAncestor(self, AbstractPopupBarOrganizerWidget)
        popup_bar = main_widget.popupBarWidget()
        widget = items[0].widget()

        # if in mini viewer
        # reset parent and insert back into mini viewer
        if widget.parent() == popup_bar:
            widget.setParent(None)
            widget.setIndex(row)
            popup_bar.addWidget(widget)

        # update all widget indexes
        popup_bar.updateWidgetIndexes()
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
        organizer_widget = getWidgetAncestor(self, AbstractPopupBarOrganizerWidget)

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
        if organizer_widget.popupBarDisplayWidget().numWidgets() < 2:
            organizer_widget.createTempWidget()

        # delete widget
        item.widget().setParent(None)
        item.widget().deleteLater()
        # resize
        organizer_widget.popupBarDisplayWidget().resizePopupBar()

    """ EVENTS """
    def showEvent(self, event):
        main_widget = getWidgetAncestor(self, AbstractPopupBarOrganizerWidget)
        main_widget.setIsLocalOrganizerVisible(True)
        AbstractModelViewWidget.showEvent(self, event)

    def hideEvent(self, event):
        main_widget = getWidgetAncestor(self, AbstractPopupBarOrganizerWidget)
        main_widget.setIsLocalOrganizerVisible(False)
        main_widget.setFocus()
        AbstractModelViewWidget.hideEvent(self, event)


class PiPPopupBarWidgetCreator(AbstractListInputWidget):
    """ Creates the widgets that are available in the current AbstractPiPDisplayWidget"""
    def __init__(self, parent=None, widget_types=None):
        super(PiPPopupBarWidgetCreator, self).__init__(parent)

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
        main_widget = getWidgetAncestor(self, AbstractPopupBarOrganizerWidget)

        # get constructor
        main_widget.createNewWidgetFromConstructorCode(self.widgetTypes()[value], name=str(value))

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
< Q >
Hold to hide all widgets

< Space >
Swap current display widget with previously displayed widget.  If this is pressed when the PopupBar is active, then the widget that is currently enlarged will be set as the actively displayed widget.

< 1 | 2 | 3 | 4 | 5 >
Sets the current display widget relative to the number pressed, and the widget available to be viewed in the Mini Viewer.
""")

        # setup scroll area
        self.setWidget(self.help_widget)
        self.setWidgetResizable(True)

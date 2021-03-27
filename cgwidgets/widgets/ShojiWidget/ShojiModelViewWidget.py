"""
TODO: To many updates...
        ShojiHeader --> selectionChanged
            sets the item, the resets the display which causes this to update 3 times
                1.) set item
                2.) Clear display
TODO: Hover Display Style:
        ShojiMainDelegateWidget --> installHoverDisplaySS
        settings --> HoverDisplay
        need to add default borders to input widgets and then pass through here

TODO: View scroll bar needs to change locations
    https://www.qtcentre.org/threads/23624-Scrollbar-on-the-left
    from the sounds it it. This is going to be a proxy display type setup


"""

from qtpy.QtWidgets import (
    QWidget, QAbstractItemView, QScrollArea, QSplitter, QApplication)#, qApp)
from qtpy.QtCore import Qt, QModelIndex, QEvent
from qtpy.QtGui import QCursor

from cgwidgets.utils import getWidgetAncestor, attrs, updateStyleSheet
from cgwidgets.settings.colors import iColor
from cgwidgets.settings.hover_display import installHoverDisplaySS
from cgwidgets.widgets import (
    AbstractFrameInputWidgetContainer,
    AbstractOverlayInputWidget,
    ModelViewWidget,
    AbstractShojiLayout,
    AbstractShojiLayoutHandle)

from cgwidgets.widgets.ShojiWidget import (ShojiModel, iShojiDynamicWidget, ShojiModelItem)
from cgwidgets.views import (AbstractDragDropAbstractView)


class ShojiModelViewWidget(QSplitter, iShojiDynamicWidget):
    """
    The ShojiModelViewWidget ( which needs a better name, potentially "Shoji Widget" )
    is essentially a Tab Widget which replaces the header with either a ListView, or a
    TreeView containing its own internal model.  When the user selects an item in the view, the Delegate, will be updated
    with a widget provided by one of two modes.

    Args:
        direction (ShojiModelViewWidget.DIRECTION): Determines where the tab
            bar should be placed.  The default value is NORTH

    Attributes:
        delegate_type (ShojiModelViewWidget.TYPE): What type of tab widget this should be,
            options are STACKED | DYNAMIC
            see class attrs for more info...
        selected_labels_list (list): list of labels that are currently selected by the user
        header_data (list): of strings that will be displayed as the headers header
        header_height (int): the default height of the tab label in pixels
            only works when the mode is set to view the labels on the north/south
        header_width (int): the default width of the tab label in pixels
            only works when the mode is set to view the labels on the east/west
        header_view_position (attrs.DIRECTION): Where the header should be placed

    Class Attrs:
        TYPE
            STACKED: Will operate like a normal tab, where widgets
                will be stacked on top of each other)
            DYNAMIC: There will be one widget that is dynamically
                updated based off of the labels args
            MULTI: Similar  to stacked, but instead of having one
                display at a time, multi tabs can be displayed next
                to each other.
    Essentially this is a custom tab widget.  Where the name
        label: refers to the small part at the top for selecting selections
        bar: refers to the bar at the top containing all of the aforementioned tabs
        widget: refers to the area that displays the GUI for each tab

    Hierarchy:
        |-- QBoxLayout
            | -- ShojiHeader (BaseShojiWidget)
            |    | -- ViewWidget (ShojiHeaderListView)
            |            ( ShojiHeaderListView | ShojiHeaderTableView | ShojiHeaderTreeView )
            | -- Scroll Area
                |-- DelegateWidget (ShojiMainDelegateWidget --> AbstractOverlayInputWidget)
                        | -- _temp_proxy_widget (QWidget)
                        | -* ShojiModelDelegateWidget (AbstractOverlayInputWidget)
                                | -- AbstractFrameInputWidgetContainer
    """
    OUTLINE_WIDTH = 1
    STACKED = 'stacked'
    DYNAMIC = 'dynamic'
    MULTI = False
    TYPE = STACKED
    def __init__(self, parent=None, direction=attrs.NORTH):
        super(ShojiModelViewWidget, self).__init__(parent)
        # etc attrs
        self.setHandleWidth(0)
        self._header_view_position = direction #just a temp set... for things
        self._header_delegate_position = attrs.SOUTH
        self._header_length = 50
        self._header_height = 50
        self._header_width = 100
        self._delegate_title_shown = False
        self._delegate_header_direction = Qt.Vertical

        # setup model / view
        # self._model = ShojiModel()
        self._header_widget = ShojiHeader(self)
        self._model = self.headerViewWidget().model()
        self._header_widget.setModel(self._model)
        self._header_widget.setIndexSelectedEvent(self._header_widget.selectionChanged)

        # setup delegate
        delegate_widget = ShojiMainDelegateWidget(self)
        self.setDelegateWidget(delegate_widget)
        self._temp_proxy_widget = QWidget()
        self._temp_proxy_widget.setObjectName("proxy_widget")

        self.delegateWidget().insertWidget(0, self._temp_proxy_widget)

        # setup main layout
        scroll_area = QScrollArea()
        scroll_area.setWidget(delegate_widget)
        scroll_area.setWidgetResizable(True)
        self.addWidget(scroll_area)
        scroll_area.setStyleSheet("QScrollArea{border:None}")

        self.addWidget(self._header_widget)

        # set default attrs
        self.setDelegateType(ShojiModelViewWidget.TYPE)
        self.setHeaderPosition(direction)
        self.setMultiSelect(ShojiModelViewWidget.MULTI)

        self.setHeaderWidgetToDefaultSize()

        self.updateStyleSheet()

    """ API """
    # TODO move all of these to HeaderItem...

    def normalizeWidgetSizes(self):
        self.delegateWidget().normalizeWidgetSizes()

    def setIndexSelected(self, index, selected):
        self.headerViewWidget().setIndexSelected(index, selected)

    def insertShojiWidget(
        self, row, column_data={}, parent=None, widget=None,
        image_path=None, display_overlay=None, text_color=None,
        display_delegate_title=None):
        """
        Creates a new tab at  the specified index

        Args:
            column_data (dict): for each item in this dict, there should
                be a corresponding header_item with the same string text.
                The key from this will be mapped to the header to get the
                correct values for column data.
            name (str): name of widget
            parent (QModelIndex): Parent index to create this new
                tab under neath
            row (int): index to insert widget at
            widget (QWidget): widget to be displayed at that index

            image_path (str): path on disk to image to be displayed as overlaid image
            display_overlay (bool): determines if an image/text should be overlaid over
                the widget
            text_color (RGBA): tuple255
            display_delegate_title (bool): if set will override the global settings for if
                the delgate title should be shown

        Returns (QModelIndex)
        """
        # create new model index
        if not parent:
            parent = QModelIndex()

        new_index = self.model().insertNewIndex(row, parent=parent)
        view_item = new_index.internalPointer()

        # setup extra data
        view_item.setColumnData(column_data)
        view_item.setImagePath(image_path)
        view_item.setDisplayOverlay(display_overlay)
        view_item.setTextColor(text_color)
        view_item.setDisplayDelegateTitle(display_delegate_title)

        # add to layout if stacked
        if self.getDelegateType() == ShojiModelViewWidget.STACKED:
            # create tab widget widget
            view_delegate_widget = self.createShojiModelDelegateWidget(view_item, widget)
            view_item.setDelegateWidget(view_delegate_widget)

            # insert tab widget
            self.delegateWidget().insertWidget(row, view_delegate_widget)
            view_delegate_widget.hide()

            # todo key event...
            # widget.installEventFilter(self)

        return new_index

    def getAllSelectedIndexes(self):
        # selected_indexes = []
        # for index in self.headerWidget().selectionModel().selectedIndexes():
        #     if index.column() == 0:
        #         selected_indexes.append(index)
        selected_indexes = self.headerWidget().selectionModel().selectedRows(0)
        return selected_indexes

    def rootItem(self):
        """
        Returns (ShojiModelViewItem): root item for the model
        """
        model = self.model()
        root_item = model.getRootItem()
        return root_item

    """ HEADER EVENT SIGNALS"""
    def setHeaderItemDragDropMode(self, drag_drop_mode):
        """
        Sets the drag/drop mode of the header.

        Args:
            drag_drop_mode (QAbstractItemModel.MODE): drag drop mode
                to be implemented on the header
        """
        self.headerWidget().setDragDropMode(drag_drop_mode)

    def setHeaderItemDragStartEvent(self, function):
        """
        Sets the function to be run after the drag has been initiated
        """
        self.model().setDragStartEvent(function)

    def setHeaderItemDropEvent(self, function):
        """
        Sets the function to be run after the drop event has happened.
        This function should take one arg which is a list of items that
        have been dropped
        """
        self.model().setDropEvent(function)

    def setHeaderItemTextChangedEvent(self, function):
        self.model().setTextChangedEvent(function)

    def setHeaderItemEnabledEvent(self, function):
        self.model().setItemEnabledEvent(function)

    def setHeaderItemDeleteEvent(self, function):
        self.model().setItemDeleteEvent(function)

    def setHeaderItemSelectedEvent(self, function):
        """
        Event run when the toggle is hidden/shown

        Should take two inputs
            event (QEvent)
            enabled (bool)
        """
        self.itemSelectedEvent = function

    def itemSelectedEvent(self, item, enabled, column=0):
        pass

    def setHeaderDelegateToggleEvent(self, function):
        """
        Event run when the toggle is hidden/shown

        Should take two inputs
            event (QEvent)
            enabled (bool)
        """
        self.headerWidget().setDelegateToggleEvent(function)

    """ SET FLAGS """
    def setHeaderItemIsDragEnabled(self, enabled):
        self.headerWidget().setIsDragEnabled(enabled)

    def setHeaderItemIsDropEnabled(self, enabled):
        self.headerWidget().setIsDropEnabled(enabled)

    def setHeaderItemIsRootDropEnabled(self, enabled):
        self.headerWidget().setIsRootDropEnabled(enabled)

    def setHeaderItemIsEditable(self, enabled):
        self.headerWidget().setIsEditable(enabled)

    def setHeaderItemIsSelectable(self, enabled):
        self.headerWidget().setIsSelectable(enabled)

    def setHeaderItemIsEnableable(self, enabled):
        self.headerWidget().setIsEnableable(enabled)

    def setHeaderItemIsDeleteEnabled(self, enabled):
        self.headerWidget().setIsDeleteEnabled(enabled)

    def headerDefaultLength(self):
        return self._header_length

    def setHeaderDefaultLength(self, length):
        # set attr
        self._header_length = length
        if self.headerPosition() in [attrs.NORTH, attrs.SOUTH]:
            self.header_height = length
        elif self.headerPosition() in [attrs.EAST, attrs.WEST]:
            self.header_width = length

        # update header
        self.setHeaderWidgetToDefaultSize()

    """ DELEGATE HEADER """
    def setDelegateTitleIsShown(self, enabled):
        self._delegate_title_shown = enabled
        # todo update all delegate headers

    def delegateTitleIsShown(self):
        return self._delegate_title_shown

    def setDelegateHeaderDirection(self, direction):
        self._delegate_header_direction = direction
        # todo update all delegate directions

    def delegateHeaderDirection(self):
        return self._delegate_header_direction

    """ MODEL """
    def model(self):
        return self._model

    def setModel(self, model):
        self._model = model
        self._model.setItemType(ShojiModelItem)
        self._header_widget.setModel(model)
        self._header_widget.setIndexSelectedEvent(self._header_widget.selectionChanged)

    def clearModel(self, event_update=False):
        """
        Clears the entire model
        Args:
            update_event (bool): determines if user event should be
                run on each item during the deletion process.
        """
        self.model().clearModel(event_update=event_update)
        # for child in reversed(self.rootItem().children()):
        #     self.model().deleteItem(child, event_update=event_update)

    """ VIEW """
    def headerWidget(self):
        return self._header_widget

    def setHeaderWidget(self, _header_widget):
        # remove all header widget
        if hasattr(self, '_header_widget'):
            self._header_widget.setParent(None)

        # set new header widget
        self._header_widget = _header_widget
        _header_widget.setModel(self.model())
        self.setHeaderPosition(self.headerPosition(), self._header_delegate_position)
        #self._header_widget.setIndexSelectedEvent(self._header_widget.selectionChanged)

    def headerViewWidget(self):
        return self.headerWidget().view()

    def setHeaderViewWidget(self, _header_view_widget):
        """
        Sets the header widget to be a custom widget type
        Args:
            _header_view_widget (QWidget):
        """
        # remove all header widget
        self.headerWidget().setView(_header_view_widget)
        _header_view_widget.setModel(self.model())

    def setHeaderViewType(self, view_type):
        """
        Forces the HeaderWidget to be a preset view type
        Args:
            view_type (ModelViewWidget.VIEW_TYPE): the view type to be used.
                ModelViewWidget.TREE_VIEW | ModelViewWidget.LIST_VIEW
        """
        header_view = self.headerWidget().setPresetViewType(view_type)
        self.setHeaderViewWidget(header_view)
        self.headerWidget().setModel(self.model())

    def addHeaderDelegateWidget(self, input, widget, modifier=Qt.NoModifier, focus=False):
        """
        Adds a new delegate that can be activated with the input/modifer combo provided

        Args:
            input (list): of Qt.KEY
            widget (QWidget):
            modifier (Qt.MODIFIER):
            focus (bool): determines if the widget should be focus when it is shown or not

        Returns (None):
        """
        self.headerWidget().addDelegate(input, widget, modifier=modifier, focus=focus)

    def delegateInputManifest(self):
        return self.headerWidget().delegateInputManifest()

    def headerPosition(self):
        return self._header_view_position

    def setHeaderPosition(self, header_view_position, header_delegate_position=None):
        """
        Sets the current direction this widget.  This is the orientation of
        where the tab labels will be vs where the main widget will be, where
        the tab labels bar will always be the first widget.

        Args:
            header_view_position (attrs.DIRECTION): The header VIEWs position
                relative to the Delegate Widget
            header_delegate_position (attrs.DIRECTION): The header DELEGATEs position
                relative to the header widget.
        """
        self._header_view_position = header_view_position
        self._header_delegate_position = header_delegate_position
        self.headerWidget().setParent(None)

        if self._header_view_position == attrs.WEST:
            self.setOrientation(Qt.Horizontal)
            self.headerWidget().setOrientation(Qt.Horizontal, header_delegate_position)
            self.insertWidget(0, self.headerWidget())
            self.setStretchFactor(0, 0)
            self.setStretchFactor(1, 1)

        elif self._header_view_position == attrs.EAST:
            self.setOrientation(Qt.Horizontal)
            self.headerWidget().setOrientation(Qt.Horizontal, header_delegate_position)
            self.insertWidget(1, self.headerWidget())
            self.setStretchFactor(1, 0)
            self.setStretchFactor(0, 1)

        elif self._header_view_position == attrs.NORTH:
            self.setOrientation(Qt.Vertical)
            self.headerWidget().setOrientation(Qt.Vertical, header_delegate_position)
            self.insertWidget(0, self.headerWidget())
            self.setStretchFactor(0, 0)
            self.setStretchFactor(1, 1)

        elif self._header_view_position == attrs.SOUTH:
            self.setOrientation(Qt.Vertical)
            self.headerWidget().setOrientation(Qt.Vertical, header_delegate_position)
            self.insertWidget(1, self.headerWidget())
            self.setStretchFactor(1, 0)
            self.setStretchFactor(0, 1)

        # make uncollapsible
        self.setCollapsible(0, False)
        self.setCollapsible(1, False)
        self.updateStyleSheet()

    def headerData(self):
        return self.model()._header_data

    def setHeaderData(self, _header_data):
        self.model()._header_data = _header_data

    def setHeaderWidgetToDefaultSize(self):
        """
        Moves the main slider to make the tab label bar the default startup size
        """
        if self.headerPosition() == attrs.NORTH:
            self.moveSplitter(self.header_height, 1)
        elif self.headerPosition() == attrs.SOUTH:
            self.moveSplitter(self.height() - self.header_height, 1)
        elif self.headerPosition() == attrs.WEST:
            self.moveSplitter(self.header_width, 1)
        elif self.headerPosition() == attrs.EAST:
            self.moveSplitter(self.width() - self.header_width, 1)

    def createShojiModelDelegateWidget(self, item, widget):
        """
        Creates a new tab widget widget...
        TODO:
            Move to base shoji?
        """
        # get attrs
        name = self.model().getItemName(item)
        image_path = item.imagePath()
        display_overlay = item.displayOverlay()

        # create delegate
        display_widget = ShojiModelDelegateWidget(
            self, title=name, image_path=image_path, display_overlay=display_overlay)

        # set up attrs
        display_widget.setMainWidget(widget)
        display_widget.setItem(item)

        # text color
        if item.textColor():
            display_widget.setTextColor(item.textColor())

        # display title
        if item.displayDelegateTitle():
            is_delegate_title_shown = item.displayDelegateTitle()
        else:
            is_delegate_title_shown = self.delegateTitleIsShown()
        display_widget.delegateWidget().setIsHeaderShown(is_delegate_title_shown)

        # set direction
        display_widget.delegateWidget().setDirection(self.delegateHeaderDirection())

        return display_widget

    def addContextMenuEvent(self, name, event):
        """
        Adds an entry into the RMB popup menu.

        Args:
            name (str): name of function to be displayed
            event (function): takes two args:
                item_under_cursor (item): current item under cursor
                indexes (list): of currently selected QModelIndexes
        """
        if hasattr(self.headerViewWidget(), 'addContextMenuEvent'):
            self.headerViewWidget().addContextMenuEvent(name, event)
        else:
            print('view does not have function addContextMenuEvent')

    """ DELEGATE """
    def delegateWidget(self):
        return self._delegate_widget

    def setDelegateWidget(self, _delegate_widget):
        self._delegate_widget = _delegate_widget

    def toggleDelegateSpacerWidget(self):
        """
        Determines if the spacer proxy widget should be hidden/shown in
        the delegate.  This is widget is only there to retain the spacing
        of the header/delegate positions
        """
        # hide/show proxy widget
        if hasattr(self, "_temp_proxy_widget"):
            selection_model = self.headerWidget().selectionModel()
            if len(selection_model.selectedIndexes()) == 0:
                self._temp_proxy_widget.show()
            else:
                self._temp_proxy_widget.hide()

    def updateDelegateDisplay(self):
        """

        Updates/refreshes which widgets should be shown/hidden based off of
        the current models selection list
        """
        if self.getDelegateType() == ShojiModelViewWidget.STACKED:
            self.toggleDelegateSpacerWidget()
            selection_model = self.headerWidget().selectionModel()
            widget_list = []
            for index in selection_model.selectedRows(0):
                item = index.internalPointer()
                widget = item.delegateWidget()
                widget_list.append(widget)
            self.delegateWidget().isolateWidgets(widget_list)

        # update dynamic delagate
        elif self.getDelegateType() == ShojiModelViewWidget.DYNAMIC:
            selection_model = self.headerWidget().selectionModel()
            for index in selection_model.selectedRows(0):
                item = index.internalPointer()
                delegate_widget = item.delegateWidget()
                self.updateDynamicWidget(self, delegate_widget, item)

    def updateDelegateItem(self, item, selected):
        """
        item (ShojiModelItem)
        selected (bool): determines if this item has been selected
            or un selected.
        """
        # update static widgets
        # todo column registry.
        ## note that this is set so that it will not run for each column
        if self.getDelegateType() == ShojiModelViewWidget.STACKED:
            if item.delegateWidget():
                self.__updateStackedDisplay(item, selected)

        # update dynamic widgets
        if self.getDelegateType() == ShojiModelViewWidget.DYNAMIC:
            self.__updateDynamicDisplay(item, selected)

    def __updateStackedDisplay(self, item, selected):
        """
        If the delegate display type is set to STACKED, this will
        automatically show/hide widgets as needed
        """
        if selected:
            item.delegateWidget().delegateWidget().setIsHeaderShown(self.delegateTitleIsShown())
            item.delegateWidget().show()
        else:
            try:
                item.delegateWidget().hide()
            except AttributeError:
                pass

    def __updateDynamicDisplay(self, item, selected):
        """
        If the delegate display type is set to DYNAMIC, this will
        automatically dynamically create/destroy widgets as needed.
        """

        if selected:
            # create dynamic widget
            dynamic_widget = self.createNewDynamicWidget(item)
            self.delegateWidget().addWidget(dynamic_widget)
            item.setDelegateWidget(dynamic_widget)
            self.updateDynamicWidget(self, dynamic_widget, item)
        else:
            # destroy widget
            try:
                item.delegateWidget().setParent(None)
                # item.delegateWidget().deleteLater()
            except AttributeError:
                pass

    """ DYNAMIC WIDGET """
    def createNewDynamicWidget(self, item):
        # check item for dynamic base class if it has that, use that
        if item.getDynamicWidgetBaseClass():
            dynamic_widget_class = item.getDynamicWidgetBaseClass()
        else:
            dynamic_widget_class = self.getDynamicWidgetBaseClass()

        new_dynamic_widget = dynamic_widget_class()
        new_widget = self.createShojiModelDelegateWidget(item, new_dynamic_widget)
        return new_widget

    def updateDynamicWidget(self, parent, widget, item, *args, **kwargs):
        """
        Updates the dynamic widget

        Args:
            widget (DynamicWidget) The dynamic widget that should be updated
            item (TabShojiLabelWidget): The tab label that should be updated
        """
        # needs to pick which to update...
        if item.getDynamicUpdateFunction():
            dynamic_update_function = item.getDynamicUpdateFunction()
        else:
            dynamic_update_function = self.getDynamicUpdateFunction()

        dynamic_update_function(parent, widget, item, *args, **kwargs)

    """ EVENTS """
    def showEvent(self, event):
        return_val = QSplitter.showEvent(self, event)
        self.setHeaderWidgetToDefaultSize()
        self.updateStyleSheet()
        return return_val

    def resizeEvent(self, event):
        model = self.model()
        num_items = model.getRootItem().childCount()
        if 0 < num_items:
            # update width
            if self.headerPosition() in [
                attrs.NORTH,
                attrs.SOUTH
            ]:
                width = int( self.width() / num_items )
                if ShojiModel.ITEM_WIDTH < width:
                    model.item_width = width
                    self.updateStyleSheet()
        return QSplitter.resizeEvent(self, event)

    @staticmethod
    def isWidgetUnderCursorChildOfHeader():
        """
        Determines if the widget under the cursor is a child of the header.

        This is to determine where key press events happen and to send that signal
        to the correct side of the widget.
        Returns:

        """
        pos = QCursor.pos()
        #widget_pressed = qApp.widgetAt(pos)
        widget_pressed = QApplication.instance().widgetAt(pos)
        is_child_of_header = None
        if widget_pressed:
            is_child_of_header = getWidgetAncestor(widget_pressed, ShojiHeader)
        return True if is_child_of_header else False

    """ PROPERTIES """
    """ selection """
    def setMultiSelect(self, enabled):
        self._multi_select = enabled
        self.headerWidget().setMultiSelect(enabled)

    def getMultiSelect(self):
        return self._multi_select

    def setMultiSelectDirection(self, orientation):
        """
        Sets the orientation of the multi select mode.

        orientation (Qt.ORIENTATION): ie Qt.Vertical or Qt.Horizontal
        """
        self.delegateWidget().setOrientation(orientation)
        self.updateStyleSheet()

    def multiSelectDirection(self):
        return self.delegateWidget().orientation()

    """ type """
    def setDelegateType(self, value, dynamic_widget=None, dynamic_function=None):
        """
        Sets the type of this widget.  This will reset the entire layout to a blank
        state.

        Args:
            value (ShojiModelViewWidget.TYPE): The type of tab menu that this
                widget should be set to
            dynamic_widget (QWidget): The dynamic widget to be displayed.
            dynamic_function (function): The function to be run when a label
                is selected.
        """
        # update layout
        if value == ShojiModelViewWidget.STACKED:
            pass
        elif value == ShojiModelViewWidget.DYNAMIC:
            self.setDynamicWidgetBaseClass(dynamic_widget)
            self.setDynamicUpdateFunction(dynamic_function)

        # update attr
        self._delegate_type = value

    def getDelegateType(self):
        return self._delegate_type

    """ LAYOUT """
    def updateStyleSheet(self):
        """
        Sets the style sheet for the outline based off of the direction of the parent.
        """
        self.setHandleWidth(0)

        # create style sheet
        style_sheet_args = iColor.style_sheet_args
        style_sheet_args = AbstractDragDropAbstractView.createAbstractStyleSheet(
            self.headerWidget().view(),
            style_sheet_args,
            header_position=self.headerPosition(),
            outline_width=ShojiModelViewWidget.OUTLINE_WIDTH
        )

        # apply style
        style_sheet = """
        {header_style_sheet}
        {splitter_style_sheet}
        """.format(**style_sheet_args)
        self.setStyleSheet(style_sheet)

        # update hover display of children
        for index in self.model().getAllIndexes():
            widget = index.internalPointer().delegateWidget()
            if widget:
                self.delegateWidget().installHoverDisplay(widget)

    """ default view size"""
    @property
    def header_width(self):
        return self._header_width

    @header_width.setter
    def header_width(self, header_width):
        self._header_width = header_width

    @property
    def header_height(self):
        return self._header_height

    @header_height.setter
    def header_height(self, _header_height):
        self._header_height = _header_height


""" LAYOUT """
class ShojiLayout(AbstractShojiLayout):
    def __init__(self, parent=None, orientation=Qt.Vertical):
        super(ShojiLayout, self).__init__(parent, orientation=orientation)


class ShojiLayoutHandle(AbstractShojiLayoutHandle):
    def __init__(self, orientation, parent=None):
        super(ShojiLayoutHandle, self).__init__(orientation, parent)


""" DELEGATE """
class ShojiMainDelegateWidget(ShojiLayout):
    """
    The main delegate view that will show all of the items widgets that
    the user currently has selected
    """
    def __init__(self, parent=None):
        super(ShojiMainDelegateWidget, self).__init__(parent)
        self.rgba_background = iColor["rgba_background_00"]
        self.setToggleSoloViewEvent(self.resetShojiLayoutDisplay)

    def resetShojiLayoutDisplay(self, enabled, widget):
        """
        Resets the display of the Shoji View back to default
        Args:
            enabled:
            widget:

        Returns:

        """
        if not enabled:
            tab_shoji_widget = getWidgetAncestor(self, ShojiModelViewWidget)
            if tab_shoji_widget:
                tab_shoji_widget.updateDelegateDisplay()
                tab_shoji_widget.toggleDelegateSpacerWidget()

    def showEvent(self, event):
        tab_shoji_widget = getWidgetAncestor(self, ShojiModelViewWidget)
        if tab_shoji_widget:
            tab_shoji_widget.updateDelegateDisplay()

    def installHoverDisplay(self, widget):
        """
        Installs the hover display mechanisn on child widgets

        Args:
            widget (QWidget): child to have hover display installed on.

        Note:
            This overrides the default behavior from the ShojiLayout
        """
        # get attrs
        # print('should do this?')
        hover_type_flags = {
            'focus':{'hover_display':True},
            'hover_focus':{'hover_display':True},
            'hover':{'hover_display':True},
        }
        tab_shoji_widget = getWidgetAncestor(self, ShojiModelViewWidget)

        # install hover display
        if tab_shoji_widget:
            # Setup border walls for each position / direction combo
            position = tab_shoji_widget.headerPosition()
            direction = tab_shoji_widget.multiSelectDirection()
            if direction == Qt.Vertical:
                if position == attrs.EAST:
                    border_walls = [attrs.NORTH, attrs.SOUTH, attrs.WEST]
                if position == attrs.WEST:
                    border_walls = [attrs.NORTH, attrs.SOUTH, attrs.EAST]
                if position in [attrs.NORTH, attrs.SOUTH]:
                    border_walls = [attrs.NORTH, attrs.SOUTH, attrs.EAST, attrs.WEST]

            if direction == Qt.Horizontal:
                if position == attrs.NORTH:
                    border_walls = [attrs.EAST, attrs.WEST, attrs.SOUTH]
                if position == attrs.SOUTH:
                    border_walls = [attrs.EAST, attrs.WEST, attrs.NORTH]
                if position in [attrs.EAST, attrs.WEST]:
                    border_walls = [attrs.NORTH, attrs.SOUTH, attrs.EAST, attrs.WEST]

            # install hover display
            installHoverDisplaySS(
                widget,
                name="SHOJI VIEW",
                hover_type_flags=hover_type_flags,
                border_walls=border_walls)

        # install event filter
        widget.installEventFilter(self)
        return

    def eventFilter(self, obj, event):
        """
        Events run on every child widget.

        Handles the dynamic style sheet updates, and overrides
        the solo view operator.

        Note: This is copy/pasted from the ShojiLayout to be modified
        """
        # preflight
        if event.type() not in [QEvent.Enter, QEvent.Leave]: return False

        # this is super expensive, like your mom
        tab_shoji_widget = getWidgetAncestor(self, ShojiModelViewWidget)
        if not tab_shoji_widget: return False

        # setup hover display
        view_widget = tab_shoji_widget.headerViewWidget()
        selection = view_widget.selectionModel().selectedRows(0)

        # # hover properties
        if event.type() == QEvent.Enter:
            if 1 < len(selection):
                obj.setProperty("hover_display", True)

            else:
                obj.setProperty("hover_display", False)
            updateStyleSheet(obj)

        if event.type() == QEvent.Leave:
            obj.setProperty("hover_display", False)
            updateStyleSheet(obj)
        # return True

        return False

    def keyPressEvent(self, event):
        # preflight | suppress if over header
        is_child_of_header = ShojiModelViewWidget.isWidgetUnderCursorChildOfHeader()
        tab_shoji_widget = getWidgetAncestor(self, ShojiModelViewWidget)
        if is_child_of_header:
            return tab_shoji_widget.headerWidget().keyPressEvent(event)
        else:
            return ShojiLayout.keyPressEvent(self, event)


class ShojiModelDelegateWidget(AbstractOverlayInputWidget):
    def __init__(self, parent=None, title="Title", image_path=None, display_overlay=False):
        super(ShojiModelDelegateWidget, self).__init__(parent, title=title, image_path=image_path)

        self.setDisplayMode(AbstractOverlayInputWidget.ENTER)

        # setup delegate
        delegate_widget = AbstractFrameInputWidgetContainer(self, title=title)
        delegate_widget.layout().setContentsMargins(0, 0, 0, 0)
        delegate_widget.setIsHeaderEditable(False)
        self.setDelegateWidget(delegate_widget)

        if not display_overlay:
            self.setCurrentIndex(1)
            self.setDisplayMode(AbstractOverlayInputWidget.DISABLED)

    def setMainWidget(self, widget):
        # remove old main widget if it exists
        if hasattr(self, '_main_widget'):
            self._main_widget.setParent(None)

        self._main_widget = widget
        self.delegateWidget().layout().addWidget(self._main_widget)

    def getMainWidget(self):
        return self._main_widget

    def setItem(self, item):
        self._item = item

    def item(self):
        return self._item


# class ShojiModelDelegateWidget(AbstractFrameInputWidgetContainer):
#     """
#     Attributes:
#         main_widget (QWidget): the main display widget
#         item (ShojiModelItem): The item from the model that is associated with
#             this delegate
#     """
#     def __init__(self, parent=None, title=None):
#         super(ShojiModelDelegateWidget, self).__init__(parent, title=title)
#
#         self.layout().setContentsMargins(0, 0, 0, 0)
#
#     def setMainWidget(self, widget):
#         # remove old main widget if it exists
#         if hasattr(self, '_main_widget'):
#             self._main_widget.setParent(None)
#
#         self._main_widget = widget
#         self.layout().addWidget(self._main_widget)
#
#     def getMainWidget(self):
#         return self._main_widget
#
#     def setItem(self, item):
#         self._item = item
#
#     def item(self):
#         return self._item


""" HEADER """
class ShojiHeader(ModelViewWidget):
    LIST_VIEW = 0
    TREE_VIEW = 1
    def __init__(self, parent=None):
        super(ShojiHeader, self).__init__(parent)
        # self.setPresetViewType(ModelViewWidget.LIST_VIEW)
        model = ShojiModel()
        self.setModel(model)
        self.setIsDropEnabled(False)

    def showEvent(self, event):
        tab_shoji_widget = getWidgetAncestor(self, ShojiModelViewWidget)
        if tab_shoji_widget:
            tab_shoji_widget.updateDelegateDisplay()
        ModelViewWidget.showEvent(self, event)

    def dropEvent(self, event):
        # resolve drop event
        return_val = super(self.__class__, self).dropEvent(event)

        # get main widget
        main_widget = getWidgetAncestor(self, ShojiModelViewWidget)

        # clear selection
        main_widget.delegateWidget().displayAllWidgets(False)
        self.selectionModel().clearSelection()

        return return_val

    def selectionChanged(self, item, enabled):
        """
        Determines whether or not an items delegateWidget() should be
        displayed/updated/destroyed.
        """

        # todo for some reason this double registers the selection even
        # when using dynamic tree widgets...
        top_level_widget = getWidgetAncestor(self, ShojiModelViewWidget)
        top_level_widget.toggleDelegateSpacerWidget()

        # update display
        top_level_widget._selection_item = enabled
        top_level_widget.updateDelegateItem(item, enabled)

        # update delegate background
        if hasattr(top_level_widget, '_delegate_widget'):
            selection = top_level_widget.headerWidget().selectionModel().selectedIndexes()
            if len(selection) == 0:
                top_level_widget.delegateWidget().rgba_background = iColor['rgba_background_00']
            else:
                top_level_widget.delegateWidget().rgba_background = iColor['rgba_background_01']

        # custom input event | need this as we're overriding the models input

        top_level_widget.itemSelectedEvent(item, enabled)
        # Todo causing multiple selection bug...
        # update full screen selection
        # selected
        if enabled:
            if hasattr(top_level_widget, '_delegate_widget'):
                delegate_widget = top_level_widget.delegateWidget()
                delegate_widget.resetShojiLayoutDisplay(False, delegate_widget)
                delegate_widget.setIsSoloView(delegate_widget, False)


""" EXAMPLE """
class TabShojiDynamicWidgetExample(QWidget):
    """
    TODO:
        turn this into an interface for creating dynamic tab widgets
    """
    def __init__(self, parent=None):
        super(TabShojiDynamicWidgetExample, self).__init__(parent)
        QVBoxLayout(self)
        self.label = QLabel('init')
        self.layout().addWidget(self.label)

    @staticmethod
    def updateGUI(parent, widget, item):
        """
        widget (ShojiModelDelegateWidget)
        item (ShojiModelItem)
        """
        print('update gui')
        # if item:
        #     widget.setTitle(item.name())
        #     widget.getMainWidget().label.setText(item.name())


"""
TODO popup search delegate...
Need:
    QlineEdit
        --> Finished editing signal exposed
        --> Signal needs to receive
                    ShojiHeaderView
                    MainShoji?

Search items
    Hotkey --> Popup LineEdit (s)
Create New Item
    Hotkey --> Popup LineEdit (c)

"""


# def toggleDelegateEvent(self, event, enabled):
#     self.__toggleDelegateEvent(event, enabled)
#     pass
if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication, QLabel, QVBoxLayout
    from qtpy.QtGui import QCursor
    app = QApplication(sys.argv)
    # w = ShojiHeader()
    # w.show()


    class test(ModelViewWidget):
        def __init__(self, parent=None):
            super(test, self).__init__(parent)
            self.addWidget(QLabel('a'))
            self.addWidget(QLabel('b'))
            self.addWidget(QLabel('c'))

    shoji_widget = ShojiModelViewWidget()
    shoji_widget.setDelegateType(ShojiModelViewWidget.DYNAMIC,TabShojiDynamicWidgetExample, TabShojiDynamicWidgetExample.updateGUI)
    #w.setHeaderPosition(attrs.WEST, attrs.SOUTH)
    #header_delegate_widget = QLabel("Custom")
    #w.setHeaderDelegateAlwaysOn(False)
    #
    # shoji_widget.setMultiSelect(True)
    #w.setOrientation(Qt.Horizontal)
    # w.setHeaderPosition(attrs.NORTH)
    # w.setMultiSelectDirection(Qt.Horizontal)

    # w.setHeaderItemDragDropMode(QAbstractItemView.InternalMove)
    # delegate_widget = QLabel("Q")
    # w.addHeaderDelegateWidget([Qt.Key_Q], delegate_widget)
    #
    # dw = TabShojiDynamicWidgetExample

    for x in range(3):
        widget = QLabel(str(x))
        parent_item = shoji_widget.insertShojiWidget(x, column_data={'name':str(x), 'one':'test'}, widget=widget)

    for y in range(0, 2):
        shoji_widget.insertShojiWidget(y, column_data={'name':str(y)}, widget=widget, parent=parent_item)
    shoji_widget.setHeaderPosition(attrs.WEST, attrs.SOUTH)
    shoji_widget.setMultiSelectDirection(Qt.Vertical)

    shoji_widget.resize(500, 500)
    shoji_widget.delegateWidget().setHandleLength(100)

    shoji_widget.show()
    # #w.headerWidget().model().setIsDragEnabled(False)
    # w.setHeaderItemIsDropEnabled(True)
    # w.setHeaderItemIsDragEnabled(True)
    # w.setHeaderItemIsEnableable(True)
    # w.setHeaderItemIsDeleteEnabled(False)
    shoji_widget.move(QCursor.pos())

    sys.exit(app.exec_())

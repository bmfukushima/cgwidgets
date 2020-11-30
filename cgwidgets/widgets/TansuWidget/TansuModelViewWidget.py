"""
TansuModelViewWidget(QSplitter, iTansuDynamicWidget):
    |-- QBoxLayout
        | -- TansuHeader (BaseTansuWidget)
            TODO:
                * View scroll bar needs to change locations
                https://www.qtcentre.org/threads/23624-Scrollbar-on-the-left
                from the sounds it it. This is going to be a proxy display type setup
            | -- ViewWidget (TansuHeaderListView)
                    ( TansuHeaderListView | TansuHeaderTableView | TansuHeaderTreeView )
            | -- TODO # widget is provided as a label right now
                    *  This still needs the API set up for the arbitrary widget
                    *  Display Mode ( On / Off / Hotkey popup )

        | -- Scroll Area
            |-- DelegateWidget (TansuMainDelegateWidget --> TansuBaseWidget)
                    | -- _temp_proxy_widget (QWidget)
                    | -* TansuModelDelegateWidget (AbstractGroupBox)
                            | -- Stacked/Dynamic Widget (main_widget)
"""

from qtpy.QtWidgets import (
    QWidget, QListView, QAbstractItemView, QScrollArea, QSplitter, QLabel, qApp)
from qtpy.QtCore import Qt, QModelIndex
from qtpy.QtGui import QCursor

from cgwidgets.utils import getWidgetAncestor, attrs
from cgwidgets.settings.colors import iColor
from cgwidgets.settings.keylist import CHARACTER_KEYS
from cgwidgets.widgets import AbstractFrameGroupInputWidget

from cgwidgets.widgets.TansuWidget import (
    TansuBaseWidget, TansuModel, iTansuDynamicWidget
)
from cgwidgets.views import (
    AbstractDragDropTreeView,
    AbstractDragDropListView,
    AbstractDragDropAbstractView

)


class TansuModelViewWidget(QSplitter, iTansuDynamicWidget):
    """
    This is the designing portion of this editor.  This is where the TD
    will design a custom UI/hooks/handlers for the tool for the end user,
    which will be displayed in the ViewWidget

    Args:
        direction (TansuModelViewWidget.DIRECTION): Determines where the tab
            bar should be placed.  The default value is NORTH

    Attributes:
        delegate_type (TansuModelViewWidget.TYPE): What type of tab widget this should be,
            options are STACKED | DYNAMIC
            see class attrs for more info...
        selected_labels_list (list): list of labels that are currently selected by the user
        header_data (list): of strings that will be displayed as the headers header
        header_height (int): the default height of the tab label in pixels
            only works when the mode is set to view the labels on the north/south
        header_width (int): the default width of the tab label in pixels
            only works when the mode is set to view the labels on the east/west
        header_position (attrs.DIRECTION): Where the header should be placed

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
    """
    OUTLINE_WIDTH = 1
    STACKED = 'stacked'
    DYNAMIC = 'dynamic'
    MULTI = False
    TYPE = STACKED

    # delegate hotkey toggle buttons
    TOGGLE_DELEGATE_KEYS = [key for key in CHARACTER_KEYS if key not in [Qt.Key_D]]
    #TOGGLE_DELEGATE_KEYS = [Qt.Key_D]
    def __init__(self, parent=None, direction=attrs.NORTH):
        super(TansuModelViewWidget, self).__init__(parent)
        # etc attrs
        self.setHandleWidth(0)
        self._header_position = direction #just a temp set... for things
        self._header_length = 50
        self._header_height = 50
        self._header_width = 100
        self._delegate_header_shown = True
        self._delegate_header_direction = Qt.Vertical

        # setup model / view
        self._model = TansuModel()
        self._header_widget = TansuHeader(self)
        #self._header_widget = TansuHeaderListView(self)
        self._header_widget.setModel(self._model)
        #self._model.header_type = str(type(self._header_widget))

        # # setup drag/drop
        # self._isSelectable = False
        # self.setIsDragDropEnabled(False)
        # self._isEditable = False

        # setup delegate
        delegate_widget = TansuMainDelegateWidget()
        self.setDelegateWidget(delegate_widget)
        self._temp_proxy_widget = QWidget()
        self._temp_proxy_widget.setObjectName("proxy_widget")

        self.delegateWidget().addWidget(self._temp_proxy_widget)

        # setup main layout
        scroll_area = QScrollArea()
        scroll_area.setWidget(delegate_widget)
        scroll_area.setWidgetResizable(True)
        self.addWidget(scroll_area)

        # TEMP
        scroll_area.setStyleSheet("QScrollArea{border:None}")
        self.addWidget(self._header_widget)

        # set default attrs
        self.setDelegateType(TansuModelViewWidget.TYPE)
        self.setHeaderPosition(direction)
        self.setMultiSelect(TansuModelViewWidget.MULTI)

        self.setHeaderWidgetToDefaultSize()

        self.updateStyleSheet()

    """ API """
    # TODO move all of these to HeaderItem...

    def insertTansuWidget(self, row, column_data={}, parent=None, widget=None):
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

        Returns (QModelIndex)
        """
        # create new model index
        if not parent:
            parent = QModelIndex()
        self.model().insertRow(row, parent)

        # setup custom object
        item_type = self.model().itemType()
        view_item = item_type()
        #view_item.setColumnData(column_data)

        self.model().createIndex(row, 1, view_item)

        # get new index/item created
        new_index = self.model().index(row, 1, parent)
        view_item = new_index.internalPointer()
        view_item.setColumnData(column_data)

        # add to layout if stacked
        if self.getDelegateType() == TansuModelViewWidget.STACKED:
            # create tab widget widget
            view_delegate_widget = self.createTansuModelDelegateWidget(view_item, widget)
            view_item.setDelegateWidget(view_delegate_widget)

            # insert tab widget
            self.delegateWidget().insertWidget(row, view_delegate_widget)
            view_delegate_widget.hide()

        return new_index

    def getAllSelectedIndexes(self):
        selected_indexes = []
        for index in self.headerWidget().selectionModel().selectedIndexes():
            if index.column() == 0:
                selected_indexes.append(index)
        return selected_indexes

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
    def setIsDelegateHeaderShown(self, enabled):
        self._delegate_header_shown = enabled
        # todo update all delegate headers

    def isDelegateHeaderShown(self):
        return self._delegate_header_shown

    def setDelegateHeaderDirection(self, direction):
        self._delegate_header_direction = direction
        # todo update all delegate directions

    def delegateHeaderDirection(self):
        return self._delegate_header_direction

    """ MODEL """
    def model(self):
        return self._model

    def setModel(self, model):
        self._header_widget.setModel(model)
        self._model = model

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
        self.setHeaderPosition(self.headerPosition())
        #self.model().header_type = str(type(self.headerWidget()))

    def headerViewWidget(self):
        return self._header_view_widget

    def setHeaderViewWidget(self, _header_view_widget):
        # remove all header widget
        self.headerWidget().setView(_header_view_widget)
        _header_view_widget.setModel(self.model())

    def headerDelegateWidget(self):
        return self.headerWidget().delegate()

    def setHeaderDelegateWidget(self, widget):
        """
        Interface to set the headers delegate widget
        """
        self.headerWidget().setDelegate(widget)

    def headerDelegateAlwaysOn(self):
        return self.headerWidget().delegateWidgetAlwaysOn()

    def setHeaderDelegateAlwaysOn(self, enabled):
        """
        Interface to determine if header delegate widget is enabled
        """
        self.headerWidget().setDelegateWidgetAlwaysOn(enabled)

    def headerPosition(self):
        return self._header_position

    def setHeaderPosition(self, header_widget_position, header_view_position=None):
        """
        Sets the current direction this widget.  This is the orientation of
        where the tab labels will be vs where the main widget will be, where
        the tab labels bar will always be the first widget.

        Args:
            header_widget_position (attrs.DIRECTION): The header WIDGETs position
                relative to the Delegate Widget
            header_view_position (attrs.DIRECTION): The header VIEWs position
                relative to the header widget.
        """
        self._header_position = header_widget_position
        self.headerWidget().setParent(None)

        if self._header_position == attrs.WEST:
            self.setOrientation(Qt.Horizontal)
            self.headerWidget().setOrientation(Qt.Horizontal, header_view_position)
            self.insertWidget(0, self.headerWidget())
            self.setStretchFactor(0, 0)
            self.setStretchFactor(1, 1)

        elif self._header_position == attrs.EAST:
            self.setOrientation(Qt.Horizontal)
            self.headerWidget().setOrientation(Qt.Horizontal, header_view_position)
            self.insertWidget(1, self.headerWidget())
            self.setStretchFactor(1, 0)
            self.setStretchFactor(0, 1)

        elif self._header_position == attrs.NORTH:
            self.setOrientation(Qt.Vertical)
            self.headerWidget().setOrientation(Qt.Vertical, header_view_position)
            self.insertWidget(0, self.headerWidget())
            self.setStretchFactor(0, 0)
            self.setStretchFactor(1, 1)

        elif self._header_position == attrs.SOUTH:
            self.setOrientation(Qt.Vertical)
            self.headerWidget().setOrientation(Qt.Vertical, header_view_position)
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

    def createTansuModelDelegateWidget(self, item, widget):
        """
        Creates a new tab widget widget...
        TODO:
            Move to base tansu?
        """
        # get attrs
        name = self.model().getItemName(item)

        # create delegate
        display_widget = TansuModelDelegateWidget(self, name)

        # set up attrs
        display_widget.setMainWidget(widget)
        display_widget.setItem(item)
        display_widget.setIsHeaderShown(self.isDelegateHeaderShown())
        display_widget.setDirection(self.delegateHeaderDirection())

        return display_widget

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
        Updates which widgets should be shown/hidden based off of
        the current models selection list
        """
        if self.getDelegateType() == TansuModelViewWidget.STACKED:
            self.toggleDelegateSpacerWidget()
            selection_model = self.headerWidget().selectionModel()
            widget_list = []
            for index in selection_model.selectedIndexes():
                item = index.internalPointer()
                widget = item.delegateWidget()
                widget_list.append(widget)
            self.delegateWidget().isolateWidgets(widget_list)
        # TODO updated for dynamic... I've never used this...
        elif self.getDelegateType() == TansuModelViewWidget.DYNAMIC:
            selection_model = self.headerWidget().selectionModel()
            for index in selection_model.selectedIndexes():
                item = index.internalPointer()
                if index.column() == 0:
                    self.__updateDelegateItem(item, False)
                    self.__updateDelegateItem(item, True)
            #self.updateDynamicWidget()

    def updateDelegateDisplayFromSelection(self, selected, deselected):
        """
        Determines whether or not an items delegateWidget() should be
        displayed/updated/destroyed.

        """
        self.toggleDelegateSpacerWidget()

        # update display
        self._selection_item = selected
        for index in selected.indexes():
            if index.column() == 0:
                item = index.internalPointer()
                self.__updateDelegateItem(item, True)

        for index in deselected.indexes():
            item = index.internalPointer()
            #item.setSelected(False)
            self.__updateDelegateItem(item, False)

        # update delegate background
        if hasattr(self, '_delegate_widget'):
            selection = self.headerWidget().selectionModel().selectedIndexes()
            if len(selection) == 0:
                self.delegateWidget().rgba_background = iColor['rgba_gray_0']
            else:
                self.delegateWidget().rgba_background = iColor['rgba_gray_1']

    def __updateDelegateItem(self, item, selected):
        """
        item (TansuModelItem)
        selected (bool): determines if this item has been selected
            or un selected.
        """
        # update static widgets
        if self.getDelegateType() == TansuModelViewWidget.STACKED:
            if item.delegateWidget():
                self.__updateStackedDisplay(item, selected)

        # update dynamic widgets
        if self.getDelegateType() == TansuModelViewWidget.DYNAMIC:
            self.__updateDynamicDisplay(item, selected)

    def __updateStackedDisplay(self, item, selected):
        """
        If the delegate display type is set to STACKED, this will
        automatically show/hide widgets as needed
        """
        if selected:
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
        new_widget = self.createTansuModelDelegateWidget(item, new_dynamic_widget)
        return new_widget

    def updateDynamicWidget(self, parent, widget, item, *args, **kwargs):
        """
        Updates the dynamic widget

        Args:
            widget (DynamicWidget) The dynamic widget that should be updated
            item (TabTansuLabelWidget): The tab label that should be updated
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
        #return QSplitter.showEvent(self, event)

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
                if TansuModel.ITEM_WIDTH < width:
                    model.item_width = width
                    self.updateStyleSheet()
        return QSplitter.resizeEvent(self, event)

    @staticmethod
    def isWidgetUnderCursorChildOfHeader():
        pos = QCursor.pos()
        widget_pressed = qApp.widgetAt(pos)
        is_child_of_header = getWidgetAncestor(widget_pressed, TansuHeader)
        return True if is_child_of_header else False

    def keyPressEvent(self, event):
        is_child_of_header = TansuModelViewWidget.isWidgetUnderCursorChildOfHeader()
        if is_child_of_header:
            return self.headerWidget().keyPressEvent(event)

        # do tansu widget key press event
        else:
            return self.delegateWidget().keyPressEvent(event)

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

    def getMultiSelectDirection(self):
        return self.delegateWidget().orientation()

    """ type """
    def setDelegateType(self, value, dynamic_widget=None, dynamic_function=None):
        """
        Sets the type of this widget.  This will reset the entire layout to a blank
        state.

        Args:
            value (TansuModelViewWidget.TYPE): The type of tab menu that this
                widget should be set to
            dynamic_widget (QWidget): The dynamic widget to be displayed.
            dynamic_function (function): The function to be run when a label
                is selected.
        """
        # update layout
        if value == TansuModelViewWidget.STACKED:
            pass
        elif value == TansuModelViewWidget.DYNAMIC:
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

        # splitter
        splitter_style_sheet = """
            QSplitter::handle {{
                border: None;
                color: rgba(255,0,0,255);
            }}
        """

        # create style sheet
        style_sheet_args = iColor.style_sheet_args
        style_sheet_args = AbstractDragDropAbstractView.createAbstractStyleSheet(
            self.headerWidget().view(),
            style_sheet_args,
            header_position=self.headerPosition(),
            outline_width=TansuModelViewWidget.OUTLINE_WIDTH
        )
        style_sheet_args['splitter_style_sheet'] = splitter_style_sheet

        # apply style
        style_sheet = """
        {header_style_sheet}
        {splitter_style_sheet}
        """.format(**style_sheet_args)
        self.setStyleSheet(style_sheet)

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


""" DELEGATE """
class TansuMainDelegateWidget(TansuBaseWidget):
    """
    The main delegate view that will show all of the items widgets that
     the user currently has selected
    """

    def __init__(self, parent=None):
        super(TansuMainDelegateWidget, self).__init__(parent)
        self.rgba_background = iColor["rgba_gray_0"]

    def showEvent(self, event):
        tab_tansu_widget = getWidgetAncestor(self, TansuModelViewWidget)
        if tab_tansu_widget:
            tab_tansu_widget.updateDelegateDisplay()

    def keyPressEvent(self, event):
        # preflight | suppress if over header
        is_child_of_header = TansuModelViewWidget.isWidgetUnderCursorChildOfHeader()
        if is_child_of_header:
            tab_tansu_widget = getWidgetAncestor(self, TansuModelViewWidget)

            return tab_tansu_widget.headerWidget().keyPressEvent(event)

        # Tansu functions
        TansuBaseWidget.keyPressEvent(self, event)

        # Global escape
        if event.key() == Qt.Key_Escape:
            tab_tansu_widget = getWidgetAncestor(self, TansuModelViewWidget)
            if tab_tansu_widget:
                tab_tansu_widget.updateDelegateDisplay()
                tab_tansu_widget.toggleDelegateSpacerWidget()

        # TODO TOGGLE DELEGATE KEY
        # This is also maintained under the TansuHeader

        tab_tansu_widget = getWidgetAncestor(self, TansuModelViewWidget)
        if event.key() in tab_tansu_widget.TOGGLE_DELEGATE_KEYS:
            header_widget = tab_tansu_widget.headerWidget()
            if not header_widget.delegateWidgetAlwaysOn():
                header_widget.toggleDelegateWidget()


class TansuModelDelegateWidget(AbstractFrameGroupInputWidget):

    """
    Attributes:
        main_widget (QWidget): the main display widget
        item (TansuModelItem): The item from the model that is associated with
            this delegate
    """
    def __init__(self, parent=None, title=None):
        super(TansuModelDelegateWidget, self).__init__(parent, title)
        self.setStyleSheet("""
            TansuModelDelegateWidget{{background-color: rgba{background_color}}}
        """.format(
            background_color=iColor["rgba_gray_1"]
        ))

    def setMainWidget(self, widget):
        # remove old main widget if it exists
        if hasattr(self, '_main_widget'):
            self._main_widget.setParent(None)

        self._main_widget = widget
        self.layout().addWidget(self._main_widget)

    def getMainWidget(self):
        return self._main_widget

    def setItem(self, item):
        self._item = item

    def item(self):
        return self._item


""" HEADER """
class TansuHeader(TansuBaseWidget):
    def __init__(self, parent=None):
        super(TansuHeader, self).__init__(parent)

        # default attrs
        self._delegate_always_on = False

        # setup style
        self.handle_width = 0
        self.handle_length = 100
        self.rgba_background = iColor["rgba_gray_1"]
        self._view_position = attrs.SOUTH
        self._view_orientation = Qt.Vertical
        self.setContentsMargins(0, 0, 0, 0)

        # setup view
        view = TansuHeaderListView(self)
        self.setView(view)

        # # TODO setup abstract widget
        # TEMP setup
        abstract_widget = QLabel(":)", parent=self)
        abstract_widget.setMinimumSize(1, 1)
        abstract_widget.hide()
        #self.addWidget(abstract_widget)

        # setup delegate
        self.setDelegate(abstract_widget)

        # scroll bar moving will need to be setup differently...

        # setup style
        self.setIsSoloViewEnabled(False)
        self.not_soloable = True

    def view(self):
        return self._view

    def setView(self, view):
        if hasattr (self, "_view"):
            self._view.setParent(None)

        # setup attr
        self._view = view
        self._view.not_soloable = True
        self.insertWidget(0, self._view)
        #self.setOrientation(self._view_orientation, view_position=self._view_position)

    """ DELEGATE """
    def delegate(self):
        return self._delegate

    def setDelegate(self, delegate):
        if hasattr(self, "_delegate"):
            self._delegate.setParent(None)
        self._delegate = delegate
        self._delegate.not_soloable = True
        self.addWidget(self._delegate)

    def toggleDelegateWidget(self):
        if self.delegate().isVisible():
            self.delegate().hide()
        else:
            self.delegate().show()
            self.delegate().setFocus()

            # todo - set focus on delegate

    def delegateWidgetAlwaysOn(self):
        return self._delegate_always_on

    def setDelegateWidgetAlwaysOn(self, enabled):
        """
        Flag to determine if the delegate should always be on, or toggled via hotkey
        """
        self._delegate_always_on = enabled

        # hide / show widget
        if enabled:
            self.delegate().show()
        else:
            self.delegate().hide()

    """ VIEW INTERFACE """
    def model(self):
        return self.view().model()

    def setModel(self, model):
        self.view().setModel(model)

    def setOrientation(self, view_orientation, view_position=None):
        """
        Set the orientation/direction of the header, and view.

        This will determine the flow of the items, from LeftToRight,
        or TopToBottom, depending on the orientation.

        Args:
            view_orientation (Qt.Orientation): The orientation that the view will
                be displayed in.  Note that this is NOT this Tansu widgets
                base orientation
                    Qt.Horizonal | Qt.Vertical
            view_position (attrs.DIRECTION):  When provided, will rearrange the
                additional data to be set in that direction...  This is the default
                orientation/position of this widget
                    ie attrs.NORTH, will place the header view on top, and the
                        extra view on the bottom

        """
        # set view orientation
        try:
            self.view().setOrientation(view_orientation)
        except AttributeError:
            # initializing
            pass

        # set header/abstract widget orientation/positions
        if view_position:
            self.view().setParent(None)
            if view_position == attrs.NORTH:
                self.insertWidget(1, self.view())
                _orientation = Qt.Vertical
            elif view_position == attrs.SOUTH:
                _orientation = Qt.Vertical
                self.insertWidget(0, self.view())
            elif view_position == attrs.EAST:
                _orientation = Qt.Horizontal
                self.insertWidget(1, self.view())
            elif view_position == attrs.WEST:
                _orientation = Qt.Horizontal
                self.insertWidget(0, self.view())
        else:
            _orientation = view_orientation
        self._view_position = view_position
        self._view_orientation = view_orientation
        return TansuBaseWidget.setOrientation(self, _orientation)

    def selectionModel(self):
        return self.view().selectionModel()

    def setMultiSelect(self, enabled):
        self.view().setMultiSelect(enabled)

    def setDragDropMode(self, drag_drop_mode):
        """
        Sets the drag/drop mode of the header.

        Args:
            drag_drop_mode (QAbstractItemModel.MODE): drag drop mode
                to be implemented on the header
        """
        self.view().setDragDropMode(drag_drop_mode)

    def setIsDragEnabled(self, enabled):
        self.view().setIsDragEnabled(enabled)

    def setIsDropEnabled(self, enabled):
        self.view().setIsDropEnabled(enabled)

    def setIsRootDropEnabled(self, enabled):
        self.view().setIsRootDropEnabled(enabled)

    def setIsEditable(self, enabled):
        self.view().setIsEditable(enabled)

    def setIsSelectable(self, enabled):
        self.view().setIsSelectable(enabled)

    def setIsEnableable(self, enabled):
        self.view().setIsEnableable(enabled)

    def setIsDeleteEnabled(self, enabled):
        self.view().setIsDeleteEnabled(enabled)

    """ EVENTS """
    def keyPressEvent(self, event):
        """
        Note duplicate to view...

         must it be duplicate?
        :param event:
        :return:
        """
        # TODO TOGGLE DELEGATE KEY
        # this is also maintained under... TansuMainDelegateWidget
        tab_tansu_widget = getWidgetAncestor(self, TansuModelViewWidget)
        if event.key() in tab_tansu_widget.TOGGLE_DELEGATE_KEYS:
            if not self.delegateWidgetAlwaysOn():
                self.toggleDelegateWidget()


class TansuHeaderAbstractView(object):
    def __init__(self, parent=None):
        super(TansuHeaderAbstractView, self).__init__()
        self.not_soloable = True

    def showEvent(self, event):
        tab_tansu_widget = getWidgetAncestor(self, TansuModelViewWidget)
        if tab_tansu_widget:
            tab_tansu_widget.updateDelegateDisplay()
        QAbstractItemView.showEvent(self, event)

    def selectionChanged(self, selected, deselected):
        top_level_widget = getWidgetAncestor(self, TansuModelViewWidget)
        if top_level_widget:
            # for index in selected.indexes():
            #     if index.column() == 0:
            #         print(index.internalPointer().columnData()['name'])
            top_level_widget.updateDelegateDisplayFromSelection(selected, deselected)

    def dropEvent(self, event):
        # resolve drop event
        return_val = super(self.__class__, self).dropEvent(event)

        # get main widget
        main_widget = getWidgetAncestor(self, TansuModelViewWidget)

        # clear selection
        main_widget.delegateWidget().displayAllWidgets(False)
        self.selectionModel().clearSelection()

        return return_val


class TansuHeaderListView(AbstractDragDropListView, TansuHeaderAbstractView):
    def __init__(self, parent=None):
        super(TansuHeaderListView, self).__init__(parent)
        self.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.tansu_header = parent

    # TODO Copy paste to TansuHeaderTreeView
    # probably due to self.tansu_header not working on init?
    def keyPressEvent(self, event):
        # TODO TOGGLE DELEGATE KEY
        # tansu hotkeys esc/~
        tab_tansu_widget = getWidgetAncestor(self, TansuModelViewWidget)
        if event.key() in tab_tansu_widget.TOGGLE_DELEGATE_KEYS:
            header_widget = tab_tansu_widget.headerWidget()
            if not header_widget.delegateWidgetAlwaysOn():
                header_widget.toggleDelegateWidget()

        return AbstractDragDropListView.keyPressEvent(self, event)


class TansuHeaderTreeView(AbstractDragDropTreeView, TansuHeaderAbstractView):
    def __init__(self, parent=None):
        super(TansuHeaderTreeView, self).__init__(parent)

        self.tansu_header = parent

    # TODO Copy paste to TansuHeaderListView
    # probably due to self.tansu_header not working on init?
    def keyPressEvent(self, event):
        # TODO TOGGLE DELEGATE KEY
        # tansu hotkeys esc/~
        tab_tansu_widget = getWidgetAncestor(self, TansuModelViewWidget)
        if event.key() in tab_tansu_widget.TOGGLE_DELEGATE_KEYS:
            header_widget = tab_tansu_widget.headerWidget()
            if not header_widget.delegateWidgetAlwaysOn():
                header_widget.toggleDelegateWidget()

        return AbstractDragDropTreeView.keyPressEvent(self, event)

    # def dropEvent(self, event):
    #     # resolve drop event
    #     return_val = super(TansuHeaderTreeView, self).dropEvent(event)
    #
    #     # get main widget
    #     main_widget = getWidgetAncestor(self, TansuModelViewWidget)
    #
    #     # clear selection
    #     main_widget.delegateWidget().displayAllWidgets(False)
    #     main_widget.delegateWidget().clear()
    #     self.selectionModel().clearSelection()
    #
    #     return return_val


""" EXAMPLE """
class TabTansuDynamicWidgetExample(QWidget):
    """
    TODO:
        turn this into an interface for creating dynamic tab widgets
    """
    def __init__(self, parent=None):
        super(TabTansuDynamicWidgetExample, self).__init__(parent)
        QVBoxLayout(self)
        self.label = QLabel('init')
        self.layout().addWidget(self.label)

    @staticmethod
    def updateGUI(parent, widget, item):
        """
        widget (TansuModelDelegateWidget)
        item (TansuModelItem)
        """
        if item:
            widget.setTitle(item.name())
            widget.getMainWidget().label.setText(item.name())


"""
TODO popup search delegate...
Need:
    QlineEdit
        --> Finished editing signal exposed
        --> Signal needs to receive
                    TansuHeaderView
                    MainTansu?

Search items
    Hotkey --> Popup LineEdit (s)
Create New Item
    Hotkey --> Popup LineEdit (c)

"""

if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication, QLabel, QVBoxLayout
    from qtpy.QtGui import QCursor
    app = QApplication(sys.argv)
    # w = TansuHeader()
    # w.show()


    class test(TansuBaseWidget):
        def __init__(self, parent=None):
            super(test, self).__init__(parent)
            self.addWidget(QLabel('a'))
            self.addWidget(QLabel('b'))
            self.addWidget(QLabel('c'))

    w = TansuModelViewWidget()
    #w.setHeaderPosition(attrs.WEST, attrs.SOUTH)
    #header_delegate_widget = QLabel("Custom")
    w.setHeaderDelegateAlwaysOn(False)
    #
    # w.setMultiSelect(True)
    # w.setMultiSelectDirection(Qt.Vertical)
    # w.setHeaderItemDragDropMode(QAbstractItemView.InternalMove)


    dw = TabTansuDynamicWidgetExample

    for x in range(3):
        widget = QLabel(str(x))
        parent_item = w.insertTansuWidget(x, column_data={'name':str(x), 'one':'test'}, widget=widget)

    for y in range(0, 2):
        w.insertTansuWidget(y, column_data={'name':str(y)}, widget=widget, parent=parent_item)

    w.resize(500, 500)
    w.delegateWidget().handle_length = 100
    print(w.headerWidget().view())
    w.show()
    # #w.headerWidget().model().setIsDragEnabled(False)
    # w.setHeaderItemIsDropEnabled(True)
    # w.setHeaderItemIsDragEnabled(True)
    # w.setHeaderItemIsEnableable(True)
    # w.setHeaderItemIsDeleteEnabled(False)
    w.move(QCursor.pos())
    sys.exit(app.exec_())

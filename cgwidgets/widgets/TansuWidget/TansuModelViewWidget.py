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
            |-- DelegateWidget (TansuMainDelegateWidget --> TansuView)
                    | -- _temp_proxy_widget (QWidget)
                    | -* TansuModelDelegateWidget (AbstractGroupBox)
                            | -- Stacked/Dynamic Widget (main_widget)
"""

from qtpy.QtWidgets import (
    QWidget, QAbstractItemView, QScrollArea, QSplitter, qApp)
from qtpy.QtCore import Qt, QModelIndex, QEvent
from qtpy.QtGui import QCursor

from cgwidgets.utils import getWidgetAncestor, attrs
from cgwidgets.settings.colors import iColor
from cgwidgets.widgets import AbstractFrameGroupInputWidget, ModelViewWidget
from cgwidgets.views import TansuView

from cgwidgets.widgets.TansuWidget import (TansuModel, iTansuDynamicWidget)
from cgwidgets.views import (AbstractDragDropAbstractView)


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
    """
    OUTLINE_WIDTH = 1
    STACKED = 'stacked'
    DYNAMIC = 'dynamic'
    MULTI = False
    TYPE = STACKED
    def __init__(self, parent=None, direction=attrs.NORTH):
        super(TansuModelViewWidget, self).__init__(parent)
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
        self._model = TansuModel()
        self._header_widget = TansuHeader(self)
        self._header_widget.setModel(self._model)
        self._header_widget.setItemSelectedEvent(self._header_widget.selectionChanged)

        # setup delegate
        delegate_widget = TansuMainDelegateWidget()
        self.setDelegateWidget(delegate_widget)
        self._temp_proxy_widget = QWidget()
        self._temp_proxy_widget.setObjectName("proxy_widget")

        self.delegateWidget().insertWidget(0, self._temp_proxy_widget)

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

        new_index = self.model().insertNewIndex(row, parent=parent)
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

            # todo key event...
            widget.installEventFilter(self)

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
        self._header_widget.setModel(model)
        self._header_widget.setItemSelectedEvent(self._header_widget.selectionChanged)

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
        #self._header_widget.setItemSelectedEvent(self._header_widget.selectionChanged)

    def headerViewWidget(self):
        return self.headerWidget().view()

    def setHeaderViewWidget(self, _header_view_widget):
        """
        Sets the header widget to be a custom widget type
        Args:
            _header_view_widget (QWidget):

        Returns:

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
        header_view = self.headerWidget().setViewType(view_type)
        self.setHeaderViewWidget(header_view)
        #self.setHeaderWidget(header_widget)
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
        display_widget.setIsHeaderShown(self.delegateTitleIsShown())
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

    def updateDelegateItem(self, item, selected, column=0):
        """
        item (TansuModelItem)
        selected (bool): determines if this item has been selected
            or un selected.
        """
        # update static widgets
        # todo column registry.
        ## note that this is set so that it will not run for each column
        if column == 0:
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
            item.delegateWidget().setIsHeaderShown(self.delegateTitleIsShown())
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
            # todo dynamic key event
            #dynamic_widget.installEventFilter(self)
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
        """
        Determines if the widget under the cursor is a child of the header.

        This is to determine where key press events happen and to send that signal
        to the correct side of the widget.
        Returns:

        """
        pos = QCursor.pos()
        widget_pressed = qApp.widgetAt(pos)
        is_child_of_header = None
        if widget_pressed:
            is_child_of_header = getWidgetAncestor(widget_pressed, TansuHeader)
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
class TansuMainDelegateWidget(TansuView):
    """
    The main delegate view that will show all of the items widgets that
     the user currently has selected
    """

    def __init__(self, parent=None):
        super(TansuMainDelegateWidget, self).__init__(parent)
        self.rgba_background = iColor["rgba_background_00"]
        self.setToggleSoloViewEvent(self.resetTansuViewDisplay)

    def resetTansuViewDisplay(self, enabled, widget):
        """

        Args:
            enabled:
            widget:

        Returns:

        """
        if not enabled:
            tab_tansu_widget = getWidgetAncestor(self, TansuModelViewWidget)
            if tab_tansu_widget:
                tab_tansu_widget.updateDelegateDisplay()
                tab_tansu_widget.toggleDelegateSpacerWidget()

    def showEvent(self, event):
        tab_tansu_widget = getWidgetAncestor(self, TansuModelViewWidget)
        if tab_tansu_widget:
            tab_tansu_widget.updateDelegateDisplay()

    def keyPressEvent(self, event):
        # preflight | suppress if over header
        is_child_of_header = TansuModelViewWidget.isWidgetUnderCursorChildOfHeader()
        tab_tansu_widget = getWidgetAncestor(self, TansuModelViewWidget)
        if is_child_of_header:
            return tab_tansu_widget.headerWidget().keyPressEvent(event)
        else:
            return TansuView.keyPressEvent(self, event)
        # ModelViewWidget.keyPressEvent(tab_tansu_widget.headerWidget(), event)

        # Global escape
        # if event.key() == Qt.Key_Escape:
        #     pass
            # tab_tansu_widget = getWidgetAncestor(self, TansuModelViewWidget)
            # if tab_tansu_widget:
            #     tab_tansu_widget.updateDelegateDisplay()
            #     tab_tansu_widget.toggleDelegateSpacerWidget()
        # Global override for conflicts
        # if event.key() == self.soloViewHotkey():
        #     """
        #     If this is another tansu/labelled input etc, it will bypass
        #     and use that widgets key press.  If it is over the main delegate,
        #     it will register a TansuView press.
        #     """
        #     pos = QCursor.pos()
        #     widget_pressed = qApp.widgetAt(pos)
        #
        #     if isinstance(widget_pressed, TansuModelDelegateWidget):
        #         return TansuView.keyPressEvent(self, event)
        # else:
        #     return TansuView.keyPressEvent(self, event)


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
            background_color=iColor["rgba_gray_3"]
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
class TansuHeader(ModelViewWidget):
    LIST_VIEW = 0
    TREE_VIEW = 1
    def __init__(self, parent=None):
        super(TansuHeader, self).__init__(parent)
        self.setViewType(ModelViewWidget.LIST_VIEW)

    def showEvent(self, event):
        tab_tansu_widget = getWidgetAncestor(self, TansuModelViewWidget)
        if tab_tansu_widget:
            tab_tansu_widget.updateDelegateDisplay()
        ModelViewWidget.showEvent(self, event)

    def dropEvent(self, event):
        # resolve drop event
        return_val = super(self.__class__, self).dropEvent(event)

        # get main widget
        main_widget = getWidgetAncestor(self, TansuModelViewWidget)

        # clear selection
        main_widget.delegateWidget().displayAllWidgets(False)
        self.selectionModel().clearSelection()

        return return_val

    def selectionChanged(self, item, enabled, column=0):
        """
        Determines whether or not an items delegateWidget() should be
        displayed/updated/destroyed.
        """

        # todo for some reason this double registers the selection even

        # when using dynamic tree widgets...
        top_level_widget = getWidgetAncestor(self, TansuModelViewWidget)
        top_level_widget.toggleDelegateSpacerWidget()

        # update display
        top_level_widget._selection_item = enabled
        top_level_widget.updateDelegateItem(item, enabled, column)

        # update delegate background
        if hasattr(top_level_widget, '_delegate_widget'):
            selection = top_level_widget.headerWidget().selectionModel().selectedIndexes()
            if len(selection) == 0:
                top_level_widget.delegateWidget().rgba_background = iColor['rgba_background_00']
            else:
                top_level_widget.delegateWidget().rgba_background = iColor['rgba_background_01']

        # custom input event | need this as we're overriding the models input
        top_level_widget.itemSelectedEvent(item, enabled, column)
        #return ModelViewWidget.selectionChanged(self, selected, deselected)


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


# def toggleDelegateEvent(self, event, enabled):
#     self.__toggleDelegateEvent(event, enabled)
#     pass
if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication, QLabel, QVBoxLayout
    from qtpy.QtGui import QCursor
    app = QApplication(sys.argv)
    # w = TansuHeader()
    # w.show()


    class test(ModelViewWidget):
        def __init__(self, parent=None):
            super(test, self).__init__(parent)
            self.addWidget(QLabel('a'))
            self.addWidget(QLabel('b'))
            self.addWidget(QLabel('c'))

    w = TansuModelViewWidget()
    #w.setHeaderPosition(attrs.WEST, attrs.SOUTH)
    #header_delegate_widget = QLabel("Custom")
    #w.setHeaderDelegateAlwaysOn(False)
    #
    # w.setMultiSelect(True)
    # w.setMultiSelectDirection(Qt.Vertical)
    # w.setHeaderItemDragDropMode(QAbstractItemView.InternalMove)
    delegate_widget = QLabel("Q")
    w.addHeaderDelegateWidget([Qt.Key_Q], delegate_widget)

    dw = TabTansuDynamicWidgetExample

    for x in range(3):
        widget = QLabel(str(x))
        parent_item = w.insertTansuWidget(x, column_data={'name':str(x), 'one':'test'}, widget=widget)

    for y in range(0, 2):
        w.insertTansuWidget(y, column_data={'name':str(y)}, widget=widget, parent=parent_item)

    w.resize(500, 500)
    w.delegateWidget().setHandleLength(100)

    w.show()
    # #w.headerWidget().model().setIsDragEnabled(False)
    # w.setHeaderItemIsDropEnabled(True)
    # w.setHeaderItemIsDragEnabled(True)
    # w.setHeaderItemIsEnableable(True)
    # w.setHeaderItemIsDeleteEnabled(False)
    w.move(QCursor.pos())
    sys.exit(app.exec_())

from qtpy.QtWidgets import (
    QWidget, QListView, QAbstractItemView, QScrollArea, QSplitter, QTreeView,
    QProxyStyle
)
from qtpy.QtCore import Qt, QModelIndex, QPoint, QRect
from qtpy.QtGui import QPainter, QColor, QPen, QBrush, QCursor, QPolygonF, QPainterPath

from cgwidgets.utils import getWidgetAncestor, attrs
from cgwidgets.settings.colors import iColor
from cgwidgets.settings.icons import icons

from cgwidgets.widgets import AbstractInputGroup
from cgwidgets.widgets.TansuWidget import (
    TansuBaseWidget, TansuModel, iTansuDynamicWidget
)
from cgwidgets.views import AbstractDragDropModel, AbstractDragDropModelDelegate


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

    Widgets:
        |-- QBoxLayout
                |-- ViewWidget (TansuHeaderListView)
                        ( TansuHeaderListView | TansuHeaderTableView | TansuHeaderTreeView )
                | -- Scroll Area
                    |-- DelegateWidget (TansuMainDelegateWidget --> TansuBaseWidget)
                            | -- _temp_proxy_widget (QWidget)
                            | -* TansuModelDelegateWidget (AbstractGroupBox)
                                    | -- Stacked/Dynamic Widget (main_widget)

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
        self._header_position = direction #just a temp set... for things
        self._header_height = 50
        self._header_width = 100

        # setup model / view
        self._model = TansuModel()
        self._header_widget = TansuHeaderListView(self)
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

    def setHeaderDragDropMode(self, drag_drop_mode):
        """
        Sets the drag/drop mode of the header.

        Args:
            drag_drop_mode (QAbstractItemModel.MODE): drag drop mode
                to be implemented on the header
        """
        self.headerWidget().setDragDropMode(drag_drop_mode)

    def setHeaderDragStartEvent(self, function):
        """
        Sets the function to be run after the drag has been initiated
        """
        self.model().setDragStartEvent(function)

    def setHeaderDropEvent(self, function):
        """
        Sets the function to be run after the drop event has happened.
        This function should take one arg which is a list of items that
        have been dropped
        """
        self.model().setDropEvent(function)

    def setHeaderTextChangedEvent(self, function):
        self.model().setTextChangedEvent(function)

    def setHeaderIsDragEnabled(self, enabled):
        self.headerWidget().setIsDragEnabled(enabled)

    def setHeaderIsDropEnabled(self, enabled):
        self.headerWidget().setIsDropEnabled(enabled)

    def setHeaderIsEditable(self, enabled):
        self.headerWidget().setIsEditable(enabled)

    def setHeaderIsSelectable(self, enabled):
        self.headerWidget().setIsSelectable(enabled)
    # """ DRAG / DROP PROPERTIES """
    # def isSelectable(self):
    #     if self._isSelectable:
    #         return Qt.ItemIsSelectable
    #     else:
    #         return 0
    #
    # def setIsSelectable(self, _isSelectable):
    #     self._isSelectable = _isSelectable
    #     self.model().setIsSelectable(_isSelectable)
    #
    # def isDragDropEnabled(self):
    #     if self._isDragEnabled:
    #         return Qt.ItemIsDragEnabled
    #     else:
    #         return 0
    #
    # def setIsDragDropEnabled(self, _isDragDropEnabled):
    #     self._isDragDropEnabled = _isDragDropEnabled
    #     # self.model().setIsDragEnabled(_isDragDropEnabled)
    #     # self.model().setIsDropEnabled(_isDragDropEnabled)
    #     # print(self.model())
    #     # if _isDragDropEnabled:
    #     #     self.headerWidget().setDragDropOverwriteMode(True)
    #     # else:
    #     #     self.headerWidget().setDragDropOverwriteMode(False)
    #
    # def isRootDropEnabled(self):
    #     return self._root_drop_enabled
    #
    # def setIsRootDropEnabled(self, _root_drop_enabled):
    #     self._root_drop_enabled = _root_drop_enabled
    #
    # def isEditable(self):
    #     if self._isEditable:
    #         return Qt.ItemIsEditable
    #     else:
    #         return 0
    #
    # def setIsEditable(self, _isEditable):
    #     self._isEditable = _isEditable
    #     self.model().setIsEditable(_isEditable)

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

    def headerPosition(self):
        return self._header_position

    def setHeaderPosition(self, _header_position):
        """
        Sets the current direction this widget.  This is the orientation of
        where the tab labels will be vs where the main widget will be, where
        the tab labels bar will always be the first widget.
        """
        self._header_position = _header_position
        self.headerWidget().setParent(None)

        if _header_position == attrs.WEST:
            self.setOrientation(Qt.Horizontal)
            self.headerWidget().setOrientation(Qt.Horizontal)
            self.insertWidget(0, self.headerWidget())
            self.setStretchFactor(0, 0)
            self.setStretchFactor(1, 1)

        elif _header_position == attrs.EAST:
            self.setOrientation(Qt.Horizontal)
            self.headerWidget().setOrientation(Qt.Horizontal)
            self.insertWidget(1, self.headerWidget())
            self.setStretchFactor(1, 0)
            self.setStretchFactor(0, 1)

        elif _header_position == attrs.NORTH:
            self.setOrientation(Qt.Vertical)
            self.headerWidget().setOrientation(Qt.Vertical)
            self.insertWidget(0, self.headerWidget())
            self.setStretchFactor(0, 0)
            self.setStretchFactor(1, 1)

        elif _header_position == attrs.SOUTH:
            self.setOrientation(Qt.Vertical)
            self.headerWidget().setOrientation(Qt.Vertical)
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
        #name = item.data()[self.model()._header_data[0]]
        name = self.model().getItemName(item)
        display_widget = TansuModelDelegateWidget(self, name)
        display_widget.setMainWidget(widget)
        display_widget.setItem(item)

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

        TODO:
            update for dynamic?
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

    def updateDelegateDisplayFromSelection(self, selected, deselected):
        """
        Determines whether or not an items delegateWidget() should be
        displayed/updated/destroyed.

        """
        self.toggleDelegateSpacerWidget()

        # update display
        self._selection_item = selected
        for index in selected.indexes():
            item = index.internalPointer()
            item.setSelected(True)
            self.__updateDelegateItem(item, True)

        for index in deselected.indexes():
            item = index.internalPointer()
            item.setSelected(False)
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
        self.setHeaderWidgetToDefaultSize()
        self.updateStyleSheet()
        return QSplitter.showEvent(self, event)

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

    def keyPressEvent(self, event):
        """
        TODO
            stop this event from happening?
            Only want the child tansu to register... not this one...
        """
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

        # setup args
        style_sheet_args = iColor.style_sheet_args
        style_sheet_args.update({
            'outline_width': TansuModelViewWidget.OUTLINE_WIDTH,
            'type': type(self.headerWidget()).__name__
        })
        style_sheet_args.update(icons)

        # splitter
        splitter_style_sheet = """
            QSplitter::handle {{
                border: None;
                color: rgba(255,0,0,255);
            }}
        """

        # header
        base_header_style_sheet = """
        QHeaderView::section {{
            background-color: rgba{rgba_gray_0};
            color: rgba{rgba_text};
            border: {outline_width}px solid rgba{rgba_outline};
        }}
        {type}{{
            border:None;
            background-color: rgba{rgba_gray_0};
            selection-background-color: rgba{rgba_invisible};
        }}
            """.format(**style_sheet_args)

        # item style snippets ( so it can be combined later...)
        style_sheet_args['item_snippet'] = """
            border: {outline_width}px solid rgba{rgba_outline};
            background-color: rgba{rgba_gray_0};
            color: rgba{rgba_text};
        """.format(**style_sheet_args)
        style_sheet_args['item_selected_snippet'] = """
            border: {outline_width}px solid rgba{rgba_outline};
            background-color: rgba{rgba_gray_1};
            color: rgba{rgba_selected};
        """.format(**style_sheet_args)

        # create style sheet
        header_style_sheet = self.headerWidget().createStyleSheet(self.headerPosition(), style_sheet_args)

        # combine style sheets
        style_sheet_args['splitter_style_sheet'] = splitter_style_sheet
        style_sheet_args['header_style_sheet'] = header_style_sheet
        style_sheet_args['base_header_style_sheet'] = base_header_style_sheet

        style_sheet = """
        {base_header_style_sheet}
        {header_style_sheet}
        {type}::item:hover{{color: rgba{rgba_hover}}}
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
        TansuBaseWidget.keyPressEvent(self, event)
        if event.key() == Qt.Key_Escape:
            tab_tansu_widget = getWidgetAncestor(self, TansuModelViewWidget)
            if tab_tansu_widget:
                tab_tansu_widget.updateDelegateDisplay()
                tab_tansu_widget.toggleDelegateSpacerWidget()


class TansuModelDelegateWidget(AbstractInputGroup):
    """
    This is a clone of the InputGroup... but I'm getting
    stuck in import recursion land... so... this is a copy
    paste.  Sorry. deal with it.
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


class TansuHeaderAbstractView(object):
    def __init__(self):
        # setup style
        self.setStyle(TansuHeaderViewDropIndicatorStyle())
        #print(self.style())
        self.setupCustomDelegate()

        # setup flags
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self._isDropEnabled = True
        self._isDragEnabled = False
        self._isEditable = True
        self._isSelectable = True

    """ ABSTRACT ITEM VIEW STUFFF"""
    def setupCustomDelegate(self):
        delegate = AbstractDragDropModelDelegate(self)
        self.setItemDelegate(delegate)

    def createStyleSheet(self, header_position, style_sheet_args):
        pass

    def getIndexUnderCursor(self):
        """
        Returns the QModelIndex underneath the cursor
        """
        pos = self.mapFromGlobal(QCursor.pos())
        index = self.indexAt(pos)
        return index

    def showEvent(self, event):
        tab_tansu_widget = getWidgetAncestor(self, TansuModelViewWidget)
        if tab_tansu_widget:
            tab_tansu_widget.updateDelegateDisplay()
        QListView.showEvent(self, event)

    def setOrientation(self, orientation):
        """
        This is inverted...
        :param orientation:
        :return:
        """
        if orientation == Qt.Horizontal:
            self.setFlow(QListView.TopToBottom)
            direction = Qt.Vertical
        else:
            self.setFlow(QListView.LeftToRight)
            direction = Qt.Horizontal

        # update drag/drop style
        # todo fix this...
        try:
            if isinstance(self, TansuHeaderListView):
                self.style().setOrientation(direction)
            else:
                self.style().setOrientation(Qt.Vertical)
        except AttributeError:
            # for some reason katana doesnt like this...
            pass

    def setMultiSelect(self, multi_select):
        if multi_select is True:
            self.setSelectionMode(QAbstractItemView.MultiSelection)
        else:
            self.setSelectionMode(QAbstractItemView.SingleSelection)

    def selectionChanged(self, selected, deselected):
        top_level_widget = getWidgetAncestor(self, TansuModelViewWidget)
        if top_level_widget:
            top_level_widget.updateDelegateDisplayFromSelection(selected, deselected)

    """ DRAG / DROP PROPERTIES """
    def setIsSelectable(self, _isSelectable):
        self._isSelectable = _isSelectable
        self.model().setIsSelectable(_isSelectable)

    def setIsDragEnabled(self, _isDragEnabled):
        self._isDragEnabled = _isDragEnabled
        self.model().setIsDragEnabled(_isDragEnabled)

    def setIsDropEnabled(self, _isDropEnabled):
        self._isDropEnabled = _isDropEnabled
        self.model().setIsDropEnabled(_isDropEnabled)

    def setIsEditable(self, _isEditable):
        self._isEditable = _isEditable
        self.model().setIsEditable(_isEditable)


class TansuHeaderViewDropIndicatorStyle(QProxyStyle):
    """
    Drag / drop style.

    Args:
        direction (Qt.DIRECTION): What direction the current flow of
            the widget is
    """
    INDICATOR_WIDTH = 2
    INDICATOR_SIZE = 10

    def __init__(self, parent=None):
        super(TansuHeaderViewDropIndicatorStyle, self).__init__(parent)
        self._orientation = Qt.Vertical

    def orientation(self):
        return self._orientation

    def setOrientation(self, orientation):
        self._orientation = orientation

    def __drawVertical(self, widget, option, painter, size, width):
        # drop between
        y_pos = option.rect.topLeft().y()
        if option.rect.height() == 0:
            # create indicators
            l_indicator = self.createTriangle(size, attrs.EAST)
            l_indicator.translate(QPoint(size + (width / 2), y_pos))

            r_indicator = self.createTriangle(size, attrs.WEST)
            r_indicator.translate(QPoint(
                widget.width() - size - (width / 2), y_pos)
            )

            # draw
            painter.drawPolygon(l_indicator)
            painter.drawPolygon(r_indicator)
            painter.drawLine(
                QPoint(size + (width / 2), y_pos),
                QPoint(widget.width() - size - (width / 2), y_pos)
            )

            # set fill color
            background_color = QColor(*iColor["rgba_gray_1"])
            brush = QBrush(background_color)
            path = QPainterPath()
            path.addPolygon(l_indicator)
            path.addPolygon(r_indicator)
            painter.fillPath(path, brush)

        # drop on
        else:
            indicator_rect = QRect((width / 2), y_pos, widget.width() - (width / 2), option.rect.height())
            painter.drawRoundedRect(indicator_rect, 1, 1)

    def __drawHorizontal(self, widget, option, painter, size, width):
        x_pos = option.rect.topLeft().x()
        if option.rect.width() == 0:
            # create indicators
            top_indicator = self.createTriangle(size, attrs.NORTH)
            top_indicator.translate(QPoint(x_pos, size + (width / 2)))

            bot_indicator = self.createTriangle(size, attrs.SOUTH)
            bot_indicator.translate(QPoint(x_pos, option.rect.height() - size - (width / 2)))

            # draw
            painter.drawPolygon(top_indicator)
            painter.drawPolygon(bot_indicator)
            painter.drawLine(
                QPoint(x_pos, size + (width / 2)),
                QPoint(x_pos, option.rect.height() - size + (width / 2))
            )

            # set fill color
            background_color = QColor(*iColor["rgba_gray_1"])
            brush = QBrush(background_color)
            path = QPainterPath()
            path.addPolygon(top_indicator)
            path.addPolygon(bot_indicator)

            painter.fillPath(path, brush)

        # drop on
        else:
            painter.drawRoundedRect(option.rect, 1, 1)

    def drawPrimitive(self, element, option, painter, widget=None):
        """
        https://www.qtcentre.org/threads/35443-Customize-drop-indicator-in-QTreeView

        Draw a line across the entire row rather than just the column
        we're hovering over.  This may not always work depending on global
        style - for instance I think it won't work on OSX.

        Still draws the original line - not really sure why
            - clearing the painter will clear the entire view
        """
        if element == self.PE_IndicatorItemViewItemDrop:
            # border
            # get attrs
            size = TansuHeaderViewDropIndicatorStyle.INDICATOR_SIZE
            width = TansuHeaderViewDropIndicatorStyle.INDICATOR_WIDTH

            # border color
            border_color = QColor(*iColor["rgba_selected"])
            pen = QPen()
            pen.setWidth(TansuHeaderViewDropIndicatorStyle.INDICATOR_WIDTH)
            pen.setColor(border_color)

            # background
            background_color = QColor(*iColor["rgba_selected"])
            background_color.setAlpha(64)
            brush = QBrush(background_color)

            # set painter
            painter.setPen(pen)
            painter.setBrush(brush)

            if self.orientation() == Qt.Vertical:
                self.__drawVertical(widget, option, painter, size, width)
                # # border
                # # get attrs
                # y_pos = option.rect.topLeft().y()
                # size = TansuHeaderViewDropIndicatorStyle.INDICATOR_SIZE
                # width = TansuHeaderViewDropIndicatorStyle.INDICATOR_WIDTH
                #
                # # border color
                # border_color = QColor(*iColor["rgba_selected"])
                # pen = QPen()
                # pen.setWidth(TansuHeaderViewDropIndicatorStyle.INDICATOR_WIDTH)
                # pen.setColor(border_color)
                #
                # # background
                # background_color = QColor(*iColor["rgba_selected"])
                # background_color.setAlpha(64)
                # brush = QBrush(background_color)
                #
                # # set painter
                # painter.setPen(pen)
                # painter.setBrush(brush)
                #
                # # drop between
                # if option.rect.height() == 0:
                #     # create indicators
                #     l_indicator = self.createTriangle(size, attrs.EAST)
                #     l_indicator.translate(QPoint(size + (width / 2), y_pos))
                #
                #     r_indicator = self.createTriangle(size, attrs.WEST)
                #     r_indicator.translate(QPoint(
                #         widget.width() - size - (width / 2), y_pos)
                #     )
                #
                #     # draw
                #     painter.drawPolygon(l_indicator)
                #     painter.drawPolygon(r_indicator)
                #     painter.drawLine(
                #         QPoint(size + (width / 2), y_pos),
                #         QPoint(widget.width() - size - (width / 2), y_pos)
                #     )
                #
                #     # set fill color
                #     background_color = QColor(*iColor["rgba_gray_1"])
                #     brush = QBrush(background_color)
                #     path = QPainterPath()
                #     path.addPolygon(l_indicator)
                #     path.addPolygon(r_indicator)
                #     painter.fillPath(path, brush)
                #
                # # drop on
                # else:
                #     indicator_rect = QRect((width / 2), y_pos, widget.width() - (width / 2), option.rect.height())
                #     painter.drawRoundedRect(indicator_rect, 1, 1)
            elif self.orientation() == Qt.Horizontal:
                self.__drawHorizontal(widget, option, painter, size, width)
        else:
            super().drawPrimitive(element, option, painter, widget)

    def createTriangle(self, size, direction=attrs.EAST):
        """
        Creates a triangle to be displayed by the painter.

        Args:
            size (int): the size of the triangle to draw
            direction (attrs.DIRECTION): which way the triangle should point
        """
        if direction == attrs.EAST:
            triangle_point_list = [
                [0, 0],
                [-size, size],
                [-size, -size],
                [0, 0]
            ]
        if direction == attrs.WEST:
            triangle_point_list = [
                [0, 0],
                [size, size],
                [size, -size],
                [0, 0]
            ]
        if direction == attrs.NORTH:
            triangle_point_list = [
                [0, 0],
                [size, -size],
                [-size, -size],
                [0, 0]
            ]
        if direction == attrs.SOUTH:
            triangle_point_list = [
                [0, 0],
                [size, size],
                [-size, size],
                [0, 0]
            ]
        triangle = QPolygonF(map(lambda p: QPoint(*p), triangle_point_list))
        return triangle


class TansuHeaderListView(QListView, TansuHeaderAbstractView):
    def __init__(self, parent=None):
        super(TansuHeaderListView, self).__init__(parent)
        self.setEditTriggers(QAbstractItemView.DoubleClicked)

    def createStyleSheet(self, header_position, style_sheet_args):
        """
        Args:
            header_position (attrs.POSITION): the current position of the header
            style_sheet_args (dict): current dictionary of stylesheet args
        Returns (dict): style sheet
        """
        if header_position == attrs.NORTH:
            style_sheet = """
            {type}::item{{
                {item_snippet}
                border-right: None;
                border-top: None;
            }}
            {type}::item:selected{{
                {item_selected_snippet}
                border-right: None;
                border-bottom: None;
            }}
            """.format(**style_sheet_args)
        elif header_position == attrs.SOUTH:
            style_sheet = """
            {type}::item{{
                {item_snippet}
                border-right: None;
                border-bottom: None;
            }}
            {type}::item:selected{{
                {item_selected_snippet}
                border-right: None;
                border-top: None;
            }}
            """.format(**style_sheet_args)
        elif header_position == attrs.EAST:
            style_sheet = """
            {type}::item{{
                {item_snippet}
                border-top: None;
                border-right: None;
            }}
            {type}::item:selected{{
                {item_selected_snippet}
                border-top: None;
                border-left: None;
            }}
            """.format(**style_sheet_args)
        elif header_position == attrs.WEST:
            style_sheet = """
            {type}::item{{
                {item_snippet}
                border-top: None;
                border-left: None;
            }}
            {type}::item:selected{{
                {item_selected_snippet}
                border-top: None;
                border-right: None;
            }}
            """.format(**style_sheet_args)

        return style_sheet


class TansuHeaderTreeView(QTreeView, TansuHeaderAbstractView):
    def __init__(self, parent=None):
        super(TansuHeaderTreeView, self).__init__(parent)

    """ """
    def setHeaderData(self, _header_data):
        """
        Sets the header display data.

        Args:
            header_data (list): of strings that will be displayed as the header
                data.  This will also set the number of columns in the view aswell.
        """
        self.model().setHeaderData(_header_data)

    """ Overload """
    def createStyleSheet(self, header_position, style_sheet_args):
        """
        Args:
            header_position (attrs.POSITION): the current position of the header
            style_sheet_args (dict): current dictionary of stylesheet args
        Returns (dict): style sheet
        """

        style_sheet = """
        QHeaderView::section {{
            background-color: rgba{rgba_gray_0};
            color: rgba{rgba_text};
            border: {outline_width}px solid rgba{rgba_outline};
        }}
        {type}::item{{
            {item_snippet}
        }}
        {type}::item:selected{{
            {item_selected_snippet}
        }}
        {type}::branch:open:has-children {{
            image: url({path_branch_open})
        }}  
        {type}::branch:closed:has-children {{
            image: url({path_branch_closed})
        }}  
            """.format(**style_sheet_args)

        return style_sheet

    def setFlow(self, _):
        pass

    def startDrag(self, event):
        # todo setup drag/drop icon transparency
        # print(event)
        # from qtpy.QtCore import QMimeData
        # from  qtpy.QtGui import QDrag
        # mimeData = QMimeData()
        #
        # drag = QDrag(self)
        # drag.setMimeData(mimeData)
        # drag.setHotSpot(event.pos() - self.rect().topLeft())

        #dropAction = drag.exec_(Qt.MoveAction)
        return QTreeView.startDrag(self, event)
        # OptionList::startDrag(Qt::DropActions
        # supportedActions){
        # if (supportedActions & Qt::CopyAction)
        # {
        #     QList < QListWidgetItem * > m_items = selectedItems();
        # if (m_items.isEmpty())
        #     return;
        # QMimeData * data = mimeData(m_items);
        # QDrag * drag = new
        # QDrag(this);
        # QPixmap
        # pixmap(":/images/MyIcon_icon.png");
        # drag->setPixmap(pixmap);
        # drag->setMimeData(data);
        # drag->setHotSpot(pixmap.rect().center());
        # drag->exec(Qt::CopyAction);
        # }
        # else
        # QListWidget::startDrag(supportedActions);
        #
        # }

    def dropEvent(self, event):
        #print('dropping???')
        return QTreeView.dropEvent(self, event)


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
            #name = self.model().getItemName(item)
            widget.setTitle(item.name())
            widget.getMainWidget().label.setText(item.name())


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication, QLabel, QVBoxLayout
    from qtpy.QtGui import QCursor
    app = QApplication(sys.argv)


    class test(TansuBaseWidget):
        def __init__(self, parent=None):
            super(test, self).__init__(parent)
            self.addWidget(QLabel('a'))
            self.addWidget(QLabel('b'))
            self.addWidget(QLabel('c'))

    w = TansuModelViewWidget()

    #w.setHeaderData(['name', 'two', 'test'])
    view = TansuHeaderTreeView()

    w.setHeaderWidget(view)
    w.setHeaderPosition(attrs.NORTH)
    w.setMultiSelect(True)
    w.setMultiSelectDirection(Qt.Vertical)
    w.setHeaderDragDropMode(QAbstractItemView.InternalMove)
    view.setHeaderData(['name', 'two', 'test'])
    #view.setHeaderData(['one', 'two'])

    #
    # new_view = TansuHeaderListView()
    # print()
    # new_view.show()
    # w.setHeaderWidget(new_view)
    # w.setHeaderPosition(TansuModelViewWidget.NORTH)

    dw = TabTansuDynamicWidgetExample
    #view.setHeaderData(['name', 'one', 'two'])
    # asdf = test(w)
    # main_splitter = TansuBaseWidget()
    # main_splitter.handle_length = 100

    #w.insertTansuWidget(0, 'tansu', widget=main_splitter)
    #w.insertTansuWidget(0, 'subclass', widget=asdf)

    for x in range(3):
        widget = QLabel(str(x))
        parent_item = w.insertTansuWidget(x, column_data={'name':str(x), 'one':'test'}, widget=widget)

    for y in range(0, 2):
        w.insertTansuWidget(y, column_data={'name':str(y)}, widget=widget, parent=parent_item)

    w.resize(500, 500)
    w.delegateWidget().handle_length = 100

    w.show()
    #w.headerWidget().model().setIsDragEnabled(False)
    w.setHeaderIsDropEnabled(True)
    w.setHeaderIsDragEnabled(True)

    w.move(QCursor.pos())
    sys.exit(app.exec_())

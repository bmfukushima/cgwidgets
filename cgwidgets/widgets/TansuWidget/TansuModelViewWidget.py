from qtpy.QtWidgets import (
    QWidget, QListView, QAbstractItemView, QScrollArea, QSplitter)
from qtpy.QtCore import Qt, QModelIndex

from cgwidgets.utils import getWidgetAncestor, attrs
from cgwidgets.settings.colors import iColor
from cgwidgets.widgets import AbstractInputGroup, AbstractFrameGroupInputWidget

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
        self._delegate_header_shown = True
        self._delegate_header_direction = Qt.Vertical

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

    def setDelegateHeaderShown(self, enabled):
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
            self.headerWidget(),
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


# todo needs to somehow inherit from the FrameGroupInputWidget...
#class TansuModelDelegateWidget(AbstractInputGroup):
class TansuModelDelegateWidget(AbstractFrameGroupInputWidget):

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
    def __init__(self, parent=None):
        super(TansuHeaderAbstractView, self).__init__()

    def showEvent(self, event):
        tab_tansu_widget = getWidgetAncestor(self, TansuModelViewWidget)
        if tab_tansu_widget:
            tab_tansu_widget.updateDelegateDisplay()
        QAbstractItemView.showEvent(self, event)

    def selectionChanged(self, selected, deselected):
        # print('selection changed...')
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


class TansuHeaderTreeView(AbstractDragDropTreeView, TansuHeaderAbstractView):
    def __init__(self, parent=None):
        super(TansuHeaderTreeView, self).__init__(parent)

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
    w.setHeaderItemDragDropMode(QAbstractItemView.InternalMove)
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
    w.setHeaderItemIsDropEnabled(True)
    w.setHeaderItemIsDragEnabled(True)
    w.setHeaderItemIsEnableable(True)
    w.setHeaderItemIsDeleteEnabled(False)
    w.move(QCursor.pos())
    sys.exit(app.exec_())

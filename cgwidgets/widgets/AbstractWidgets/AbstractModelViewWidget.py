import sys
import os

from qtpy.QtWidgets import (QSplitterHandle, QApplication, QLabel, QCompleter, QTreeView, QWidget, QVBoxLayout)
from qtpy.QtCore import Qt, QModelIndex, QItemSelectionModel, QEvent, QSortFilterProxyModel
from qtpy.QtGui import QCursor
from cgwidgets.widgets import AbstractStringInputWidget, AbstractListInputWidget
from cgwidgets.views import (
    AbstractDragDropModel,
    AbstractDragDropTreeView,
    AbstractDragDropListView,
    AbstractDragDropModelItem
)
from cgwidgets.utils import getWidgetAncestor, isWidgetDescendantOfInstance
from cgwidgets.settings import iColor, attrs
from cgwidgets.widgets import AbstractShojiLayout

class AbstractModelViewItem(AbstractDragDropModelItem):
    def __int__(self, parent=None):
        super(AbstractModelViewItem, self).__init__(parent)


class AbstractModelViewWidget(AbstractShojiLayout):
    """
    View widget for the Abstract ModelViewDelegate in this lib

    Args:

    Attributes:
        view
        model
        delegate_manifest (list): when the input/modifier combo is pressed
            the widget will be displayed
            {   "input" : Qt.Key_*,
                "modifier"  :   Qt.Modifier,
                "widget" : QWidget}

    Virtual:
        delegateToggleEvent (event, widget, enabled)
        dragStartEvent (item)
        dropEvent (row_dropped_on, item, parent)
        itemDeleteEvent (item)
        itemEnabledEvent (item, enabled)
        itemSelectedEvent (item, enabled)
        textChangedEvent (item, old_value, new_value)

    Hierarchy:
        AbstractShojiLayout --> QSplitter
            |- view --> (AbstractDragDropListView | AbstractDragDropTreeView) --> QSplitter
                |- model (AbstractDragDropModel)
                    |- (AbstractDragDropModelItems)
            |* delegate --> QWidget

    """
    LIST_VIEW = 0
    TREE_VIEW = 1
    SEARCH_KEY = [Qt.Key_F]
    SEARCH_MODIFIER = Qt.ControlModifier

    def __init__(self, parent=None):
        super(AbstractModelViewWidget, self).__init__(parent)

        # default attrs
        self._delegate_always_on = False
        self._delegate_manifest = []

        # setup style
        self.setHandleWidth(0)
        self._handle_length = 100
        self.rgba_background = iColor["rgba_gray_3"]
        self._view_position = attrs.SOUTH
        self._view_orientation = Qt.Vertical
        self.setContentsMargins(0, 0, 0, 0)

        # setup view
        self.setPresetViewType(AbstractModelViewWidget.LIST_VIEW)

        # setup model
        # model = AbstractDragDropModel()
        # self.setModel(model)

        # set up search bar
        self.search_widget = ModelViewSearchWidget(self)
        self.addDelegate(
            AbstractModelViewWidget.SEARCH_KEY,
            self.search_widget,
            AbstractModelViewWidget.SEARCH_MODIFIER,
            focus=True,
            focus_widget=self.search_widget.search_box
        )

        # setup style
        self.setIsSoloViewEnabled(False)
        self.setIsSoloViewEnabled(True, override_children=False)

        # todo set delegate stretch factor
        # self.setStretchFactor(0, 1)

    """ HEADER """
    def setHeaderData(self, _header_data):
        self.model().setHeaderData(_header_data)

    """ VIEW """
    def view(self):
        return self._view

    def setView(self, view, view_type=None):
        """

        Args:
            view (VIEW): to be set
            view_type (AbstractModelViewWidget.VIEW_TYPE): default preset view type to use
                if this is set.  It will automagically setup drag/drop defaults for
                LIST and TREE views.

        Returns:

        """
        if hasattr(self, "_view"):
            self._view.setParent(None)

        # setup model
        if self.model():
            view.setModel(self.model())
        else:
            model = AbstractDragDropModel()
            view.setModel(model)

        # setup attr
        self._view = view

        # add view
        self.insertWidget(0, self._view, is_soloable=False)

        # setup custom key presses
        if hasattr(view, "setKeyPressEvent"):
            view.setKeyPressEvent(self.keyPressEvent)

        if hasattr(view, "setKeyReleaseEvent"):
            view.setKeyReleaseEvent(self.keyReleaseEvent)
            #view.installEventFilter(self)

        # setup default drop attrs
        if view_type == AbstractModelViewWidget.TREE_VIEW:
            self.setIsDroppable(True)
        if view_type == AbstractModelViewWidget.LIST_VIEW:
            self.setIsDroppable(False)

    def setPresetViewType(self, view_type):
        """
        Sets the view to either a LIST or a TREE view

        Args:
            view_type (AbstractModelViewWidget.VIEW_TYPE): the view type to be used.
                AbstractModelViewWidget.TREE_VIEW | AbstractModelViewWidget.LIST_VIEW

        Returns (QWidget): view
        """
        if view_type in [AbstractModelViewWidget.TREE_VIEW, AbstractModelViewWidget.LIST_VIEW]:
            if view_type == AbstractModelViewWidget.TREE_VIEW:
                view = AbstractDragDropTreeView()

            if view_type == AbstractModelViewWidget.LIST_VIEW:
                view = AbstractDragDropListView()

            self.setView(view, view_type=view_type)

            return view

        print("Illegal view type found use: AbstractModelViewWidget.TREE_VIEW, AbstractModelViewWidget.LIST_VIEW")
        return None

    def addContextMenuSeparator(self, conditions=None):
        """
        Adds a separator into the RMB popup menu.

        Args:
            conditions (dict): a mapping of the items args to be used to display the item.
                If no conditions are found the item will be added to the menu
        """
        self.view().addContextMenuSeparator(conditions)

    def addContextMenuEvent(self, name, event, conditions=None):
        """
        Adds an entry into the RMB popup menu.

        Args:
            name (str): name of function to be displayed
            event (function): takes two args:
                item_under_cursor (item): current item under cursor
                indexes (list): of currently selected QModelIndexes
            conditions (dict): a mapping of the items args to be used to display the item.
                If no conditions are found the item will be added to the menu
        """
        if hasattr(self.view(), 'addContextMenuEvent'):
            self.view().addContextMenuEvent(name, event, conditions)
        else:
            print('view does not have function addContextMenuEvent')

    """ DELETE """
    def setDeleteWarningWidget(self, widget):
        self.view().setDeleteWarningWidget(widget)

    def deleteItem(self, item, event_update=False):
        self.model().deleteItem(item, event_update=event_update)

    """ MODEL """
    def model(self):
        if hasattr(self, "_view"):
            model = self.view().model()
            if isinstance(model, QSortFilterProxyModel):
                return model.sourceModel()
            else:
                return model
        else:
            return None

    def setModel(self, model):
        self.view().setModel(model)

    def insertNewIndex(
        self,
        row,
        name="None",
        column_data=None,
        parent=QModelIndex(),
        is_editable=None,
        is_selectable=None,
        is_enableable=None,
        is_deletable=None,
        is_draggable=None,
        is_droppable=None
    ):
        new_index = self.model().insertNewIndex(
            row,
            name=name,
            column_data=column_data,
            parent=parent,
            is_editable=is_editable,
            is_selectable=is_selectable,
            is_enableable=is_enableable,
            is_deletable=is_deletable,
            is_draggable=is_draggable,
            is_droppable=is_droppable
        )

        return new_index

    def clearModel(self):
        self.model().clearModel()

    def setAddMimeDataFunction(self, function):
        """ During drag/drop of a header item.  This will add additional mimedata

        Args:
            function (func): to add mimedata to the drag events
                mimedata (QMimedata):
                indexes (list): of QModelIndexes that are currently selected

        Returns (QMimedata) """
        self.model().setAddMimeDataFunction(function)

    def selectionModel(self):
        return self.view().selectionModel()

    """ MODEL FILTERS"""
    def isModelCustomFilterable(self):
        self.view().isModelCustomFilterable()

    def makeModelFilterable(self):
        self.view().makeModelFilterable()

    def addFilter(self, regex_filter, arg="name"):
        self.view().addFilter(regex_filter=regex_filter, arg=arg)

    def clearFilters(self):
        self.view().clearFilters()

    def filters(self):
        self.view().filters()

    def removeFilter(self, regex_filter, arg="name"):
        self.view().removeFilter({"filter": regex_filter, "arg": arg})

    def removeFilterByIndex(self, index):
        self.view().removeFilterByIndex(index)

    def removeFilterByName(self, name):
        self.view().removeFilterByName(name)

    def updateFilterByName(self, pattern, name):
        """ Updates the given filter with the regex provided

        Args:
            pattern (str): regex pattern to be updated
            name (str): name of filter to update
        """
        self.view().updateFilterByName(pattern, name)

    """ SELECTION """
    def clearItemSelection(self):
        self.view().clearItemSelection()

    def findItems(self, value, index=None, role=Qt.DisplayRole, match_type=Qt.MatchExactly):
        """
        Finds all of the indexes of the value provided that are descendents of the index provided.
        If no index is provided, the default index will be the root.

        Args:
            value (string): to search for
            index (QModelIndex): to search from
            role (Qt.DisplayRole): to search data of
            match_type (Qt.MatchFlags): Flags to match with...
                Qt.MatchExactly | Qt.MatchStartsWith
                https://doc.qt.io/archives/qtjambi-4.5.2_01/com/trolltech/qt/core/Qt.MatchFlag.html
        Returns (list): of QModelIndex

        """
        return self.model().findItems(value, index=index, role=role, match_type=match_type)

    def getAllBaseItems(self, items=None):
        """ Takes a list of items, and returns only the top most item of each branch

        Args:
            items (list): of AbstractDragDropModelItem

        Returns (list): of AbstractDragDropModelItem

        """
        return self.view().getAllBaseItems(items)

    def getAllIndexes(self):
        return self.model().getAllIndexes()

    def getAllSelectedItems(self):
        return self.view().getAllSelectedItems()

    def getAllSelectedIndexes(self):
        return self.view().getAllSelectedIndexes()

    def getItemsDescendants(self, item, descendants=None):
        """ Gets all of the descendants from the item provided

        Returns (list): of AbstractDragDropModelItem"""
        return self.view().getItemsDescendants(item, descendants)

    def getItemsSelectedDescendants(self, item, descendants=None):
        """ Gets all of the selected descendants from the item provided

        Returns (list): of AbstractDragDropModelItem"""
        return self.view().getItemsSelectedDescendants(item, descendants)

    def getIndexFromItem(self, item):
        return self.model().getIndexFromItem(item)

    def rootItem(self):
        return self.model().rootItem()

    def setIndexSelected(self, index, selected):
        self.view().setIndexSelected(index, selected)

    def setItemSelected(self, item, selected):
        """ Selects the item provided
        Args:
            item (QModelIndex):
            selected (bool):

        Returns (True)"""
        return self.view().setItemSelected(item, selected)

    """ DELEGATE """
    def delegateInputManifest(self):
        """
        Args:
            manifest (list): of dict
                {   "input" : Qt.Key_*,
                    "modifier"  :   Qt.Modifier,
                    "widget" : QWidget}
                when the input/modifier combo is pressed, the widget will be displayed

        Returns:

        """
        return self._delegate_manifest

    def setDelegateInputManifest(self, manifest={}):
        self._delegate_manifest = manifest

    def addDelegate(self, input, widget, modifier=Qt.NoModifier, focus=False, focus_widget=None, always_on=False):
        """
        Adds a new delegate that can be activated with the input/modifer combo provided

        Args:
            input (list): of Qt.KEY
            widget (QWidget):
            modifier (Qt.MODIFIER):
            focus (bool): determines if the widget should be focus when it is shown or not
            always_on (bool): determines if this widget is always visible or not

        Returns:
        """
        # add to manifest
        delegate_manifest = {}
        delegate_manifest["input"] = input
        delegate_manifest["widget"] = widget
        delegate_manifest["modifier"] = modifier
        delegate_manifest["focus"] = focus
        delegate_manifest["focus_widget"] = focus_widget
        delegate_manifest["always_on"] = always_on

        self._delegate_manifest.append(delegate_manifest)

        # todo set delegate stretch factor
        # self.setStretchFactor(len(self._delegate_manifest), 0)
        # add widget
        self.addWidget(widget)
        if focus_widget:
            focus_widget.installEventFilter(self)
        if not always_on:
            widget.hide()

    def delegateWidgets(self):
        delegate_widgets = []
        for item in self.delegateInputManifest():
            delegate_widgets.append(item["widget"])
        return delegate_widgets

    def toggleDelegateWidget(self, event, widget):
        """
        Hides/Shows the widget provided

        Args:
            event (QEvent.KeyPress:
            widget (QWidget): widget to be hidden/shown

        Returns:

        """
        # toggle visibility
        if widget.isVisible():
            enabled = False
            widget.hide()
            self.setFocus()
        else:
            enabled = True
            widget.show()
            widget.setFocus()

        # run virtual function
        self.delegateToggleEvent(enabled, event, widget)

    """ DELEGATE VIRTUAL """
    def __delegateToggleEvent(self, enabled, event, widget):
        return

    def delegateToggleEvent(self, enabled, event, widget):
        self.__delegateToggleEvent(enabled, event, widget)
        pass

    def setCopyEvent(self, function):
        self.view().setCopyEvent(function)

    def setCutEvent(self, function):
        self.view().setCutEvent(function)

    def setDuplicateEvent(self, function):
        self.view().setDuplicateEvent(function)

    def setPasteEvent(self, function):
        self.view().setPasteEvent(function)

    def setDelegateToggleEvent(self, function):
        self.__delegateToggleEvent = function

        """ VIRTUAL FUNCTIONS """

    def setItemDeleteEvent(self, function, update_first=True):
        self.model().setItemDeleteEvent(function, update_first=update_first)

    def setDragStartEvent(self, function):
        self.model().setDragStartEvent(function)

    def setDropEvent(self, function):
        self.model().setDropEvent(function)

    def setItemEnabledEvent(self, function):
        self.model().setItemEnabledEvent(function)

    def setTextChangedEvent(self, function):
        self.model().setTextChangedEvent(function)

    def setIndexSelectedEvent(self, function):
        self.model().setItemSelectedEvent(function)

    """ FLAGS """
    def setOrientation(self, view_orientation, view_position=None):
        """
        Set the orientation/direction of the header, and view.

        This will determine the flow of the items, from LeftToRight,
        or TopToBottom, depending on the orientation.

        Args:
            view_orientation (Qt.Orientation): The orientation that the view will
                be displayed in.  Note that this is NOT this Shoji widgets
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
        return AbstractShojiLayout.setOrientation(self, _orientation)

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

    def isCopyable(self):
        return self.view().isCopyable()

    def setIsCopyable(self, enabled):
        self.view().setIsCopyable(enabled)

    def isDraggable(self):
        return self.view().isDraggable()

    def setIsDraggable(self, enabled):
        self.view().setIsDraggable(enabled)

    def isDroppable(self):
        return self.view().isDroppable()

    def setIsDroppable(self, enabled):
        self.view().setIsDroppable(enabled)

    def isRootDroppable(self):
        return self.view().isRootDroppable()

    def setIsRootDroppable(self, enabled):
        self.view().setIsRootDroppable(enabled)

    def isEditable(self):
        return self.view().isEditable()

    def setIsEditable(self, enabled):
        self.view().setIsEditable(enabled)

    def isSelectable(self):
        return self.view().isSelectable()

    def setIsSelectable(self, enabled):
        self.view().setIsSelectable(enabled)

    def isEnableable(self):
        return self.view().isEnableable()

    def setIsEnableable(self, enabled):
        self.view().setIsEnableable(enabled)

    def isDeletable(self):
        return self.view().isDeletable()

    def setIsDeletable(self, enabled):
        self.view().setIsDeletable(enabled)

    """ EXPORT DATA """
    def setItemExportDataFunction(self, func):
        self.model().setItemExportDataFunction(func)

    def exportModelToDict(self, item, item_data=None):
        return self.model().exportModelToDict(item, item_data=item_data)

    """ EVENTS """
    def eventFilter(self, obj, event):
        """ Event filter for handling the hide/show events for the delegate widgets"""
        if event.type() == QEvent.KeyPress:
            from cgwidgets.utils import isWidgetDescendantOf, isWidgetDescendantOf2, getWidgetUnderCursor
            widget_under_cursor = getWidgetUnderCursor()

            if not widget_under_cursor: return
            if (isWidgetDescendantOf2(widget_under_cursor, widget_under_cursor.parent(), self.delegateWidgets())
                or isWidgetDescendantOf2(obj, obj.parent(), self.delegateWidgets())
            ):
                delegate_data = None

                # get item data
                for item in self.delegateInputManifest():
                    if isWidgetDescendantOf(obj, obj.parent(), item["widget"]):
                        delegate_data = item
                        break

                # check hotkey press
                if delegate_data:
                    if event.modifiers() == delegate_data["modifier"]:
                        if event.key() in delegate_data["input"]:
                            if not AbstractShojiLayout.isSoloViewEventActive():
                                AbstractShojiLayout.setIsSoloViewEventActive(True)
                                self.toggleDelegateWidget(event, delegate_data["widget"])
                                return True

                # check escape pressed
                if event.key() == Qt.Key_Escape:
                    if not delegate_data["always_on"]:
                        delegate_data["widget"].hide()
                        self.delegateToggleEvent(False, event, obj)
                        self.setFocus()
                        # return False

        if event.type() == QEvent.KeyRelease:
            AbstractShojiLayout.setIsSoloViewEventActive(False)

        return AbstractShojiLayout.eventFilter(self, obj, event)

    def enterEvent(self, event):
        self.setFocus()
        return AbstractShojiLayout.enterEvent(self, event)

    def keyPressEvent(self, event):
        """
        # TODO TOGGLE DELEGATE KEY
        # this is also maintained under... ShojiMainDelegateWidget
        """
        from cgwidgets.widgets import AbstractShojiLayout

        # get attrs
        modifiers = QApplication.keyboardModifiers()
        input_manifest = self.delegateInputManifest()
        # if event.key() in [Qt.Key_D, Qt.Key_Backspace, Qt.Key_Delete]:
        #     return self.view().keyPressEvent(event)

        # check manifest for key/modifier combo
        ## if found, show/hide widget
        for delegate_manifest in input_manifest:
            input_keys = delegate_manifest["input"]
            input_modifier = delegate_manifest["modifier"]
            if modifiers == input_modifier:
                if event.key() in input_keys:
                    if not AbstractShojiLayout.isSoloViewEventActive():
                        widget = delegate_manifest["widget"]
                        self.toggleDelegateWidget(event, widget)

                        # set focus
                        if delegate_manifest["focus"]:
                            if widget.isVisible():
                                # focus widget provided
                                if delegate_manifest["focus_widget"]:
                                    delegate_manifest["focus_widget"].setFocus()
                                # focus delegate
                                else:
                                    widget.setFocus()
                            else:
                                self.setFocus()
                        else:
                            # focus model
                            self.setFocus()

                        AbstractShojiLayout.setIsSoloViewEventActive(True)

        # full screen
        """ Need to override the ShojiLayout handler here as it goes a bit wonky """
        if event.key() in AbstractShojiLayout.SOLO_VIEW_HOTKEY + AbstractShojiLayout.UNSOLO_VIEW_HOTKEY:
            if self.parent():
                shoji_layout = isWidgetDescendantOfInstance(self.parent(), self.parent().parent(), AbstractShojiLayout)
                if shoji_layout:
                    shoji_layout.keyPressEvent(event)

    def keyReleaseEvent(self, event):
        from cgwidgets.widgets import AbstractShojiLayout
        AbstractShojiLayout.setIsSoloViewEventActive(False)


class ModelViewSearchWidget(AbstractShojiLayout):
    """
    Input widget containing the controls to search for specific items in the model.

    This widget can be shown by hitting the CTRL+F combo'

    Hierarchy:
        ModelViewSearchWidget --> AbstractShojiLayout
            |- ModelViewSearchBox --> AbstractStringInputWidget
            |- search_options --> AbstractShojiLayout
                    |- select_flags --> (ModelViewSelectFlags --> AbstractListInputWidget)
                    |- match_flags --> (ModelViewSelectFlags --> AbstractListInputWidget)
    """
    def __init__(self, parent=None):
        super(ModelViewSearchWidget, self).__init__(parent)
        # create widgets

        # search area

        # create search box
        self.search_box = ModelViewSearchBox(self)

        # setup flag
        self.flags_layout = AbstractShojiLayout(self, orientation=Qt.Horizontal)
        self.select_flags = ModelViewSelectFlags(self)
        self.match_flags = ModelViewMatchFlags(self)

        self.flags_layout.addWidget(self.select_flags)
        self.flags_layout.addWidget(self.match_flags)

        # add main widgets
        self.addWidget(self.search_box)
        self.addWidget(self.flags_layout)

        # setup style
        self.setOrientation(Qt.Vertical)
        self.setIsHandleVisible(False)


class ModelViewSearchBox(AbstractStringInputWidget):
    def __init__(self, parent=None):
        super(ModelViewSearchBox, self).__init__(parent)
        #self.textChanged.connect(self.filterCompletionResults)
        completer = QCompleter()
        self.setCompleter(completer)

    """ COMPLETER """
    def selectIndexes(self, indexes):
        """
        Selects all of the indexes provided

        Args:
            indexes (list): of QModelIndexes

        Returns:

        """
        # get view
        model_view_widget = getWidgetAncestor(self, AbstractModelViewWidget)
        view = model_view_widget.view()

        # clear view
        view.clearItemSelection()

        # select / expand
        for index in indexes:
            view.setIndexSelected(index, True)
            view.expandToIndex(index)

    def keyPressEvent(self, event):
        from cgwidgets.settings.keylist import ACCEPT_KEYS

        if event.key() in ACCEPT_KEYS:
            text = self.text()
            model_view_widget = getWidgetAncestor(self, AbstractModelViewWidget)

            match_type = self.parent().match_flags.text()
            try:
                match_type = ModelViewMatchFlags.MATCH[match_type]
            except KeyError:
                match_type = Qt.MatchExactly

            matches = model_view_widget.model().findItems(text, match_type=match_type)

            self.selectIndexes(matches)

        return AbstractStringInputWidget.keyPressEvent(self, event)


class ModelViewSelectFlags(AbstractListInputWidget):
    """
    List input that displays all of the available search options.
    """
    SELECT = [
        "SELECT"
    ]
    def __init__(self, parent=None):
        super(ModelViewSelectFlags, self).__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        _options = [[option] for option in ModelViewSelectFlags.SELECT]
        self.populate(_options)
        self.setText("SELECT")


class ModelViewMatchFlags(AbstractListInputWidget):
    """
    List input that displays all of the available search options.
    """
    MATCH = {
        "REGEX": Qt.MatchRegExp,
        "EXACT": Qt.MatchExactly,
        "CONTAINS": Qt.MatchContains,
        "STARTS WITH": Qt.MatchStartsWith
    }

    def __init__(self, parent=None):
        super(ModelViewMatchFlags, self).__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        _options = [[option] for option in ModelViewMatchFlags.MATCH.keys()]
        self.populate(_options)
        self.setText("EXACT")
        self.filter_results = False


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # create event functions
    #
    def testDelete(item):
        print("DELETING --> -->", item.columnData()['name'])

    def testDrag(items, model):
        print("DRAGGING -->", items)
        print(items)

    def testDrop(data, items, model, row, parent):
        print("DROPPING -->", row, items, parent)

    def testEdit(item, old_value, new_value):
        print("EDITING -->", item, old_value, new_value)
    #
    def testEnable(item, enabled):
        print("ENABLING -->", item.columnData()['name'], enabled)
    #
    def testSelect(item, enabled):
        print("SELECTING -->", item.columnData()['name'], enabled)
    #
    def testDelegateToggle(event, widget, enabled):
        print('toggle joe')

    main_widget = AbstractModelViewWidget()
    main_widget.setIndexSelectedEvent(testSelect)
    # main_widget.setPresetViewType(AbstractModelViewWidget.TREE_VIEW)
    view = QTreeView()
    model = main_widget.model()

    #
    # # insert indexes
    for x in range(0, 4):
        index = main_widget.model().insertNewIndex(x, name=str('node%s'%x))
        for i, char in enumerate('no0'):
            main_widget.model().insertNewIndex(i, name=char*3, parent=index)
    # test filter
    # TODO FILTER TEST
    view.setModel(model)
    #proxy_model.setSourceModel(model)
    #view.setModel(proxy_model)

    # syntax = QRegExp.PatternSyntax(
    #     self.filterSyntaxComboBox.itemData(z
    #         self.filterSyntaxComboBox.currentIndex()))
    # caseSensitivity = (
    #         self.filterCaseSensitivityCheckBox.isChecked()
    #         and Qt.CaseSensitive or Qt.CaseInsensitive)
    # regExp = QRegExp("node0")
    #regExp = QRegExp("a")
    #proxy_model.setFilterRegExp(regExp)
    #main_widget.model().setFilterRegExp(regExp)

    w = QWidget()
    l = QVBoxLayout(w)
    l.addWidget(main_widget)
    l.addWidget(view)

    # # # create delegates
    # delegate_widget = QLabel("F")
    # main_widget.addDelegate([Qt.Key_F], delegate_widget)
    #
    # delegate_widget = QLabel("Q")
    # main_widget.addDelegate([Qt.Key_Q], delegate_widget)
    #
    # #
    # # # set model event
    # main_widget.setDragStartEvent(testDrag)
    # main_widget.setDropEvent(testDrop)
    # main_widget.setTextChangedEvent(testEdit)
    # main_widget.setItemEnabledEvent(testEnable)
    # main_widget.setItemDeleteEvent(testDelete)
    # main_widget.setIndexSelectedEvent(testSelect)
    # main_widget.setDelegateToggleEvent(testDelegateToggle)
    # #
    # # # set flags
    # main_widget.setIsRootDroppable(True)
    # main_widget.setIsEditable(True)
    # main_widget.setIsDraggable(True)
    # #main_widget.setIsDroppable(True)
    # main_widget.setIsEnableable(True)
    # main_widget.setIsDeletable(True)
    #
    # # set selection mode
    # main_widget.setMultiSelect(True)



    w.move(QCursor.pos())

    w.show()




    sys.exit(app.exec_())
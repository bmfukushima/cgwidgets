""" TODO
        *   Context Menu
                - ExpandItem (813)

"""

import copy

from qtpy import API_NAME

from qtpy.QtWidgets import (
    QListView, QAbstractItemView, QTreeView, QApplication,
    QProxyStyle, QStyledItemDelegate, QStyleOptionViewItem, QStyle, QMenu
)
from qtpy.QtCore import Qt, QPoint, QPointF, QRect, QItemSelectionModel, QSortFilterProxyModel, QModelIndex
from qtpy.QtGui import QColor, QPen, QBrush, QCursor, QPolygonF, QPainterPath

from cgwidgets.utils import showWarningDialogue
from cgwidgets.settings import iColor, attrs, icons
from cgwidgets.views import AbstractDragDropModel


""" VIEWS """
class AbstractDragDropAbstractView(object):
    """
    Attributes:
        copied_indexes (list): of QModelIndexes, currently in the internal clipboard
        context_menu_manifest (list): of AbstractContextMenuItem defining context menu events
            has the args "name", "event", "item_type"
    """
    def __init__(self):
        # attrs
        self._copied_items = []
        self._copy_data = []
        self._context_menu_manifest = []
        self._delete_warning_widget = None
        self.setMouseTracking(True)
        self.__pressed = False

        # setup style
        self.style = AbstractDragDropIndicator()
        self.setStyle(self.style)
        self.setupCustomDelegate()

        # setup flags
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self._is_droppable = False
        self._is_draggable = False
        self._is_editable = False
        self._is_enableable = False
        #self._isSelectable = True

        style_sheet_args = iColor.style_sheet_args
        self.createAbstractStyleSheet(style_sheet_args)

        model = AbstractDragDropModel()
        self.setModel(model)

    def createAbstractStyleSheet(self, style_sheet_args, header_position=None, outline_width=1):
        """
        Creates a default style sheet to be used on the view.

        Args:
            style_sheet_args (dict): of color values in the form provided in
                cgwidgets.settings.color.iColor
            header_position (attrs.POSITION): What the current position of the header is.
            outline_width (int): the width of the outline shown
        """
        # todo this is a duplicate call to the ShojiModelViewWidget
        # * need to figure out how to auto populate this.. while maintaining customization
        # setup args

        style_sheet_args.update({
            'outline_width': outline_width,
            'type': type(self).__name__
        })
        style_sheet_args.update(icons)

        # header
        base_header_style_sheet = """
                QHeaderView::section {{
                    background-color: rgba{rgba_background_00};
                    color: rgba{rgba_text};
                    border: {outline_width}px solid rgba{rgba_outline};
                }}
                {type}{{
                    border:None;
                    background-color: rgba{rgba_background_00};
                    selection-background-color: rgba{rgba_invisible};
                }}
                    """.format(**style_sheet_args)

        # item style snippets ( so it can be combined later...)
        style_sheet_args['item_snippet'] = """
                    border: {outline_width}px solid rgba{rgba_black};
                    background-color: rgba{rgba_background_00};
                """.format(**style_sheet_args)
        style_sheet_args['item_selected_snippet'] = """
                    border: {outline_width}px solid rgba{rgba_selected};
                    background-color: rgba{rgba_gray_3};
                """.format(**style_sheet_args)

        # create style sheet
        header_style_sheet = self.__class__.createStyleSheet(self, header_position, style_sheet_args)

        # combine style sheets
        style_sheet_args['splitter_style_sheet'] = "{type}{{selection-background-color: rgba(0,0,0,0);}}".format(**style_sheet_args)
        style_sheet_args['header_style_sheet'] = header_style_sheet
        style_sheet_args['base_header_style_sheet'] = base_header_style_sheet

        style_sheet = """
        {base_header_style_sheet}
        {header_style_sheet}
        {type}::item:hover{{
            color: rgba{rgba_text_hover};
            background-color: rgba{rgba_background_01};
        }}
        {splitter_style_sheet}
        """.format(**style_sheet_args)

        self.setStyleSheet(style_sheet)
        return style_sheet_args

    def setupCustomDelegate(self):
        delegate = AbstractDragDropModelDelegate(self)
        self.setItemDelegate(delegate)

    def getIndexUnderCursor(self):
        """
        Returns the QModelIndex underneath the cursor
        https://bugreports.qt.io/browse/QTBUG-72234
        """
        pos = self.viewport().mapFromParent(self.mapFromGlobal(QCursor.pos()))
        index = self.indexAt(pos)
        return index

    def setOrientation(self, orientation):
        """
        Set the orientation/direction of the view.  This will determine
        the flow of the items, from LeftToRight, or TopToBottom, depending
        on the orientation.

        Args:
            orientation (Qt.Orientation): Can either be
                Qt.Horizonal | Qt.Vertical
        """
        if orientation == Qt.Horizontal:
            self.setFlow(QListView.TopToBottom)
            direction = Qt.Vertical
        else:
            self.setFlow(QListView.LeftToRight)
            direction = Qt.Horizontal
        # update drag/drop style
        # todo WARNING: HARDCODED HERE
        try:
            if "ListView" in str(type(self)):
                self.style.setOrientation(direction)
            else:
                self.style.setOrientation(Qt.Vertical)
        except AttributeError:
            # for some reason katana doesnt like this...
            pass

    def setMultiSelect(self, multi_select):
        if multi_select is True:
            self.setSelectionMode(QAbstractItemView.MultiSelection)
        else:
            self.setSelectionMode(QAbstractItemView.SingleSelection)

    """ PROPERTIES (FLAGS) """
    def isCopyable(self):
        return self.model().isCopyable()

    def isItemCopyable(self, item):
        return self.model().isItemCopyable(item)

    def setIsCopyable(self, enabled):
        self.model().setIsCopyable(enabled)

    def isDraggable(self):
        return self.model().isDraggable()

    def setIsDraggable(self, enabled):
        self.model().setIsDraggable(enabled)

    def isDroppable(self):
        return self.model().isDroppable()

    def isItemDroppable(self, item):
        return self.model().isItemDroppable(item)

    def setIsDroppable(self, enabled):
        self.model().setIsDroppable(enabled)

    def isRootDroppable(self):
        return self.model().isRootDroppable()

    def setIsRootDroppable(self, enabled):
        self._isRootDroppable = enabled
        self.model().setIsRootDroppable(enabled)

    def isEditable(self):
        return self.model().isEditable()

    def setIsEditable(self, enabled):
        self.model().setIsEditable(enabled)

    def isEnableable(self):
        return self.model().isEnableable()

    def setIsEnableable(self, enabled):
        self.model().setIsEnableable(enabled)

    def isDeletable(self):
        return self.model().isDeletable()

    def setIsDeletable(self, enabled):
        self.model().setIsDeletable(enabled)

    def isSelectable(self):
        return self.model().isSelectable()

    def setIsSelectable(self, enabled):
        self.model().setIsSelectable(enabled)

    """ PROPERTIES """
    def copiedItems(self):
        return self._copied_items

    def setCopiedItems(self, copied_items):
        self._copied_items = copied_items

    def rootItem(self):
        return self.model().rootItem()

    """ SELECTION """
    def setItemSelected(self, item, selected):
        """ Selects the item provided
        Args:
            item (QModelIndex):
            selected (bool):

        Returns (True)"""
        index = self.model().getIndexFromItem(item)
        if selected:
            self.selectionModel().select(index, QItemSelectionModel.Select | QItemSelectionModel.Rows)
        else:
            self.selectionModel().select(index, QItemSelectionModel.Deselect | QItemSelectionModel.Rows)
        return True

    def setIndexSelected(self, index, selected):
        """
        Args:
            index (QModelIndex):
            selected (bool):

        Returns:

        """
        if selected:
            self.selectionModel().select(index, QItemSelectionModel.Select | QItemSelectionModel.Rows)
        else:
            self.selectionModel().select(index, QItemSelectionModel.Deselect | QItemSelectionModel.Rows)
        return True

    def clearItemSelection(self):
        self.selectionModel().clearSelection()
        # for index in self.selectedIndexes():
        #     self.selectionModel().select(index, QItemSelectionModel.Deselect)

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

    def getAllSelectedIndexes(self):
        selected_indexes = self.selectionModel().selectedRows(0)
        return selected_indexes

    def getAllSelectedItems(self):
        item_list = []
        for index in self.getAllSelectedIndexes():
            item_list.append(index.internalPointer())

        return item_list

    def getItemsSelectedDescendants(self, item, descendants=None):
        """ Gets all of the selected descendants from the item provided

        Returns (list): of AbstractDragDropModelItem"""
        if not descendants:
            descendants = []

        for child in item.children():
            if child in self.getAllSelectedItems():
                descendants.append(child)
            if 0 < item.childCount():
                descendants += self.getItemsDescendants(child)

        return descendants

    def getItemsDescendants(self, item, descendants=None):
        """ Gets all of the descendants from the item provided

        Returns (list): of AbstractDragDropModelItem"""
        if not descendants:
            descendants = []

        for child in item.children():
            # todo check if copyable?
            descendants.append(child)
            if 0 < item.childCount():
                descendants += self.getItemsDescendants(child)

        return descendants

    def getAllBaseItems(self, items=None):
        """ Takes a list of items, and returns only the top most item of each branch

        Args:
            items (list): of AbstractDragDropModelItem

        Returns (list): of AbstractDragDropModelItem

        """

        # get attrs
        if not items:
            items = self.getAllSelectedItems()
        base_items = self.getAllSelectedItems()

        # remove all selected descendants
        for item in items:
            for child in self.getItemsSelectedDescendants(item):
                if child in base_items:
                    base_items.remove(child)

        return base_items

    """ EXPORT DATA """
    def setItemExportDataFunction(self, func):
        self.model().setItemExportDataFunction(func)

    def exportModelToDict(self, item, item_data=None):
        return self.model().exportModelToDict(item, item_data=item_data)

    """ DELETE """
    def deleteWarningWidget(self):
        return self._delete_warning_widget

    def setDeleteWarningWidget(self, widget):
        self._delete_warning_widget = widget

    """ UTILS """
    def recurseFromIndexToRoot(self, index, function, *args, **kwargs):
        """
        Recursively searches up the ancestory doing the function provided to each index

        Args:
            index (QModelIndex):
            function (function): function to be passed to index.  This function takes
                atleast one arg, index
                Args: view, index, *args, **kwargs

        Returns:

        """
        parent_index = index.parent()
        parent_item = parent_index.internalPointer()
        if parent_item:
            function(self, parent_index, *args, **kwargs)
            return self.recurseFromIndexToRoot(parent_index, function, *args, **kwargs)
        else:
            return

    def getAllCopyableItems(self):
        """ Gets all of the currently selected indexes that can be copied.

        Returns (list): of AbstractDragDropModelItem"""

        copyable_items = self.getAllBaseItems()

        # check to see if items are copyable
        for item in copyable_items:
            if not self.model().isItemCopyable(item):
                copyable_items.remove(item)

        return copyable_items

    def copyCurrentSelectionToInternalClipboard(self):
        copyable_items = self.getAllCopyableItems()
        self.setCopiedItems(copyable_items)

        return copyable_items

    """ EVENTS """
    def enterEvent(self, event):
        self.setFocus()
        return QAbstractItemView.enterEvent(self, event)

    def expandToIndex(self, index, select=True):
        """ Expands to the index provided.  Assuming this is a TreeView"""
        def expandIndex(view, expand_index, expanded=True):
            self.setExpanded(expand_index, expanded)

        if select:
            self.setIndexSelected(index, True)
        self.recurseFromIndexToRoot(index, expandIndex, expanded=True)

    """ VIRTUAL """
    def abstractSelectionChanged(self, selected, deselected):
        for index in selected.indexes():
            if index.column() == 0:
                item = index.internalPointer()
                self.model().itemSelectedEvent(item, True)
                self.model().setLastSelectedItem(item)

        for index in deselected.indexes():
            if index.column() == 0:
                item = index.internalPointer()
                self.model().itemSelectedEvent(item, False)
                self.model().setLastSelectedItem(item)

    def abstractKeyPressEvent(self, event):
        if event.modifiers() == Qt.NoModifier:
            # Clear Selection
            if event.key() == Qt.Key_Escape:
                # from qtpy.QtWidgets import qApp
                # if qApp.widgetAt(QCursor.pos()) == self:
                self.clearItemSelection()

            # Delete Item
            #if self.model().isDeletable():
            if event.key() in [Qt.Key_Delete, Qt.Key_Backspace]:
                # delete events
                def deleteItems(widget):
                    deletable_items = self.getAllBaseItems()
                    for item in deletable_items:
                        if (item.isDeletable() == True) or (item.isDeletable() == None and self.isDeletable() == True):
                            self.model().deleteItem(item, event_update=True)

                def dontDeleteItem(widget):
                    return

                # delete item
                if self.deleteWarningWidget():
                    showWarningDialogue(self, self.deleteWarningWidget(), deleteItems, dontDeleteItem)
                else:
                    deleteItems(None)

            # Disable Item
            #if self.model().isEnableable():
            if event.key() == Qt.Key_D:
                indexes = self.selectionModel().selectedRows(0)
                for index in indexes:
                    item = index.internalPointer()
                    if (item.isEnableable() == True) or (item.isEnableable() == None and self.isEnableable() == True):
                        enabled = False if item.isEnabled() else True
                        self.model().setItemEnabled(item, enabled)
                self.model().layoutChanged.emit()

            #self.__keyPressEvent(event)

        if self.isCopyable():
            if event.modifiers() == Qt.ControlModifier:
                if event.key() == Qt.Key_C:
                    self.copyEvent()
                if event.key() == Qt.Key_V:
                    self.pasteEvent()
                if event.key() == Qt.Key_X:
                    self.cutEvent()
                if event.key() == Qt.Key_D:
                    self.duplicateEvent()

    def abstractMousePressEvent(self, event):
        self.__pressed = True
        self.__start_pos = event.pos()

    def abstractMouseReleaseEvent(self, event):
        self.__pressed = False

    def abstractMouseMoveEvent(self, event):
        if self.__pressed:
            index_under_cursor = self.indexAt(event.pos())
            if index_under_cursor.internalPointer():
                if self.model().lastSelectedItem():
                    index = self.model().getIndexFromItem(self.model().lastSelectedItem())
                    if index_under_cursor == index:
                        self.setIndexSelected(index, True)
            self.__pressed = False

    def setKeyPressEvent(self, function):
        self.__keyPressEvent = function

    # def setExpanded(self, index, bool):
    #     """ override for list views
    #
    #     I actually have no idea how this works, but somehow,
    #     it magically works"""
    #     return QAbstractItemView.keyPressEvent(self, index, bool)

    """ COPY / PASTE """
    def deepCopyItem(self, item, parent_index, row=0):
        """ Duplicates an item from the one provided

        Args:
            item (AbstractDragDropModelItem):
            parent_index (QModelIndex):
            row (int)

        Returns (QModelIndex): of new item
        """
        name = copy.deepcopy(item.name())
        column_data = copy.deepcopy(item.columnData())

        # create new index
        new_index = self.model().insertNewIndex(row, name=name, column_data=column_data, parent=parent_index)
        return new_index

    def setCopyEvent(self, function):
        self.__copyEvent = function

    def copyEvent(self):
        """ Copies all of the indexes selected to an internal clipboard"""
        copyable_items = self.copyCurrentSelectionToInternalClipboard()
        self.__copyEvent(copyable_items)

    def __copyEvent(self, copied_items):
        pass

    def setPasteEvent(self, function):
        self.__pasteEvent = function

    def getPasteLocation(self):
        """ Returns the current location where a paste event should occur

        Returns (AbstractDragDropModelItem)"""
        # default paste location
        if 0 < len(self.getAllSelectedItems()):
            current_item = self.getAllSelectedItems()[-1]
            if self.isItemDroppable(current_item):
                parent_item = current_item
            # paste on non-group
            else:
                parent_item = current_item.parent()
        # no objects selected
        else:
            parent_item = self.model().rootItem()

        # check is not pasting under current selection
        for item in self.copiedItems():
            if self.isItemDescendantOf(parent_item, item):
                parent_item = item
        return parent_item

    def isItemDescendantOf(self, item, ancestor):
        return self.model().isItemDescendantOf(item, ancestor)

    def pasteEvent(self):
        """
        Arg:
            copied_indexes (list): of QModelIndexes
            parent_index (QModelIndex):
        """
        # Get parent node/item
        parent_item = self.getPasteLocation()

        parent_index = self.model().getIndexFromItem(parent_item)

        # paste items
        pasted_items = []
        for item in self.copiedItems():
            # get attrs
            if item == parent_item:
                parent_item = item.parent()
                parent_index = self.model().getIndexFromItem(parent_item)
            row = copy.deepcopy(parent_item.childCount())
            new_index = self.deepCopyItem(item, parent_index, row)
            new_item = new_index.internalPointer()

            # check for group item
            self.__pasteGroupItem(item, new_index)

            # store new item
            pasted_items.append(new_item)

        # user defined paste event
        self.__pasteEvent(self.copiedItems(), pasted_items, parent_item)

    def __pasteGroupItem(self, item, parent_index):
        """ Creates all of the children when pasting a GroupItem"""
        # check for children
        if 0 < item.childCount():
            for child in item.children():
                row = copy.deepcopy(child.row())

                new_index = self.deepCopyItem(child, parent_index, row)
                # name = copy.deepcopy(item.name())
                # column_data = copy.deepcopy(item.columnData())
                # new_index = self.model().insertNewIndex(
                #     row, name=name, column_data=column_data, parent=parent_index)
                if 0 < child.childCount():
                    self.__pasteGroupItem(child, new_index)

    def __pasteEvent(self, copied_items, pasted_items, parent_item):
        pass

    def setCutEvent(self, function):
        self.__cutEvent = function

    def cutEvent(self):
        """ Copies all of the indexes selected to an internal clipboard"""
        copyable_items = self.copyCurrentSelectionToInternalClipboard()
        self.__cutEvent(copyable_items)

        # delete indexes
        for item in self.copiedItems():
            self.model().deleteItem(item, event_update=True)

    def __cutEvent(self, copied_items):
        pass

    def setDuplicateEvent(self, function):
        self.__duplicateEvent = function

    def duplicateEvent(self):
        """ Copies all of the indexes selected to an internal clipboard"""
        copyable_items = self.copyCurrentSelectionToInternalClipboard()
        new_items = []
        for item in self.copiedItems():

            row = copy.deepcopy(item.row())
            parent = self.model().getIndexFromItem(item.parent())
            new_index = self.deepCopyItem(item, parent, row)
            new_items.append(new_index.internalPointer())
            # name = copy.deepcopy(item.name())
            # column_data = copy.deepcopy(item.columnData())
            #

            # new_index = self.model().insertNewIndex(row+1, name=name, column_data=column_data, parent=parent)
            self.__pasteGroupItem(item, new_index)

        self.__duplicateEvent(copyable_items, new_items)

    def __duplicateEvent(self, copied_items, new_items):
        pass

    """ CONTEXT MENU """
    def abstractContextMenuEvent(self, event):
        # populate menu entries
        context_menu = AbstractViewContextMenu(self)

        for context_menu_item in self.contextMenuManifest():
            if context_menu_item.itemType() == attrs.CONTEXT_EVENT:
                context_menu.addAction(context_menu_item.name())
            else:
                context_menu.addSeparator()

        # Show/Execute menu
        pos = event.globalPos()
        context_menu.popup(pos)
        action = context_menu.exec_(pos)

        # get selected items / items under cursor
        index_clicked = context_menu.item
        selected_indexes = self.selectionModel().selectedRows(0)

        # do user defined event
        if action is not None:
            event = self.findContextMenuEvent(action.text())
            if event:
                event(index_clicked, selected_indexes)
            # self.contextMenuManifest()[action.text()](index_clicked, selected_indexes)

    def addContextMenuSeparator(self):
        context_data = AbstractContextMenuItem(None, None, attrs.CONTEXT_SEPERATOR)
        self.contextMenuManifest().append(context_data)

    def addContextMenuEvent(self, name, event):
        """
        Adds an entry into the RMB popup menu.

        Args:
            name (str): name of function to be displayed
            event (function): event to be run.
                takes two args:
                    item_under_cursor (item): current item under cursor
                    indexes (list): of currently selected QModelIndexes
            item_type (attrs.CONTEXT_ITEM_TYPE):
        """
        context_data = AbstractContextMenuItem(name, event, attrs.CONTEXT_EVENT)
        self.contextMenuManifest().append(context_data)

    def findContextMenuEvent(self, name):
        for item in self.contextMenuManifest():
            if item.name() == name:
                return item.event()
        return None

    def contextMenuManifest(self):
        return self._context_menu_manifest


class AbstractContextMenuItem(object):
    """ An item that containts the data required to create a context menu event"""
    def __init__(self, name, event, item_type):
        self._name = name
        self._event = event
        self._item_type = item_type

    def event(self):
        return self._event

    def setEvent(self, event):
        self._event = event

    def itemType(self):
        return self._item_type

    def setItemType(self, item_type):
        self._item_type = item_type

    def name(self):
        return self._name

    def setName(self, name):
        self._name = name


class AbstractDragDropListView(QListView, AbstractDragDropAbstractView):
    def __init__(self, parent=None):
        super(AbstractDragDropListView, self).__init__(parent)
        if API_NAME == "PySide2":
            AbstractDragDropAbstractView.__init__(self)
        self.setEditTriggers(QAbstractItemView.DoubleClicked)
        self._is_droppable = False

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
        else:
            style_sheet = """
            {type}::item{{
                {item_snippet}
            }}
            {type}::item:selected{{
                {item_selected_snippet}
            }}
            """.format(**style_sheet_args)

        # add scroll bar
        from cgwidgets.settings.stylesheets import scroll_bar_ss
        style_sheet += scroll_bar_ss

        #
        return style_sheet

    """ EVENTS """

    def contextMenuEvent(self, event):
        self.abstractContextMenuEvent(event)
        return QListView.contextMenuEvent(self, event)

    def mousePressEvent(self, event):
        self.abstractMousePressEvent(event)
        return QListView.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        self.abstractMouseReleaseEvent(event)
        return QListView.mouseReleaseEvent(self, event)

    def mouseMoveEvent(self, event):
        self.abstractMouseMoveEvent(event)
        return QListView.mouseMoveEvent(self, event)

    def selectionChanged(self, selected, deselected):
        self.abstractSelectionChanged(selected, deselected)

    def keyPressEvent(self, event):
        self.abstractKeyPressEvent(event)
        return QListView.keyPressEvent(self, event)


class AbstractDragDropTreeView(QTreeView, AbstractDragDropAbstractView):
    def __init__(self, parent=None):
        super(AbstractDragDropTreeView, self).__init__(parent)
        if API_NAME == "PySide2":
            AbstractDragDropAbstractView.__init__(self)

        # context menu
        # self.addContextMenuEvent("Expand Item and All Children", self.expandItemEvent)
        self.addContextMenuEvent("Expand All", self.expandAllEvent)
        self.addContextMenuEvent("Collapse All", self.collapseAllEvent)

    """ EVENTS """
    def expanded(self, index):
        print("============ EXPANDED ==================")
        # print("expanded", index.internalPointer().name())
        return QTreeView.expanded(self, index)

    """ EVENTS (CONTEXT MENU)"""
    def expandItemEvent(self, item, indexes):
        # todo expand recursively broken
        for index in indexes:
            if hasattr(self, "expandRecursively"):
                self.expandRecursively(index)
        # self.expandAll()

    def expandAllEvent(self, item, indexes):
        self.expandAll()

    def collapseAllEvent(self,  item, indexes):
        self.collapseAll()
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
            background-color: rgba{rgba_background_00};
            color: rgba{rgba_text};
            border: {outline_width}px solid rgba{rgba_black};
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

        # add scroll bar
        from cgwidgets.settings.stylesheets import scroll_bar_ss
        style_sheet += scroll_bar_ss

        # return
        return style_sheet

    def setFlow(self, _):
        pass

    """ EVENTS """
    def contextMenuEvent(self, event):
        self.abstractContextMenuEvent(event)
        return QTreeView.contextMenuEvent(self, event)

    def mousePressEvent(self, event):
        self.abstractMousePressEvent(event)
        return QTreeView.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        self.abstractMouseReleaseEvent(event)

        # update items expansion state
        index = self.indexAt(event.pos())
        if index.internalPointer():
            is_expanded = self.isExpanded(index)
            index.internalPointer().setIsExpanded(is_expanded)

        return QTreeView.mouseReleaseEvent(self, event)

    def mouseMoveEvent(self, event):
        self.abstractMouseMoveEvent(event)
        return QTreeView.mouseMoveEvent(self, event)

    def selectionChanged(self, selected, deselected):
        self.abstractSelectionChanged(selected, deselected)

    def keyPressEvent(self, event):
        self.abstractKeyPressEvent(event)
        return QTreeView.keyPressEvent(self, event)


class AbstractViewContextMenu(QMenu):
    def __init__(self, parent=None):
        super(AbstractViewContextMenu, self).__init__(parent)
        self.item = None

    def showEvent(self, event):
        self.item = self.parent().getIndexUnderCursor()


""" STYLES """
class AbstractDragDropModelDelegate(QStyledItemDelegate):
    """
    Default item delegate that is used in the custom Drag/Drop model

    Attributes:
        delegate_widget (QWidget): constructor to be displayed when editor is shown
    """
    def __init__(self, parent=None):
        super(AbstractDragDropModelDelegate, self).__init__(parent)
        # importing the default delegate here
        # as it will run into import errors if imported at top most lvl
        from cgwidgets.widgets.AbstractWidgets import AbstractStringInputWidget
        self._delegate_widget = AbstractStringInputWidget
        # from qtpy.QtWidgets import QLineEdit
        # self._delegate_widget = QLineEdit

    def sizeHint(self, *args, **kwargs):
        return QStyledItemDelegate.sizeHint(self, *args, **kwargs)

    def updateEditorGeometry(self, editor, option, index):
        """
        Updates the editor geometry to will up the entire row

        Updates the delegates geometry with the options rect
        for some reason this wont work if you manually do a
        setGeometry(0,0,100,100), but it works when plugging in
        a rect /shrug
        """
        rect = option.rect
        width = self.parent().geometry().width()
        rect.setWidth(width)
        rect.setX(0)
        editor.setGeometry(option.rect)

    def createEditor(self, parent, option, index):
        """

        """
        delegate_widget = self.delegateWidget(parent)
        return delegate_widget

    def setEditorData(self, editor, index):
        # text = index.model().data(index, Qt.DisplayRole)
        # editor.setText(text)
        return QStyledItemDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        """# swap out 'v' for current value"""
        # =======================================================================
        # get data
        # =======================================================================
        "setting model data???"
        new_value = editor.text()
        if new_value == '':
            return
        item = index.internalPointer()
        arg = model._header_data[index.column()]
        old_value = item.columnData()[arg]
        new_value = editor.text()

        # set model data
        item.columnData()[arg] = new_value

        # emit text changed event
        model.textChangedEvent(item, old_value, new_value)

        #model.setData(index, QVariant(new_value))
        #model.aov_list[index.row()] = new_value
        '''
        data_type = self.getDataType(index)
        main_table = self.parent()
        old_value = main_table.getCurrentValue()
        value = main_table.evaluateCell(old_value, new_value, data_type=data_type)
        model.setData(index, QtCore.QVariant(value))
        '''

    def setDelegateWidget(self, delegate_widget):
        self._delegate_widget = delegate_widget

    def delegateWidget(self, parent):
        constructor = self._delegate_widget
        widget = constructor(parent)
        return widget

    def paint(self, painter, option, index):
        """
        Overrides the selection highlight color.

        https://www.qtcentre.org/threads/41299-How-to-Change-QTreeView-highlight-color
        Note: this can actually do alot more than that with the QPalette...
            which is something I should learn how to use apparently...

        """
        from qtpy.QtGui import QPalette
        item = index.internalPointer()
        new_option = QStyleOptionViewItem(option)
        brush = QBrush()
        if item.isEnabled():
            color = QColor(*iColor["rgba_text"])
        else:
            color = QColor(*iColor["rgba_text_disabled"])
        # TODO highlight selection color???
        # why did I move this here?
        brush.setColor(color)

        # brush2 = QBrush(QColor(0, 255, 0, 128))
        new_option.palette.setBrush(QPalette.Normal, QPalette.HighlightedText, brush)
        # new_option.palette.setBrush(QPalette.Normal, QPalette.Highlight, brush2)

        QStyledItemDelegate.paint(self, painter, new_option, index)

        # if option.state == QStyle.State_Selected:
        #     brush2 = QBrush(QColor(0, 255, 255, 128))
        return


# example drop indicator
class AbstractDragDropIndicator(QProxyStyle):
    """
    Drag / drop style.

    Args:
        direction (Qt.DIRECTION): What direction the current flow of
            the widget is
    """
    INDICATOR_WIDTH = 2
    INDICATOR_SIZE = 10

    def __init__(self, parent=None):
        super(AbstractDragDropIndicator, self).__init__(parent)
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
            l_indicator.translate(QPoint(int(size + (width / 2)), y_pos))

            r_indicator = self.createTriangle(size, attrs.WEST)
            r_indicator.translate(QPoint(
                int(widget.width() - size - (width / 2)), y_pos)
            )

            # draw
            painter.drawPolygon(l_indicator)
            painter.drawPolygon(r_indicator)
            painter.drawLine(
                QPoint(int(size + (width / 2)), y_pos),
                QPoint(int(widget.width() - size - (width / 2)), y_pos)
            )

            # set fill color
            background_color = QColor(*iColor["rgba_gray_3"])
            brush = QBrush(background_color)
            path = QPainterPath()
            path.addPolygon(l_indicator)
            path.addPolygon(r_indicator)
            painter.fillPath(path, brush)
        #
        # # drop on
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
            background_color = QColor(*iColor["rgba_gray_3"])
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
            size = AbstractDragDropIndicator.INDICATOR_SIZE
            width = AbstractDragDropIndicator.INDICATOR_WIDTH

            # border color
            border_color = QColor(*iColor["rgba_selected"])
            pen = QPen()
            pen.setWidth(AbstractDragDropIndicator.INDICATOR_WIDTH)
            pen.setColor(border_color)

            # background
            background_color = QColor(*iColor["rgba_selected"])
            background_color.setAlpha(64)
            brush = QBrush(background_color)

            # set painter
            painter.setPen(pen)
            painter.setBrush(brush)

            # draw
            if self.orientation() == Qt.Vertical:
                self.__drawVertical(widget, option, painter, size, width)
            elif self.orientation() == Qt.Horizontal:
                self.__drawHorizontal(widget, option, painter, size, width)
        else:
            super(AbstractDragDropIndicator, self).drawPrimitive(element, option, painter, widget)

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

        # fixed this...
        if API_NAME == "PySide2":
            triangle = QPolygonF([QPointF(point[0], point[1]) for point in triangle_point_list])
        else:
             triangle = QPolygonF(map(lambda p: QPoint(*p), triangle_point_list))

        return triangle


if __name__ == '__main__':
    import sys
    from qtpy.QtWidgets import (
        QApplication, QTreeView, QListView, QAbstractItemView)
    from qtpy.QtGui import QCursor


    app = QApplication(sys.argv)

    def testDrag(indexes, model):
        " test drag..."
        print(indexes)

    def testDrop(indexes, parent):
        print(indexes, parent)

    def testEdit(item, old_value, new_value):
        print(item, old_value, new_value)

    def testEnable(item, enabled):
        print(item.columnData()['name'], enabled)

    def testDelete(item):
        print(item.columnData()['name'])

    model = AbstractDragDropModel()

    for x in range(0, 4):
        model.insertNewIndex(x, str('node%s'%x))

    #model.setIsRootDroppable(False)
    #model.setIsDraggable(False)
    # set model event
    model.setDragStartEvent(testDrag)
    model.setDropEvent(testDrop)
    model.setTextChangedEvent(testEdit)
    model.setItemEnabledEvent(testEnable)
    model.setItemDeleteEvent(testDelete)

    tree_view = AbstractDragDropListView()
    tree_view.setStyle(AbstractDragDropIndicator())

    tree_view.move(QCursor.pos())
    tree_view.setSelectionMode(QAbstractItemView.MultiSelection)

    tree_view.setModel(model)
    #model.setIsDraggable(True)

    list_view = AbstractDragDropListView()

    list_view.move(QCursor.pos())
    #list_view.setDragDropOverwriteMode(False)
    list_view.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
    #list_view.setDropIndicatorShown(True)
    list_view.setModel(model)
    list_view.setIsDroppable(False)
    list_view.setIsEnableable(False)
    # table_view = QTableView()
    # table_view.show()

    #tree_view.show()

    list_view.show()
    # table_view.setModel(model)

    sys.exit(app.exec_())
import sys
import os

from qtpy.QtWidgets import (QSplitterHandle, QApplication, QLabel, QCompleter, QTreeView, QWidget, QVBoxLayout)
from qtpy.QtCore import Qt
from qtpy.QtGui import QCursor

from cgwidgets.widgets import AbstractStringInputWidget, AbstractListInputWidget
from cgwidgets.views import (
    AbstractDragDropModel,
    AbstractDragDropTreeView,
    AbstractDragDropListView,
    AbstractDragDropModelItem
)
from cgwidgets.utils import attrs, getWidgetAncestor
from cgwidgets.settings import iColor
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
        self.not_soloable = True
        self.setProperty('is_soloable', True)

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
        if hasattr (self, "_view"):
            self._view.setParent(None)

        # setup model
        if self.model():
            view.setModel(self.model())
            # if isinstance(view, AbstractDragDropListView):
            #     self.setIsDropEnabled(False)
        else:
            model = AbstractDragDropModel()
            view.setModel(model)

        # setup attr
        self._view = view
        self._view.not_soloable = True

        # add view
        self.insertWidget(0, self._view)

        # setup custom key presses
        if hasattr(view, "setKeyPressEvent"):
            view.setKeyPressEvent(self.keyPressEvent)

        # setup default drop attrs
        if view_type == AbstractModelViewWidget.TREE_VIEW:
            self.setIsDropEnabled(True)
        if view_type == AbstractModelViewWidget.LIST_VIEW:
            self.setIsDropEnabled(False)

    def setPresetViewType(self, view_type):
        """
        Sets the view to either a LIST or a TREE view

        Args:
            view_type (AbstractModelViewWidget.VIEW_TYPE): the view type to be used.
                AbstractModelViewWidget.TREE_VIEW | AbstractModelViewWidget.LIST_VIEW

        Returns (QWidget): view
        """
        if view_type == AbstractModelViewWidget.TREE_VIEW:
            view = AbstractDragDropTreeView()

        if view_type == AbstractModelViewWidget.LIST_VIEW:
            view = AbstractDragDropListView()

        self.setView(view, view_type=view_type)

        return view

    def addContextMenuEvent(self, name, event):
        """
        Adds an entry into the RMB popup menu.

        Args:
            name (str): name of function to be displayed
            event (function): takes two args:
                item_under_cursor (item): current item under cursor
                indexes (list): of currently selected QModelIndexes
        """
        if hasattr(self.view(), 'addContextMenuEvent'):
            self.view().addContextMenuEvent(name, event)
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
            return self.view().model()
        else:
            return None

    def setModel(self, model):
        self.view().setModel(model)

    def clearModel(self):
        self.model().clearModel()

    """ SELECTION """
    def selectionModel(self):
        return self.view().selectionModel()

    def getAllSelectedIndexes(self):
        # selected_indexes = []
        # for index in self.headerWidget().selectionModel().selectedIndexes():
        #     if index.column() == 0:
        #         selected_indexes.append(index)
        selected_indexes = self.selectionModel().selectedRows(0)
        return selected_indexes

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

    def addDelegate(self, input, widget, modifier=Qt.NoModifier, focus=False, focus_widget=None):
        """
        Adds a new delegate that can be activated with the input/modifer combo provided

        Args:
            input (list): of Qt.KEY
            widget (QWidget):
            modifier (Qt.MODIFIER):
            focus (bool): determines if the widget should be focus when it is shown or not

        Returns:
        """
        # add to manifest
        delegate_manifest = {}
        delegate_manifest["input"] = input
        delegate_manifest["widget"] = widget
        delegate_manifest["modifier"] = modifier
        delegate_manifest["focus"] = focus
        delegate_manifest["focus_widget"] = focus_widget

        self._delegate_manifest.append(delegate_manifest)

        # add widget
        self.addWidget(widget)
        widget.hide()

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

    def setDelegateToggleEvent(self, function):
        self.__delegateToggleEvent = function

        """ VIRTUAL FUNCTIONS """

    def setItemDeleteEvent(self, function):
        self.model().setItemDeleteEvent(function)

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
    def enterEvent(self, event):
        self.setFocus()

    def keyPressEvent(self, event):
        """
        # TODO TOGGLE DELEGATE KEY
        # this is also maintained under... ShojiMainDelegateWidget
        """

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
                    widget = delegate_manifest["widget"]
                    self.toggleDelegateWidget(event, widget)

                    # set focus
                    if delegate_manifest["focus"]:
                        # focus widget provided
                        if delegate_manifest["focus_widget"]:
                            delegate_manifest["focus_widget"].setFocus()
                        # focus delegate
                        else:
                            widget.setFocus()
                    else:
                        # focus model
                        self.setFocus()

        # full screen
        """copy / paste from AbstractShojiLayout.__soloViewHotkeyPressed
        this is essentially just overriding to automagically full screen
        the parent with Alt+~ instead of the base of ~"""
        if event.key() == AbstractShojiLayout.FULLSCREEN_HOTKEY:
            # preflight
            pos = QCursor.pos()

            widget_pressed = QApplication.instance().widgetAt(pos)

            # bypass handles
            if isinstance(widget_pressed, QSplitterHandle):
                return
            # Press solo view hotkey
            widget_soloable = self.getFirstSoloableWidget(widget_pressed)

            # return if no soloable widget found
            if not widget_soloable: return

            # toggle solo view ( shoji view )
            if widget_soloable.parent():
                widget_soloable = widget_soloable.parent()
                self.toggleIsSoloView(True, widget=widget_soloable)


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
        def expandIndex(view, index, expanded=True):
            view.setExpanded(index, expanded)

        for index in indexes:
            view.setIndexSelected(index, True)
            view.recurseFromIndexToRoot(index, expandIndex, expanded=True)

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
    # main_widget.setIsRootDropEnabled(True)
    # main_widget.setIsEditable(True)
    # main_widget.setIsDragEnabled(True)
    # #main_widget.setIsDropEnabled(True)
    # main_widget.setIsEnableable(True)
    # main_widget.setIsDeleteEnabled(True)
    #
    # # set selection mode
    # main_widget.setMultiSelect(True)



    w.move(QCursor.pos())

    w.show()




    sys.exit(app.exec_())
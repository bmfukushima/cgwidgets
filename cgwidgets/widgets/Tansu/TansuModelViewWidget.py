"""
TODO:
    - Escape
        Return to correct widget display mode in the Tansu Widget
    - Dynamic will need updates since
         - insertViewItem modified to put the tab name at the top when solo'ing
    - DelegateWidget needs to sync up with ~/esc for the Tansu Widget
        *   If none selected, show ALL
    - setCurrentIndex?
    - currentIndex?

    Horizontal/vertical tree widgets... makes a case to pull out the double tree widget...
"""

from qtpy.QtWidgets import (
    QWidget, QListView, QAbstractItemView, QScrollArea
)
from qtpy.QtCore import Qt, QModelIndex

from cgwidgets.settings.colors import (
    RGBA_TANSU_HANDLE,
)
from cgwidgets.utils import getWidgetAncestor

from cgwidgets.widgets import AbstractInputGroup
from cgwidgets.widgets.Tansu import (
    BaseTansuWidget, TansuModel, TansuModelItem
)


class TansuModelViewWidget(BaseTansuWidget):
    """
    This is the designing portion of this editor.  This is where the TD
    will design a custom UI/hooks/handlers for the tool for the end user,
    which will be displayed in the ViewWidget

    Args:
        direction (TansuModelViewWidget.DIRECTION): Determines where the tab
            bar should be placed.  The default value is NORTH
        type (TansuModelViewWidget.TYPE): What type of tab widget this should be,
            options are STACKED | DYNAMIC | MULTI
            see class attrs for more info...
        selected_labels_list (list): list of labels that are currently selected by the user

    Attributes:
        rgba_handle (rgba): color of the outline for the individual tab labels
            default color is TansuModelViewWidget.OUTLINE_COLOR
        rgba_selected_tab (rgba): text color of selected tab
            default color is TansuModelViewWidget.SELECTED_COLOR
        rgba_selected_tab_hover (rgba): text color of tab when hovered over
         TansuModelViewWidget.SELECTED_COLOR_HOVER
        view_height (int): the default height of the tab label in pixels
            only works when the mode is set to view the labels on the north/south
        view_width (int): the default width of the tab label in pixels
            only works when the mode is set to view the labels on the east/west
    Class Attrs:
        TYPE
            STACKED: Will operate like a normal tab, where widgets
                will be stacked on top of each other)
            DYNAMIC: There will be one widget that is dynamically
                updated based off of the labels args
            MULTI: Similair to stacked, but instead of having one
                display at a time, multi tabs can be displayed next
                to each other.
    Essentially this is a custom tab widget.  Where the name
        label: refers to the small part at the top for selecting selctions
        bar: refers to the bar at the top containing all of the afformentioned tabs
        widget: refers to the area that displays the GUI for each tab

    Widgets:
        |-- QBoxLayout
                |-- ViewWidget (TansuTreeView)
                        ( TansuListView | TansuTableView | TansuTreeView )
                | -- Scroll Area
                    |-- DelegateWidget (TansuMainDelegateWidget --> BaseTansuWidget)
                            | -- _temp_proxy_widget (QWidget)
                            | -* TansuModelDelegateWidget (AbstractGroupBox)
                                    | -- Stacked/Dynamic Widget (main_widget)

    """
    NORTH = 'north'
    SOUTH = 'south'
    EAST = 'east'
    WEST = 'west'
    OUTLINE_WIDTH = 1
    OUTLINE_COLOR = RGBA_TANSU_HANDLE
    STACKED = 'stacked'
    DYNAMIC = 'dynamic'
    MULTI = False
    TYPE = STACKED

    def __init__(self, parent=None, direction=NORTH):
        super(TansuModelViewWidget, self).__init__(parent)
        # etc attrs
        self.setHandleWidth(5)
        self._direction = direction #just a temp set... for things
        self._view_height = 50
        self._view_width = 100

        # colors attrs
        self.rgba_handle = TansuModelViewWidget.OUTLINE_COLOR
        style_sheet = """
            QSplitter::handle {
                border: None;
            }
        """
        self.setStyleSheet(style_sheet)

        # setup model / view
        new_model = TansuModel()
        default_view_widget = TansuListView(self)
        self.setViewWidget(default_view_widget)
        self.setModel(new_model)

        # setup delegate
        delegate_widget = TansuMainDelegateWidget()
        self.setDelegateWidget(delegate_widget)
        self._temp_proxy_widget = QWidget()

        self.delegateWidget().addWidget(self._temp_proxy_widget)

        # setup main layout
        scroll_area = QScrollArea()
        scroll_area.setWidget(delegate_widget)
        scroll_area.setWidgetResizable(True)

        self.addWidget(scroll_area)
        self.addWidget(self._view_widget)

        # set default attrs
        self.setDelegateType(TansuModelViewWidget.TYPE)
        self.setViewPosition(direction)
        self.setMultiSelect(TansuModelViewWidget.MULTI)

    def insertViewItem(self, index, name, parent=None, widget=None):
        """
        Creates a new tab at  the specified index

        Args:
            index (int): index to insert widget at
            widget (QWidget): widget to be displayed at that index
            name (str): name of widget
            parent (QModelIndex): Parent index to create this new
                tab under neath

        Returns (Tab Label)
        """
        # create new model index
        if not parent:
            parent = QModelIndex()
        self.model().insertRows(index, 1, parent)

        # setup custom object
        row = self.model().index(index, 1, parent)
        view_item = row.internalPointer()
        view_item.setName(name)

        # add to layout if stacked
        if self.getDelegateType() == TansuModelViewWidget.STACKED:
            # create tab widget widget
            view_delegate_widget = self.createTansuModelDelegateWidget(name, widget)
            view_item.setDelegateWidget(view_delegate_widget)
            # insert tab widget
            self.delegateWidget().insertWidget(index, view_delegate_widget)
            view_delegate_widget.hide()

        return view_item

    """ MODEL """
    def model(self):
        return self._model

    def setModel(self, model):
        self._view_widget.setModel(model)
        self._model = model

    """ VIEW """
    def viewWidget(self):
        return self._view_widget

    def setViewWidget(self, view_widget):
        self._view_widget = view_widget

    def getViewPosition(self):
        return self._direction

    def setViewPosition(self, direction):
        """
        Sets the current direction this widget.  This is the orientation of
        where the tab labels will be vs where the main widget will be, where
        the tab labels bar will always be the first widget.
        """
        self._direction = direction
        self.viewWidget().setParent(None)

        if direction == TansuModelViewWidget.WEST:
            self.setOrientation(Qt.Horizontal)
            self.viewWidget().setOrientation(Qt.Horizontal)
            self.insertWidget(0, self.viewWidget())

        elif direction == TansuModelViewWidget.EAST:
            self.setOrientation(Qt.Horizontal)
            self.viewWidget().setOrientation(Qt.Horizontal)
            self.insertWidget(1, self.viewWidget())

        elif direction == TansuModelViewWidget.NORTH:
            self.setOrientation(Qt.Vertical)
            self.viewWidget().setOrientation(Qt.Vertical)
            self.insertWidget(0, self.viewWidget())

        elif direction == TansuModelViewWidget.SOUTH:
            self.setOrientation(Qt.Vertical)
            self.viewWidget().setOrientation(Qt.Vertical)
            self.insertWidget(1, self.viewWidget())

        # make uncollapsible
        self.setCollapsible(0, False)
        self.setCollapsible(1, False)

    def setViewWidgetToDefaultSize(self):
        """
        Moves the main slider to make the tab label bar the default startup size
        """
        if self.getViewPosition() == TansuModelViewWidget.NORTH:
            self.moveSplitter(self.view_height, 1)
        elif self.getViewPosition() == TansuModelViewWidget.SOUTH:
            self.moveSplitter(self.height() - self.view_height, 1)
        elif self.getViewPosition() == TansuModelViewWidget.WEST:
            self.moveSplitter(self.view_width, 1)
        elif self.getViewPosition() == TansuModelViewWidget.EAST:
            self.moveSplitter(self.width() - self.view_width, 1)

    def createTansuModelDelegateWidget(self, name, widget):
        """
        Creates a new tab widget widget...
        TODO:
            Move to base tansu?
        """
        display_widget = TansuModelDelegateWidget(self, name)
        display_widget.setMainWidget(widget)

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
        of the view/delegate positions
        """
        # hide/show proxy widget
        if hasattr(self, "_temp_proxy_widget"):
            selection_model = self.viewWidget().selectionModel()
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
            selection_model = self.viewWidget().selectionModel()
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
            self.__updateDelegateItem(item, True)

        for index in deselected.indexes():
            item = index.internalPointer()
            self.__updateDelegateItem(item, False)

    def __updateDelegateItem(self, item, selected):
        """
        item (TansuModelItem)
        selected (bool): determines if this item has been selected
            or un selected.
        """
        if not hasattr(item, '_delegate_widget'): return

        # update static widgets
        if self.getDelegateType() == TansuModelViewWidget.STACKED:
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
            dynamic_widget = self.createNewDynamicWidget(name=item.name())
            self.delegateWidget().addWidget(dynamic_widget)
            item.setDelegateWidget(dynamic_widget)
            self.updateDynamicWidget(dynamic_widget, item)
        else:
            # destroy widget
            try:
                item.delegateWidget().setParent(None)
            except AttributeError:
                pass

    """ DYNAMIC WIDGET """
    def createNewDynamicWidget(self, name="Nothing Selected..."):
        dynamic_widget_class = self.getDynamicWidgetBaseClass()
        new_dynamic_widget = dynamic_widget_class()
        new_widget = self.createTansuModelDelegateWidget(name, new_dynamic_widget)
        return new_widget

    def __dynamicWidgetFunction(self):
        pass

    def setDynamicUpdateFunction(self, function):
        self.__dynamicWidgetFunction = function

    def setDynamicWidgetBaseClass(self, widget):
        """
        Sets the constructor for the dynamic widget.  Everytime
        a new dynamic widget is created. It will use this base class
        """
        self._dynamic_widget_base_class = widget

    def getDynamicWidgetBaseClass(self):
        return self._dynamic_widget_base_class

    def updateDynamicWidget(self, widget, label, *args, **kwargs):
        """
        Updates the dynamic widget

        Args:
            widget (DynamicWidget) The dynamic widget that should be updated
            label (TabTansuLabelWidget): The tab label that should be updated
        """
        # needs to pick which to update...
        self.__dynamicWidgetFunction(widget, label, *args, **kwargs)

    """ EVENTS """
    def showEvent(self, event):
        self.setViewWidgetToDefaultSize()
        return BaseTansuWidget.showEvent(self, event)

    """ PROPERTIES """
    """ selection """
    def setMultiSelect(self, enabled):
        self._multi_select = enabled
        self.viewWidget().setMultiSelect(enabled)

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
            # preflight check
            if not dynamic_widget:
                print ("provide a widget to use...")
                return
            if not dynamic_function:
                print ("provide a function to use...")
                return
            self.setDynamicWidgetBaseClass(dynamic_widget)
            self.setDynamicUpdateFunction(dynamic_function)

        # update attr
        self._delegate_type = value

    def getDelegateType(self):
        return self._delegate_type

    def getViewInstanceType(self):
        return self._view_item_type

    def setViewInstanceType(self, view_item_type):
        self._view_item_type = view_item_type

    """ LAYOUT """

    """ colors """
    @property
    def rgba_handle(self):
        return self._rgba_handle

    @rgba_handle.setter
    def rgba_handle(self, rgba_handle):
        self._rgba_handle = rgba_handle

    """ default view size"""
    @property
    def view_width(self):
        return self._view_width

    @view_width.setter
    def view_width(self, view_width):
        self._view_width = view_width

    @property
    def view_height(self):
        return self._view_height

    @view_height.setter
    def view_height(self, view_height):
        self._view_height = view_height


class TansuMainDelegateWidget(BaseTansuWidget):
    """
    The main delegate view that will show all of the items widgets that
     the user currently has selected
    """
    def __init__(self, parent=None):
        super(TansuMainDelegateWidget, self).__init__(parent)

    def showEvent(self, event):
        tab_tansu_widget = getWidgetAncestor(self, TansuModelViewWidget)
        if tab_tansu_widget:
            tab_tansu_widget.updateDelegateDisplay()

    def keyPressEvent(self, event):
        BaseTansuWidget.keyPressEvent(self, event)
        if event.key() == Qt.Key_Escape:
            tab_tansu_widget = getWidgetAncestor(self, TansuModelViewWidget)
            if tab_tansu_widget:
                tab_tansu_widget.updateDelegateDisplay()


class TansuModelDelegateWidget(AbstractInputGroup):
    """
    This is a clone of the InputGroup... but I'm getting
    stuck in import recursion land... so... this is a copy
    paste.  Sorry. deal with it.
    """
    def __init__(self, parent=None, title=None):
        super(TansuModelDelegateWidget, self).__init__(parent, title)
        self.display_background = False
        self.alpha = 0
        self.updateStyleSheet()

    def setMainWidget(self, widget):
        # remove old main widget if it exists
        if hasattr(self, '_main_widget'):
            self._main_widget.setParent(None)

        self._main_widget = widget
        self.layout().addWidget(self._main_widget)

    def getMainWidget(self):
        return self._main_widget


# need to do a QAbstractItemView injection here...

class TansuListView(QListView):
    def __init__(self, parent=None):
        super(TansuListView, self).__init__(parent)
        self.setEditTriggers(QAbstractItemView.DoubleClicked)

    def showEvent(self, event):
        tab_tansu_widget = getWidgetAncestor(self, TansuModelViewWidget)
        if tab_tansu_widget:
            tab_tansu_widget.updateDelegateDisplay()
            # if tab_tansu_widget.getDelegateType() == TansuModelViewWidget.STACKED:
            #     tab_tansu_widget.toggleDelegateSpacerWidget()
            #     selection_model = self.selectionModel()
            #     widget_list = []
            #     for index in selection_model.selectedIndexes():
            #         item = index.internalPointer()
            #         widget = item.delegateWidget()
            #         widget_list.append(widget)
            #
            #     tab_tansu_widget.delegateWidget().isolateWidgets(widget_list)
        QListView.showEvent(self, event)

    def setOrientation(self, orientation):
        if orientation == Qt.Horizontal:
            self.setFlow(QListView.TopToBottom)
        else:
            self.setFlow(QListView.LeftToRight)

    def setMultiSelect(self, multi_select):
        if multi_select is True:
            self.setSelectionMode(QAbstractItemView.MultiSelection)
        else:
            self.setSelectionMode(QAbstractItemView.SingleSelection)

    def selectionChanged(self, selected, deselected):
        top_level_widget = getWidgetAncestor(self, TansuModelViewWidget)
        if top_level_widget:
            top_level_widget.updateDelegateDisplayFromSelection(selected, deselected)
        # for index in selected.indexes():
        #     item = index.internalPointer()


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
    def updateGUI(widget, item):
        """
        widget (TansuModelDelegateWidget)
        item (TansuModelItem)
        """
        if item:
            widget.setTitle(item.name())
            widget.getMainWidget().label.setText(item.name())


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout
    from PyQt5.QtGui import QCursor
    app = QApplication(sys.argv)

    w = TansuModelViewWidget()
    w.setViewPosition(TansuModelViewWidget.WEST)
    w.setMultiSelect(True)
    w.setMultiSelectDirection(Qt.Vertical)

    # dw = TabTansuDynamicWidgetExample
    # w.setDelegateType(
    #     TansuModelViewWidget.DYNAMIC,
    #     dynamic_widget=TabTansuDynamicWidgetExample,
    #     dynamic_function=TabTansuDynamicWidgetExample.updateGUI
    # )

    for x in range(3):
        widget = QLabel(str(x))
        w.insertViewItem(x, str(x),widget=widget)

    w.resize(500, 500)

    w.show()
    w.setViewWidgetToDefaultSize()

    # q = TansuListView()
    # q.show()
    #
    # q.setModel(w.model())

    w.move(QCursor.pos())
    sys.exit(app.exec_())

"""
TODO:
    - Escape
        Return to correct widget display mode in the Tansu Widget
    - Dynamic will need updates since
         - insertTab modified to put the tab name at the top when solo'ing
    - DelegateWidget needs to sync up with ~/esc for the Tansu Widget
        *   If none selected, show ALL
    - setCurrentIndex?
    - currentIndex?
"""

from qtpy.QtWidgets import (
    QWidget, QListView, QAbstractItemView
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
                |-- TabTansuLabelBarWidget (QWidget)
                        |-- QBoxLayout
                                |-* TabTansuLabelWidget (Label)
                |-- BaseTansuWidget
                        | -- TansuModelDelegateWidget (AbstractGroupBox)
                                | -* Stacked/Dynamic Widget (main_widget)

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

        # create widgets
        new_model = TansuModel()
        default_view_widget = ListView()

        self.setViewWidget(default_view_widget)
        self.setModel(new_model)

        self.main_widget = BaseTansuWidget(self)

        self.addWidget(self.main_widget)
        self.addWidget(self._view_widget)

        # set default attrs
        self.setType(TansuModelViewWidget.TYPE)

        # set direction
        self.setDelegatePosition(direction)

        # set multi
        self.setMultiSelect(TansuModelViewWidget.MULTI)

        self._selected_labels_list = []

    def insertTab(self, index, name, parent=None, widget=None):
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
        if self.getType() == TansuModelViewWidget.STACKED:
            # create tab widget widget
            tab_widget_widget = self.createTansuModelDelegateWidget(name, widget)
            view_item.setDelegateWidget(tab_widget_widget)
            # insert tab widget
            self.main_widget.insertWidget(index, tab_widget_widget)

        # add to view bar
        #self.view_item_bar_widget.insertWidget(index, view_item)

        # update all label index
        #self.__updateAllViewIndexes()

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

    def setViewWidgetToDefaultSize(self):
        """
        Moves the main slider to make the tab label bar the default startup size
        """
        if self.getDelegatePosition() == TansuModelViewWidget.NORTH:
            self.moveSplitter(self.view_height, 1)
        elif self.getDelegatePosition() == TansuModelViewWidget.SOUTH:
            self.moveSplitter(self.height() - self.view_height, 1)
        elif self.getDelegatePosition() == TansuModelViewWidget.WEST:
            self.moveSplitter(self.view_width, 1)
        elif self.getDelegatePosition() == TansuModelViewWidget.EAST:
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
    def getDelegatePosition(self):
        return self._direction

    def setDelegatePosition(self, direction):
        """
        Sets the current direction this widget.  This is the orientation of
        where the tab labels will be vs where the main widget will be, where
        the tab labels bar will always be the first widget.
        """
        self._direction = direction
        self.viewWidget().setParent(None)

        if direction == TansuModelViewWidget.WEST:
            self.setOrientation(Qt.Horizontal)
            self.insertWidget(0, self.viewWidget())

        elif direction == TansuModelViewWidget.EAST:
            self.setOrientation(Qt.Horizontal)
            self.insertWidget(1, self.viewWidget())

        elif direction == TansuModelViewWidget.NORTH:
            self.setOrientation(Qt.Vertical)
            self.insertWidget(0, self.viewWidget())

        elif direction == TansuModelViewWidget.SOUTH:
            self.setOrientation(Qt.Vertical)
            self.insertWidget(1, self.viewWidget())

        # make uncollapsible
        self.setCollapsible(0, False)
        self.setCollapsible(1, False)

    def updateTansuWidget(self, item):
        """
        Determines whether or not an items delegateWidget() should be
        displayed/updated/destroyed.

        item (TansuModelItem)
        """
        # update display
        if not hasattr(item, 'delegateWidget()'): return

        # update static widgets
        if self.getType() == TansuModelViewWidget.STACKED:
            self.__updateStackedDisplay(item)

        # update dynamic widgets
        if self.getType() == TansuModelViewWidget.DYNAMIC:
            self.__updateDynamicDisplay(item)

    def __updateStackedDisplay(self, item):
        if item.is_selected:
            item.delegateWidget().show()
        else:
            try:
                item.delegateWidget().hide()
            except AttributeError:
                pass

    def __updateDynamicDisplay(self, item):
        if item.is_selected:
            # create new dynamic widget...
            new_dynamic_widget = self.createNewDynamicWidget(name=item.text())

            self.main_widget.addWidget(new_dynamic_widget)
            item.setDelegateWidget(new_dynamic_widget)
            self.updateDynamicWidget(new_dynamic_widget, item)
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

    def getDynamicMainWidget(self):
        return self._dynamic_widget

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

    def getMultiSelect(self):
        return self._multi_select

    def setMultiSelectDirection(self, orientation):
        """
        Sets the orientation of the multi select mode.

        orientation (Qt.ORIENTATION): ie Qt.Vertical or Qt.Horizontal
        """
        self.main_widget.setOrientation(orientation)

    def getMultiSelectDirection(self):
        return self.main_widget.orientation()

    """ type """
    def setType(self, value, dynamic_widget=None, dynamic_function=None):
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

            self.dynamic_widget = self.createNewDynamicWidget()
            self.main_widget.addWidget(self.dynamic_widget)

        # update attr
        self._type = value

    def getType(self):
        return self._type

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


class ListView(QListView):
    def __init__(self, parent=None):
        super(ListView, self).__init__(parent)
        self.setEditTriggers(QAbstractItemView.DoubleClicked)

    def selectionChanged(self, selected, deselected):
        top_level_widget = getWidgetAncestor(self, TansuModelViewWidget)
        for index in selected.indexes():
            item = index.internalPointer()
            print(item.name())
            #item.test()
        #return ListView.selectionChanged(self, selected, deselected)


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication, QLabel
    from PyQt5.QtGui import QCursor
    app = QApplication(sys.argv)

    w = TansuModelViewWidget()
    for x in range(3):
        widget = QLabel(str(x))
        w.insertTab(x, str(x),widget=widget)

    w.resize(500,500)
    w.show()

    q = ListView()
    q.show()

    q.setModel(w.model())

    w.move(QCursor.pos())
    sys.exit(app.exec_())

"""
TODO:
    - Default sizes
    - set up colors
    - set up handle widths

"""

from PyQt5.QtWidgets import (
    QWidget, QLabel, QBoxLayout, QStackedLayout, QVBoxLayout, QSizePolicy
)
from PyQt5.QtCore import Qt


from cgwidgets.utils import getWidgetAncestor
from cgwidgets.settings.colors import (
    RGBA_TANSU_HANDLE,
    RGBA_SELECTED,
    RGBA_SELECTED_HOVER
)

try:
    from cgwidgets.BaseTansuWidget import BaseTansuWidget
except ImportError:
    from BaseTansuWidget import BaseTansuWidget


class TansuTabWidget(BaseTansuWidget):
    """
    This is the designing portion of this editor.  This is where the TD
    will design a custom UI/hooks/handlers for the tool for the end user,
    which will be displayed in the ViewWidget

    Args:
        direction (TansuTabWidget.DIRECTION): Determines where the tab
            bar should be placed.  The default value is NORTH
        type (TansuTabWidget.TYPE): What type of tab widget this should be,
            options are STACKED | DYNAMIC | MULTI
            see class attrs for more info...
        selected_labels_list (list): list of labels that are currently selected by the user

    Attributes:
        rgba_handle (rgba): color of the outline for the individual tab labels
            default color is TansuTabWidget.OUTLINE_COLOR
        rgba_selected_tab (rgba): text color of selected tab
            default color is TansuTabWidget.SELECTED_COLOR
        rgba_selected_tab_hover (rgba): text color of tab when hovered over
         TansuTabWidget.SELECTED_COLOR_HOVER

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
                |-- TabLabelBarWidget
                        |-- QBoxLayout
                                |-* TabLabelWidget
                |-- BaseTansuWidget

    """
    NORTH = 'north'
    SOUTH = 'south'
    EAST = 'east'
    WEST = 'west'
    OUTLINE_WIDTH = 1
    OUTLINE_COLOR = RGBA_TANSU_HANDLE
    SELECTED_COLOR = RGBA_SELECTED
    SELECTED_COLOR_HOVER = RGBA_SELECTED_HOVER
    STACKED = 'stacked'
    DYNAMIC = 'dynamic'
    MULTI = False
    TYPE = STACKED

    def __init__(self, parent=None, direction=NORTH):
        super(TansuTabWidget, self).__init__(parent)
        # etc attrs
        self.setHandleWidth(0)
        self._direction = TansuTabWidget.NORTH #just a temp set... for things

        # colors attrs
        self.rgba_handle = TansuTabWidget.OUTLINE_COLOR
        self.rgba_selected_tab = TansuTabWidget.SELECTED_COLOR
        self.rgba_selected_tab_hover = TansuTabWidget.SELECTED_COLOR_HOVER
        style_sheet = """
            QSplitter::handle {
                border: None;
            }
        """
        self.setStyleSheet(style_sheet)

        # create widgets
        self.tab_label_bar_widget = TabLabelBarWidget(self)
        self.main_widget = BaseTansuWidget(self)

        self.addWidget(self.tab_label_bar_widget)
        self.addWidget(self.main_widget)

        # set default attrs
        self.setType(TansuTabWidget.TYPE)
        # self.tab_width = 100
        # self.tab_height = 35

        # set direction
        self.setTabPosition(direction)

        # set multi
        self.setMultiSelect(TansuTabWidget.MULTI)

        self._selected_labels_list = []

    """ UTILS """
    def setTabPosition(self, direction):
        """
        Sets the orientation of the tab bar relative to the main widget.
        This is done by setting the direction on this widget, and then
        setting the layout direction on the tab label bar widget

        Args:
            direction (QVBoxLayout.DIRECTION): The direction that this widget
                should be layed out in.  Where the tab label bar will always be
                the first widget added
        """
        if direction == TansuTabWidget.NORTH:
            self.setDirection(TansuTabWidget.NORTH)
            self.tab_label_bar_widget.layout().setDirection(QBoxLayout.LeftToRight)
        elif direction == TansuTabWidget.SOUTH:
            self.setDirection(TansuTabWidget.SOUTH)
            self.tab_label_bar_widget.layout().setDirection(QBoxLayout.LeftToRight)
        elif direction == TansuTabWidget.EAST:
            self.setDirection(TansuTabWidget.EAST)
            self.tab_label_bar_widget.layout().setDirection(QBoxLayout.TopToBottom)
        elif direction == TansuTabWidget.WEST:
            self.setDirection(TansuTabWidget.WEST)
            self.tab_label_bar_widget.layout().setDirection(QBoxLayout.TopToBottom)
        self.tab_label_bar_widget.setupStyleSheet()

    def insertTab(self, index, widget, name, tab_label=None):
        """
        Creates a new tab at  the specified index

        Args:
            index (int): index to insert widget at
            widget (QWidget): widget to be displayed at that index
            name (str): name of widget
            tab_label (widget): If provided this will use the widget
                provided as a label, as opposed to the default one.
        """

        if self.getType() == TansuTabWidget.STACKED:
            # insert tab widget
            self.main_widget.insertWidget(index, widget)
        # widget.setStyleSheet("""border: 1px solid rgba(0,0,0,255)""")
        # create tab label widget
        if not tab_label:
            tab_label = TabLabelWidget(self, name, index)
        tab_label.tab_widget = widget

        self.tab_label_bar_widget.insertWidget(index, tab_label)

        # update all label index
        self.__updateAllTabLabelIndexes()

    def removeTab(self, index):
        self.tab_label_bar_widget.itemAt(index).widget().setParent(None)
        self.tab_widget_layout.itemAt(index).widget().setParent(None)
        self.__updateAllTabLabelIndexes()

    def __updateAllTabLabelIndexes(self):
        """
        Sets the tab labels index to properly update to its current
        position in the Tab Widget.
        """
        for index, label in enumerate(self.tab_label_bar_widget.getAllLabels()):
            label.index = index

    """ DYNAMIC WIDGET """
    def createNewDynamicWidget(self):
        dynamic_widget_class = self.getDynamicWidgetBaseClass()
        new_widget = dynamic_widget_class()
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
            label (TabLabelWidget): The tab label that should be updated
        """
        # needs to pick which to update...
        self.__dynamicWidgetFunction(widget, label, *args, **kwargs)

    """ EVENTS """
    def showEvent(self, event):
        # super(TansuTabWidget, self).showEvent(event)
        # direction = self.getDirection()
        # all_labels = self.tab_label_bar_widget.getAllLabels()
        #
        # # horizontal
        # if direction in [QBoxLayout.LeftToRight, QBoxLayout.RightToLeft]:
        #     for label in all_labels:
        #         label.setFixedHeight(self.tab_width)
        #     pass
        # # vertical
        # elif direction in [QBoxLayout.TopToBottom, QBoxLayout.BottomToTop]:
        #     for label in all_labels:
        #         label.setFixedWidth(self.tab_height)
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

    def setSelectedLabelsList(self, selected_labels_list):
        self._selected_labels_list = selected_labels_list

    def getSelectedLabelsList(self):
        return self._selected_labels_list

    def appendLabelToList(self, label):
        self.getSelectedLabelsList().append(label)

    def removeLabelFromList(self, label):
        self.getSelectedLabelsList().remove(label)

    """ type """
    def setType(self, value, dynamic_widget=None, dynamic_function=None):
        """
        Sets the type of this widget.  This will reset the entire layout to a blank
        state.

        Args:
            value (TansuTabWidget.TYPE): The type of tab menu that this
                widget should be set to
            dynamic_widget (QWidget): The dynamic widget to be displayed.
            dynamic_function (function): The function to be run when a label
                is selected.
        """
        # reset tab label bar
        if hasattr(self, 'tab_label_bar_widget'):
            self.tab_label_bar_widget.setParent(None)
        self.tab_label_bar_widget = TabLabelBarWidget(self)
        self.insertWidget(0, self.tab_label_bar_widget)

        # clear layout
        self.main_widget.clear()

        # update layout
        if value == TansuTabWidget.STACKED:
            pass
        elif value == TansuTabWidget.DYNAMIC:
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

    """ direction """
    def getDirection(self):
        return self._direction

    def setDirection(self, direction):
        """
        Sets the current direction this widget.  This is the orientation of
        where the tab labels will be vs where the main widget will be, where
        the tab labels bar will always be the first widget.
        """
        self._direction = direction
        self.main_widget.setParent(None)
        self.tab_label_bar_widget.setParent(None)

        if direction == TansuTabWidget.WEST:
            self.addWidget(self.tab_label_bar_widget)
            self.addWidget(self.main_widget)
            self.setOrientation(Qt.Horizontal)
        elif direction == TansuTabWidget.EAST:
            self.addWidget(self.main_widget)
            self.addWidget(self.tab_label_bar_widget)
            self.setOrientation(Qt.Horizontal)
        elif direction == TansuTabWidget.NORTH:
            self.addWidget(self.tab_label_bar_widget)
            self.addWidget(self.main_widget)
            self.setOrientation(Qt.Vertical)
        elif direction == TansuTabWidget.SOUTH:
            self.addWidget(self.main_widget)
            self.addWidget(self.tab_label_bar_widget)
            self.setOrientation(Qt.Vertical)

    """ colors """
    @property
    def rgba_handle(self):
        return self._rgba_handle

    @rgba_handle.setter
    def rgba_handle(self, rgba_handle):
        self._rgba_handle = rgba_handle

    @property
    def rgba_selected_tab(self):
        return self._rgba_selected_tab

    @rgba_selected_tab.setter
    def rgba_selected_tab(self, rgba_selected_tab):
        self._rgba_selected_tab = rgba_selected_tab

    @property
    def rgba_selected_tab_hover(self):
        return self._rgba_selected_tab_hover

    @rgba_selected_tab_hover.setter
    def rgba_selected_tab_hover(self, rgba_selected_tab_hover):
        self._rgba_selected_tab_hover = rgba_selected_tab_hover

    """ not currently in use..."""
    @property
    def tab_width(self):
        return self._tab_width

    @tab_width.setter
    def tab_width(self, tab_width):
        self._tab_width = tab_width

    @property
    def tab_height(self):
        return self._tab_height

    @tab_height.setter
    def tab_height(self, tab_height):
        self._tab_height = tab_height


class TabLabelBarWidget(QWidget):
    """
    The top bar of the Two Faced Design Widget containing all of the tabs
    """
    def __init__(self, parent=None):
        super(TabLabelBarWidget, self).__init__(parent)
        QBoxLayout(QBoxLayout.LeftToRight, self)
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setupStyleSheet()

    def insertWidget(self, index, widget):
        self.layout().insertWidget(index, widget)

    def clearSelectedTabs(self):
        """
        Removes the current tab from being selected
        """
        for index in range(self.layout().count()):
            tab_label = self.layout().itemAt(index).widget()
            tab_label.is_selected = False

    def getAllLabels(self):
        """
        Gets all of the Tab Labels in this bar

        returns (list): of TabLabelWidget
        """
        _all_labels = []
        for index in range(self.layout().count()):
            label = self.layout().itemAt(index).widget()
            _all_labels.append(label)

        return _all_labels

    def setupStyleSheet(self):
        """
        Sets the style sheet for the outline based off of the direction of the parent.

        """
        tab_widget = getWidgetAncestor(self, TansuTabWidget)
        direction = tab_widget.getDirection()
        style_sheet_args = [
            repr(tab_widget.rgba_handle),
            repr(tab_widget.rgba_selected_tab),
            repr(tab_widget.rgba_selected_tab_hover),
            TansuTabWidget.OUTLINE_WIDTH
        ]
        if direction == TansuTabWidget.NORTH:
            style_sheet = """
            QLabel:hover{{color: rgba{2}}}
            QLabel[is_selected=false]{{
                border: {3}px solid rgba{0};
                border-top: None;
                border-left: None;
            }}
            QLabel[is_selected=true]{{
                border: {3}px solid rgba{0} ;
                border-left: None;
                border-bottom: None;
                color: rgba{1};
            }}
            """.format(*style_sheet_args)
        elif direction == TansuTabWidget.SOUTH:
            style_sheet = """
            TabLabelWidget:hover{{color: rgba{2}}}
            TabLabelWidget[is_selected=false]{{
                border: {3}px solid rgba{0};
                border-left: None;
                border-bottom: None;
            }}
            TabLabelWidget[is_selected=true]{{
                border: {3}px solid rgba{0} ;
                border-left: None;
                border-top: None;
                color: rgba{1};
            }}
            """.format(*style_sheet_args)
        elif direction == TansuTabWidget.EAST:
            style_sheet = """
            TabLabelWidget:hover{{color: rgba{2}}}
            TabLabelWidget[is_selected=false]{{
                border: {3}px solid rgba{0};
                border-top: None;
                border-right: None;
            }}
            TabLabelWidget[is_selected=true]{{
                border: {3}px solid rgba{0} ;
                border-top: None;
                border-left: None;
                color: rgba{1};
            }}
            """.format(*style_sheet_args)
        elif direction == TansuTabWidget.WEST:
            style_sheet = """
            TabLabelWidget:hover{{color: rgba{2}}}
            TabLabelWidget[is_selected=false]{{
                border: {3}px solid rgba{0};
                border-top: None;
                border-left: None;
            }}
            TabLabelWidget[is_selected=true]{{
                border: {3}px solid rgba{0} ;
                border-top: None;
                border-right: None;
                color: rgba{1};
            }}
            """.format(*style_sheet_args)
        self.setStyleSheet(style_sheet)


class TabLabelWidget(QLabel):
    """
    This is the tab's tab.

    Attributes:
        is_selected (bool): Determines if this label is currently selected
        tab_widget (widget): The widget that this label correlates to.

    TODO:
        *   Update Font Size dynamically:
                if prefKey == PrefNames.APPLICATION_FONTSIZE
                prefChanged
                self.setFixedHeight(self.height() * 2)
    """
    def __init__(self, parent, text, index):
        super(TabLabelWidget, self).__init__(parent)
        # set up attrs
        self.setText(text)
        self.index = index

        # set up display
        self.setAlignment(Qt.AlignCenter)
        self.is_selected = False
        #TabLabelWidget.setupStyleSheet(self)
        self.setMinimumSize(35, 35)

    # @staticmethod
    # def setupStyleSheet(item):
    #     """
    #     Sets the style sheet for the outline based off of the direction of the parent.
    #
    #     """
    #     tab_widget = getWidgetAncestor(item, TansuTabWidget)
    #     direction = tab_widget.direction
    #     style_sheet_args = [
    #         repr(TansuTabWidget.OUTLINE_COLOR),
    #         repr(TansuTabWidget.SELECTED_COLOR),
    #         TansuTabWidget.OUTLINE_WIDTH
    #     ]
    #     if direction == TansuTabWidget.NORTH:
    #         style_sheet = """
    #         QLabel:hover{{color: rgba{0}}}
    #         QLabel[is_selected=false]{{
    #             border: {2}px solid rgba{0};
    #             border-top: None;
    #             border-left: None;
    #         }}
    #         QLabel[is_selected=true]{{
    #             border: {2}px solid rgba{0} ;
    #             border-left: None;
    #             border-bottom: None;
    #             color: rgba{1};
    #         }}
    #         """.format(*style_sheet_args)
    #     elif direction == TansuTabWidget.SOUTH:
    #         style_sheet = """
    #         QLabel:hover{{color: rgba{0}}}
    #         QLabel[is_selected=false]{{
    #             border: {2}px solid rgba{0};
    #             border-left: None;
    #             border-bottom: None;
    #         }}
    #         QLabel[is_selected=true]{{
    #             border: {2}px solid rgba{0} ;
    #             border-left: None;
    #             border-top: None;
    #             color: rgba{1};
    #         }}
    #         """.format(*style_sheet_args)
    #     elif direction == TansuTabWidget.EAST:
    #         style_sheet = """
    #         QLabel:hover{{color: rgba{0}}}
    #         QLabel[is_selected=false]{{
    #             border: {2}px solid rgba{0};
    #             border-top: None;
    #             border-right: None;
    #         }}
    #         QLabel[is_selected=true]{{
    #             border: {2}px solid rgba{0} ;
    #             border-top: None;
    #             border-left: None;
    #             color: rgba{1};
    #         }}
    #         """.format(*style_sheet_args)
    #     elif direction == TansuTabWidget.WEST:
    #         style_sheet = """
    #         QLabel:hover{{color: rgba{0}}}
    #         QLabel[is_selected=false]{{
    #             border: {2}px solid rgba{0};
    #             border-top: None;
    #             border-left: None;
    #         }}
    #         QLabel[is_selected=true]{{
    #             border: {2}px solid rgba{0} ;
    #             border-top: None;
    #             border-right: None;
    #             color: rgba{1};
    #         }}
    #         """.format(*style_sheet_args)
    #     item.setStyleSheet(style_sheet)

    def mousePressEvent(self, event):
        # get attrs
        top_level_widget = getWidgetAncestor(self, TansuTabWidget)
        is_multi_select = top_level_widget.getMultiSelect()
        modifiers = event.modifiers()

        # set up multi select
        if is_multi_select is True:
            # toggle
            if modifiers == Qt.ControlModifier:
                labels_list = top_level_widget.getSelectedLabelsList()
                if self in labels_list:
                    self.is_selected = False
                    top_level_widget.removeLabelFromList(self)
                else:
                    self.is_selected = True
                    top_level_widget.appendLabelToList(self)
            # reset list
            else:
                TabLabelWidget.__setExclusiveSelect(self)
        # set up single select
        else:
            TabLabelWidget.__setExclusiveSelect(self)

    @staticmethod
    def __setExclusiveSelect(item):
        """
        Sets this to be the ONLY tab selected by the user
        """

        top_level_widget = getWidgetAncestor(item, TansuTabWidget)
        item.parent().clearSelectedTabs()
        item.is_selected = True

        # isolate widget
        if top_level_widget.getType() == TansuTabWidget.STACKED:
            top_level_widget.main_widget.isolateWidgets([item.tab_widget])

        elif top_level_widget.getType() == TansuTabWidget.DYNAMIC:
            top_level_widget.main_widget.clear(exclusion_list=[top_level_widget.dynamic_widget])
            top_level_widget.updateDynamicWidget(top_level_widget.dynamic_widget, item)

        # append to selection list
        top_level_widget.setSelectedLabelsList([item])

    @staticmethod
    def updateDisplay(item):
        """
        Determines whether or not an items tab_widget should be
        displayed/updated/destroyed.
        """
        # update display
        if not hasattr(item, 'tab_widget'): return

        top_level_widget = getWidgetAncestor(item, TansuTabWidget)

        # update static widgets
        if top_level_widget.getType() == TansuTabWidget.STACKED:
            if item.is_selected:
                item.tab_widget.show()
            else:
                item.tab_widget.hide()

        # update dynamic widgets
        if top_level_widget.getType() == TansuTabWidget.DYNAMIC:
            if item.is_selected:
                # create new dynamic widget...
                new_dynamic_widget = top_level_widget.createNewDynamicWidget()
                top_level_widget.main_widget.addWidget(new_dynamic_widget)
                item.tab_widget = new_dynamic_widget
                top_level_widget.updateDynamicWidget(new_dynamic_widget, item)
            else:
                # destroy widget
                item.tab_widget.setParent(None)

    """ PROPERTIES """
    @property
    def is_selected(self):
        return self._is_selected

    @is_selected.setter
    def is_selected(self, is_selected):
        self.setProperty('is_selected', is_selected)
        self._is_selected = is_selected
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

        TabLabelWidget.updateDisplay(self)

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, index):
        self._index = index

    @property
    def tab_widget(self):
        return self._tab_widget

    @tab_widget.setter
    def tab_widget(self, tab_widget):
        self._tab_widget = tab_widget


class DynamicTabWidget(TansuTabWidget):
    def __init__(self, parent=None):
        super(DynamicTabWidget, self).__init__(parent)


class TabDynamicWidgetExample(QWidget):
    def __init__(self, parent=None):
        super(TabDynamicWidgetExample, self).__init__(parent)
        QVBoxLayout(self)
        self.label = QLabel('init')
        self.layout().addWidget(self.label)

    @staticmethod
    def updateGUI(widget, label):
        if label:
            widget.label.setText(label.text())


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtGui import QCursor
    app = QApplication(sys.argv)

    w = TansuTabWidget()

    # stacked widget example
    w.setType(TansuTabWidget.STACKED)
    w.setTabPosition(TansuTabWidget.NORTH)
    w.setMultiSelect(True)
    w.setMultiSelectDirection(Qt.Horizontal)
    #
    # for x in range(3):
    #     nw = QLabel(str(x))
    #     w.insertTab(0, nw, str(x))

    # # dynamic widget example
    #dw = TabDynamicWidgetExample
    w.setType(TansuTabWidget.DYNAMIC, dynamic_widget=TabDynamicWidgetExample, dynamic_function=TabDynamicWidgetExample.updateGUI)

    for x in range(3):
        nw = QLabel(str(x))
        w.insertTab(0, nw, str(x))

    w.show()
    w.move(QCursor.pos())
    sys.exit(app.exec_())

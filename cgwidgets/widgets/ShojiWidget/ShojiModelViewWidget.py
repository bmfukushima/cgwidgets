
from qtpy.QtCore import Qt

from cgwidgets.settings import attrs
from cgwidgets.widgets import (
    AbstractShojiLayout,
    AbstractShojiLayoutHandle,
    AbstractShojiModelViewWidget,
    AbstractShojiModelDelegateWidget)


""" LAYOUT """
class ShojiLayout(AbstractShojiLayout):
    def __init__(self, parent=None, orientation=Qt.Vertical):
        super(ShojiLayout, self).__init__(parent, orientation=orientation)


class ShojiLayoutHandle(AbstractShojiLayoutHandle):
    def __init__(self, orientation, parent=None):
        super(ShojiLayoutHandle, self).__init__(orientation, parent)


class ShojiModelViewWidget(AbstractShojiModelViewWidget):
    """
    The ShojiModelViewWidget ( which needs a better name, potentially "Shoji Widget" )
    is essentially a Tab Widget which replaces the header with either a ListView, or a
    TreeView containing its own internal model.  When the user selects an item in the view, the Delegate, will be updated
    with a widget provided by one of two modes.

    Args:
        direction (ShojiModelViewWidget.DIRECTION): Determines where the tab
            bar should be placed.  The default value is NORTH

    Attributes:
        delegate_type (ShojiModelViewWidget.TYPE): What type of tab widget this should be,
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

    Hierarchy:
        |-- QBoxLayout
            | -- ShojiHeader (BaseShojiWidget)
            |    | -- ViewWidget (ShojiHeaderListView)
            |            ( ShojiHeaderListView | ShojiHeaderTableView | ShojiHeaderTreeView )
            | -- Scroll Area
                |-- DelegateWidget (ShojiMainDelegateWidget --> AbstractOverlayInputWidget)
                        | -- _temp_proxy_widget (QWidget)
                        | -* ShojiModelDelegateWidget (AbstractOverlayInputWidget)
                                | -- AbstractFrameInputWidgetContainer
    """
    def __init__(self, parent=None, direction=attrs.NORTH):
        super(ShojiModelViewWidget, self).__init__(parent, direction=direction)


class ShojiModelDelegateWidget(AbstractShojiModelDelegateWidget):
    def __init__(self, parent=None, title="Title", image_path=None, display_overlay=False):
        super(ShojiModelDelegateWidget, self).__init__(
            parent,
            title=title,
            image_path=image_path,
            display_overlay=display_overlay)


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

    from qtpy.QtGui import QCursor
    app = QApplication(sys.argv)

    """ EXAMPLE """
    class TabShojiDynamicWidgetExample(QWidget):
        """
        TODO:
            turn this into an interface for creating dynamic tab widgets
        """

        def __init__(self, parent=None):
            super(TabShojiDynamicWidgetExample, self).__init__(parent)
            QVBoxLayout(self)
            self.label = QLabel('init')
            self.layout().addWidget(self.label)

        @staticmethod
        def updateGUI(parent, widget, item):
            """
            widget (ShojiModelDelegateWidget)
            item (ShojiModelItem)
            """
            print('update gui')
            # if item:
            #     widget.setTitle(item.name())
            #     widget.getMainWidget().label.setText(item.name())

    shoji_widget = ShojiModelViewWidget()
    shoji_widget.setDelegateType(ShojiModelViewWidget.DYNAMIC, TabShojiDynamicWidgetExample, TabShojiDynamicWidgetExample.updateGUI)
    #w.setHeaderPosition(attrs.WEST, attrs.SOUTH)
    #header_delegate_widget = QLabel("Custom")
    #w.setHeaderDelegateAlwaysOn(False)
    #
    # shoji_widget.setMultiSelect(True)
    #w.setOrientation(Qt.Horizontal)
    # w.setHeaderPosition(attrs.NORTH)
    # w.setMultiSelectDirection(Qt.Horizontal)

    # w.setHeaderItemDragDropMode(QAbstractItemView.InternalMove)
    # delegate_widget = QLabel("Q")
    # w.addHeaderDelegateWidget([Qt.Key_Q], delegate_widget)
    #
    # dw = TabShojiDynamicWidgetExample

    for x in range(3):
        widget = QLabel(str(x))
        parent_item = shoji_widget.insertShojiWidget(x, column_data={'name':str(x), 'one':'test'}, widget=widget)

    for y in range(0, 2):
        shoji_widget.insertShojiWidget(y, column_data={'name':str(y)}, widget=widget, parent=parent_item)
    shoji_widget.setHeaderPosition(attrs.WEST, attrs.SOUTH)
    shoji_widget.setMultiSelectDirection(Qt.Vertical)

    shoji_widget.resize(500, 500)
    shoji_widget.delegateWidget().setHandleLength(100)

    shoji_widget.show()
    # #w.headerWidget().model().setIsDraggable(False)
    # w.setHeaderItemIsDroppable(True)
    # w.setHeaderItemIsDraggable(True)
    # w.setHeaderItemIsEnableable(True)
    # w.setHeaderItemIsDeletable(False)
    shoji_widget.move(QCursor.pos())

    sys.exit(app.exec_())

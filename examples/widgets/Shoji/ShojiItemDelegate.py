"""
Example of how to expand the Shoji Widgets header view to allow dynamic delegates.
This simple example uses a list to display those delegates.

"""

import string
import sys
from qtpy.QtWidgets import QApplication, QLabel, qApp
from qtpy.QtGui import QCursor
from qtpy.QtCore import QPoint

from cgwidgets.widgets import ShojiModelViewWidget, ListInputWidget, OverlayInputWidget
from cgwidgets.views import AbstractDragDropListView, AbstractDragDropModelDelegate
from cgwidgets.utils import getWidgetAncestor, centerWidgetOnCursor, attrs


class ShojiDelegateExample(ShojiModelViewWidget):
    """
    This is the main widget.
    """
    def __init__(self, parent=None):
        super(ShojiDelegateExample, self).__init__(parent)

        # setup header
        events_view = CustomListView(self)
        self.setHeaderViewWidget(events_view)

        # setup as dynamic
        self.setDelegateType(
            ShojiModelViewWidget.DYNAMIC,
            CustomDynamicWidgetExample,
            dynamic_function=CustomDynamicWidgetExample.updateGUI)


class CustomListView(AbstractDragDropListView):
    """
    Custom list view that will have a custom model/item delegate installed on it.
    """
    def __init__(self, parent=None):
        super(CustomListView, self).__init__(parent)
        delegate = CustomModelDelegate(self)
        self.setItemDelegate(delegate)


class CustomModelDelegate(AbstractDragDropModelDelegate):
    """
    Custom model that will have a custom delegate editor for displaying
    the options back to the user as a list.
    """
    def __init__(self, parent=None):
        super(CustomModelDelegate, self).__init__(parent)
        self.setDelegateWidget(ListInputWidget)
        self._parent = parent

    def createEditor(self, parent, option, index):
        """
        Responsible for creating the editor that is displayed
        Args:
            parent (QWidget): parent of the editor that is being returned.
                I think this is constructed on demand?
            option (QStyleOptionViewItem):
            index (QModelIndex):

        Returns:

        """
        # create editor widget
        editor_widget = self.delegateWidget(parent)

        # populate delegate options
        editor_widget.populate([[char] for char in string.ascii_lowercase])

        # set update event
        editor_widget.setUserFinishedEditingEvent(self.delegateUpdate)

        # show popup
        self.__showCompleterPopup(editor_widget, parent)

        # store index being edited...
        self._index = index

        return editor_widget

    def __showCompleterPopup(self, widget, parent):
        """
        Shows the completer popup at a predetermined position/size based off
        of the orientation of the ShojiWidget
        Args:
            widget (QWidget): Editor widget that is being displayed to the user
            parent:
        """
        # get attrs
        shoji_widget = getWidgetAncestor(self._parent, ShojiDelegateExample)
        header_position = shoji_widget.headerPosition()
        pos = parent.mapToGlobal(widget.pos())

        # show
        widget.showCompleter()
        popup = widget.completer().popup()

        # resize
        if header_position in [attrs.NORTH, attrs.SOUTH]:
            popup.setFixedWidth(shoji_widget.delegateWidget().width())
            popup_height = int(shoji_widget.delegateWidget().height() * 0.5)
            popup.setFixedHeight(popup_height)
            if header_position == attrs.NORTH:
                pos.setY(pos.y() + parent.height())
            if header_position == attrs.SOUTH:
                pos.setY(pos.y() - popup_height)

        if header_position in [attrs.EAST, attrs.WEST]:
            popup.setFixedHeight(shoji_widget.delegateWidget().height())
            if header_position == attrs.EAST:
                pos.setX(pos.x() + parent.width())
            if header_position == attrs.WEST:
                pos.setX(pos.x() - parent.width())

        # set popup position
        popup.move(pos)

    def delegateUpdate(self, widget, value):
        print("updating...", widget, value)

        # update static widget
        # static_widget = self._index.internalPointer().delegateWidget().getMainWidget()
        # static_widget.setText(value)

        # update dynamic widget
        main_widget = getWidgetAncestor(self._parent, ShojiDelegateExample)
        self._index.internalPointer().columnData()['name'] = value
        main_widget.updateDelegateDisplay()


class CustomDelegateEditor(ListInputWidget):
    def __init__(self, parent=None):
        super(CustomModelDelegate, self).__init__(parent)


class CustomDynamicWidgetExample(OverlayInputWidget):
    """
    Custom dynamic widget example.  This is a base example of the OverlayInputWidget
    as well.
    """
    def __init__(self, parent=None):
        super(CustomDynamicWidgetExample, self).__init__(parent, title="Hello")
        input_widget = ListInputWidget(self, item_list=[[char] for char in string.ascii_lowercase])
        self.setInputWidget(input_widget)

        # todo update image
        self.setImage("/media/plt01/Downloads_web/awkward.png")

    @staticmethod
    def updateGUI(parent, widget, item):
        """
        parent (ShojiModelViewWidget)
        widget (ShojiModelDelegateWidget)
        item (ShojiModelItem)
        self --> widget.getMainWidget()
        """
        if item:
            name = parent.model().getItemName(item)
            widget.getMainWidget().setTitle(name)

            # todo update image
            widget.getMainWidget().setImage("/media/plt01/Downloads_web/awkward.png")
            from cgwidgets.utils import updateStyleSheet
            updateStyleSheet(widget)


app = QApplication(sys.argv)

main_widget = ShojiDelegateExample()
main_widget.setMultiSelect(True)
main_widget.setHeaderPosition(attrs.SOUTH, attrs.SOUTH)
for char in "SINE.":
    main_widget.insertShojiWidget(0, column_data={'name':char}, widget=QLabel(char))

centerWidgetOnCursor(main_widget)
main_widget.show()

sys.exit(app.exec_())
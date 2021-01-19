import sys
from qtpy.QtWidgets import (
    QApplication, QSplitter, QAbstractItemView, QLabel)
from qtpy.QtGui import QCursor

from cgwidgets.views import (
    AbstractDragDropModel,
    AbstractDragDropTreeView,
    AbstractDragDropListView,
)
from cgwidgets.utils import LayoutOrientation, attrs, getWidgetAncestor
from cgwidgets.settings.colors import iColor
from cgwidgets.widgets import TansuBaseWidget

from qtpy.QtWidgets import QBoxLayout, QWidget
from qtpy.QtCore import Qt


class ModelViewWidget(TansuBaseWidget, LayoutOrientation):
    # orientation
    # type
    # delegate
    def __init__(self, parent=None):
        super(ModelViewWidget, self).__init__(parent)
        #super(Orientation, self).__init__()
        self.layout().addWidget(QLabel('yolo'))
        self.layout().addWidget(QLabel('bolo'))



    """ PROPERTIES """
    def model(self):
        pass

    def setModel(self):
        pass


class TansuHeader(TansuBaseWidget):
    def __init__(self, parent=None):
        super(TansuHeader, self).__init__(parent)

        # default attrs
        self._delegate_always_on = False
        self._delegate_input_keys = [Qt.Key_AsciiTilde, 96]
        self._delegate_input_modifiers = Qt.NoModifier

        # setup style
        self.handle_width = 0
        self.handle_length = 100
        self.rgba_background = iColor["rgba_gray_1"]
        self._view_position = attrs.SOUTH
        self._view_orientation = Qt.Vertical
        self.setContentsMargins(0, 0, 0, 0)

        # setup view
        view = AbstractDragDropListView(self)
        self.setView(view)

        # # TODO setup abstract widget
        # TEMP setup
        abstract_widget = QLabel(":)", parent=self)
        abstract_widget.setStyleSheet("background-color: rgba(0,255,0,255);")
        abstract_widget.setMinimumSize(1, 1)
        abstract_widget.hide()
        #self.addWidget(abstract_widget)

        # setup delegate
        self.setDelegate(abstract_widget)

        # scroll bar moving will need to be setup differently...

        # setup style
        self.setIsSoloViewEnabled(False)
        self.not_soloable = True

    def view(self):
        return self._view

    def setView(self, view):
        if hasattr (self, "_view"):
            self._view.setParent(None)

        # setup attr
        self._view = view
        self._view.not_soloable = True
        self.insertWidget(0, self._view)
        view.setKeyPressEvent(self.keyPressEvent)
        #self.setOrientation(self._view_orientation, view_position=self._view_position)

    """ DELEGATE """
    def delegate(self):
        return self._delegate

    def setDelegate(self, delegate):
        if hasattr(self, "_delegate"):
            self._delegate.setParent(None)
        self._delegate = delegate
        self._delegate.not_soloable = True
        self.addWidget(self._delegate)

    def delegateWidgetAlwaysOn(self):
        return self._delegate_always_on

    def setDelegateWidgetAlwaysOn(self, enabled):
        """
        Flag to determine if the delegate should always be on, or toggled via hotkey
        """
        self._delegate_always_on = enabled

        # hide / show widget
        if enabled:
            self.delegate().show()
        else:
            self.delegate().hide()

    def delegateInputModifiers(self):
        return self._delegate_input_modifiers

    def setDelegateInputModifiers(self, _delegate_input_modifiers):
        self._delegate_input_modifiers = _delegate_input_modifiers

    def delegateInputKeys(self):
        return self._delegate_input_keys

    def setDelegateInputKeys(self, _delegate_input_keys):
        self._delegate_input_keys = _delegate_input_keys

    def toggleDelegateWidget(self, event):
        if self.delegate().isVisible():
            enabled = False
            self.delegate().hide()
        else:
            enabled = True
            self.delegate().show()
            self.delegate().setFocus()

        self.delegateToggleEvent(event, enabled)

    """ DELEGATE VIRTUAL """
    def __delegateToggleEvent(self, event, enabled):
        return

    def delegateToggleEvent(self, event, enabled):
        self.__delegateToggleEvent(event, enabled)
        pass

    def setDelegateToggleEvent(self, function):
        self.__delegateToggleEvent = function

    """ VIEW INTERFACE """
    def model(self):
        return self.view().model()

    def setModel(self, model):
        self.view().setModel(model)

    def setOrientation(self, view_orientation, view_position=None):
        """
        Set the orientation/direction of the header, and view.

        This will determine the flow of the items, from LeftToRight,
        or TopToBottom, depending on the orientation.

        Args:
            view_orientation (Qt.Orientation): The orientation that the view will
                be displayed in.  Note that this is NOT this Tansu widgets
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
        return TansuBaseWidget.setOrientation(self, _orientation)

    def selectionModel(self):
        return self.view().selectionModel()

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
    def keyPressEvent(self, event):
        """
        Note duplicate to view...

         must it be duplicate?
        :param event:
        :return:
        """
        # TODO TOGGLE DELEGATE KEY
        # this is also maintained under... TansuMainDelegateWidget
        #tab_tansu_widget = getWidgetAncestor(self, TansuModelViewWidget)
        modifiers = QApplication.keyboardModifiers()
        if modifiers == self.delegateInputModifiers():
            if event.key() in self.delegateInputKeys():
                if not self.delegateWidgetAlwaysOn():
                    self.toggleDelegateWidget(event)

        return TansuBaseWidget.keyPressEvent(self, event)




app = QApplication(sys.argv)

# create event functions
def testDelete(item):
    print("DELETING --> -->", item.columnData()['name'])

def testDrag(indexes):
    print(indexes)
    print("DRAGGING -->", indexes)

def testDrop(row, indexes, parent):
    print("DROPPING -->", row, indexes, parent)

def testEdit(item, old_value, new_value):
    print("EDITING -->", item, old_value, new_value)

def testEnable(item, enabled):
    print("ENABLING -->", item.columnData()['name'], enabled)

def testSelect(item, enabled):
    print("SELECTING -->", item.columnData()['name'], enabled)

# create model
model = AbstractDragDropModel()

# # create views
# tree_view = AbstractDragDropTreeView()
# tree_view.setModel(model)
#
# list_view = AbstractDragDropListView()
# list_view.setModel(model)
#
# insert indexes
for x in range(0, 4):
    index = model.insertNewIndex(x, name=str('node%s'%x))
    for i, char in enumerate('abc'):
        model.insertNewIndex(i, name=char, parent=index)
#
#
# # set model event
# model.setDragStartEvent(testDrag)
# model.setDropEvent(testDrop)
# model.setTextChangedEvent(testEdit)
# model.setItemEnabledEvent(testEnable)
# model.setItemDeleteEvent(testDelete)
# model.setItemSelectedEvent(testSelect)
#
# # set flags
# tree_view.setIsRootDropEnabled(True)
# tree_view.setIsEditable(True)
# tree_view.setIsDragEnabled(True)
# tree_view.setIsDropEnabled(True)
# tree_view.setIsEnableable(True)
# tree_view.setIsDeleteEnabled(True)
#
# # set selection mode
# tree_view.setSelectionMode(QAbstractItemView.MultiSelection)

###########################################
# new...
###########################################
from qtpy.QtWidgets import QWidget, QVBoxLayout, QPushButton
from qtpy.QtCore import QModelIndex



w = TansuHeader()
print(TansuHeader.__mro__)
w.setModel(model)
w.move(QCursor.pos())
w.show()

###########################################
# end new ...
###########################################

sys.exit(app.exec_())
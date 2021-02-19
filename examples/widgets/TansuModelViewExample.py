"""
The TansuModelViewWidget ( which needs a better name, potentially "Tansu Widget" )
is essentially a Tab Widget which replaces the header with either a ListView, or a
TreeView containing its own internal model.  When the user selects an item in the view, the Delegate, will be updated
with a widget provided by one of two modes.
    Stacked (ezmode):
        All widgets are created upon construction, and they are hidden/shown
        as the user clicks on different items
    Dynamic (notasezmode)
        Widgets are constructed on demand.  These widgets can either be provided
        as one widget to rule them all, or can be provided per item, so that
        sets of items can utilize the same constructors.

Header (ModelViewWidget):
    The header is what is what is usually called the "View" on the ModelView system.
    However, due to how the TansuModelViewWidget works, header is a better term.  This
    header will display the View for the model, along with its own internal delegate
    system that will allow you to register widgets that will popup on Modifier+Key Combos.
    These delegates can be used for multiple purposes, such as setting up filtering of the
    view, item creation, etc.TREE

Delegate (TansuView):
    This is the area that displays the widgets when the user selects different items in the
    header.  If multi select is enabled, AND the user selects multiple items, the delegate
    will display ALL of the widgets to the user.  Any widget can become full screen by pressing
    the ~ key (note that this key can also be set using TansuView.FULLSCREEN_HOTKEY class attr),
    and can leave full screen by pressing the ESC key.  Pressing the ESC key harder will earn you
    epeen points for how awesome you are.  The recommended approach is to use both hands and slam
    them down on the ESC key for maximum effect.  Bonus points are earned if the key board is lifted
    off the ground, other keys fly off the keyboard, and/or people stare at you as you yell FUUCCKKKKKK.
    For those of you to dense to get it, this was a joke, if you didn't get that this was a joke, please
    take a moment here to do one of the following:
        LOL | ROFL | LMAO | HAHAHA

Hierachy
    TansuModelViewWidget --> (QSplitter, iTansuDynamicWidget):
        |-- QBoxLayout
            | -- headerWidget --> ModelViewWidget --> QSplitter
                    |-- view --> (AbstractDragDropListView | AbstractDragDropTreeView) --> QSplitter
                        |-- model --> AbstractDragDropModel
                            |-* AbstractDragDropModelItems
                    |* delegate --> QWidget

            | -- Scroll Area
                |-- DelegateWidget (TansuMainDelegateWidget --> TansuView)
                        | -- _temp_proxy_widget (QWidget)
                        | -* TansuModelDelegateWidget (AbstractGroupBox)
                                | -- Stacked/Dynamic Widget (main_widget)
TODO:
    * custom model / items
    * add model/main widget to virtual events?
        I don't think this is necessary...  Assuming that you can access the
        main widget through some class attr.
"""
import sys

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication, QLabel, QLineEdit, QWidget, QVBoxLayout
from qtpy.QtGui import QCursor

from cgwidgets.widgets import (
    TansuModelViewWidget, TansuModelItem, TansuModel,
    ModelViewWidget, FloatInputWidget, LabelledInputWidget, StringInputWidget)
from cgwidgets.views import TansuView, AbstractDragDropListView, AbstractDragDropTreeView
from cgwidgets.utils import attrs


app = QApplication(sys.argv)


# CREATE MAIN WIDGET
tansu_widget = TansuModelViewWidget()

# SETUP VIEW
"""
Choose between a Tree, List, or Custom view.
By default this will be a LIST_VIEW
"""
def setupCustomView():
    class CustomView(AbstractDragDropListView):
        """
        Can also inherit from
            <AbstractDragDropTreeView>
        """
        def __init__(self):
            super(CustomView, self).__init__()
            pass
    view = CustomView()
    tansu_widget.setHeaderViewWidget(view)

tansu_widget.setHeaderViewType(ModelViewWidget.TREE_VIEW)
#tansu_widget.setHeaderViewType(ModelViewWidget.LIST_VIEW)
#setupCustomView()


# SETUP CUSTOM MODEL
def setupCustomModel():
    class CustomModel(TansuModel):
        def __init__(self, parent=None, root_item=None):
            super(CustomModel, self).__init__(parent, root_item=root_item)

    class CustomModelItem(TansuModelItem):
        def __init__(self, parent=None):
            super(CustomModelItem, self).__init__(parent)

    model = TansuModel()
    item_type = CustomModelItem
    model.setItemType(item_type)
    tansu_widget.setModel(model)

setupCustomModel()


# Set column names
"""
note:
    when providing column data, the key in the dict with the 0th
    index is required, and is the text displayed to the user by default
"""
tansu_widget.setHeaderData(['name', 'SINE.', "woowoo"])

# CREATE ITEMS / TABS
def setupAsStacked():
    # insert tabs

    tansu_widget.insertTansuWidget(0, column_data={'name' : '<title> hello'},
                                   widget=LabelledInputWidget(name='hello', widget_type=FloatInputWidget))
    tansu_widget.insertTansuWidget(0, column_data={'name' : '<title> world'}, widget=QLabel('world'))

    tansu_delegate = TansuView()
    for char in 'SINE.':
        tansu_delegate.addWidget(StringInputWidget(char))
    tansu_delegate_item = tansu_widget.insertTansuWidget(0, column_data={'name' : '<title> tansu'}, widget=tansu_delegate)

    # insert child tabs
    # insert child widgets
    for y in range(0, 2):
        widget = StringInputWidget(str("SINE."))
        tansu_widget.insertTansuWidget(y, column_data={'name': str(y), 'one': 'datttaaa'}, widget=widget, parent=tansu_delegate_item)

def setupAsDynamic():
    class DynamicWidgetExample(QWidget):
        """
        Dynamic widget to be used for the TansuModelViewWidget.  This widget will be shown
        everytime an item is selected in the TansuModelViewWidget, and the updateGUI function
        will be run, every time an item is selected.

        Simple name of overloaded class to be used as a dynamic widget for
        the TansuModelViewWidget.
        """

        def __init__(self, parent=None):
            super(DynamicWidgetExample, self).__init__(parent)
            QVBoxLayout(self)
            self.label = QLabel('init')
            self.layout().addWidget(self.label)

        @staticmethod
        def updateGUI(parent, widget, item):
            """
            parent (TansuModelViewWidget)
            widget (TansuModelDelegateWidget)
            item (TansuModelItem)
            self --> widget.getMainWidget()
            """
            if item:
                print("---- DYNAMIC WIDGET ----")
                print(parent, widget, item)
                name = parent.model().getItemName(item)
                widget.setName(name)
                widget.getMainWidget().label.setText(name)

    class DynamicItemExample(FloatInputWidget):
        """
        Custom widget which has overloaded functions/widget to be
        displayed in the Tansu
        """
        def __init__(self, parent=None):
            super(DynamicItemExample, self).__init__(parent)

        @staticmethod
        def updateGUI(parent, widget, item):
            """
            parent (TansuModelViewWidget)
            widget (TansuModelDelegateWidget)
            item (TansuModelItem)
            self --> widget.getMainWidget()
            """
            print("---- DYNAMIC ITEM ----")
            print(parent, widget, item)
            this = widget.getMainWidget()
            this.setText('whatup')

    # set all items to use this widget
    tansu_widget.setDelegateType(
        TansuModelViewWidget.DYNAMIC,
        dynamic_widget=DynamicWidgetExample,
        dynamic_function=DynamicWidgetExample.updateGUI
    )

    # create items
    for x in range(3):
        name = '<title {}>'.format(str(x))
        tansu_widget.insertTansuWidget(x, column_data={'name': name})

    # insert child tabs
    # insert child widgets
    parent_item = tansu_widget.insertTansuWidget(0, column_data={'name': "PARENT"})
    for y in range(0, 2):
        tansu_widget.insertTansuWidget(y, column_data={'name': str(y), 'one': 'datttaaa'}, parent=parent_item)

    # custom item
    custom_index = tansu_widget.insertTansuWidget(0, column_data={'name': 'Custom Item Widget'})
    custom_index.internalPointer().setDynamicWidgetBaseClass(DynamicItemExample)
    custom_index.internalPointer().setDynamicUpdateFunction(DynamicItemExample.updateGUI)

setupAsStacked()
#setupAsDynamic()

# SET FLAGSLabelledInputWidget
tansu_widget.setMultiSelect(True)
tansu_widget.setMultiSelectDirection(Qt.Vertical)
tansu_widget.delegateWidget().setHandleLength(100)
tansu_widget.setHeaderPosition(attrs.WEST, attrs.SOUTH)
tansu_widget.setDelegateTitleIsShown(True)

#####################################################
# SET EVENT FLAGS
#####################################################
tansu_widget.setHeaderItemIsDropEnabled(True)
tansu_widget.setHeaderItemIsDragEnabled(True)
tansu_widget.setHeaderItemIsEditable(True)
tansu_widget.setHeaderItemIsEnableable(True)
tansu_widget.setHeaderItemIsDeleteEnabled(True)
#select
#toggle
#####################################################
# Setup Virtual Events
#####################################################
def testDrag(items, model):
    """
    Initialized when the drag has started.  This triggers in the mimeData portion
    of the model.

    Args:
        items (list): of TansuModelItems
        model (TansuModel)
    """
    print("---- DRAG EVENT ----")
    print(items, model)

def testDrop(items, model, row, parent):
    """
    Run when the user does a drop.  This is triggered on the dropMimeData funciton
    in the model.

    Args:
        items (list): of TansuModelItems
        model (TansuModel):
        row (int): row item dropped at
        parent (TansuModelItem): parent item that was dropped on

    """
    print("---- DROP EVENT ----")
    print(row, model, items, parent)

def testEdit(item, old_value, new_value):
    print("---- EDIT EVENT ----")
    print(item, old_value, new_value)

def testEnable(item, enabled):
    print('---- ENABLE EVENT ----')
    print(item.columnData()['name'], enabled)

def testDelete(item):
    """

    Args:
        item:
    """
    print('---- DELETE EVENT ----')
    print(item.columnData()['name'])

def testDelegateToggle(event, widget, enabled):
    """

    Args:
        event (QEvent.KeyPress):
        widget (QWidget): widget currently being toggled
        enabled (bool):

    Returns:

    """
    print('---- TOGGLE EVENT ----')
    print (event, widget, enabled)

def testSelect(item, enabled, column=0):
    """
    Handler that is run when the user selects an item in the view.

    Note that this will run for each column in that row.  So in order
    to have this only register once, have it register to the 0 column
    Args:
        item:
        enabled:
        column:
    """
    if column == 0:
        print('---- SELECT EVENT ----')
        print(column, item.columnData(), enabled)


tansu_widget.setHeaderItemEnabledEvent(testEnable)
tansu_widget.setHeaderItemDeleteEvent(testDelete)
tansu_widget.setHeaderDelegateToggleEvent(testDelegateToggle)
tansu_widget.setHeaderItemDragStartEvent(testDrag)
tansu_widget.setHeaderItemDropEvent(testDrop)
tansu_widget.setHeaderItemTextChangedEvent(testEdit)
tansu_widget.setHeaderItemSelectedEvent(testSelect)

#####################################################
# Header Delegates
#####################################################
"""
In the Tree/List view this is a widget that will pop up when
the user presses a specific key/modifier combination
"""
delegate_widget = QLabel("Q")
tansu_widget.addHeaderDelegateWidget([Qt.Key_Q], delegate_widget, modifier=Qt.NoModifier, focus=False)

# display widget
tansu_widget.resize(500, 500)
tansu_widget.show()
tansu_widget.move(QCursor.pos())
sys.exit(app.exec_())
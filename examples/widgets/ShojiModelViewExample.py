"""
The ShojiModelViewWidget ( which needs a better name, potentially "Shoji Widget" )
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
    However, due to how the ShojiModelViewWidget works, header is a better term.  This
    header will display the View for the model, along with its own internal delegate
    system that will allow you to register widgets that will popup on Modifier+Key Combos.
    These delegates can be used for multiple purposes, such as setting up filtering of the
    view, item creation, etc.TREE

Delegate (ShojiView):
    This is the area that displays the widgets when the user selects different items in the
    header.  If multi select is enabled, AND the user selects multiple items, the delegate
    will display ALL of the widgets to the user.  Any widget can become full screen by pressing
    the ~ key (note that this key can also be set using ShojiView.FULLSCREEN_HOTKEY class attr),
    and can leave full screen by pressing the ESC key.  Pressing the ESC key harder will earn you
    epeen points for how awesome you are.  The recommended approach is to use both hands and slam
    them down on the ESC key for maximum effect.  Bonus points are earned if the key board is lifted
    off the desk, and/or keys fly off the keyboard, and/or people stare at you as you yell FUUCCKKKKKK
    as you display your alpha status.  For those of you to dense to get it, this was a joke, if you
    didn't get that this was a joke, please feel free to take a moment here to do one of the following
    so that you feel like you fit in with everyone else:
        LOL | ROFL | LMAO | HAHAHA

Hierachy
    ShojiModelViewWidget --> (QSplitter, iShojiDynamicWidget):
        |-- QBoxLayout
            | -- headerWidget --> ModelViewWidget --> QSplitter
                    |-- view --> (AbstractDragDropListView | AbstractDragDropTreeView) --> QSplitter
                        |-- model --> AbstractDragDropModel
                            |-* AbstractDragDropModelItems
                    |* delegate --> QWidget

            | -- Scroll Area
                |-- DelegateWidget (ShojiMainDelegateWidget --> ShojiView)
                        | -- _temp_proxy_widget (QWidget)
                        | -* ShojiModelDelegateWidget (AbstractGroupBox)
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
    ShojiModelViewWidget, ShojiModelItem, ShojiModel,
    ModelViewWidget, FloatInputWidget, LabelledInputWidget, StringInputWidget)
from cgwidgets.views import ShojiView, AbstractDragDropListView, AbstractDragDropTreeView
from cgwidgets.utils import attrs


app = QApplication(sys.argv)


# CREATE MAIN WIDGET
shoji_widget = ShojiModelViewWidget()

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
    shoji_widget.setHeaderViewWidget(view)

shoji_widget.setHeaderViewType(ModelViewWidget.TREE_VIEW)
#shoji_widget.setHeaderViewType(ModelViewWidget.LIST_VIEW)
#setupCustomView()


# SETUP CUSTOM MODEL
def setupCustomModel():
    class CustomModel(ShojiModel):
        def __init__(self, parent=None, root_item=None):
            super(CustomModel, self).__init__(parent, root_item=root_item)

    class CustomModelItem(ShojiModelItem):
        def __init__(self, parent=None):
            super(CustomModelItem, self).__init__(parent)

    model = ShojiModel()
    item_type = CustomModelItem
    model.setItemType(item_type)
    shoji_widget.setModel(model)

setupCustomModel()


# Set column names
"""
note:
    when providing column data, the key in the dict with the 0th
    index is required, and is the text displayed to the user by default
"""
shoji_widget.setHeaderData(['name', 'SINE.', "woowoo"])

# CREATE ITEMS / TABS
def setupAsStacked():
    # insert tabs
    shoji_widget.setDelegateType(ShojiModelViewWidget.STACKED)
    shoji_widget.insertShojiWidget(0, column_data={'name' : '<title> hello'},
                                   widget=LabelledInputWidget(name='hello', widget_type=FloatInputWidget))
    shoji_widget.insertShojiWidget(0, column_data={'name' : '<title> world'}, widget=QLabel('world'))

    shoji_delegate = ShojiView()
    for char in 'SINE.':
        shoji_delegate.addWidget(StringInputWidget(char))
    shoji_delegate_item = shoji_widget.insertShojiWidget(0, column_data={'name' : '<title> shoji'}, widget=shoji_delegate)

    # insert child tabs
    # insert child widgets
    for y in range(0, 2):
        widget = StringInputWidget(str("SINE."))
        shoji_widget.insertShojiWidget(y, column_data={'name': str(y), 'one': 'datttaaa'}, widget=widget, parent=shoji_delegate_item)

def setupAsDynamic():
    class DynamicWidgetExample(QWidget):
        """
        Dynamic widget to be used for the ShojiModelViewWidget.  This widget will be shown
        everytime an item is selected in the ShojiModelViewWidget, and the updateGUI function
        will be run, every time an item is selected.

        Simple name of overloaded class to be used as a dynamic widget for
        the ShojiModelViewWidget.
        """

        def __init__(self, parent=None):
            super(DynamicWidgetExample, self).__init__(parent)
            QVBoxLayout(self)
            self.label = QLabel('init')
            self.layout().addWidget(self.label)

        @staticmethod
        def updateGUI(parent, widget, item):
            """
            parent (ShojiModelViewWidget)
            widget (ShojiModelDelegateWidget)
            item (ShojiModelItem)
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
        displayed in the Shoji
        """
        def __init__(self, parent=None):
            super(DynamicItemExample, self).__init__(parent)

        @staticmethod
        def updateGUI(parent, widget, item):
            """
            parent (ShojiModelViewWidget)
            widget (ShojiModelDelegateWidget)
            item (ShojiModelItem)
            self --> widget.getMainWidget()
            """
            print("---- DYNAMIC ITEM ----")
            print(parent, widget, item)
            this = widget.getMainWidget()
            this.setText('whatup')

    # set all items to use this widget
    shoji_widget.setDelegateType(
        ShojiModelViewWidget.DYNAMIC,
        dynamic_widget=DynamicWidgetExample,
        dynamic_function=DynamicWidgetExample.updateGUI
    )

    # create items
    for x in range(3):
        name = '<title {}>'.format(str(x))
        shoji_widget.insertShojiWidget(x, column_data={'name': name})

    # insert child tabs
    # insert child widgets
    parent_item = shoji_widget.insertShojiWidget(0, column_data={'name': "PARENT"})
    for y in range(0, 2):
        shoji_widget.insertShojiWidget(y, column_data={'name': str(y), 'one': 'datttaaa'}, parent=parent_item)

    # custom item
    custom_index = shoji_widget.insertShojiWidget(0, column_data={'name': 'Custom Item Widget'})
    custom_index.internalPointer().setDynamicWidgetBaseClass(DynamicItemExample)
    custom_index.internalPointer().setDynamicUpdateFunction(DynamicItemExample.updateGUI)

setupAsStacked()
#setupAsDynamic()

# SET FLAGSLabelledInputWidget
shoji_widget.setMultiSelect(True)

shoji_widget.delegateWidget().setHandleLength(100)
shoji_widget.setHeaderPosition(attrs.WEST, attrs.SOUTH)
shoji_widget.setMultiSelectDirection(Qt.Vertical)
shoji_widget.setDelegateTitleIsShown(True)

#####################################################
# SET EVENT FLAGS
#####################################################
shoji_widget.setHeaderItemIsDropEnabled(True)
shoji_widget.setHeaderItemIsDragEnabled(True)
shoji_widget.setHeaderItemIsEditable(True)
shoji_widget.setHeaderItemIsEnableable(True)
shoji_widget.setHeaderItemIsDeleteEnabled(True)
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
        items (list): of ShojiModelItems
        model (ShojiModel)
    """
    print("---- DRAG EVENT ----")
    print(items, model)

def testDrop(data, items, model, row, parent):
    print("""
DROPPING -->
    data --> {data}
    row --> {row}
    items --> {items}
    model --> {model}
    parent --> {parent}
        """.format(data=data, row=row, model=model, items=items, parent=parent)
          )

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


shoji_widget.setHeaderItemEnabledEvent(testEnable)
shoji_widget.setHeaderItemDeleteEvent(testDelete)
shoji_widget.setHeaderDelegateToggleEvent(testDelegateToggle)
shoji_widget.setHeaderItemDragStartEvent(testDrag)
shoji_widget.setHeaderItemDropEvent(testDrop)
shoji_widget.setHeaderItemTextChangedEvent(testEdit)
shoji_widget.setHeaderItemSelectedEvent(testSelect)

#####################################################
# Header Delegates
#####################################################
"""
In the Tree/List view this is a widget that will pop up when
the user presses a specific key/modifier combination
"""
delegate_widget = QLabel("Q")
shoji_widget.addHeaderDelegateWidget([Qt.Key_Q], delegate_widget, modifier=Qt.NoModifier, focus=False)

# add context menu
def contextMenu(index, selected_indexes):
    print(index, selected_indexes)
    print(index.internalPointer())

shoji_widget.addContextMenuEvent('test', contextMenu)


# display widget
shoji_widget.resize(500, 500)
shoji_widget.show()
shoji_widget.move(QCursor.pos())
sys.exit(app.exec_())
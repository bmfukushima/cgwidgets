import sys
from qtpy.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox)
from qtpy.QtGui import QCursor
from qtpy.QtCore import Qt

from cgwidgets.widgets import (
    FloatInputWidget,
    IntInputWidget,
    StringInputWidget,
    BooleanInputWidget,
    GroupInputWidget,
    ListInputWidget,
    FrameInputWidget,
    FrameGroupInputWidget,
    PlainTextInputWidget
)

app = QApplication(sys.argv)

list_of_crap = [
    ['a', (0, 0, 0, 255)], ['b', (0, 0, 0, 255)], ['c', (0, 0, 0, 255)], ['d', (0, 0, 0, 255)], ['e', (0, 0, 0, 255)],
    ['aa', (255, 0, 0, 255)], ['bb', (0, 255, 0, 255)], ['cc', (0, 0, 255, 255)], ['dd'], ['ee'],
    ['aba'], ['bcb'], ['cdc'], ['ded'], ['efe']
]
l2 = [['a', (255, 0, 0, 255)], ['b'], ['c'], ['aa'], ['bb'], ['cc']]

def createGroupBox(title):
    group_box = QGroupBox()
    group_box.setTitle(title)
    group_box_layout = QVBoxLayout(group_box)
    return group_box

def test(widget, value):
    print("---- user input function ----")
    print('setting value to... ', value)
    print(widget, value)
    #widget.setText(str(value))

""" group insert """
group_widget_layout = QVBoxLayout()
gw = GroupInputWidget(parent=None, title='cool stuff')

# add user inputs
gw.insertInputWidget(0, FloatInputWidget, 'Float', test)
gw.insertInputWidget(0, IntInputWidget, 'Int', test)
gw.insertInputWidget(0, BooleanInputWidget, 'Boolean', test)
gw.insertInputWidget(0, StringInputWidget, 'String', test)
gw.insertInputWidget(0, ListInputWidget, 'List', test, data={'items_list':list_of_crap})
gw.insertInputWidget(0, PlainTextInputWidget, 'Text', test)

gw.display_background = False
group_widget_layout.addWidget(gw)

""" normal widgets """
normal_widget = createGroupBox("Normal Widgets")

float_input_widget = FloatInputWidget()
float_input_widget.setUseLadder(True)
int_input_widget = IntInputWidget()
int_input_widget.setUseLadder(True, value_list=[1, 2, 3, 4, 5])
boolean_input_widget = BooleanInputWidget()
string_input_widget = StringInputWidget()
list_input_widget = ListInputWidget(item_list=list_of_crap)
plain_text_input_widget = PlainTextInputWidget()

normal_widget.layout().addWidget(float_input_widget)
normal_widget.layout().addWidget(int_input_widget)
normal_widget.layout().addWidget(boolean_input_widget)
normal_widget.layout().addWidget(string_input_widget)
normal_widget.layout().addWidget(list_input_widget)
normal_widget.layout().addWidget(plain_text_input_widget)

float_input_widget.setUserFinishedEditingEvent(test)
int_input_widget.setUserFinishedEditingEvent(test)
boolean_input_widget.setUserFinishedEditingEvent(test)
string_input_widget.setUserFinishedEditingEvent(test)
list_input_widget.setUserFinishedEditingEvent(test)
plain_text_input_widget.setUserFinishedEditingEvent(test)

""" Labeled Widgets """
def createLabeledWidgets(title, direction=Qt.Horizontal):
    """
    Creates a GroupBox with label widgets inside of it

    Args:
        direction (Qt.DIRECTION): what direction the input widgets should be
            laid out in

    Returns (QGroupBox)

    Widgets:
        GroupBox
            | -- VBox
                    | -* FrameInputWidget
    """
    label_widgets = {
        "float": FloatInputWidget,
        "int": IntInputWidget,
        "bool": BooleanInputWidget,
        "str": StringInputWidget,
        "list": ListInputWidget,
        "text": PlainTextInputWidget
    }

    """ Label widgets"""
    group_label_widget = createGroupBox(title)

    for arg in label_widgets:
        # create widget
        widget_type = label_widgets[arg]
        input_widget = FrameInputWidget(name=arg, widget_type=widget_type)

        # set widget orientation
        input_widget.setDirection(direction)

        # set separator
        if direction == Qt.Horizontal:
            input_widget.setDefaultLabelLength(125)
        input_widget.setSeparatorLength(100)
        input_widget.setSeparatorWidth(3)

        # add to group layout
        group_label_widget.layout().addWidget(input_widget)

        # connect user input
        input_widget.setUserFinishedEditingEvent(test)

        # list override
        if arg == "list":
            input_widget.getInputWidget().populate(list_of_crap)
            input_widget.getInputWidget().display_item_colors = True

    return group_label_widget


horizontal_label_widget = createLabeledWidgets("Frame Widgets ( Horizontal )", Qt.Horizontal)
vertical_label_widget = createLabeledWidgets("Frame Widgets ( Vertical )", Qt.Vertical)

""" Group Widget"""
frame_group_input_widget = FrameGroupInputWidget(name='Frame Input Widgets', direction=Qt.Vertical)

# set header editable / Display
frame_group_input_widget.setIsHeaderEditable(True)
frame_group_input_widget.setIsHeaderShown(True)

# Add widgets
label_widgets = {
        "float": FloatInputWidget,
        "int": IntInputWidget,
        "bool": BooleanInputWidget,
        "str": StringInputWidget,
        "list": ListInputWidget,
        "text": PlainTextInputWidget
    }

for arg in label_widgets:
    # create widget
    widget_type = label_widgets[arg]
    input_widget = FrameInputWidget(name=arg, widget_type=widget_type)

    # set widget orientation
    input_widget.setDirection(Qt.Horizontal)

    # add to group layout
    frame_group_input_widget.addInputWidget(input_widget, finished_editing_function=test)

    # list override
    if arg == "list":
        input_widget.getInputWidget().populate(list_of_crap)
        input_widget.getInputWidget().display_item_colors = True


""" Main Widget"""
main_widget = QWidget()
main_layout = QHBoxLayout(main_widget)
main_layout.addLayout(group_widget_layout)
main_layout.addWidget(normal_widget)
main_layout.addWidget(vertical_label_widget)
main_layout.addWidget(horizontal_label_widget)
main_layout.addWidget(frame_group_input_widget)

main_widget.resize(500, 500)
main_widget.show()
main_widget.move(QCursor.pos())



sys.exit(app.exec_())

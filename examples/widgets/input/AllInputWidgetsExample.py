import sys, os
#os.environ['QT_API'] = 'pyside2'
from qtpy.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QSplitter)
from qtpy.QtGui import QCursor
from qtpy.QtCore import Qt

from cgwidgets.settings.colors import iColor
from cgwidgets.widgets import (
    ButtonInputWidget,
    FloatInputWidget,
    IntInputWidget,
    StringInputWidget,
    BooleanInputWidget,
    ShojiInputWidgetContainer,
    ListInputWidget,
    LabelledInputWidget,
    FrameInputWidgetContainer,
    OverlayInputWidget,
    PlainTextInputWidget,
    ButtonInputWidgetContainer
)

from __CreateFrame__ import createFrame

app = QApplication(sys.argv)

list_of_crap = [
    ['a', (0, 0, 0, 255)], ['b', (0, 0, 0, 255)], ['c', (0, 0, 0, 255)], ['d', (0, 0, 0, 255)], ['e', (0, 0, 0, 255)],
    ['aa', (255, 0, 0, 255)], ['bb', (0, 255, 0, 255)], ['cc', (0, 0, 255, 255)], ['dd'], ['ee'],
    ['aba'], ['bcb'], ['cdc'], ['ded'], ['efe']
]
l2 = [['a', (255, 0, 0, 255)], ['b'], ['c'], ['aa'], ['bb'], ['cc']]

def test(widget, value):
    print("---- user input function ----")
    print('setting value to... ', value)
    print(widget, value)
    #widget.setText(str(value))

def shojiInputTest(widget, value):
    print("---- SHOJI input function ----")
    print('setting value to... ', value)
    print(widget, value)
    # widget.setText(str(value))

def fail():
    print("fail")


""" normal widgets """
normal_widget = createFrame("Normal Widgets")

float_input_widget = FloatInputWidget()
float_input_widget.setUseLadder(True)
int_input_widget = IntInputWidget()
int_input_widget.setUseLadder(True, value_list=[1, 2, 3, 4, 5])
boolean_input_widget = BooleanInputWidget(text="yellow")
string_input_widget = StringInputWidget()
list_input_widget = ListInputWidget(item_list=list_of_crap)
plain_text_input_widget = PlainTextInputWidget()
overlay_input_widget = OverlayInputWidget(delegate_widget=StringInputWidget(), title="SINE.")
def userEvent(widget):
    print("user input...", widget)

button_input_widget_container = ButtonInputWidgetContainer(orientation=Qt.Vertical)
button_input_widget_container.setIsMultiSelect(True)
for flag in range(3):
    if flag == 1:
        button_input_widget_container.addButton("button_" + str(flag), flag, userEvent, True)
    else:
        button_input_widget_container.addButton("button_" + str(flag), flag, userEvent, False)

button_input_widget = ButtonInputWidget(user_clicked_event=userEvent, title="Script Button", flag=False, is_toggleable=False)


normal_widget.layout().addWidget(float_input_widget)
normal_widget.layout().addWidget(int_input_widget)
normal_widget.layout().addWidget(boolean_input_widget)
normal_widget.layout().addWidget(string_input_widget)
normal_widget.layout().addWidget(list_input_widget)
normal_widget.layout().addWidget(plain_text_input_widget)
normal_widget.layout().addWidget(overlay_input_widget)
normal_widget.layout().addWidget(button_input_widget_container)
normal_widget.layout().addWidget(button_input_widget)

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
                    | -* LabelledInputWidget
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
    group_label_widget = createFrame(title)

    for arg in label_widgets:
        # create widget
        delegate_widget = label_widgets[arg]()
        input_widget = LabelledInputWidget(name=arg, delegate_widget=delegate_widget)

        # set widget orientation
        input_widget.setDirection(direction)

        # # set separator
        # if direction == Qt.Horizontal:
        #     input_widget.setDefaultLabelLength(100)
        #     input_widget.setSeparatorWidth(30)
        # elif direction == Qt.Vertical:
        #     input_widget.setDefaultLabelLength(30)

        input_widget.setSeparatorLength(35)

        # add to group layout
        group_label_widget.layout().addWidget(input_widget)

        # connect user input
        input_widget.setUserFinishedEditingEvent(test)

        # list override
        if arg == "list":
            input_widget.delegateWidget().populate(list_of_crap)
            input_widget.delegateWidget().display_item_colors = True

    return group_label_widget


horizontal_label_widget = createLabeledWidgets("Frame Widgets ( Horizontal )", Qt.Horizontal)
vertical_label_widget = createLabeledWidgets("Frame Widgets ( Vertical )", Qt.Vertical)

""" Group Widget"""
frame_group_input_widget = FrameInputWidgetContainer(title='Frame Input Widgets', direction=Qt.Vertical)

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
    delegate_widget = label_widgets[arg]()
    input_widget = LabelledInputWidget(name=arg, delegate_widget=delegate_widget)

    # set widget orientation
    input_widget.setDirection(Qt.Horizontal)

    # add to group layout
    frame_group_input_widget.addInputWidget(input_widget, finished_editing_function=test)

    # list override
    if arg == "list":
        input_widget.delegateWidget().populate(list_of_crap)
        input_widget.delegateWidget().display_item_colors = True

""" Shoji Input Widget Container """
shoji_input_widget_container = ShojiInputWidgetContainer(name='ShojiInputWidgetContainer')

# add user inputs
shoji_input_widget_container.insertInputWidget(0, BooleanInputWidget, 'Boolean', shojiInputTest)
shoji_input_widget_container.insertInputWidget(0, StringInputWidget, 'String', shojiInputTest)
shoji_input_widget_container.insertInputWidget(0, IntInputWidget, 'Int', shojiInputTest)
shoji_input_widget_container.insertInputWidget(0, FloatInputWidget, 'Float', shojiInputTest)
shoji_input_widget_container.insertInputWidget(0, ListInputWidget, 'List', shojiInputTest, data={'items_list':list_of_crap})
shoji_input_widget_container.insertInputWidget(0, PlainTextInputWidget, 'Text', shojiInputTest)

shoji_input_widget_container.display_background = False

""" Main Widget"""

main_widget = QSplitter()
main_widget.setStyleSheet("""background-color: rgba{rgba_background_00}""".format(**iColor.style_sheet_args))

main_widget.addWidget(normal_widget)
main_widget.addWidget(vertical_label_widget)
main_widget.addWidget(horizontal_label_widget)
main_widget.addWidget(shoji_input_widget_container)
main_widget.addWidget(frame_group_input_widget)


main_widget.resize(500, 500)
main_widget.show()
main_widget.move(QCursor.pos())



sys.exit(app.exec_())



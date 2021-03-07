import sys
from qtpy.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QSplitter)
from qtpy.QtGui import QCursor
from qtpy.QtCore import Qt

from cgwidgets.settings.colors import iColor

from cgwidgets.widgets import (
    ShojiModelViewWidget,
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

app = QApplication(sys.argv)

list_of_crap = [
    ['a', (0, 0, 0, 255)], ['b', (0, 0, 0, 255)], ['c', (0, 0, 0, 255)], ['d', (0, 0, 0, 255)], ['e', (0, 0, 0, 255)],
    ['aa', (255, 0, 0, 255)], ['bb', (0, 255, 0, 255)], ['cc', (0, 0, 255, 255)], ['dd'], ['ee'],
    ['aba'], ['bcb'], ['cdc'], ['ded'], ['efe']
]
l2 = [['a', (255, 0, 0, 255)], ['b'], ['c'], ['aa'], ['bb'], ['cc']]

def userEvent(widget, value):
    print("---- user input function ----")
    print('setting value to... ', value)
    print(widget, value)
    #widget.setText(str(value))

""" Shoji Input Widget Container """
shoji_input_widget_container = ShojiInputWidgetContainer(parent=None, name='ShojiInputWidgetContainer')

# add user inputs
shoji_input_widget_container.insertInputWidget(0, FloatInputWidget, 'Float', userEvent)
shoji_input_widget_container.insertInputWidget(0, IntInputWidget, 'Int', userEvent)
shoji_input_widget_container.insertInputWidget(0, BooleanInputWidget, 'Boolean', userEvent)
shoji_input_widget_container.insertInputWidget(0, StringInputWidget, 'String', userEvent)
shoji_input_widget_container.insertInputWidget(0, ListInputWidget, 'List', userEvent, data={'items_list':list_of_crap})
shoji_input_widget_container.insertInputWidget(0, PlainTextInputWidget, 'Text', userEvent)

shoji_input_widget_container.display_background = False


""" BUTTON INPUT WIDGET CONTAINER """
def userEvent(widget):
    print("user input...", widget)
buttons = []
for x in range(3):
    flag = x
    buttons.append(["button_" + str(x), flag, userEvent])
button_input_widget_container = ButtonInputWidgetContainer(buttons=buttons, orientation=Qt.Vertical)


""" FRAME INPUT WIDGET CONTAINER"""
frame_input_widget_container = FrameInputWidgetContainer(name='Frame Input Widgets', direction=Qt.Vertical)

# set header editable / Display
frame_input_widget_container.setIsHeaderEditable(True)
frame_input_widget_container.setIsHeaderShown(True)

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
    input_widget = LabelledInputWidget(name=arg, widget_type=widget_type)

    # set widget orientation
    input_widget.setDirection(Qt.Horizontal)

    # add to group layout
    frame_input_widget_container.addInputWidget(input_widget, finished_editing_function=userEvent)

    # list override
    if arg == "list":
        input_widget.getInputWidget().populate(list_of_crap)
        input_widget.getInputWidget().display_item_colors = True


""" Main Widget"""
main_widget = ShojiModelViewWidget()
main_widget.setStyleSheet("""background-color: rgba{rgba_background_00}""".format(**iColor.style_sheet_args))
main_widget.insertShojiWidget(0, column_data={'name':'Shoji Container'}, widget=shoji_input_widget_container)
main_widget.insertShojiWidget(0, column_data={'name':'Button Container'}, widget=button_input_widget_container)
main_widget.insertShojiWidget(0, column_data={'name':'Frame Container'}, widget=frame_input_widget_container)


main_widget.resize(500, 500)
main_widget.show()
main_widget.move(QCursor.pos())



sys.exit(app.exec_())



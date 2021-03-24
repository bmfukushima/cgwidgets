"""
The Labelled Input Widget provides a convenient way of mapping a name/title to an input widget.
"""

import sys
from qtpy.QtWidgets import QApplication, QWidget, QHBoxLayout
from qtpy.QtGui import QCursor
from qtpy.QtCore import Qt

from cgwidgets.widgets import (
    LabelledInputWidget,
    FloatInputWidget,
    FrameInputWidgetContainer,
    BooleanInputWidget)

app = QApplication(sys.argv)

def createFrame(name, widget):
    """
    Creates a container to hold the overlay widgets with a display label on them
    Args:
        name (str): title of the widget
        widget (OverlayInputWidget): to be displayed

    Returns (FrameInputWidgetContainer)
    """
    frame_group_input_widget = FrameInputWidgetContainer(title=name, direction=Qt.Vertical)

    # set header editable / Display
    frame_group_input_widget.setIsHeaderEditable(False)
    frame_group_input_widget.setIsHeaderShown(True)
    frame_group_input_widget.addInputWidget(widget)
    return frame_group_input_widget

class CustomLabelledInputWidget(LabelledInputWidget):
    """
    A single input widget.  This inherits from the ShojiLayout,
    to provide a slider for the user to expand/contract the editable area
    vs the view label.

    Args:
        name (str):
        note (str):
        direction (Qt.ORIENTATION):
        default_label_length (int): default length to display labels when showing this widget
        delegate_widget (QWidget): Widget type to be constructed for as the delegate widget

    Hierarchy:
        |- ViewWidget --> AbstractOverlayInputWidget
        |- DelegateWidget --> QWidget

    Note:
        Needs parent to be provided in order for the default size to be
        displayed correctly

    """
    def __init__(
        self,
        parent=None,
        name="None",
        note="None",
        direction=Qt.Horizontal,
        default_label_length=50,
        delegate_widget=None
    ):
        super(CustomLabelledInputWidget, self).__init__(
            parent,
            name=name,
            note=note,
            default_label_length=default_label_length,
            direction=direction,
            delegate_widget=delegate_widget
        )

# Args
args_labelled_widget = LabelledInputWidget(
    name="Args",
    note="This is a note",
    direction=Qt.Vertical,
    default_label_length=50,
    delegate_widget=FloatInputWidget())
args_widget = createFrame("Args", args_labelled_widget)

# setters
setters_labelled_widget = LabelledInputWidget()
setters_labelled_widget.setName("Name")
setters_labelled_widget.setDirection(Qt.Vertical)
setters_labelled_widget.setDelegateWidget(BooleanInputWidget())
setters_labelled_widget.setDefaultLabelLength(125)

setters_widget = createFrame("Setters", setters_labelled_widget)

# subclass
subclass_widget = createFrame("SubClass", CustomLabelledInputWidget())

# create main widget
main_widget = QWidget()
main_layout = QHBoxLayout(main_widget)

# add widgets to layout
main_layout.addWidget(args_widget)
main_layout.addWidget(setters_widget)
main_layout.addWidget(subclass_widget)

# show main widget
main_widget.move(QCursor.pos())
main_widget.show()
main_widget.resize(500, 500)

sys.exit(app.exec_())
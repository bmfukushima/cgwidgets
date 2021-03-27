"""
The Labelled Input Widget provides a convenient way of mapping a name/title to an input widget.
"""

import sys
from qtpy.QtWidgets import QApplication, QWidget, QHBoxLayout
from qtpy.QtGui import QCursor
from qtpy.QtCore import Qt

from cgwidgets.widgets import (
    LabelledInputWidget,
    OverlayInputWidget,
    FloatInputWidget,
    BooleanInputWidget)

from cgwidgets.settings.colors import iColor
from cgwidgets.settings.icons import icons
from __CreateFrame__ import createFrame

app = QApplication(sys.argv)

# Subclass
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
        delegate_widget (QWidget): instance of widget to use as delegate
        delegate_constructor (QWidget): constructor to use as delegate widget.  This will automatically
            be overwritten by the delegate_widget if it is provided.
        widget_type (QWidget): Widget type to be constructed for as the delegate widget

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
        delegate_widget=None,
        delegate_constructor=None,
    ):
        super(CustomLabelledInputWidget, self).__init__(
            parent,
            name=name,
            note=note,
            default_label_length=default_label_length,
            direction=direction,
            delegate_widget=delegate_widget,
            delegate_constructor=delegate_constructor
        )

# Args
args_labelled_widget = LabelledInputWidget(
    name="Args",
    note="This is a note",
    direction=Qt.Vertical,
    default_label_length=50,
    # delegate_widget=FloatInputWidget(), # will override the delegate_constructor
    delegate_constructor=FloatInputWidget)
args_widget = createFrame("Args", args_labelled_widget)


# Setters
setters_labelled_widget = LabelledInputWidget()
setters_labelled_widget.setName("Name")
setters_labelled_widget.setDirection(Qt.Vertical)
setters_labelled_widget.setDelegateWidget(BooleanInputWidget())
setters_labelled_widget.setDefaultLabelLength(75)

# Setters view widget
"""
After accessing the viewWidget, you can use all of the functions provided by the OverlayInputWidget
"""
setters_view_widget = setters_labelled_widget.viewWidget()
setters_view_widget.setTextColor(iColor["rgba_green_7"])
setters_view_widget.setImage(icons["example_image_01"])
setters_view_widget.setDisplayMode(OverlayInputWidget.ENTER)
def hideViewDelegateEvent(widget, delegate_widget):
    print('---- HIDE VIEW DELEGATE EVENT ----')
    print(widget, delegate_widget.text())
setters_view_widget.setHideDelegateEvent(hideViewDelegateEvent)

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
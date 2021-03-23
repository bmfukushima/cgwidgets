"""
The OverlayInputWidget is a widget that is essentially two widgets stacked on top of each other.  The purpose of this
widget is to make it so that more complex widgets can be hidden from view while not active, thus reducing the amount
of visual stimuli.  The reason that this is necessary is that more often than not a giant cluster fuck of data is
presented to the user, which often overloads what they are looking for.  Using the OverlayInputWidget will enable
the developer to categorize parameters that the user should be adjusting, and easily display that category to a user
either using TEXT or an IMAGE.

The two widgets in the OverlayInputWidget are called the "view" and the "delegate".  The VIEW will be what is shown
to the user when the widget is in an inactive, and the delegate will be shown to the user when the widget is active.  These
widgets are available with the getters/setters delegateWidget/setDelegateWidget, and viewWidget/setViewWidget.

The widget can be activated by setting the display mode using "setDisplayMode" and setting it to
    OverlayInputWidget.RELEASE | DISABLE | ENTER
"""

import sys, inspect
from qtpy.QtWidgets import QApplication, QWidget, QHBoxLayout
from qtpy.QtCore import Qt
from qtpy.QtGui import QCursor
from cgwidgets.widgets import BooleanInputWidget, OverlayInputWidget, FrameInputWidgetContainer
from cgwidgets.settings.icons import icons

app = QApplication(sys.argv)

# subclass
class SubclassOverlayInputWidget(OverlayInputWidget):
    """
    Input widget with a display delegate overlaid.  This delegate will dissapear
    when the user first hover enters.

    Args:
        input_widget (QWidget): Widget for user to input values into
        title (string): Text to display when the widget is shown
            for the first time.

    Attributes:
        input_widget:
        overlay_widget:
    """
    def __init__(
            self,
            parent=None,
            delegate_widget=None,
            image=None,
            title="",
            display_mode=OverlayInputWidget.RELEASE
    ):
        super(SubclassOverlayInputWidget, self).__init__(
            parent,
            delegate_widget=delegate_widget,
            image=image,
            title=title,
            display_mode=display_mode)

# create containers
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


# Create Overlay Widgets

# create event functions
def hideDelegateEvent(widget):
    print('---- HIDE ----')
    print(widget)

def showDelegateEvent(widget):
    print("---- SHOW ----")
    print(widget)

# default
overlay_widget_default = OverlayInputWidget(title="Title")
default_widget = createFrame("Default", overlay_widget_default)

# with input args
overlay_widget_args = OverlayInputWidget(
    title="Args",
    display_mode=OverlayInputWidget.RELEASE,
    delegate_widget=BooleanInputWidget(text="yolo"),
    image_path=icons["example_image_02"])

args_widget = createFrame("Args", overlay_widget_args)


# with setters
overlay_widget_setters = OverlayInputWidget()
overlay_widget_setters.setDisplayMode(OverlayInputWidget.ENTER)
overlay_widget_setters.setTitle("Setters")
overlay_widget_setters.setImage(icons["example_image_01"])

# set delegate widget
overlay_widget_setters.setDelegateWidget(BooleanInputWidget(text="yolo"))

# set virtual events
overlay_widget_setters.setHideDelegateEvent(hideDelegateEvent)
overlay_widget_setters.setShowDelegateEvent(showDelegateEvent)

#overlay_widget_setters.showImage(False)
overlay_widget_setters.setImageResizeMode(Qt.IgnoreAspectRatio)
overlay_widget_setters.setTextColor((0, 255, 0, 255))

# create frame
setters_widget = createFrame("Setters", overlay_widget_setters)


# create main widget
main_widget = QWidget()
main_layout = QHBoxLayout(main_widget)

# add overlay widgets
main_layout.addWidget(default_widget)
main_layout.addWidget(args_widget)
main_layout.addWidget(setters_widget)

# show main widget
main_widget.move(QCursor.pos())
main_widget.show()
main_widget.resize(500, 500)
main_widget.show()

sys.exit(app.exec_())


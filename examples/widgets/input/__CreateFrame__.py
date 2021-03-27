from qtpy.QtCore import Qt
from cgwidgets.widgets import FrameInputWidgetContainer

def createFrame(name, widget=None):
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
    if widget:
        frame_group_input_widget.addInputWidget(widget)
    return frame_group_input_widget
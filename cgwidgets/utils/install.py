from qtpy.QtWidgets import *
from qtpy.QtCore import *
from qtpy.QtGui import *


def installInvisibleCursorEvent(widget):
    """
    Installs an event filter on the widget that makes it so that when the
    user click/drags, it will turn the cursor invisible, and all the cursor
    to move an infinite distance.  On release, it will return the cursor
    back to the starting position

    Args:
        widget (QWidget): Widget to install the invisible drag event on

    Returns:
        (InvisibleCursorEvent): QWidget which holds the event
            filter for the invisible drag event
    """
    from cgwidgets.events import InvisibleCursorEvent
    invis_drag_filter = InvisibleCursorEvent(parent=widget)
    widget.installEventFilter(invis_drag_filter)

    return invis_drag_filter


def installInvisibleWidgetEvent(widget, hide_widget=None):
    """
    Installs an event filter on the widget that makes it so that when the
    user click/drags, it will turn the cursor invisible, and all the cursor
    to move an infinite distance.  On release, it will return the cursor
    back to the starting position

    Args:

    Returns:
    """
    from cgwidgets.events import InvisibleWidgetEvent

    # ensure defaults for hide widget
    if hide_widget is None:
        hide_widget = widget

    # install event filter
    invis_cursor_filter = InvisibleWidgetEvent(
        parent=widget, hide_widget=hide_widget
    )
    widget.installEventFilter(invis_cursor_filter)

    return invis_cursor_filter


def installSlideDelegate(
        widget,
        sliderPosMethod,
        breed=None,
        display_widget=None
    ):
    """
    Args:
        widget (QWidget): the PyQt widget to install this delegate
            on to.
        getSliderPos (method): returns the position of the slider
            as a percentage (0-1)
            Returns:
                (float): 0-1
    Kwargs:
        breed (cgwidgets.delegate.SliderDelegate.breed): what type
            of slide display to show to the user.  Appropriate values are
            Unit, Hue, Sat, Val
    Returns:
        SlideDelegate
    """
    from cgwidgets.delegates import SlideDelegate
    # set up default slide display type
    if breed is None:
        breed = 0

    slide_delegate = SlideDelegate(
        parent=widget,
        getSliderPos=sliderPosMethod,
        breed=breed,
        display_widget=display_widget
    )
    widget._dragging = False
    widget._slider_pos = 0.0
    widget.installEventFilter(slide_delegate)
    return slide_delegate


def removeSlideDelegate(item, slide_delegate):
    item.removeEventFilter(slide_delegate)


def installLadderDelegate(
    widget,
    user_input=QEvent.MouseButtonRelease,
    value_list=[0.001, 0.01, 0.1, 1, 10, 100, 1000]
):
    """
    Args:
        widget: <QLineEdit> or <QLabel>
            widget to install ladder delegate onto.  Note this currently
            works for QLineEdit and QLabel.  Other widgets will need
            to implement a 'setValue(value)' method on which sets the
            widgets value.
    Kwargs:
        user_input: <QEvent>
            user event that triggers the popup of the Ladder Delegate
        value_list: <list> of <float>
            list of values for the user to be able to adjust by, usually this
            is set to .01, .1, 1, 10, etc
        display_widget (QWidget): optional argument.  If entered, the display
            will show up over that widget rather than over the main display.
    Returns:
        LadderDelegate
    """
    from cgwidgets.delegates import LadderDelegate
    ladder = LadderDelegate(
        parent=widget,
        value_list=value_list,
        user_input=user_input
    )
    widget.installEventFilter(ladder)
    return ladder
#

def installStickyValueAdjustWidgetDelegate(
        widget, pixels_per_tick=100, value_per_tick=0.01
    ):
    from cgwidgets.delegates import StickyValueAdjustWidgetDelegate

    widget.setMouseTracking(True)
    event_filter = StickyValueAdjustWidgetDelegate(widget)
    event_filter.setPixelsPerTick(pixels_per_tick)
    event_filter.setValuePerTick(value_per_tick)

    widget.installEventFilter(event_filter)
    return event_filter


def installStickyValueAdjustItemDelegate(
        item, pixels_per_tick=100, value_per_tick=0.01
    ):
    """
    Installs a delegate on the widget which makes it so when the user clicks.
    It will hide the cursor and allow the user to move the mouse around to
    adjust the value of this widget.

    Note:
        You MUST override the mouseMoveEvent() of the QGraphicsView and reject
        the event signal with event.reject()
    item:
    pixels_per_tick:
    value_per_tick:
    """
    from cgwidgets.delegates import (
        StickyValueAdjustItemDelegate,
        StickyValueAdjustViewDelegate
    )
    # install view filter
    view = item.scene().views()[0]
    view_filter = StickyValueAdjustViewDelegate(view)
    view.installEventFilter(view_filter)
    view.setMouseTracking(True)
    view._dragging = False

    event_filter = StickyValueAdjustItemDelegate(item)
    event_filter.setPixelsPerTick(pixels_per_tick)
    event_filter.setValuePerTick(value_per_tick)

    item.installSceneEventFilter(event_filter)
    item.event_filter = event_filter


    # view_filter = StickyValueAdjustViewDelegate()
    # w.installEventFilter(view_filter)
    # w.setMouseTracking(True)
    # ef = installStickyValueAdjustItemDelegate(w.circle_item)
    return event_filter


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    w = QLabel('1.0')
    installStickyValueAdjustWidgetDelegate(w)
    w.show()
    w.move(QCursor.pos())
    w.resize(100, 100)

    sys.exit(app.exec_())
from qtpy.QtWidgets import *
from qtpy.QtCore import *
from qtpy.QtGui import *

""" INVISIBLE CURSOR"""
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


""" INVISIBLE WIDGET"""
def installInvisibleWidgetEvent(hide_widget, activation_widget=None):
    """
    Installs an event filter on the widget that makes it so that when the
    user click/drags, it will turn the cursor invisible, and all the cursor
    to move an infinite distance.  On release, it will return the cursor
    back to the starting position

    Args:
        activation_widget (QWidget): Widget when clicked to hide the hide_widget.
            If none is provided, the parent widget will be used
        hide_widget (QWidget): widget to be hidden, if none is provided,
            the parent widget will be used
    Returns:
    """
    from cgwidgets.events import InvisibleWidgetEvent

    # set up default widgets
    parent = hide_widget.parent()
    if not parent:
        parent = hide_widget

    if activation_widget is None:
        activation_widget = hide_widget

    invisible_widget_data = {
        'parent' : parent,
        'hide_widget' : hide_widget,
        'activation_widget' : activation_widget}

    # create filter
    invisible_widget_filter = InvisibleWidgetEvent(
        parent=parent
    )

    # setup attrs / install event filter
    hide_widget._hide_widget_filter_INVISIBLE = False
    for key in invisible_widget_data:
        widget = invisible_widget_data[key]
        print(widget)
        widget._invisible_widget_data = invisible_widget_data

        # install event filter
        widget.installEventFilter(invisible_widget_filter)

    return invisible_widget_filter


""" SLIDE"""
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


""" LADDER"""
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


""" STICKY VALUE DRAG"""
def installStickyValueAdjustWidgetDelegate(
        active_widget, pixels_per_tick=200, value_per_tick=0.01, drag_widget=None, activation_widget=None
    ):
    """

    active_widget (QWidget): widget to set the value on.
    activation_widget (QWidget): widget when clicked on will start this delegate
    pixels_per_tick:
    value_per_tick:
    drag_widget (QWidget): Widget to use as the drag area.  By default
        this will be the widget unless specified

    """

    from cgwidgets.delegates import StickyValueAdjustWidgetDelegate

    if not drag_widget:
        drag_widget = active_widget

    if not activation_widget:
        activation_widget = active_widget

    sticky_widget_data = {
        'drag_widget': drag_widget,
        'active_widget': active_widget,
        'activation_widget': activation_widget
    }

    # create filter
    sticky_widget_filter = StickyValueAdjustWidgetDelegate(active_widget)
    sticky_widget_filter.setPixelsPerTick(pixels_per_tick)
    sticky_widget_filter.setValuePerTick(value_per_tick)
    sticky_widget_filter._updating = False

    # setup extra attrs on widgets
    for key in sticky_widget_data:
        # get widget
        widget = sticky_widget_data[key]

        # set attrs
        widget._sticky_widget_data = sticky_widget_data
        widget.setMouseTracking(True)
        widget._drag_STICKY = False
        widget._filter_STICKY = sticky_widget_filter
        widget._slider_pos = 0

        # install filter
        widget.installEventFilter(sticky_widget_filter)

    return sticky_widget_filter


def installStickyValueAdjustItemDelegate(
        item, pixels_per_tick=200, value_per_tick=0.01, activation_item=None
    ):
    """
    Installs a delegate on the widget which makes it so when the user clicks.
    It will hide the cursor and allow the user to move the mouse around to
    adjust the value of this widget.

    Note:
        You MUST override the mouseMoveEvent() and mouseReleaseEvent()
        of the QGraphicsView and reject the event signal with event.reject().
        Because for reasons, these signals do not get passed... and are blocked =\

    item (QGraphicsItem): Item to do adjustments on
    activation_item (QGraphicsItem): item when clicked will activate the sticky drag
    pixels_per_tick:
    value_per_tick:
    """
    from cgwidgets.delegates import (
        StickyValueAdjustItemDelegate,
        StickyValueAdjustViewDelegate
    )
    if not activation_item:
        activation_item = item

    # install view filter
    # get view
    view = activation_item.scene().views()[0]
    view.setMouseTracking(True)
    view._drag_STICKY = False
    view._slider_pos = 0

    # create/install view filter
    view_filter = StickyValueAdjustViewDelegate(view)
    view_filter.setPixelsPerTick(pixels_per_tick)
    view_filter.setValuePerTick(value_per_tick)
    view.installEventFilter(view_filter)


    # create/install item filter
    item_filter = StickyValueAdjustItemDelegate(item)
    activation_item.installSceneEventFilter(item_filter)

    # setup extra attrs
    item_filter.setPixelsPerTick(pixels_per_tick)
    item_filter.setValuePerTick(value_per_tick)

    activation_item._filter_STICKY = item_filter
    activation_item._filter_STICKY_item = item

    if not hasattr(view, '_filter_STICKY_activation_list'):
        view._filter_STICKY_activation_list = []
    view._filter_STICKY_activation_list.append(activation_item)

    return view_filter, item_filter


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    w = QLabel('1.0')
    installStickyValueAdjustWidgetDelegate(w)
    w.show()
    w.move(QCursor.pos())
    w.resize(100, 100)

    sys.exit(app.exec_())
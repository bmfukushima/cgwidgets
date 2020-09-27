import json
import re

from collections import OrderedDict

from qtpy.QtWidgets import *
from qtpy.QtCore import *
from qtpy.QtGui import *


def checkNegative(enabled, value):
    """
    Checks to determine if this value should be allowed to be negative or not

    Args:
        value (float)
    """
    if enabled is False:
        if value < 0:
            value = 0
    return value


def checkIfValueInRange(enabled, value, range_min, range_max):
    """
    if set range is enabled, this will force user inputs into the specified range

    Args:
        enabled (bool): Determines whether or not to do this operation or not
            Decided to just leave this in here, as it makes the code at the other
            level look neater.
        value (float): value to check
        range_min (float):
        range_max (float):
    """
    if enabled is True:
        if value < range_min:
            value = range_min
        elif range_max < value:
            value = range_max

    return value


def checkMousePos(pos, widget):
    """
    Checks the mouse position to determine its relation to the current
    widget.

    Args:
        pos (QPoint): current cursor position in global space
        widget (QWidget): current widget to check to see if the cursor
            is inside of or not
    Returns (dict) of booleans
        INSIDE, NORTH, SOUTH, EAST, WEST
        if the arg is True then that is true.  Ie if North is true, then the cursor
        is north of the widget.  If INSIDE is True, then all of the other
        args must be False, and the cursor is inside of the widget still.

    """
    # setup return attrs
    return_dict = {
        "INSIDE" : True,
        "NORTH" : False,
        "EAST" : False,
        "SOUTH" : False,
        "WEST" : False
    }

    # check mouse position...
    top_left = widget.mapToGlobal(widget.geometry().topLeft())
    top = top_left.y()
    left = top_left.x()
    right = left + widget.geometry().width()
    bot = top + widget.geometry().height()

    # update dictionary based off of mouse position
    if top > pos.y():
        return_dict["NORTH"] = True
        return_dict["INSIDE"] = False
    if right < pos.x():
        return_dict["EAST"] = True
        return_dict["INSIDE"] = False
    if bot < pos.y():
        return_dict["SOUTH"] = True
        return_dict["INSIDE"] = False
    if left > pos.x():
        return_dict["WEST"] = True
        return_dict["INSIDE"] = False

    return return_dict


def getFontSize(application):
    """
    Returns the current systems font size
    """
    font = application.font()
    return font.pointSize()


def guessBackgroundColor(style_sheet):
    """
    Searches a style sheet for the background-color
    """
    find_matches = b = re.findall("background-color.*rgba.*\)", style_sheet)
    if len(find_matches) > 0:
        return '(' + b[0].split('(')[1:][0]
    return repr((64, 64 ,64 ,255))


def printStartTest(name):
    print("""

----------------------------------------------------------------------
----------------------------------------------------------------------
""")
    print('Starting {} unittest...'.format(name))


def getJSONData(json_file):
    """
    returns the actual json dict
    """
    if json_file:
        with open(json_file, 'r') as f:
            datastore = json.load(f, object_pairs_hook=OrderedDict)
    return datastore


def getWidgetUnderCursor():
    pos = QCursor.pos()
    widget = qApp.widgetAt(pos)
    return widget
# this needs to die

def getMainWidget(widget, name):
    """
    searchs widgets parents until it finds one with the name
    provided in the variables.

    Note:
        that name is found with the __name__() dunder

    @widget < widget >
        widget to start searching parents from
    @name < str >
        name of widget to find
    """
    try:
        if widget.__name__() == name:
            return widget
        else:
            return getMainWidget(widget.parent(), name)
    except AttributeError:
        try:
            return getMainWidget(widget.parent(), name)
        except AttributeError:
            print("this is has no parents...")


def getWidgetAncestor(widget, instance_type):
    """
    Recursively searches up from the current widget
    until an widget of the specified instance is found

    Args:
        widget (QWidget): widget to search from
        instance_type (object): Object type to find
    """

    if isinstance(widget, instance_type):
        return widget
    else:
        parent = widget.parent()
        if parent:
            return getWidgetAncestor(widget.parent(), instance_type)
        else:
            return None


def getBottomLeftPos(widget):
    """
    Returns the bottom left position of the specific widget.  This is mainly for
    lining up any sort of popups and what not.

    Args:
        widget (QWidget): Widget whose position you want to return
    Returns (QPoint): Point in world space of the bottom left coordinate
        of the widget given
    """

    # get pos
    if widget.parent():
        pos = widget.parent().mapToGlobal(widget.geometry().bottomLeft())
    else:
        pos = widget.geometry().bottomLeft()

    # back up clause
    if not pos:
        pos = QPoint(0, 0)

    return pos


def clearLayout(layout, start=None, end=None):
    """
    removes all widgets from the layout provided

    args:
        @layout: < QLayout >
    kwargs:
        @start: < int > 
            index to start removing from
        @end: <int>
            index to stop removing at
    """
    if not end:
        end = layout.count()
    if not start:
        start = 0
    for i in reversed(range(start, end)):
        widget = layout.itemAt(i).widget()
        try:
            widget.setParent(None)
        except AttributeError:
            pass


def setAsTool(widget):
    import platform
    if platform.system() == 'Windows':
        widget.setWindowFlags(
            Qt.Tool
            | Qt.NoDropShadowWindowHint
            | Qt.WindowStaysOnTopHint
            )
    elif platform.system() == 'Linux':
        widget.setWindowFlags(
            Qt.Tool
            | Qt.NoDropShadowWindowHint
            | Qt.FramelessWindowHint
            )


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
    from .delegates import SlideDelegate
    # set up default slide display type
    if breed is None:
        breed = 0

    slide_delegate = SlideDelegate(
        parent=widget,
        getSliderPos=sliderPosMethod,
        breed=breed,
        display_widget=display_widget
    )
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


def getGlobalPos(widget):
    """
    returns the global position of the widget provided, because Qt
    does such a lovely job of doing this out of box and making it
    so simple

    No idea why this doesnt get the actual title bar height?
    args:
        widget: <QWidget>
            widget to return screen space position of

    returns: <QPoint>
    """
    parent = widget.parentWidget()
    if parent is None:
        #top_level_widget = widget.window()
        top_level_widget = widget
        title_bar_height = top_level_widget.style().pixelMetric(QStyle.PM_TitleBarHeight)
        pos = QPoint(
            top_level_widget.pos().x(),
            top_level_widget.pos().y() + title_bar_height + top_level_widget.PdmDepth + (top_level_widget.PdmHeight * .5)
        )

    else:
        pos = parent.mapToGlobal(widget.pos())

    return pos


def updateStyleSheet(widget):
    """
    Updates the stylesheet for the specified widget for dynamic
    style sheets
    """
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()

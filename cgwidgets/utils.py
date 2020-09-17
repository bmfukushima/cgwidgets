import json
import re

from collections import OrderedDict

from qtpy.QtWidgets import *
from qtpy.QtCore import *
from qtpy.QtGui import *

from cgwidgets.settings.colors import RGBA_DEFAULT_BACKGROUND


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
    print('''

----------------------------------------------------------------------
----------------------------------------------------------------------
''')
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
    user_input=QEvent.MouseButtonPress,
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
    '''
    returns the global position of the widget provided, because Qt
    does such a lovely job of doing this out of box and making it
    so simple

    No idea why this doesnt get the actual title bar height?
    args:
        widget: <QWidget>
            widget to return screen space position of

    returns: <QPoint>
    '''
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
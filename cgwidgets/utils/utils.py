import json
import re
import math
import os

from collections import OrderedDict

from qtpy.QtWidgets import *
from qtpy.QtCore import *
from qtpy.QtGui import *


def checkNegative(enabled, value):
    """
    Checks to determine if this value should be allowed to be negative or not

    Args:
        enabled (bool)
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
        # print(type(value), value, type(range_min), range_min, type(range_max), range_max)
        if value < range_min:

            value = range_min
        elif range_max < value:
            value = range_max

    return value


def getUniqueName(name, children, exists=True):
        """ Gets a unique name for an item when it is created

        Args:
            name (str): name to search for
            children (ModelViewItem): to check children of
            exists (bool): determines if the item exists prior to searching for the name or not"""
        name = name

        # remove one instance of name, as it has already been added
        if exists:
            if name in children:
                children.remove(name)

        # get unique name of item
        if name in children:
            while name in children:
                try:
                    suffix = str(int(name[-1]) + 1)
                    name = name[:-1] + suffix
                except ValueError:
                    name = name + "0"

        return name


def getFontSize(application=None):
    """
    Returns the current systems font size
    """
    if not application:
        application = QApplication
    font = application.font()
    return font.pointSize()


def guessBackgroundColor(style_sheet):
    """
    Searches a style sheet for the background-color
    """
    find_matches = b = re.findall("background-color.*rgba.*\)", style_sheet)
    if len(find_matches) > 0:
        return '(' + b[0].split('(')[1:][0]
    return repr((64, 64, 64, 255))


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
    if datastore:
        return datastore
    else:
        return None


def getDefaultSavePath():
    """
    Gets the default save path located at $HOME/.cgwidgets

    Returns (str): $HOME/.cgwidgets
    """
    save_dir = os.environ["HOME"] + '/.cgwidgets'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    return save_dir


def isCursorOverWidget(widget):
    """ Determines if the cursor is over the widget or not
    Args:
        widget (QWidget): to test position of

    Returns (bool)"""
    global_event_pos = QCursor.pos()
    if widget.parent():
        """ Need to check if its a tool or not.  If its not a tool, we need to cast
        this to the global position.  If it is a tool, for some reason it already works"""
        if bool(widget.windowFlags() & Qt.Tool):
            global_event_pos = widget.parent().mapToGlobal(QCursor.pos())
        top_left = widget.parent().mapToGlobal(widget.geometry().topLeft())
    else:
        top_left = widget.geometry().topLeft()

    cursor_xpos = global_event_pos.x()
    cursor_ypos = global_event_pos.y()

    x = top_left.x()
    y = top_left.y()
    w = widget.geometry().width()
    h = widget.geometry().height()

    if (x < cursor_xpos and cursor_xpos < (x + w)) and (y < cursor_ypos and cursor_ypos < (y + h)):
        return True
    else:
        return False


def runDelayedEvent(widget, event, name="_timer", delay_amount=50):
    """ Runs the event provided after a certain amount of delay (delay_amount)

    Args:
        widget (obj): to store metadata on
        event (func): function to be run when timer times out
        name (str):
        delay_amount (int)
    """
    if hasattr(widget, name):
        getattr(widget, name).setInterval(delay_amount)

    def eventWrapper():
        event()
        delattr(widget, name)

    new_timer = QTimer()
    setattr(widget, name, new_timer)
    getattr(widget, name).start(delay_amount)
    getattr(widget, name).timeout.connect(eventWrapper)


def convertScriptToString(file_path):
    with open(file_path, "r") as myfile:
        data = myfile.readlines()

    string_script = "".join(data)

    return string_script


def clearLayout(layout, start=None, end=None):
    """
    removes all widgets from the layout provided

    args:
        layout (QLayout): layout to be clear
        start (int): index to start removing from
        end (int): index to stop removing at
    """
    if not end:
        end = layout.count()
    if not start:
        start = 0
    for i in reversed(range(start, end)):
        widget = layout.itemAt(i).widget()
        try:
            widget.setParent(None)
            widget.deleteLater()
        except AttributeError:
            pass


def showWarningDialogue(widget, warning_display_widget, accept_event, cancel_event, width=1080, height=512):
    """
    Displays a warning widget to the user at the center of the screen

    Args:
        widget (QWidget): That widget that is launching the warning dialogue.  Note that this
            widget will be the same arg that will be provided to the accept_event,
            and cancel_event virtual functions
        warning_display_widget (QWidget): Widget to be displayed at the center of the warning box
        accept_event (function): Function that will be run when the user clicks the happy dog
            args (widget)
        cancel_event (function): Function that will be run when the user clicks the sad dog
            args (widget)
        width (int): width of the warning box
        height (int): height of the warning box

    Returns:

    """
    from cgwidgets.widgets import AbstractWarningWidget
    from cgwidgets.utils import centerCursorOnWidget
    # create warning widget
    widget._warning_widget = AbstractWarningWidget(widget=widget, display_widget=warning_display_widget)

    # connect user events
    widget._warning_widget.setAcceptEvent(accept_event)
    widget._warning_widget.setCancelEvent(cancel_event)

    # show widget._warning_widget
    setAsAlwaysOnTop(widget._warning_widget)
    widget._warning_widget.show()
    centerCursorOnWidget(widget._warning_widget)
    # widget._warning_widget.setFocus()

    return widget._warning_widget


def setAsAlwaysOnTop(widget):
    """ Sets the widget as always on top.

    Must be run BEFORE the widget has been shown."""
    widget.setWindowFlag(Qt.WindowStaysOnTopHint)
    widget.setWindowState(widget.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
    widget.activateWindow()


def setAsTool(widget, enabled=True):
    import platform
    if enabled:
        if platform.system() == 'Windows':
            widget.setWindowFlags(
                widget.windowFlags()
                | Qt.Tool
                | Qt.NoDropShadowWindowHint
                | Qt.WindowStaysOnTopHint
                )
        elif platform.system() == 'Linux':
            widget.setWindowFlags(
                widget.windowFlags()
                | Qt.Tool
                | Qt.NoDropShadowWindowHint
                | Qt.FramelessWindowHint
                )
    else:
        if platform.system() == 'Windows':
            widget.setWindowFlags(
                widget.windowFlags()
                & ~Qt.Tool
                & ~Qt.NoDropShadowWindowHint
                & ~Qt.WindowStaysOnTopHint
            )
        elif platform.system() == 'Linux':
            widget.setWindowFlags(
                widget.windowFlags()
                & ~Qt.Tool
                & ~Qt.NoDropShadowWindowHint
                & ~Qt.FramelessWindowHint
            )


def setAsPopup(widget, enabled=True):
    import platform
    if enabled:
        if platform.system() == 'Windows':
            widget.setWindowFlags(
                widget.windowFlags()
                | Qt.Popup
                | Qt.NoDropShadowWindowHint
                | Qt.WindowStaysOnTopHint
                )
        elif platform.system() == 'Linux':
            widget.setWindowFlags(
                widget.windowFlags()
                | Qt.Popup
                | Qt.NoDropShadowWindowHint
                | Qt.FramelessWindowHint
                )
    else:
        if platform.system() == 'Windows':
            widget.setWindowFlags(
                widget.windowFlags()
                & ~Qt.Popup
                & ~Qt.NoDropShadowWindowHint
                & ~Qt.WindowStaysOnTopHint
            )
        elif platform.system() == 'Linux':
            widget.setWindowFlags(
                widget.windowFlags()
                & ~Qt.Popup
                & ~Qt.NoDropShadowWindowHint
                & ~Qt.FramelessWindowHint
            )


def setAsWindow(widget):
    import platform
    if platform.system() == 'Windows':
        widget.setWindowFlags(
            widget.windowFlags()
            | Qt.Window
            | Qt.NoDropShadowWindowHint
            | Qt.WindowStaysOnTopHint
            )
    elif platform.system() == 'Linux':
        widget.setWindowFlags(
            widget.windowFlags()
            | Qt.Window
            | Qt.NoDropShadowWindowHint
            | Qt.FramelessWindowHint
            )


def setAsTransparent(widget):
    widget.setAttribute(Qt.WA_NoSystemBackground)
    widget.setWindowFlags(
        widget.windowFlags()
        | Qt.FramelessWindowHint
        | Qt.WindowStaysOnTopHint
    )
    widget.setAttribute(Qt.WA_TranslucentBackground)
    widget.setStyleSheet("background-color: rgba(0,0,0,0)")


def updateStyleSheet(widget):
    """
    Updates the stylesheet for the specified widget for dynamic
    style sheets
    """
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()

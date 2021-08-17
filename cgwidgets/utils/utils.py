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
        if value < range_min:
            value = range_min
        elif range_max < value:
            value = range_max

    return value


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


def getDefaultSavePath():
    """
    Gets the default save path located at $HOME/.cgwidgets

    Returns (str): $HOME/.cgwidgets
    """
    save_dir = os.environ["HOME"] + '/.cgwidgets'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    return save_dir


# remove this for now
# def getMainWidget(widget, name):
#     """
#     searchs widgets parents until it finds one with the name
#     provided in the variables.
#
#     Note:
#         that name is found with the __name__() dunder
#
#     @widget < widget >
#         widget to start searching parents from
#     @name < str >
#         name of widget to find
#     """
#     try:
#         if widget.__name__() == name:
#             return widget
#         else:
#             return getMainWidget(widget.parent(), name)
#     except AttributeError:
#         try:
#             return getMainWidget(widget.parent(), name)
#         except AttributeError:
#             print("this is has no parents...")

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


def setAsTool(widget):
    import platform
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


def unsetAsTool(widget):
    import platform
    if platform.system() == 'Windows':
        widget.setWindowFlags(
            widget.windowFlags()
            & Qt.Tool
            & Qt.NoDropShadowWindowHint
            & Qt.WindowStaysOnTopHint
            )
    elif platform.system() == 'Linux':
        widget.setWindowFlags(
            widget.windowFlags()
            & Qt.Tool
            & Qt.NoDropShadowWindowHint
            & Qt.FramelessWindowHint
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

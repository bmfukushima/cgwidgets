import os
import json
from collections import OrderedDict

from qtpy.QtWidgets import *
from qtpy.QtCore import *
from qtpy.QtGui import *


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


def installLadderDelegate(
    widget,
    user_input=QEvent.MouseButtonPress,
    value_list=[0.001, 0.01, 0.1, 1, 10, 100, 1000]
):
    """
    args:
        widget: <QLineEdit> or <QLabel>
            widget to install ladder delegate onto.  Note this currently
            works for QLineEdit and QLabel.  Other widgets will need
            to implement a 'setValue(value)' method on which sets the
            widgets value. 
    kwargs:
        user_input: <QEvent>
            user event that triggers the popup of the Ladder Delegate
        value_list: <list> of <float>
            list of values for the user to be able to adjust by, usually this
            is set to .01, .1, 1, 10, etc
    """
    from .delegates import LadderDelegate
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
    so simply
    args:
        widget: <QWidget>
            widget to return screen space position of

    returns: <QPoint>
    '''
    top_level_widget = widget.window()
    parent = widget.parentWidget()
    if parent is None:
        title_bar_height = top_level_widget.style().pixelMetric(QStyle.PM_TitleBarHeight)
        #pos = top_level_widget.pos() + title_bar_height + 4
        
        pos = QPoint(
            top_level_widget.pos().x(),
            top_level_widget.pos().y() + title_bar_height + 4
        )
        
    else:
        pos = parent.mapToGlobal(widget.pos())

    return pos
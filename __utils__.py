import os
import json
from collections import OrderedDict

from qtpy.QtWidgets import *
from qtpy.QtCore import *
from qtpy.QtGui import *
from cgqtpy.delegates.__utils__ import installLadderDelegate


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


def installLadderDelegate(widget, user_input):
    """
    kwargs:
        @widget: <QLineEdit> or <QLabel>
            widget to install ladder delegate onto.  Note this currently
            works for QLineEdit and QLabel.  Other widgets will need
            to implement a 'setValue(value)' method on which sets the
            widgets value. 
        @user_input: <QEvent>
            user event that triggers the popup of the Ladder Delegate
            
    """
    ladder = LadderDelegate(
        parent=widget,
        widget=widget,
        #pos=self.pos(),
        value_list=self._value_list,
        user_input=user_input
    )
    widget.installEventFilter(ladder)


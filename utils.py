import os
import json
from collections import OrderedDict

from qtpy.QtWidgets import *
from qtpy.QtCore import *
from qtpy.QtGui import *


def getJSONData(json_file):
    '''
    returns the actual json dict
    '''
    if json_file:
        with open(json_file, 'r') as f:
            datastore = json.load(f, object_pairs_hook=OrderedDict)
    return datastore


def getModel(widget):
    main_widget = getMainWidget(widget)
    model = main_widget.model
    return model


def getMainWidget(widget):
    try:
        if widget.__name__() == 'Library':
            return widget
        else:
            return getMainWidget(widget.parent())
    except AttributeError:
        try:
            return getMainWidget(widget.parent())
        except AttributeError:
            print("this is has no parents...")


def clearLayout(layout, start=None, end=None):
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


def createGroupBoxSS(border, margin):
        '''
        @border: <int> width of border
        @margin: <int> size of margin
        '''
        stylesheet = """
        QGroupBox::title{{
            subcontrol-origin: margin;
            subcontrol-position: top center;
                padding: -{0}px {0}px;
            }}

        QGroupBox{{
            border-width: {0}px;
            border-radius: {0}px;
            border-style: solid;
            margin-top: 1.25ex;
            margin-bottom: {1};
            margin-left: {1};
            margin-right: {1};
        }}
        """.format(border, margin)

        # just doing a stupid hack here so its more human readable
        # and returning a list to force it to be more machine readable
        return stylesheet.split(';')


def createThumbnailSS(border_width, active):
    activated_color = '96, 96, 96'
    if active is True:
        activated_color = '255, 200, 0'

    stylesheet = '''
        border-width:{}px;
        border-style: solid;
        border-color: rgba(48,48,48,192);
        background-color: rgba({activated_color},192);
        '''.format(border_width, activated_color=activated_color)

    return stylesheet

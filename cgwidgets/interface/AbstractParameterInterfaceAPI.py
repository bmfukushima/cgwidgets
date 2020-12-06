"""
When a node calls a specific function that would normally be called through
a DCC's API.  This translator intercepts the signal, and chooses the correct
DCC's API to use.
NOTE:
    <node> is always an AbstractNode used as a wrapper for the DCC node
    <port> is always an AbstractPort used as a wrapper for the DCC port
"""

import sys
#from cgwidgets.interface import AbstractPort

# get DCC
dcc_path = sys.argv[0].lower()

KATANA = 'KATANA'
NUKE = 'NUKE'
MARI = 'MARI'
HOUDINI = 'HOUDINI'

if 'katana' in dcc_path:
    from cgwidgets.interface.katana import parameter as dccparam
    split_type = '.'
# todo setup other translators
if 'nuke' in dcc_path:
    from cgwidgets.interface.nuke import parameter as dccparam
if 'houdini' in dcc_path:
    from cgwidgets.interface.houdini import parameter as dccparam
if 'mari' in dcc_path:
    from cgwidgets.interface.mari import parameter as dccparam


def name(parameter):
    return dccparam.name(parameter.parameter())

def setName(parameter, name):
    return dccparam.setName(parameter.parameter(), name)

""" HIERARCHY """
def path(parameter):
    # import / initialize
    from cgwidgets.interface import AbstractParameter

    parameter = dccparam.path(parameter.parameter())
    return AbstractParameter(parameter)
# todo
def setPath(parameter, path):
    # todo
    # not set up
    parent_path = '{split_type}'.format(split_type=split_type).join(path.split('{split_type}'.format(split_type=split_type))[:-1])
    dccparam.setPath(parameter.parameter(), path)
    return path
# todo
def insertChild(parameter, index, child):
    # todo dccparam insert child
    dccparam.insertChild(parameter.parameter(), index, child)
# todo
def removeChild(parameter, child):
    # todo dccparam remove child
    dccparam.removeChild(parameter.parameter(), child)

def child(parameter, child_name):
    # import / initialize
    from cgwidgets.interface import AbstractParameter

    child = dccparam.child(parameter.parameter(), child_name)
    return AbstractParameter(child)

def childAtIndex(parameter, index):
    # import / initialize
    child = parameter.children()[index]
    return child

def children(parameter):
    # import / initialize
    from cgwidgets.interface import AbstractParameter

    children = dccparam.children(parameter.parameter())
    return [AbstractParameter(child) for child in children]

def parent(parameter):
    # import / initialize
    from cgwidgets.interface import AbstractParameter

    parent = dccparam.parent(parameter.parameter())
    return AbstractParameter(parent)

# todo
def setParent(parameter, parent, index=0):
    """
    Sets the parameters parent.

    This should set the parameter to a new parent at
    the specified index.

    Args:
        parameter (AbstractParameter)
        parent (AbstractParameter)
        index (int)

    Returns (AbstractParameter)
    """
    from cgwidgets.interface import AbstractParameter

    # todo dccparam setParent
    new_parent = dccparam.setParent(parameter.parameter(), parent.parameter(), index)
    return AbstractParameter(new_parent)

""" ARGS """
def value(parameter, frame=0):
    return dccparam.value(parameter.parameter(), frame=frame)

def setValue(parameter, value, frame=0):
    return dccparam.setValue(parameter.parameter(), value, frame=frame)
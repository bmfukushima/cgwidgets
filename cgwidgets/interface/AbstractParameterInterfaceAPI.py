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
dcc_path = sys.argv[0]

KATANA = 'KATANA'
NUKE = 'NUKE'
MARI = 'MARI'
HOUDINI = 'HOUDINI'

if 'katana' in dcc_path:
    from cgwidgets.interface.katana import parameter as dccparam
# todo setup other translators
if 'nuke' in dcc_path:
    from cgwidgets.interface.nuke import parameter as dccparam
if 'houdini' in dcc_path:
    from cgwidgets.interface.houdini import parameter as dccparam
if 'mari' in dcc_path:
    from cgwidgets.interface.mari import parameter as dccparam

""" ARGS """
def value(parameter, frame=0):
    return dccparam.value(parameter.parameter(), frame=frame)

def setValue(parameter, value, frame=0):
    dccparam.setValue(parameter.parameter(), value, frame=frame)
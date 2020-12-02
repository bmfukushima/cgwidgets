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
    from cgwidgets.interface.katana import port as dccport
# todo setup other translators
if 'nuke' in dcc_path:
    from cgwidgets.interface.nuke import port as dccport
if 'houdini' in dcc_path:
    from cgwidgets.interface.houdini import port as dccport
if 'mari' in dcc_path:
    from cgwidgets.interface.mari import port as dccport

def connect(port_a, port_b):
    # preflight
    type_a = port_a.type()
    type_b = port_b.type()
    if type_a == type_b: return

""" ARGS """
def name(port):
    return dccport.name(port.port())

def node(port):
    return dccport.node(port.port())

def setName(port, name):
    dccport.setName(port.port(), name)

def gender(port):
    """
    0 = MALE
    1 = FEMALE
    """
    return dccport.gender(port)
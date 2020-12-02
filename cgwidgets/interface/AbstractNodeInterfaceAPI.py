"""
When a node calls a specific function that would normally be called through
a DCC's API.  This translator intercepts the signal, and chooses the correct
DCC's API to use.
NOTE:
    on abstract classes:
    <node>
        - Receiving is always the DCC node
        - Returns AbstractNodes
    <port>
        - Receiving is DCC Port
        - Returns AbstractPorts

    modules are loaded on demand due to import recursion caused when loading
    during system init.

    # is always an AbstractPort used as a wrapper for the DCC port

"""

import sys
# TODO Import loop fail =\
# recursive import between Interface --> Node
# import loop
# from cgwidgets.interface import AbstractNode
# from cgwidgets.interface import AbstractPort


# get DCC
dcc_path = sys.argv[0]

KATANA = 'KATANA'
NUKE = 'NUKE'
MARI = 'MARI'
HOUDINI = 'HOUDINI'

if 'katana' in dcc_path:
    from cgwidgets.interface.katana import node as dccnode
# todo setup other translators
if 'nuke' in dcc_path:
    from cgwidgets.interface.nuke import node as dccnode
if 'houdini' in dcc_path:
    from cgwidgets.interface.houdini import node as dccnode
if 'mari' in dcc_path:
    from cgwidgets.interface.mari import node as dccnode

""" NODE API"""
def getNodeFromName(name):
    """ returns an abstract node"""

    dccnode.getNodeFromName(name)

""" PORTS """
def ports(node, port_type):
    """
    returns a list of ports
    """
    ports = dccnode.ports(node, port_type)

    # on demand imports... due to recursion errors
    from cgwidgets.interface import AbstractPort
    return [AbstractPort(port) for port in ports]

def createPort(node, port_type, name, index=None):
    """

    :param node: AbstractNode
    :param port_type: Port.TYPE
    :param name: Port name
    :param index: insertino index
    :return:
    """
    dccnode.createPort(node, port_type, name, index=index)

""" HIERARCHY """
def parent(node):
    """
    Gets the current nodes parent

    Returns (node): returns the parent node
    """
    # on demand imports... due to recursion errors
    from cgwidgets.interface import AbstractNode
    return AbstractNode(dccnode.parent(node))

def setParent(node, parent):
    """
    Sets the current nodes parent

    Args:
        node (dccNode): node to set the parent of
        parent (dccNode): node to set the parent to
    """
    dccnode.setParent(node, parent)

def children(node):
    """
    Returns a list of all of the children of specified node
    """
    children = dccnode.children(node)
    # on demand imports... due to recursion errors
    from cgwidgets.interface import AbstractNode
    return [AbstractNode(child) for child in children]

""" POSITION """
def pos(node):
    """
    Returns the nodes position as a QPoint
    """
    return dccnode.pos(node)

def setPos(node, pos):
    """
    Sets the position of the node

    Args:
        pos (QPoint): position to set the node at
    """
    dccnode.setPos(node, pos)

""" ARGS """
def name(node):
    dccnode.name(node)

def setName(node, name):
    dccnode.setName(node, name)


def test():
    print(DCC)
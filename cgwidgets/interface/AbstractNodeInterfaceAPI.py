"""
When a node calls a specific function that would normally be called through
a DCC's API.  This translator intercepts the signal, and chooses the correct
DCC's API to use.
NOTE:
    on abstract classes:
    <node>
        - Receiving is always the AbstractNodes node
        - Returns AbstractNodes
    <port>
        - Receiving is AbstractPort
        - Returns AbstractPorts

    modules are loaded on demand due to import recursion caused when loading
    during system init.

    # is always an AbstractPort used as a wrapper for the DCC port

"""

import sys

# get DCC
dcc_path = sys.argv[0].lower()
KATANA = 'KATANA'
NUKE = 'NUKE'
MARI = 'MARI'
HOUDINI = 'HOUDINI'

if 'katana' in dcc_path:
    from cgwidgets.interface.katana import node as dccnode
    split_type = '.'
# todo setup other translators
if 'nuke' in dcc_path:
    from cgwidgets.interface.nuke import node as dccnode
if 'houdini' in dcc_path:
    from cgwidgets.interface.houdini import node as dccnode
if 'mari' in dcc_path:
    from cgwidgets.interface.mari import node as dccnode

TRANSLATE = False
for dcc in ['katana', 'nuke', 'houdini', 'mari']:
    if dcc in dcc_path:
        TRANSLATE = True

""" PORTS """
def ports(node, port_gender):
    """
    returns a list of ports

    Args:
        node (AbstractNode)
        port_gender (AbstractPort.GENDER)
    """
    from cgwidgets.interface import AbstractPort

    node = node.node()

    # get ports list
    if port_gender == AbstractPort.FEMALE:
        port_list = dccnode.getInputPorts(node)
    elif port_gender == AbstractPort.MALE:
        port_list = dccnode.getOutputPorts(node)
    else:
        port_list = dccnode.getOutputPorts(node) + dccnode.getInputPorts(node)

    # return abstract ports
    return [AbstractPort(port) for port in port_list]

def createPort(node, port_gender, name, index=None):
    """

    Args:
        node (AbstractNode):
        port_gender (AbstractPort.GENDER):
        name (str): Port name

        index (int): index to be inserted at.
            If not provided, will insert as the 0th index
    :return:
    """
    #return dccnode.createPort(node.node(), port_gender, name, index=index)

    # todo get num children and put at end
    # default insertino index
    from cgwidgets.interface import AbstractPort

    # get index
    if not index:
        index = 0

    # create port
    # FEMALE
    if port_gender == AbstractPort.FEMALE:
        if not name:
            name = 'i0'
        port = dccnode.createInputPort(node, name, index)

    # MALE
    elif port_gender == AbstractPort.MALE:
        if not name:
            name = 'o0'
        port = dccnode.createOutputPort(node, name, index)

    # return
    return AbstractPort(port)

""" HIERARCHY """
def parent(node):
    """
    Gets the current nodes parent

    Returns (node): returns the parent node
    """
    # on demand imports... due to recursion errors
    from cgwidgets.interface import AbstractNode
    return AbstractNode(dccnode.parent(node.node()))

def setParent(node, parent):
    """
    Sets the current nodes parent

    Args:
        node (dccNode): node to set the parent of
        parent (dccNode): node to set the parent to
    """
    dccnode.setParent(node.node(), parent.node())

def children(node):
    """
    Returns a list of all of the children of specified node
    """
    children = dccnode.children(node.node())
    # on demand imports... due to recursion errors
    from cgwidgets.interface import AbstractNode
    return [AbstractNode(child) for child in children]

""" POSITION """
def pos(node):
    """
    Returns the nodes position as a QPoint
    """
    return dccnode.pos(node.node())

def setPos(node, pos):
    """
    Sets the position of the node

    Args:
        pos (QPoint): position to set the node at
    """
    dccnode.setPos(node.node(), pos)

""" PARAMETERS """
def parameter(node, parameter_path):
    from cgwidgets.interface import AbstractParameter
    _parameter = dccnode.parameter(node.node(), parameter_path)
    return AbstractParameter(_parameter)

def getRootParameter(node):
    from cgwidgets.interface import AbstractParameter
    return AbstractParameter(dccnode.getRootParameter(node.node()))

def createParameter(
        node,
        parameter_type,
        parameter_parent=None,
        name="parameter",
        value=None):
    # import / initialize
    from cgwidgets.interface import AbstractParameter
    # get parent param
    if not parameter_parent:
        parameter_parent = getRootParameter(node).parameter()
    else:
        parameter_parent = parameter_parent.parameter()

    node = node.node()
    # create param
    if parameter_type == AbstractParameter.GROUP:
        parameter = dccnode.createGroupParameter(
            node, parameter_type, parameter_parent, name, value)
    if parameter_type == AbstractParameter.INTEGER:
        parameter = dccnode.createIntegerParameter(
            node, parameter_type, parameter_parent, name, value)
    if parameter_type == AbstractParameter.STRING:
        parameter = dccnode.createStringParameter(
            node, parameter_type, parameter_parent, name, value)
    # return param
    return AbstractParameter(parameter)

""" ARGS """
def name(node):
    return dccnode.name(node.node())

def setName(node, name):
    return dccnode.setName(node.node(), name)

def type(node):
    return dccnode.type(node.node())

def setType(node, type):
    # todo setup setType (not sure I want this...)
    #node.setName(type)
    pass

""" NODEGRAPH API"""

def createNode(node_type, parent, name=None):
    from cgwidgets.interface import AbstractNode
    if TRANSLATE:
        node = AbstractNode(dccnode.createNode(node_type, parent=parent, name=name))
    else:
        node = AbstractNode(parent=parent, name=name)

    return node

def getRootNode():
    if TRANSLATE:
        from cgwidgets.interface import AbstractNode
        return AbstractNode(dccnode.getRootNode())
    else:
        # todo not sure if this is right... or how to do root node atm...
        return None

def getNodeFromName(name):
    from cgwidgets.interface import AbstractNode
    return AbstractNode(dccnode.getNodeFromName(name))

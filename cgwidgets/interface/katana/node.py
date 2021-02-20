from qtpy.QtCore import QPoint
import NodegraphAPI

""" PORT """
def getInputPorts(node):
    return node.getInputPorts()

def getOutputPorts(node):
    return node.getOutputPorts()

def getSendPorts(node):
    send_ports = []
    for port in node.getInputPorts():
        port_name = port.getName()
        send_ports.append(node.getSendPort(port_name))

    return send_ports

def getReturnPorts(node):
    return_ports = []
    for port in node.getOutputPorts():
        port_name = port.getName()
        return_ports.append(node.getReturnPort(port_name))

    return return_ports

def createInputPort(node, name, index):
    node = node.node()
    port = node.addInputPortAtIndex(name, index)
    return port

def createOutputPort(node, name, index):
    node = node.node()
    port = node.addOutputPortAtIndex(name, index)
    return port

""" PARAMETER """
def parameter(node, parameter_path):
    parameter = node.getParameter(parameter_path)
    return parameter

def rootParameter(node):
    return node.getParameters()

def createGroupParameter(
    node,
    parameter_type,
    parameter_parent=None,
    name="parameter",
    value=None
):
    parameter = parameter_parent.createChildGroup(name)
    return parameter

def createStringParameter(
    node,
    parameter_type,
    parameter_parent,
    name="parameter",
    value=''):

    parameter = parameter_parent.createChildString(name, value)
    return parameter

def createIntegerParameter(
    node,
    parameter_type,
    parameter_parent,
    name="parameter",
    value=0):

    parameter = parameter_parent.createChildNumber(name, value)

    return parameter

def createFloatParameter(
    node,
    parameter_type,
    parameter_parent,
    name="parameter",
    value=0):

    parameter = parameter_parent.createChildNumber(name, value)

    return parameter

""" HIERARCHY """
def parent(node):
    return node.getParent()

def setParent(node, parent):
    node.setParent(parent)

def children(node):
    return node.getChildren()

""" POSITION """
def pos(node):
    return QPoint(*NodegraphAPI.GetNodePosition(node))

def setPos(node, pos):
    NodegraphAPI.SetNodePosition(node, (pos.x(), pos.y()))

""" ARGS """
def name(node):
    return node.getName()

def setName(node, name):
    node = node.setName(name)
    return node.getName()

def type(node):
    return node.getType()

def setType(node, type):
    # todo setup setType (not sure I want this...)
    #node.setName(type)
    return type

""" NODEGRAPH API"""
def createNode(node_type, parent, name=None):
    # get name
    if not name:
        name = node_type
    new_node = NodegraphAPI.CreateNode(node_type, parent.node())
    new_node.setName(name)
    return new_node

def getRootNode():
    return NodegraphAPI.GetRootNode()

def getNodeFromName(name):
    return NodegraphAPI.GetNode(name)

def getAllNodeTypes():
    return NodegraphAPI.GetNodeTypes()

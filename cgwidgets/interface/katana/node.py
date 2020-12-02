""" NODE """
from qtpy.QtCore import QPoint

#from cgwidgets.interface.AbstractPort import AbstractPort

import NodegraphAPI

""" PORT """
# def ports(node, port_type):
#     if port_type == AbstractPort.FEMALE:
#         return node.getInputPorts()
#     elif port_type == AbstractPort.MALE:
#         return node.getOutputPorts()
#     else:
#         return node.getOutputPorts() + node.getInputPorts()

def getInputPorts(node):
    return node.getInputPorts()

def getOutputPorts(node):
    return node.getOutputPorts()

def createInputPort(node, name, index):
    node = node.node()
    port = node.addInputPortAtIndex(name, index)
    return port

def createOutputPort(node, name, index):
    node = node.node()
    port = node.addOutputPortAtIndex(name, index)
    return port

# def createPort(node, port_type, name, index=None):
#     # todo get num children and put at end
#     # default insertino index
#     if not index:
#         index = 0
#
#     # if FEMALE
#     if port_type == AbstractPort.FEMALE:
#         port = node.addInputPortAtIndex(name, index)
#         return port
#
#     # if MALE
#     elif port_type == AbstractPort.MALE:
#         port = node.addOutputPortAtIndex(name, index)
#         return port

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
    node.setName(name)

def type(node):
    return node.getType()

def setType(node, type):
    # todo setup setType (not sure I want this...)
    #node.setName(type)
    pass

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



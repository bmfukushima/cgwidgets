""" NODE """
from qtpy.QtCore import QPoint

from cgwidgets.interface.AbstractPort import AbstractPort

import NodegraphAPI



""" PORT """
def ports(node, port_type):
    if port_type == AbstractPort.INPUT:
        return node.getInputPorts()
    elif port_type == AbstractPort.OUTPUT:
        return node.getOutputPorts()
    else:
        return node.getOutputPorts() + node.getInputPorts()

def createPort(node, port_type, name, index=None):
    # todo get num children and put at end
    # default insertino index
    if not index:
        index = 0

    # if INPUT
    if port_type == AbstractPort.INPUT:
        port = node.addInputPortAtIndex(name, index)
        return port

    # if OUTPUT
    elif port_type == AbstractPort.OUTPUT:
        port = node.addOutputPortAtIndex(name, index)
        return port


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
def getNodeFromName(name):
    return NodegraphAPI.GetNode(name)



""" NODE """
from qtpy.QtCore import QPoint

from cgwidgets.interface import AbstractNode

import NodegraphAPI


def convertDCCNodeToAbstractNode(dcc_node):
    abstract_node = AbstractNode(dcc_node)

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

""" NODEGRAPH API"""
def getNodeFromName(name):
    return NodegraphAPI.GetNode(name)



""" PORT """
from qtpy.QtCore import QPoint

import NodegraphAPI

""" ARGS """
def node(port):
    return port.getNode()

def name(port):
    return port.getName()

def setName(port, name):
    port.setName(name)

def gender(port):
    return port.getType()



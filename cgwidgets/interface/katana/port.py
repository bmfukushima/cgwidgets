""" PORT """
from qtpy.QtCore import QPoint

import NodegraphAPI

""" CONNECT """
def connect(port_a, port_b):
    port_a.connect(port_b)

def disconnect(port_a, port_b):
    port_a.disconnect(port_b)

def connectedPorts(port):
    return port.getConnectedPorts()

""" ARGS """
def node(port):
    return port.getNode()

def name(port):
    return port.getName()

def setName(port, name):
    port.setName(name)
    _name = port.getName()
    return _name

def gender(port):
    return port.getType()

def index(port):
    return port.getIndex()

def setIndex(port, index):
    # todo setup setIndex (port)
    return port.setIndex(port.port(), index)



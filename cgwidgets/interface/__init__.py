"""
will need...
    Node
    Parameter
    Port

# Interface is setup like this for node/param/port
DCC Node --> AbstractNodeInterfaceAPI --> Abstract Node --> cgwidgets -->
    -- > AbstractNode --> AbstractNodeInterfaceAPI --> DCC Node
        * interface functions will get the DCC node, and convert them
        into AbstractNodes.
        * AbstractNodes will call the interface to get/set data
        * Interfaces need local imports for AbstractNode/Port

An AbstractNode is created from an existing DCC node.  The abstract node
will call the AbstractNodeInterfaceAPI to get the commands for specific DCC's.

"""

from .AbstractNode import AbstractNode
from .AbstractPort import AbstractPort
from . import AbstractNodeInterfaceAPI
from . import AbstractPortInterfaceAPI


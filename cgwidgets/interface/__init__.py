"""
will need...
    Node
    Parameter
    Port

Katana Node --> AbstractNodeInterfaceAPI --> Abstract Node --> cgwidgets
    * interface functions will get the DCC node, and convert them
    into AbstractNodes.
    * AbstractNodes will call the interface to get/set data

An AbstractNode is created from an existing DCC node.  The abstract node
will call the AbstractNodeInterfaceAPI to get the commands for specific DCC's.

"""

from .AbstractNode import AbstractNode
from . import AbstractNodeInterfaceAPI

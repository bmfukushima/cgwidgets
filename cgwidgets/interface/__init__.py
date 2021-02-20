"""
will need...
    Node
    Parameter
    Port

# Interface is setup like this for node/param/port
DCC Node --> AbstractNodeInterfaceAPI --> Abstract Node --> cgwidgets -->
    -- > AbstractNode --> AbstractNodeInterfaceAPI --> DCC Node
Abstract Node < -- > AbstractPort < -- > AbstractPortInterfaceAPI
AbstractNode < -- > AbstractParameter <--> AbstractParameterInterfaceAPI
        * interface functions will get the DCC node/param/port, and convert them
            into AbstractNode/Port/Param.
        * AbstractNodes will call the interface to get/set data
        * Interfaces need local imports for AbstractNode/Port

An AbstractNode is created from an existing DCC node.  The abstract node
will call the AbstractNodeInterfaceAPI to get the commands for specific DCC's.

"""

from .AbstractNode import AbstractNode
from .AbstractPort import AbstractPort
from .AbstractParameter import AbstractParameter
from . import AbstractNodeInterfaceAPI
from . import AbstractPortInterfaceAPI
from . import AbstractParameterInterfaceAPI

from . import AbstractUtilsInterfaceAPI


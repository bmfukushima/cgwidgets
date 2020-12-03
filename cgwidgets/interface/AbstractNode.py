import sys

from qtpy.QtCore import QPoint

from cgwidgets.interface import AbstractNodeInterfaceAPI
from cgwidgets.interface import AbstractPort, AbstractParameter

dcc_path = sys.argv[0].lower()
TRANSLATE = False
for dcc in ['katana', 'nuke', 'houdini', 'mari']:
    if dcc in dcc_path:
        TRANSLATE = True
    """


        _parameters? _root_parameter?
        _root_parameter
        """

class AbstractNode(object):
    """
    Arbitrary node class.  DCC specific nodes should be converted into a node of this type.

    Setters on this Node should be going through the AbstractNodeInterfaceAPI,
    to choose which DCC to use to do the setting.

    Everytime a node is returned, this will use an instance of AbstractNode as
    a wrapper for that dcc specific node.

    Args:
        node (node): current DCC node

    """
    def __init__(
        self,
        node,
        args=None,
        children=None,
        female_ports=None,
        male_ports=None,
        name='node',
        parent=None,
        pos=QPoint(1, 1),
        _type=None
    ):
        # initialize args
        self._node = node
        self._parent = parent
        self._pos = pos
        self._type = _type
        if not children:
            self._children = []
        if not male_ports:
            self._male_ports = []
        if not female_ports:
            self._male_ports = []
        self._name = name

        # initialize arbitrary args
        if args:
            self._args = args
        else:
            self._args = {}

    """ PARENT """
    def parent(self):
        if TRANSLATE:
            parent_node = AbstractNodeInterfaceAPI.parent(self)
            return AbstractNode(parent_node)
        else:
            return self._parent

    def setParent(self, parent):
        """
        Sets the parent

        Args:
            parent (AbstractNode): parent to set to
        """
        # update dcc
        if TRANSLATE:
            self._parent = AbstractNodeInterfaceAPI.setParent(self, parent)
        else:
            # set up add/remove parent
            self._parent.removeChild(self)
            self._parent = parent
            self._parent.addChild(self)

    """ CHILDREN """
    def hasChildren(self):
        self._has_children = True if 0 < len(self.children()) else False
        return self._has_children

    def children(self):
        if TRANSLATE:
            self._children = AbstractNodeInterfaceAPI.children(self)

        return self._children

    def addChild(self, child):
        self._children.append(child)

    def removeChild(self, child):
        self._children.remove(child)

    def pos(self):
        if TRANSLATE:
            self._pos = AbstractNodeInterfaceAPI.pos(self)

        return self._pos

    def setPos(self, pos):
        """
        Sets the position of the node in the nodegraph.

        Args:
            pos (QPoint)
        """
        if TRANSLATE:
            self._pos = AbstractNodeInterfaceAPI.setPos(self, pos)
        else:
            self._pos = pos
        return self._pos


    """ PORTS """
    # TODO setup node ports
    """
    getNumInputPorts
    getNumOutputPorts
    """
    def ports(self, port_type=None):
        """
        Returns all of the ports of the specified type.

        If none specified will return FEMALE and MALE ports

        Args:
            port_type (AbstractPort.TYPE): type of port to create,
                0 = MALE
                1 = FEMALE
        """
        if TRANSLATE:
            ports = AbstractNodeInterfaceAPI.ports(self, port_type)
        else:
            if port_type == AbstractPort.FEMALE:
                ports = self._female_ports
            elif port_type == AbstractPort.MALE:
                ports = self._male_ports
        return ports

    def createPort(self, port_type, port_name=None, index=None):
        """
        Creates an port on the node of the specified type.

        Args:
            port_type (AbstractPort.TYPE): type of port to create,
                0 = MALE
                1 = FEMALE
            port_name (string):
            index (int):
        """
        if TRANSLATE:
            port = AbstractNodeInterfaceAPI.createPort(self, port_type, port_name, index=index)
        else:
            # todo setup universal port constructor
            port = AbstractPort(self, port_type, port_name, index=index)
            self.ports(port_type=port_type).insert(index, port)
        return port

    """ PARAMETERS """
    def parameter(self, parameter_path):
        if TRANSLATE:
            AbstractNodeInterfaceAPI.parameter(self, parameter_path)
        else:
            # todo setup get child
            # search from root parameter?
            parameter = self.rootParameter().getChild(parameter_path)
        return

    def createParameter(
        self,
        parameter_type,
        name="parameter",
        value=None,
        parameter_parent=None
    ):
        if TRANSLATE:
            parameter = AbstractNodeInterfaceAPI.createParameter(
                self,
                parameter_type,
                parameter_parent=parameter_parent,
                name=name,
                value=value
            )
        else:
            parameter = AbstractParameter(
                self,
                parameter_type,
                parameter_parent=parameter_parent,
                name=name,
                value=value
            )
        return parameter

    def parameterValue(self, path, frame=0):
        if TRANSLATE:
            parameter = self.parameter(path)
            value = parameter.value(frame=frame)
        else:
            parameter = self.parameter(path).value(frame=frame)
        return value

    def setParameterValue(self, path, value, frame=0):
        parameter = self.parameter(path)
        parameter.setValue(value, frame=frame)


    """ PROPERTIES """
    def node(self):
        return self._node

    def setNode(self, node):
        self._node = node

    def name(self):
        if TRANSLATE:
            self._name = AbstractNodeInterfaceAPI.name(self)

        return self._name

    def setName(self, name):
        if TRANSLATE:
            self._name = AbstractNodeInterfaceAPI.setName(self, name)
        else:
            self._name = name

    def type(self):
        if TRANSLATE:
            self._type = AbstractNodeInterfaceAPI.type(self)
        return self._type

    def setType(self, type):
        if TRANSLATE:
            self._type = AbstractNodeInterfaceAPI.setType(self, type)
        else:
            self._type = type

    """ ARBITRARY ARGS"""
    def args(self):
        return self._args

    def getArg(self, arg):
        self.args()[arg]

    def setArgValue(self, arg, value):
        self.args()[arg] = value

    def removeArg(self, arg):
        self.args().pop(arg, None)


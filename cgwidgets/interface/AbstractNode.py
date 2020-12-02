from cgwidgets.interface import AbstractNodeInterfaceAPI

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
    def __init__(self, node, args=None):
        # initialize node
        self.setNode(node)

        # initialize arbitrary args
        if args:
            self._args = args
        else:
            self._args = {}

    """ PARENT """
    def parent(self):
        parent_node = AbstractNodeInterfaceAPI.parent(self)
        return AbstractNode(parent_node)

    def setParent(self, parent):
        """
        Sets the parent

        Args:
            parent (AbstractNode): parent to set to
        """
        # update dcc
        AbstractNodeInterfaceAPI.setParent(self, parent)

    """ CHILDREN """
    def hasChildren(self):
        has_children = True if 0 < len(self.children()) else False
        return has_children

    def children(self):
        children = AbstractNodeInterfaceAPI.children(self)

        return [AbstractNode(child) for child in children]

    def pos(self):
        AbstractNodeInterfaceAPI.pos(self)

    def setPos(self, pos):
        """
        Sets the position of the node in the nodegraph.

        Args:
            pos (QPoint)
        """
        AbstractNodeInterfaceAPI.setPos(self, pos)

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
        return AbstractNodeInterfaceAPI.ports(self, port_type)
        # get all FEMALE ports AbstractNodeInterfaceAPI
        # AbstractPortInterfaceAPI...

        # returns a list of AbstractPorts?
        #
        pass

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
        AbstractNodeInterfaceAPI.createPort(self, port_type, port_name, index=index)

    """ PARAMETERS """
    def parameter(self, parameter_path):
        return AbstractNodeInterfaceAPI.parameter(self, parameter_path)

    def createParameter(
        self,
        parameter_type,
        name="parameter",
        value=None,
        parameter_parent=None
    ):
        parameter = AbstractNodeInterfaceAPI.createParameter(
            self,
            parameter_type,
            parameter_parent=parameter_parent,
            name=name,
            value=value
        )
        return parameter

    def parameterValue(self, path):
        return

    def setParameterValue(self, path, value):
        return

    """ PROPERTIES """
    def node(self):
        return self._node

    def setNode(self, node):
        self._node = node

    def name(self):
        return AbstractNodeInterfaceAPI.name(self)

    def setName(self, name):
        AbstractNodeInterfaceAPI.setName(self, name)

    def type(self):
        return AbstractNodeInterfaceAPI.type(self)

    def setType(self, type):
        AbstractNodeInterfaceAPI.setType(self, type)

    """ ARBITRARY ARGS"""
    def args(self):
        return self._args

    def getArg(self, arg):
        self.args()[arg]

    def setArgValue(self, arg, value):
        self.args()[arg] = value

    def removeArg(self, arg):
        self.args().pop(arg, None)


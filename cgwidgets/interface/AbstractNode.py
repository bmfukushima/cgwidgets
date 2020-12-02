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
        parent_node = AbstractNodeInterfaceAPI.parent(self.node())
        return AbstractNode(parent_node)

    def setParent(self, parent):
        # update dcc
        AbstractNodeInterfaceAPI.setParent(self.node(), parent)

    """ CHILDREN """
    def hasChildren(self):
        has_children = True if 0 < len(AbstractNodeInterfaceAPI.children(self.node())) else False
        return has_children

    def children(self):
        children = AbstractNodeInterfaceAPI.children(self.node())

        return [AbstractNode(child) for child in children]

    def pos(self):
        AbstractNodeInterfaceAPI.pos(self.node())

    def setPos(self, pos):
        """
        Sets the position of the node in the nodegraph.

        Args:
            pos (QPoint)
        """
        AbstractNodeInterfaceAPI.setPos(self.node(), pos)

    """ PORTS """
    # TODO setup node ports
    """
    create Input
    create Output
    insert Input
    insert Output
    getNumInputPorts
    getNumOutputPorts
    """
    def createPort(self, port_type, port_name=None, index=None):
        """
        Creates an port on the node of the specified type.

        Args:
            port_type (AbstractPort.TYPE): type of port to create,
                0 = output
                1 = input
            port_name (string):
            index (int):
        """
        AbstractNodeInterfaceAPI.createPort(self.node(), port_type, port_name, index=index)

    def ports(self, port_type=None):
        """
        Returns all of the ports of the specified type.

        If none specified will return input and output ports

        Args:
            port_type (AbstractPort.TYPE): type of port to create,
                0 = output
                1 = input
        """
        AbstractNodeInterfaceAPI.ports(self.node(), port_type)
        # get all input ports AbstractNodeInterfaceAPI
        # AbstractPortInterfaceAPI...

        # returns a list of AbstractPorts?
        #
        pass

    def getOutputPorts(self):
        pass

    """ ARGS """
    def node(self):
        return self._node

    def setNode(self, node):
        self._node = node

    def name(self):
        return AbstractNodeInterfaceAPI.name(self.node())

    def setName(self, name):
        AbstractNodeInterfaceAPI.setName(self.node(), name)

    def type(self):
        return AbstractNodeInterfaceAPI.type(self.node())

    def setType(self, type):
        AbstractNodeInterfaceAPI.setType(self.node(), type)

    """ ARBITRARY ARGS"""
    def args(self):
        return self._args

    def getArg(self, arg):
        self.args()[arg]

    def setArgValue(self, arg, value):
        self.args()[arg] = value

    def removeArg(self, arg):
        self.args().pop(arg, None)


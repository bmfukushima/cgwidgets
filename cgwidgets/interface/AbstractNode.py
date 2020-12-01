from cgwidgets.interface import AbstractNodeInterfaceAPI


class AbstractNode(object):
    """
    Arbitrary node class.  DCC specific nodes should be converted into a node of this type.

    Setters on this Node should be going through the AbstractNodeInterfaceAPI,
    to choose which DCC to use to do the setting.
    Args:
        node (node): current DCC node
        parent (node): current parent node
        children (list): of nodes

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
        return AbstractNodeInterfaceAPI.parent(self.node())

    def setParent(self, parent):
        # update dcc
        AbstractNodeInterfaceAPI.setParent(self.node(), parent)

    """ CHILDREN """
    def hasChildren(self):
        has_children = True if 0 < len(AbstractNodeInterfaceAPI.children(self.node())) else False
        return has_children

    def children(self):
        return AbstractNodeInterfaceAPI.children(self.node())

    def pos(self):
        AbstractNodeInterfaceAPI.children(self.node())

    def setPos(self, pos):
        """
        Sets the position of the node in the nodegraph.

        Args:
            pos (QPoint)
        """
        AbstractNodeInterfaceAPI.setPos(self.node(), pos)

    """ PORTS """
    def getInputPorts(self):
        pass

    def getOutputPorts(self):

    """ ARGS """
    def node(self):
        return self._node

    def setNode(self, node):
        self._node = node

    """ ARBITRARY ARGS"""
    def args(self):
        return self._args

    def getArg(self, arg):
        self.args()[arg]

    def setArgValue(self, arg, value):
        self.args()[arg] = value

    def removeArg(self, arg):
        self.args().pop(arg, None)


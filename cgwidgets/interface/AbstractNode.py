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
        node=None,
        args=None,
        children=None,
        is_pubescent=False,
        e_female_ports=None,
        e_male_ports=None,
        i_female_ports=None,
        i_male_ports=None,
        name='node',
        parent=None,
        pos=QPoint(1, 1),
        root_parameter=None,
        _type=None
    ):
        # initialize args
        if not node:
            node = self
        self._node = node
        self._parent = parent
        if parent:
            self.setParent(parent)
        # how to if no parent get root item?
        self._pos = pos
        if not root_parameter:
            from cgwidgets.interface import AbstractParameter
            root_parameter = AbstractParameter(None, name='root')
        self._root_parameter = root_parameter
        self._type = _type

        # children
        self._is_pubescent = is_pubescent
        if not children:
            self._children = []

        # ports
        if not e_male_ports:
            self._e_male_ports = []
        if not e_female_ports:
            self._e_female_ports = []
        if not i_male_ports:
            self._i_male_ports = []
        if not i_female_ports:
            self._i_female_ports = []
        self._name = name

        # initialize arbitrary args
        if args:
            self._args = args
        else:
            self._args = {}

    def __name__(self):
        return "AbstractNode"

    def log(self, tabLevel=-1):

        output = ""
        tabLevel += 1

        for i in range(tabLevel):
            output += "\t"

        output += "|------  " + self._name + "\n"

        for child in self.children():
            output += child.log(tabLevel)

        tabLevel -= 1
        output += "\n"

        return output

    def __repr__(self):
        return self.log()

    def __str__(self):
        args = {
            'parent':self.parent(),
            'node_type':self.type(),
            'has_children':self.hasChildren(),
            'children':self.children(),
            'node_name':self.name(),
        }
        if self.parent():
            args['parent'] = self.parent().name()
        output = """
        -------  ABSTRACT NODE API  -------
        parent === {parent}
        node name === {node_name}
        node type === {node_type}
        has children === {has_children}
        children === {children}
        """.format(**args)

        #print(output)
        return output

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
    def isPubescent(self):
        return self._is_pubescent

    def setIsPubescent(self, enabled):
        self._is_pubescent = enabled

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
        if child in self.children():
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
    def ports(self, port_gender=None):
        """
        Returns all of the ports of the specified type.

        If none specified will return FEMALE and MALE ports

        Args:
            port_gender (AbstractPort.TYPE): type of port to create,
                0 = MALE
                1 = FEMALE
        """
        from cgwidgets.interface import AbstractPort

        if TRANSLATE:
            ports = AbstractNodeInterfaceAPI.ports(self, port_gender)
        else:
            if port_gender == AbstractPort.eFEMALE:
                ports = self._e_female_ports
            elif port_gender == AbstractPort.eMALE:
                ports = self._e_male_ports
            elif port_gender == AbstractPort.iFEMALE:
                ports = self._i_female_ports
            elif port_gender == AbstractPort.iMALE:
                ports = self._i_male_ports
        return ports

    def createPort(self, port_gender, port_name=None, index=None):
        """
        Creates an port on the node of the specified type.

        Args:
            port_gender (AbstractPort.TYPE): type of port to create,
                0 = MALE
                1 = FEMALE
            port_name (string):
            index (int):
        """

        if not index:
            index = len(self.ports(port_gender=port_gender))

        if TRANSLATE:
            port = AbstractNodeInterfaceAPI.createPort(self, port_gender, port_name, index=index)
        else:
            # todo setup universal port constructor
            from cgwidgets.interface import AbstractPort

            port = AbstractPort(node=self, gender=port_gender, name=port_name, index=index)
            self.ports(port_gender=port_gender).insert(index, port)
        return port

    """ PARAMETERS """
    def rootParameter(self):
        if TRANSLATE:
            self._root_parameter = AbstractNodeInterfaceAPI.rootParameter()
        return self._root_parameter

    def parameter(self, parameter_path):
        if TRANSLATE:
            parameter = AbstractNodeInterfaceAPI.parameter(self, parameter_path)
        else:
            # todo setup get child
            # search from root parameter?
            parameter = self.rootParameter().child(parameter_path)
        return parameter

    def createParameter(
        self,
        parameter_type,
        name="parameter",
        value=None,
        parent=None
    ):
        if TRANSLATE:
            parameter = AbstractNodeInterfaceAPI.createParameter(
                node=self,
                type=parameter_type,
                parent=parent,
                name=name,
                value=value
            )
        else:
            from cgwidgets.interface import AbstractParameter
            parameter = AbstractParameter(
                node=self,
                type=parameter_type,
                parent=parent,
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


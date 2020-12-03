from cgwidgets.interface import AbstractParameterInterfaceAPI


class AbstractParameter(object):
        """
        parameter (Parameter): instance of DCC parameter
        name (string): display name of parameter
        path (string): dcc path to parameter
            ie AbstractNode1.Group.foo
            Note:
                setting the path will reparent the parameter
        """
        GROUP = 0
        STRING = 1
        INTEGER = 2
        def __init__(self, parameter, path=None, name=None):
            self._parameter = parameter

        def parameter(self):
            return self._parameter

        def setParameter(self, parameter):
            self._parameter = parameter

        def name(self):
            return AbstractParameterInterfaceAPI.name(self)

        def setName(self, name):
            AbstractParameterInterfaceAPI.setName(self, name)

        def value(self, frame=0):
            return AbstractParameterInterfaceAPI.value(self, frame=frame)

        def setValue(self, value, frame=0):
            AbstractParameterInterfaceAPI.setValue(self, value, frame=frame)

        """ HIERARCHY """
        def path(self):
            return AbstractParameterInterfaceAPI.path(self)

        def setPath(self, path):
            AbstractParameterInterfaceAPI.setPath(self, path)

        def child(self, child_name):
            child = AbstractParameterInterfaceAPI.child(self, child_name)
            return child

        def childAtIndex(self, index):
            child = AbstractParameterInterfaceAPI.childAtIndex(self, index)
            return child

        def children(self):
            children = AbstractParameterInterfaceAPI.children(self)
            return children

        def parent(self):
            parent = AbstractParameterInterfaceAPI.parent(self)
            return parent


        # todo """ setup these """

        def node(self):
            return AbstractParameterInterfaceAPI.node(self)

        def type(self):
            return AbstractParameterInterfaceAPI.type(self)

        def setType(self, type):
            AbstractParameterInterfaceAPI.setType(self, type)

        """ ARBITRARY ARGS"""

        def args(self):
            return self._args

        def getArg(self, arg):
            self.args()[arg]

        def setArgValue(self, arg, value):
            self.args()[arg] = value

        def removeArg(self, arg):
            self.args().pop(arg, None)



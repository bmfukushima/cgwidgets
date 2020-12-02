from cgwidgets.interface import AbstractParameterInterfaceAPI


class AbstractParameter(object):
        """

        """
        GROUP = 0
        STRING = 1
        INTEGER = 2
        def __init__(self, parameter):
            self._parameter = parameter

        def parameter(self):
            return self._parameter

        def setParameter(self, parameter):
            self._parameter = parameter

        def value(self, frame=0):
            return AbstractParameterInterfaceAPI.value(self, frame=frame)

        def setValue(self, value, frame=0):
            AbstractParameterInterfaceAPI.setValue(self, value, frame=frame)

        # todo """ setup these """

        def node(self):
            return AbstractParameterInterfaceAPI.node(self)

        def type(self):
            return AbstractParameterInterfaceAPI.type(self)

        def setType(self, type):
            AbstractParameterInterfaceAPI.setType(self, type)

        def name(self):
            return AbstractParameterInterfaceAPI.name(self)

        def setName(self, name):
            AbstractParameterInterfaceAPI.setName(self, name)

        """ ARBITRARY ARGS"""

        def args(self):
            return self._args

        def getArg(self, arg):
            self.args()[arg]

        def setArgValue(self, arg, value):
            self.args()[arg] = value

        def removeArg(self, arg):
            self.args().pop(arg, None)



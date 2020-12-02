from cgwidgets.interface import AbstractParameterInterfaceAPI


class AbstractParameter(object):
        """

        """

        def node(self):
            return AbstractParameterInterfaceAPI.node(self)

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



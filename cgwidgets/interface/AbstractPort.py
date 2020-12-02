from cgwidgets.interface import AbstractPortInterfaceAPI


class AbstractPort(object):
        """
        gender (data FEMALE)
        name
        connected ports
        index

        Arbitrary port class.  DCC specific ports should be using this as a wrapper.

        Setters on this port should be going through the AbstractPortInterfaceAPI,
        to choose which DCC to use to do the setting.

        Everytime a port is returned, this will use an instance of AbstractPort as
        a wrapper for that dcc specific port.

        Args:
            port (port): current DCC port

        """
        MALE = 0
        FEMALE = 1

        def __init__(self, port, args=None):
            # initialize port
            self.setPort(port)

            # initialize arbitrary args
            if args:
                self._args = args
            else:
                self._args = {}

        """ PORT """
        # TODO Setup Port connections
        """
        getConnectedPorts
        isConnected
        connect
        disconnect
        """
        def connect(self, port_a, port_b):
            AbstractPortInterfaceAPI.connect(port_a, port_b)

        """ ARGS """
        def port(self):
            return self._port

        def setPort(self, port):
            self._port = port

        def node(self):
            return AbstractPortInterfaceAPI.node(self)

        def name(self):
            return AbstractPortInterfaceAPI.name(self)

        def gender(self):
            return AbstractPortInterfaceAPI.gender(self)

        def setName(self, name):
            AbstractPortInterfaceAPI.setName(self, name)

        """ ARBITRARY ARGS"""

        def args(self):
            return self._args

        def getArg(self, arg):
            self.args()[arg]

        def setArgValue(self, arg, value):
            self.args()[arg] = value

        def removeArg(self, arg):
            self.args().pop(arg, None)



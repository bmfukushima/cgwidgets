import sys

from cgwidgets.interface import AbstractPortInterfaceAPI

dcc_path = sys.argv[0].lower()
TRANSLATE = False
for dcc in ['katana', 'nuke', 'houdini', 'mari']:
    if dcc in dcc_path:
        TRANSLATE = True

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

        def __init__(
            self,
            args=None,
            gender=None,
            index=None,
            name='port',
            node='None',
            port=None,

        ):
            # initialize attrs
            if not port:
                port = self
            self._port = port
            self._gender = gender
            self._name = name
            self._node = node
            self._index = index

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
        def index(self):
            if TRANSLATE:
                self._index = AbstractPortInterfaceAPI.index(self)
            return self._index

        def setIndex(self, index):
            if TRANSLATE:
                self._index = AbstractPortInterfaceAPI.setIndex(index)
            else:
                self._index = index

        def port(self):
            return self._port

        def setPort(self, port):
            self._port = port

        def node(self):
            if TRANSLATE:
                self._node = AbstractPortInterfaceAPI.node(self)

            return self._node

        def gender(self):
            if TRANSLATE:
                self._gender = AbstractPortInterfaceAPI.gender(self)
            return self._gender

        def setGender(self, gender):
            self._gender = gender

        def name(self):
            if TRANSLATE:
                self._name = AbstractPortInterfaceAPI.name(self)
            return self._name

        def setName(self, name):
            if TRANSLATE:
                self._name = AbstractPortInterfaceAPI.setName(self, name)
            else:
                self._name = name

        """ ARBITRARY ARGS"""

        def args(self):
            return self._args

        def getArg(self, arg):
            self.args()[arg]

        def setArgValue(self, arg, value):
            self.args()[arg] = value

        def removeArg(self, arg):
            self.args().pop(arg, None)



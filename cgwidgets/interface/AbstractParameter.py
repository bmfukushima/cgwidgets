"""

TODO:
    getting parameters...
        still need to set up path splitting
    setPath
    node
    setType
"""

import sys

from cgwidgets.interface import AbstractParameterInterfaceAPI

dcc_path = sys.argv[0].lower()
TRANSLATE = False
for dcc in ['katana', 'nuke', 'houdini', 'mari']:
    if dcc in dcc_path:
        TRANSLATE = True


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
        def __init__(
            self,
            children=None,
            name="new_param",
            node=None,
            parameter=None,
            parent=None,
            path=None,
            type=None,
            value=None
        ):
            # setup self
            if not parameter:
                parameter = self
            self._parameter = parameter

            # set up defaults attrs
            if not children:
                children = []
            self._children = children
            self._name = name
            self._node = node
            self._path = path
            self._type = type
            self._value = value

            self._parent = parent
            if parent:
                self.setParent(parent)
            elif node:
                self.setParent(node.rootParameter())

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

        def parameter(self):
            if TRANSLATE:
                return self._parameter

        def setParameter(self, parameter):
            self._parameter = parameter

        def name(self):
            if TRANSLATE:
                self._name = AbstractParameterInterfaceAPI.name(self)
            return self._name

        def setName(self, name):
            if TRANSLATE:
                self._name = AbstractParameterInterfaceAPI.setName(self, name)
            else:
                self._name = name

        def value(self, frame=0):
            if TRANSLATE:
                self._value = AbstractParameterInterfaceAPI.value(self, frame=frame)
            return self._value

        def setValue(self, value, frame=0):
            """
            :param value:
            :param frame:
            :return:

            # todo set up animated values on frames
            """
            if TRANSLATE:
                self._value = AbstractParameterInterfaceAPI.setValue(self, value, frame=frame)
            else:
                self._value = value

        """ HIERARCHY """
        def path(self):
            if TRANSLATE:
                self._path = AbstractParameterInterfaceAPI.path(self)
            # todo check children/ parent for full path?
            return self._path

        def setPath(self, path):
            if TRANSLATE:
                self._path = AbstractParameterInterfaceAPI.setPath(self, path)
            else:
                # todo setPath reparent to this hierarchy
                self._path = path
        #
        def insertChild(self, index, child):
            """
            Inserts a child parameter

            Args:
                index (int)
                child (AbstractParameter)
            """
            # remove child from old parent
            child.parent().removeChild(child)

            # insert child under this item
            if TRANSLATE:
                AbstractParameterInterfaceAPI.insertChild(self, index, child)
            else:
                #child.setParent(self, index=index)
                self.children().insert(index, child)

            # insert update childs parent
            # note: updating with setParent here will go into infinite recursion
            #           as setParent calles insertChild
            child._parent = self
        #
        def removeChild(self, child):
            if not self.hasChildren(): return

            if TRANSLATE:
                AbstractParameterInterfaceAPI.removeChild(self, child)

            if child in self.children():
                self.children().remove(child)

        def child(self, child_name):
            """
            Returns the first child with the specified name

            Args:
                child_name (str)

            Return (Abstract Parameter)
            """

            # preflight
            if not self.hasChildren(): return None

            # get child
            if TRANSLATE:
                child = AbstractParameterInterfaceAPI.child(self, child_name)
            else:
                for child in self.children():
                    if child.name() == child_name:
                        break
            return child

        def childAtIndex(self, index):
            """
            Returns the child at the specified index.

            If no children are present, or the index is out of range, this will
            return None

            Args:
                index (int)

            Returns (AbstractParameter | None)
            :param index:
            :return:
            """
            #child = AbstractParameterInterfaceAPI.childAtIndex(self, index)
            if self.hasChildren():
                if index in range(len(self.children())):
                    child = self.children()[index]
                    return child
                else:
                    # index out of range
                    return None
            else:
                # no children
                print('*PROTOSS VOICE* Need more babies')
                return None

        def children(self):
            if TRANSLATE:
                self._children = AbstractParameterInterfaceAPI.children(self)
            return self._children

        def hasChildren(self):
            self._has_children = True if 0 < len(self.children()) else False
            return self._has_children

        def parent(self):
            if TRANSLATE:
                self._parent = AbstractParameterInterfaceAPI.parent(self)
            return self._parent
        #
        def setParent(self, parent, index=None):
            """
            Args:
                parent (AbstractParameter)
                index (int)
            """
            # remove child from old parent
            #print('name == ', self.name())
            if self.parent():
                self.parent().removeChild(self)

            # manipulate data structures
            if TRANSLATE:
                self._parent = AbstractParameterInterfaceAPI.setParent(parent, index)
            else:
                self._parent = parent
                num_children = len(self.parent().children())
                if not index:
                    index = num_children
                elif num_children < index:
                    index = num_children

            # insert child into new parent
            parent.insertChild(index, self)

        # todo """ setup these """

        def node(self):
            if TRANSLATE:
                self._node = AbstractParameterInterfaceAPI.node(self)
            return self._node

        def type(self):
            if TRANSLATE:
                self._type = AbstractParameterInterfaceAPI.type(self)

            return self._type

        def setType(self, type):
            if TRANSLATE:
                self._type = AbstractParameterInterfaceAPI.setType(self, type)
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



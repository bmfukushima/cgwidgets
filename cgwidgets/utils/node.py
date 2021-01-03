import sys
dcc_path = sys.argv[0]
# /opt/katana/4.0v1/bin/python/Main/Main.pyc

class Node(object):
    """

    Attributes:
        delegate_widget (QWidget): Widget to be shown when this item is
            selected
        dynamic_widget_base_class (QWidget): Widget to be shown when this item is
            selected if the Tansu is in DYNAMIC mode.
        column_data (dict): Dictionary of key pair values relating to the column name,
            and the value for the item in that column.  Special column names are
                name
                value
                items_list
    """
    def __init__(self, parent=None):
        self._children = []
        self._parent = parent

        # default parent
        if parent is not None:
            parent.addChild(self)

    def addChild(self, child):
        self._children.append(child)

    def insertChild(self, position, child):

        if position < 0 or position > len(self._children):
            return False

        self._children.insert(position, child)
        child._parent = self
        return True

    def removeChild(self, position):

        if position < 0 or position > len(self._children):
            return False

        child = self._children.pop(position)
        child._parent = None

        return True

    def childCount(self):
        return len(self._children)

    def children(self):
        return self._children

    def child(self, row):
        try:
            return self._children[row]
        except:
            return None

    def parent(self):
        return self._parent

    def getNodeFromName(name):
        """ Returns a node, from the given name """
        return


class NodeAPI(object):
    def getAllNodes(self):
        """
        Returns a list of all of the nodes
        """
        return
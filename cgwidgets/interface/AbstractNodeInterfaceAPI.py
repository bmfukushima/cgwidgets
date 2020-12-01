"""
When a node calls a specific function that would normally be called through
a DCC's API.  This translator intercepts the signal, and chooses the correct
DCC's API to use.
NOTE:
    <node> is always the DCC node
"""

import sys
#from cgwidgets.interface import katana

# get DCC
dcc_path = sys.argv[0]

KATANA = 'KATANA'
NUKE = 'NUKE'
MARI = 'MARI'
HOUDINI = 'HOUDINI'

if 'katana' in dcc_path:
    import katana as DCC
if 'nuke' in dcc_path:
    import nuke as DCC
if 'houdini' in dcc_path:
    import houdini as DCC
if 'mari' in dcc_path:
    import mari as DCC

""" NODE API"""
def getNodeFromName(name):
    """ returns an abstract node"""

    DCC.getNodeFromName(name)

# def convertDCCNodeToAbstractNode(node):
#     """
#     Converts an existing DCC node type into an ArbitraryNode type
#
#     Args:
#         node (DCC NODE):
#     Returns (AbstractNode)
#     """
#     abstract_node = DCC.convertDCCNodeToAbstractNode(node)
#     return abstract_node

""" HIERARCHY """
def parent(node):
    """
    Gets the current nodes parent

    Returns (node): returns the parent node
    """
    DCC.parent(node)

def setParent(node, parent):
    """
    Sets the current nodes parent

    Args:
        node (dccNode): node to set the parent of
        parent (dccNode): node to set the parent to
    """
    DCC.setParent(node, parent)

def children(node):
    """
    Returns a list of all of the children of specified node
    """
    return DCC.children()

""" POSITION """
def pos(node):
    """
    Returns the nodes position as a QPoint
    """
    return DCC.pos(node)

def setPos(node, pos):
    """
    Sets the position of the node

    Args:
        pos (QPoint): position to set the node at
    """
    DCC.setPos(node, pos)




def test():
    print(DCC)
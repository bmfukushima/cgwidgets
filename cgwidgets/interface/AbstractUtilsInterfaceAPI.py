import sys
from qtpy.QtWidgets import QApplication
from qtpy.QtCore import QPoint

dcc_path = sys.argv[0].lower()
TRANSLATE = False
for dcc in ['katana', 'nuke', 'houdini', 'mari']:
    if dcc in dcc_path:
        TRANSLATE = True

# get DCC
dcc_path = sys.argv[0].lower()
KATANA = 'KATANA'
NUKE = 'NUKE'
MARI = 'MARI'
HOUDINI = 'HOUDINI'

if 'katana' in dcc_path:
    from cgwidgets.interface import katana as dcc
# todo setup other translators
if 'nuke' in dcc_path:
    from cgwidgets.interface.nuke import node as dccnode
if 'houdini' in dcc_path:
    from cgwidgets.interface.houdini import node as dccnode
if 'mari' in dcc_path:
    from cgwidgets.interface.mari import node as dccnode

from cgwidgets.interface.AbstractNodeInterfaceAPI import ports, setPos
from cgwidgets.interface.AbstractPort import AbstractPort

def processAllEvents():
    if TRANSLATE:
        dcc.utils.processAllEvents()
    else:
        QApplication.processEvents()


def disconnectNode(node, input=False, output=False, reconnect=False):
    """
    Disconnects the node provide from all other nodes.  The same
    as hitting 'x' on the keyboard... or "Extract Nodes" except this
    is in the NodegraphWidget, not the NodegraphAPI. so kinda hard
    to call... so I made my own...

    Args:
        node (node): Node to be extracted
        input (bool): If true disconnect all input ports
        output (bool): If true disconnect all output ports
        reconnect (bool): If true, will rewire the node graphs input/output ports
            will only work if input and output are true
    """
    if reconnect is True:
        if input is True and output is True:
            input_port = ports(node, AbstractPort.eFEMALE)[0]
            upstream_port = input_port.connectedPorts()[0]
            output_port = ports(node, AbstractPort.eMALE)[0]
            downstream_port = output_port.connectedPorts()[0]

            if upstream_port and downstream_port:
                # reconnect wire
                upstream_port.connect(downstream_port)

    if input is True:
        for input_port in ports(node, AbstractPort.eFEMALE):
            output_ports = input_port.connectedPorts()
            for port in output_ports:
                port.disconnect(input_port)

    if output is True:
        for output in ports(node, AbstractPort.eMALE):
            input_ports = output.connectedPorts()
            for port in input_ports:
                port.disconnect(output)


def connectInsideGroup(node_list, parent_node):
    """
    Connects all of the nodes inside of a specific node in a linear fashion

    Args:
        node_list (list): list of nodes to be connected together, the order
            of the nodes in this list, will be the order that they are connected in
        parent_node (node): node have the nodes from the node_list
            wired into.
    """

    send_port = ports(parent_node, AbstractPort.iMALE)[0]
    return_port = ports(parent_node, AbstractPort.iFEMALE)[0]
    if len(node_list) == 0:
        send_port.connect(return_port)
    elif len(node_list) == 1:
        ports(node_list[0], AbstractPort.eMALE)[0].connect(return_port)
        ports(node_list[0], AbstractPort.eFEMALE)[0].connect(send_port)
    elif len(node_list) == 2:
        ports(node_list[0], AbstractPort.eFEMALE)[0].connect(send_port)
        ports(node_list[1], AbstractPort.eMALE)[0].connect(return_port)
        ports(node_list[0], AbstractPort.eMALE)[0].connect(ports(node_list[1], AbstractPort.eFEMALE)[0])
        setPos(node_list[0], QPoint(0, 100))

    elif len(node_list) > 2:
        for index, node in enumerate(node_list[:-1]):
            node.getOutputPortByIndex(0).connect(node_list[index+1].getInputPortByIndex(0))
            setPos(node, QPoint(0, index * -100))

        ports(node_list[0], AbstractPort.eFEMALE)[0].connect(send_port)
        ports(node_list[-1], AbstractPort.eMALE)[0].connect(return_port)
        setPos(node_list[-1], QPoint(0, len(node_list) * -100))

# todo
def insertNode(node, parent_node):
    """
    Inserts the node in the correct position in the Nodegraph, and then
    wires the node into that position.

    Note:
        When this happens, the node has already been connected..
        Thus the awesome -2

    Args:
        node (node): Current node to be inserted
        parent_node (node): The current nodes parent
    """
    # get previous port / position

    if len(parent_node.getChildren()) == 1:
        # previous port
        previous_port = parent_node.getSendPort('in')

        # position
        pos = (0, 0)
    else:
        # get previous node
        node_references = parent_node.getParameter('nodeReference')
        previous_node_name = node_references.getChildByIndex(node_references.getNumChildren() - 2)
        previous_node = NodegraphAPI.GetNode(previous_node_name.getValue(0))

        # previous port
        previous_port = previous_node.getOutputPortByIndex(0)

        # setup pos
        current_pos = NodegraphAPI.GetNodePosition(previous_node)
        xpos = current_pos[0]
        ypos = current_pos[1] - 100
        pos = QPoint(xpos, ypos)

    # wire node
    previous_port.connect(node.getInputPortByIndex(0))
    node.getOutputPortByIndex(0).connect(parent_node.getReturnPort('out'))

    # position node
    setPos(node, pos)


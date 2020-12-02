from qtpy.QtCore import QPoint

from cgwidgets.interface import (
    AbstractNode,
    AbstractPort,
    AbstractParameter,
    AbstractNodeInterfaceAPI,
)

# create node
node = AbstractNodeInterfaceAPI.createNode('Group', AbstractNodeInterfaceAPI.getRootNode())
node.setName("AbstractNode")

# create port
node.createPort(AbstractPort.MALE, "o0")
node.createPort(AbstractPort.FEMALE, "i0")
node.createPort(AbstractPort.FEMALE, "insert_this", index=0)
node.createPort(AbstractPort.FEMALE)
# get ports
input_ports = node.ports(AbstractPort.FEMALE)
output_ports = node.ports(AbstractPort.MALE)

# todo connect port

parent = node.parent()
node_type = node.type()
has_children = node.hasChildren()
children = node.children()
node_name = node.name()

# position node
pos = node.pos()
node.setPos(QPoint(100, 50))

# get parameters
parameter = node.createParameter(
    AbstractParameter.GROUP,
    name="Group"
)
# create child parameter?
child_parameter = AbstractNodeInterfaceAPI.createParameter(
        node,
        AbstractParameter.STRING,
        parameter_parent=parameter,
        name="foo",
        value="bar")

child_parameter_value = child_parameter.value()

print ('-------  ABSTRACT NODE API  -------')
print('node name === ', node_name)
print('node type === ', node_type)

print('child_parameter === ', child_parameter)
print('child parameter value === ', child_parameter_value)

print('input ports === ', input_ports)
print('output ports ===', output_ports)
print('parent === ', parent)
print('has children ===', has_children)
print('children ===', children)


""" NodegraphAPI """
print ('-------  ABSTRACT NODEGRAPH API  -------')
# get node from name
node = AbstractNodeInterfaceAPI.getNodeFromName(node_name)

# get root node
root_node = AbstractNodeInterfaceAPI.getRootNode()


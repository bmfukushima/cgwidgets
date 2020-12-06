from qtpy.QtCore import QPoint

from cgwidgets.interface import (
    AbstractNode,
    AbstractPort,
    AbstractParameter,
    AbstractNodeInterfaceAPI,
)

# create node
node = AbstractNodeInterfaceAPI.createNode('Group', parent=AbstractNodeInterfaceAPI.getRootNode())
node.setName("AbstractNode")

child_node = AbstractNodeInterfaceAPI.createNode('Group', parent=node)
child_node.setName("ChildNode")

# position node
pos = node.pos()
node.setPos(QPoint(100, 50))

print(repr(node))
print(child_node)

print ('-------  PORT API  -------')
# create port
node.createPort(AbstractPort.MALE, "o0")
node.createPort(AbstractPort.FEMALE, "i0")
node.createPort(AbstractPort.FEMALE, "insert_this", index=0)
node.createPort(AbstractPort.FEMALE)
# get ports
female_ports = node.ports(AbstractPort.FEMALE)
male_ports = node.ports(AbstractPort.MALE)

# # todo connect port
print('female ports === ', female_ports)
print('male ports ===', male_ports)

# print ('-------  PARAMETER API  -------')
# get parameters

parameter = node.createParameter(
    AbstractParameter.GROUP,
    name="Group",
    parent=node.rootParameter()
)

# create child parameter?
child_parameter = node.createParameter(
        AbstractParameter.STRING,
        parent=parameter,
        name="foo",
        value="bar")

other_param = node.createParameter(
    AbstractParameter.STRING,
    name="try",
    value="hard")

# get param children
node.parameter('Group').child('foo')


# parameter values
node.parameter('Group').child('foo').setValue('test', frame=0)
child_parameter_value = child_parameter.value()
node.parameter('Group.foo').value()

# reparent parameter
other_param.setParent(child_parameter, index=0)

parent = child_parameter.parent()
child = parameter.child('foo')
child_by_index = parameter.childAtIndex(0)
children = parameter.children()
#insertChild
#setParent
#remove
## set path...
print(repr(node.rootParameter()))
# print('\n\n')
# print('child_parameter === ', child_parameter)
# print('child parameter value === ', child_parameter_value)
# print('parent == ', parent)
# print('child == ', child)
# print('child_by_index == ', child_by_index)
# print('children == ', children)
#
# """ NodegraphAPI """
# print ('-------  ABSTRACT NODEGRAPH API  -------')
# # get node from name
# node = AbstractNodeInterfaceAPI.getNodeFromName(node_name)
#
# # get root node
# root_node = AbstractNodeInterfaceAPI.getRootNode()


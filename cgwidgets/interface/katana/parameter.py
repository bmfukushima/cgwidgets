import NodegraphAPI

def name(parameter):
    return parameter.getName()

def setName(parameter, name):
    parameter.setName(name)

""" HIERARCHY """
def path(parameter):
    path = parameter.getFullPath()
    full_path = '.'.join(path.split('.')[:-1])
    return full_path

# todo not set up
def setPath(parameter, path):
    # reparent parameter to path provided
    param_name = parameter.name()
    parameter.setPath(parameter, path)

def child(parameter, child_name):
    child = parameter.getChild(child_name)
    return child

def children(parameter):
    # import / initialize
    children = parameter.getChildren()
    return children

def parent(parameter):
    # import / initialize
    parent = parameter.getParent()
    return parent

""" ARGS """
def value(parameter, frame=0):
    value = parameter.getValue(frame)
    return value

def setValue(parameter, value, frame=0):
    parameter.setValue(value, frame)
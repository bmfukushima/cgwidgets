import NodegraphAPI

def name(parameter):
    return parameter.getName()

def setName(parameter, name):
    parameter.setName(name)
    name = parameter.getName()
    return name

""" HIERARCHY """
def path(parameter):
    path = parameter.getFullPath()
    full_path = '.'.join(path.split('.')[:-1])
    return full_path

def setPath(parameter, path):
    # todo set path (katana)
    # reparent parameter to path provided
    param_name = parameter.name()
    parameter.setPath(parameter, path)
    return path
# todo
def insertChild(parameter, index, child):
    from Katana import UniqueName
    row = index
    param = child
    # current_parent_param = child.parent()
    new_parent_param = parameter

    param_name = UniqueName.GetUniqueName(param.getName(), new_parent_param.getChild)
    # convert param to xml
    param_xml = param.buildXmlIO()
    param_xml.setAttr('name', param_name)

    # # delete old param
    # current_parent_param.deleteChild(param)

    # create new param
    new_param = new_parent_param.createChildXmlIO(param_xml)
    new_parent_param.reorderChild(new_param, row)

# todo
def removeChild(parameter, child):
    # todo remove child
    parameter.deleteChild(child)

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
    value = parameter.getValue(frame)
    return value
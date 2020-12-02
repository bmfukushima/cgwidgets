import NodegraphAPI

def value(parameter, frame=0):
    print('param... ')
    print(parameter, frame)
    value = parameter.getValue(frame)
    return value

def setValue(parameter, value, frame=0):
    parameter.setValue(value, frame)
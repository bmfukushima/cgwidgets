def isWidgetDescendantOf(widget, parent, ancestor):
    """
    Determines if a widget is a descendant of another widget
    Args:
        widget (QWidget): widget to start searching from
        parent (QWidget): parent of the widget... need this to avoid garbage cleanup
        ancestor (QWidget): widget to see if it is an ancestor of

    Returns:

    """
    if widget:
        if widget == ancestor:
            return True
        else:
            if parent:
                return isWidgetDescendantOf(parent, parent.parent(), ancestor)
            else:
                return False
    else:
        return False

# def isWidgetDescendantOf(widget, parent):
#     """
#     Determines if a widget is a descendant of another widget
#     Args:
#         widget (QWidget): widget to start searching from
#         parent (QWidget): widget to check if it is an ancestor of
#
#     Returns:
#
#     """
#     if widget:
#         if widget == parent:
#             return True
#         else:
#             if widget.parent():
#                 return isWidgetDescendantOf(widget.parent(), parent)
#             else:
#                 return False
#     else:
#         return False

# for some reason... need to do this really stupid for PySide2 cleanup...
# def getWidgetAncestor(widget, parent, instance_type):
#     """
#     Recursively searches up from the current widget
#     until an widget of the specified instance is found
#
#     Args:
#         widget (QWidget): widget to search from
#         instance_type (object): Object type to find
#     """
#
#     if isinstance(widget, instance_type):
#         return widget
#     else:
#         #parent = widget.parent()
#         if parent:
#             return getWidgetAncestor(widget.parent(), widget.parent().parent(), instance_type)
#         else:
#             return None


def getWidgetAncestor(widget, instance_type):
    """
    Recursively searches up from the current widget
    until an widget of the specified instance is found

    Args:
        widget (QWidget): widget to search from
        instance_type (object): Object type to find
    """

    if isinstance(widget, instance_type):
        return widget
    else:
        parent = widget.parent()
        if parent:
            return getWidgetAncestor(widget.parent(), instance_type)
        else:
            return None


def getWidgetAncestorByName(widget, widget_name):
    """
    Recursively searches up from the current widget
    until an widget of the specified instance is found

    Args:
        widget (QWidget): widget to search from
        widget_name (str): object name returned by __name__
            field of the object.
    """
    if hasattr(widget, '__name__'):
        if widget.__name__() == widget_name:
            return widget
        else:
            parent = widget.parent()
            if parent:
                return getWidgetAncestorByName(widget.parent(), widget_name)
            else:
                return None
    else:
        parent = widget.parent()
        if parent:
            return getWidgetAncestorByName(widget.parent(), widget_name)
        else:
            return None


def getWidgetAncestorByObjectName(widget, widget_name):
    """
    Recursively searches up from the current widget
    until an widget of the specified instance is found

    Args:
        widget (QWidget): widget to search from
        widget_name (str): object name returned by __name__
            field of the object.
    """
    if widget.objectName():
        if widget.objectName() == widget_name:
            return widget
        else:
            parent = widget.parent()
            if parent:
                return getWidgetAncestorByObjectName(widget.parent(), widget_name)
            else:
                return None
    else:
        parent = widget.parent()
        if parent:
            return getWidgetAncestorByObjectName(widget.parent(), widget_name)
        else:
            return None
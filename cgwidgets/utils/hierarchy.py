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


def isWidgetDescendantOfInstance(widget, parent, ancestor):
    """
    Determines if a widget is a descendant of another widget
    Args:
        widget (QWidget): widget to start searching from
        parent (QWidget): parent of the widget... need this to avoid garbage cleanup
        ancestor (Class): widget to see if it is an ancestor of

    Returns:

    """
    if widget:
        if isinstance(widget, ancestor):
            return True
        else:
            if parent:
                return isWidgetDescendantOfInstance(parent, parent.parent(), ancestor)
            else:
                return False
    else:
        return False


def getWidgetsDescendants(layout, descendants=None):
    """ Gets all of the descendants from the item provided

    Args:
        layout (QLayout): to start searching from

    Returns (list): of AbstractDragDropModelItem"""
    if not descendants:
        descendants = []

    if not layout: return descendants
    if not hasattr(layout, "count"):
        layout = layout.layout()

    #self.group_box.layout().itemAt(index).widget()
    for i in range(layout.count()):
        item = layout.itemAt(i)
        # todo check if copyable?
        if hasattr(item, "count"):
            if 0 < item.count():

                descendants += getWidgetsDescendants(item)
        else:
            if item.widget():
                descendants.append(item.widget())

    return descendants


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


# import sys
# from qtpy.QtWidgets import QVBoxLayout, QLabel, QWidget, QApplication
# #from cgwidgets.utils import centerWidgetOnCursor
# app = QApplication(sys.argv)
#
# main = QWidget()
# QVBoxLayout(main)
# for x in range(3):
#     main.layout().addWidget(QLabel(str(x)))
# layout = QVBoxLayout()
# main.layout().addLayout(layout)
# for x in range(2):
#     layout.addWidget(QLabel(str(x)))
#
# main.show()
# #centerWidgetOnCursor(main)
# descendants = getWidgetsDescendants(main.layout())
# print(descendants)
#
#
# sys.exit(app.exec_())
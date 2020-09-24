# https://doc.qt.io/qt-5/model-view-programming.html#model-view-classes
from cgwidgets.widgets.TansuWidget import (
    iDynamicWidget
)


class TansuModelItem(iDynamicWidget):
    """

    Attributes:
        delegate_widget (QWidget): Widget to be shown when this item is
            selected
        dynamic_widget_base_class (QWidget): Widget to be shown when this item is
            selected if the Tansu is in DYNAMIC mode.
    """
    def __init__(self, name, parent=None):
        self._name = name
        self._children = []
        self._parent = parent
        self._delegate_widget = None
        self._dynamicWidgetFunction = None

        self._is_selected = False

        if parent is not None:
            parent.addChild(self)

    def delegateWidget(self):
        return self._delegate_widget

    def setDelegateWidget(self, _delegate_widget):
        self._delegate_widget = _delegate_widget

    def isSelected(self):
        return self._is_selected

    def setSelected(self, selected):
        self._is_selected = selected

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

    def name(self):
        return self._name

    def setName(self, name):
        self._name = name

    def child(self, row):
        return self._children[row]

    def childCount(self):
        return len(self._children)

    def parent(self):
        return self._parent

    def row(self):
        if self._parent is not None:
            return self._parent._children.index(self)

    def log(self, tabLevel=-1):
        output = ""
        tabLevel += 1

        for i in range(tabLevel):
            output += "\t"
        output += "|------" + self._name + "\n"

        for child in self._children:
            output += child.log(tabLevel)

        tabLevel -= 1
        output += "\n"

        return output

    # def __repr__(self):
    #     return self.log()

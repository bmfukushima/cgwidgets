import os

from qtpy.QtWidgets import QWidget

from cgwidgets.widgets import ListInputWidget
from cgwidgets.interface import AbstractNodeInterfaceAPI


class NodeTypeListWidget(ListInputWidget):
    """
    Drop down menu with autocomplete for the user to select
    what Node Type that they wish for the Variable Manager to control
    """
    def __init__(self, parent=None):
        super(NodeTypeListWidget, self).__init__(parent)
        self.previous_text = ""

        self.setUserFinishedEditingEvent(self.indexChanged)
        self.populate(self.__getAllNodes())

        self.setCleanItemsFunction(self.__getAllNodes)
        self.dynamic_update = True

    @staticmethod
    def __getAllNodes():
        node_list = sorted([[node] for node in AbstractNodeInterfaceAPI.getAllNodeTypes()])
        return node_list

    def checkUserInput(self):
        """
        Checks the user input to determine if it is a valid option
        in the current model.  If it is not this will reset the menu
        back to the previous option
        """
        does_node_variable_exist = self.isUserInputValid()
        if does_node_variable_exist is False:
            self.setText(self.previous_text)
            return

    """ VIRTUAL FUNCTIONS """
    def nodeTypeChanged(self, widget, value):
        """
        Needs to be overloaded.

        Args:
            widget (QWidget): This widget
            value (string): current value being set on this widget
        """
        return

    def setNodeTypeChangedEvent(self, function):
        self.nodeTypeChanged = function

    """ EVENTS """
    def mousePressEvent(self, *args, **kwargs):
        self.update()
        return ListInputWidget.mousePressEvent(self, *args, **kwargs)

    def indexChanged(self, widget, value):
        """ When the user selects a node type this will update the display"""
        # preflight
        if self.previous_text == self.text(): return
        """
        without this it randomly allows the user to change to a
        new node type =/
        """
        # preflight checks
        # return if this node type does not exist
        if self.text() not in AbstractNodeInterfaceAPI.getAllNodeTypes().GetNodeTypes(): return

        # run user defined signal
        self.nodeTypeChanged(widget, value)


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication, QLabel, QVBoxLayout
    from qtpy.QtGui import QCursor
    from cgwidgets.widgets import ShojiModelViewWidget
    app = QApplication(sys.argv)

    w = NodeTypeListWidget()
    w.resize(500, 500)

    w.show()
    w.move(QCursor.pos())
    sys.exit(app.exec_())

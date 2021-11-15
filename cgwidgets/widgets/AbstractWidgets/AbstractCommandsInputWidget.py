from .AbstractListInputWidget import AbstractListInputWidget


class AbstractCommandsInputWidget(AbstractListInputWidget):
    """ The Commands Widget allows you to set up a list of executables.
    Each item in the list will correspond to a function that will be run.

    Attributes:
        commandsList (list): of strings of command names.  Each command name
            will have a corresponding function registered to it."""
    def __init__(self, parent=None):
        super(AbstractCommandsInputWidget, self).__init__(parent)
        self._commands_list = []
        self.setUserFinishedEditingEvent(self.userInputCommand)

    """ USER INPUT COMMANDS """
    def userInputCommand(self, widget, command_name):
        """ User has just finished editing text, and a command is going to be executed.

        Args:
            widget (AbstractCommandsInputWidget)
            command_name (str): command to be run from commandsList()"""
        if widget.text() == "": return

        if command_name in self.commandsList():
            command = getattr(self, command_name)
            command()
            widget.setText("")

    def commandsList(self):
        return self._commands_list

    def clearCommandsList(self):
        for command in self.commandsList():
            delattr(self, command)

        self._commands_list = []

    def addCommand(self, command_name, command):
        """ Adds a command to the command list

        Args:
            command_name (str): name of command
            command (func): command to be executed"""
        self.commandsList().append(command_name)
        setattr(self, command_name, command)
        self.populate([[command] for command in self.commandsList()])

    def removeCommand(self, command):
        if command in self.commandsList():
            self.commandsList().remove(command)
            delattr(self, command)


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication
    from cgwidgets.utils import centerWidgetOnScreen, setAsAlwaysOnTop
    app = QApplication(sys.argv)

    widget = AbstractCommandsInputWidget()

    setAsAlwaysOnTop(widget)
    widget.show()
    centerWidgetOnScreen(widget)

    sys.exit(app.exec_())
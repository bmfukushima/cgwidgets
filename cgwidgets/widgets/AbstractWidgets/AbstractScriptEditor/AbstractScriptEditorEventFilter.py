import sys
import os

from qtpy.QtWidgets import QWidget
from qtpy.QtCore import QEvent
from qtpy.QtGui import QKeySequence


from .AbstractScriptEditorWidgets import PopupHotkeyMenu, PopupGestureMenu
from .AbstractScriptEditorUtils import Utils as Locals
from cgwidgets.utils import getJSONData

class AbstractScriptEditorPopupEventFilter(QWidget):
    """ Event Filter for displaying the PopupHotkeys

    This will need to be installed on the main window that the instance of the application is running

    Args:
        main_window (QMainWindow): Main window of the application (ie. widget.window())
        scripts_variable (str): Environment variable that holds the scripts directories"""
    def __init__(self, parent=None, main_window=None, scripts_variable="CGWscripts"):
        super(AbstractScriptEditorPopupEventFilter, self).__init__(parent)
        if not main_window:
            main_window = self.window()

        self._main_window = main_window
        self._scripts_variable = scripts_variable

    """ PROPERTIES """
    def scriptsVariable(self):
        return self._scripts_variable

    def scriptsDirectories(self):
        return os.environ[self.scriptsVariable()].split(":")

    # """ UTILS """
    # def importModules(self):
    #     """ Virtual function to be overwritten.  Can import custom modules
    #     to be run in the script here.
    #
    #     Returns (dict): of locals values"""
    #     return {}

    """ WIDGETS """
    def mainWindow(self):
        return self._main_window

    """ EVENTS """
    def closeEvent(self, *args, **kwargs):
        self._main_window.removeEventFilter(self)
        return QWidget.closeEvent(self, *args, **kwargs)

    def eventFilter(self, obj, event, *args, **kwargs):
        if event.type() == QEvent.KeyPress:
            # get user hotkeys
            for directory in self.scriptsDirectories():
                hotkeys_file_path = "{directory}/hotkeys.json".format(directory=directory)
                self.hotkey_dict = getJSONData(hotkeys_file_path)

                # get key input
                user_input = QKeySequence(
                    int(event.modifiers()) + event.key()
                ).toString()
                for file_path in list(self.hotkey_dict.keys()):
                    hotkey = self.hotkey_dict[file_path]
                    if hotkey == user_input:
                        file_type = Locals().checkFileType(file_path)
                        if file_type == 'hotkey':
                            main_widget = PopupHotkeyMenu(self.mainWindow(), file_path=file_path)
                            main_widget.show()
                        elif file_type == 'gesture':
                            main_widget = PopupGestureMenu(self.mainWindow(), file_path=file_path)
                            main_widget.show()
                        elif file_type == 'script':
                            if os.path.exists(file_path):
                                environment = dict(locals(), **globals())
                                # environment.update(self.importModules())
                                with open(file_path) as script_descriptor:
                                    exec(script_descriptor.read(), environment, environment)
                        return QWidget.eventFilter(self, obj, event, *args, **kwargs)

        return QWidget.eventFilter(self, obj, event, *args, **kwargs)
import sys
import os

from qtpy.QtWidgets import QWidget
from qtpy.QtCore import QEvent
from qtpy.QtGui import QKeySequence

from Katana import UI4

from AbstractScriptEditorWidgets import PopupHotkeyMenu, PopupGestureMenu
from AbstractScriptEditorUtils import Utils as Locals

class eventFilter(QWidget):
    def __init__(self, parent=None, scripts_variable="CGWscripts"):
        super(eventFilter, self).__init__(parent)
        self.widget = UI4.App.MainWindow.GetMainWindow()
        self._scripts_variable = scripts_variable
        #self.widget.installEventFilter(self)

    """ PROPERTIES """
    def scriptsVariable(self):
        return self._scripts_variable

    def scriptsDirectories(self):
        return os.environ[self.scriptsVariable()].split(":")

    """ EVENTS """
    def closeEvent(self, *args, **kwargs):
        self.widget.removeEventFilter(self)
        return QWidget.closeEvent(self, *args, **kwargs)

    def eventFilter(self, obj, event, *args, **kwargs):
        if event.type() == QEvent.KeyPress:
            # get user hotkeys
            for directory in self.scriptsDirectories():
                hotkeys_file_path = "{directory}/{hotkeys_file_path}".format(
                    directory=directory, hotkeys_file_path=hotkeys_file_path)
                self.hotkey_dict = Locals().getFileDict(hotkeys_file_path)

                # get key input
                user_input = QKeySequence(
                    int(event.modifiers()) + event.key()
                ).toString()
                for file_path in list(self.hotkey_dict.keys()):
                    hotkey = self.hotkey_dict[file_path]
                    if hotkey == user_input:
                        file_type = Locals().checkFileType(file_path)
                        if file_type == 'hotkey':
                            main_widget = PopupHotkeyMenu(self.widget, file_path=file_path)
                            main_widget.show()
                        elif file_type == 'gesture':
                            main_widget = PopupGestureMenu(self.widget, file_path=file_path)
                            main_widget.show()
                        elif file_type == 'script':
                            if os.path.exists(file_path):
                                with open(file_path) as script_descriptor:
                                    exec(script_descriptor.read())
                        return QWidget.eventFilter(self, obj, event, *args, **kwargs)

        return QWidget.eventFilter(self, obj, event, *args, **kwargs)
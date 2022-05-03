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

    Attributes:
        is_active (bool): determines if the hotkeys are activated or not.
            This should be turned off when the user is setting a hotkey, so that
            it doesn't double register.
        is_setting_hotkey (bool): determines if the user is currently setting a hotkey.
            This is used to block the signal to run the script/design when the hotkey is set
        main_window (QMainWindow): Main window of the application (ie. widget.window())
        scripts_variable (str): Environment variable that holds the scripts directories"""
    def __init__(self, parent=None, main_window=None, scripts_variable="CGWscripts"):
        super(AbstractScriptEditorPopupEventFilter, self).__init__(parent)
        if not main_window:
            main_window = self.window()

        self._main_window = main_window
        self._scripts_variable = scripts_variable
        self._is_active = True
        self._is_setting_hotkey = False

    """ PROPERTIES """
    def scriptsVariable(self):
        return self._scripts_variable

    def scriptsDirectories(self):
        return os.environ[self.scriptsVariable()].split(";")

    def isSettingHotkey(self):
        return self._is_setting_hotkey

    def setIsSettingHotkey(self, enabled):
        self._is_setting_hotkey = enabled

    def isActive(self):
        return self._is_active

    def setIsActive(self, enabled):
        self._is_active = enabled

    """ WIDGETS """
    def mainWindow(self):
        return self._main_window

    """ EVENTS """
    def closeEvent(self, *args, **kwargs):
        self._main_window.removeEventFilter(self)
        return QWidget.closeEvent(self, *args, **kwargs)

    def eventFilter(self, obj, event, *args, **kwargs):
        if event.type() == QEvent.KeyPress:
            if self.isSettingHotkey():
                self.setIsSettingHotkey(False)
                return True
            # get user hotkeys
            if self.isActive():
                for directory in self.scriptsDirectories():
                    hotkeys_file_path = "{directory}/hotkeys.json".format(directory=directory)
                    self.hotkey_dict = getJSONData(hotkeys_file_path)
                    if self.hotkey_dict:
                        # get key input
                        user_input = QKeySequence(
                            int(event.modifiers()) + event.key()
                        ).toString()
                        if self.hotkey_dict:
                            for file_path in list(self.hotkey_dict.keys()):
                                hotkey = self.hotkey_dict[file_path]
                                # check for relative paths
                                if file_path.startswith(".."):
                                    file_path = file_path.replace("..", directory)
                                if hotkey == user_input:
                                    file_type = Locals().checkFileType(file_path)
                                    if file_type == "hotkey":
                                        main_widget = PopupHotkeyMenu(self.mainWindow(), file_path=file_path)
                                        main_widget.show()
                                    elif file_type == "gesture":
                                        main_widget = PopupGestureMenu(self.mainWindow(), file_path=file_path)
                                        main_widget.show()
                                    elif file_type == "script":
                                        if os.path.exists(file_path):
                                            environment = dict(locals(), **globals())
                                            # environment.update(self.importModules())
                                            with open(file_path) as script_descriptor:
                                                exec(script_descriptor.read(), environment, environment)
                                    return True

        return False


def installScriptEditorEventFilter(main_window, event_filter_widget):
    """ Installs the event filter on the applications Main Window

    Args:
        main_window (QMainWindow): Applications main window
        event_filter_widget (AbstractScriptEditorPopupEventFilter): widget class holding
            event filter to be installed"""
    main_window._script_editor_event_filter_widget = event_filter_widget(main_window)
    main_window.installEventFilter(main_window._script_editor_event_filter_widget)
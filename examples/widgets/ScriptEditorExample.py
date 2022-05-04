
import sys, os
from qtpy.QtWidgets import QApplication
from cgwidgets.widgets import ScriptEditorWidget, PopupHotkeyMenu, PopupGestureMenu, GestureDesignPopupWidget
from cgwidgets.utils import centerWidgetOnScreen, getDefaultSavePath, setAsAlwaysOnTop, setAsTransparent
app = QApplication(sys.argv)

os.environ["CGWscripts"] = ";".join([
    getDefaultSavePath() + "/.scripts",
    getDefaultSavePath() + "/.scripts2",
    #"/media/ssd01/dev/katana/KatanaResources_old/ScriptsTest"
])
# print(os.environ["CGWscripts"])
# main_widget = ScriptEditorWidget()
# setAsAlwaysOnTop(main_widget)
# main_widget.show()
# centerWidgetOnScreen(main_widget)

# # popup hotkey example
# hotkey_file_path = "/home/brian/.cgwidgets/.scripts/3641172470576247296.a.json"
# popup_widget = PopupHotkeyMenu(file_path=hotkey_file_path)
# popup_widget.show()

# popup gesture example
gesture_file_path = "/home/brian/.cgwidgets/.scripts/7561119950682766336.gestureTest/2258396054567534080.GestureDesign1.json"
gesture_widget = PopupGestureMenu(file_path=gesture_file_path, size=500)
gesture_widget.show()


sys.exit(app.exec_())
# main()

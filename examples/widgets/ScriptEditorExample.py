
import sys, os
from qtpy.QtWidgets import QApplication
from cgwidgets.widgets import ScriptEditorWidget, PopupHotkeyMenu
from cgwidgets.utils import centerWidgetOnScreen, getDefaultSavePath, setAsAlwaysOnTop
app = QApplication(sys.argv)

os.environ["CGWscripts"] = ":".join([
    getDefaultSavePath() + "/.scripts",
    getDefaultSavePath() + "/.scripts2",
    #"/media/ssd01/dev/katana/KatanaResources_old/ScriptsTest"
])
print(os.environ["CGWscripts"])
main_widget = ScriptEditorWidget()
setAsAlwaysOnTop(main_widget)
main_widget.show()
centerWidgetOnScreen(main_widget)

# popup hotkey example
hotkey_file_path = "/home/brian/.cgwidgets/.scripts/3641172470576247296.a.json"
popup_widget = PopupHotkeyMenu(file_path=hotkey_file_path)

popup_widget.show()

sys.exit(app.exec_())
main()

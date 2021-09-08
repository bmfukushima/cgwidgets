
import sys, os
from qtpy.QtWidgets import QApplication
from cgwidgets.widgets import AbstractScriptEditorWidget
from cgwidgets.utils import centerWidgetOnScreen, getDefaultSavePath, setAsAlwaysOnTop
app = QApplication(sys.argv)

os.environ["CGWscripts"] = ":".join([
    getDefaultSavePath() + "/.scripts",
    getDefaultSavePath() + "/.scripts2",
    "/media/ssd01/dev/katana/KatanaResources_old/ScriptsTest"
])

main_widget = AbstractScriptEditorWidget()
setAsAlwaysOnTop(main_widget)
main_widget.show()
centerWidgetOnScreen(main_widget)

sys.exit(app.exec_())
main()

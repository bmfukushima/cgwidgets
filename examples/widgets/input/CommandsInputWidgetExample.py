import sys
from qtpy.QtWidgets import QApplication
from cgwidgets.utils import centerWidgetOnScreen, setAsAlwaysOnTop

from cgwidgets.widgets import CommandsInputWidget

app = QApplication(sys.argv)

widget = CommandsInputWidget()

# add command
def test():
    print("Test command")

widget.addCommand("test", test)

setAsAlwaysOnTop(widget)
widget.show()
centerWidgetOnScreen(widget)

sys.exit(app.exec_())
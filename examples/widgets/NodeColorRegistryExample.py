import sys
import os

from qtpy.QtWidgets import QApplication

from cgwidgets.widgets import NodeColorRegistryWidget
from cgwidgets.utils import centerWidgetOnScreen, setAsAlwaysOnTop

app = QApplication(sys.argv)
# setup environment configs
os.environ["CGWNODECOLORCONFIGS"] = "/home/brian/.cgwidgets/colorConfigs_01/:/home/brian/.cgwidgets/colorConfigs_02"

# create main widget
node_color_registry = NodeColorRegistryWidget()

# setup default color profile
file = "/home/brian/.cgwidgets/colorConfigs_01/test.json"
node_color_registry.setColorFile(file)

# add command
def testCommand():
    print('test command')

node_color_registry.addCommand("test", testCommand)


setAsAlwaysOnTop(node_color_registry)
node_color_registry.show()
centerWidgetOnScreen(node_color_registry, width=512)

sys.exit(app.exec_())
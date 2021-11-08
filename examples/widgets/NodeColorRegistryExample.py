import sys
import os

from qtpy.QtWidgets import QApplication

from cgwidgets.widgets import NodeColorRegistryWidget
from cgwidgets.utils import centerWidgetOnScreen, setAsAlwaysOnTop

app = QApplication(sys.argv)
os.environ["CGWNODECOLORCONFIGS"] = "/home/brian/.cgwidgets/colorConfigs_01/;/home/brian/.cgwidgets/colorConfigs_02"
#os.environ["CGWNODECOLORCONFIGS"] = "/home/brian/.cgwidgets/colorConfigs_01/;/home/brian/.cgwidgets/colorConfigs_02"

node_color_registry = NodeColorRegistryWidget()
setAsAlwaysOnTop(node_color_registry)
node_color_registry.show()
centerWidgetOnScreen(node_color_registry)

sys.exit(app.exec_())
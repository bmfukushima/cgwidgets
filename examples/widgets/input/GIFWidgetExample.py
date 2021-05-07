import sys
from qtpy.QtWidgets import QApplication

from cgwidgets.widgets import GIFWidget
from cgwidgets.utils import centerWidgetOnCursor
from cgwidgets.settings.hover_display import installHoverDisplaySS
from cgwidgets.settings.icons import icons

app = QApplication(sys.argv)

gif_file = icons["ACCEPT_GIF"]
widget = GIFWidget(gif_file)
installHoverDisplaySS(widget)

widget.show()
centerWidgetOnCursor(widget)
widget.setResolution(50, maintain_aspect_ratio=True)

sys.exit(app.exec_())
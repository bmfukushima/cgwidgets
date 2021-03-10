import sys, string

from qtpy.QtWidgets import QApplication, QLabel, QWidget, QHBoxLayout
from qtpy.QtGui import QCursor

from cgwidgets.utils import centerWidgetOnCursor, attrs
from cgwidgets.settings.hover_display import installHoverDisplaySS, HoverStyleSheet
from cgwidgets.settings.colors import iColor


app = QApplication(sys.argv)


# Create Main Widget
main_widget = QWidget()
main_layout = QHBoxLayout(main_widget)

# Create Hover Widgets
for char in string.ascii_letters:
    widget = QLabel(char)
    installHoverDisplaySS(
        widget,
        name="UNIQUE NAME"
        position=attrs.NORTH, # SOUTH | EAST | WEST | VERTICAL | HORIZONTAL | None
        hover_style_type=HoverStyleSheet.BORDER, # BACKGROUND | RADIAL
        color=iColor["rgba_selected_hover"], # (255, 255, 255, 255)
        focus=True,
        hover=True,
        hover_focus=True,
    )
    main_layout.addWidget(widget)

main_widget.show()
centerWidgetOnCursor(main_widget)
sys.exit(app.exec_())

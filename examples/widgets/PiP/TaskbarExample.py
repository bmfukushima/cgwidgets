import sys
from qtpy.QtWidgets import QApplication, QLabel, QHBoxLayout, QWidget
from qtpy.QtCore import Qt

from cgwidgets.utils import centerWidgetOnCursor, setAsAlwaysOnTop, centerWidgetOnScreen
from cgwidgets.settings import attrs

from cgwidgets.widgets import AbstractPopupBarWidget


app = QApplication(sys.argv)

# create popup bar
popup_bar_widget = AbstractPopupBarWidget()
popup_bar_widget.setDirection(attrs.EAST)
for x in range(3):
    label = QLabel(str(x))
    label.setFixedWidth(50)
    popup_bar_widget.createNewWidget(label, str(x))

# create main widget
main_widget = QWidget()
main_layout = QHBoxLayout(main_widget)
other_widget = QLabel("Something Else")
main_layout.addWidget(popup_bar_widget)
main_layout.addWidget(other_widget)

# set popup bar widget
popup_bar_widget.setOverlayWidget(other_widget)
popup_bar_widget.setIsDisplayNamesShown(False)

# show widget
setAsAlwaysOnTop(main_widget)
main_widget.show()
centerWidgetOnScreen(main_widget)
popup_bar_widget.setFixedWidth(50)

sys.exit(app.exec_())

import sys


# os.environ['QT_API'] = 'pyside2'
from qtpy import API_NAME
print(API_NAME)
#import PySide2
#print(PySide2.__version__)
from qtpy.QtWidgets import (QApplication, QWidget, QLabel, QHBoxLayout, QVBoxLayout)
from cgwidgets.widgets import PopupBarDisplayWidget, AbstractPopupBarWidget
from cgwidgets.utils import centerWidgetOnCursor, setAsAlwaysOnTop, getDefaultSavePath, centerWidgetOnScreen
from cgwidgets.settings import attrs

app = QApplication(sys.argv)

# create popup bar
popup_bar_widget = PopupBarDisplayWidget()
for x in range(3):
    label = QLabel(str(x))
    popup_bar_widget.addWidget(label, name=str(x))

# create main widget
main_widget = QWidget()
main_layout = QHBoxLayout(main_widget)
main_layout.setContentsMargins(0,0,0,0)
other_widget = QLabel("Something Else")
main_layout.addWidget(popup_bar_widget)
main_layout.addWidget(other_widget)

test = QWidget()
test_label = QLabel("test")
test_label.setFixedHeight(120)
test_layout = QVBoxLayout(test)
test_layout.addWidget(test_label)
test_layout.addWidget(main_widget)

# set popup bar widget

#popup_bar_widget.popupBarWidget().setOverlayWidget(other_widget)

popup_bar_widget.setFixedWidth(150)
popup_bar_widget.loadPopupDisplayFromFile(
    getDefaultSavePath() + '/.PiPWidgets_02.json',
    "standalone_taskbar"
)
popup_bar_widget.setDisplayMode(PopupBarDisplayWidget.PIP)
# popup_bar_widget.setDirection(attrs.SOUTH)

# show widget
setAsAlwaysOnTop(test)
test.show()
test.resize(512, 512)
centerWidgetOnScreen(test)

sys.exit(app.exec_())

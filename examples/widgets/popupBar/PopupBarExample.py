
import sys, os


# os.environ['QT_API'] = 'pyside2'
# from qtpy import API_NAME
# print(API_NAME)
#import PySide2
#print(PySide2.__version__)
from qtpy.QtWidgets import (QApplication, QWidget, QLabel, QHBoxLayout, QVBoxLayout)
from cgwidgets.widgets import PopupBarDisplayWidget, AbstractPopupBarWidget
from cgwidgets.utils import centerWidgetOnCursor, setAsAlwaysOnTop, getDefaultSavePath, centerWidgetOnScreen
from cgwidgets.settings import attrs

app = QApplication(sys.argv)

# create popup bar
popup_bar_widget = PopupBarDisplayWidget()
# for x in range(3):
#     label = QLabel(str(x))
#     popup_bar_widget.addWidget(label, name=str(x))

# load widgets
popup_bar_widget.loadPopupDisplayFromFile(
    getDefaultSavePath() + '/.PiPWidgets_02.json',
    "taskbar"
)
for x in popup_bar_widget.allWidgets():
    print(x.name())

# set popup bar widget
popup_bar_widget.setPiPScale(0.55)
# popup_bar_widget.setSizes([50, 50])
#popup_bar_widget.setTaskbarSize(150)
# popup_bar_widget.setFixedWidth(150)
popup_bar_widget.setDirection(attrs.WEST)
# popup_bar_widget.setDisplayMode(PopupBarDisplayWidget.STANDALONETASKBAR)

# create main widget
main_widget = QWidget()
main_layout = QHBoxLayout(main_widget)
main_layout.setContentsMargins(0, 0, 0, 0)
other_widget = QLabel("Something Else")
main_layout.addWidget(popup_bar_widget)
main_layout.addWidget(other_widget)


# show widget
setAsAlwaysOnTop(main_widget)
main_widget.show()
main_widget.resize(512, 512)
centerWidgetOnScreen(main_widget)

sys.exit(app.exec_())


import sys
import os

# os.environ['QT_API'] = 'pyside2'
from qtpy import API_NAME
print(API_NAME)
#import PySide2
#print(PySide2.__version__)
from qtpy.QtWidgets import (QApplication, QWidget)
from cgwidgets.widgets import PiPOrganizerWidget, PiPDisplayWidget
from cgwidgets.utils import centerWidgetOnCursor, setAsAlwaysOnTop, getDefaultSavePath
from cgwidgets.settings import attrs
app = QApplication(sys.argv)

# PiP Widget
save_data = {
    "Foo": {
        "file_path": getDefaultSavePath() + '/.PiPWidgets.json',
        "locked": True},
    "Bar": {
        "file_path": getDefaultSavePath() + '/.PiPWidgets_02.json',
        "locked": False}
}

widget_types = {
    "QLabel": """
from qtpy.QtWidgets import QLabel
widget = QLabel(\"TEST\") """,
    "QPushButton":"""
from qtpy.QtWidgets import QPushButton
widget = QPushButton(\"TESTBUTTON\") """,
    "List":"""
from qtpy.QtWidgets import QListWidget
from qtpy.QtWidgets import QAbstractItemView
widget = QListWidget()
widget.setDragDropMode(QAbstractItemView.DragDrop)
widget.setAcceptDrop(True)
widget.addItems(['a', 'b', 'c', 'd'])
# widget.setFixedWidth(100)
""",
    "Recursion":"""

from cgwidgets.widgets import PiPDisplayWidget
widget = PiPDisplayWidget()
widget.loadPiPWidgetFromFile(
    getDefaultSavePath() + '/.PiPWidgets_02.json',
    "test02"
)
""",
    "Popup":"""
import string
from qtpy.QtWidgets import QWidget, QVBoxLayout, QComboBox
from qtpy.QtGui import QCursor

pos = QCursor().pos()
widget = QWidget()
l = QVBoxLayout(widget)
b = QComboBox()
b.addItems([char for char in string.ascii_letters])
l.addWidget(b)
"""
}
pip_organizer_widget = PiPOrganizerWidget(save_data=save_data, widget_types=widget_types)

pip_organizer_widget.setPiPScale((0.25, 0.25))
pip_organizer_widget.setEnlargedScale(0.75)
pip_organizer_widget.setDirection(attrs.WEST)
#pip_widget.setIsDisplayNamesShown(False)


# show organizer
setAsAlwaysOnTop(pip_organizer_widget)
pip_organizer_widget.show()
centerWidgetOnCursor(pip_organizer_widget)
pip_organizer_widget.resize(512, 512)

# setup display widget
pip_display_widget = PiPDisplayWidget()
pip_display_widget.loadPiPWidgetFromFile(
    getDefaultSavePath() + '/.PiPWidgets_02.json',
    "double"
)

pip_organizer_widget.setPiPScale(.55)
pip_organizer_widget.setEnlargedScale(0.35)
pip_organizer_widget.setDirection(attrs.WEST)

centerWidgetOnCursor(pip_display_widget)
#pip_display_widget.resize(1024, 1024)
setAsAlwaysOnTop(pip_display_widget)
pip_display_widget.show()



sys.exit(app.exec_())
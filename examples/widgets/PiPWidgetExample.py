import sys
import os

os.environ['QT_API'] = 'pyside2'
from qtpy import API_NAME

from qtpy.QtWidgets import (QWidget, QHBoxLayout, QApplication)
from cgwidgets.utils import centerWidgetOnCursor, getDefaultSavePath
from cgwidgets.settings import attrs
from cgwidgets.widgets import PiPWidget

app = QApplication(sys.argv)

# PiP Widget
""" more widgets can be added be extending the dict"""
widget_types = {
    "QLabel": """
from qtpy.QtWidgets import QLabel
widget = QLabel(\"TEST\") """,
    "QPushButton": """
from qtpy.QtWidgets import QPushButton
widget = QPushButton(\"TESTBUTTON\") """}

# create save directories
""" more directories can be added by extending the dict"""
save_file_path = getDefaultSavePath() + '/.PiPWidgets.json'
save_data = {"File Name": {"file_path": save_file_path, "locked": False}}

# create pip widget
pip_widget = PiPWidget(save_data=save_data, widget_types=widget_types)

# set to headerless mode
print(save_file_path)
#pip_widget.setDisplayWidget(file_name, widget_name)
# pip_widget.setDisplayWidget("File Name", "test02")
# pip_widget.setCreationMode(PiPWidget.DISPLAY)

# setup default attrs
pip_widget.setPiPScale((0.25, 0.25))
pip_widget.setEnlargedScale(0.75)
pip_widget.setDirection(attrs.WEST)
pip_widget.setIsDisplayNamesShown(False)

# Main Widget
main_widget = QWidget()

main_layout = QHBoxLayout(main_widget)
main_layout.setContentsMargins(0, 0, 0, 0)
main_layout.addWidget(pip_widget)
# main_layout.addWidget(drag_drop_widget)

main_widget.show()
centerWidgetOnCursor(main_widget)
main_widget.resize(512, 512)

sys.exit(app.exec_())

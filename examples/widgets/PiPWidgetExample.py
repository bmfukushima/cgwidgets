import sys
import os

os.environ['QT_API'] = 'pyside2'
from qtpy import API_NAME

from qtpy.QtWidgets import (QWidget, QHBoxLayout, QApplication, QListWidget, QAbstractItemView, QPushButton)
from cgwidgets.utils import centerWidgetOnCursor
from cgwidgets.utils import attrs
from cgwidgets.widgets import PiPWidget

app = QApplication(sys.argv)

# PiP Widget
widget_types = {
    "QLabel": """
from qtpy.QtWidgets import QLabel
widget = QLabel(\"TEST\") """,
    "QPushButton": """
from qtpy.QtWidgets import QPushButton
widget = QPushButton(\"TESTBUTTON\") """
}
pip_widget = PiPWidget(widget_types=widget_types)


pip_widget.setPiPScale((0.25, 0.25))
pip_widget.setEnlargedScale(0.75)
pip_widget.setDirection(attrs.WEST)
pip_widget.showWidgetDisplayNames(False)

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

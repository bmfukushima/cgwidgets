from qtpy.QtCore import Qt

from cgwidgets.widgets import TansuModelViewWidget, TansuBaseWidget
from cgwidgets.utils import attrs

import sys
from qtpy.QtWidgets import QApplication, QLabel, QAbstractItemView
from qtpy.QtGui import QCursor

app = QApplication(sys.argv)

tansu_widget = TansuModelViewWidget()
tansu_widget.setHeaderData(['example'])
tab_1 = QLabel('hello')
tab_2 = QLabel('world')
tab_3 = TansuBaseWidget()
tab_3.setObjectName("main")
tab_3.addWidget(QLabel('a'))
tab_3.addWidget(QLabel('b'))
tab_3.addWidget(QLabel('c'))

# set attrs
tansu_widget.setHeaderPosition(attrs.NORTH)
tansu_widget.setMultiSelect(True)
tansu_widget.setMultiSelectDirection(Qt.Vertical)

# insert tabs
tansu_widget.insertTansuWidget(0, column_data={'example' : '<title> hello'}, widget=tab_1)
tansu_widget.insertTansuWidget(0, column_data={'example' : '<title> world'}, widget=tab_2)
tansu_widget.insertTansuWidget(0, column_data={'example' : '<title> tansu'}, widget=tab_3)

# enable drag/drop
tansu_widget.setHeaderDragDropMode(QAbstractItemView.DragDropMode.InternalMove)

tansu_widget.resize(500, 500)
tansu_widget.delegateWidget().handle_length = 100



tansu_widget.show()

tansu_widget.move(QCursor.pos())
sys.exit(app.exec_())
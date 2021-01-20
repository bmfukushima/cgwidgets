import sys
from qtpy.QtWidgets import QApplication, QLabel
from qtpy.QtGui import QCursor
from qtpy.QtCore import Qt
from cgwidgets.widgets import TansuBaseWidget

app = QApplication(sys.argv)

# create tansu
main_tansu_widget = TansuBaseWidget()

# OPTIONAL | set handle length (if not set, by default this will be full length)
main_tansu_widget.handle_length = 100

# add widgets
main_tansu_widget.addWidget(QLabel('a'))
main_tansu_widget.addWidget(QLabel('b'))
main_tansu_widget.addWidget(QLabel('c'))

# create second tansu widget
tansu_widget_2 = TansuBaseWidget(orientation=Qt.Horizontal)
tansu_widget_2.setObjectName("embed")

# add widgets
for x in range(3):
    l = QLabel(str(x))
    tansu_widget_2.addWidget(l)

# add tansu to tansu
main_tansu_widget.addWidget(tansu_widget_2)
# show widget
f = QLabel("what")
f.show()
main_tansu_widget.show()
main_tansu_widget.move(QCursor.pos())
sys.exit(app.exec_())


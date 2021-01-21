import sys
from qtpy.QtWidgets import QApplication, QLabel
from qtpy.QtGui import QCursor
from qtpy.QtCore import Qt
from cgwidgets.delegates import TansuDelegate

app = QApplication(sys.argv)

# create tansu
main_tansu_widget = TansuDelegate()

# OPTIONAL | set handle length (if not set, by default this will be full length)
main_tansu_widget.handle_length = 100

# add widgets
for char in "SINEP":
    widget = QLabel(char)
    main_tansu_widget.addWidget(widget)
    widget.setStyleSheet("color: rgba(255,0,0,255)")

# create second tansu widget
tansu_widget_2 = TansuDelegate(orientation=Qt.Horizontal)
tansu_widget_2.setObjectName("embed")

# add widgets
for x in range(3):
    l = QLabel(str(x))
    tansu_widget_2.addWidget(l)
    l.setStyleSheet("color: rgba(255,0,0,255)")

# add tansu to tansu
main_tansu_widget.addWidget(tansu_widget_2)

# show widget

main_tansu_widget.show()
main_tansu_widget.move(QCursor.pos())
sys.exit(app.exec_())

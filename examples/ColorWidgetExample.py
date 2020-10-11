import sys

from qtpy.QtWidgets import *

from cgwidgets.widgets import ColorWidget

if __name__ == '__main__':
    app = QApplication(sys.argv)
    cw = ColorWidget()
    cw.show()
    sys.exit(app.exec_())

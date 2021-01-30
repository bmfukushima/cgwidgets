from qtpy.QtWidgets import (
    QLineEdit, QLabel, QPlainTextEdit, QStackedWidget, QApplication
)
from qtpy.QtCore import Qt, QEvent

from cgwidgets.utils import (
    updateStyleSheet, clearLayout, installLadderDelegate, getWidgetAncestor,
    getFontSize, checkIfValueInRange, checkNegative, setAsTransparent, updateStyleSheet
)
from cgwidgets.settings.colors import iColor
from cgwidgets.settings.keylist import NUMERICAL_INPUT_KEYS, MATH_KEYS

# this is causing circular import =\
from cgwidgets.views.TansuView import TansuView
from cgwidgets.widgets import iAbstractInputWidget






if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication, QWidget, QVBoxLayout
    from qtpy.QtGui import QCursor

    import sys, inspect

    app = QApplication(sys.argv)

    def userEvent(widget):
        print("user input...", widget)

    widget = AbstractMultiButtonInputWidget(orientation=Qt.Horizontal)
    for x in range(3):
        widget.addButton(str(x), userEvent)

    widget.move(QCursor.pos())
    widget.show()
    widget.resize(256, 256)
    widget.resize(500, 500)
    widget.show()
    # w.move(QCursor.pos())
    sys.exit(app.exec_())
    #
    # def print_classes():
    #     for name, obj in inspect.getmembers(sys.modules[__name__]):
    #         if inspect.isclass(obj):
    #             print(obj)
    #
    # print(__name__)
    # print_classes()
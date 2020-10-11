"""
TODO:
    Hue adjust -->
        Shift + LMB?
    Display Value Labels
        *   Make this adjustable with the INPUT WIDGETS
                - Connect to gradients
                    will need a flag to stop recursion...
    CLOCK ( Display Label )
        * Show current values
        * background
                - semi transparent?
                - middle gray?
"""

import sys

from qtpy.QtWidgets import (
    QApplication, QStackedWidget, QLabel,
)
from qtpy.QtCore import (Qt, QPoint)
from qtpy.QtGui import (
    QColor, QCursor
)

from cgwidgets.utils import getWidgetAncestor, attrs
from cgwidgets.widgets.InputWidgets.ColorInputWidget import (
    ColorInputWidget, ColorGradientDelegate, ColorClockDelegate
)


if __name__ == '__main__':
    from qtpy.QtWidgets import QWidget, QVBoxLayout

    app = QApplication(sys.argv)
    mw = QWidget()
    l = QVBoxLayout(mw)
    test_label = QLabel('lkjasdf')

    def userInputEvent(widget, color):
        test_label.setText(repr(color.getRgb()))

    color_widget = ColorInputWidget()
    color_widget.setUserInput(userInputEvent)
    color_widget.setDisplayLocation(position=attrs.NORTH)

    l.addWidget(test_label)
    l.addWidget(color_widget)

    mw.show()
    mw.move(QCursor.pos())
    sys.exit(app.exec_())









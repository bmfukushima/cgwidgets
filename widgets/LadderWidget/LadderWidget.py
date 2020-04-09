import sys
import math

from qtpy.QtGui import *
from qtpy.QtWidgets import *
from qtpy.QtCore import *

from cgwidgets.utils import installLadderDelegate


class LadderWidget(QWidget):
    '''
    Widget with a LadderDelegate for editing

    Kwargs:
        value_list (list): A list of float values.  This list will be displayed
            to the user as the available options to click/drag on in order
            to manipulate the value on the LadderWidget

        widget (QLineEdit or QLabel): The actual widget type for the user
            manipulate.  This can also be any widget,  however you will
            need to implement a "setValue()" method on that widget and
            have it set the display value.

        user_input (QEvent): Event to be triggered in order to have the
            delegate popup.
    '''
    def __init__(
        self,
        parent=None,
        value_list=[0.0001, 0.001, 0.01, 0.1],
        widget=None,
        user_input=QEvent.MouseButtonPress
    ):
        super(LadderWidget, self).__init__(parent)
        # setup widget
        layout = QVBoxLayout(self)

        # set up position
        pos = QCursor().pos()
        self.setGeometry(pos.x(), pos.y(), 200, 100)

        # create default widget
        if not widget:
            widget = QLineEdit()

        # install ladder delegate
        self.ladder = installLadderDelegate(
            widget,
            user_input=user_input,
            value_list=value_list
        )

        layout.addWidget(widget)

    def setValue(self, value):
        self.setText(str(value))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    label = QLabel('-5')
    ladder_widget = LadderWidget(widget=label)
    ladder_widget.ladder.setDiscreteDrag(
        True,
        alignment=Qt.AlignLeft,
        depth=10,
        fg_color=(128, 128, 32, 255),
        display_widget=label.window()
    )

    ladder_widget.show()
    sys.exit(app.exec_())




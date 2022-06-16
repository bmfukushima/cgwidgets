
import logging
from cgwidgets.widgets import FloatInputWidget, IntInputWidget
from qtpy.QtWidgets import QLabel, QApplication


from cgwidgets.widgets.LadderWidget import LadderWidget

import sys
from qtpy.QtWidgets import QApplication
from qtpy.QtCore import QEvent
from qtpy.QtGui import QCursor
app = QApplication(sys.argv)

logging.basicConfig(level=logging.DEBUG)

def finishedEditing(widget, value):
    print('------ FINISHED EDITING --------')
    print(widget, value)

def liveEditing(widget, value):
    print('------ LIVE EDITING --------')
    print(widget, value)

# create main widget
main_widget = FloatInputWidget()
main_widget.setUseLadder(
    True,
    user_input=QEvent.MouseButtonRelease,
    value_list=[0.01, 0.05, 0.1],
    range_max=7)
main_widget.setValue(5.0)
# main_widget.setLiveInputEvent(liveEditing)
main_widget.setUserFinishedEditingEvent(finishedEditing)
# main_widget.setRange(True, 0.0, 1.0)
# main_widget.setAllowNegative(True)
# self._colorr_widget = FloatInputWidget(allow_negative=False, allow_zero=False)
# self._colorr_widget.setUseLadder(True, value_list=[0.001, 0.01, 0.1], range_min=0, range_max=1, range_enabled=True)
# show widget
main_widget.show()
main_widget.move(QCursor.pos())
sys.exit(app.exec_())
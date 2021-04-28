"""
Simple example of how to install a function to run after a user has finished resizing something.

This event is installed with "installResizeEventFinishedEvent" from the cgwidgets.utils.install module

This works off of a basic timer, where a timer is set as an attribute on the widget provided,
and everytime a resizeEvent occurs, that timer is reset back to zero.  When the timer finishes
after the user has stopped resizing the widget, then the function that is provided will be run.

This should ALWAYS be installed on the resizeEvent of the widget provided, as it is a protected
function and cannot be overridden with a monkey patch.
"""

import sys

from qtpy.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout

from cgwidgets.utils import installResizeEventFinishedEvent, centerWidgetOnCursor

app = QApplication(sys.argv)

# create resize event
def _resizeFinishedEvent(*args, **kwargs):
    print('resizing???')

class ResizeFinishedEventWidget(QLabel):
    def __init__(self, parent=None, text="None"):
        super(ResizeFinishedEventWidget, self).__init__(parent)
        self.setText(text)

    def resizeEvent(self, event):
        installResizeEventFinishedEvent(self, 200, _resizeFinishedEvent, 'timer_name', 'a', b="b")
        return QLabel.resizeEvent(self, event)

# create basic widget
main_widget = QWidget()
main_widget.setStyleSheet("background-color:rgba(255,0,0,255);")
main_layout = QVBoxLayout(main_widget)
foo = ResizeFinishedEventWidget(text="foo")
bar = ResizeFinishedEventWidget(text="bar")
foo.setStyleSheet("background-color:rgba(255,255,0,255);")

main_layout.addWidget(foo)
main_layout.addWidget(bar)

main_widget.show()
centerWidgetOnCursor(main_widget)

# install resize finished event


sys.exit(app.exec_())
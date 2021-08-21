from cgwidgets.widgets import AbstractSplitterWidget, SplitterWidget

import sys
from qtpy.QtWidgets import QApplication, QLabel
from qtpy.QtCore import Qt
from cgwidgets.utils import setAsAlwaysOnTop, centerWidgetOnCursor
app = QApplication(sys.argv)


# setup splitter
splitter = SplitterWidget(Qt.Horizontal)
for x in range(3):
    label = QLabel("test")
    splitter.addWidget(label)

# add delayed events
def delayEvent1():
    print('1')

def delayEvent2():
    print('2')

def delayEvent3():
    print('3')

splitter.addDelayedSplitterMovedEvent("one", delayEvent1, 100)
splitter.addDelayedSplitterMovedEvent("two", delayEvent2, 200)
splitter.addDelayedSplitterMovedEvent("three", delayEvent3, 300)

splitter.removeDelayedSplitterMovedEvent("three")

# show splitter
setAsAlwaysOnTop(splitter)
splitter.show()
centerWidgetOnCursor(splitter)
sys.exit(app.exec_())
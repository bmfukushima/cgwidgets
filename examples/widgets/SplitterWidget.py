from cgwidgets.widgets import AbstractSplitterWidget, SplitterWidget

import sys
from qtpy.QtWidgets import QApplication, QLabel
from qtpy.QtCore import Qt
from cgwidgets.utils import setAsAlwaysOnTop, centerWidgetOnCursor
app = QApplication(sys.argv)


# setup splitter
splitter = SplitterWidget(orientation=Qt.Horizontal)
for x in range(3):
    label = QLabel("test")
    splitter.addWidget(label)

# add delayed events
def delayEvent1(pos, index):
    print('========== 1 ========== ')
    print(pos, index)

def delayEvent2(pos, index):
    print('========== 2 ========== ')
    print(pos, index)


def delayEvent3(pos, index):
    print('========== 3 ========== ')
    print(pos, index)

splitter.addDelayedSplitterMovedEvent("one", delayEvent1)
splitter.addDelayedSplitterMovedEvent("two", delayEvent2, 200)
splitter.addDelayedSplitterMovedEvent("three", delayEvent3, 300)

splitter.removeDelayedSplitterMovedEvent("three")

print(splitter.delayedSplitterMovedEventNames())
splitter.changeDelayedEventName("one", "five")
print(splitter.delayedSplitterMovedEventNames())

splitter.setEventDelayAmount("five", 300)


# show splitter
setAsAlwaysOnTop(splitter)
splitter.show()
centerWidgetOnCursor(splitter)
sys.exit(app.exec_())
from qtpy.QtCore import QEvent
from qtpy.QtWidgets import QWidget, QApplication, QLabel
from qtpy.QtGui import QRegion
import sys


class InvisibleWidgetEvent(QWidget):
    """
Causes a widget to hide/show during pen down/up.

Sets up an invisible drag event.  When the user clicks, and drags,
the widget will dissappear.  On release, the widget will reappear at
the original location.

Args:
    **  hide_widget (QWidget): optional argument, if this is defined
            this will be the widget that is hidden.
    **  parent(QWidget): if no hide_widget argument is provided,
            this will become the widget to be hidden.
    """
    def __init__(self, parent=None, hide_widget=None):
        super(InvisibleWidgetEvent, self).__init__(parent)
        if hide_widget is None:
            self._hide_widget = parent
        else:
            self._hide_widget = hide_widget

    def eventFilter(self, obj, event, *args, **kwargs):
        if event.type() == QEvent.MouseButtonPress:
            region = QRegion(self._hide_widget.frameGeometry())
            self._hide_widget.setMask(region)

        elif event.type() == QEvent.MouseButtonRelease:
            width = self._hide_widget.width()
            height = self._hide_widget.height()
            region = QRegion(0, 0, width, height)
            self._hide_widget.setMask(region)

        return QWidget.eventFilter(self, obj, event, *args, **kwargs)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = QLabel('Test')
    ef = InvisibleWidgetEvent()
    w.installEventFilter(ef)
    w.show()

    sys.exit(app.exec_())

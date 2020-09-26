from qtpy.QtCore import QEvent, Qt, QPoint
from qtpy.QtWidgets import QWidget, QApplication, QLabel, QDesktopWidget
from qtpy.QtGui import QCursor
import sys


class InvisibleCursorEvent(QWidget):
    """
Causes the cursor to hide/show during pen down/up.

Sets up an invisible drag event.  When the user clicks, and drags,
the cursor will dissappear.  On release, the cursor will reappear at
the original location.  This will also allow the cursor to travel an
infinite distance without disrupting the user.
    """
    def __init__(self, parent=None):
        super(InvisibleCursorEvent, self).__init__(parent)
        self._screen_resolution = self.screen_resolutions()

    def eventFilter(self, obj, event, *args, **kwargs):
        """
        # catch init failures
        try:
            self._init_pos
        except AttributeError:
            return QWidget.eventFilter(self, obj, event, *args, **kwargs)
        """

        # do work
        if event.type() == QEvent.MouseButtonRelease:
            self._init_pos = obj.mapToGlobal(event.pos())
            obj.window().setCursor(Qt.BlankCursor)
        elif event.type() == QEvent.MouseMove:
            pos = obj.mapToGlobal(event.pos())

            if pos.x() > self._screen_resolution:
                y_pos = pos.y()
                QCursor().setPos(QPoint(1, y_pos))
            elif pos.x() < 1:
                y_pos = pos.y()
                QCursor().setPos(QPoint(self._screen_resolution - 1, y_pos))
        elif event.type() == QEvent.MouseButtonRelease:
            obj.window().unsetCursor()
            QCursor().setPos(self._init_pos)

        return QWidget.eventFilter(self, obj, event, *args, **kwargs)

    def screen_resolutions(self):
        width = 0
        for displayNr in range(QDesktopWidget().screenCount()):
            sizeObject = QDesktopWidget().screenGeometry(displayNr)
            width += sizeObject.width()
        return width - 5


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = QLabel('Test')
    ef = InvisibleCursorEvent()
    w.installEventFilter(ef)
    w.show()

    sys.exit(app.exec_())

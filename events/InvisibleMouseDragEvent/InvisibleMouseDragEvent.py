from PyQt5.QtCore import QEvent, Qt, QPoint
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QDesktopWidget
from PyQt5.QtGui import QCursor
import sys


class InvisibleMouseDragEvent(QWidget):
    def __init__(self, parent=None):
        super(InvisibleMouseDragEvent, self).__init__(parent)
        self._screen_resolution = self.screen_resolutions()

    def eventFilter(self, obj, event, *args, **kwargs):
        if event.type() == QEvent.MouseButtonPress:
            self._init_pos = obj.mapToGlobal(event.pos())
            obj.setCursor(Qt.BlankCursor)

        elif event.type() == QEvent.MouseMove:
            pos = obj.mapToGlobal(event.pos())

            if pos.x() > self._screen_resolution:
                y_pos = pos.y()
                QCursor().setPos(QPoint(1, y_pos))

        elif event.type() == QEvent.MouseButtonRelease:
            obj.unsetCursor()
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
    ef = InvisibleMouseDragEvent()
    w.installEventFilter(ef)
    w.show()

    sys.exit(app.exec_())

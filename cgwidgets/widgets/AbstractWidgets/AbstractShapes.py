# https://doc.qt.io/qt-5/qframe.html#Shape-enum
from qtpy.QtWidgets import QFrame


class AbstractLine(QFrame):
    def __init__(self, parent=None):
        super(AbstractLine, self).__init__(parent)
        self.setStyleSheet("""
            margin: 30px;
        """)


class AbstractHLine(AbstractLine):
    def __init__(self, parent=None):
        super(AbstractHLine, self).__init__(parent)
        self.setFrameShape(QFrame.HLine)


class AbstractVLine(AbstractLine):
    def __init__(self, parent=None):
        super(AbstractVLine, self).__init__(parent)
        self.setFrameShape(QFrame.VLine)


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication, QLabel
    from PyQt5.QtGui import QCursor
    app = QApplication(sys.argv)

    sys.exit(app.exec_())

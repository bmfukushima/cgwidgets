import sys
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QSplitterHandle

from cgwidgets.delegates import TansuDelegate


class AbstractBidirectionalWidget(TansuDelegate):
    """

    Resizing... Block hovering / resizing
    Allow size setting
    """

    def __init__(self, parent=None, orientation=Qt.Vertical):
        super(AbstractBidirectionalWidget, self).__init__(parent, orientation=orientation)
        self.setIsSoloViewEnabled(False)
        self.setIsHandleStatic(True)


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QLabel, QApplication
    from qtpy.QtGui import QCursor
    app = QApplication(sys.argv)
    widget = AbstractBidirectionalWidget(orientation=Qt.Horizontal)

    for x in range(3):
        l = QLabel(str(x))
        l.setStyleSheet("color: rgba(255,0,0,255)")
        widget.addWidget(l)

    widget.move(QCursor.pos())
    widget.show()
    widget.resize(256, 256)
    sys.exit(app.exec_())

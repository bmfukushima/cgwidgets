'''
To Do...
    * HSV
        Setup Gradient for QGraphicsView
            From Color Widget
    * Unit
        Set up Gradient (style sheet)
            From Ladder Delegate
'''
import sys

from qtpy.QtWidgets import QDesktopWidget, QApplication, QWidget
from qtpy.QtCore import Qt


class AbstractSlideBar(QWidget):
    """
    This should be abstract
        SliderBar--> HueAbstractSlideBar / SatAbstractSlideBar / ValueAbstractSlideBar / Unit Slide Bar...
    print(Qt.AlignLeft) 1
    print(Qt.AlignRight) 2
    print(Qt.AlignTop) 32
    print(Qt.AlignBottom) 64
    """
    def __init__(self, parent=None):
        super(AbstractSlideBar, self).__init__(parent)

        self.setWindowFlags(Qt.FramelessWindowHint)

        self.screen_geometry = QDesktopWidget().screenGeometry(-1)
        self.screen_width = self.screen_geometry.width()
        self.screen_height = self.screen_geometry.height()
        self.screen_pos = self.screen_geometry.topLeft()

        self.setFixedWidth(self.screen_width)
        self.setFixedHeight(50)

    def setPosition(self, alignment):
        """
        Determines where on the monitor the widget should be located
        
        Args:
            Alignment (QtCore.Qt.Alignment): Determines where on the
            monitor to position the widget.
                AlignLeft
                AlignRight
                AlignTop
                AlignBottom
        """
        _accepted = [
            Qt.AlignLeft,
            Qt.AlignRight,
            Qt.AlignTop,
            Qt.AlignBottom
        ]

        if alignment in _accepted:
            if alignment == Qt.AlignLeft:
                pass
            elif alignment == Qt.AlignRight:
                pass
            elif alignment == Qt.AlignTop:
                pass
            elif alignment == Qt.AlignBottom:
                pass

    def keyPressEvent(self, event, *args, **kwargs):
        if event.key() == Qt.Key_Escape:
            self.close()
        return QWidget.keyPressEvent(self, event, *args, **kwargs)


class UnitSlideBar(AbstractSlideBar):
    """
    Displays a bar on a cardinal position relative to the monitor
    (Top, Bottom, Left Right).  That this bar will have two colors,
    which will display how far a user slide has gone before the
    next tick is registered to be updated
    """
    def __init__(self, parent=None):
        super(UnitSlideBar, self).__init__(parent)

    """ PROPERTIESS """
    def getBGSlideColor(self):
        return self._bg_slide_color

    def setBGSlideColor(self, bg_slide_color):
        self._bg_slide_color = bg_slide_color

    def getFGSlideColor(self):
        return self._fg_slide_color

    def setFGSlideColor(self, fg_slide_color):
        self._fg_slide_color = fg_slide_color

    def __update(self, xpos):
        style_sheet = """
        background: qlineargradient(
            x1:{xpos1} y1:0,
            x2:{xpos2} y2:0,
            stop:0 rgba{bgcolor},
            stop:1 rgba{fgcolor}
        );
        """.format(
                xpos1=str(xpos),
                xpos2=str(xpos + 0.01),
                bgcolor=repr(self.getBGSlideColor()),
                fgcolor=repr(self.getFGSlideColor())
            )
        self.setStyleSheet(style_sheet)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = AbstractSlideBar()
    w.show()
    sys.exit(app.exec_())
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

class AbstractSlideBar(QWidget):
    """
    This should be abstract
        SliderBar--> HueAbstractSlideBar / SatAbstractSlideBar / ValueAbstractSlideBar / Unit Slide Bar...
    """
    def __init__(self, parent=None):
        super(AbstractSlideBar, self).__init__(parent)

        self.screen_geometry = QDesktopWidget().screenGeometry(-1)
        self.screen_width = self.screen_geometry.width()
        self.screen_height = self.screen_geometry.height()
        self.screen_pos = self.screen_geometry.topLeft()
        
        self.setFixedWidth(self.screen_width)
        self.setFixedHeight(50)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = AbstractSlideBar()
    w.show()
    sys.exit(app.exec_())
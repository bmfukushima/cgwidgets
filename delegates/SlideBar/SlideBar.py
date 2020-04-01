import sys

from qtpy.QtWidgets import QDesktopWidget, QApplication, QWidget

class SlideBar(QWidget):
    """
    This should be abstract
        SliderBar--> HueSlideBar / SatSlideBar / ValueSlideBar / Unit Slide Bar...
    """
    def __init__(self, parent=None):
        super(SlideBar, self).__init__(parent)

        self.screen_geometry = QDesktopWidget().screenGeometry(-1)
        self.screen_width = self.screen_geometry.width()
        self.screen_height = self.screen_geometry.height()
        self.screen_pos = self.screen_geometry.topLeft()
        
        self.setFixedWidth(self.screen_width)
        self.setFixedHeight(50)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = SlideBar()
    w.show()
    sys.exit(app.exec_())
import sys

from qtpy.QtWidgets import QApplication, QWidget

from cgwidgets.utils import installSlideDelegate
from cgwidgets.delegates import SlideDelegate

class TestWidget(QWidget):
    def __init__(self, parent=None):
        super(TestWidget, self).__init__(parent)
        self.value = .75
        print('init?')
        self.slider = installSlideDelegate(self, sliderPosMethod=self.testSliderPos)
        self.slider.show()

    def testSliderPos(self):
        return self.value


if __name__ == '__main__':
    app = QApplication(sys.argv)
    print('what')
    print(dir(SlideDelegate))
    print(SlideDelegate.UNIT)

    w = TestWidget()
    w.show()
    sys.exit(app.exec_())
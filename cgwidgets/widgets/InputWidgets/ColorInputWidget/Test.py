import logging
import sys

""" TESTING """
from qtpy.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsLineItem,
QGraphicsEllipseItem, QGraphicsTextItem, QWidget, QLabel, QApplication
)
from qtpy.QtCore import QEvent

from qtpy.QtGui import QColor, QBrush, QPen, QCursor


class TestWidget(QLabel):
    def __init__(self, parent=None):
        super(TestWidget, self).__init__(parent)
        self.setText('5')

    def setValue(self, value):
        print(value)
        self.setText(str(value))


class TestWidgetItem(QGraphicsView):
    def __init__(self, parent=None):
        super(TestWidgetItem, self).__init__(parent)
        scene = QGraphicsScene()
        self.setScene(scene)

        self.line_item = LineItem()
        self.line_item.setLine(0, 0, 10, 10)

        self.line_item2 = LineItem()
        self.line_item2.setLine(30, 30, 40, 40)

        self.circle_item = CenterManipulatorItem()
        self.circle_item.setRect(10, 10, 50, 50)

        self.text_item = TextItem()

        self.scene().addItem(self.text_item)
        self.scene().addItem(self.circle_item)
        self.scene().addItem(self.line_item)
        self.scene().addItem(self.line_item2)


        self.scene().setSceneRect(0,0,100,100)
        self.setMouseTracking(True)

        #QApplication.processEvents()
        # installStickyValueAdjustItemDelegate(self.line_item2, pixels_per_tick=100, value_per_tick=0.01)
        # installStickyValueAdjustItemDelegate(self.line_item, pixels_per_tick=100, value_per_tick=0.01)

    def mouseReleaseEvent(self, event):
        event.ignore()
        QGraphicsView.mouseReleaseEvent(self, event)

    def mouseMoveEvent(self, event):
        event.ignore()
        QGraphicsView.mouseMoveEvent(self, event)


class TestFilter(QWidget):
    def __init__(self, parent=None):
        super(TestFilter, self).__init__(parent)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonRelease:
            print("release")

        if event.type() == QEvent.MouseButtonPress:
            print('press it')
        return False

class CenterManipulatorItem(QGraphicsEllipseItem):
    def __init__(self, parent=None):
        super(CenterManipulatorItem, self).__init__(parent)
        # pen = self.pen()
        # pen.setStyle(Qt.NoPen)
        # pen.setWidth(0)
        # self.setPen(pen)
        self.value = 1

    def setColor(self, color=QColor(255, 0, 0)):
        self.setBrush(QBrush(color))

    def setValue(self, value):
        self.value = value

    def getValue(self):
        return self.value


class LineItem(QGraphicsLineItem):
    def __init__(self, parent=None):
        super(LineItem, self).__init__(parent)
        self.setLine(0, 0, 25, 25)
        self.value = 1
        self.setSize(15, 15)

    def setSize(self, width, height, hand_width=4):
        """
        width (int): this is how wide the slider is.  This is the length
            parallel to the hand
        height (int): how tall the slider is, this is the size going down
            the same axis as the hand
        """

        self.setLine(
            (-width * 0.5) - (hand_width * 2), 0,
            width + hand_width, 0
        )
        pen = QPen()
        pen.setWidth(height)
        self.setPen(pen)

    def setColor(self, color=QColor(255, 0, 0)):
        self.setBrush(QBrush(color))

    def setValue(self, value):
        self.value = value

    def getValue(self):
        return self.value


class TextItem(QGraphicsTextItem):
    def __init__(self, parent=None):
        super(TextItem, self).__init__(parent)
        self.setValue("12.0")

    def setValue(self, value):
        self._value = float(value)
        self.setPlainText(str(value))

    def getValue(self):
        return self._value


def testWidget():
   # double delegate use case

    w = QWidget()
    l = QVBoxLayout(w)
    w2 = TestWidget()
    w3 = QLabel('test')
    l.addWidget(w2)
    l.addWidget(w3)

    # todo fix invisible widget not allowing clicking?
    installInvisibleWidgetEvent(w2, activation_widget=w3)
    ef = installStickyValueAdjustWidgetDelegate(w2, drag_widget=w3, activation_widget=w3)

    # simple use case
    ef = installStickyValueAdjustWidgetDelegate(w2)

    #example user update functino
    ef.setUserUpdateFunction(testUpdate)

    ef.setValuePerTick(.001)
    ef.setPixelsPerTick(50)

    return w


def testItem():
    view = TestWidgetItem()
    test_filter = TestFilter(test_widget)
    view.installEventFilter(test_filter)
    #ef = installStickyValueAdjustItemDelegate(w.text_item, activation_item=w.circle_item)
    #ef = installStickyValueAdjustItemDelegate(w.line_item, pixels_per_tick=100, value_per_tick=0.01)

    return view


if __name__ == '__main__':
    from qtpy.QtWidgets import QVBoxLayout
    from cgwidgets.utils import installInvisibleWidgetEvent
    from cgwidgets.utils import installStickyValueAdjustItemDelegate, installStickyValueAdjustWidgetDelegate
    app = QApplication(sys.argv)
    logging.basicConfig(level=logging.DEBUG)


    def testUpdate(obj, original_value, slider_pos, num_ticks):
        print('obj == %s'%obj)
        print('original_value == %s'%original_value)
        print('slider pos == %s'%slider_pos)
        print('num_ticks == %s'%num_ticks)

    test_widget = testWidget()


    test_view = testItem()


    test_view.show()
    test_view.move(QCursor.pos())
    test_view.resize(100, 100)

    sys.exit(app.exec_())

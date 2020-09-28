import sys

from qtpy.QtWidgets import (
    QApplication, QStackedWidget, QLabel, QFrame, QVBoxLayout,
    QGraphicsView, QGraphicsScene, QGraphicsItemGroup, QGraphicsTextItem,
    QGraphicsRectItem, QGraphicsLineItem, QWidget
)
from qtpy.QtCore import (Qt, QPoint)
from qtpy.QtGui import (
    QColor, QCursor, QPen
)

from cgwidgets.utils import getWidgetAncestor, attrs, getWidgetAncestorByName
from cgwidgets.settings.colors import iColor
from cgwidgets.widgets.InputWidgets.ColorInputWidget import ColorGradientMainWidget


class ClockDisplayWidget(QWidget):
    """
    This is the cover that goes over the gradient so that it doesn't spam color at
    the user and hurt their precious precious eyes
    """
    def __init__(self, parent=None):
        super(ClockDisplayWidget, self).__init__(parent=parent)
        QVBoxLayout(self)

        self.scene = ClockDisplayScene(self)
        self.view = ClockDisplayView(self.scene)

        self.layout().addWidget(self.view)

        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("background-color: rgba(0,0,255,255)")

    def resizeEvent(self, event):
        #self.scene.setSceneRect(0, 0, self.width(), self.height())
        return QWidget.resizeEvent(self, event)

    def enterEvent(self, *args, **kwargs):
        color_display_widget = getWidgetAncestorByName(self, "ColorInputWidget")
        if color_display_widget:
            color_display_widget.setCurrentIndex(1)
        return QLabel.enterEvent(self, *args, **kwargs)


class ClockDisplayView(QGraphicsView):
    def __init__(self, parent=None):
        super(ClockDisplayView, self).__init__(parent)
        self.setStyleSheet("background-color: rgba(255,0,255,255)")

    def resizeEvent(self, *args, **kwargs):
        """
        allow widget to resize with the rectangle...
        """
        # update scene rect
        rect = self.geometry()
        self.scene().setSceneRect(
            rect.topLeft().x(),
            rect.topLeft().y(),
            rect.width()-2,
            rect.height()-2
        )

        # update scene hands
        print(rect)
        self.scene().updateHands()

        return QGraphicsView.resizeEvent(self, *args, **kwargs)


class ClockDisplayScene(QGraphicsScene):
    """
    Scene to display the clock

    Attributes:
        hands_items (dict): dictionary of all of the hands items mapped to
            "hue" : item
        rgba_list  (list): of strings for each RGBA color arg
            ["red", "green", "blue", "alpha"]
        hsv_list (list): of strings for each HSV color arg
            ["hue", "saturation", "value"]
    """
    def __init__(self, parent=None):
        super(ClockDisplayScene, self).__init__(parent)
        self.hands_items = {}
        self.rgba_list = ["red", "green", "blue", "alpha"]
        self.hsv_list = ["hue", "saturation", "value"]

        # create clock hands
        for color_arg in self.rgba_list + self.hsv_list:
            new_item = ClockHandItem()
            self.hands_items[color_arg] = new_item
            self.addItem(new_item)

    def updateHands(self):
        """
        Updates the size of the individual hands
        orig_x / y (float): center of scene
        length ( float): how long each hand should be
        """
        rect = self.sceneRect()
        width = rect.width()
        height = rect.height()
        length = min(width, height) * 0.45
        orig_x = width / 2
        orig_y = height / 2

        for count, color_arg in enumerate(self.rgba_list):
            hand = self.hands_items[color_arg]
            hand.setLine(0, 0, 0, length)
            hand.setRotation(count * 45 + 22.5 + 90)
            hand.setPos(orig_x, orig_y)


class ClockHandGroupItem(QGraphicsItemGroup):
    def __init__(self, parent=None):
        super(ClockHandGroupItem, self).__init__(parent)



class ClockHandItem(QGraphicsLineItem):
    def __init__(self, parent=None):
        super(ClockHandItem, self).__init__(parent)

        self.setLine(0, 0, 0, 50)

        pen = QPen()
        pen.setColor(QColor(255,0,0))
        pen.setWidth(3)

        # pen1 = QPen()
        # pen1.setColor(QColor(0, 0, 0))
        # pen1.setDashPattern([line_length, total_line_space])
        # pen1.setWidth(width)
        # self.line_1.setPen(pen1)

class ClockHandPickerItem(QGraphicsLineItem):
    def __init__(self, parent=None):
        super(ClockHandPickerItem, self).__init__(parent)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    color_widget = ClockDisplayWidget()
    # color_widget.setLinearCrosshairDirection(Qt.Vertical)
    color_widget.show()
    color_widget.move(QCursor.pos())
    sys.exit(app.exec_())


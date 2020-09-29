import sys

from qtpy.QtWidgets import (
    QApplication, QLabel, QVBoxLayout,
    QGraphicsView, QGraphicsScene, QGraphicsItemGroup, QGraphicsTextItem, QGraphicsItem,
    QGraphicsLineItem, QWidget
)
from qtpy.QtCore import (Qt, QPoint, QRectF)
from qtpy.QtGui import (
    QColor, QCursor, QPen, QLinearGradient, QBrush, QGradient
)

from cgwidgets.utils import attrs, getWidgetAncestorByName, draw
from cgwidgets.settings.colors import iColor


class ClockDisplayWidget(QWidget):
    """
    This is the cover that goes over the gradient so that it doesn't spam color at
    the user and hurt their precious precious eyes
    """
    def __init__(self, parent=None):
        super(ClockDisplayWidget, self).__init__(parent=parent)
        # create scene
        QVBoxLayout(self)

        self.scene = ClockDisplayScene(self)
        self.view = ClockDisplayView(self.scene)

        self.layout().addWidget(self.view)

        # setup display
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("background-color: rgba{rgba_gray_2}".format(**iColor.style_sheet_args))

    def updateDisplay(self, color):
        """
        Runs through every widget, and sets their crosshair based off of the
        color that is provided

        color (QColor): color to update the display to
        """
        # get widget list
        # compare args?
        pass

    def resizeEvent(self, event):
        return QWidget.resizeEvent(self, event)

    def enterEvent(self, *args, **kwargs):
        """
        This is for the actual top level display
        TODO:
            Not sure if I'm going to use this moving forward...
        """
        color_display_widget = getWidgetAncestorByName(self, "ColorInputWidget")
        if color_display_widget:
            color_display_widget.setCurrentIndex(1)
        return QLabel.enterEvent(self, *args, **kwargs)


class ClockDisplayView(QGraphicsView):
    def __init__(self, parent=None):
        super(ClockDisplayView, self).__init__(parent)

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
        hand_length (int): length of the hand (the long portion)
        value (float): The current value of this specific slider
    """
    def __init__(self, parent=None):
        super(ClockDisplayScene, self).__init__(parent)
        self.hands_items = {}
        self.rgba_list = [attrs.RED, attrs.GREEN, attrs.BLUE, attrs.ALPHA]
        self.hsv_list = [attrs.HUE, attrs.SATURATION, attrs.VALUE]

        # create clock hands
        for color_arg in self.rgba_list + self.hsv_list:
            new_item = ClockHandGroupItem(color_arg)
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
        length = min(width, height) * 0.5
        orig_x = width / 2
        orig_y = height / 2
        for count, color_arg in enumerate(self.hsv_list):
            hand = self.hands_items[color_arg]
            hand.show()

            # resize hand length
            _length = length - hand.getOffset()
            if length < 0:
                hand.hide()
            hand.setLength(_length)
            hand.updateGradient()

            # set crosshair pos
            hand.setValue(0.25)

            # transform hand
            hand.setTransformOriginPoint(0, 10)
            hand.setRotation(count * 60 + 30)
            hand.setPos(orig_x, orig_y)

        for count, color_arg in enumerate(self.rgba_list):
            hand = self.hands_items[color_arg]
            hand.show()

            # resize hand length
            _length = length - hand.getOffset()
            if length < 0:
                hand.hide()
            hand.setLength(_length)
            hand.updateGradient()

            # set crosshair pos
            hand.setValue(0.25)

            # transform hand
            hand.setTransformOriginPoint(0, 10)
            hand.setRotation(count * 45 + 180 + 22.5)
            hand.setPos(orig_x, orig_y)


class ClockHandGroupItem(QGraphicsItemGroup):
    def __init__(self, gradient_type=attrs.VALUE):
        super(ClockHandGroupItem, self).__init__()

        # create items
        self.hand = ClockHandItem(gradient_type)
        self.hand_crosshair = ClockHandPickerItem()

        self.addToGroup(self.hand)
        self.addToGroup(self.hand_crosshair)

        # setup default attrs
        self.setLength(50)
        self.setOffset(30)

    """ EVENTS"""
    def mousePressEvent(self, event):
        print ("CLICKKCKCKCK")
        return QGraphicsItemGroup.mousePressEvent(self, event)

    """ DISPLAY """
    def updateGradient(self):
        self.hand.updateGradient()

    """ PROPERTIES """
    def getOffset(self):
        return self.hand.offset()

    def setOffset(self, offset):
        self.hand.setOffset(offset)

    def getValue(self):
        return self._value

    def setValue(self, value):
        """
        sets the value, and updates the crosshair
        value (float): value to be set to.  This is between 0-1 and will be a percentage
            of the length of the hand.
        """
        self._value = value
        self.hand_crosshair.setPos(0, (self.length() * value) + self.getOffset())

    def length(self):
        return self._length

    def setLength(self, length):
        self._length = length
        self.hand.setLength(length)

    def setCrosshairSize(self, width, height):
        """
        Sets the size of the color picker

        width (int): this is how wide the slider is.  This is the length
            parallel to the hand
        height (int): how tall the slider is, this is the size going down
            the same axis as the hand
        """
        self.hand_crosshair.setLine(width, height)


class ClockHandItem_OLD(QGraphicsLineItem):
    def __init__(self, parent=None):
        super(ClockHandItem_OLD, self).__init__(parent)

        self.setLine(0, 0, 0, 50)

        pen = QPen()
        pen.setColor(QColor(255, 0, 0))
        pen.setWidth(1)
        self.setPen(pen)

        # pen1 = QPen()
        # pen1.setColor(QColor(0, 0, 0))
        # pen1.setDashPattern([line_length, total_line_space])
        # pen1.setWidth(width)
        # self.line_1.setPen(pen1)


class ClockHandItem(QGraphicsItem):
    """
    Custom graphics item that has a gradient as a background.

    Items fill is determined by their paint method
    Args:

        gradient_type (attrs.COLOR): What type of gradient this is
            RED | GREEN | BLUE | ALPHA | HUE | SAT | VALUE

    Attributes:
        gradient (QLinearGradient): The gradient to be displayed.  This is wrapped
            in a QBrush in the paint event
        width (int): how wide the line is
        offset (int): how far from the origin (center) the line is
        length (int): how long the line is
    """

    def __init__(self, gradient_type):
        super(ClockHandItem, self).__init__()
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self._width = 4
        self._length = 200
        self._offset = 0
        self._rectangle = QRectF(0, self._offset, self._width, self._length)

        # setup default bg
        self.gradient_type = gradient_type
        self.updateGradient()

    def setBrush(self, brush):
        self._brush = brush
        self.update()

    def boundingRect(self):
        """
        method to set the actual bounding rectangle of the item
        """
        return self._rectangle

    def updateGradient(self):
        """
        Draws the gradient
        """
        if not hasattr(self, '_gradient'):
            self._gradient = draw.drawColorTypeGradient(self.gradient_type, self.width(), self.length())
            self.setGradient(self._gradient)
        # update gradient size
        self._gradient.setStart(QPoint(0, self.offset()))
        self._gradient.setFinalStop(QPoint(self.width(), self.length() + self.offset()))

    def paint(self, painter=None, style=None, widget=None):
        painter.fillRect(self._rectangle, QBrush(self.getGradient()))

    """ PROPERTIES """
    def getGradient(self):
        return self._gradient

    def setGradient(self, gradient):
        self._gradient = gradient

    def offset(self):
        return self._offset

    def setOffset(self, offset):
        rect = QRectF(0, offset, self._width, self._length)
        self._offset = offset
        self._rectangle = rect

    def length(self):
        return self._length

    def setLength(self, length):
        rect = QRectF(0, self._offset, self._width, length)
        self._length = length
        self._rectangle = rect

    def width(self):
        return self._width

    def setWidth(self, width):
        """
        TODO
         ClockHandPickerItem.setSize()
            this needs to update the hand width so that it will scale.
        """
        rect = QRectF(0, self._offset, self._width, self._length)
        self._width = width
        self._rectangle = rect
        # setSize

    @property
    def gradient_type(self):
        return self._gradient_type

    @gradient_type.setter
    def gradient_type(self, gradient_type):
        self._gradient_type = gradient_type


class ClockHandPickerItem(QGraphicsLineItem):
    def __init__(self, parent=None):
        super(ClockHandPickerItem, self).__init__(parent)
        self.setSize(15, 3)

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
        #self.setRotation(90)
        pen = QPen()
        pen.setWidth(height)
        self.setPen(pen)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    color_widget = ClockDisplayWidget()
    # color_widget.setLinearCrosshairDirection(Qt.Vertical)
    color_widget.show()
    color_widget.move(QCursor.pos())
    sys.exit(app.exec_())


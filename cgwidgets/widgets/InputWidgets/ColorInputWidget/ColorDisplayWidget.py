"""
TODO:
    Cursor Position setting to last instead of first?
        self.setCursorPosition(0)
            FloatInputWidget
            LadderDelegate

"""

import sys
import math

from qtpy.QtWidgets import (
    QApplication, QLabel, QVBoxLayout,
    QGraphicsView, QGraphicsScene, QGraphicsItemGroup, QGraphicsTextItem, QGraphicsItem,
    QGraphicsLineItem, QWidget, QFrame, QHBoxLayout
)
from qtpy.QtCore import (Qt, QPoint, QRectF)
from qtpy.QtGui import (
    QColor, QCursor, QPen, QLinearGradient, QBrush, QGradient
)

from cgwidgets.widgets import FloatInputWidget
from cgwidgets.utils import attrs, draw, getWidgetAncestorByName, getFontSize
from cgwidgets.settings.colors import iColor, getHSVRGBAFloatFromColor


class ClockDisplayWidget(QWidget):
    """
    This is the cover that goes over the gradient so that it doesn't spam color at
    the user and hurt their precious precious eyes

    Attributes:
        color_args_values_dict (dict): of key pair values relating to the
            individual display values of each color arg
    """
    def __init__(self, parent=None):
        super(ClockDisplayWidget, self).__init__(parent=parent)
        # create scene
        QVBoxLayout(self)
        self._offset = 30

        self.scene = ClockDisplayScene(self)
        self.view = ClockDisplayView(self.scene)

        self.layout().addWidget(self.view)

        # setup display
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("background-color: rgba{rgba_gray_2}".format(**iColor.style_sheet_args))
        self._createDisplayLabels()
        self._updateDisplayLabelsPosition()
        self.updateDisplay()

    """ API """
    def getOffset(self):
        return self._offset

    def setOffset(self, offset):
        self._offset = offset

        # update all hands offsets...
        for color_arg in attrs.RGBA_LIST + attrs.HSV_LIST:
            hand_widget = self.scene.hands_items[color_arg]
            hand_widget.setOffset(offset)

        # update display
        self.updateDisplay()

    def updateDisplay(self, color=QColor(128, 128, 255, 255)):
        """
        Runs through every widget, and sets their crosshair based off of the
        color that is provided

        color (QColor): color to update the display to
        """
        color_args_dict = getHSVRGBAFloatFromColor(color)
        # update headers
        self.rgba_header_widget.updateUserInputs(color_args_dict)
        self.hsv_header_widget.updateUserInputs(color_args_dict)
        # update hands
        for color_arg in color_args_dict:
            # get value widget
            value = color_args_dict[color_arg]

            # set hand widget
            hand_widget = self.scene.hands_items[color_arg]
            hand_widget.setValue(value)

    """ UTILS """
    def _createDisplayLabels(self):
        self.rgba_header_widget = ClockHeaderWidget(self)
        self.rgba_header_widget.layout().setAlignment(Qt.AlignRight)
        self.rgba_header_widget.createDisplayLabels(attrs.RGBA_LIST)

        self.hsv_header_widget = ClockHeaderWidget(self)
        self.hsv_header_widget.layout().setAlignment(Qt.AlignLeft)
        self.hsv_header_widget.createDisplayLabels(attrs.HSV_LIST)

    def _updateDisplayLabelsPosition(self):
        """
        On resize, this will update the position of all of the user inputs

        """
        length = min(self.width(), self.height()) * 0.5
        orig_x = self.width() * 0.5
        orig_y = self.height() * 0.5
        font_size = getFontSize(QApplication) + 2

        # set HSV Header
        self.hsv_header_widget.move(orig_x + self.getOffset(), orig_y + font_size)
        self.hsv_header_widget.setFixedSize(orig_x, font_size)

        # set RGBA Header
        self.rgba_header_widget.move(0, orig_y + font_size)
        self.rgba_header_widget.setFixedSize(orig_x - self.getOffset(), font_size)


        # OLD CIRCLE PLACEMENT
        # self._placeLabelsFromListInCircle(attrs.RGBA_LIST, offset=-1.5)
        # self._placeLabelsFromListInCircle(attrs.HSV_LIST, offset=2)

    """ NOT IN USE BUT I LIKE THIS CODE"""
    def _placeLabelsFromListInCircle(self, color_args_list, offset=0):
        """
        Places labels in a circle around the origin based off of the length

        color_args_list (list): list of color args to be placed
        offset (float): how many rotational ticks to offset

        Attrs:
            orig_x (float): x origin
            orig_y (float): y origin
            length (float): how for to place the widget from origin
            rotational_tick (radian): how many degrees one tick is in radians
        """
        orig_x = self.width() * 0.5
        orig_y = self.height() * 0.5
        length = min(orig_x, orig_y)
        rotational_tick = 1 / ( len(color_args_list) * 2 )

        for index, color_arg in enumerate(color_args_list):
            widget = self.color_args_values_dict[color_arg]
            rotation = (index+ offset) * rotational_tick

            x0 = (length * math.cos(2 * math.pi * rotation))
            y0 = (length * math.sin(2 * math.pi * rotation))
            x0 += orig_x
            y0 *= 0.8
            y0 += orig_y
            widget.move(x0, y0)

    """ EVENTS """
    def resizeEvent(self, event):
        self._updateDisplayLabelsPosition()
        self.updateDisplay()
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

    def showEvent(self, event):
        self.updateDisplay()
        return QWidget.showEvent(self, event)


class ClockHeaderWidget(QFrame):
    def __init__(self, parent=None):
        super(ClockHeaderWidget, self).__init__(parent)
        QHBoxLayout(self)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.color_args_values_dict = {}
        self.setStyleSheet("background-color: rgba(0,255,0,255)")

    def createDisplayLabels(self, color_args_list):
        self.color_args_values_dict = {}

        # create clock hands
        for index, color_arg in enumerate(color_args_list):
            new_item = FloatInputWidget(self)
            new_item.setFixedWidth(50)
            new_item.setAlignment(Qt.AlignLeft)
            new_item.setUseLadder(True, value_list=[0.0001, 0.001, 0.01, 0.1])
            new_item.setRange(True, 0, 1)
            self.color_args_values_dict[color_arg] = new_item
            self.layout().addWidget(new_item)
            new_item.setStyleSheet("background-color: rgba(0,0,0,0); border: None")

    def updateUserInputs(self, color_args_dict):
        """
        Updates the user inputs with the color args dict provided

        """
        for color_arg in self.color_args_values_dict:
            # get value widget
            try:
                input_widget = self.color_args_values_dict[color_arg]
                #hand_widget = self.scene.hands_items[color_arg]

                # set new value
                value = color_args_dict[color_arg]
                input_widget.setText(str(value))
                input_widget.setCursorPosition(0)
            except KeyError:
                pass
            #hand_widget.setValue(value)


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
        hand_length (int): length of the hand (the long portion)
        value (float): The current value of this specific slider
    """
    def __init__(self, parent=None):
        super(ClockDisplayScene, self).__init__(parent)
        self.hands_items = {}

        # create clock hands
        for color_arg in attrs.RGBA_LIST + attrs.HSV_LIST:
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
        # update hsv list
        for count, color_arg in enumerate(attrs.HSV_LIST):
            hand = self.hands_items[color_arg]
            hand.show()

            # resize hand length
            _length = length - hand.getOffset()
            if length < 0:
                hand.hide()
            hand.setLength(_length)
            hand.updateGradient()

            # set crosshair pos
            #hand.setValue(0.25)

            # transform hand
            hand.setTransformOriginPoint(0, 10)
            hand.setRotation(count * 60 + 30 + 270)
            hand.setPos(orig_x, orig_y)

        # update rgba list
        for count, color_arg in enumerate(attrs.RGBA_LIST):
            hand = self.hands_items[color_arg]
            hand.show()

            # resize hand length
            _length = length - hand.getOffset()
            if length < 0:
                hand.hide()
            hand.setLength(_length)
            hand.updateGradient()

            # set crosshair pos
            #hand.setValue(0.25)

            # transform hand
            hand.setTransformOriginPoint(0, 10)
            hand.setRotation(count * 45 + 90 + 22.5)
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
    color_widget.setOffset(50)
    # color_widget.setLinearCrosshairDirection(Qt.Vertical)
    color_widget.show()
    color_widget.move(QCursor.pos())
    sys.exit(app.exec_())


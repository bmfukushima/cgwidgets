"""
TODO:
    *   LadderDelegate | Live Sliding
            - RGB Header sliders Live Updates causing recursive error

Notes:
    *   Border offset ( the area between the giant circle in the middle and
        the surrounding hands / values ) is hard coded to 10.
            - Gradient update
            - Length update
"""

import sys
import math

from qtpy.QtWidgets import (
    QApplication, QLabel, QVBoxLayout,
    QGraphicsView, QGraphicsScene, QGraphicsItemGroup, QGraphicsItem,
    QGraphicsEllipseItem,
    QGraphicsLineItem, QWidget, QFrame, QBoxLayout
)
from qtpy.QtCore import (Qt, QPoint, QRectF)
from qtpy.QtGui import (
    QColor, QCursor, QPen, QLinearGradient, QBrush
)

from cgwidgets.utils import (
    attrs, draw, getWidgetAncestor, getWidgetAncestorByName,
    getFontSize, installStickyAdjustDelegate
)
from cgwidgets.settings.colors import (
    iColor, getHSVRGBAFloatFromColor, updateColorFromArgValue,
)
from cgwidgets.widgets.InputWidgets.ColorInputWidget import (
    ColorHeaderWidgetItem, AbstractColorDelegate, AbstractColorView,
    ColorHeaderWidget
)


class AbstractColorClock(QWidget):
    """
    This is the cover that goes over the gradient so that it doesn't spam color at
    the user and hurt their precious precious eyes

    Attributes:
        color_header_items_dict (dict): of key pair values relating to the
            individual display values of each color arg
    """
    def __init__(self, parent=None):
        super(AbstractColorClock, self).__init__(parent=parent)
        # create scene
        self._offset = 30
        self._header_item_size = 50
        self._color = QColor(128, 128, 255)
        self._updating = False

        self.scene = ClockDisplayScene(self)
        self.view = ClockDisplayView(self.scene)

        self.layout().addWidget(self.view)

        # setup display
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("background-color: rgba{rgba_gray_2}".format(**iColor.style_sheet_args))
        self._createHeaderWidgetItems()
        self._updateHeaderWidgetPosition()
        self.setOffset(30)
        self.updateDisplay()

    """ API """
    def offset(self):
        return self.scene.offset()

    def setOffset(self, offset):
        self.scene.setOffset(offset)

        self.scene.center_manipulator_item.updateRadius(offset)
        # update display
        self.updateDisplay()

    def color(self):
        return self._color

    def setColor(self, color):
        """
        Sets the color of this widget

        Args:
            color (QColor):
        """
        self._color = color
        # self.scene.center_manipulator_item.setColor(color)
        # self.scene.update()
        self.updateDisplay()

    def headerItemSize(self):
        return self._header_item_size

    def setHeaderItemSize(self, header_item_size):
        """
        Sets the header_item_size of this widget

        Args:
            header_item_size (QColor):
        """
        self._header_item_size = header_item_size

    """ UTILS """
    def _createHeaderWidgetItems(self):
        self.rgba_header_widget = ClockHeaderWidget(self)
        self.rgba_header_widget.main_layout.setAlignment(Qt.AlignRight | Qt.AlignTop)
        self.rgba_header_widget.createHeaderItems(attrs.RGBA_LIST, abbreviated_title=True)

        self.hsv_header_widget = ClockHeaderWidget(self)
        self.hsv_header_widget.main_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.hsv_header_widget.createHeaderItems(attrs.HSV_LIST, abbreviated_title=True)

        self.header_item_height = getFontSize(QApplication) * 3 + 5
        self.header_item_width = 40
        header_widgets = {
            **self.hsv_header_widget.getWidgetDict(),
            **self.rgba_header_widget.getWidgetDict()
        }
        for color_arg in header_widgets:
            header_item = header_widgets[color_arg]

            header_item.setMinimumHeight(self.header_item_height)
            header_item.setMinimumWidth(self.header_item_width)

    def updateColorFromArgValue(self, color_arg, value):
        """
        Updates the current color from the color_arg/value provided
        color_arg (attrs.COLOR_ARG):
        value (float)
        """
        new_color = updateColorFromArgValue(self.color(), color_arg, float(value))
        self.setColor(new_color)

    """ PLACE HEADER"""
    def _updateHeaderWidgetPosition(self):
        """
        On resize, this will update the position of all of the user inputs
        This will do a dynamic placement based off of the current ratio of
        the widget

        """
        length = min(self.width(), self.height()) * 0.5
        # setup default attrs
        # setup full length
        if length < self.headerItemSize() * 4:
            # align to top / bottom
            if self.height() > self.width():
                self._placeHeaderVertical()
            # align to sides
            else:
                self._placeHeaderHorizontal()

        # setup middle
        else:
            self._placeHeaderCenter()
            # set HSV Header

        # OLD CIRCLE PLACEMENT
        # self._placeLabelsFromListInCircle(attrs.RGBA_LIST, offset=-1.5)
        # self._placeLabelsFromListInCircle(attrs.HSV_LIST, offset=2)

    def _placeHeaderVertical(self):
        """
        Places the header vertically.  This will place the HSV header on the bottom
        of the display, and the RGBA header on the top of the display.

        Args:
            item_height (int): this will determine how tall each item is
        """
        self.hsv_header_widget.move(0, self.height() - self.headerItemSize())
        self.hsv_header_widget.setFixedSize(self.width(), self.headerItemSize())
        self.hsv_header_widget.main_layout.setDirection(QBoxLayout.LeftToRight)

        self.rgba_header_widget.move(0, 0)
        self.rgba_header_widget.setFixedSize(self.width(), self.headerItemSize())
        self.rgba_header_widget.main_layout.setDirection(QBoxLayout.LeftToRight)

    def _placeHeaderHorizontal(self):
        """
        Places the header horizontally.  This will put the HSV header on the left
        side of the display, and the RGBA header on the right side of the display
        item_width (int): the fixed item_width this widget should take up.
        Args:
            item_width (int): this will determine how wide each item is
        """
        # set hsv header
        ypos = (self.height() * 0.5) - (1.5 * self.header_item_height)
        self.hsv_header_widget.move(0, ypos)
        self.hsv_header_widget.setFixedSize(self.headerItemSize(), self.height())
        self.hsv_header_widget.main_layout.setDirection(QBoxLayout.TopToBottom)

        # set rgba header
        ypos = (self.height() * 0.5) - (2 * self.header_item_height)
        self.rgba_header_widget.move(self.width() - self.headerItemSize(), ypos)
        self.rgba_header_widget.setFixedSize(self.headerItemSize(), self.height())
        self.rgba_header_widget.main_layout.setDirection(QBoxLayout.TopToBottom)

    def _placeHeaderCenter(self):
        """
        Places the header in the center
        :return:
        """
        # get attrs
        orig_x = self.width() * 0.5
        orig_y = self.height() * 0.5
        x_offset = 10
        # set HSV header
        self.hsv_header_widget.move(0, orig_y - (self.header_item_height * 0.5))
        self.hsv_header_widget.setFixedSize(orig_x - self.offset() - x_offset, self.header_item_height + 2)
        self.hsv_header_widget.main_layout.setDirection(QBoxLayout.LeftToRight)

        # set RGBA Header
        self.rgba_header_widget.move(orig_x + self.offset() + x_offset, orig_y - (self.header_item_height * 0.5))
        self.rgba_header_widget.setFixedSize(orig_x - self.offset() - x_offset, self.header_item_height + 2)
        self.rgba_header_widget.main_layout.setDirection(QBoxLayout.LeftToRight)

    # """ NOT IN USE BUT I LIKE THIS CODE"""
    # def _placeLabelsFromListInCircle(self, color_args_list, offset=0):
    #     """
    #     Places labels in a circle around the origin based off of the length
    #
    #     color_args_list (list): list of color args to be placed
    #     offset (float): how many rotational ticks to offset
    #
    #     Attrs:
    #         orig_x (float): x origin
    #         orig_y (float): y origin
    #         length (float): how for to place the widget from origin
    #         rotational_tick (radian): how many degrees one tick is in radians
    #     """
    #     orig_x = self.width() * 0.5
    #     orig_y = self.height() * 0.5
    #     length = min(orig_x, orig_y)
    #     rotational_tick = 1 / ( len(color_args_list) * 2 )
    #
    #     for index, color_arg in enumerate(color_args_list):
    #         widget = self.color_header_items_dict[color_arg]
    #         rotation = (index + offset) * rotational_tick
    #
    #         x0 = (length * math.cos(2 * math.pi * rotation))
    #         y0 = (length * math.sin(2 * math.pi * rotation))
    #         x0 += orig_x
    #         y0 *= 0.8
    #         y0 += orig_y
    #         widget.move(x0, y0)

    """ EVENTS """
    def resizeEvent(self, event):
        self._updateHeaderWidgetPosition()
        self.updateDisplay()
        return QWidget.resizeEvent(self, event)

    def showEvent(self, event):
        self.updateDisplay()
        return QWidget.showEvent(self, event)

    def updateDisplay(self):
        """
        Updates the entire display based off of the current color.
        This will update the
            * hands
            * header

        color (QColor): color to update the display to
        """
        if self._updating is False:
            self._updating = True
            self.scene.center_manipulator_item.setColor(self._color)
            self.scene.update()

            color_args_dict = getHSVRGBAFloatFromColor(self._color)
            # update headers
            # TODO This is causing the recursion issues...
            self.rgba_header_widget.updateUserInputs(color_args_dict)
            self.hsv_header_widget.updateUserInputs(color_args_dict)

            # update hands
            for color_arg in color_args_dict:
                # get value widget
                value = color_args_dict[color_arg]

                # set hand widget
                hand_widget = self.scene.hands_items[color_arg]
                hand_widget.setValue(value)

        self._updating = False


class ColorClockDelegate(AbstractColorClock, AbstractColorDelegate):
    def __init__(self, parent=None):
        super(ColorClockDelegate, self).__init__(parent)

    # def setColor(self, color):
    #     """
    #     Sets the color of this widget
    #
    #     Args:
    #         color (QColor):
    #     """
    #     AbstractColorClock.setColor(self, color)
    #     return AbstractColorDelegate.setColor(self, color)


class ColorClockView(AbstractColorClock, AbstractColorView):
    def __init__(self, parent=None):
        super(ColorClockView, self).__init__(parent)

    def setColor(self, color):
        """
        Sets the color of this widget

        Args:
            color (QColor):
        """
        #AbstractColorClock.setColor(self, color)
        self._color = color
        self.updateDisplay()
        # self.scene.center_manipulator_item.setColor(color)
        # self.scene.update()
        #return AbstractColorView.setColor(self, color)

    def enterEvent(self, *args, **kwargs):
        """
        This is for the actual top level display
        TODO:
            Not sure if I'm going to use this moving forward...
        """
        color_display_widget = getWidgetAncestorByName(self, "ColorInputWidget")
        if color_display_widget:
            color_display_widget.setCurrentIndex(1)
        return QWidget.enterEvent(self, *args, **kwargs)


class ClockHeaderWidget(ColorHeaderWidget):
    """
    This is a header that will contain the text values of each individual
    color arg (HSV / RGBA).  This will automatically be displayed on the
    top/bottom, left/right, or middle, based off of the size and dimensions
    of the parent widget.

    There should be one of these Header Widgets per color list, ie one
    HeaderWidget for RGBA and one for HSV.
    """
    def __init__(self, parent=None):
        super(ClockHeaderWidget, self).__init__(parent)

        # set up attrs
        self.setHeaderItemType(ColorGradientHeaderWidgetItem)

       # set up display
        self.setStyleSheet("background-color: rgba(0,0,0,0)")
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # disable scrollbars
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def updateUserInputs(self, color_args_dict):
        """
        Updates all of the header item user inputs from the dict
        that is provided as the color_args_dict

        color_args_dict (dict): of attrs.COLOR_ARG : ColorGradientHeaderWidgetItem

        """

        for color_arg in self.getWidgetDict():
            try:
                # get header item
                header_item = self.getWidgetDict()[color_arg]

                # set new value
                value = color_args_dict[color_arg]
                header_item.setValue(str(value))
            except KeyError:
                pass


class ColorGradientHeaderWidgetItem(ColorHeaderWidgetItem):
    """
    Attributes:
        name (str)
        value (str)
        selected (bool)

    Widgets:
        | -- QBoxLayout
                | -- label_widget (QLabel)
                | -- divider_widget (AbstractLine)
                | -- value_widget (QLabel)
    """
    def __init__(self, parent=None, title='None', value='None'):
        super(ColorGradientHeaderWidgetItem, self).__init__(parent, title)

        # update style sheets / margins
        self.setupDisplayProperties()

    def setupDisplayProperties(self):
        """
        sets up all of the display properties for each widget
            group_box (AbstractInputGroupBox)
                * disable separator
            value_widget (FloatInputWidget)

            Updates to
                * stylesheet
                * content margins
                * spacing

        """
        # self
        self.setStyleSheet("background-color: rgba(0,0,0,0)")
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        # group box
        self.group_box.display_background = True
        self.group_box.rgba_background = (0, 0, 0, 32)
        self.group_box.layout().setContentsMargins(0, 7, 0, 0)
        self.group_box.layout().setSpacing(0)
        self.group_box.displaySeparator(False)
        self.group_box.padding = 0
        self.group_box.updateStyleSheet()

        # input widget
        self.value_widget.setStyleSheet("""
            background-color: rgba{rgba_invisible};
            color: rgba{rgba_text};
            border: None
        """.format(**iColor.style_sheet_args))


""" CLOCK GRAPHICS VIEW"""
class ClockDisplayView(QGraphicsView):
    def __init__(self, parent=None):
        super(ClockDisplayView, self).__init__(parent)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scene().createHands()

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

        # update center item
        self.scene().center_manipulator_item.setPos(rect.width() * 0.5, rect.height() * 0.5)

        return QGraphicsView.resizeEvent(self, *args, **kwargs)

    def mouseReleaseEvent(self, event):
        event.ignore()
        QGraphicsView.mouseReleaseEvent(self, event)

    def mouseMoveEvent(self, event):
        event.ignore()
        QGraphicsView.mouseMoveEvent(self, event)


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
        self._offset = 30

        # draw center manipulator
        self.center_manipulator_item = CenterManipulatorItem()
        self.addItem(self.center_manipulator_item)

        # # create hands
        # self.createHands()

    def createHands(self):
        """
        Creates all of the clock hands for RGBA / HSV and returns them
        in the dict hands_items
        """
        # create clock hands
        self.hands_items = {}

        for color_arg in attrs.RGBA_LIST + attrs.HSV_LIST:
            # create new item
            hand_item = ClockHandGroupItem(color_arg)

            # create item
            self.addItem(hand_item)
            self.hands_items[color_arg] = hand_item

            # add filter
            installStickyAdjustDelegate(
                hand_item.hand_crosshair, pixels_per_tick=25, value_per_tick=0.01)

    def updateHands(self):
        """
        Updates the size of the individual hands
        orig_x / y (float): center of scene
        length ( float): how long each hand should be

        Todo:
            figure out how to do the differential for the offset of the widgets
        """

        self.__updateHandLength()
        self.__updateHandRotation()

    def __getHandLength(self):
        """
        Gets the length of the hand after all of the offsets have been applied
        """
        width = self.sceneRect().width()
        height = self.sceneRect().height()
        length = min(width, height) * 0.5
        main_widget = getWidgetAncestor(self, AbstractColorClock)
        widget_size = main_widget.headerItemSize()

        # reduce hand length
        # reduce for widgets
        height_width_difference = math.fabs(width - height)
        if height_width_difference < (widget_size * 2):
            length -= widget_size
        # reduce for cross hair
        length -= 10
        length -= self.offset()

        return length

    def __updateHandLength(self):
        # get attrs
        length = self.__getHandLength()

        # update hand
        for color_arg in attrs.HSV_LIST + attrs.RGBA_LIST:
            # get hand
            hand = self.hands_items[color_arg]

            # resize hand length
            hand.setLength(length)
            hand.updateGradient()

            # display hand
            hand.show()
            if length < 0:
                hand.hide()

    def __updateHandRotation(self):
        """
        Helper function that will rotate all of the hands to their
        appropriate positions on the clock
        """
        x_orig = self.sceneRect().width() * 0.5
        y_orig = self.sceneRect().height() * 0.5

        # rotate hands to their positions
        for count, color_arg in enumerate(attrs.HSV_LIST):
            hand = self.hands_items[color_arg]
            hand.setRotation(count * 60 + 30 + 270)
            hand.setPos(x_orig, y_orig)

        for count, color_arg in enumerate(attrs.RGBA_LIST):
            hand = self.hands_items[color_arg]
            hand.setRotation(count * 45 + 90 + 22.5)
            hand.setPos(x_orig, y_orig)

    def offset(self):
        return self._offset

    def setOffset(self, offset):
        self._offset = offset


class ClockHandGroupItem(QGraphicsItemGroup):
    def __init__(self, gradient_type=attrs.VALUE):
        super(ClockHandGroupItem, self).__init__()
        self.color_arg = gradient_type
        # create items
        self.hand = ClockHandItem(gradient_type)
        self.hand_crosshair = ClockHandCrosshairItem()

        self.addToGroup(self.hand)
        self.addToGroup(self.hand_crosshair)

        # setup default attrs
        self._length = 50

    """ DISPLAY """
    def updateGradient(self):
        self.hand.updateGradient()

    """ PROPERTIES """
    def getValue(self):
        return self._value

    def setValue(self, value):
        """
        sets the value, and updates the crosshair
        value (float): value to be set to.  This is between 0-1 and will be a percentage
            of the length of the hand.
        """
        self._value = value

        self.hand_crosshair.setPos(0, (self.length() * value) + self.scene().offset() + 10)

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
    This is the long portion of the display. On a clock, it would be the long
    hand, however, the long hand here points to
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

    Notes
        Origin is in the setLength/setWidth functions and is linked to the "offset"
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
        # if initializaing create a new gradient
        if not hasattr(self, '_gradient'):
            self._gradient = draw.drawColorTypeGradient(self.gradient_type, self.width(), self.length())
            self.setGradient(self._gradient)

        # update gradient
        try:
            self._gradient.setStart(QPoint(0, self.scene().offset() + 10))
            self._gradient.setFinalStop(QPoint(self.width(), self.length() + self.scene().offset() + 10))
        except AttributeError:
            # not yet initialized
            pass

    def paint(self, painter=None, style=None, widget=None):
        painter.fillRect(self._rectangle, QBrush(self.getGradient()))

    """ PROPERTIES """
    def getGradient(self):
        return self._gradient

    def setGradient(self, gradient):
        self._gradient = gradient

    def length(self):
        return self._length

    def setLength(self, length):
        rect = QRectF(0, self.scene().offset() + 10, self._width, length)
        self._length = length
        self._rectangle = rect

    def width(self):
        return self._width

    def setWidth(self, width):
        """
        TODO
         ClockHandCrosshairItem.setSize()
            this needs to update the hand width so that it will scale.
        """
        rect = QRectF(0, self.scene().offset() + 10, self._width, self._length)
        self._width = width
        self._rectangle = rect
        # setSize

    @property
    def gradient_type(self):
        return self._gradient_type

    @gradient_type.setter
    def gradient_type(self, gradient_type):
        self._gradient_type = gradient_type


class ClockHandCrosshairItem(QGraphicsLineItem):
    """
    The cross portion of the 't' that will show to the user where the current
    value should sit on the display
    """
    def __init__(self, parent=None):
        super(ClockHandCrosshairItem, self).__init__(parent)
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

    def setValue(self, value):
        # constrain to 0-1 range
        if value < 0:
            value = 0
        elif 1 < value:
            value = 1

        # update color value
        main_widget = getWidgetAncestor(self.scene().views()[0], AbstractColorClock)
        # main widget
        color_arg = self.group().color_arg
        main_widget.updateColorFromArgValue(color_arg, value)

    def getValue(self):
        return self.group().getValue()


class CenterManipulatorItem(QGraphicsEllipseItem):
    def __init__(self, parent=None):
        super(CenterManipulatorItem, self).__init__(parent)
        pen = self.pen()
        pen.setStyle(Qt.NoPen)
        pen.setWidth(0)
        self.setPen(pen)

    def setColor(self, color=QColor(0, 0, 0)):
        self.setBrush(QBrush(color))

    def updateRadius(self, radius):
        radius -= 4
        self.setRect(
            radius,
            radius,
            -(radius * 2),
            -(radius * 2),
        )


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    app = QApplication(sys.argv)
    color_widget = ColorClockDelegate()
    color_widget.setColor(QColor(255, 255, 128))
    color_widget.setOffset(40)
    # color_widget.setLinearCrosshairDirection(Qt.Vertical)
    color_widget.show()
    color_widget.move(QCursor.pos())
    sys.exit(app.exec_())


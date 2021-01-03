from qtpy.QtWidgets import QGraphicsItemGroup, QGraphicsLineItem
from qtpy.QtCore import Qt, QRectF, QPoint
from qtpy.QtGui import QColor, QBrush, QLinearGradient, QGradient, QPen

from cgwidgets.utils import attrs


def create1DGradient(
        width,
        height,
        direction=Qt.Horizontal,
        color1=(0, 0, 0, 1),
        color2=(1, 1, 1, 1),
):
    """
    Creates 1D Linear gradient to be displayed to the user.

    Args:
        width (int)
        height (int)
        direction (Qt.Direction): The direction the gradient should go
        color1 (QColorF): The first color in the gradient, the default value is black.
        color2 (QColorF): The second color in the gradient, the default value is white.

    Returns (QBrush)
    """
    # create QColor Floats
    colorA = QColor()
    colorA.setRgbF(*color1)
    colorB = QColor()
    colorB.setRgbF(*color2)

    # set direction
    if direction == Qt.Horizontal:
        gradient = QLinearGradient(0, 0, width, 0)
    elif direction == Qt.Vertical:
        gradient = QLinearGradient(0, 0, 0, height)

    # create brush
    gradient.setSpread(QGradient.RepeatSpread)
    gradient.setColorAt(0, colorA)
    gradient.setColorAt(1, colorB)

    return gradient


def drawColorTypeGradient(gradient_type, width, height):
    """
    Draws a gradient of the specific gradient type (color value type) with
    the specified width/height
    gradient_type (attrs.COLOR_ARG): Type of gradient to draw
        RED | GREEN | BLUE | ALPHA | HUE | SATURATION | VALUE
    width (int):
    height (int):

    """
    if gradient_type == attrs.RED:
        _gradient = create1DGradient(width, height, color2=(1, 0, 0, 1))
    elif gradient_type == attrs.GREEN:
        _gradient = create1DGradient(width, height, color2=(0, 1, 0, 1))
    elif gradient_type == attrs.BLUE:
        _gradient = create1DGradient(width, height, color2=(0, 0, 1, 1))
    elif gradient_type == attrs.ALPHA:
        _gradient = create1DGradient(width, height, color1=(0, 0, 0, 0))
    elif gradient_type in [attrs.HUE, attrs.RGBA]:
        # get Value from main widget
        value = 1
        sat = 1
        _gradient = create1DGradient(width, height)
        num_colors = 6
        _gradient.setSpread(QGradient.RepeatSpread)
        for x in range(num_colors):
            pos = (1 / num_colors) * (x)
            color = QColor()
            color.setHsvF(x * (1 / num_colors), sat, value)
            _gradient.setColorAt(pos, color)
        # set red to end
        color = QColor()
        color.setHsvF(1, sat, value)
        _gradient.setColorAt(1, color)

    elif gradient_type == attrs.SATURATION:
        _gradient = create1DGradient(width, height)
    elif gradient_type == attrs.VALUE:
        _gradient = create1DGradient(width, height)
    else:
        _gradient = create1DGradient(width, height)

    return _gradient


class DualColoredLineSegment(QGraphicsItemGroup):
    """
    One individual line segment.  This is a group because it needs to create two
    lines in order to create a multi colored dashed pattern.

    Attributes:
        spacing (int): how much space in pixels are between each line segment
    """

    def __init__(self, parent=None, width=1, color1=QColor(0, 0, 0), color2=QColor(255, 255, 255)):
        super(DualColoredLineSegment, self).__init__(parent)

        # create lines
        self.line_1 = QGraphicsLineItem()
        self.line_2 = QGraphicsLineItem()

        self.width = width
        self._length = 2
        self._spacing = 5

        # set pen
        self.setColor1(color1)
        self.setColor2(color2)

        # add lines to group
        self.addToGroup(self.line_1)
        self.addToGroup(self.line_2)

    """ DISPLAY"""
    def setColor1(self, color):
        """
        Sets the first line to the specified color

        Args:
            color (QColor): color for the line to be set to
        """
        pen = self.createPen(color)
        self.line_1.setPen(pen)

    def setColor2(self, color):
        """
        Sets the first line to the specified color

        Args:
            color (QColor): color for the line to be set to
        """
        pen = self.createPen(color, offset=True)
        self.line_2.setPen(pen)

    def updatePen(self):
        for line in [self.line_1, self.line_2]:
            pen = line.pen()
            total_line_space = self.length() + (2 * self.spacing())
            pen.setDashPattern([self.length(), total_line_space])
            pen.setWidth(self.width)
            line.setPen(pen)

    def createPen(self, color, offset=None):
        """
        Creates a pen of the color specified

        Args:
            color (QColor): color for the line to be set to
            offset (bool): if color should be offset or not.
                Since this is only two colors, this can be a boolean, rather
                than an index.
        """
        pen = QPen()
        pen.setColor(color)
        total_line_space = self.length() + (2 * self.spacing())
        if offset:
            pen.setDashOffset(self.length() + self.spacing())
        pen.setDashPattern([self.length(), total_line_space])
        pen.setWidth(self.width)

        return pen

    def setLine(self, x, y, width, height):
        self.line_1.setLine(x, y, width, height)
        self.line_2.setLine(x, y, width, height)

    """ PROPERTIES """
    def width(self):
        return self._width

    def setWidth(self, width):
        self._width = width

    def length(self):
        return self._length

    def setLength(self, length):
        self._length = length

    def spacing(self):
        return self._spacing

    def setSpacing(self, spacing):
        self._spacing = spacing


if __name__ == '__main__':
    import sys
    from qtpy.QtWidgets import QApplication, QGraphicsView, QGraphicsScene
    from qtpy.QtGui import QCursor
    app = QApplication(sys.argv)
    v = QGraphicsView()
    s = QGraphicsScene()
    v.setSceneRect(0,0,200,200)
    v.setScene(s)
    # GRADIENT
    g = drawColorTypeGradient(attrs.HUE, 100, 100)
    g.setFinalStop(0,300)
    s.setBackgroundBrush(QBrush(g))

    #LINE
    l = DualColoredLineSegment()
    l.setLine(0,0,300,300)
    s.addItem(l)

    v.show()
    v.move(QCursor.pos())
    sys.exit(app.exec_())


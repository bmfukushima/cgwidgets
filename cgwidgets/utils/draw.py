from qtpy.QtCore import Qt, QRectF, QPoint
from qtpy.QtGui import QColor, QBrush, QLinearGradient, QGradient

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


if __name__ == '__main__':
    import sys
    from qtpy.QtWidgets import QApplication, QGraphicsView, QGraphicsScene
    from qtpy.QtGui import QCursor
    app = QApplication(sys.argv)
    v = QGraphicsView()
    s = QGraphicsScene()
    v.setSceneRect(0,0,200,200)
    v.setScene(s)
    g = drawColorTypeGradient(attrs.HUE, 100, 100)
    g.setFinalStop(0,300)
    s.setBackgroundBrush(QBrush(g))
    v.show()
    v.move(QCursor.pos())
    sys.exit(app.exec_())


"""
TODO:
    pretty much this entire module...
    ColorPicker2D

"""

from qtpy.QtWidgets import (QGraphicsItemGroup,)
from qtpy.QtCore import (Qt, QPoint)

from cgwidgets.utils.draw import DualColoredLineSegment


class ColorPickerItem2D(QGraphicsItemGroup):
    def __init__(self, parent=None):
        super(ColorPickerItem2D, self).__init__(parent)


class ColorPickerItem1D(QGraphicsItemGroup):
    """
    Bar picker item.  This is a 1D bar that will slide back and forth
    over the gradient to show what color is currently being selected.

    Attributes:
        direction (Qt.Direction): the direction this color picker is expected to
            move in.
                Qt.Vertical | Qt.Horizontal

    """
    def __init__(self, parent=None):
        super(ColorPickerItem1D, self).__init__(parent)

        """
        Creates the initial linear crosshair.  Note that this is hard coded to setup
        to be drawn horizontally.  You can update the direction with
        setLinearCrosshairDirection(Qt.Direction) on the
        ColorInputWidget.
        """
        # vertical line
        self.linear_topline_item = DualColoredLineSegment(width=1)
        self.linear_botline_item = DualColoredLineSegment(width=1)

        # horizontal line
        self.linear_leftline_item = DualColoredLineSegment(width=1)
        self.linear_rightline_item = DualColoredLineSegment(width=1)

        # create linear cross hair items group
        self.addToGroup(self.linear_botline_item)
        self.addToGroup(self.linear_rightline_item)
        self.addToGroup(self.linear_topline_item)
        self.addToGroup(self.linear_leftline_item)

    def getDirection(self):
        return self._direction

    def setDirection(self, direction):
        """
        Sets the direction of travel of the linear crosshair.  This will also update
        the display of the crosshair
        """
        # set direction
        self._direction = direction

        # update display
        if direction == Qt.Horizontal:
            self.linear_topline_item.setLine(-5, 0, 5, 0)
            self.linear_botline_item.setLine(-5, self.height(), 5, self.height())

            self.linear_leftline_item.setLine(-5, 0, -5, self.height())
            self.linear_rightline_item.setLine(5, 0, 5, self.height())

        elif direction == Qt.Vertical:
            self.linear_topline_item.setLine(0, -5, self.width(), -5)
            self.linear_botline_item.setLine(0, 5, self.width(), 5)

            self.linear_leftline_item.setLine(0, -5, 0, 5)
            self.linear_rightline_item.setLine(self.width(), -5, self.width(), 5)

    def setCrosshairPos(self, pos):
        """
        Places the crosshair at a specific  location in the widget.  This is generally
        used when updating color values, and passing them back to the color widget.

        This is in LOCAL space
        """
        # get crosshair direction
        #main_widget = getWidgetAncestorByName(self, "ColorInputWidget")
        direction = self.getDirection()
        # set cross hair pos
        if direction == Qt.Horizontal:
            pos = QPoint(pos.x(), 0)
            self.setPos(pos.x(), 0)
        elif direction == Qt.Vertical:
            pos = QPoint(0, pos.y())
            self.setPos(0, pos.y())

    """ SIZE """
    def updateGeometry(self, width, height):
        """
        Updates the linear crosshair based off of the new width/height provided.

        This is currently piggy backing on the direction setting
        mechanism.  As by default that will redraw the crosshair

        Args:
            width (int)
            height (int)
        """

        self.setHeight(height)
        self.setWidth(width)

        # get pos ( for scaling position )
        pos = self.scene().linear_crosshair_item.pos()
        old_width = self.width()
        old_height = self.height()
        crosshair_xpos = pos.x() / old_width
        crosshair_ypos = pos.y() / old_height

        # update linear crosshair position
        xpos = crosshair_xpos * width
        ypos = crosshair_ypos * height
        new_pos = QPoint(xpos, ypos)
        self.scene().linear_crosshair_item.setCrosshairPos(new_pos)

        # update the cross hair size
        self.setHeight(height)
        self.setWidth(width)
        self.setDirection(self.getDirection())

    def height(self):
        return self._height

    def setHeight(self, height):
        self._height = height

    def setWidth(self, width):
        self._width = width

    def width(self):
        return self._width
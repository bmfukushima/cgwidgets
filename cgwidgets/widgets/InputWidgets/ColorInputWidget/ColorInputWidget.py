"""
TODO:
    Hue adjust -->
        Shift + LMB?
    Display Value Labels
        *   Make this adjustable with the INPUT WIDGETS
                - Connect to gradients
                    will need a flag to stop recursion...
    CLOCK ( Display Label )
        * Show current values
        * background
                - semi transparent?
                - middle gray?
"""

import sys

from qtpy.QtWidgets import (
    QApplication, QStackedWidget, QLabel,
)
from qtpy.QtCore import (Qt, QPoint)
from qtpy.QtGui import (
    QColor, QCursor
)

from cgwidgets.utils import getWidgetAncestor, attrs
from cgwidgets.settings.colors import iColor, getHSVRGBAFloatFromColor
from cgwidgets.widgets.InputWidgets.ColorInputWidget import ColorGradientMainWidget, ClockDisplayWidget


class ColorInputWidget(QStackedWidget):
    """
    Displays the color swatch to the user.  This color swatch will have a cross
    hair where the user can select the color that they want to use

    Attributes:
        border_width (int): The width of the border that displays the color
            to the user
        color (QColor): The current color that is being returned
        linear_crosshair_direction (Qt.Direction): Direction that the crosshair
            will travel when doing a 1D selection (HSV/RGB)
            TODO
                setColor needs to have a userTrigger on it to do some operation...

    Widgets
        | -- color_picker (ColorGradientWidget)
                | -- BoxLayout
                        | -- QWidget
                        |       | -- QGraphicsView
                        | -- QGraphicsLabel
        | -- clock_display_widget (ClockDisplayWidget)
                TODO:
                    Add the RGBA | HSV values to the label
                    Potentially make this into a Layout?

    TODO
        *   Previous Colors Module
                Key press event
                    Toggle current index to show previous colors
    """

    def __init__(self, parent=None):
        super(ColorInputWidget, self).__init__(parent=parent)
        # setup attrs
        self._border_width = 10
        self._linear_crosshair_direction = Qt.Horizontal

        # create widgets
        self.color_picker_widget = ColorGradientMainWidget()
        self.clock_display_widget = ClockDisplayWidget()

        self.addWidget(self.clock_display_widget)
        self.addWidget(self.color_picker_widget)

        default_color = QColor()
        default_color.setRgbF(0.5, 0.5, 1.0, 1.0)
        self.setColor(default_color)

    def __name__(self):
        return "ColorInputWidget"

    """ API """
    def setRGBACrosshairPosition(self, pos):
        """
        Interface to set the cross hair position on the scene

        Args:
            pos (QPoint):
        """
        scene = self.getScene()
        scene.setRGBACrosshairPos(pos)

    def setColor(self, color):
        """
        Sets the current color of this widget to the one provided.  This will
        update the display border, as well as the crosshair position in the
        gradient widget.

        Args:
            color (QColor): color to be set to

        TODO:
            Add user trigger event here
        """
        self._color = color
        self.updateDisplayBorder()

        # get data
        widget_dict = self.color_picker_widget.color_gradient_header_widget.getWidgetDict()
        new_color_args = getHSVRGBAFloatFromColor(color)

        # update display args
        for color_arg in widget_dict:
            # get value widget
            widget = widget_dict[color_arg]

            # set new value
            value = new_color_args[color_arg]
            widget.setValue(value)

    def getColor(self):
        if not hasattr(self, '_color'):
            self._color = QColor()
        return self._color

    def setLinearCrosshairDirection(self, direction=Qt.Horizontal):
        self.getScene().linear_crosshair_item.setDirection(direction)

    def getLinearCrosshairDirection(self):
        return self.getScene().linear_crosshair_item.getDirection()

    def setDisplayLocation(self, position=attrs.SOUTH):
        """
        When manipulating in the color picker, this will set the position
        of the display labels for the user.

        Args
            position (ColorInputWidget.POSITION): the position
                for the labels to be displayed at.

        TODO:
            This only works for SOUTH at the moment... need to update gradient
            draw to fully support all directions...
        """
        self.color_picker_widget.setHeaderPosition(position)

    """ UTILS """
    def getScene(self):
        return self.color_picker_widget.color_gradient_view_widget.scene

    def updateDisplayBorder(self, color=None):
        """
        Updates the border color that is displayed to the user
        Args:
            color (QColor): color to set the border to, if no color is provided,
                this by default will use the getColor() method
        """
        # get color
        if not color:
            color = self.getColor()

        # set up style sheet
        kwargs = {
            "color" : repr(color.getRgb()),
            "border_width" : self.border_width
        }
        self.setStyleSheet(
            """
            ColorInputWidget{{
            border: {border_width} solid rgba{color}
            }}
            """.format(**kwargs)
        )

    """ PROPERTIES"""

    @property
    def border_width(self):
        return self._border_width

    @border_width.setter
    def border_width(self, border_width):
        self._border_width = border_width


""" DISPLAY LABELS"""


if __name__ == '__main__':
    app = QApplication(sys.argv)
    color_widget = ColorInputWidget()
    #color_widget.setLinearCrosshairDirection(Qt.Vertical)
    color_widget.setDisplayLocation(position=attrs.NORTH)
    color_widget.show()
    color_widget.move(QCursor.pos())
    sys.exit(app.exec_())








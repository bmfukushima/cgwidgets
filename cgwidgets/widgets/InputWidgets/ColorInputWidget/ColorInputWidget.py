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
from cgwidgets.widgets.InputWidgets.ColorInputWidget import (
    ColorGradientDelegate, ColorClockView
)


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
        | -- clock_display_widget (ColorClockDelegate)
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
        self.color_picker_widget = ColorGradientDelegate()
        self.clock_display_widget = ColorClockView()

        self.addWidget(self.clock_display_widget)
        self.addWidget(self.color_picker_widget)

        default_color = QColor()
        default_color.setRgbF(0.5, 0.5, 1.0, 1.0)
        self.setColor(default_color)
        self.setMinimumWidth(30)

    def __name__(self):
        return "ColorInputWidget"

    """ VIRTUAL FUNCTION """
    def setUserInput(self, function):
        """
        Sets the function to be run everytime this widget updates:

        Args:
            function (function) that will be run every time that this input updates
                the color.  This function should take two args
                    QWidget, QColor
                where the QWidget will be the QWidget that is defined in this input
                as the current active widget

        """
        self.__user_input_function = function

    def userInputFunction(self, widget, color):
        return self.__user_input_function(widget, color)

    def __user_input_function(self, widget, color):
        pass

    """ API """
    def setActiveWidget(self, widget):
        """
        Sets the current widget of this widget to the one provided.  This will
        update the display border, as well as the crosshair position in the
        gradient widget.

        Args:
            widget (QWidget): widget to be set to the constructor

        TODO:
            Add user trigger event here
        """
        self._widget = widget

    def getActiveWidget(self):
        if not hasattr(self, '_widget'):
            self._widget = QColor()
        return self._widget

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
        self.updateDisplay()
        # update user set function
        self.userInputFunction(self, color)

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

    def updateDisplay(self, color=None):
        """
        Updates the border color that is displayed to the user
        Args:
            color (QColor): color to set the border to, if no color is provided,
                this by default will use the getColor() method
        """
        # get color
        if not color:
            color = self.getColor()

        # Border Color
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

        # Update display
        self.clock_display_widget.setColor(color)
        self.clock_display_widget.updateDisplay()

    """ PROPERTIES"""

    @property
    def border_width(self):
        return self._border_width

    @border_width.setter
    def border_width(self, border_width):
        self._border_width = border_width


if __name__ == '__main__':
    from qtpy.QtWidgets import QWidget, QVBoxLayout

    app = QApplication(sys.argv)
    mw = QWidget()
    l = QVBoxLayout(mw)
    test_label = QLabel('lkjasdf')

    def test(widget, color):
        test_label.setText(repr(color.getRgb()))

    color_widget = ColorInputWidget()
    color_widget.setUserInput(test)
    #color_widget.setLinearCrosshairDirection(Qt.Vertical)
    color_widget.setDisplayLocation(position=attrs.NORTH)

    l.addWidget(test_label)
    l.addWidget(color_widget)

    mw.show()
    mw.move(QCursor.pos())
    sys.exit(app.exec_())









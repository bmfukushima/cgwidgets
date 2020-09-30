import sys
import math
import re

from qtpy.QtWidgets import (
    QApplication,
    QStackedWidget, QWidget, QVBoxLayout,
    QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsItemGroup,
    QGraphicsLineItem, QLabel, QBoxLayout, QFrame, QGraphicsItem,
    QSizePolicy
)
from qtpy.QtCore import (Qt, QPoint, QEvent, QSize, QRectF)
from qtpy.QtGui import (
    QColor, QLinearGradient, QGradient, QBrush, QCursor, QPen
)

from cgwidgets.utils import attrs, draw, getWidgetAncestor, checkMousePos,  getWidgetAncestorByName
from cgwidgets.utils.draw import DualColoredLineSegment
from cgwidgets.widgets.InputWidgets import FloatInputWidget
from cgwidgets.widgets.AbstractWidgets import AbstractInputGroup
from cgwidgets.settings.colors import iColor

from cgwidgets.widgets.InputWidgets.ColorInputWidget import ColorPickerItem1D


class ColorGradientMainWidget(QWidget):
    def __init__(self, parent=None):
        super(ColorGradientMainWidget, self).__init__(parent)
        # set up attrs
        self._header_position = attrs.EAST

        # create layout
        QBoxLayout(QBoxLayout.TopToBottom, self)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        # create widgets
        self.color_gradient_view_widget = ColorGradientWidget(self)
        self.color_gradient_header_widget = ColorGradientHeaderWidget(self)

        # add widgets to layout
        self.layout().addWidget(self.color_gradient_header_widget)
        self.layout().addWidget(self.color_gradient_view_widget)

        # setup style
        self.setStyleSheet("border:None")

    def setHeaderSize(self, size):
        self._header_size = size
        self.color_gradient_header_widget.setSize(size)

    def headerPosition(self):
        return self._header_position

    def setHeaderPosition(self, position):
        """
        Sets the display labels position.  Valid inputs are
        ColorInputWidget.DIRECTION
            NORTH | SOUTH | EAST | WEST

        """
        if position == attrs.NORTH:
            self.layout().setDirection(QBoxLayout.TopToBottom)
            self.color_gradient_header_widget.layout().setDirection(QBoxLayout.LeftToRight)
            self.color_gradient_header_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        elif position == attrs.SOUTH:
            self.layout().setDirection(QBoxLayout.BottomToTop)
            self.color_gradient_header_widget.layout().setDirection(QBoxLayout.LeftToRight)
            self.color_gradient_header_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        elif position == attrs.EAST:
            self.layout().setDirection(QBoxLayout.LeftToRight)
            self.color_gradient_header_widget.layout().setDirection(QBoxLayout.TopToBottom)
            self.color_gradient_header_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        elif position == attrs.WEST:
            self.layout().setDirection(QBoxLayout.RightToLeft)
            self.color_gradient_header_widget.layout().setDirection(QBoxLayout.TopToBottom)
            self.color_gradient_header_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        self._header_position = position

    def leaveEvent(self, *args, **kwargs):
        # cursor_sector_dict = checkMousePos(QCursor.pos(), self)
        # if cursor_sector_dict["INSIDE"] is False:
        color_widget = getWidgetAncestorByName(self, "ColorInputWidget")
        color_widget.setCurrentIndex(0)
        return QWidget.leaveEvent(self, *args, **kwargs)


class ColorGradientWidget(QWidget):
    """
    MainWindow
        --> Layout
            --> GraphicsView (GLWidget)
                --> GraphicsScene
    """

    def __init__(self, parent=None):
        super(ColorGradientWidget, self).__init__(parent)
        QVBoxLayout(self)

        self.scene = ColorGraphicsScene(self)
        self.view = ColorGraphicsView(self.scene)

        self.layout().addWidget(self.view)

        self.layout().setContentsMargins(0, 0, 0, 0)

    def mousePressEvent(self, *args, **kwargs):
        return QWidget.mousePressEvent(self, *args, **kwargs)


class ColorGraphicsView(QGraphicsView):
    """
    Attributes:
        previous_size (geometry) hold the previous position
            so that a resize event can recalculate the cross hair
            based off of this geometry
    """

    def __init__(self, parent=None):
        super(ColorGraphicsView, self).__init__(parent)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    """ UTILS """

    def __hideRGBACrosshair(self, hide=True):
        """
        Determines if the cross hair for the RGBA picker should be shown/hidden

        Args:
            hide (bool): if true, hides the RGBA color picker, if false, shows the
                RGBA color picker
        """
        if hide is True:
            self.scene().rgba_crosshair_item.hide()
        else:
            self.scene().rgba_crosshair_item.show()

    def __hideLinearCrosshair(self, hide=True):
        """
        Determines if the cross hair for the RGBA picker should be shown/hidden

        Args:
            hide (bool): if true, hides the RGBA color picker, if false, shows the
                RGBA color picker
        """
        if hide is True:
            self.scene().linear_crosshair_item.hide()
        else:
            self.scene().linear_crosshair_item.show()

    def __updateRGBACrosshairOnResize(self):
        """
        Updates the RGBA crosshair to the correct position.
        """

        rgba_crosshair_pos = self.scene().getRGBACrosshairPos()
        old_width = self.getPreviousSize().width()
        old_height = self.getPreviousSize().height()
        crosshair_xpos = rgba_crosshair_pos.x() / old_width
        crosshair_ypos = rgba_crosshair_pos.y() / old_height

        # get new crosshair position
        xpos = crosshair_xpos * self.geometry().width()
        ypos = crosshair_ypos * self.geometry().height()
        new_pos = QPoint(xpos, ypos)
        self.scene().updateRGBACrosshair(new_pos)
        #self.scene().linear_crosshair_item.setCrosshairPos(new_pos)

    """ EVENTS """
    def mousePressEvent(self, event, *args, **kwargs):
        """
        Attrs:
            _picking (bool): tells the widget that the user is now attempting
                to pick a value
            _in_gradient_widget (bool) tells the widget that the cursor is
                in the gradient widget
        """
        modifiers = QApplication.keyboardModifiers()
        button = event.button()
        if button in [Qt.LeftButton, Qt.RightButton, Qt.MiddleButton]:
            # move rgba

            # HSV
            self._picking = True
            self._black_select = False
            self._in_gradient_widget = True
            self._orig_pos = QCursor.pos()
            # setup default crosshair
            self.__hideRGBACrosshair(True)
            self.__hideLinearCrosshair(False)

            # RGB
            main_widget = getWidgetAncestorByName(self, "ColorInputWidget")
            color = main_widget.getColor()
            pos = QPoint(0, 0)
            if modifiers == Qt.AltModifier:
                if button == Qt.LeftButton:
                    pos = QPoint(color.redF() * self.width(), color.redF() * self.height())
                    self.scene().gradient_type = attrs.RED
                elif button == Qt.MiddleButton:
                    pos = QPoint(color.greenF() * self.width(), color.greenF() * self.height())
                    self.scene().gradient_type = attrs.GREEN
                elif button == Qt.RightButton:
                    pos = QPoint(color.blueF() * self.width(), color.blueF() * self.height())
                    self.scene().gradient_type = attrs.BLUE

            # HSV
            else:
                if button == Qt.LeftButton:
                    self.__hideRGBACrosshair(False)
                    self.__hideLinearCrosshair(True)
                    self.scene().gradient_type = attrs.RGBA
                elif button == Qt.MiddleButton:
                    pos = QPoint(color.valueF() * self.width(), color.valueF() * self.height())
                    self.scene().gradient_type = attrs.VALUE
                elif button == Qt.RightButton:
                    pos = QPoint(color.saturationF() * self.width(), color.saturationF() * self.height())
                    self.scene().gradient_type = attrs.SATURATION

            # update display label to show selected value
            color_gradient_widget = getWidgetAncestor(self, ColorGradientMainWidget)
            color_arg_widgets_dict = color_gradient_widget.color_gradient_header_widget.getWidgetDict()
            if self.scene().gradient_type != attrs.RGBA:
                color_arg_widgets_dict[self.scene().gradient_type].setSelected(True)

            # draw gradient / hide cursor
            self.scene().drawGradient()

            # set up cursor
            self.setCursor(Qt.BlankCursor)
            if pos:
                self.scene().linear_crosshair_item.setCrosshairPos(pos)
                QCursor.setPos(self.mapToGlobal(pos))

        return QGraphicsView.mousePressEvent(self, event, *args, **kwargs)

    def mouseMoveEvent(self, event, *args, **kwargs):
        """
        This move event will determine if the values should be updated
        this will need to update the hsv/rgba moves aswell
        """
        if self._picking:
            self._getColor(event)

        return QGraphicsView.mouseMoveEvent(self, event, *args, **kwargs)

    def mouseReleaseEvent(self, *args, **kwargs):
        # reset everything back to default state

        # reset gradient
        self.__hideRGBACrosshair(False)
        self.__hideLinearCrosshair(True)
        self.scene().gradient_type = attrs.RGBA
        self.scene().drawGradient()

        # reset picking attrs
        self._picking = False
        self._black_select = False

        # reset cursor
        self.unsetCursor()
        QCursor.setPos(self._orig_pos)

        # disable labels
        color_gradient_widget = getWidgetAncestor(self, ColorGradientMainWidget)
        color_arg_widgets_dict = color_gradient_widget.color_gradient_header_widget.getWidgetDict()
        for color_arg in color_arg_widgets_dict:
            color_arg_widgets_dict[color_arg].setSelected(False)

        # update RGBA cross hair pos
        main_widget = getWidgetAncestorByName(self, "ColorInputWidget")
        xpos = (main_widget.getColor().hueF() * self.width())
        ypos = math.fabs((main_widget.getColor().saturationF() * self.height()) - self.height())
        pos = QPoint(xpos, ypos)
        self.scene().updateRGBACrosshair(pos)

        return QGraphicsView.mouseReleaseEvent(self, *args, **kwargs)

    def resizeEvent(self, *args, **kwargs):
        """
        allow widget to resize with the rectangle...
        """
        # there has to be a better way to set this...

        # =======================================================================
        # resize widget
        # =======================================================================
        rect = self.geometry()
        self.scene().setSceneRect(
            rect.topLeft().x(),
            rect.topLeft().y(),
            rect.width(),
            rect.height()
        )

        # update gradient
        self.scene().drawGradient()

        # update crosshair
        # RGBA Crosshair
        self.__updateRGBACrosshairOnResize()

        # Linear crosshair
        # main_widget = getWidgetAncestorByName(self, "ColorInputWidget")
        # direction = main_widget.getLinearCrosshairDirection()
        # self.__updateLinearCrosshairOnResize(direction)
        self.scene().linear_crosshair_item.updateGeometry(self.width(), self.height())
        self.setPreviousSize(rect)
        return QGraphicsView.resizeEvent(self, *args, **kwargs)

    """ SELECTION """

    # def _checkMousePos(self, pos):
    #     """
    #     Checks the mouse position to determine its relation to the current
    #     widget.
    #
    #     Args:
    #         pos (QPoint): current cursor position in global space
    #
    #     Returns (dict) of booleans
    #         INSIDE, NORTH, SOUTH, EAST, WEST
    #         if the arg is True then that is true.  Ie if North is true, then the cursor
    #         is north of the widget.  If INSIDE is True, then all of the other
    #         args must be False, and the cursor is inside of the widget still.
    #
    #     """
    #     # setup return attrs
    #     return_dict = {
    #         "INSIDE" : True,
    #         "NORTH" : False,
    #         "EAST" : False,
    #         "SOUTH" : False,
    #         "WEST" : False
    #     }
    #
    #     # check mouse position...
    #     top_left = self.mapToGlobal(self.geometry().topLeft())
    #     top = top_left.y()
    #     left = top_left.x()
    #     right = left + self.geometry().width()
    #     bot = top + self.geometry().height()
    #
    #     # update dictionary based off of mouse position
    #     if top > pos.y():
    #         return_dict["NORTH"] = True
    #         return_dict["INSIDE"] = False
    #     if right < pos.x():
    #         return_dict["EAST"] = True
    #         return_dict["INSIDE"] = False
    #     if bot < pos.y():
    #         return_dict["SOUTH"] = True
    #         return_dict["INSIDE"] = False
    #     if left > pos.x():
    #         return_dict["WEST"] = True
    #         return_dict["INSIDE"] = False
    #
    #     return return_dict

    def _getColor(self, event):
        """
        Gets the color from the user selection and sends it to the
        setColor on the main widget ( ColorInputWidget )

        """
        # get attrs
        color_display_widget = getWidgetAncestorByName(self, "ColorInputWidget")
        selection_type = self.scene().gradient_type

        # 2D Gradient
        if selection_type == attrs.RGBA:
            # RGBA (HUE / SATURATION)
            color = self._getRGBAValue(event)
            color_display_widget.setColor(color)
            return

        # Linear Gradient
        else:
            self.scene().linear_crosshair_item.setCrosshairPos(event.pos())

            pos = event.globalPos()
            orig_color = color_display_widget.getColor()
            new_color = self._pickColor(pos)
            # TODO DUPLICATE SET COLOR VALUE FROM ARG
            """ TODO UPDATE COLOR"""
            # saturation
            if selection_type == attrs.SATURATION:
                hue = orig_color.hueF()
                sat = new_color.valueF()
                value = orig_color.valueF()

                orig_color.setHsvF(hue, sat, value)
            # value
            elif selection_type == attrs.VALUE:
                # get HSV values
                hue = orig_color.hueF()
                sat = orig_color.saturationF()
                value = new_color.valueF()
                orig_color.setHsvF(hue, sat, value)
            # red
            elif selection_type == attrs.RED:
                red = new_color.redF()
                orig_color.setRedF(red)
            # green
            elif selection_type == attrs.GREEN:
                green = new_color.greenF()
                orig_color.setGreenF(green)
            # blue
            elif selection_type == attrs.BLUE:
                blue = new_color.blueF()
                orig_color.setBlueF(blue)

            color_display_widget.setColor(orig_color)
            return

    def _getRGBAValue(self, event):
        """
        Gets the RGBA color

        Returns (QColor)
        """
        # get color
        # TODO check distance?

        # todo flickers
        """
        This either flickers, or grabs the wrong value... its like picking the less bad
        option =/

        could make the cursor black/white... and ignore?

        foreground alpha is messing up display
        """
        scene = self.scene()
        pos = event.globalPos()
        # scene.rgba_crosshair_item.hide()
        scene.updateRGBACrosshair(event.pos())
        # QApplication.processEvents()
        color = self._pickColor(pos, constrain_to_picker=False)

        # scene.update()
        # scene.rgba_crosshair_item.show()

        # update cursor display depending on if the cursor is inside of the widget or not
        cursor_sector_dict = checkMousePos(pos, self)
        is_inside = cursor_sector_dict['INSIDE']
        if not is_inside:
            if self._in_gradient_widget is True:
                self.setCursor(Qt.CrossCursor)
                self._in_gradient_widget = False
        else:
            if self._in_gradient_widget is False:
                self.setCursor(Qt.BlankCursor)
                self._in_gradient_widget = True

        # scene.rgba_crosshair_item.show()
        return color

    def _pickColor(self, pos, constrain_to_picker=True):
        """
        picks the the current color displayed on screen at
        the current location of the cursor

        Args:
            pos (QPoint): Global pos
            constrain_to_pick (bool): determines whether or not the crosshair
                should be forced to remain inside of the picker while the user
                is selecting.
        """
        # preflight check (cursor)
        # forces the cursor to remain inside of the color picker
        # TODO Removing bouncing
        """
        display is bouncing when reaching ends as it snaps back to the last
        position in space.  It also cannot get the final 0/1 values =
        """
        if constrain_to_picker is True:
            cursor_sector_dict = checkMousePos(pos, self)
            if cursor_sector_dict["INSIDE"] is False:
                top_left = self.mapToGlobal(self.pos())
                top = top_left.y()
                left = top_left.x()
                right = left + self.geometry().width()
                bottom = top + self.geometry().height()

                if cursor_sector_dict["NORTH"] is True:
                    pos.setY(top + 1)
                if cursor_sector_dict["EAST"] is True:
                    pos.setX(right - 1)
                if cursor_sector_dict["SOUTH"] is True:
                    pos.setY(bottom - 1)
                if cursor_sector_dict["WEST"] is True:
                    pos.setX(left + 1)

                QCursor.setPos(pos)

        # self.scene().rgba_crosshair_item.hide()
        # get pixel data
        desktop = QApplication.desktop().winId()
        screen = QApplication.primaryScreen()
        pixmap = screen.grabWindow(
            desktop,
            pos.x(), pos.y(),
            1, 1
        )
        img = pixmap.toImage()
        color = QColor(img.pixel(0, 0))

        # if pure black recurse
        # if color.valueF() == 0:
        # TODO
        """
        Grabbing color of picker because fails
        """
        if color.valueF() < .0001:
            self._black_select = True
            pos = QPoint(pos.x() + 1, pos.y() + 1)
            return self._pickColor(pos)

        return color

    """ PROPERTIES """

    def setPreviousSize(self, geometry):
        self.previous_size = geometry

    def getPreviousSize(self):
        if not hasattr(self, 'previous_size'):
            self.previous_size = self.geometry()
        return self.previous_size


class ColorGraphicsScene(QGraphicsScene):
    """
    The widget that is responsible for displaying the color gradient to the user
    """

    def __init__(self, parent=None):
        super(ColorGraphicsScene, self).__init__(parent)
        # setup default attrs
        self.CROSSHAIR_RADIUS = 10
        self._rgba_crosshair_pos = QPoint(0, 0)
        self._linear_crosshair_pos = QPoint(0, 0)
        self._linear_crosshair_size = 15

        # create scene
        self.setSceneRect(0, 0, 500, 500)
        self.gradient_type = attrs.RGBA
        self.drawRGBACrosshair()
        self.drawLinearCrosshair()
        self._drawRGBAForegroundItem()

    """ DRAW GRADIENTS """
    def drawGradient(self, direction=Qt.Horizontal):

        _gradient = draw.drawColorTypeGradient(self.gradient_type, self.width(), self.height())
        self.rgba_foreground.hide()
        # update gradient size
        if direction == Qt.Horizontal:
            _gradient.setFinalStop(QPoint(self.width(), 0))
        elif direction == Qt.Vertical:
            _gradient.setFinalStop(QPoint(0, self.height()))

        if self.gradient_type == attrs.RGBA:
            # TODO Update value of foreground gradient
            """
            for some reason the darker it gets the harder of a time the picker has
            and the steps become larger and larger =/
    
            something with update cross hair pos?
    
            141 setColor
            self.setRGBACrosshairPositionFromColor(color)
            """
            # get value
            main_widget = getWidgetAncestorByName(self, "ColorInputWidget")
            value = main_widget.getColor().valueF()
            self.rgba_foreground.updateSize(QRectF(0, 0, self.width(), self.height()))
            self.rgba_foreground.updateGradient(value, self.width(), self.height())

            self.rgba_foreground.show()

        self.setBackgroundBrush(QBrush(_gradient))

    """ PROPERTIES """
    @property
    def gradient_type(self):
        return self._gradient_type

    @gradient_type.setter
    def gradient_type(self, gradient_type):
        self._gradient_type = gradient_type

    """ CROSSHAIR"""

    def drawLinearCrosshair(self):
        """
        Creates the initial linear crosshair.  Note that this is hard coded to setup
        to be drawn horizontally.  You can update the direction with
        setLinearCrosshairDirection(Qt.Direction) on the
        ColorInputWidget.
        """
        self.linear_crosshair_item = ColorPickerItem1D()
        self.linear_crosshair_item.setWidth(self.width())
        self.linear_crosshair_item.setHeight(self.height())
        self.linear_crosshair_item.setDirection(Qt.Horizontal)

        # add group item
        self.addItem(self.linear_crosshair_item)

        # hide by default
        self.linear_crosshair_item.hide()

    # def getLinearCrosshairPos(self):
    #     return self._linear_crosshair_pos

    # def setLinearCrosshairPos(self, pos):
    #     """
    #     Places the crosshair at a specific  location in the widget.  This is generally
    #     used when updating color values, and passing them back to the color widget.
    #
    #     This is in LOCAL space
    #     """
    #     # get crosshair direction
    #     main_widget = getWidgetAncestorByName(self, "ColorInputWidget")
    #     direction = main_widget.getLinearCrosshairDirection()
    #
    #     # set cross hair pos
    #     if direction == Qt.Horizontal:
    #         pos = QPoint(pos.x(), 0)
    #         self.linear_crosshair_item.setPos(pos.x(), 0)
    #     elif direction == Qt.Vertical:
    #         pos = QPoint(0, pos.y())
    #         self.linear_crosshair_item.setPos(0, pos.y())
    #
    #     # update pos attr
    #     self._linear_crosshair_pos = pos

    # def setLinearCrosshairDirection(self, direction):
    #     """
    #     Sets the direction of travel of the linear crosshair.  This will also update
    #     the display of the crosshair
    #     """
    #     # set direction
    #     self._linear_crosshair_direction = direction
    #     # self._linear_crosshair_size
    #
    #     # update display
    #     if direction == Qt.Horizontal:
    #         self.linear_topline_item.setLine(-5, 0, 5, 0)
    #         self.linear_botline_item.setLine(-5, self.height(), 5, self.height())
    #
    #         self.linear_leftline_item.setLine(-5, 0, -5, self.height())
    #         self.linear_rightline_item.setLine(5, 0, 5, self.height())
    #
    #     elif direction == Qt.Vertical:
    #         self.linear_topline_item.setLine(0, -5, self.width(), -5)
    #         self.linear_botline_item.setLine(0, 5, self.width(), 5)
    #
    #         self.linear_leftline_item.setLine(0, -5, 0, 5)
    #         self.linear_rightline_item.setLine(self.width(), -5, self.width(), 5)

    # def getLinearCrosshairDirection(self):
    #     return self._linear_crosshair_direction

    """ RGBA """

    def drawRGBACrosshair(self):
        """
        rgba_topline_item
        rgba_botline_item
        rgba_leftline_item
        rgba_rightline_item:
        rgba_crosshair_item_circle: center portion of crosshair

        """
        # vertical line
        self.rgba_topline_item = DualColoredLineSegment()
        self.rgba_topline_item.setLine(0, 0, 0, self.height())
        self.rgba_botline_item = DualColoredLineSegment()
        self.rgba_botline_item.setLine(0, 0, 0, self.height())

        # horizontal line
        self.rgba_leftline_item = DualColoredLineSegment()
        self.rgba_leftline_item.setLine(0, 0, self.width(), 0)
        self.rgba_rightline_item = DualColoredLineSegment()
        self.rgba_rightline_item.setLine(0, 0, self.width(), 0)

        # crosshair circle
        self.rgba_crosshair_item_circle = QGraphicsEllipseItem()

        self.rgba_crosshair_item_circle.setRect(
            -(self.CROSSHAIR_RADIUS * 0.5),
            -(self.CROSSHAIR_RADIUS * 0.5),
            self.CROSSHAIR_RADIUS,
            self.CROSSHAIR_RADIUS
        )

        # add items
        self.rgba_crosshair_item = QGraphicsItemGroup()

        self.rgba_crosshair_item.addToGroup(self.rgba_crosshair_item_circle)
        self.rgba_crosshair_item.addToGroup(self.rgba_topline_item)
        self.rgba_crosshair_item.addToGroup(self.rgba_botline_item)
        self.rgba_crosshair_item.addToGroup(self.rgba_leftline_item)
        self.rgba_crosshair_item.addToGroup(self.rgba_rightline_item)

        self.addItem(self.rgba_crosshair_item)

    def getRGBACrosshairPos(self):
        return self._rgba_crosshair_pos

    def setRGBACrosshairPos(self, pos):
        """ This is in LOCAL space """
        self._rgba_crosshair_pos = pos

    def updateRGBACrosshair(self, pos):
        """
        Places the crosshair at a specific  location in the widget.  This is generally
        used when updating color values, and passing them back to the color widget.
        """
        crosshair_radius = self.CROSSHAIR_RADIUS * 0.5
        xpos = pos.x()
        ypos = pos.y()

        # update items positions
        self.rgba_crosshair_item_circle.setPos(pos)
        self.rgba_topline_item.setLine(xpos, 0, xpos, ypos - crosshair_radius)
        self.rgba_botline_item.setLine(xpos, ypos + crosshair_radius, xpos, self.height())
        self.rgba_leftline_item.setLine(0, ypos, xpos - crosshair_radius, ypos)
        self.rgba_rightline_item.setLine(xpos + crosshair_radius, ypos, self.width(), ypos)

        self.setRGBACrosshairPos(pos)

    def _drawRGBAForegroundItem(self):
        """
        Creates the RGBA Foreground item.  This item is just one big rectangle
        that spans the entire scene with a 1D gradient in it to compensate for the
        Saturation portion of the RGBA gradient.
        """
        self.rgba_foreground = RGBAForegroundGradient(self.width(), self.height())
        self.addItem(self.rgba_foreground)
        self.rgba_foreground.setZValue(-10)


class RGBAForegroundGradient(QGraphicsItem):
    """
    Custom graphics item that has a gradient as a background.

    Items fill is determined by their paint method
    """

    def __init__(self, width, height):
        super(RGBAForegroundGradient, self).__init__()
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self._rectangle = QRectF(0, 0, width, height)

        self._brush = QBrush(Qt.black)

        self._gradient = draw.create1DGradient(
            100,
            100,
            direction=Qt.Vertical,
            color1=(0, 0, 0, 0),
            color2=(1, 1, 1, 1),
        )
        self.setGradient(self._gradient)

    def setBrush(self, brush):
        self._brush = brush
        self.update()

    def boundingRect(self):
        """
        method to set the actual bounding rectangle of the item
        """
        return self._rectangle

    """ PROPERTIES """

    def updateGradient(self, value, width, height):
        """
        Creates a new gradient based off of new parameters.
        This normally happens during a color change, or a widget resize event.
        width (int) :
        height (int) :
        value (float) : 0-1 float value
        """
        _gradient = draw.create1DGradient(
            width,
            height,
            direction=Qt.Vertical,
            color1=(0, 0, 0, 0),
            color2=(value, value, value, 1),
        )
        self.setGradient(_gradient)

    def getGradient(self):
        return self._gradient

    def setGradient(self, gradient):
        self._gradient = gradient

    def updateSize(self, rect):
        self._rectangle = rect

    def paint(self, painter=None, style=None, widget=None):
        painter.fillRect(self._rectangle, self.getGradient())


class ColorGradientHeaderWidget(QFrame):
    """
    Widget that will contain all of the display values for the user.

    Args:
        direction (QBoxLayout.Direction): direction that this widget should be
            set up in.  LeftToRight | RightToLeft | TopToBottom | BottomToTop

    Attributes:
        widget_dict (dict): of DisplayLabels whose keys will be the title
            of the widget.  These will correspond with the
            ColorGraphicsScene.TYPE.  However, there will be no option
            for RGBA / rgba.  So don't use that...
        size (int): the default size of the header

    Widgets
        | -- QBoxLayout
                | -* ColorGradientHeaderWidgetItem

    """

    def __init__(self, parent=None, direction=QBoxLayout.LeftToRight):
        super(ColorGradientHeaderWidget, self).__init__(parent)
        # setup default attrs
        self._size = 25
        self._widget_dict = {}

        # create widgets
        QBoxLayout(direction, self)
        for title in ['hue', 'saturation', 'value']:
            label = ColorGradientHeaderWidgetItem(self, title=title)
            label.setRange(True, 0, 1)
            self.layout().addWidget(label)
            self._widget_dict[title] = label

        for title in ['red', 'green', 'blue']:
            label = ColorGradientHeaderWidgetItem(self, title=title)
            label.setAllowNegative(False)
            self.layout().addWidget(label)
            self._widget_dict[title] = label

        # setup display
        self.updateStyleSheet()

    """ SETUP DEFAULT SIZE"""

    def getSize(self):
        return self._size

    def setSize(self, size):
        self._size = size

    def sizeHint(self):
        return QSize(self.getSize(), self.getSize())

    def setLayoutDirection(self, direction):
        self.layout().setDirection(direction)

    def getWidgetDict(self):
        return self._widget_dict

    def updateStyleSheet(self):

        self.setStyleSheet("""
        background-color: rgba{rgba_gray_1}

        """.format(**iColor.style_sheet_args))


class ColorGradientHeaderWidgetItem(AbstractInputGroup):
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
        # setup attrs
        self._value = value
        self._is_selected = False

        # setup GUI
        self.value_widget = FloatInputWidget()
        self.value_widget.setUseLadder(True, value_list=[0.0001, 0.001, 0.01, 0.1])
        self.value_widget.setAlignment(Qt.AlignLeft)
        self.insertWidget(1, self.value_widget)

        self.setStyleSheet("background-color: rgba{rgba_gray_1}".format(**iColor.style_sheet_args))
        self.setFixedWidth(125)
        self.setFixedHeight(100)

    # def setValue(self, value):
    #     self.setText(str(value))

    """ PROPERTIES """

    def setValue(self, value):
        self._value = value
        self.value_widget.setText(str(value))
        self.value_widget.setCursorPosition(0)

    def getValue(self):
        return self._value

    def setRange(self, enable, range_min, range_max):
        """
        Sets the range of the user input
        """
        self.value_widget.setRange(enable, range_min, range_max)

    def setAllowNegative(self, enabled):
        """
        Determines if the input will be allowed to go into negative numbers or
        not
        """
        self.value_widget.setAllowNegative(enabled)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    color_widget = ColorGradientMainWidget()
    #color_widget.setLinearCrosshairDirection(Qt.Vertical)
    #color_widget.setDisplayLocation(position=attrs.NORTH)
    color_widget.show()
    color_widget.move(QCursor.pos())
    sys.exit(app.exec_())


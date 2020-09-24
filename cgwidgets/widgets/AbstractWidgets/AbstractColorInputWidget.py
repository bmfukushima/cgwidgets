"""
KATANA BUGS:
    - Drag outside...
        - Hitbox is not correct, skewed by what appears to be the
            border-width to the topleft
IDEA:
    Put ring of default colors around the color widget for quick color selection

#-------------------------------------------------------------------------- Bugs

ColorValueInputWidget --> Set Color
    Disabling style sheets for now...
    as they were overriding the delegate...
    will need to rethink this...
"""

import sys
import math
import re

# from qtpy.QtWidgets import *
# from qtpy.QtCore import *
# from qtpy.QtGui import *

from qtpy.QtWidgets import (
    QApplication,
    QStackedWidget, QStackedLayout, QVBoxLayout, QWidget,
    QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsItemGroup,
    QGraphicsLineItem, QLabel
)
from qtpy.QtCore import (Qt, QPoint, QPointF)
from qtpy.QtGui import (
    QColor, QLinearGradient, QGradient, QBrush
)

from cgwidgets.utils import installLadderDelegate, getWidgetAncestor
from cgwidgets.widgets import FloatInputWidget
from cgwidgets.settings.colors import iColor


class AbstractColorGradientMainWidget(QStackedWidget):
    """
    Displays the color swatch to the user.  This color swatch will have a cross
    hair where the user can select the color that they want to use

    Widgets
        | -- color_picker (ColorGradientWidget)
        | -- display_color_widget (ColorDisplayLabel)
    """
    def __init__(self, parent=None):
        super(AbstractColorGradientMainWidget, self).__init__(parent=parent)
        # setup attrs
        self._border_width = 10

        # create widgets
        self.color_picker_widget = ColorGradientWidget()
        self.display_color_widget = ColorDisplayLabel()

        self.addWidget(self.display_color_widget)
        self.addWidget(self.color_picker_widget)

        self.setColor(QColor(128,128,255))

    """ API """
    def setRGBACrosshairPosition(self, pos):
        """
        Interface to set the cross hair position on the scene

        Args:
            pos (QPoint):
        """
        scene = self.getScene()
        scene.setRGBACrosshairPos(pos)

    def setRGBACrosshairPositionFromColor(self, color):
        """
        Sets the crosshair position to color provided.

        color (QColor):
            color to search for in the crosshair position
        """
        scene = self.getScene()
        xpos = (color.hueF() * scene.width())
        ypos = math.fabs((color.valueF() * scene.height()) - scene.height())

        pos = QPoint(xpos, ypos)
        self.setRGBACrosshairPosition(pos)

    def setColor(self, color):
        """
        Sets the current color of this widget to the one provided.  This will
        update the display border, as well as the crosshair position in the
        gradient widget.
        Args:
            color (QColor): color to be set to
        """
        self._color = color
        self.updateDisplayBorder()
        self.setRGBACrosshairPositionFromColor(color)
        # self.setRGBACrosshairPosition()

    def getColor(self):
        if not hasattr(self, '_color'):
            self._color = QColor()
        return self._color

    """ UTILS """
    def getScene(self):
        return self.color_picker_widget.scene

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
            AbstractColorGradientMainWidget{{
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


class ColorGradientWidget(QWidget):
    """
    MainWindow
        --> Layout
            --> GraphicsView (GLWidget)
                --> GraphicsScene
    """
    def __init__(self, parent=None):
        super(ColorGradientWidget, self).__init__(parent)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.scene = ColorGraphicsScene(self)
        self.view = ColorGraphicsView(self.scene)

        layout.addWidget(self.view)

        self.setStyleSheet("border:None")

    def mousePressEvent(self, *args, **kwargs):
        return QWidget.mousePressEvent(self, *args, **kwargs)

    def leaveEvent(self, *args, **kwargs):
        color_widget = getWidgetAncestor(self, AbstractColorGradientMainWidget)
        color_widget.setCurrentIndex(0)
        return QWidget.leaveEvent(self, *args, **kwargs)


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
            self.scene().rgba_crosshair.hide()
        else:
            self.scene().rgba_crosshair.show()

    def __updateRGBACrosshairOnResize(self):
        """
        Updates the RGBA crosshair to the correct position.
        """
        crosshair_pos = self.scene().getRGBACrosshairPos()
        old_width = self.getPreviousSize().width()
        old_height = self.getPreviousSize().height()
        crosshair_xpos = crosshair_pos.x() / old_width
        crosshair_ypos = crosshair_pos.y() / old_height

        # get new crosshair position
        xpos = crosshair_xpos * self.geometry().width()
        ypos = crosshair_ypos * self.geometry().height()
        new_pos = QPoint(xpos, ypos)
        self.scene().updateRGBACrosshair(new_pos)

    """ EVENTS """
    def mousePressEvent(self, *args, **kwargs):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.AltModifier:
            self.__hideRGBACrosshair(True)

        else:
            self._picking = True
            self._in_color_widget = True

        self.setCursor(Qt.BlankCursor)

        return QGraphicsView.mousePressEvent(self, *args, **kwargs)

    def mouseMoveEvent(self, event, *args, **kwargs):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.AltModifier:
            return

        # TODO Setup value getters/setters
        """
        This move event will determine if the values should be updated
        this will need to update the hsv/rgba moves aswell
        """
        if self._picking:
            if self.scene().gradient_type == ColorGraphicsScene.RGBA:
                self._getRGBAValue(event)

        return QGraphicsView.mouseMoveEvent(self, event, *args, **kwargs)

    def mouseReleaseEvent(self, *args, **kwargs):
        # reset everything back to default state
        self.__hideRGBACrosshair(False)
        self._picking = False
        self.unsetCursor()
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

        # update cross
        self.scene().drawGradient()
        if self.scene().gradient_type == ColorGraphicsScene.RGBA:
            self.__updateRGBACrosshairOnResize()

        self.setPreviousSize(rect)
        return QGraphicsView.resizeEvent(self, *args, **kwargs)

    """ SELECTION """
    def _getRGBAValue(self, event):
        # get color
        scene = self.scene()
        pos = event.globalPos()
        self._pickColor(pos)
        scene.updateRGBACrosshair(event.pos())

        # check mouse position...
        top_left = self.mapToGlobal(self.pos())
        top = top_left.y()
        left = top_left.x()
        right = left + self.geometry().width()
        bot = top + self.geometry().height()
        if pos.y() < top or pos.y() > bot or pos.x() < left or pos.x() > right:
            if self._in_color_widget == True:
                self.setCursor(Qt.CrossCursor)
                self._in_color_widget = False
        else:
            if self._in_color_widget == False:
                self.setCursor(Qt.BlankCursor)
                self._in_color_widget = True

    def _pickColor(self, pos):
        """
        picks the the current color displayed on screen at
        the current location of the cursor
        """
        desktop = QApplication.desktop().winId()
        screen = QApplication.primaryScreen()
        pixmap = screen.grabWindow(
            desktop,
            pos.x(), pos.y(),
            1, 1
        )
        img = pixmap.toImage()
        color = QColor(img.pixel(0, 0))

        # might want to check here to make sure it's not grabbing black?
        color_display_widget = getWidgetAncestor(self.scene(), AbstractColorGradientMainWidget)
        color_display_widget.setColor(color)

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

    RED = 'red'
    GREEN = 'green'
    BLUE = 'blue'
    ALPHA = 'alpha'
    HUE = 'hue'
    SATURATION = 'saturation'
    VALUE = 'value'
    RGBA = 'rgba'
    def __init__(self, parent=None):
        super(ColorGraphicsScene, self).__init__(parent)
        # setup default attrs
        self.CROSSHAIR_RADIUS = 10
        self._crosshair_pos = QPoint(0, 0)

        # create scene
        self.setSceneRect(0, 0, 500, 500)
        self.gradient_type = ColorGraphicsScene.RGBA
        self.drawRGBACrosshair()

    """ UTILS """
    def drawRGBACrosshair(self):
        # vertical line

        self.vlinetop_item = LineSegment()
        self.vlinetop_item.setLine(0, 0, 0, self.height())
        self.vlinebot_item = LineSegment()
        self.vlinebot_item.setLine(0, 0, 0, self.height())

        # horizontal line
        self.hlinetop_item = LineSegment()
        self.hlinetop_item.setLine(0, 0, self.width(), 0)
        self.hlinebot_item = LineSegment()
        self.hlinebot_item.setLine(0, 0, self.width(), 0)

        # crosshair circle
        self.crosshair_circle = QGraphicsEllipseItem()
        self.crosshair_circle.setRect(
            -(self.CROSSHAIR_RADIUS * 0.5),
            -(self.CROSSHAIR_RADIUS * 0.5),
            self.CROSSHAIR_RADIUS,
            self.CROSSHAIR_RADIUS
        )

        # add items
        self.rgba_crosshair = QGraphicsItemGroup()

        self.rgba_crosshair.addToGroup(self.crosshair_circle)
        self.rgba_crosshair.addToGroup(self.vlinetop_item)
        self.rgba_crosshair.addToGroup(self.vlinebot_item)
        self.rgba_crosshair.addToGroup(self.hlinetop_item)
        self.rgba_crosshair.addToGroup(self.hlinebot_item)

        self.addItem(self.rgba_crosshair)

    """ DRAW GRADIENTS """
    def create1DGradient(
        self,
        direction=Qt.Horizontal,
        color1=QColor(0, 0, 0, 255),
        color2=QColor(255, 255, 255, 255)
    ):
        """
        Creates 1D Linear gradient to be displayed to the user.

        Args:
            direction (Qt.Direction): The direction the gradient should go
            color1 (QColor): The first color in the gradient, the default value is black.
            color2 (QColor): The second color in the gradient, the default value is white.

        Returns (QBrush)
        """
        if direction == Qt.Horizontal:
            gradient = QLinearGradient(0, 0, self.width(), 0)
        elif direction == Qt.Vertical:
            gradient = QLinearGradient(0, 0, 0, self.height())

        gradient.setSpread(QGradient.RepeatSpread)
        gradient.setColorAt(0, color1)
        gradient.setColorAt(1, color2)
        gradient_brush = QBrush(gradient)
        return gradient_brush

    def drawGradient(self):
        """
        Primary drawing function of the gradient.
        This wil look at the property "gradient_type" and set the
        gradient according to that.
        """
        if self.gradient_type == ColorGraphicsScene.RED:
            background_gradient = self.create1DGradient(color2=QColor(255, 0, 0, 255))
        elif self.gradient_type == ColorGraphicsScene.GREEN:
            background_gradient = self.create1DGradient(color2=QColor(0, 255, 0, 255))
        elif self.gradient_type == ColorGraphicsScene.BLUE:
            background_gradient = self.create1DGradient(color2=QColor(0, 0, 255, 255))
        elif self.gradient_type == ColorGraphicsScene.ALPHA:
            background_gradient = self.create1DGradient()
        elif self.gradient_type == ColorGraphicsScene.HUE:
            pass
        elif self.gradient_type == ColorGraphicsScene.SATURATION:
            pass
        elif self.gradient_type == ColorGraphicsScene.VALUE:
            pass
        elif self.gradient_type == ColorGraphicsScene.RGBA:
            background_gradient = self._drawRGBAGradient()
            # black_gradient = QLinearGradient(0, 0, 0, self.height())
            # black_gradient.setSpread(QGradient.RepeatSpread)
            # black_gradient.setColorAt(0, QColor(0, 0, 0, 0))
            # black_gradient.setColorAt(1, QColor(value, value, value, 255))
            foreground_gradient = self.create1DGradient(
                direction=Qt.Vertical,
                color1=QColor(0, 0, 0, 0),
                color2=QColor(255, 255, 255, 255),
            )
            self.setForegroundBrush(foreground_gradient)

        self.setBackgroundBrush(background_gradient)

    def _drawRGBAGradient(self):
        """
        draws the background color square for the main widget
        """

        # get Value from main widget
        value = 255
        sat = 255

        color_gradient = QLinearGradient(0, 0, self.width(), 0)

        num_colors = 6
        color_gradient.setSpread(QGradient.RepeatSpread)
        for x in range(num_colors):
            pos = (1 / num_colors) * (x)
            color = QColor()
            color.setHsv(x * (360/num_colors), sat, value)
            color_gradient.setColorAt(pos, color)
        # set red to end
        color = QColor()
        color.setHsv(0, sat, value)
        color_gradient.setColorAt(1, color)

        # black_gradient = QLinearGradient(0, 0, 0, self.height())
        # black_gradient.setSpread(QGradient.RepeatSpread)
        # black_gradient.setColorAt(0, QColor(0, 0, 0, 0))
        # black_gradient.setColorAt(1, QColor(value, value, value, 255))

        color_gradient_brush = QBrush(color_gradient)
        #black_gradient_brush = QBrush(black_gradient)
        return color_gradient_brush
        self.setBackgroundBrush(color_gradient_brush)
        self.setForegroundBrush(black_gradient_brush)

    """ PROPERTIES """
    @property
    def gradient_type(self):
        return self._gradient_type

    @gradient_type.setter
    def gradient_type(self, gradient_type):
        self._gradient_type = gradient_type


    """ CROSSHAIR"""
    def getRGBACrosshairPos(self):
        return self._crosshair_pos

    def setRGBACrosshairPos(self, pos):
        self._crosshair_pos = pos

    def updateRGBACrosshair(self, pos):
        """
        Places the crosshair at a specific  location in the widget.  This is generally
        used when updating color values, and passing them back to the color widget.
        """
        crosshair_radius = self.CROSSHAIR_RADIUS * 0.5
        xpos = pos.x()
        ypos = pos.y()

        # update items positions
        self.crosshair_circle.setPos(pos)
        self.vlinetop_item.setLine(xpos, 0, xpos, ypos - crosshair_radius)
        self.vlinebot_item.setLine(xpos, ypos + crosshair_radius, xpos, self.height())
        self.hlinetop_item.setLine(0, ypos, xpos - crosshair_radius, ypos)
        self.hlinebot_item.setLine(xpos + crosshair_radius, ypos, self.width(), ypos)

        self.setRGBACrosshairPos(pos)


class LineSegment(QGraphicsLineItem):
    """
    Abstract line segment to be used fro the crosshair
    """
    def __init__(self, parent=None):
        super(LineSegment, self).__init__(parent)
        pen = self.pen()
        pen.setWidth(1)
        self.setPen(pen)


class ColorDisplayLabel(QLabel):
    #  ==========================================================================
    # Display color swatch to the user
    #  ==========================================================================
    def __init__(self, parent=None):
        super(ColorDisplayLabel, self).__init__(parent=parent)
        updated_args = {'rgba_background': iColor['rgba_gray_2']}
        style_sheet = iColor.createDefaultStyleSheet(self, updated_args)

        self.setStyleSheet(style_sheet)

    def enterEvent(self, *args, **kwargs):
        color_display_widget = getWidgetAncestor(self, AbstractColorGradientMainWidget)
        color_display_widget.setCurrentIndex(1)
        return QLabel.enterEvent(self, *args, **kwargs)


# class SETTINGS(object):
#     GRID_SIZE = 50
#     GRID_BORDER_WIDTH = 3
#     HUD_BORDER_WIDTH = 1
#     HUD_BORDER_OFFSET = 3
#     PADDING = 3
#     ALPHA = '48'
#     CREATE_LABEL_WIDTH = 150
#     SELECTION_WIDTH = 15
#
#     # ===============================================================================
#     # COLORS
#     # ===============================================================================
#     #Darkest (letters)
#     DARK_GREEN_ORIG = '.01600 .16827 .03560'
#
#     DARK_GREEN_RGB = QColor()
#     #DARK_GREEN_RGB.setRgbF(.016 * 255, .16827 * 255, .03560 * 255)
#     DARK_GREEN_RGB.setRgb(18, 86, 36)
#
#     DARK_GREEN_STRI = '16, 86, 36'
#     DARK_GREEN_STRRGBA = '16, 86, 36, 255'
#     #DARK_GREEN_STRI = '8, 86, 18'
#
#     DARK_GREEN_HSV = QColor()
#     DARK_GREEN_HSV.setHsvF(.5, .9, .17)
#
#     MID_GREEN_STRRGBA = '64, 128, 64, 255'
#
#     LIGHT_GREEN_RGB = QColor()
#     #LIGHT_GREEN_RGB.setRgb(10.08525, 95.9463, 20.9814)
#     LIGHT_GREEN_RGB.setRgb(90, 180, 90)
#     LIGHT_GREEN_STRRGBA = '90, 180, 90, 255'
#
#     DARK_RED_RGB = QColor()
#     DARK_RED_RGB.setRgb(86, 18, 36)
#
#     LOCAL_YELLOW_STRRGBA = '240, 200, 0, 255'
#     DARK_YELLOW_STRRGBA = '112, 112, 0, 255'
#
#     DARK_GRAY_STRRGBA = '64, 64, 64, 255'
#
#     FULL_TRANSPARENT_STRRGBA = '0, 0, 0, 0'
#     DARK_TRANSPARENT_STRRGBA ='0, 0, 0, 48'
#     LIGHT_TRANSPARENT_STRRGBA ='255, 255, 255, 12'
#
#     # ===============================================================================
#     # STYLE SHEETS
#     # ===============================================================================
#     BUTTON_SELECTED = \
#         'border-width: 2px; \
#         border-color: rgba(%s) ; \
#         border-style: solid' \
#         % LOCAL_YELLOW_STRRGBA
#
#     BUTTON_DEFAULT = \
#         'border-width: 1px; \
#         border-color: rgba(%s) ; \
#         border-style: solid' \
#         % DARK_GRAY_STRRGBA
#
#     TOOLTIP = 'QToolTip{ \
#                         background-color: rgb(%s); \
#                         color: rgb(%s); \
#                         border: black solid 1px\
#                     } \
#                     ' % (DARK_GRAY_STRRGBA,             # Tool Tip BG
#                         LOCAL_YELLOW_STRRGBA)      # Tool Tip Color
#
#     # GROUP_BOX_HUD_WIDGET
#     GROUP_BOX_HUD_WIDGET = \
#         'QGroupBox{\
#             background-color: rgba(0,0,0,%s);\
#             border-width: %spx; \
#             border-radius: %spx;\
#             border-style: solid; \
#             border-color: rgba(%s); \
#         } \
#         ' % (
#             ALPHA,
#             GRID_BORDER_WIDTH,                               # border-width
#             PADDING * 2,                           # border-radius
#             DARK_GREEN_STRRGBA,        # border color
#         )
#     """
#     QListView::item:selected:active {
#         background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
#                                     stop: 0 #6a6ea9, stop: 1 #888dd9);
#     }
#     """
#     # FLOATING WIDGET
#     FLOATING_LISTWIDGET_SS = \
#         'QListView::item:hover{\
#         color: rgba(%s);\
#         }\
#         QListView{\
#         background-color: rgba(%s); \
#         selection-color: rgba(%s);\
#         selection-background-color: rgba(%s);\
#         } ' % (
#             LIGHT_GREEN_STRRGBA,
#             FULL_TRANSPARENT_STRRGBA,
#             LOCAL_YELLOW_STRRGBA,
#             FULL_TRANSPARENT_STRRGBA,
#         )
#     FLOATING_LISTWIDGETHUD_SS = \
#         'QListView::item:hover{\
#         color: rgba(%s);\
#         }\
#         QListView{\
#         background-color: rgba(%s); \
#         selection-color: rgba(%s);\
#         selection-background-color: rgba(%s);\
#         } ' % (
#             LIGHT_GREEN_STRRGBA,
#             DARK_TRANSPARENT_STRRGBA,
#             LOCAL_YELLOW_STRRGBA,
#             FULL_TRANSPARENT_STRRGBA,
#         )
#
#     FLOATING_WIDGET_HUD_SS =\
#         'QWidget.UserHUD{background-color: rgba(0,0,0,0); \
#         border-width: %spx; \
#         border-style: solid; \
#         border-color: rgba(%s);} \
#         ' % (
#             HUD_BORDER_WIDTH,
#             DARK_GREEN_STRRGBA
#         )
#     # ===============================================================================
#     # GROUP BOX MASTER STYLE SHEET
#     # ===============================================================================
#
#     # REGEX
#     background_color = r"background-color: .*?(?=\))"
#     border_radius = r"border-width: .*?(?=p)"
#     border_color = r"border-color: rgba\(.*?(?=\))"
#     color = r"color: rgba\(.*?(?=\))"
#
#     # MASTER
#     GROUP_BOX_SS = \
#         'QGroupBox::title{\
#         subcontrol-origin: margin;\
#         subcontrol-position: top center; \
#         padding: -%spx %spx; \
#         } \
#         QGroupBox{\
#             background-color: rgba(0,0,0,%s);\
#             border-width: %spx; \
#             border-radius: %spx;\
#             border-style: solid; \
#             border-color: rgba(%s); \
#             margin-top: 1ex;\
#             margin-bottom: %s;\
#             margin-left: %s;\
#             margin-right: %s;\
#         } \
#         %s \
#         ' % (
#             PADDING,                               # padding text height
#             PADDING * 2,                       # padding offset
#             ALPHA,
#             1,                               # border-width
#             PADDING * 2,                           # border-radius
#             MID_GREEN_STRRGBA,        # border color
#             PADDING,                                   # margin-bottom
#             PADDING,                                   # margin-left
#             PADDING,                                   # margin-right
#             TOOLTIP
#         )
#
#
#     # GROUP_BOX_SS_TRANSPARENT
#     GROUP_BOX_SS_TRANSPARENT = re.sub(
#         background_color,
#         'background-color: rgba(0,0,0,0',
#         GROUP_BOX_SS
#     )
#
#     # GROUP_BOX_USER_NODE
#     GROUP_BOX_USER_NODE = str(GROUP_BOX_SS)
#
#
#     # GROUP_BOX_USER_SELECTED_NODE
#     GROUP_BOX_USER_NODE_SELECTED = re.sub(
#         background_color,
#         'background-color: rgba(%s,%s' % (DARK_GREEN_STRI, ALPHA),
#         GROUP_BOX_SS,
#         1
#     )
#     GROUP_BOX_USER_NODE_SELECTED = re.sub(
#         border_color,
#         'border-color: rgba(%s' % (LOCAL_YELLOW_STRRGBA),
#         GROUP_BOX_USER_NODE_SELECTED,
#         1
#     )
#
#     # GROUP_BOX_EDIT_PARAMS
#     GROUP_BOX_EDIT_PARAMS = re.sub(
#         border_radius,
#         'border-width: 2',
#         GROUP_BOX_SS
#     )
#     GROUP_BOX_EDIT_PARAMS = re.sub(
#         border_color,
#         'border-color: rgba(%s' % (DARK_GREEN_STRRGBA),
#         GROUP_BOX_EDIT_PARAMS
#     )
#
#     GROUP_BOX_HUDDISPLAY = \
#         'QGroupBox::title{\
#         subcontrol-origin: margin;\
#         subcontrol-position: top center; \
#         padding: -%spx %spx; \
#         } \
#         QGroupBox{\
#             background-color: rgba(%s);\
#             border-width: %spx; \
#             border-radius: %spx;\
#             border-style: solid; \
#             border-color: rgba(%s); \
#             margin-top: 1ex;\
#         } \
#         ' % (
#             PADDING,
#             PADDING * 2,
#             FULL_TRANSPARENT_STRRGBA,
#             1,                               # border-width
#             PADDING * 2,                           # border-radius
#             MID_GREEN_STRRGBA,        # border color
#     )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    color_widget = AbstractColorGradientMainWidget()
    color_widget.show()
    sys.exit(app.exec_())









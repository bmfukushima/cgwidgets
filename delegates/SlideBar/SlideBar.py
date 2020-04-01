'''
To Do...
    * Display / Screen
        Allow user to choose between, display, or widget
    * HSV
        Setup Gradient for QGraphicsView
            From Color Widget
    * Unit
        Set up Gradient (style sheet)
            From Ladder Delegate
'''
import sys

from qtpy.QtWidgets import QDesktopWidget, QApplication, QWidget
from qtpy.QtCore import Qt, QPoint


class AbstractSlideBar(QWidget):
    """
    Abstract class for all slide bars.  This will be inherited by the
    HSVSlideBar and UnitSlideBar.  The base properties of this
    widget are to create the containter for these widgets, and then
    subclass this widget and draw the visuals.

    Kwargs:
        depth (int): how wide/tall the widget should be depending
            on its orientation
        alignment (QtCore.Qt.Align): where the widget should be align
            relative to the display

    Properties:
        + public+
            depth (int): width/height of the slideBar (depends on orientation)
            alignment (Qt.Alignment): Where widget should be aligned

        - private -
            screen_width (int): width of screen
            screen_height (int): height of screen
            screen_pos (QPoint): position of display ( if using multiple displays )
            screen_geometry (QDesktopWidget.screenGeometry): geometry for
                the main display.

    This should be abstract
        SliderBar--> HueAbstractSlideBar / SatAbstractSlideBar / ValueAbstractSlideBar / Unit Slide Bar...

    """
    def __init__(
        self,
        parent=None,
        depth=50,
        alignment=Qt.AlignBottom
    ):
        super(AbstractSlideBar, self).__init__(parent)

        # set screen properties
        self._screen_geometry = QDesktopWidget().screenGeometry(-1)
        self._screen_width = self.screen_geometry.width()
        self._screen_height = self.screen_geometry.height()
        self._screen_pos = self.screen_geometry.topLeft()

        # set properties
        self.setDepth(depth)
        self.setAlignment(alignment)

        # set display flags
        self.setWindowFlags(Qt.FramelessWindowHint)

    """ API """
    def getDepth(self):
        return self._depth

    def setDepth(self, depth):
        self._depth = depth

    def getAlignment(self):
        return self._alignment

    def setAlignment(self, alignment):
        self._alignment = alignment
        self.__setWidgetPosition(alignment)

    """ PROPERTIES """
    @property
    def screen_geometry(self):
        return self._screen_geometry

    @screen_geometry.setter
    def screen_geometry(self, screen_geometry):
        self._screen_geometry = screen_geometry

    def screen_width(self):
        return self._screen_width

    @screen_width.setter
    def screen_width(self, screen_width):
        self._screen_width = screen_width

    @property
    def screen_height(self):
        return self._screen_height

    @screen_height.setter
    def screen_height(self, screen_height):
        self._screen_height = screen_height

    @property
    def screen_pos(self):
        return self._screen_pos

    @screen_pos.setter
    def screen_pos(self, screen_pos):
        self._screen_pos = screen_pos

    """ UTILS """
    def __setWidgetPosition(self, alignment):
        """
        Determines where on the monitor the widget should be located

        Args:
            Alignment (QtCore.Qt.Alignment): Determines where on the
            monitor to position the widget.
                AlignLeft
                AlignRight
                AlignTop
                AlignBottom
        """
        _accepted = [
            Qt.AlignLeft,
            Qt.AlignRight,
            Qt.AlignTop,
            Qt.AlignBottom
        ]

        if alignment in _accepted:
            if alignment == Qt.AlignLeft:
                height = self.screen_height
                width = self.getDepth()
                pos = self.screen_pos
            elif alignment == Qt.AlignRight:
                height = self.screen_height
                width = self.getDepth()
                pos_x = (
                    self.screen_pos.x()
                    + self.screen_width
                    - self.getDepth()
                )
                pos = QPoint(pos_x, self.screen_pos.y())
            elif alignment == Qt.AlignTop:
                height = self.getDepth()
                width = self.screen_width
                pos = self.screen_pos
            elif alignment == Qt.AlignBottom:
                height = self.getDepth()
                width = self.screen_width
                pos_y = (
                    self.screen_pos.y()
                    + self.screen_height
                    - self.getDepth()
                )
                pos = QPoint(self.screen_pos.x(), pos_y)

            self.setFixedHeight(height)
            self.setFixedWidth(width)
            self.move(pos)

    def keyPressEvent(self, event, *args, **kwargs):
        if event.key() == Qt.Key_Escape:
            self.close()
        return QWidget.keyPressEvent(self, event, *args, **kwargs)


class UnitSlideBar(AbstractSlideBar):
    """
    Displays a bar on a cardinal direction relative to the monitor
    (Top, Bottom, Left Right).  This bar will have two colors,
    which will display how far a user slide has gone before the
    next tick is registered to be updated

    Kwargs:
        depth (int): how wide/tall the widget should be depending
            on its orientation
        alignment (QtCore.Qt.Align): where the widget should be align
            relative to the display

    Attributes:
        + public +
            bg_slide_color: (rgba) | ( int array ) | 0 - 255
                The bg color that is displayed to the user when the user starts
                to click/drag to slide

            fg_slide_color: (rgba) | ( int array ) | 0 - 255
                The bg color that is displayed to the user when the user starts
                to click/drag to slide
    """
    def __init__(
        self,
        parent=None,
        depth=50,
        alignment=Qt.AlignBottom
    ):
        super(UnitSlideBar, self).__init__(
            parent, alignment=alignment, depth=depth
        )

        # set slide color
        self.setBGSlideColor((18, 18, 18, 128))
        self.setFGSlideColor((32, 128, 32, 255))

    """ PROPERTIESS """
    def getBGSlideColor(self):
        return self._bg_slide_color

    def setBGSlideColor(self, bg_slide_color):
        self._bg_slide_color = bg_slide_color

    def getFGSlideColor(self):
        return self._fg_slide_color

    def setFGSlideColor(self, fg_slide_color):
        self._fg_slide_color = fg_slide_color

    """ UTILS """
    def __update(self, xpos):
        """
        Updates the color of the widget relative to how far the user
        has dragged.

        Args:
            xpos (float): what percentage the user has travelled towards
                the next tick.

        Returns:
            None
        """
        style_sheet = """
        background: qlineargradient(
            x1:{xpos1} y1:0,
            x2:{xpos2} y2:0,
            stop:0 rgba{bgcolor},
            stop:1 rgba{fgcolor}
        );
        """.format(
                xpos1=str(xpos),
                xpos2=str(xpos + 0.01),
                bgcolor=repr(self.getBGSlideColor()),
                fgcolor=repr(self.getFGSlideColor())
            )
        self.setStyleSheet(style_sheet)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = UnitSlideBar(alignment=Qt.AlignRight)
    w.show()
    sys.exit(app.exec_())
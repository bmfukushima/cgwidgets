'''

SlideDelegate --> SlideBreed -->AbstractSlideDisplay
To Do...
    * Display / Screen
        - Allow user to choose between, display, or widget

    * HSV
        - Setup Gradient for QGraphicsView
            From Color Widget

            SlideDelegate --> getBreedWidget
    * Vertical Alignment
        - Unit
            - When aligning vertically gradient still moves horizontally...and notvertically...
            - Need to reverse order depending on direction of cursor move...

    * Organize attributes...
        API is all over the place with multiple setters/getters in all of the slide delegates...
            Currently being set as a setter on the SlideDelegate

    * How to set up class Attributes/Properties?
        so that I can do a
            - SlideDelegate.Unit
            - SlideDelegate.Hue
            - SlideDelegate.Sat
            - SlideDelegate.Val

'''
import sys
import platform

from qtpy.QtWidgets import QDesktopWidget, QApplication, QWidget
from qtpy.QtCore import Qt, QPoint, QEvent

from utils import setAsTool

Unit = 0
Hue = 1
Sat = 2
Val = 3


class AbstractSlideDisplay(QWidget):
    """
    Abstract class for all slide bars.  This will be inherited by the
    HSVSlideDisplay and UnitSlideDisplay.  The base properties of this
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
        SliderBar--> HueAbstractSlideDisplay / SatAbstractSlideDisplay / ValueAbstractSlideDisplay / Unit Slide Bar...

    """
    def __init__(
        self,
        parent=None,
        depth=50,
        alignment=Qt.AlignBottom
    ):
        super(AbstractSlideDisplay, self).__init__(parent)
        # set as tool
        setAsTool(self)

        # set screen properties
        self._screen_geometry = QDesktopWidget().screenGeometry(-1)
        self._screen_width = self.screen_geometry.width()
        self._screen_height = self.screen_geometry.height()
        self._screen_pos = self.screen_geometry.topLeft()

        # set properties
        self.setDepth(depth)
        self.setAlignment(alignment)
        self.setWidgetPosition(self.getAlignment())

    """ API """
    def getDepth(self):
        return self._depth

    def setDepth(self, depth):
        self._depth = depth

    def getAlignment(self):
        return self._alignment

    def setAlignment(self, alignment):
        self._alignment = alignment

    """ PROPERTIES """
    @property
    def screen_geometry(self):
        return self._screen_geometry

    @screen_geometry.setter
    def screen_geometry(self, screen_geometry):
        self._screen_geometry = screen_geometry

    @property
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
    def setWidgetPosition(self, alignment):
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

    def update(self, *args, **kwargs):
        print('you need to reimplement this on: {}'.format(self))
        return QWidget.update(self, *args, **kwargs)

    """ EVENTS"""
    def keyPressEvent(self, event, *args, **kwargs):
        if event.key() == Qt.Key_Escape:
            self.close()
        return QWidget.keyPressEvent(self, event, *args, **kwargs)


class UnitSlideDisplay(AbstractSlideDisplay):
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
        alignment=Qt.AlignBottom,
        bg_slide_color=(18, 18, 18, 128),
        fg_slide_color=(18, 128, 18, 128),
    ):
        super(UnitSlideDisplay, self).__init__(
            parent, alignment=alignment, depth=depth
        )

        # set slide color
        self.setBGSlideColor(bg_slide_color)
        self.setFGSlideColor(fg_slide_color)
        self.update(0.0)

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
    def update(self, xpos):
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
                xpos2=str(xpos + 0.0001),
                bgcolor=repr(self.getBGSlideColor()),
                fgcolor=repr(self.getFGSlideColor())
            )
        self.setStyleSheet(style_sheet)


class SlideDelegate(QWidget):
    """
    Container that encapsulates the different types of SlideDisplays.
    This widget has two major components, the event filter, and
    the breed.

    Kwargs:
        breed (cgwidgets.delegates.SlideDisplay.breed): bit based value
            designated at the top of this file.  This value will determine
            what type of SlideDisplay is displayed to the user.  The options
            Unit, Hue, Sat, and Val.
            Note:
                All breeds will need the 'update' method to be overwritten
                and accept a float value.  The update method should update
                the display to the user to show what the current value is.
        getSliderPos (method): gets the current position of the slider,
            this is called by the slider to determine where it should
            display the current tick to the user.
            Returns:
                (float): 0-1
    """
    def __init__(
        self,
        parent=None,
        breed=0,
        getSliderPos=None
    ):
        super(SlideDelegate, self).__init__(parent)
        self.setBreed(breed)
        # set initial colors
        self.setBGSlideColor((32, 32, 32, 128))
        self.setFGSlideColor((32, 128, 32, 255))
        self.setDepth(50)
        self.setAlignment(Qt.AlignBottom)

        self.getSliderPos = getSliderPos

    """ API """
    def getBreed(self):
        return self._breed

    def setBreed(self, breed):
        self._breed = breed

    def getDepth(self):
        return self._depth

    def setDepth(self, depth):
        self._depth = depth

    def getAlignment(self):
        return self._alignment

    def setAlignment(self, alignment):
        self._alignment = alignment

    def getBGSlideColor(self):
        return self._bg_slide_color

    def setBGSlideColor(self, color):
        self._bg_slide_color = color
        '''
        if self.getBreed() == 0:
            self.getBreedWidget().setBGSlideColor(color)
        '''

    def getFGSlideColor(self):
        return self._fg_slide_color

    def setFGSlideColor(self, color):
        self._fg_slide_color = color
        '''
        if self.getBreed() == 0:
            self.getBreedWidget().setFGSlideColor(color)
        '''

    """ UTILS """
    def getBreedWidget(self):
        """
        0 = Unit
        1 = Hue
        2 = Sat
        3 = Val
        """
        breed = self.getBreed()
        if breed == 0:
            return UnitSlideDisplay(
                bg_slide_color=self.getBGSlideColor(),
                fg_slide_color=self.getFGSlideColor()
            )
        else:
            pass

    """ EVENTS """
    def eventFilter(self, obj, event, *args, **kwargs):
        if event.type() == QEvent.MouseButtonPress:
            self.slidebar = self.getBreedWidget()
            self.slidebar.setWidgetPosition(self.getAlignment())
            self.slidebar.show()

            return QWidget.eventFilter(self, obj, event, *args, **kwargs)
        elif event.type() == QEvent.MouseMove:
            try:
                slider_pos = self.getSliderPos()
                '''
                try:
                    slider_pos = self.getSliderPos()
                except:
                    slider_pos = self.getSliderPos(obj)
                '''
                self.slidebar.update(slider_pos)
            except AttributeError:
                pass
            return QWidget.eventFilter(self, obj, event, *args, **kwargs)
        elif event.type() == QEvent.MouseButtonRelease:
            try:
                self.slidebar.close()
            except AttributeError:
                pass
            return QWidget.eventFilter(self, obj, event, *args, **kwargs)
        return QWidget.eventFilter(self, obj, event, *args, **kwargs)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    class TestWidget(QWidget):
        def __init__(self, parent=None):
            super(TestWidget, self).__init__(parent)
            self.value = .75

        def testSliderPos(self):
            return self.value

    w = TestWidget()
    ef = SlideDelegate(
        parent=w,
        getSliderPos=TestWidget.testSliderPos
    )
    w.installEventFilter(ef)
    w.show()
    '''
    w = UnitSlideDisplay(alignment=Qt.AlignRight)
    w.show()
    '''
    sys.exit(app.exec_())
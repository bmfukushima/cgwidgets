'''

SlideDelegate --> SlideBreed -->AbstractSlideDisplay
To Do...
    *Invisible Slide?
        What?
#-------------------------------------------------------------------------- Bugs
    * Not filling entire space?
        - appears to be on vertical display only...
        - appears at ~roughly .15
        - almost like its adding another stop to the ramp...
    * Not travelling entire distance... sometimes...
        - aggrevated by adding a parent widget
            content margins / padding?
        - end postion value greater than 1?

#--------------------------------------------------------------------- Features
    * Layout --> Slide Widget / Value?
        - display value on top of slider?
            QGraphicsScene / Mask?
        - easier to display to right/left/top/bottom of slider...
            also better to look at...  provides a consistent place to look
            rather than a dynamic one...

    * Display / Screen
        - Allow user to choose between, display, or widget
            - currently passing _widget as an untracked attribute...
            - need to start documenting this chain...
            - instead of absolute position...
                do this with a layout? stacked widget?

    * HSV
        - Setup Gradient for QGraphicsView
            From Color Widget

            SlideDelegate --> getBreedWidget

#---------------------------------------------------------------------- Clean up
    * Organize attributes...
        API is all over the place with multiple setters/getters in all of the slide delegates...
            Currently being set as a setter on the SlideDelegate
                - bg_color
                - fg_color
                - alignment
            Currently doing an inheritance chain due to the creation process... As
            the widget is created/destroyed on demand... this way each widget
            will be more standalone, and the different display bars could potentially
            be inherited later on...
        - Also due to the fact that the inheritance wasnt passed to the abstract widget
            through the super... well aint that super...
        - clean up screen_pos attributes...

    * Document
        - _widget added...


'''
import sys
#import platform
import math

from qtpy.QtWidgets import QDesktopWidget, QApplication, QWidget#, QStackedLayout
from qtpy.QtCore import Qt, QPoint, QEvent

from cgwidgets.utils import setAsTool, getGlobalPos
#from PyQt5.QtWidgets import QVBoxLayout, QPushButton


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
        widget (QWidget): optional argument.  If entered, the display
            will show up over that widget rather than over the main display.

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
        alignment=Qt.AlignBottom,
        display_widget=None
    ):
        super(AbstractSlideDisplay, self).__init__(parent)

        setAsTool(self)

        # set screen properties
        self._screen_geometry = QDesktopWidget().screenGeometry(-1)
        self._screen_width = self.screen_geometry.width()
        self._screen_height = self.screen_geometry.height()
        self._screen_pos = self.screen_geometry.topLeft()

        # set properties
        self._display_widget = display_widget
        self.setDepth(depth)
        self.setAlignment(alignment)
        #self.setWidgetPosition(self.getAlignment(), widget=widget)

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
    def setWidgetPosition(self, alignment, widget=None):
        if widget:
            self.alignToWidget(alignment, widget)
        else:
            self.alignToDisplay(alignment)

    def alignToWidget(self, alignment, widget):
        '''
        needs to be setup incase a widget has no parent?
        '''
        _accepted = [
            Qt.AlignLeft,
            Qt.AlignRight,
            Qt.AlignTop,
            Qt.AlignBottom
        ]
        """
        parent = widget.parent()
        parent_layout = parent.layout()
        print(widget, parent.layout())
        print(widget.objectName(), parent.layout().objectName())
        
        stacked_layout = QStackedLayout()
        
        # get widget index in parent...
        # insert stacked layout into parent
        
        align_widget = QWidget()
        align_layout = QVBoxLayout(align_widget)
        align_layout.setAlignment(alignment)
        align_layout.setContentsMargins(0, 0, 0, 0)

        # stupid method beacuse I can't figure out the correct
        # way to get the index of the widget in a layout...
        child_index = -1
        print('layout count == %s'%parent_layout.count())
        for index in range(parent_layout.count()):
            print('i == %s'%index)
            child_widget = parent_layout.itemAt(index).widget()
            print(child_widget)
            if child_widget == widget:
                child_index = index
        print('child_index == =%s'%child_index)

        # add widgets to stacked layout
        #stacked_layout.addWidget(align_widget)
        button = QPushButton('test')
        stacked_layout.addWidget(button)
        stacked_layout.addWidget(widget)
        button.setFixedSize(50, 50)
        button.setStyleSheet('background-color:rgba(128,128,128,128)')
        parent_layout.insertLayout(child_index, stacked_layout)

        """
        screen_pos = getGlobalPos(widget)
        '''
        contents_margins = widget.layout().getContentsMargins()
        left_pad = contents_margins[0]
        top_pad = contents_margins[1]
        right_pad = contents_margins[2]
        bot_pad = contents_margins[3]
        '''
        if alignment in _accepted:
            if alignment == Qt.AlignLeft:
                height = widget.height()
                width = self.getDepth()
                pos = screen_pos

                # add padding
                #height += top_pad
                #screen_pos.setX(screen_pos.x() - left_pad)
                #screen_pos.setY(screen_pos.y() - top_pad)
            elif alignment == Qt.AlignRight:
                height = widget.height()
                width = self.getDepth()
                pos_x = (
                    screen_pos.x()
                    + widget.width()
                    - self.getDepth()
                )
                pos = QPoint(pos_x, screen_pos.y())
            elif alignment == Qt.AlignTop:
                height = self.getDepth()
                width = widget.width()
                pos = screen_pos
            elif alignment == Qt.AlignBottom:
                height = self.getDepth()
                width = widget.width()
                pos_y = (
                    screen_pos.y()
                    + widget.height()
                    - self.getDepth()
                )
                pos = QPoint(screen_pos.x(), pos_y)

            self.setFixedHeight(height)
            self.setFixedWidth(width)
            self.move(pos)

    def alignToDisplay(self, alignment):
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
        display_widget=None
    ):
        super(UnitSlideDisplay, self).__init__(
            parent, alignment=alignment, depth=depth
        )

        # set default attrs
        self.setBGSlideColor(bg_slide_color)
        self.setFGSlideColor(fg_slide_color)
        self.setAlignment(alignment)
        self._display_widget = display_widget
        self.update(0.0)

    """ PROPERTIES """
    def getBGSlideColor(self):
        return self._bg_slide_color

    def setBGSlideColor(self, bg_slide_color):
        self._bg_slide_color = bg_slide_color

    def getFGSlideColor(self):
        return self._fg_slide_color

    def setFGSlideColor(self, fg_slide_color):
        self._fg_slide_color = fg_slide_color

    def getAlignment(self):
        return self._alignment

    def setAlignment(self, alignment):
        self._alignment = alignment

    """ UTILS """
    def update(self, pos):
        """
        Updates the color of the widget relative to how far the user
        has dragged.

        Args:
            xpos (float): what percentage the user has travelled towards
                the next tick.

        Returns:
            None
        """

        # align horizontally
        if self.getAlignment() in [Qt.AlignBottom, Qt.AlignTop]:
            pos = pos
            style_sheet = """
            background: qlineargradient(
                x1:{pos1} y1:0,
                x2:{pos2} y2:0,
                stop:0 rgba{bgcolor},
                stop:1 rgba{fgcolor}
            );
            """.format(
                    pos1=str(pos),
                    pos2=str(pos + 0.0001),
                    bgcolor=repr(self.getBGSlideColor()),
                    fgcolor=repr(self.getFGSlideColor())
                )
        # align vertically
        elif self.getAlignment() in [Qt.AlignLeft, Qt.AlignRight]:
            pos = math.fabs(1 - pos)
            style_sheet = """
            background: qlineargradient(
                x1:0 y1:{pos1},
                x2:0 y2:{pos2},
                stop:0 rgba{fgcolor},
                stop:1 rgba{bgcolor}
            );
            """.format(
                    pos1=str(pos),
                    pos2=str(pos + 0.0001),
                    bgcolor=repr(self.getBGSlideColor()),
                    fgcolor=repr(self.getFGSlideColor())
                )
        try:
            self.setStyleSheet(style_sheet)
        except UnboundLocalError:
            # alignment not set
            pass


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

    Class Attributes:
        UNIT
        HUE
        SATURATION
        VALUE
    """
    UNIT = 0
    HUE = 1
    SATURATION = 2
    VALUE = 4

    def __init__(
        self,
        parent=None,
        breed=0,
        getSliderPos=None,
        display_widget=None
    ):
        super(SlideDelegate, self).__init__(parent)
        self.setBreed(breed)

        # set initial attributes
        self.setBGSlideColor((32, 32, 32, 128))
        self.setFGSlideColor((32, 128, 32, 255))
        self.setDepth(50)
        self.setAlignment(Qt.AlignBottom)
        self._display_widget = display_widget
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

    def getFGSlideColor(self):
        return self._fg_slide_color

    def setFGSlideColor(self, color):
        self._fg_slide_color = color

    """ UTILS """
    def getBreedWidget(self):
        """
        0 = Unit
        1 = Hue
        2 = Sat
        4 = Val
        """
        breed = self.getBreed()
        if breed == SlideDelegate.UNIT:
            return UnitSlideDisplay(
                bg_slide_color=self.getBGSlideColor(),
                fg_slide_color=self.getFGSlideColor(),
                alignment=self.getAlignment(),
                display_widget=self._display_widget,
                depth=self._depth
            )
        else:
            pass

    """ EVENTS """
    def eventFilter(self, obj, event, *args, **kwargs):
        if event.type() == QEvent.MouseButtonPress:
            self.slidebar = self.getBreedWidget()
            self.slidebar.setWidgetPosition(
                self.getAlignment(), widget=self._display_widget
            )
            self.slidebar.show()

            return QWidget.eventFilter(self, obj, event, *args, **kwargs)
        elif event.type() == QEvent.MouseMove:
            try:
                try:
                    slider_pos = self.getSliderPos(event)
                except TypeError:
                    slider_pos = self.getSliderPos(obj, event)
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
    import sys
    from cgwidgets.utils import installLadderDelegate
    from qtpy.QtWidgets import QLineEdit, QVBoxLayout, QLabel, QPushButton
    from qtpy.QtGui import QCursor

    class TestWidget(QLineEdit):
        def __init__(self, parent=None, value=0):
            super(TestWidget, self).__init__(parent)
            pos = QCursor().pos()
            self.setGeometry(pos.x(), pos.y(), 200, 100)
            value_list = [0.001, 0.01, 0.1, 1, 10, 100, 1000]
            pos = QCursor.pos()
            ladder = installLadderDelegate(
                self,
                user_input=QEvent.MouseButtonPress,
                value_list=value_list
            )

            ladder.setDiscreteDrag(True, alignment=Qt.AlignLeft, depth=10)
            ladder.setDiscreteDrag(
                True,
                alignment=Qt.AlignLeft,
                depth=10,
                fg_color=(128, 128, 32, 255),
                display_widget=self.parent().parent()
                )
            #ladder.setDiscreteDrag(True, alignment=Qt.AlignLeft)

        def setValue(self, value):
            self.setText(str(value))

    app = QApplication(sys.argv)
    mw = QWidget()
    ml = QVBoxLayout()
    mw.setLayout(ml)

    w2 = QWidget(mw)
    w2.setStyleSheet('background-color: rgba(0,255,255,255)')
    l2 = QVBoxLayout()
    #l2.setContentsMargins(0,0,0,0)
    w2.setLayout(l2)

    menu = TestWidget(w2)
    l2.addWidget(menu)
    l2.addWidget(QPushButton('BUTTTON'))
    l2.addWidget(QLabel('LABELLLLL'))

    ml.addWidget(w2)
    mw.show()
    sys.exit(app.exec_())
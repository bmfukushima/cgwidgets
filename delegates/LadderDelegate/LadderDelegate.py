import sys
import math

from qtpy.QtGui import *
from qtpy.QtWidgets import *
from qtpy.QtCore import *

'''
#-------------------------------------------------------------------------- Bugs
Slider no longer updating....

# -----------------------------------------------------------------------To Do

- Detect if close to edge...
    - Detect center point function
    - only needs to handle y pos

#------------------------------------------------------------------- API
    seperate display option "discrete" mode:
        - Transparent while sliding option
        - display values somewhere non obtrustive
        - minimal value slider ticker...

    
'''


class LadderDelegate(QWidget):
    '''
    Widget that should be added as a popup during an event.  This should be
    installed with the utils.installLadderDelegate(widget).
    
    - 
    @item_list: list of all of the items
    @is_active  boolean to determine if the widget
                        is currently being manipulated by
                        the user
    @current_item: <LadderItem>
        The current item that the user is manipulating.  This property is currently used
        to determine if this ladder item should have its visual appearance changed on
        interaction.
                        
    +
    @slide_distance: <float>
        multiplier of how far the user should have to drag in order
        to trigger a value update.  Lower values are slower, higher
        values are faster.
    @bg_slide_color: < rgba > | ( int array ) | 0 - 255 
        The bg color that is displayed to the user when the user starts
        to click/drag to slide
    @fg_slide_color: < rgba > | ( int array ) | 0 - 255 
        The bg color that is displayed to the user when the user starts
        to click/drag to slide
    @selection_color: < rgba >  | ( int array ) | 0 - 255 
        The color that is displayed to the user when they are selecting
        which value they wish to adjust
    @item_height: < int>
        The height of each individual adjustable item.  The middle item will always
        have the same geometry as the parent widget.
    # no longer valid
    the @widget needs a 'setValue' method, this is where
    the LadderDelegate will set the value.  The value ladder
    does @widget.setValue(offset=offset) where offset is
    the amount that the current value should be offset.

    The setValue, will then need to do the final math to calculate the result
    '''
    def __init__(
            self, parent=None,
            widget=None,
            pos=None,
            value_list=None
    ):
        super(LadderDelegate, self).__init__(parent)
        if self.getValue() is None:
            print('This widgets like numbers. Not whatever you put in here.')
            return
        layout = QVBoxLayout()
        self.setLayout(layout)
        # self.setWidget(widget)

        # default attrs
        self.setSlideDistance(.01)
        self.setBGSlideColor((18, 18, 18, 128))
        self.setFGSlideColor((32, 128, 32, 255))
        self.setSelectionColor((32, 32, 32, 255))
        self.setItemHeight(50)
        self.setMiddleItemBorderWidth(2)

        # set up style
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setWindowFlags(
            self.windowFlags()
            | Qt.FramelessWindowHint
            | Qt.Popup
        )

        self.middle_item_index = int(len(value_list) * 0.5)

        # create widgets
        for value in value_list:
            widget = LadderItem(
                value_mult=value,
                height=self.getItemHeight(),
                width=self.parent().width()
            )
            layout.addWidget(widget)
            self.item_list.append(widget)

        # special handler for display widget
        self.middle_item = LadderMiddleItem(
            parent=self,
            value=self.getValue(),
            height=self.parent().height(),
            width=self.parent().width()
        )
        layout.insertWidget(self.middle_item_index, self.middle_item)
        item_list = self.item_list
        item_list.insert(self.middle_item_index, self.middle_item)
        self.item_list = item_list

        self.__setPosition()

    ''' API '''

    def getMiddleItemBorderWidth(self):
        return self._middle_item_border_width
    
    def setMiddleItemBorderWidth(self, border_width):
        self._middle_item_border_width = border_width    

    def getSlideDistance(self):
        return self._slide_distance
    
    def setSlideDistance(self, slide_distance):
        self._slide_distance = slide_distance

    def getBGSlideColor(self):
        return self._bg_slide_color
    
    def setBGSlideColor(self, color):
        self._bg_slide_color = color

    def getFGSlideColor(self):
        return self._fg_slide_color
    
    def setFGSlideColor(self, color):
        self._fg_slide_color = color

    def getSelectionColor(self):
        return self._selection_color
    
    def setSelectionColor(self, color):
        self._selection_color = color

    def getItemHeight(self):
        return self._item_height
        
    def setItemHeight(self, item_height):
        self._item_height = item_height

    ''' PROPERTIES '''

    @property
    def current_item(self):
        return self._current_item

    @current_item.setter
    def current_item(self, current_item):
        self._current_item = current_item

    @property
    def is_active(self):
        if not hasattr(self, '_is_active'):
            self._is_active = False
        return self._is_active

    @is_active.setter
    def is_active(self, boolean):
        self._is_active = boolean
    
    @property
    def item_list(self):
        if not hasattr(self, '_item_list'):
            self._item_list = []
        return self._item_list

    @item_list.setter
    def item_list(self, item_list):
        '''
        list of widgets
        '''
        self._item_list = item_list

    def setValue(self, value):
        '''
        @value: <float>
        Sets the value on the parent widget.
        
        creating a setValue(value) method on the parent widget
        will run this method last when setting the value
        '''
        if value is not None:
            self._value = value
            parent = self.parent()
            # set value
            self.middle_item.setValue(str(self._value))
            parent.setText(str(self._value))
            try:
                parent.setValue(value)
            except AttributeError:
                print('{} has no method \"setValue(value)\"'.format(parent))

    def getValue(self):
        try:
            self._value = float(self.parent().text())
            return self._value
        except ValueError:
            return None

    ''' UTILS '''

    def __setPosition(self):
        '''
        sets the position of the delegate relative to the
        widget that it is adjusting
        '''
        num_values = len(self.item_list)
        pos = self.parent().pos()

        # set position
        offset = self.middle_item_index * self.getItemHeight()
        pos = QPoint(
            pos.x(),
            pos.y()
            - ((self.getItemHeight() * (num_values + 1))
            * .5)
            + self.parent().height() + 6
        )
        self.move(pos)

    ''' EVENTS '''

    def leaveEvent(self, event, *args, **kwargs):
        if self.is_active is False:
            self.close()
        return QWidget.leaveEvent(self, event, *args, **kwargs)

    def keyPressEvent(self, event, *args, **kwargs):
        if event.key() == Qt.Key_Escape:
            self.close()
        return QWidget.keyPressEvent(self, event, *args, **kwargs)


class iLadderItem():
    def updateColor(self, xpos):
        '''
        @xpos: floatf of single channel rgb color
        sets the style sheet to converge from left
        to right so that each full convergance will
        display another increment in value 
        '''
        style_sheet = '''
        background: qlineargradient(
            x1:{xpos1} y1:0,
            x2:{xpos2} y2:0,
            stop:0 rgba{bgcolor},
            stop:1 rgba{fgcolor}
        );
        '''.format(
                xpos1=str(xpos),
                xpos2=str(xpos + 0.01),
                bgcolor=repr(self.parent().getBGSlideColor()),
                fgcolor=repr(self.parent().getFGSlideColor())
            )
        self.setStyleSheet(style_sheet)

    def updateWidgetGradients(self, xpos):
        '''
        Draws out the moving slider over the items to show
        the user how close they are to the next tick
        '''
        item_list = self.parent().item_list
        for index, item in enumerate(item_list):
            if index is not self.parent().middle_item_index:
                if item is not self.parent().current_item:
                    item.updateColor(xpos)
    

class LadderMiddleItem(QLabel, iLadderItem):
    '''
    Poorly named class... this is the display label to overlay
    over the current widget.  Due to how awesomely bad
    transparency is to do in Qt =\
    '''
    def __init__(self, parent=None, height=50, value=None, width=100):
        super(LadderMiddleItem, self).__init__(parent)
        self.setValue(value)
        self.setFixedHeight(height)
        self.setFixedWidth(width)
        self.default_style_sheet = self.styleSheet()
        self.setStyleSheet('border-width: {}px; border-color: rgb(18,18,18);border-style: solid;'.format(
            self.parent().getMiddleItemBorderWidth())
        )
        #self.setStyleSheet('background-color: rgb(255,0,0)')

    def setValue(self, value):
        self.setText(str(value))
        self._value = value

    def getValue(self):
        return float(self._value)


class LadderItem(QLabel, iLadderItem):
    '''
    @orig_value: <float> the value of the widget prior to starting a
        value adjustment.  This is reset everytime a new value adjustment
        is started.
    @value_mult: float how many units the drag should update
    @start_pos: QPoint starting position of drag
    @num_ticks: < int > how many units the user has moved.
        ( units_moved * value_mult ) + orig_value = new_value
    '''
    def __init__(self, parent=None, value_mult='', height=50, width=None):
        super(LadderItem, self).__init__(parent)

        # set default attrs
        self._value_mult = value_mult
        self.setText(str(value_mult))
        self.default_stylesheet = self.styleSheet()
        self.setFixedHeight(height)
        self.setFixedWidth(width)
    
    ''' PROPERTIES '''
    @property
    def num_ticks(self):
        return self._num_ticks
    
    @num_ticks.setter
    def num_ticks(self, num_ticks):
        self._num_ticks = num_ticks
    
    @property
    def orig_value(self):
        return self._orig_value
    
    @orig_value.setter
    def orig_value(self, orig_value):
        self._orig_value = orig_value
    
    @property
    def value_mult(self):
        return self._value_mult

    @value_mult.setter
    def value_mult(self, value_mult):
        self._value_mult = value_mult

    @property
    def start_pos(self):
        if not hasattr(self, '_start_pos'):
            self._start_pos = QCursor.pos()
        return self._start_pos

    @start_pos.setter
    def start_pos(self, pos):
        self._start_pos = pos

    ''' UTILS '''

    def __resetWidgetGradients(self):
        '''
        Returns all of the items back to their default color
        '''
        item_list = self.parent().item_list
        for index, item in enumerate(item_list):
            if index != self.parent().middle_item_index:
                item.__resetColor()

    def __resetColor(self):
        '''
        resets the color widget color back to default
        '''
        self.setStyleSheet(self.default_stylesheet)

    ''' EVENTS '''

    def enterEvent(self, *args, **kwargs):
        '''
        hack to set up hover color for QLabels
        '''
        if self.parent().is_active is False:
            self.setStyleSheet(
                'background-color: rgba{selected_color}'.format(
                    selected_color=repr(self.parent().getSelectionColor()))
                )
        return QLabel.enterEvent(self, *args, **kwargs)

    def leaveEvent(self, *args, **kwargs):
        '''
        hack to set up hover color for QLabels
        reset to default values
        '''
        self.setStyleSheet(self.default_stylesheet)
        return QLabel.leaveEvent(self, *args, **kwargs)

    def mousePressEvent(self, event, *args, **kwargs):
        '''
        if the user clicks on the item, it will start the click/drag value adjust
        '''
        # get initial position
        pos = QCursor.pos()
        self.start_pos = pos
        self.parent().current_item = self
        
        # initialize attrs
        self.orig_value = self.parent().middle_item.getValue()
        self.num_ticks = 0
        self.parent().is_active = True

        # reset style
        self.__resetColor()
        return QLabel.mousePressEvent(self, event, *args, **kwargs)

    def mouseMoveEvent(self, event, *args, **kwargs):
        '''
        primary work horse for mouse movement slider
        '''
        MAGNITUDE_MULTIPLIER = self.parent().getSlideDistance()
        if self.parent().is_active is True:
            # get attrs
            current_pos = QCursor.pos()
            start_pos = self.start_pos

            # get magnitude
            xoffset = start_pos.x() - current_pos.x()
            yoffset = start_pos.y() - current_pos.y()
            magnitude = math.sqrt(
                pow(xoffset, 2)
                + pow(yoffset, 2)
            )

            # determine offset direction
            offset = self.value_mult
            if xoffset > 0:
                magnitude *= -1
            magnitude *= MAGNITUDE_MULTIPLIER

            # ===================================================================
            # update values
            # note: this will look for a change with num_ticks vs magnitude
            #         to determine when a full value changed has happened
            # ===================================================================
            # update value
            xpos = math.fabs(math.modf(magnitude)[0])
            if self.num_ticks != int(magnitude):
                offset *= self.num_ticks
                return_val = offset + self.orig_value
                self.parent().setValue(return_val)
                self.num_ticks = int(magnitude)
            self.updateWidgetGradients(xpos)
        return QLabel.mouseMoveEvent(self, event, *args, **kwargs)

    def mouseReleaseEvent(self, *args, **kwargs):
        # reset all of the items/attributes back to default
        self.parent().is_active = False
        self.parent().current_item = None
        self.__resetWidgetGradients()
        return QLabel.mouseReleaseEvent(self, *args, **kwargs)


''' TEST STUFF '''


class TestWidget(QLineEdit):
    def __init__(self, parent=None, value=0):
        super(TestWidget, self).__init__(parent)
        pos = QCursor().pos()
        self.setGeometry(pos.x(), pos.y(), 200, 100)
        self._value_list = [0.001, 0.01, 0.1, 1, 10, 100, 1000]

    def setValue(self, value):
        self.setText(str(value))

    def mousePressEvent(self, event, *args, **kwargs):
        '''
        trigger to active the popup menu
        '''
        if event.button() == Qt.MiddleButton:
            ladder = LadderDelegate(
                parent=self,
                widget=self,
                #pos=self.pos(),
                value_list=self._value_list
            )
            ladder.show()
        return QLineEdit.mousePressEvent(self, event, *args, **kwargs)

'''
app = QApplication(sys.argv)
menu = TestWidget()
menu.show()
sys.exit(app.exec_())
'''

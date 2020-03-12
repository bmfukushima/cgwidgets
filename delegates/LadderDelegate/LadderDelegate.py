"""
#-------------------------------------------------------------------------- Bugs
    * Updating values on ladder during slide...
        seems to be calculating correctly... just not properly updating?

# -----------------------------------------------------------------------To Do

    * Detect if close to edge...
        - Detect center point function
        - only needs to handle y pos

#------------------------------------------------------------------- API
    * seperate display option "discrete" mode:
        - Transparent while sliding option
        - display values somewhere non obtrustive
        - minimal value slider ticker...

    * need to figure out how to make eventFilter more robust...
        ie support CTRL+ALT+CLICK / RMB, etc
            rather than just a QEvent.Type
    
    * set range
        allow ladder widget to only go between a specifc range
            ie
                Only allow this to work in the 0-1 range
    
"""
import sys
import math

from qtpy.QtGui import *
from qtpy.QtWidgets import *
from qtpy.QtCore import *

from cgwidgets.__utils__ import getGlobalPos
from decimal import Decimal, getcontext


class LadderDelegate(QWidget):
    """
    Widget that should be added as a popup during an event.  This should be
    installed with the utils.installLadderDelegate(widget).
    args:

    kwargs: 
        @parent: <QLineEdit> or <QLabel>
            widget to install ladder delegate onto.  Note this currently
            works for QLineEdit and QLabel.  
            
            Other widgets will need to implement the 'setValue(value)'
            method to properly parse the value from the ladder to the widget.

        @value_list: <list> of <float>
            list of values for the user to be able to adjust by, usually this
            is set to .01, .1, 1, 10, etc

        @user_input: <QEvent.Type>
            The action for the user to do to trigger the ladder to be installed
                ie.
            QEvent.MouseButtonPress
    
    properties:
        +
        use getters / setters
            ie.
        getPropertyName()
        setPropertyName(value)
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

        The setValue, will then need to do the final math to calculate the result
        -
        @item_list: list of all of the items

        @is_active  boolean to determine if the widget
                            is currently being manipulated by
                            the user

        @current_item: <LadderItem>
            The current item that the user is manipulating.  This property is
            currently used to determine if this ladder item should have its
            visual appearance changed on interaction.

        @middle_item_index: <int>
            Index of the middle item in the item's list.  This is used to offset
            the middle item to overlay the widget it was used on.
    """
    def __init__(
            self,
            parent=None,
            value_list=None,
            user_input=None,
    ):
        super(LadderDelegate, self).__init__(parent)
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
        self.setUserInput(user_input)
        self.middle_item_index = int(len(value_list) * 0.5)

        # set up style
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setWindowFlags(
            self.windowFlags()
            | Qt.FramelessWindowHint
            | Qt.Popup
        )

        # create widgets
        for value in value_list:
            widget = LadderItem(
                value_mult=value
            )
            layout.addWidget(widget)
            self.item_list.append(widget)

        # special handler for display widget
        self.middle_item = LadderMiddleItem(
            parent=self,
            value=self.getValue()
        )
        layout.insertWidget(self.middle_item_index, self.middle_item)
        item_list = self.item_list
        item_list.insert(self.middle_item_index, self.middle_item)
        self.item_list = item_list
        self.__setSignificantDigits()

    """ API """

    def getUserInput(self):
        return self._user_input
    
    def setUserInput(self, user_input):
        self._user_input = user_input

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

    """ PROPERTIES """

    @property
    def middle_item_index(self):
        return self._middle_item_index

    @middle_item_index.setter
    def middle_item_index(self, middle_item_index):
        self._middle_item_index = middle_item_index

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
        """
        list of widgets
        """
        self._item_list = item_list

    def setValue(self, value):
        """
        args:
            @value: <float>
            Sets the value on the parent widget.
            
            creating a setValue(value) method on the parent widget
            will run this method last when setting the value
        """
        if value is not None:
            self._value = value
            parent = self.parent()
            # set value
            self.middle_item.setValue(str(self._value))
            parent.setText(str(self._value))

    def getValue(self):
        try:
            self._value = float(self.parent().text())
            return self._value
        except ValueError:
            return None

    """ UTILS """
    def __setSignificantDigits(self):
        '''
        sets the number of significant digits to round to
        
        This is to avoid floating point errors...
        
        Currently only working with what's set up... does not expand
        when the number of sig digits increases... this really only needs
        to work for decimals
        '''
        self._significant_digits = 1
        for item in self.item_list:
            if item is not self.middle_item:
                value = item.value_mult
                string_value = ''.join(str(value).lstrip('0').rstrip('0').split('.'))
                sig_digits = int(len(string_value))
                if sig_digits > self._significant_digits:
                    self._significant_digits = sig_digits
        
        getcontext().prec = self._significant_digits

    def __setItemSize(self):
        
        # set adjustable items
        height = self.getItemHeight()
        width = self.parent().width()
        for item in self.item_list:
            item.setFixedSize(width, height)
        
        # set display item ( middle item)
        self.middle_item.setFixedSize(width, self.parent().height())
            
    def __setPosition(self):
        """
        sets the position of the delegate relative to the
        widget that it is adjusting
        """
        num_values = len(self.item_list)

        pos = getGlobalPos(self.parentWidget())
        # set position
        offset = self.middle_item_index * self.getItemHeight()
        pos = QPoint(
            pos.x(),
            pos.y() - offset
        )
        self.move(pos)

    """ EVENTS """
    def hideEvent(self, *args, **kwargs):
        self.is_active = False
        return QWidget.hideEvent(self, *args, **kwargs)

    def showEvent(self, *args, **kwargs):
        self.middle_item.setValue(self.getValue())
        self.__setItemSize()
        self.__setPosition()
        return QWidget.showEvent(self, *args, **kwargs)

    def leaveEvent(self, event, *args, **kwargs):
        if self.is_active is False:
            self.hide()
        return QWidget.leaveEvent(self, event, *args, **kwargs)

    def keyPressEvent(self, event, *args, **kwargs):
        if event.key() == Qt.Key_Escape:
            self.hide()
        return QWidget.keyPressEvent(self, event, *args, **kwargs)
    
    def eventFilter(self, obj, event, *args, **kwargs):
        """
        installed on the parent widget to determine the user input
        for triggering the ladder delegate
        """
        if self.getValue() is None:
            # print('This widgets like numbers. Not whatever you put in here.')
            return QWidget.eventFilter(self, obj, event, *args, **kwargs)
        if event.type() == self.getUserInput():
            self.show()
        return QWidget.eventFilter(self, obj, event, *args, **kwargs)


class LadderMiddleItem(QLabel):
    """
    This is the display label to overlay
    over the current widget.  

    Due to how awesomely bad transparency is to do in Qt =\
    """
    def __init__(self, parent=None, height=50, value=None, width=100):
        super(LadderMiddleItem, self).__init__(parent)
        self.setValue(value)
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


class LadderItem(QLabel):
    """
    This represents one item in the ladder that is displayed to the user.
    Clicking/Dragging left/right on one of these will update the widget
    that is passed to the ladder delegate.

    kwargs:
        orig_value < float >
            the value of the widget prior to starting a
            value adjustment.  This is reset everytime a new value adjustment
            is started.

        value_mult < float >
            how many units the drag should update

        start_pos < QPoint >
            starting position of drag

        num_ticks < int >
            how many units the user has moved.
            ( num_ticks * value_mult ) + orig_value = new_value

    """
    def __init__(
            self,
            parent=None,
            value_mult='',
            height=50,
            width=None
        ):
        super(LadderItem, self).__init__(parent)

        # set default attrs
        self._value_mult = value_mult
        self.setText(str(value_mult))
        self.default_stylesheet = self.styleSheet()
    
    """ PROPERTIES """
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
        self._orig_value = Decimal(orig_value)
    
    @property
    def value_mult(self):
        return self._value_mult

    @value_mult.setter
    def value_mult(self, value_mult):
        self._value_mult = Decimal(value_mult)

    @property
    def start_pos(self):
        if not hasattr(self, '_start_pos'):
            self._start_pos = QCursor.pos()
        return self._start_pos

    @start_pos.setter
    def start_pos(self, pos):
        self._start_pos = pos

    """ UTILS """
    def __updateColor(self, xpos):
        """
        changes the color for the moving slider for all
        the individual items in the ladder

        args:
            @xpos: floatf of single channel rgb color
            sets the style sheet to converge from left
            to right so that each full convergance will
            display another increment in value 
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
                bgcolor=repr(self.parent().getBGSlideColor()),
                fgcolor=repr(self.parent().getFGSlideColor())
            )
        self.setStyleSheet(style_sheet)

    def __updateWidgetGradients(self, xpos):
        """
        Draws out the moving slider over the items to show
        the user how close they are to the next tick

        args:
            @xpos: floatf of single channel rgb color
            sets the style sheet to converge from left
            to right so that each full convergance will
            display another increment in value 
        """
        item_list = self.parent().item_list
        for index, item in enumerate(item_list):
            if index is not self.parent().middle_item_index:
                if item is not self.parent().current_item:
                    item.__updateColor(xpos)

    def __resetWidgetGradients(self):
        """
        Returns all of the items back to their default color
        """
        item_list = self.parent().item_list
        for index, item in enumerate(item_list):
            if index != self.parent().middle_item_index:
                item.__resetColor()

    def __resetColor(self):
        """
        resets the color widget color back to default
        """
        self.setStyleSheet(self.default_stylesheet)

    def __updateSignificantDigits(self):
        sig_digits = self.parent()._significant_digits
        int_len = len(self.parent().middle_item.text().split('.')[0])
        getcontext().prec = sig_digits + int_len 


    """ EVENTS """

    def enterEvent(self, *args, **kwargs):
        """
        hack to set up hover color for QLabels
        """
        if self.parent().is_active is False:
            self.setStyleSheet(
                'background-color: rgba{selected_color}'.format(
                    selected_color=repr(self.parent().getSelectionColor()))
                )
        return QLabel.enterEvent(self, *args, **kwargs)

    def leaveEvent(self, *args, **kwargs):
        """
        hack to set up hover color for QLabels
        reset to default values
        """
        self.setStyleSheet(self.default_stylesheet)
        return QLabel.leaveEvent(self, *args, **kwargs)

    def mousePressEvent(self, event, *args, **kwargs):
        """
        if the user clicks on the item, it will start the click/drag value adjust
        """
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
        """
        primary work horse for mouse movement slider
        """
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
                self.__updateSignificantDigits()
                # do math
                offset *= self.num_ticks
                return_val = Decimal(offset) + self.orig_value
                #print(Decimal(offset) , self.orig_value)
                # set value
                self.parent().setValue(return_val)

                # reset values
                self.num_ticks = int(magnitude)
            self.__updateWidgetGradients(xpos)
        return QLabel.mouseMoveEvent(self, event, *args, **kwargs)

    def mouseReleaseEvent(self, *args, **kwargs):
        # reset all of the items/attributes back to default
        self.parent().is_active = False
        self.parent().current_item = None
        self.__resetWidgetGradients()
        return QLabel.mouseReleaseEvent(self, *args, **kwargs)

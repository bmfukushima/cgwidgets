"""
# -------------------------------------------------------------------------- Bugs
    * First tick does not register

# -----------------------------------------------------------------------To Do
    * Detect if close to edge...
        - Detect center point function
        - only needs to handle y pos
    * Horizontal Delegate?
    * Move SlideDelegate display widget to the
        "setDiscreteMode" method

# ------------------------------------------------------------------- API
    * seperate display option "discrete" mode:
        - How to set transparency?
            - New delegate?
                This is probably better...
            - Force set in LadderDelegate?
        - display values somewhere non obtrustive

    * need to figure out how to make eventFilter more robust...
        ie support CTRL+ALT+CLICK / RMB, etc
            rather than just a QEvent.Type

    * set range
        allow ladder widget to only go between a specifc range
            ie
                Only allow this to work in the 0-1 range

"""
import math
from decimal import Decimal, getcontext

from qtpy.QtGui import *
from qtpy.QtWidgets import *
from qtpy.QtCore import *

from cgwidgets.utils import (
    getGlobalPos,
    installInvisibleDragEvent,
    installSlideDelegate,
    removeSlideDelegate
)
from cgwidgets.delegates import SlideDelegate


class LadderDelegate(QWidget):
    """
    Widget that should be added as a popup during an event.  This should be
    installed with the utils.installLadderDelegate(widget).

    If you directly install this on a widget.  The widget must have the text/getText
    methods (QLineEdit/QLabel).  If they do not, you need to subclass this and
    reimplement the setValue() and getValue() methods or add those methods
    to the parent widget.


    Kwargs:
        parent: (QLineEdit) or (QLabel)
            widget to install ladder delegate onto.  Note this currently
            works for QLineEdit and QLabel.

            Other widgets will need to implement the 'setValue(value)'
            method to properly parse the value from the ladder to the widget.

        value_list: (list) of (float)
            list of values for the user to be able to adjust by, usually this
            is set to .01, .1, 1, 10, etc

        user_input: (QEvent.Type)
            The action for the user to do to trigger the ladder to be installed
                ie.
            QEvent.MouseButtonPress

        invisible_drag (bool): Toggle on/off the invisible drag
            functionality.  Having this turned on will also enable cursor
            wrapping for infinite dragging

        slide_bar (bool): Toggle on/off the slide bar while manipulating
            the ladder


    Attributes:
        + Public:
            use getters / setters
                ie.
                    getPropertyName()
                    setPropertyName(value)

            user_input: (QEvent)
                Event to be used on the widget to allow the user to trigger
                the ladder delegate to popup
                    ie
                        QEvent.MouseButtonPress

            middle_item_border_width: (int)
                The width of the border for the widget that displays the current value

            slide_distance: (float)
                multiplier of how far the user should have to drag in order
                to trigger a value update.  Lower values are slower, higher
                values are faster.

            selection_color: (rgba)  | ( int array ) | 0 - 255
                The color that is displayed to the user when they are selecting
                which value they wish to adjust

            item_height: (int)
                The height of each individual adjustable item.  The middle item
                will always have the same geometry as the parent widget.

            * The setValue, will then need to do the final math to calculate the result

        - Private
            item_list (list)
                list of all of the ladder items

            is_active  (boolean)
                determines if the widget is currently being manipulated by the user

            current_item: (LadderItem)
                The current item that the user is manipulating.  This property
                is currently used to determine if this ladder item should have
                its visual appearance changed on interaction.

            middle_item_index: (int)
                Index of the middle item in the item's list.  This is used to
                offset the middle item to overlay the widget it was used on.
    """
    def __init__(
            self,
            parent=None,
            value_list=[0.001, 0.01, 0.1, 1, 10, 100, 1000],
            user_input=QEvent.MouseButtonPress,
            widget=None
    ):
        super(LadderDelegate, self).__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)
        # self.setWidget(widget)

        # default attrs
        self.setSlideDistance(.01)
        self.setBGSlideColor((0, 0, 0, 128))
        self.setFGSlideColor((128, 128, 32, 255))
        self.setSelectionColor((32, 32, 32, 255))
        self.setItemHeight(50)
        self.setMiddleItemBorderWidth(2)
        self.setUserInput(user_input)
        self._widget = widget
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

        # populate item list
        item_list = self.item_list
        item_list.insert(self.middle_item_index, self.middle_item)
        self.item_list = item_list

        # set significant digits
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

    # remove
    def getBGSlideColor(self):
        return self._bg_slide_color

    # remove
    def setBGSlideColor(self, color):
        self._bg_slide_color = color

    # remove
    def getFGSlideColor(self):
        return self._fg_slide_color

    # remove
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
        Args:
            value: (float)
            Sets the value on the parent widget.

            creating a setValue(value) method on the parent widget
            will run this method last when setting the value
        """
        if value is not None:
            self._value = value
            parent = self.parent()
            # set value
            self.middle_item.setValue(str(self._value))
            try:
                parent.setText(str(self._value))
            except AttributeError:
                try:
                    self.parent().setValue(self._value)
                except AttributeError:
                    return None

    def getValue(self):
        """
        Returns:
            current parent widgets value. Will attempt to look for the
            default text() attr, however if it is not available, will look for
            the parents getValue() method.
        """
        try:
            self._value = float(self.parent().text())
            return self._value
        except AttributeError:
            try:
                return self.parent().getValue()
            except AttributeError:
                return None
        except ValueError:
            return None

    """ UTILS """
    def __setSignificantDigits(self):
        """
        sets the number of significant digits to round to

        This is to avoid floating point errors...

        Currently only working with what's set up... does not expand
        when the number of sig digits increases... this really only needs
        to work for decimals
        """
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
        """
        Sets each individual item's size according to the
        getItemHeight and parents widgets width

        This is also probably where I will be installing a delegate
        for a horizontal ladder layout...
        """
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
        pos = getGlobalPos(self.parentWidget())
        # set position
        offset = self.middle_item_index * self.getItemHeight()
        pos = QPoint(
            pos.x(),
            pos.y() - offset
        )
        self.move(pos)

    def __setInvisibleDrag(self, boolean):
        """
        When the mouse is click/dragged in each individual
        item, the cursor dissappears from the users view.  When
        the user releases the trigger, it will show the cursor again
        at the original clicking point.
        """
        for item in self.item_list:
            if not isinstance(item, LadderMiddleItem):
                if boolean is True:
                    installInvisibleDragEvent(item)
                elif boolean is False:
                    self.removeEventFilter()

    def __setSlideBar(
        self,
        boolean,
        alignment=Qt.AlignRight,
        depth=50,
        fg_color=(32, 32, 32, 255),
        bg_color=(32, 128, 32, 255),
        breed=SlideDelegate.UNIT
    ):
        """
        Creates a visual bar on the screen to show the user
        how close they are to creating the next tick
        """
        for item in self.item_list:
            if not isinstance(item, LadderMiddleItem):
                if boolean is True:
                    slidebar = installSlideDelegate(
                        item,
                        sliderPosMethod=item.getCurrentPos,
                        breed=breed,
                        display_widget=self._widget
                    )
                    slidebar.setBGSlideColor(bg_color)
                    slidebar.setFGSlideColor(fg_color)
                    slidebar.setDepth(depth)

                    slidebar.setAlignment(alignment)
                    item.slidebar = slidebar

                elif boolean is False:
                    try:
                        removeSlideDelegate(item, item.slidebar)
                    except AttributeError:
                        pass

    def setDiscreteDrag(
        self,
        boolean,
        alignment=Qt.AlignRight,
        depth=50,
        fg_color=(32, 32, 32, 255),
        bg_color=(32, 128, 32, 255),
        breed=SlideDelegate.UNIT
    ):
        """
        Discrete drag is a display mode that happens when
        the user manipulates an item in the ladder ( click + drag +release)

        On pen down, the cursor will dissapear and a visual cue will be added
        based on the alignment kwarg. Pen drag will update the visual cue
        to show the user how close they are to the next tick.

        Args:
            boolean (boolean): Whether or not to enable/disable discrete
            drag mode

        Kwargs:
            depth (int): how wide/tall the widget should be depending
                on its orientation
            alignment (QtCore.Qt.Align): where the widget should be align
                relative to the display
            bg_slide_color rgba int 0-255):
                The bg color that is displayed to the user when the user starts
                to click/drag to slide
            fg_slide_color rgba int 0-255):
                The bg color that is displayed to the user when the user starts
                to click/drag to slide
            breed (SlideDelegate.TYPE): What type of visual cue to display.
                Other options HUE, SATURATION, VALUE
        """
        # delete old slidebar
        self.__setSlideBar(False)

        # set cursor drag mode
        self.__setInvisibleDrag(boolean)

        # create new slide bar
        if boolean is True:
            self.__setSlideBar(
                boolean,
                bg_color=bg_color,
                fg_color=fg_color,
                depth=depth,
                alignment=alignment,
                breed=breed
            )

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

    def closeEvent(self, event, *args, **kwargs):
        if self.is_active is True:
            return
        return QWidget.closeEvent(self, event, *args, **kwargs)

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
    def __init__(self, parent=None, value=None):
        super(LadderMiddleItem, self).__init__(parent)
        self.setValue(value)
        self.default_style_sheet = self.styleSheet()
        self.setStyleSheet(
            '''
        border-width: {}px;
        border-color: rgb(18,18,18);
        border-style: solid;
        '''.format(self.parent().getMiddleItemBorderWidth()))

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

    Kwargs:
        value_mult (float): how many units the drag should update

    Attributes:
        orig_value (float): the value of the widget prior to starting a
            value adjustment.  This is reset everytime a new value adjustment
            is started.
        value_mult (float): how many units the drag should update
        start_pos (QPoint): starting position of drag
        num_ticks (int): how many units the user has moved.
            ( num_ticks * value_mult ) + orig_value = new_value

    """
    def __init__(
        self,
        parent=None,
        value_mult=''
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
    def getCurrentPos(self, event):
        current_pos = self.mapToGlobal(event.pos())
        magnitude = self.__getMagnitude(self.start_pos, current_pos)
        return math.fabs(math.modf(magnitude)[0])
        #return self.slider_pos

    # remove
    def __updateColor(self, xpos):
        """
        changes the color for the moving slider for all
        the individual items in the ladder

        Args:
            xpos (float): single channel rgb color ( 0 - 1)
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

    # this can prob be removed
    def __updateWidgetGradients(self, xpos):
        """
        Draws out the moving slider over the items to show
        the user how close they are to the next tick

        Args:
            xpos (float): single channel rgb color ( 0 - 1)
                sets the style sheet to converge from left
                to right so that each full convergance will
                display another increment in value
        """
        item_list = self.parent().item_list
        for index, item in enumerate(item_list):
            if index is not self.parent().middle_item_index:
                if item is not self.parent().current_item:
                    item.__updateColor(xpos)

    # remove
    def __resetWidgetGradients(self):
        """
        Returns all of the items back to their default color
        """
        item_list = self.parent().item_list
        for index, item in enumerate(item_list):
            if index != self.parent().middle_item_index:
                item.__resetColor()

    #remove
    def __resetColor(self):
        """
        resets the color widget color back to default
        """
        self.setStyleSheet(self.default_stylesheet)

    def __updateSignificantDigits(self, value):
        '''
        updates the significant digits

        This is used to ensure that the floating point precision is
        correct when the user scrubs the widget

        Args:
            value (float)

        Returns:
            None
        '''
        sig_digits = self.parent()._significant_digits
        str_val = str(value).split('.')[0].replace('-', '')
        int_len = len(str_val)
        getcontext().prec = sig_digits + int_len

    def __getMagnitude(self, start_pos, current_pos):
        '''
        returns the magnitude of a user click/drop operation

        Args:
            start_pos (QPoint)
                initial point of the cursor.  This could be when the user
                clicked, or when the last tick was registered
            current_pos (QPoint)
                current position of the cursor
        Returns:
            float
        '''
        # get magnitude
        xoffset = start_pos.x() - current_pos.x()
        yoffset = start_pos.y() - current_pos.y()
        magnitude = math.sqrt(
            pow(xoffset, 2)
            + pow(yoffset, 2)
        )

        # direction of magnitude
        if xoffset > 0:
            magnitude *= -1

        # user mult
        MAGNITUDE_MULTIPLIER = self.parent().getSlideDistance()
        magnitude *= MAGNITUDE_MULTIPLIER
        return magnitude

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
        self.start_pos = QCursor.pos()
        self.parent().current_item = self

        # initialize attrs
        self.orig_value = self.parent().middle_item.getValue()
        self.num_ticks = 0
        self.parent().is_active = True
        self.slider_pos = 0

        # reset style
        self.__resetColor()
        return QLabel.mousePressEvent(self, event, *args, **kwargs)

    def mouseMoveEvent(self, event, *args, **kwargs):
        """
        primary work horse for mouse movement slider
        """
        if self.parent().is_active is True:
            # magnitude = self.__getMagnitude(self.start_pos, QCursor.pos())
            magnitude = self.__getMagnitude(self.start_pos, self.mapToGlobal(event.pos()))
            offset = self.value_mult

            # ===================================================================
            # update values
            # note: this will look for a change with num_ticks vs magnitude
            #         to determine when a full value changed has happened
            # ===================================================================
            # update value
            self.slider_pos = math.fabs(math.modf(magnitude)[0])
            self.__updateWidgetGradients(self.slider_pos)
            if self.num_ticks != int(magnitude):
                # reset values
                self.num_ticks = int(magnitude)

                # do math
                offset *= self.num_ticks
                self.__updateSignificantDigits(Decimal(offset) + self.orig_value)
                return_val = Decimal(offset) + self.orig_value

                # set value
                self.parent().setValue(return_val)

        return QLabel.mouseMoveEvent(self, event, *args, **kwargs)

    def mouseReleaseEvent(self, *args, **kwargs):
        # reset all of the items/attributes back to default
        self.parent().is_active = False
        self.parent().current_item = None
        self.__resetWidgetGradients()
        return QLabel.mouseReleaseEvent(self, *args, **kwargs)


if __name__ == '__main__':
    import sys
    from cgwidgets.utils import installLadderDelegate

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
                value_list=value_list,
                display_widget=self.parent()
            )

            ladder.setDiscreteDrag(True, alignment=Qt.AlignBottom)
            ladder.setDiscreteDrag(True, alignment=Qt.AlignRight)
            #ladder.setDiscreteDrag(True, alignment=Qt.AlignLeft)

        def setValue(self, value):
            self.setText(str(value))

    app = QApplication(sys.argv)
    mw = QWidget()
    ml = QVBoxLayout()
    mw.setLayout(ml)

    w2 = QWidget(mw)
    l2 = QVBoxLayout()
    w2.setLayout(l2)

    menu = TestWidget(w2)
    l2.addWidget(menu)
    l2.addWidget(QPushButton('BUTTTON'))
    l2.addWidget(QLabel('LABELLLLL'))

    ml.addWidget(w2)
    mw.show()
    sys.exit(app.exec_())

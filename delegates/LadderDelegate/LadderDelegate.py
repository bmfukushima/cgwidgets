import sys
import math

from qtpy.QtGui import *
from qtpy.QtWidgets import *
from qtpy.QtCore import *

'''
# ===============================================================================
# To Do
# ===============================================================================
- Detect if close to edge...
    - Detect center point function
    - only needs to handle y pos

LadderDelegate --> SetValue... -->
    Need to support multiple different widget types...
        Should overload this?
        
Slide direction change...
    midway through

Gradient Update:
    Not effect current selected value

Expose Colors
    

'''


class LadderDelegate(QWidget):
    '''
    @item_list: list of widgets
    @widget widget to send signal to update to
    @is_active  boolean to determine is the widget
                        is currently being manipulated by
                        the user
                        
    +
    @slide_distance: <float> multiplier of how far the user
        should have to drag in order to trigger a value update.
        Lower values are slower, higher values are faster.
    @slide_color: (<str>, <str>) | (color1, color2)
        The color that is displayed to the user when the user starts
        to click/drag to slide
        
        255, 255, 255, 255
        setter requires two strings that are comma delimeated RGBA values
        Color0:
            Background Color
        color1:
            Foreground Color
    @selected_color: <str> rgba 255, 255, 255, 255
        The color that is displayed to the user when they are selecting
        which value they wish to adjust
        
    # no longer valid
    the @widget needs a 'setValue' method, this is where
    the LadderDelegate will set the value.  The value ladder
    does @widget.setValue(offset=offset) where offset is
    the amount that the current value should be offset.

    The setValue, will then need to do the final math to calculate the result
    '''
    def __init__(
            self, parent=None,
            widget=None, pos=None,
            value_list=None
    ):
        super(LadderDelegate, self).__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setWidget(widget)

        # default attrs
        self._slide_distance = .01
        self._slide_color = ('18, 18, 18, 128', '255, 128, 32, 255')
        self._selected_color = '32, 32, 32, 255'
        # set up style
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setWindowFlags(
            self.windowFlags()
            | Qt.FramelessWindowHint
            | Qt.Popup
        )
        WIDGET_WIDTH = self.parentWidget().width()
        WIDGET_HEIGHT = 50

        # set position
        self.middle_item_index = int(len(value_list) * 0.5)
        offset = self.middle_item_index * WIDGET_HEIGHT
        pos = QPoint(
            pos.x(), #+ (WIDGET_WIDTH),
            pos.y() - ((WIDGET_HEIGHT * (len(value_list) + 1)) * .5)
        )
        self.move(pos)

        # create widgets
        for value in value_list:
            widget = LadderItem(
                value_mult=value,
                height=WIDGET_HEIGHT,
                width=WIDGET_WIDTH
            )
            layout.addWidget(widget)
            self.appendItemList(widget)

        # special handler for display widget
        self.middle_item = LadderMiddleItem(
            value=self.getValue(),
            height=WIDGET_HEIGHT,
            width=WIDGET_WIDTH
        )
        layout.insertWidget(self.middle_item_index, self.middle_item)
        item_list = self.getItemList()
        item_list.insert(self.middle_item_index, self.middle_item)
        self.setItemList(item_list)

    ''' API '''
    @property
    def slide_distance(self):
        return self._slide_distance
    
    @slide_distance.setter
    def slide_distance(self, slide_distance):
        self._slide_distance = slide_distance

    @property
    def slide_color(self):
        return self._slide_color
    
    @slide_color.setter
    def slide_color(self, color0, color1):
        self._slide_color = (color0, color1)

    @property
    def selected_color(self):
        return self._selected_color
    
    @selected_color.setter
    def selected_color(self, color):
        self._selected_color = color

    ''' PROPERTIES '''
    def appendItemList(self, widget):
        '''
        appends widget to item_list
        '''
        item_list = self.getItemList()
        item_list.append(widget)
        self.setItemList(item_list)

    def setItemList(self, item_list):
        '''
        list of widgets
        '''
        self.item_list = item_list

    def getItemList(self):
        if not hasattr(self, 'item_list'):
            self.item_list = []
        return self.item_list

    def setWidget(self, widget):
        self.widget = widget

    def getWidget(self):
        return self.widget

    def getIsActive(self):
        if not hasattr(self, 'is_active'):
            self.is_active = False
        return self.is_active

    def setIsActive(self, boolean):
        self.is_active = boolean

    def setValue(self, offset):
        value = self.getValue()
        if value is not None:
            self.value = float(value) + offset
            
            # set value
            
            self.middle_item.setText(str(self.value))
            self.parent().setText(str(self.value))

    def getValue(self):
        try:
            self.value = float(self.parent().text())
            return self.value
        except ValueError:
            print('knead numba...')
            return None

    ''' UTILS '''

    def updateWidgetGradients(self, xpos):
        '''
        Draws out the moving slider over the items to show
        the user how close they are to the next tick
        '''
        item_list = self.getItemList()
        for index, item in enumerate(item_list):
            if index != self.middle_item_index:
                item.updateColor(xpos)

    def resetWidgetGradients(self):
        '''
        Returns all of the items back to their default color
        '''
        item_list = self.getItemList()
        for index, item in enumerate(item_list):
            if index != self.middle_item_index:
                item.resetColor()

    ''' EVENTS '''

    def leaveEvent(self, event, *args, **kwargs):
        if self.getIsActive() is False:
            self.close()
        return QWidget.leaveEvent(self, event, *args, **kwargs)

    def keyPressEvent(self, event, *args, **kwargs):
        if event.key() == Qt.Key_Escape:
            self.close()
        return QWidget.keyPressEvent(self, event, *args, **kwargs)


class LadderMiddleItem(QLabel):
    '''
    Poorly named class... this is the display label to overlay
    over the current widget.  Due to how awesomely bad
    transparency is to do in Qt =\
    '''
    def __init__(self, parent=None, height=50, value=None, width=100):
        super(LadderMiddleItem, self).__init__()
        self.setValue(value)
        self.setFixedHeight(height)
        self.setFixedWidth(width)
        self.default_style_sheet = self.styleSheet()
        self.setStyleSheet('border-width: 3px; border-color: rgb(18,18,18);border-style: solid;')
        #self.setStyleSheet('background-color: rgb(255,0,0)')

    def setValue(self, value):
        self.setText(str(value))
        self.value = value

    def getValue(self):
        return self.value

    def updateColor(self, xpos):
        if self.getIsActive() is True:
            self.setStyleSheet("* {background: \
            qlineargradient( x1:{xpos1} y1:0, x2:{xpos2} y2:0, \
                stop:0 rgba({bgcolor}), stop:1 rgba({fgcolor}) \
            );}".format(
                xpos1=str(xpos),
                xpos2=str(xpos + 0.01),
                bgcolor=self.parent().slide_color[0],
                fgcolor=self.parent().slide_color[1]
                )
            )
        else:
            self.setStyleSheet(self.default_stylesheet)


class LadderItem(QLabel):
    '''
    
    @orig_value: float starting value of widget before opening of menu
    @value_mult: float how many units the drag should update
    @start_pos: QPoint starting position of drag
    @is_active: whether or not the user is currently manipulating a value
    '''
    def __init__(self, parent=None, value_mult='', height=50, width=None):
        super(LadderItem, self).__init__(parent)
        self.setText(str(value_mult))
        self.setValueMult(value_mult)
        self.default_stylesheet = self.styleSheet()
        self.setFixedHeight(height)
        self.setFixedWidth(width)
    
    def setValueMult(self, value_mult):
        self.value_mult = value_mult

    def getValueMult(self):
        return self.value_mult

    def setStartPos(self, pos):
        self.start_pos = pos

    def getStartPos(self):
        if not hasattr(self, 'start_pos'):
            self.start_pos = QCursor.pos()
        return self.start_pos

    def getIsActive(self):
        if not hasattr(self, 'is_active'):
            self.is_active = False
        return self.is_active

    def setIsActive(self, boolean):
        self.parent().setIsActive(boolean)
        self.is_active = boolean

    def updateColor(self, xpos):
        '''
        @xpos: floatf of single channel rgb color
        sets the style sheet to converge from left
        to right so that each full convergance will
        display another increment in value 
        '''
        '''
        # because Katana won't let me RGB this...
        style_sheet = "background-color: \
        qlineargradient( x1:%s y1:0, x2:%s y2:0, \
            stop:0 rgba(200,200,0,255), stop:1 rgba(100,200,100,255) \
        )" % (str(xpos), str(xpos + 0.01))
        
        style_sheet = "background-color: \
        qlineargradient( x1:%s y1:0, x2:%s y2:0, \
            stop:0 rgba(64,128,64,128) , stop:1 rgba(0,0,0,128) \
        )" % (str(xpos), str(xpos + 0.01))
        '''
        style_sheet = '''
        background: qlineargradient(
            x1:{xpos1} y1:0,
            x2:{xpos2} y2:0,
            stop:0 rgba({bgcolor}),
            stop:1 rgba({fgcolor})
        );
        '''.format(
                xpos1=str(xpos),
                xpos2=str(xpos + 0.01),
                bgcolor=self.parent().slide_color[0],
                fgcolor=self.parent().slide_color[1]
            )
        self.setStyleSheet(style_sheet)

    def resetColor(self):
        '''
        resets the color widget color back to default
        '''
        self.setStyleSheet(self.default_stylesheet)

    def enterEvent(self, *args, **kwargs):
        '''
        hack to set up hover color for QLabels
        '''
        self.setStyleSheet(
            'background-color: rgba({selected_color})'.format(
                selected_color=self.parent().selected_color)
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
        if the user selects the MMB it will start the click/drag operation
        '''
        #if event.button() == Qt.MiddleButton:
        pos = QCursor.pos()
        self.setStartPos(pos)
        self.tick_amount = 0
        self.setIsActive(True)
        return QLabel.mousePressEvent(self, event, *args, **kwargs)

    def mouseMoveEvent(self, event, *args, **kwargs):
        '''
        primary work horse for mouse movement slider
        '''
        MAGNITUDE_MULTIPLIER = self.parent().slide_distance
        if self.getIsActive() is True:
            # ===================================================================
            # get attrs
            # ===================================================================
            current_pos = QCursor.pos()
            start_pos = self.getStartPos()

            # ===================================================================
            # get magnitude
            # ===================================================================
            xoffset = start_pos.x() - current_pos.x()
            yoffset = start_pos.y() - current_pos.y()
            magnitude = math.sqrt(
                pow(xoffset, 2)
                + pow(yoffset, 2)
            )

            # ===================================================================
            # determine offset direction
            # ===================================================================
            offset = self.getValueMult()
            if xoffset > 0:
                offset = -self.getValueMult()
                magnitude *= -1
            magnitude *= MAGNITUDE_MULTIPLIER

            return_value = (int(magnitude) * self.getValueMult())

            # ===================================================================
            # update values
            # note: this will look for a change with tick_amount vs magnitude
            #         to determine when a full value changed has happened
            # ===================================================================
            # update value
            xpos = math.fabs(math.modf(magnitude)[0])
            if self.tick_amount != int(magnitude):
                self.parent().setValue(offset)
                self.tick_amount = int(magnitude)
            self.parent().updateWidgetGradients(xpos)
        return QLabel.mouseMoveEvent(self, event, *args, **kwargs)

    def mouseReleaseEvent(self, *args, **kwargs):
        self.setIsActive(False)
        self.parent().resetWidgetGradients()
        return QLabel.mouseReleaseEvent(self, *args, **kwargs)


''' TEST STUFF '''


class TestWidget(QLineEdit):
    def __init__(self, parent=None, value=0):
        super(TestWidget, self).__init__(parent)
        pos = QCursor().pos()
        self.setGeometry(pos.x(), pos.y(), 200, 100)
        self.value_list = [0.001, 0.01, 0.1, 1, 10, 100, 1000]

    def mousePressEvent(self, event, *args, **kwargs):
        '''
        trigger to active the popup menu
        '''
        if event.button() == Qt.MiddleButton:
            ladder = LadderDelegate(
                parent=self,
                widget=self,
                pos=self.pos(),
                value_list=self.value_list
            )
            ladder.show()
        return QLineEdit.mousePressEvent(self, event, *args, **kwargs)


#if __name__ == '__main__':
# tested line edit, label

print(__name__)

app = QApplication(sys.argv)
menu = TestWidget()
menu.show()
sys.exit(app.exec_())




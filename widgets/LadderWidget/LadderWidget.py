import sys

from qtpy.QtGui import *
from qtpy.QtWidgets import *
from qtpy.QtCore import *

from ...delegates import LadderDelegate

class LadderWidget(QLineEdit):
    '''
    @orig_value: float starting value of widget before opening of menu
    @value_mult: float how many units the drag should update
    @start_pos: QPoint starting position of drag
    @is_active: whether or not the user is currently manipulating a value
    '''
    def __init__(self, parent=None, value_mult='', height=50, width=None):
        super(LadderWidget, self).__init__(parent)
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
        '''
        style_sheet = "background-color: \
        qlineargradient( x1:%s y1:0, x2:%s y2:0, \
            stop:0 black, stop:1 green \
        )" % (str(xpos), str(xpos + 0.01))
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
        self.setStyleSheet('background-color: green')
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
        if event.button() == Qt.MiddleButton:
            pos = QCursor.pos()
            self.setStartPos(pos)
            self.tick_amount = 0
            self.setIsActive(True)
        return QLabel.mousePressEvent(self, event, *args, **kwargs)

    def mouseMoveEvent(self, event, *args, **kwargs):
        '''
        primary work horse for mouse movement slider
        '''
        MAGNITUDE_MULTIPLIER = .02
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
            # update color
            xpos = math.fabs(math.modf(magnitude)[0])
            if self.tick_amount != int(magnitude):
                self.parent().middle_widget.setValue(return_value)
                self.parent().getWidget().setValue(offset=offset)
                self.tick_amount = int(magnitude)
            self.parent().updateWidgetGradients(xpos)
        return QLabel.mouseMoveEvent(self, event, *args, **kwargs)

    def mouseReleaseEvent(self, *args, **kwargs):
        self.setIsActive(False)
        self.parent().resetWidgetGradients()
        return QLabel.mouseReleaseEvent(self, *args, **kwargs)


class TestWidget(QLabel):
    def __init__(self, parent=None, value=0):
        super(TestWidget, self).__init__(parent)
        pos = QCursor().pos()
        self.setGeometry(pos.x(), pos.y(), 200, 100)
        self.setValue(value)
        self.value_list = [0.001, 0.01, 0.1, 1, 10, 100, 1000]

    def setValue(self, value):
        self.setText(str(value))
        self.value = value

    def getValue(self):
        return self.value

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
        return QLabel.mousePressEvent(self, event, *args, **kwargs)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    menu = TestWidget()
    menu.show()
    sys.exit(app.exec_())

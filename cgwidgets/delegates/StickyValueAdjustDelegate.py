"""
Function to run?
Get original value...
set value...
"""

import math
import sys

from qtpy.QtCore import QEvent, Qt, QPoint, QRectF
from qtpy.QtWidgets import (
    QWidget, QApplication, QLabel, QDesktopWidget, QGraphicsItem
)
from qtpy.QtGui import QCursor

from cgwidgets.utils import getMagnitude


class iStickyValueAdjustDelegate(object):
    """
    Registers a click/drag even for the user.  By default this will
    automatically update the widget provided.  However custom functionality
    can be added by using the "setUpdateFunction" which will install a function
    to run during each mouse move event.

    By default this is setup to work with sticky drag.  Also there is no other option
    so... get used to it.  You're welcome.

    Attributes:
        pixels_per_tick (int): number of pixels the cursor must travel to register 1 tick
        value_per_tick (float): how much the original value should be modified per
            tick.
        orig_value (str): original value provided by the widget
        _dragging (bool): if the user is current in a click/drag event
        widget (QWidget): Widget to adjust.

    Notes:
        widget/item provided needs setValue method that will set the text/value
    """
    input_events = [
        QEvent.MouseButtonPress,
        QEvent.GraphicsSceneMousePress
    ]

    move_events = [
        QEvent.MouseMove,
        QEvent.GraphicsSceneMouseMove
    ]

    exit_events = [
        QEvent.Leave
    ]

    def __init__(self, widget=None):
        #super(iStickyValueAdjustDelegate, self).__init__(parent)
        self._pixels_per_tick = 100
        self._value_per_tick = 0.1
        self._dragging = False
        self.widget = widget

    """ PROPERTIES """
    def widget(self):
        return self._widget

    def setWidget(self, widget):
        self._widget = widget

    def valuePerTick(self):
        return self._value_per_tick

    def setValuePerTick(self, _value_per_tick):
        self._value_per_tick = _value_per_tick

    def pixelsPerTick(self):
        return self._pixels_per_tick

    def setPixelsPerTick(self, _pixels_per_tick):
        self._pixels_per_tick = _pixels_per_tick

    def updateOrigValue(self):
        try:
            orig_value = self.widget.getInput()
        except AttributeError:
            try:
                orig_value = self.widget.getValue()
            except AttributeError:
                orig_value = self.widget.text()
        self.setOrigValue(str(orig_value))

    def origValue(self):
        return self._orig_value

    def setOrigValue(self, orig_value):
        self._orig_value = orig_value

    def updateValue(self):
        """
        Sets the current value in the widget/item provided
        to the new value based off of how far the cursor has moved
        """
        new_value = self._num_ticks * self.valuePerTick()
        new_value += float(self.origValue())
        self.widget.setValue(new_value)

    def __updateFunction(self, original_value, slider_pos, num_ticks):
        """
        TODO:
            set this up...
        original_value (float)
        slider_pos (float)
        num_ticks (int)
        """
        pass
        #self.widget.setText(str(num_ticks))

    def updateFunction(self, slider_pos, num_ticks):
        return self.__updateFunction(self.origValue(), slider_pos, num_ticks)

    def setUpdateFunction(self, updateFunction):
        """
        This function will be required to take 3 args
            original_value, slider_pos, num_ticks
        """
        self.__updateFunction = updateFunction

    def stickyEventFilter(self, obj, event, *args, **kwargs):
        # pen down
        if event.type() in iStickyValueAdjustDelegate.input_events:
            """
            _calc_pos (QPoint): Position to calculate magnitude from
            _cursor_pos (QPoint): Original cursor click point
            _num_ticks (int): the number of ticks 
                value_mult * _num_ticks = value_offset
            """
            # setup default attrs
            self._calc_pos = QCursor.pos()
            self._cursor_pos = QCursor.pos()

            self._dragging = not self._dragging
            self._num_ticks = 0
            self.updateOrigValue()

            # toggle cursor display
            if self._dragging:
                obj.setCursor(Qt.BlankCursor)
            else:
                obj.unsetCursor()

        # pen move
        if event.type() in iStickyValueAdjustDelegate.move_events:
            if self._dragging:
                current_pos = QCursor.pos()
                magnitude = getMagnitude(self._calc_pos, current_pos)
                slider_pos, self._num_ticks = math.modf(magnitude / self.pixelsPerTick())

                # update values
                self.updateFunction(slider_pos, self._num_ticks)

                self.updateValue()

        # exit event
        if event.type() in iStickyValueAdjustDelegate.exit_events:
            # force this widget to never loser focus on drag
            if self._dragging:
                # update maths
                current_pos = QCursor.pos()
                offset = (current_pos - self._cursor_pos)
                self._calc_pos = self._calc_pos - offset

                # reset cursor position back to initial click position
                QCursor.setPos(self._cursor_pos)

        # cancel event with escape key
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Escape:
                obj.window().unsetCursor()
                self._dragging = False


class StickyValueAdjustWidgetDelegate(QWidget, iStickyValueAdjustDelegate):
    def __init__(self, parent=None, widget=None):
        super(StickyValueAdjustWidgetDelegate, self).__init__(parent)
        if not widget:
            widget = parent

        iStickyValueAdjustDelegate.__init__(self, widget=widget)

    def eventFilter(self, obj, event, *args, **kwargs):
        self.stickyEventFilter(obj, event, *args, **kwargs)
        return QWidget.eventFilter(self, obj, event, *args, **kwargs)


class TestFilter(QGraphicsItem):
    def __init__(self, parent=None):
        super(TestFilter, self).__init__(parent)


class StickyValueAdjustItemDelegate(QGraphicsItem, iStickyValueAdjustDelegate):
    def __init__(self, parent=None, widget=None):
        super(StickyValueAdjustItemDelegate, self).__init__(parent)
        if not widget:
            widget = parent

        iStickyValueAdjustDelegate.__init__(self, widget=widget)

    def boundingRect(self):
        return QRectF(0, 0, 0, 0)

    def paint(self, *args, **kwargs):
        return None

    def sceneEventFilter(self, obj, event, *args, **kwargs):
        self.stickyEventFilter(obj, event, *args, **kwargs)
        return True


class TestWidget(QLabel):
    def __init__(self, parent=None):
        super(TestWidget, self).__init__(parent)

    def setValue(self, value):
        self.setText(str(value))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    from cgwidgets.utils import installStickyValueAdjustWidgetDelegate
    w = TestWidget('1.0')
    ef = installStickyValueAdjustWidgetDelegate(w)
    ef.setValuePerTick(.001)
    ef.setPixelsPerTick(50)
    w.show()
    w.move(QCursor.pos())
    w.resize(100, 100)

    sys.exit(app.exec_())

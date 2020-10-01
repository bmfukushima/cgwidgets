"""
Function to run?
Get original value...
set value...
"""

import math
import sys

from qtpy.QtCore import QEvent, Qt, QPoint
from qtpy.QtWidgets import QWidget, QApplication, QLabel, QDesktopWidget
from qtpy.QtGui import QCursor

from cgwidgets.utils import getMagnitude


class StickyValueAdjustDelegate(QWidget):
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

    def __init__(self, parent=None, widget=None):
        super(StickyValueAdjustDelegate, self).__init__(parent)
        self._pixels_per_tick = 100
        self._value_per_tick = 0.1
        self._dragging = False
        if not widget:
            widget = parent
        self.widget = widget

    def eventFilter(self, obj, event, *args, **kwargs):
        # pen down
        if event.type() in StickyValueAdjustDelegate.input_events:
            """
            _calc_pos (QPoint): Position to calculate magnitude from
            _cursor_pos (QPoint): Original cursor click point
            _num_ticks (int): the number of ticks 
                value_mult * _num_ticks = value_offset
            """
            # setup default attrs
            self._calc_pos = obj.mapToGlobal(event.pos())
            self._cursor_pos = obj.mapToGlobal(event.pos())

            self._dragging = not self._dragging
            self._num_ticks = 0
            self.updateOrigValue()

            # toggle cursor display
            if self._dragging:
                obj.window().setCursor(Qt.BlankCursor)
            else:
                obj.window().unsetCursor()

        # pen move
        if event.type() in StickyValueAdjustDelegate.move_events:
            if self._dragging:
                current_pos = QCursor.pos()
                magnitude = getMagnitude(self._calc_pos, current_pos)
                slider_pos, self._num_ticks = math.modf(magnitude / self.pixelsPerTick())

                # update values
                self.updateFunction(slider_pos, self._num_ticks)

                self.updateValue()

        # exit event
        if event.type() in StickyValueAdjustDelegate.exit_events:
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

        return QWidget.eventFilter(self, obj, event, *args, **kwargs)

    """ PROPERTIES """
    def widget(self):
        return self._widget

    def setWidget(self, widget):
        self._widget = widget

    def valuePerTick(self):
        return self._value_per_tick

    def setPixelsPerTick(self, _value_per_tick):
        self._value_per_tick = _value_per_tick

    def pixelsPerTick(self):
        return self._pixels_per_tick

    def setPixelsPerTick(self, _pixels_per_tick):
        self._pixels_per_tick = _pixels_per_tick

    def updateOrigValue(self):
        try:
            orig_value = self.widget.getInput()
        except AttributeError:
            orig_value = self.widget.text()
        self.setOrigValue(str(orig_value))

    def origValue(self):
        return self._orig_value

    def setOrigValue(self, orig_value):
        self._orig_value = orig_value

    def updateValue(self):
        new_value = self._num_ticks * self.valuePerTick()
        self.widget.setText(str(new_value))

    def __updateFunction(self, original_value, slider_pos, num_ticks):
        """
        TODO:
            set this up...
        original_value (float)
        slider_pos (float)
        num_ticks (int)
        """

        self.widget.setText(str(num_ticks))

    def updateFunction(self, slider_pos, num_ticks):
        return self.__updateFunction(self.origValue(), slider_pos, num_ticks)

    def setUpdateFunction(self, updateFunction):
        """
        This function will be required to take 3 args
            original_value, slider_pos, num_ticks
        """
        self.__updateFunction = updateFunction


def installStickyValueAdjustDelegate(widget):
    widget.setMouseTracking(True)
    ef = StickyValueAdjustDelegate(widget)
    widget.installEventFilter(ef)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = QLabel('1.0')
    installStickyValueAdjustDelegate(w)
    w.show()
    w.move(QCursor.pos())
    w.resize(100, 100)

    sys.exit(app.exec_())

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
    can be added by using the "setUserUpdateFunction" which will install a function
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
        QEvent.Leave,
        QEvent.GraphicsSceneHoverLeave,
        QEvent.DragLeave
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
        #print('setting orig value to %s'%orig_value)
        self.setOrigValue(str(orig_value))

    def origValue(self):
        return self._orig_value

    def setOrigValue(self, orig_value):
        self._orig_value = orig_value

    """ VALUE UPDATERS / SETTERS"""
    def __setValue(self):
        """
        This function is run to update the value on the parent widget.
        This will update the value on the widget, and then run
        the userUpdateFunction
        """
        current_pos = QCursor.pos()
        magnitude = getMagnitude(self._calc_pos, current_pos)
        slider_pos, self._num_ticks = math.modf(magnitude / self.pixelsPerTick())

        # update values
        self.userUpdateFunction(slider_pos, self._num_ticks)
        self.updateValue()

    def updateValue(self):
        """
        Sets the current value on the widget/item provided
        to the new value based off of how far the cursor has moved
        """
        new_value = self._num_ticks * self.valuePerTick()
        new_value += float(self.origValue())
        # print(self.widget, new_value)
        self.widget.setValue(new_value)

    def __userUpdateFunction(self, original_value, slider_pos, num_ticks):
        """
        original_value (float)
        slider_pos (float)
        num_ticks (int)
        """
        pass
        #self.widget.setText(str(num_ticks))

    def userUpdateFunction(self, slider_pos, num_ticks):
        return self.__userUpdateFunction(self.origValue(), slider_pos, num_ticks)

    def setUserUpdateFunction(self, userUpdateFunction):
        """
        This takes one function which should be run when ever the value
        is changed during a slide event.

        This function will be required to take 3 args
            original_value, slider_pos, num_ticks
        """
        self.__userUpdateFunction = userUpdateFunction

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
                # TODO blank cursor
                obj.setCursor(Qt.BlankCursor)
            else:
                obj.unsetCursor()

        # pen move
        if event.type() in iStickyValueAdjustDelegate.move_events:
            if self._dragging:
                self.__setValue()

        # exit event
        if event.type() in iStickyValueAdjustDelegate.exit_events:
            # force this widget to never loser focus on drag
            if self._dragging:
                # update maths
                current_pos = QCursor.pos()
                offset = (current_pos - self._cursor_pos)
                self._calc_pos = self._calc_pos - offset

                # update value
                self.__setValue()

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
        item = obj
        obj = obj.scene().views()[0]
        # pen press
        if event.type() in iStickyValueAdjustDelegate.input_events:
            """
            _calc_pos (QPoint): Position to calculate magnitude from
            _cursor_pos (QPoint): Original cursor click point
            _num_ticks (int): the number of ticks 
                value_mult * _num_ticks = value_offset
            """
            # setup default attrs
            obj._calc_pos = QCursor.pos()
            obj._cursor_pos = QCursor.pos()
            obj._dragging = not obj._dragging
            self._num_ticks = 0
            self.updateOrigValue()

            # toggle cursor display
            if obj._dragging:
                obj.setCursor(Qt.BlankCursor)
                obj._current_item = item
            else:
                pass
                obj.unsetCursor()
            return True

        # pen move
        if event.type() in iStickyValueAdjustDelegate.move_events:
            if obj._dragging:
                current_pos = QCursor.pos()
                magnitude = getMagnitude(obj._calc_pos, current_pos)
                slider_pos, self._num_ticks = math.modf(magnitude / self.pixelsPerTick())

                # update values
                self.userUpdateFunction(slider_pos, self._num_ticks)
                self.updateValue()

        # exit event
        if event.type() in iStickyValueAdjustDelegate.exit_events:
            # force this widget to never loser focus on drag
            if obj._dragging:
                # update maths
                current_pos = QCursor.pos()
                offset = (current_pos - obj._cursor_pos)
                obj._calc_pos = obj._calc_pos - offset

                # reset cursor position back to initial click position
                QCursor.setPos(obj._cursor_pos)

        # cancel event with escape key
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Escape:
                obj.unsetCursor()
                obj._dragging = False

        return True
    # def sceneEventFilter(self, obj, event, *args, **kwargs):
    #     #self.stickyEventFilter(obj, event, *args, **kwargs)
    #     return True


""" TESTING """
from qtpy.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsLineItem,
QGraphicsEllipseItem
)
from qtpy.QtGui import QColor, QBrush
from cgwidgets.utils import installStickyValueAdjustItemDelegate, installStickyValueAdjustWidgetDelegate

class TestWidget(QLabel):
    def __init__(self, parent=None):
        super(TestWidget, self).__init__(parent)
        self.setText('0')
    def setValue(self, value):
        self.setText(str(value))


class StickyValueAdjustViewDelegate(QWidget):
    def __init__(self, parent=None, widget=None):
        super(StickyValueAdjustViewDelegate, self).__init__(parent)
        iStickyValueAdjustDelegate.__init__(self, widget=widget)
        self.setMouseTracking(True)

    def eventFilter(self, obj, event, *args, **kwargs):
        # pen down
        if event.type() == QEvent.MouseButtonPress:
            if obj._dragging is True:
                obj._dragging = False
                QCursor.setPos(obj._cursor_pos)
                obj.unsetCursor()
                return False

        # mouse move
        if event.type() == QEvent.MouseMove:
            if obj._dragging is True:
                current_pos = QCursor.pos()
                magnitude = getMagnitude(obj._calc_pos, current_pos)
                slider_pos, obj._current_item.event_filter._num_ticks = math.modf(magnitude / obj._current_item.event_filter.pixelsPerTick())

                # update values
                obj._current_item.event_filter.userUpdateFunction(slider_pos, obj._current_item.event_filter._num_ticks)
                obj._current_item.event_filter.updateValue()

        # mouse leave
        if event.type() == QEvent.Leave:
            # force this widget to never loser focus on drag
            if obj._dragging:
                # update maths
                current_pos = QCursor.pos()
                offset = (current_pos - obj._cursor_pos)
                obj._calc_pos = obj._calc_pos - offset

                # reset cursor position back to initial click position
                QCursor.setPos(obj._cursor_pos)

        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Escape:
                if obj._dragging is True:
                    QCursor.setPos(obj._cursor_pos)
                    obj.unsetCursor()
                    obj._dragging = False
                    #return True

        return QWidget.eventFilter(self, obj, event, *args, **kwargs)


class TestWidgetItem(QGraphicsView):
    def __init__(self, parent=None):
        super(TestWidgetItem, self).__init__(parent)
        scene = QGraphicsScene()
        self.setScene(scene)

        self.line_item = QGraphicsLineItem()
        self.line_item.setLine(0, 0, 10, 10)

        self.circle_item = CenterManipulatorItem()
        self.circle_item.setRect(10, 10, 50, 50)

        self.scene().addItem(self.circle_item)
        self.scene().addItem(self.line_item)

        self.scene().setSceneRect(0,0,100,100)

        self._dragging = False

        self.setMouseTracking(True)


    def mouseMoveEvent(self, event):
        event.ignore()
        QGraphicsView.mouseMoveEvent(self, event)


class CenterManipulatorItem(QGraphicsEllipseItem):
    def __init__(self, parent=None):
        super(CenterManipulatorItem, self).__init__(parent)
        # pen = self.pen()
        # pen.setStyle(Qt.NoPen)
        # pen.setWidth(0)
        # self.setPen(pen)
        self.value = 1

    def setColor(self, color=QColor(255, 0, 0)):
        self.setBrush(QBrush(color))

    def setValue(self, value):
        # print(value)
        self.value = value

    def getValue(self):
        return self.value


class LineItem(QGraphicsLineItem):
    def __init__(self, parent=None):
        super(CenterManipulatorItem, self).__init__(parent)
        self.setLine(0,0, 25,25)
        self.value = 1

    def setColor(self, color=QColor(255, 0, 0)):
        self.setBrush(QBrush(color))

    def setValue(self, value):
        self.value = value

    def getValue(self):
        return self.value


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # w = TestWidgetItem()
    # ef = installStickyValueAdjustItemDelegate(w.circle_item)

    def testUpdate(original_value, slider_pos, num_ticks):
        print('original_value == %s'%original_value)
        print('slider pos == %s'%slider_pos)
        print('num_ticks == %s'%num_ticks)
    w = TestWidget()

    ef = installStickyValueAdjustWidgetDelegate(w)
    #ef.setUserUpdateFunction(testUpdate)

    # ef.setValuePerTick(.001)
    # ef.setPixelsPerTick(50)

    w.show()
    w.move(QCursor.pos())
    w.resize(100, 100)

    sys.exit(app.exec_())

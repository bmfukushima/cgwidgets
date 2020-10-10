"""
Function to run?
Get original value...
set value...
"""

import math
import sys
import logging

from qtpy.QtCore import QEvent, Qt, QPoint, QRectF
from qtpy.QtWidgets import (
    QWidget, QApplication, QLabel, QDesktopWidget, QGraphicsItem, QFrame
)
from qtpy.QtGui import QCursor

from cgwidgets.utils import getMagnitude, getTopLeftPos, setAsTransparent, setAsTool
from cgwidgets.settings.colors import iColor


class iStickyValueAdjustDelegate(object):
    """
    The interface for all of the sticky drag delegates, by default they will
    registers a click/drag event for the user and will
    automatically update the widget provided.  However custom functionality
    can be added by using the "setUserUpdateFunction" which will install a function
    to run during each mouse move event.

    Attributes:
        pixels_per_tick (int): number of pixels the cursor must travel to register 1 tick
        value_per_tick (float): how much the original value should be modified per
            tick.
        orig_value (str): original value provided by the widget
        _drag_STICKY (bool): if the user is current in a click/drag event
        widget (QWidget): Widget to adjust.

    Notes:
        - widget/item provided needs setValue method that will set the text/value
        - if you want the live update to work on InputWidgets, you'll need to toggle the
            _updating attr on the input widget.
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

    def __init__(self):
        self._pixels_per_tick = 200
        self._value_per_tick = 0.1
        self._updating = False

    """ PROPERTIES """
    def valuePerTick(self):
        return self._value_per_tick

    def setValuePerTick(self, _value_per_tick):
        self._value_per_tick = _value_per_tick

    def pixelsPerTick(self):
        return self._pixels_per_tick

    def setPixelsPerTick(self, _pixels_per_tick):
        self._pixels_per_tick = _pixels_per_tick


class iStickyActivationDelegate(object):
    """
    Interface for the activation objects
    """
    def penDownEvent(self, activation_obj):
        """
        Event to be run when the user clicks on the activation widget.
        This will enable the activation of the sticky drag.

        Args:
            obj (QWidget): Activation Widget
        """
        # get widgets
        drag_widget = activation_obj._sticky_widget_data['drag_widget']
        active_object = activation_obj._sticky_widget_data['active_object']

        # setup drag attrs
        drag_widget.setActiveWidget(active_object)
        drag_widget.setActivationWidget(activation_obj)

        # activate sticky drag
        self.__activateStickyDrag(drag_widget)

        # show invisible widget ( yeah I know how it sounds )
        drag_widget.show()

    def __activateStickyDrag(self, obj):
        """
        This should be run every time the user clicks.

        Args:
            obj (QWidget / QItem --> DragWidget): Object to install all of the extra attrs on
        """
        obj._cursor_pos = QCursor.pos()
        top_left = getTopLeftPos(obj)
        QCursor.setPos(top_left + QPoint(10, 10))
        obj.setFocus()

        # set up drag time attrs
        obj.updateOrigValue()
        obj._calc_pos = QCursor.pos()
        obj._drag_STICKY = not obj._drag_STICKY
        obj._num_ticks = 0

        obj._value_per_tick = self.valuePerTick()

        # toggle cursor display
        if obj._drag_STICKY:
            obj.setCursor(Qt.BlankCursor)


class StickyValueAdjustWidgetDelegate(QWidget, iStickyActivationDelegate, iStickyValueAdjustDelegate):
    def __init__(self, parent=None):
        super(StickyValueAdjustWidgetDelegate, self).__init__(parent)
        iStickyValueAdjustDelegate.__init__(self)

    def eventFilter(self, activation_obj, event, *args, **kwargs):
        # activate
        if event.type() in iStickyValueAdjustDelegate.input_events:
            self.penDownEvent(activation_obj)
            return False

        return False


class StickyValueAdjustItemDelegate(QGraphicsItem, iStickyActivationDelegate, iStickyValueAdjustDelegate):
    def __init__(self, parent=None):
        super(StickyValueAdjustItemDelegate, self).__init__(parent)
        iStickyValueAdjustDelegate.__init__(self)

    def boundingRect(self):
        return QRectF(0, 0, 0, 0)

    def paint(self, *args, **kwargs):
        return None

    def sceneEventFilter(self, activation_obj, event, *args, **kwargs):
        # get widgets
        if event.type() in iStickyValueAdjustDelegate.input_events:
            self.penDownEvent(activation_obj)
            return False

        return False


class StickyDragWindowWidget(QFrame, iStickyValueAdjustDelegate):
    """
    Main window that is shown when the user enters a sticky drag event...
    This will be invisible to the user.
    """
    def __init__(self, parent=None):
        super(StickyDragWindowWidget, self).__init__(parent)
        # setup default attrs
        self._orig_value = 0
        self._updating = False
        self._drag_STICKY = False
        self.setMouseTracking(True)

        # setup display attrs
        self.hide()
        setAsTool(self)
        setAsTransparent(self)

    """ PROPERTIES """
    def activeWidget(self):
        return self._active_object

    def setActiveWidget(self, _active_object):
        self._active_object = _active_object

    def activationWidget(self):
        return self._activation_object

    def setActivationWidget(self, _activation_object):
        self._activation_object = _activation_object

    def origValue(self):
        return self._orig_value

    def updateOrigValue(self):
        """
        Returns the current value as a string.  This should be run when a
        click drag event is started
        """
        try:
            orig_value = self.activeWidget().getInput()
        except AttributeError:
            try:
                orig_value = self.activeWidget().getValue()
            except AttributeError:
                orig_value = self.activeWidget().text()

        self._orig_value = float(orig_value)
    """ UTILS """
    def __deactivateStickyDrag(self):
        self._drag_STICKY = False
        self.unsetCursor()
        self.hide()

    """ VALUE UPDATERS / SETTERS"""
    def __setValue(self):
        """
        This function is run to update the value on the parent widget.
        This will update the value on the widget, and then run
        the userUpdateFunction
        """
        current_pos = QCursor.pos()
        magnitude = getMagnitude(self._calc_pos, current_pos)
        self._slider_pos, self._num_ticks = math.modf(magnitude / self.pixelsPerTick())

        # update values
        self.userUpdateFunction()
        self.__updateValue()

    def __updateValue(self):
        """
        Sets the current value on the widget/item provided
        to the new value based off of how far the cursor has moved
        """
        new_value = self._num_ticks * self.valuePerTick()
        new_value += float(self._orig_value)
        logging.debug(new_value)
        self.activeWidget().setValue(new_value)

    def __userUpdateFunction(self, obj, original_value, slider_pos, num_ticks):
        """
        obj (QWidget): the widget that should have its values manipulated
        original_value (float)
        slider_pos (float)
        num_ticks (int)
        """
        pass

    def userUpdateFunction(self):
        obj = self.activeWidget()
        return self.__userUpdateFunction(obj, self._orig_value, self._slider_pos, self._num_ticks)

    def setUserUpdateFunction(self, userUpdateFunction):
        """
        This takes one function which should be run when ever the value
        is changed during a slide event.

        This function will be required to take 3 args
            original_value, slider_pos, num_ticks
        """
        self.__userUpdateFunction = userUpdateFunction

    """ EVENTS """
    def leaveEvent(self, event, *args, **kwargs):
        current_pos = QCursor.pos()
        offset = (current_pos - self._cursor_pos)
        self._calc_pos = self._calc_pos - offset

        # reset cursor
        QCursor.setPos(self._cursor_pos)

        # update value
        self.__setValue()
        return QFrame.leaveEvent(self, event, *args, **kwargs)

    def mouseMoveEvent(self, event, *args, **kwargs):
        self.__setValue()
        QFrame.mouseMoveEvent(self, event, *args, **kwargs)

    def mousePressEvent(self, event):
        self.__deactivateStickyDrag()
        return QFrame.mousePressEvent(self, event)

    def showEvent(self, event):
        offset = 100
        screen_resolution = QApplication.desktop().screenGeometry()
        width, height = screen_resolution.width() - (offset*2), screen_resolution.height() - (offset*2)
        self.setFixedSize(width, height)
        self.move(offset, offset)
        return QFrame.showEvent(self, event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.__deactivateStickyDrag()


""" TESTING """
from qtpy.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsLineItem,
QGraphicsEllipseItem, QGraphicsTextItem
)
from qtpy.QtGui import QColor, QBrush, QPen


class TestWidget(QLabel):
    def __init__(self, parent=None):
        super(TestWidget, self).__init__(parent)
        self.setText('5')

    def setValue(self, value):
        self.setText(str(value))


class TestWidgetItem(QGraphicsView):
    def __init__(self, parent=None):
        super(TestWidgetItem, self).__init__(parent)
        scene = QGraphicsScene()
        self.setScene(scene)

        self.line_item = LineItem()
        self.line_item.setLine(0, 0, 10, 10)

        self.line_item2 = LineItem()
        self.line_item2.setLine(30, 30, 40, 40)

        self.circle_item = CenterManipulatorItem()
        self.circle_item.setRect(10, 10, 50, 50)

        self.text_item = TextItem()

        self.scene().addItem(self.text_item)
        self.scene().addItem(self.circle_item)
        self.scene().addItem(self.line_item)
        self.scene().addItem(self.line_item2)

        self.scene().setSceneRect(0,0,100,100)
        self.setMouseTracking(True)

    def mouseReleaseEvent(self, event):
        event.ignore()
        QGraphicsView.mouseReleaseEvent(self, event)

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
        self.value = value

    def getValue(self):
        return self.value


class LineItem(QGraphicsLineItem):
    def __init__(self, parent=None):
        super(LineItem, self).__init__(parent)
        self.setLine(0, 0, 25, 25)
        self.value = 1
        self.setSize(15, 15)

    def setSize(self, width, height, hand_width=4):
        """
        width (int): this is how wide the slider is.  This is the length
            parallel to the hand
        height (int): how tall the slider is, this is the size going down
            the same axis as the hand
        """

        self.setLine(
            (-width * 0.5) - (hand_width * 2), 0,
            width + hand_width, 0
        )
        pen = QPen()
        pen.setWidth(height)
        self.setPen(pen)

    def setColor(self, color=QColor(255, 0, 0)):
        self.setBrush(QBrush(color))

    def setValue(self, value):
        self.value = value

    def getValue(self):
        return self.value


class TextItem(QGraphicsTextItem):
    def __init__(self, parent=None):
        super(TextItem, self).__init__(parent)
        self.setValue("12.0")

    def setValue(self, value):
        self._value = float(value)
        self.setPlainText(str(value))

    def getValue(self):
        return self._value


def testWidget():
   # double delegate use case

    w = QWidget()
    l = QVBoxLayout(w)
    w2 = TestWidget()
    w3 = QLabel('test')
    l.addWidget(w2)
    l.addWidget(w3)

    # todo fix invisible widget not allowing clicking?
    #installInvisibleWidgetEvent(w2, activation_object=w3)
    #ef = installStickyAdjustDelegate(w2, drag_widget=w3, activation_object=w3)

    # simple use case


    #installInvisibleWidgetEvent(w2)
    from cgwidgets.utils import installStickyAdjustDelegate
    ef = installStickyAdjustDelegate(w2, value_per_tick=.01, activation_object=w3)

    # #example user update functino
    # ef.setUserUpdateFunction(testUpdate)

    # ef.setValuePerTick(.001)
    # ef.setPixelsPerTick(50)

    return w


def testItem():
    w = TestWidgetItem()

    ef = installStickyAdjustDelegate(w.line_item, pixels_per_tick=100, value_per_tick=0.01)
    ef = installStickyAdjustDelegate(w.line_item2, pixels_per_tick=100, value_per_tick=0.01)
    return w


if __name__ == '__main__':
    from qtpy.QtWidgets import QVBoxLayout
    from cgwidgets.utils import installInvisibleWidgetEvent
    from cgwidgets.utils import installStickyAdjustDelegate
    app = QApplication(sys.argv)
    logging.basicConfig(level=logging.DEBUG)


    def testUpdate(obj, original_value, slider_pos, num_ticks):
        print('obj == %s'%obj)
        print('original_value == %s'%original_value)
        print('slider pos == %s'%slider_pos)
        print('num_ticks == %s'%num_ticks)

    # test_widget = testWidget()
    # test_widget.show()
    # test_widget.move(QCursor.pos())
    # test_widget.resize(100, 100)

    test_view = testItem()

    test_view.show()
    test_view.move(QCursor.pos())
    test_view.resize(100, 100)

    sys.exit(app.exec_())

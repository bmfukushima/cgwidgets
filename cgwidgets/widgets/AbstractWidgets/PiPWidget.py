"""
Todo:
    * show event overlapping oddly
    * add / remove widgets dynamically?
        Add a delegate?
    * add special handler for only 1, 2, 3+ widgets
        AbstractPiPWidget --> resizeMiniViewer
    * PiPMiniViewerWidget --> Borders... styles not working???
        - base style sheet added to ShojiLayout...
            in general the shoji layout needs to be more flexible
"""

from qtpy.QtWidgets import (
    QStackedLayout, QWidget, QBoxLayout, QVBoxLayout, QLabel)
from qtpy.QtCore import QEvent, Qt

from cgwidgets.utils import attrs, getWidgetUnderCursor, isWidgetDescendantOf, getWidgetAncestor
from cgwidgets.settings.hover_display import installHoverDisplaySS, removeHoverDisplay
from cgwidgets.settings.colors import iColor

from cgwidgets.widgets.AbstractWidgets.AbstractLabelledInputWidget import AbstractLabelledInputWidget
from cgwidgets.widgets.AbstractWidgets.AbstractOverlayInputWidget import AbstractOverlayInputWidget

class AbstractPiPWidget(QWidget):
    """
    The PiPWidget is designed to display multiple widgets simultaneously to the user.

    Similar to the function that was provided to TV's in the mid 1970's.  This widget is
    designed to allow the user to create multiple hot swappable widgets inside of the same
    widget.

    Args:

    Attributes:
        current_widget (QWidget): the widget that is currently set as the main display
        direction (attrs.DIRECTION): what side the mini viewer will be displayed on.
        pip_size (float): fractional percentage of the amount of space that the mini viewer
            will take up in relation to the overall size of the widget.
        swap_mode (PiPWidget.SWAP): when the widget will be swapped
        swap_key (Qt.KEY): When the swap_mode is set to KEY_PRESS, this key will trigger the
            popup
        widgets (list): of widgets

    Hierarchy:
        |- QVBoxLayout
        |    |- PiPMainViewer (QWidget)
        |- MiniViewer (QWidget)
            |- QBoxLayout
                |-* PiPMiniViewerWidget --> QWidget
                        |- QVBoxLayout
                        |- AbstractLabelledInputWidget

    Signals:
        Swap (Enter):
            PiPMiniViewer --> EventFilter --> EnterEvent
                - swap widget
                - freeze swapping (avoid recursion)
            PiPMiniViewer --> LeaveEvent
                - unfreeze swapping
        Swap (Key Press):
            AbstractPiPWidget --> keyPressEvent --> setCurrentWidget
        HotSwap (Key Press 1-5):
            AbstractPiPWidget --> keyPressEvent --> setCurrentWidget
        Toggle previous widget
            AbstractPiPWidget --> keyPressEvent --> swapWidgets

    """

    ENTER = 0
    KEY_PRESS = 1

    def __init__(self, parent=None, swap_mode=None):
        super(AbstractPiPWidget, self).__init__(parent)

        # setup attrs
        self._widgets = []
        self._current_widget = None
        self._previous_widget = None
        self._pip_size = 0.35
        self._direction = attrs.SOUTH
        self._swap_key = 96
        if not swap_mode:
            swap_mode = AbstractPiPWidget.KEY_PRESS

        # create widgets
        self.main_viewer = PiPMainViewer(self)
        self.mini_viewer = PiPMiniViewer(self, swap_mode=swap_mode)
        # self.mini_viewer.setStyleSheet("background-color: rgba(0,255,0,255)")

        # create layout
        """
        Not using a stacked layout as the enter/leave events get borked
        """
        #QStackedLayout(self)
        QVBoxLayout(self)
        #self.layout().setStackingMode(QStackedLayout.StackAll)
        self.layout().addWidget(self.main_viewer)
        #self.layout().addWidget(self.mini_viewer)

    """ UTILS (SWAP) """
    def swapWidgets(self):
        """
        Swaps the previous widget with the current widget.

        This allows the user to quickly swap between two widgets.
        """
        if self.previousWidget():
            self.setCurrentWidget(self.previousWidget())

    def swapMode(self):
        return self.mini_viewer.swapMode()

    def setSwapMode(self, swap_mode):
        self.mini_viewer.setSwapMode(swap_mode)

    def swapKey(self):
        return self._swap_key

    def setSwapKey(self, key):
        self._swap_key = key

    """ UTILS """
    def pipSize(self):
        return self._pip_size

    def setPiPSize(self, pip_size):
        self._pip_size = pip_size
        self.resizeMiniViewer()

    def showWidgetNames(self, enabled):
        for widget in self.widgets():
            if enabled:
                widget.main_widget.viewWidget().show()
            else:
                widget.main_widget.viewWidget().hide()
                pass

    """ WIDGETS """
    def addWidget(self, widget, name=""):
        if 0 < len(self.widgets()):
            mini_widget = self.mini_viewer.createNewWidget(widget, name=name)
        else:
            mini_widget = PiPMiniViewerWidget(self, direction=Qt.Vertical, delegate_widget=widget, name=name)
            self.setCurrentWidget(mini_widget)

        self.widgets().append(mini_widget)
        self.resizeMiniViewer()

    def removeWidget(self, widget):
        self.widgets().remove(widget)
        widget.setParent(None)
        widget.deleteLater()

    def widgets(self):
        return self._widgets

    def currentWidget(self):
        return self._current_widget

    def setCurrentWidget(self, widget):
        """
        Sets the current full screen widget

        Args:
            widget (QWidget): widget to be set as full screen
        """
        # reset current widget
        if self._current_widget:
            self._current_widget.setParent(None)
            self.mini_viewer.addWidget(self._current_widget)
            self.setPreviousWidget(self._current_widget)

        # set widget as current
        self._current_widget = widget
        self.mini_viewer.removeWidget(widget)
        self.main_viewer.setWidget(widget)

    def previousWidget(self):
        return self._previous_widget

    def setPreviousWidget(self, widget):
        self._previous_widget = widget

    """ DIRECTION """
    def direction(self):
        return self._direction

    def setDirection(self, direction):
        self._direction = direction
        if direction in [attrs.EAST, attrs.WEST]:
            self.mini_viewer.setDirection(QBoxLayout.TopToBottom)
        elif direction in [attrs.NORTH, attrs.SOUTH]:
            self.mini_viewer.setDirection(QBoxLayout.LeftToRight)

    def resizeMiniViewer(self):
        """
        Main function for resizing the mini viewer
        """
        w = self.width()
        h = self.height()
        pip_offset = 1 - self.pipSize()
        # set position
        if self.direction() in [attrs.EAST, attrs.WEST]:
            height = h
            width = w * self.pipSize()

            if self.direction() == attrs.EAST:
                ypos = 0
                xpos = 0
            if self.direction() == attrs.WEST:
                ypos = 0
                xpos = w * pip_offset

        if self.direction() in [attrs.NORTH, attrs.SOUTH]:
            height = h * self.pipSize()
            width = w
            if self.direction() == attrs.SOUTH:
                xpos = 0
                ypos = h * pip_offset
            if self.direction() == attrs.NORTH:
                xpos = 0
                ypos = 0

        # move/resize mini viewer
        self.mini_viewer.move(int(xpos), int(ypos))
        self.mini_viewer.resize(int(width), int(height))

    """ EVENTS """
    def resizeEvent(self, event):
        self.resizeMiniViewer()

        return QWidget.resizeEvent(self, event)

    def keyPressEvent(self, event):
        # swap between this and previous
        if event.key() == 96:
            # pre flight
            widget = getWidgetUnderCursor()
            if widget == self.mini_viewer: return

            # swap previous widget widgets
            is_descendant_of_main_viewer = isWidgetDescendantOf(widget, self.currentWidget())
            if widget == self or is_descendant_of_main_viewer:
                self.swapWidgets()
                return QWidget.keyPressEvent(self, event)

            # set widget under cursor as current
            is_descendant_of_mini_viewer = isWidgetDescendantOf(widget, self.mini_viewer)
            if is_descendant_of_mini_viewer:
                if self.swapMode() == AbstractPiPWidget.KEY_PRESS:
                    swap_widget = getWidgetAncestor(widget, PiPMiniViewerWidget)
                    self.setCurrentWidget(swap_widget)
                    return QWidget.keyPressEvent(self, event)

        # hotkey swapping
        if event.key() in [Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4, Qt.Key_5]:
            try:
                if event.key() == Qt.Key_1:
                    widget = self.mini_viewer.layout().itemAt(0).widget()
                if event.key() == Qt.Key_2:
                    widget = self.mini_viewer.layout().itemAt(1).widget()
                if event.key() == Qt.Key_3:
                    widget = self.mini_viewer.layout().itemAt(2).widget()
                if event.key() == Qt.Key_4:
                    widget = self.mini_viewer.layout().itemAt(3).widget()
                if event.key() == Qt.Key_5:
                    widget = self.mini_viewer.layout().itemAt(4).widget()
                self.setCurrentWidget(widget)

            except AttributeError:
                # not enough widgets
                pass
        return QWidget.keyPressEvent(self, event)


class PiPMainViewer(QWidget):
    def __init__(self, parent=None):
        super(PiPMainViewer, self).__init__(parent)
        QVBoxLayout(self)

    def setWidget(self, widget):
        self.layout().addWidget(widget)


class PiPMiniViewer(QWidget):
    def __init__(self, parent=None, swap_mode=None):
        super(PiPMiniViewer, self).__init__(parent)
        QBoxLayout(QBoxLayout.LeftToRight, self)

        if not swap_mode:
            swap_mode = AbstractPiPWidget.KEY_PRESS
        self._swap_mode = swap_mode
        self._widgets = []
        self._is_frozen = False

    def swapMode(self):
        return self._swap_mode

    def setSwapMode(self, swap_mode):
        self._swap_mode = swap_mode

    """ EVENTS """
    def eventFilter(self, obj, event):
        # set up PiP Swap on ENTER
        if event.type() in [QEvent.DragEnter, QEvent.Enter]:
            if not self._is_frozen:
                if self.swapMode() == AbstractPiPWidget.ENTER:
                    from cgwidgets.utils import getWidgetAncestor
                    main_widget = getWidgetAncestor(self, AbstractPiPWidget)
                    main_widget.setCurrentWidget(obj)
                    self._is_frozen = True
        return False

    def leaveEvent(self, event):
        # enable swapping again
        if self.swapMode() == AbstractPiPWidget.ENTER:
            self._is_frozen = False
        return QWidget.leaveEvent(self, event)

    """ DIRECTION """
    def setDirection(self, direction):
        self.layout().setDirection(direction)

    """ WIDGETS """
    def addWidget(self, widget):
        self.layout().addWidget(widget)
        widget.installEventFilter(self)

        # installHoverDisplaySS(
        #     widget,
        #     name="PIP")

    def createNewWidget(self, widget, name=""):
        """
        Creates a new widget in the mini widget.  This is only when a new widget needs to be instantiated.

        Args:
            widget:
            name:

        Returns (PiPMiniViewerWidget):
        """
        mini_widget = PiPMiniViewerWidget(self, direction=Qt.Vertical, delegate_widget=widget, name=name)

        self.layout().addWidget(mini_widget)
        mini_widget.installEventFilter(self)

        return mini_widget

    def removeWidget(self, widget):
        self.layout().removeWidget(widget)
        widget.removeEventFilter(self)

    # def widgets(self):
    #     self.layout().children()


class PiPMiniViewerWidget(QWidget):
    def __init__(
        self,
        parent=None,
        name="None",
        direction=Qt.Horizontal,
        delegate_widget=None,
    ):
        super(PiPMiniViewerWidget, self).__init__(parent)
        QVBoxLayout(self)
        self.main_widget = AbstractLabelledInputWidget(self, name=name, direction=direction, delegate_widget=delegate_widget)
        self.layout().addWidget(self.main_widget)

        base_style_sheet = """
        {type}{{
            background-color: rgba{rgba_background};
            color: rgba{rgba_text};
            border: 2px solid rgba{rgba_border};
        }}""".format(
            rgba_background=repr(self.main_widget.rgba_background),
            rgba_border=iColor["rgba_background_01"],
            rgba_text=repr(self.main_widget.rgba_text),
            type=type(self.main_widget).__name__,
        )
        self.main_widget.setBaseStyleSheet(base_style_sheet)
        # installHoverDisplaySS(self, "TEST")


if __name__ == '__main__':
    import sys
    from qtpy.QtWidgets import (QApplication)
    from cgwidgets.utils import centerWidgetOnCursor
    app = QApplication(sys.argv)

    widget = AbstractPiPWidget()
    widget.setDirection(attrs.SOUTH)
    for x in range(4):
        child = QLabel(str(x))
        child.setAlignment(Qt.AlignCenter)
        child.setStyleSheet("color: rgba(255,255,255,255);")
        widget.addWidget(child)
    widget.show()
    widget.showWidgetNames(False)
    centerWidgetOnCursor(widget)
    widget.resize(512, 512)
    sys.exit(app.exec_())
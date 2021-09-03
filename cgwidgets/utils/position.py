import math

from qtpy.QtWidgets import *
from qtpy.QtCore import *
from qtpy.QtGui import *

class LayoutOrientation(object):
    """
    Sets the orientation for a widget.

    This will create a QBoxLayout and set that as the main layout.

    Attributes:
        orientation (Qt.ORIENTATION): default is Qt.Vertical
            Qt.Vertical | Qt.Horizontal

    Virtual:
        orientationChangeEvent (Qt.ORIENTATION): function to be run
            when setOrientation is called.  Please note that this will
            run AFTER the orientation has been set.
    """
    def __init__(self, orientation=Qt.Vertical):
        self._layout_orientation = orientation
        if orientation == Qt.Vertical:
            QBoxLayout(QBoxLayout.TopToBottom, self)
        if orientation == Qt.Horizontal:
            QBoxLayout(QBoxLayout.LeftToRight, self)

        self.setLayoutOrientation(orientation)

    """ PROPERTIES """
    def layoutOrientation(self):
        return self._layout_orientation

    def setLayoutOrientation(self, orientation, spacing=5):
        """
        Sets the orientation this input will be displayed as.

        Args:
            orientation (Qt.DIRECTION)
            spacing (int)
        """
        # preflight
        if orientation not in [Qt.Horizontal, Qt.Vertical]: return

        # set orientation
        self._layout_orientation = orientation

        # update separator
        if orientation == Qt.Vertical:
            # orientation
            self.layout().setDirection(QBoxLayout.TopToBottom)

            self.layout().setAlignment(Qt.AlignTop)
            self.layout().setSpacing(spacing)

        elif orientation == Qt.Horizontal:
            # set layout orientation
            self.layout().setDirection(QBoxLayout.LeftToRight)

            # alignment
            self.layout().setAlignment(Qt.AlignLeft)

        # virtual fucntion
        self.layoutOrientationChangedEvent(orientation)

    """ VIRTUAL FUNCTIONS """
    def setLayoutOrientationChangedEvent(self, function):
        self.__orientationChangedEvent = function

    def layoutOrientationChangedEvent(self, orientation):
        self.__layoutOrientationChangedEvent(orientation)

    def __layoutOrientationChangedEvent(self, orientation):
        pass
    # toggle orientation
    # toggle orientation function


class Magnitude(object):
    x = 0
    y = 1
    m = 2
    """
    Object containing the offset/magnitude between two points
    Properties:
        magnitude (float):
        xoffset (float):
        yoffset (float):
    """
    def __init__(self, magnitude, xoffset, yoffset):
        self.magnitude = magnitude
        self.xoffset = xoffset
        self.yoffset = yoffset


def centerCursorOnWidget(widget):
    pos = widget.pos()
    height = widget.height()
    width = widget.width()
    xpos = pos.x() + (width * 0.5)
    ypos = pos.y() + (height * 0.5)
    QCursor.setPos(QPoint(xpos, ypos))


def centerWidgetOnCursor(widget):
    pos = QCursor.pos()
    widget.setGeometry(
        pos.x() - (widget.geometry().width() * 0.5),
        pos.y() - (widget.geometry().height() * 0.5),
        widget.geometry().width(),
        widget.geometry().height()
    )


def centerWidgetOnScreen(widget, width=1080, height=512, resize=False):
    """
    Centers a widget on the screen
    Args:
        widget (QWidget): to be centered/resizesd
        width (int): of widget, only valid if resize TRUE
        height (int): of widget, only valid if resize TRUE
        resize (bool): if True will resize the widget to the height/width dimensions provided
    """
    screen_resolution = QApplication.desktop().screenGeometry()

    xpos = (screen_resolution.width() * 0.5) - (width * 0.5)
    ypos = (screen_resolution.height() * 0.5) - (height * 0.5)

    if resize:
        widget.setFixedSize(width, height)
    widget.move(int(xpos), int(ypos))


def getCenterOfScreen():
    """ Returns the center of the screen as a QPoint

    Returns (QPoint)"""
    screen_resolution = QApplication.desktop().screenGeometry()

    xpos = (screen_resolution.width() * 0.5)
    ypos = (screen_resolution.height() * 0.5)
    return QPoint(xpos, ypos)

def getCenterOfWidget(widget):
    """ Returns the center of the widget

    Args:
        widget (QWidget)

    Returns (QPoint)"""
    xpos = widget.geometry().width() * 0.5
    ypos = widget.geometry().height() * 0.5
    return QPoint(xpos, ypos)

def checkMousePos(pos, widget):
    """
    Checks the mouse position to determine its relation to the current
    widget.

    Args:
        pos (QPoint): current cursor position in global space
        widget (QWidget): current widget to check to see if the cursor
            is inside of or not
    Returns (dict) of booleans
        INSIDE, NORTH, SOUTH, EAST, WEST
        if the arg is True then that is true.  Ie if North is true, then the cursor
        is north of the widget.  If INSIDE is True, then all of the other
        args must be False, and the cursor is inside of the widget still.

    """
    # setup return attrs
    return_dict = {
        "INSIDE" : True,
        "NORTH" : False,
        "EAST" : False,
        "SOUTH" : False,
        "WEST" : False
    }

    # check mouse position...
    top_left = widget.mapToGlobal(widget.geometry().topLeft())
    top = top_left.y()
    left = top_left.x()
    right = left + widget.geometry().width()
    bot = top + widget.geometry().height()

    # update dictionary based off of mouse position
    if top > pos.y():
        return_dict["NORTH"] = True
        return_dict["INSIDE"] = False
    if right < pos.x():
        return_dict["EAST"] = True
        return_dict["INSIDE"] = False
    if bot < pos.y():
        return_dict["SOUTH"] = True
        return_dict["INSIDE"] = False
    if left > pos.x():
        return_dict["WEST"] = True
        return_dict["INSIDE"] = False

    return return_dict


def getBottomLeftPos(widget):
    """
    Returns the bottom left position of the specific widget.  This is mainly for
    lining up any sort of popups and what not.

    Args:
        widget (QWidget): Widget whose position you want to return
    Returns (QPoint): Point in world space of the bottom left coordinate
        of the widget given
    """

    # get pos
    if widget.parent():
        pos = widget.parent().mapToGlobal(widget.geometry().bottomLeft())
    else:
        pos = widget.geometry().bottomLeft()

    # back up clause
    if not pos:
        pos = QPoint(0, 0)

    return pos



# TODO Combine these into an uber function
def getGlobalPos(widget):
    """
    returns the global position of the widget provided, because Qt
    does such a lovely job of doing this out of box and making it
    so simple

    No idea why this doesnt get the actual title bar height?
    args:
        widget: <QWidget>
            widget to return screen space position of

    returns: <QPoint>
    """
    parent = widget.parentWidget()
    if parent is None:
        #top_level_widget = widget.window()
        top_level_widget = widget
        title_bar_height = top_level_widget.style().pixelMetric(QStyle.PM_TitleBarHeight)
        pos = QPoint(
            top_level_widget.pos().x(),
            top_level_widget.pos().y() + title_bar_height + top_level_widget.PdmDepth + (top_level_widget.PdmHeight * .5)
        )

    else:
        pos = parent.mapToGlobal(widget.pos())

    return pos


def getGlobalItemPos(item):
    """
    Returns the screen coordinates of an item

    Args:
        item (QGraphicsItem): item whose coordinates will be returned in screen space

    Returns (QPoint)
    """
    view = item.scene().views()[0]
    view_pos = view.mapFromScene(item.activeObject().scenePos())
    pos = view.viewport().mapToGlobal(view_pos)

    return pos


def getTopLeftPos(widget):
    """
    Returns the bottom left position of the specific widget.  This is mainly for
    lining up any sort of popups and what not.

    Args:
        widget (QWidget): Widget whose position you want to return
    Returns (QPoint): Point in world space of the bottom left coordinate
        of the widget given
    """

    # get pos
    if widget.parent():
        pos = widget.parent().mapToGlobal(widget.geometry().topLeft())
    else:
        pos = widget.geometry().topLeft()

    # back up clause
    if not pos:
        pos = QPoint(0, 0)

    return pos


def getWidgetUnderCursor(pos=None):
    """
    Returns the current widget that is directly under the cursor

    Args:
        pos (QPos):

    Returns (QWidget):
    """
    if not pos:
        pos = QCursor.pos()
    widget = QApplication.instance().widgetAt(pos)
    return widget


def getMagnitude(start_pos, current_pos, magnitude_type=None, multiplier=1):
    """
    returns the magnitude of a user click/drop operation

    Args:
        start_pos (QPoint)
            initial point of the cursor.  This could be when the user
            clicked, or when the last tick was registered
        current_pos (QPoint)
            current position of the cursor
        magnitude_type (Magnitude.TYPE): What type of magnitude to get
            x | y | m
    Returns (Magnitude): container of floats
            xoffset | yoffset | magnitude

    """
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
    magnitude *= multiplier

    # return magnitude
    if magnitude_type == Magnitude.x:
        return xoffset
    elif magnitude_type == Magnitude.y:
        return yoffset
    elif magnitude_type == Magnitude.m:
        return magnitude
    else:
        return Magnitude(magnitude, xoffset, yoffset)


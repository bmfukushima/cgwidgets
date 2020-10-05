from qtpy.QtCore import QEvent
from qtpy.QtWidgets import QWidget, QApplication, QLabel
from qtpy.QtGui import QRegion
import sys

from cgwidgets.utils import getTopLeftPos


class InvisibleWidgetEvent(QWidget):
    """
Causes a widget to hide/show during pen down/up.

Sets up an invisible drag event.  When the user clicks, and drags,
the widget will dissappear.  On release, the widget will reappear at
the original location.

Args:
    **  hide_widget (QWidget): optional argument, if this is defined
            this will be the widget that is hidden.
    **  parent(QWidget): if no hide_widget argument is provided,
            this will become the widget to be hidden.
    """
    def __init__(self, parent=None):
        super(InvisibleWidgetEvent, self).__init__(parent)
        self._updating = False

    def hideWidget(self):
        pass

    def showWidget(self):
        pass

    def eventFilter(self, obj, event, *args, **kwargs):
        """
        This will assuming that sticky drag has been turned on.

        Attributes:
            _updating (bool): essentially keeps track of the event loop. To ensure
                that recursion does not happen as this event filter is installed
                on 3 widgets.  This makes sure that a click only happens once.
        """
        # preflight
        if not hasattr(obj, '_invisible_widget_data'): return False

        # interface
        hide_widget = obj._invisible_widget_data['hide_widget']
        parent_widget = obj._invisible_widget_data['parent']
        activation_widget = obj._invisible_widget_data['activation_widget']

        if event.type() == QEvent.MouseButtonPress:
            # preflight
            # ensure this is only run once per click
            if self._updating is True: return False
            # ensure that the user clicked on the right widget
            if obj != activation_widget and hide_widget._hide_widget_filter_INVISIBLE is False: return False

            # toggle display flag
            hide_widget._hide_widget_filter_INVISIBLE = not hide_widget._hide_widget_filter_INVISIBLE
            print("toggly joe? %s"%obj)
            # hide
            if hide_widget._hide_widget_filter_INVISIBLE is True:
                if self._updating is False:
                    if obj == activation_widget:
                        self._updating = True
                        region = QRegion(parent_widget.frameGeometry())
                        hide_widget.setMask(region)

            # show
            else:
                if self._updating is False:
                    self._updating = True
                    width = hide_widget.width()
                    height = hide_widget.height()
                    region = QRegion(0, 0, width, height)
                    hide_widget.setMask(region)

        if event.type() == QEvent.MouseButtonRelease:
            self._updating = False

        return QWidget.eventFilter(self, obj, event, *args, **kwargs)


def installInvisibleWidgetEvent(hide_widget, activation_widget=None):
    """
    Installs an event filter on the widget that makes it so that when the
    user click/drags, it will turn the cursor invisible, and all the cursor
    to move an infinite distance.  On release, it will return the cursor
    back to the starting position

    Args:
        activation_widget (QWidget): Widget when clicked to hide the hide_widget.
            If none is provided, the parent widget will be used
        hide_widget (QWidget): widget to be hidden, if none is provided,
            the parent widget will be used
        parent (QWidget): parent / widget to install the event filter on
            when clicked will Show the hide_widget
    Returns:
    """
    from cgwidgets.events import InvisibleWidgetEvent

    # set up default widgets
    parent = hide_widget.parent()

    if activation_widget is None:
        activation_widget = hide_widget

    invisible_widget_data = {
        'parent' : parent,
        'hide_widget' : hide_widget,
        'activation_widget' : activation_widget}

    # create filter
    invisible_widget_filter = InvisibleWidgetEvent(
        parent=parent
    )

    # setup attrs / install event filter
    hide_widget._hide_widget_filter_INVISIBLE = False
    for key in invisible_widget_data:
        widget = invisible_widget_data[key]
        widget._invisible_widget_data = invisible_widget_data

        # install event filter
        widget.installEventFilter(invisible_widget_filter)

    return invisible_widget_filter


if __name__ == '__main__':
    from qtpy.QtGui import QCursor
    from qtpy.QtWidgets import QWidget, QVBoxLayout
    #
    # from cgwidgets.utils import installInvisibleWidgetEvent

    app = QApplication(sys.argv)
    mw = QWidget()
    l = QVBoxLayout(mw)

    w = QLabel('Test')
    w2 = QLabel("test2")
    w.setStyleSheet("background-color:rgba(255,0,0,255)")
    l.addWidget(w)
    l.addWidget(w2)

    installInvisibleWidgetEvent(w, activation_widget=w2)
    # ef = InvisibleWidgetEvent()
    # w.installEventFilter(ef)
    mw.show()
    mw.move(QCursor.pos())
    sys.exit(app.exec_())

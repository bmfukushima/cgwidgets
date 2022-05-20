"""
Add API for viewWidget
    - editFinishedSignal
    - setViewDelegateWidget

"""
from qtpy import API_NAME
from qtpy.QtWidgets import (QSizePolicy)
from qtpy.QtCore import (QEvent, QDir, QTimer)

from qtpy.QtWidgets import (QFileSystemModel, QCompleter, QApplication, QFrame, QVBoxLayout)
from qtpy.QtCore import Qt

from cgwidgets.widgets.AbstractWidgets.AbstractBaseInputWidgets import AbstractStringInputWidget
from cgwidgets.widgets.AbstractWidgets.AbstractOverlayInputWidget import AbstractOverlayInputWidget
from cgwidgets.widgets.AbstractWidgets.AbstractShojiLayout import AbstractShojiLayout
from cgwidgets.widgets.AbstractWidgets.AbstractInputInterface import iAbstractInputWidget


from cgwidgets.utils import (getFontSize, installResizeEventFinishedEvent)
from cgwidgets.settings import iColor

class AbstractLabelledInputWidget(QFrame, iAbstractInputWidget):
    """
    A single input widget.  This inherits from the ShojiLayout,
    to provide a slider for the user to expand/contract the editable area
    vs the view label.

    Args:
        name (str):
        note (str):
        direction (Qt.ORIENTATION):
        default_label_length (int): default length to display labels when showing this widget
        delegate_widget (QWidget): instance of widget to use as delegate
        delegate_constructor (QWidget): constructor to use as delegate widget.  This will automatically
            be overwritten by the delegate_widget if it is provided.
        widget_type (QWidget): Widget type to be constructed for as the delegate widget
        view_as_read_only (bool): Determines if the label should be read only or not

    Attributes:
        resize_slider_on_widget_resize (bool): determines if widgets labels should be automatically
            reset to their default position when the widget is resized.
        splitter_event_is_paused (bool): determines if the splitter resize event is currently paused
            or not
        initializing (bool): determines if the widget is starting up or not
            This is mainly used to set the default size positions

    Hierarchy:
        |- ViewWidget --> AbstractOverlayInputWidget
        |- DelegateWidget --> QWidget

    Note:
        Needs parent to be provided in order for the default size to be
        displayed correctly
    """

    TYPE = "label_input"
    def __init__(
        self,
        parent=None,
        name="None",
        note=None,
        image_path=None,
        direction=Qt.Horizontal,
        default_label_length=50,
        delegate_widget=None,
        delegate_constructor=None,
        view_as_read_only=False,
    ):
        super(AbstractLabelledInputWidget, self).__init__(parent)
        if API_NAME == "PySide2":
            iAbstractInputWidget.__init__(self) #pyside2 forces us to do this import

        # set up attrs
        self.__initializing = True
        self._default_label_length = default_label_length
        self._separator_length = -1
        self._separator_width = 5
        self._splitter_event_is_paused = False
        self._resize_slider_on_widget_resize = False
        font_size = getFontSize(QApplication)

        # create main widget
        QVBoxLayout(self)
        self._main_widget = AbstractShojiLayout(self, direction)
        self.layout().addWidget(self._main_widget)

        # create view widget
        self._view_widget = AbstractOverlayInputWidget(title=name)

        if note:
            self._view_widget.setToolTip(note)
        if image_path:
            self.viewWidget().setImage(image_path)

        # todo, why does a subclassed combo box not register here...
        # setup delegate widget
        if not delegate_widget and not delegate_constructor:
            delegate_widget = AbstractStringInputWidget(self)

        if not delegate_widget and delegate_constructor:
            delegate_widget = delegate_constructor(self)

        if delegate_constructor:
            self._delegate_constructor = delegate_constructor

        self._delegate_widget = delegate_widget #hack to make the setInputBaseClass update work
        self._delegate_widget.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.Preferred
        )
        self._delegate_widget.setMinimumSize(1, int(font_size*2.5))

        # add widgets
        self.mainWidget().addWidget(self._view_widget)
        self.mainWidget().addWidget(self._delegate_widget)

        # setup style
        self.mainWidget().setStretchFactor(0, 0)
        self.mainWidget().setStretchFactor(1, 1)
        self.resetSliderPositionToDefault()
        self.layout().setContentsMargins(1, 1, 1, 1)
        if view_as_read_only:
            self.setViewAsReadOnly(True)
        # connect signals
        # todo move to newer tech
        # self.mainWidget().addDelayedSplitterMovedEvent(self, self.__splitterMoved, 100)
        self.mainWidget().splitterMoved.connect(self.__splitterMoved)

        self.mainWidget().setIsSoloViewEnabled(False)
        self.setDirection(direction)

    """ HANDLE GROUP FRAME MOVING"""
    def __splitterMoved(self, pos, index):
        """ When the splitter is moved, this will check to see if it there are parrallel
        splitters that can be moved in unison

        Args:
            pos (int): position of the spltiter handle
            index (int): index of the splitter handle
            """
        modifiers = QApplication.keyboardModifiers()
        frame_container = self.parent()
        if hasattr(frame_container, "_frame_container"):
            if frame_container.direction() == Qt.Vertical:
                if modifiers in [Qt.AltModifier]:
                    return
                else:
                    if not self._splitter_event_is_paused:
                        def pauseSplitter():
                            self._splitter_event_is_paused = False

                        # start timer
                        self._test_timer = QTimer()
                        self._test_timer.start(10)
                        self._test_timer.timeout.connect(pauseSplitter)

                        # update handle positions
                        self.setAllHandlesToPos(pos, index)
                        self._splitter_event_is_paused = True

    @staticmethod
    def getAllParrallelWidgets(labelled_input_widget):
        """
        Returns a list of all of the parallel AbstractLabelledInputWidgets

        Args:
            labelled_input_widget (AbstractLabelledInputWidgets)
        """

        parent = labelled_input_widget.parent()
        handles_list = []
        widget_list = parent.delegateWidgets()
        for widget in widget_list:
            if hasattr(widget, "TYPE"):
                if widget.TYPE == "label_input":
                    handles_list.append(widget)

        return handles_list

    def setAllHandlesToPos(self, pos, index):
        """
        Sets all of the handles to the pos provided

        Args:
            pos (int): value offset of the slider
            index (int): index of splitter being moved
        Attributes:
            _splitter_event_is_paused (bool): blocks events from updating
        :param pos:
        :return:
        """
        self._splitter_event_is_paused = True
        widgets_list = AbstractLabelledInputWidget.getAllParrallelWidgets(self)
        for widget in widgets_list:
            widget.mainWidget().moveSplitter(pos, index)

        self._splitter_event_is_paused = False

    def getHandlePosition(self):
        """
        Need to figure out how to return the handles position...

        :return:
        """
        return

    """ MAIN WIDGET"""
    def mainWidget(self):
        return self._main_widget

    def setMainWidget(self, main_widget):
        self._main_widget = main_widget

    """ VIEW WIDGET """
    def viewWidget(self):
        return self._view_widget

    def setViewWidget(self, _view_widget):
        # delete view widget
        if hasattr(self, "_view_widget"):
            self._view_widget.setParent(None)
            self._view_widget.deleteLater()

        # set new view widget
        self._view_widget = _view_widget
        self.mainWidget().insertWidget(0, _view_widget)

    def setViewAsReadOnly(self, enabled, mode=AbstractOverlayInputWidget.RELEASE):
        """ Determines if the View Widget should be read only or not.

        Args:
            enabled (bool):
            mode (AbstractOverlayInputWidget.DISPLAYMODE): If enabled is False, this
                can be set to determine the display mode.  The default mode is
                    AbstractOverlayInputWidget.RELEASE"""
        if enabled:
            self.viewWidget().setDisplayMode(AbstractOverlayInputWidget.DISABLED)
        else:
            self.viewWidget().setDisplayMode(mode)

    def name(self):
        return self.viewWidget().title()

    def setName(self, name):
        self.viewWidget().setTitle(name)

    def image(self):
        return self.viewWidget().title()

    def setImage(self, image_path):
        self.viewWidget().setImage(image_path)

    """ DELEGATE WIDGET """
    def setDelegateWidget(self, _delegate_widget):
        # remove previous input widget
        if self.delegateWidget():
            self.delegateWidget().setParent(None)

        # create new input widget
        self._delegate_widget = _delegate_widget
        self.mainWidget().addWidget(_delegate_widget)
        self._delegate_widget.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding
        )

    def delegateWidget(self):
        return self._delegate_widget

    def setDelegateConstructor(self, _delegate_constructor):
        """
        Sets a delegate constructor.  This provides a class constructor, and creates that
        class type as the delegate widget.

        This is most useful for instances where a delegate needs to be dynamically populated,
        such as DynamicShojiModelViewWidgets.

        Args:
            _delegate_constructor (QWidget Class): to be constructed

        """
        self._delegate_constructor = _delegate_constructor

        if self.delegateWidget():
            self.delegateWidget().setParent(None)
            #self.delegateWidget().deleteLater()

            # create new input widget
            self._delegate_widget = _delegate_constructor(self)
            self._delegate_widget.setMinimumSize(1, 1)
            self._delegate_widget.setSizePolicy(
                QSizePolicy.MinimumExpanding, QSizePolicy.Preferred
            )

            # reset splitter
            self.mainWidget().addWidget(self._delegate_widget)
            self._delegate_widget.show()
            self.resetSliderPositionToDefault()

    def delegateConstructor(self):
        return self._delegate_constructor

    """ WIDGETS """
    def addWidget(self, widget, is_soloable=True):
        self.mainWidget().addWidget(widget, is_soloable=is_soloable)

    """ SIZES """
    # todo update these to correct names
    def setHandleLength(self, length):
        self.mainWidget().setHandleLength(length)
        self._separator_length = length

    def setHandleWidth(self, width):
        self.mainWidget().setHandleWidth(width)
        self._separator_width = width

    def direction(self):
        return self._direction

    def setDirection(self, direction, update_defaults=False):
        """

        Args:
            direction (Qt.DIRECITON):
            update_defaults (bool): If enabled will automagically update
                the display of the splitter to correctly display the default sizes.

        Returns:

        """
        # preflight
        if direction not in [Qt.Horizontal, Qt.Vertical]: return

        # set attr
        self._direction = direction

        # setup minimum sizes
        font_size = getFontSize(QApplication)
        if direction == Qt.Vertical:
            # hide handle?
            self.mainWidget().setHandleMarginOffset(0)
            self.mainWidget().setIsHandleVisible(False)
            self.mainWidget().setIsHandleStatic(True)
            self.mainWidget().setMinimumSize(font_size*4, font_size*6)
        elif direction == Qt.Horizontal:
            self.mainWidget().setHandleMarginOffset(15)
            self.mainWidget().setIsHandleVisible(True)
            self.mainWidget().setIsHandleStatic(False)
            self.mainWidget().setMinimumSize(font_size*12, int(font_size*2.5))

        # update defaults
        if update_defaults:
            if direction == Qt.Horizontal:
                self.setDefaultLabelLength(50)
                self.setSeparatorWidth(0)
            elif direction == Qt.Vertical:
                self.setDefaultLabelLength(30)
            self.resetSliderPositionToDefault()

        # update label
        self.mainWidget().setOrientation(direction)

    def defaultLabelLength(self):
        return self._default_label_length

    def setDefaultLabelLength(self, length):
        self._default_label_length = length

    def setResizeSlidersOnWidgetResize(self, enabled):
        self._resize_slider_on_widget_resize = enabled

    def resizeSliderOnWidgetResize(self):
        return self._resize_slider_on_widget_resize

    """ EVENTS """
    def resetSliderPositionToDefault(self):
        self.mainWidget().moveSplitter(self.defaultLabelLength(), 1)

    def setUserFinishedEditingEvent(self, function):
        self.delegateWidget().setUserFinishedEditingEvent(function)

    def showEvent(self, event):
        # Set label to default position
        """ Note: need to pause the splitter, or it will wreak havoc in the 
        FrameInputWidgetContainer """
        if self.__initializing is True:
            super(AbstractLabelledInputWidget, self).showEvent(event)
            self._splitter_event_is_paused = True
            self.resetSliderPositionToDefault()
            self._splitter_event_is_paused = False
            self.__initializing = False
        return QFrame.showEvent(self, event)

    def resizeEvent(self, event):
        """ installs a resize event to automagically reset the sliders to their default positions"""
        def _resizeFinishedEvent(*args, **kwargs):
            """ Note: This will not work if the widget is deleted
            Some sort of RuntimeError"""
            try:
                if self.resizeSliderOnWidgetResize():
                    super(AbstractLabelledInputWidget, self).resizeEvent(event)
                    self.resetSliderPositionToDefault()
            except RuntimeError:
                # event deleted...
                """ Will still work... this will just remove the annoying af error message """
                pass

        installResizeEventFinishedEvent(self, 100, _resizeFinishedEvent, '_timer')

        return QFrame.resizeEvent(self, event)


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
    from qtpy.QtGui import QCursor

    import sys, inspect

    app = QApplication(sys.argv)
    # def userEvent(widget):
    #     print("user input...", widget)
    #
    #
    # def asdf(item, widget, value):
    #     return
    #
    #
    # @staticmethod
    # def liveEdit(item, widget, value):
    #     return
    #
    #
    # widget = ShojiInputWidgetContainer(name="test")
    # inputs = ["cx", "cy", "fx", "fy", "radius"]  # , stops"""
    # for i in inputs:
    #     widget.insertInputWidget(0, FloatInputWidget, i, asdf,
    #                            user_live_update_event=asdf, default_value=0.5)

    main_widget = QWidget()
    main_layout = QVBoxLayout(main_widget)

    for x in range(3):

        test_labelled_embed = AbstractLabelledInputWidget(name="embed")
        test_labelled_embed.setDefaultLabelLength(200)
        test_labelled_embed.addWidget(QLabel("test"))
        main_layout.addWidget(test_labelled_embed)

    main_widget.move(QCursor.pos())
    main_widget.show()
    #main_widget.resize(256, 256)
    main_widget.resize(500, 500)
    # test_labelled_embed.setStyleSheet("background-color:rgba(255,0,0,255); border: 2px solid rgba(0,255,0,255);")
    #w.move(QCursor.pos())
    sys.exit(app.exec_())

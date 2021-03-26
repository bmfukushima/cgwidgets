"""
Add API for viewWidget
    - editFinishedSignal
    - setViewDelegateWidget

"""
from qtpy.QtWidgets import (QSizePolicy)
from qtpy.QtCore import (QEvent, QDir)
from qtpy.QtWidgets import (QFileSystemModel, QCompleter, QApplication)
from qtpy.QtCore import Qt

from cgwidgets.widgets.AbstractWidgets.AbstractBaseInputWidgets import AbstractStringInputWidget
from cgwidgets.widgets.AbstractWidgets.AbstractOverlayInputWidget import AbstractOverlayInputWidget
from cgwidgets.widgets.AbstractWidgets.AbstractShojiLayout import AbstractShojiLayout

from cgwidgets.utils import (getFontSize)
from cgwidgets.settings.colors import iColor

class AbstractLabelledInputWidget(AbstractShojiLayout):
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

    Hierarchy:
        |- ViewWidget --> AbstractOverlayInputWidget
        |- DelegateWidget --> QWidget

    Note:
        Needs parent to be provided in order for the default size to be
        displayed correctly

    """
    def __init__(
        self,
        parent=None,
        name="None",
        note=None,
        image_path=None,
        direction=Qt.Horizontal,
        default_label_length=50,
        delegate_widget=None,
        delegate_constructor=None
    ):
        super(AbstractLabelledInputWidget, self).__init__(parent, direction)

        # set up attrs
        self._default_label_length = default_label_length
        self._separator_length = -1
        self._separator_width = 5
        self.__splitter_event_is_paused = False
        font_size = getFontSize(QApplication)

        # create view widget
        self._view_widget = AbstractOverlayInputWidget(title=name)
        if note:
            self._view_widget.setToolTip(note)
        if image_path:
            self.viewWidget().setImage(image_path)

        # setup delegate widget
        if not delegate_widget and not delegate_constructor:
            delegate_widget = AbstractStringInputWidget(self)

        if not delegate_widget and delegate_constructor:
            delegate_widget = delegate_constructor(self)

        self._delegate_widget = delegate_widget #hack to make the setInputBaseClass update work
        self._delegate_widget.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.Preferred
        )
        self._delegate_widget.setMinimumSize(1, int(font_size*2.5))

        # add widgets
        self.addWidget(self._view_widget)
        self.addWidget(self._delegate_widget)

        # set size hints
        self.setStretchFactor(0, 0)
        self.setStretchFactor(1, 1)
        self.resetSliderPositionToDefault()

        # setup style
        self.splitterMoved.connect(self.__splitterMoved)

        # todo this blocks hover display...
        self.setIsSoloViewEnabled(False)
        self.setDirection(direction)
        #self._delegate_widget.setProperty("hover_display", True)

    """ HANDLE GROUP FRAME MOVING"""

    def __splitterMoved(self, pos, index):
        modifiers = QApplication.keyboardModifiers()

        if modifiers in [Qt.AltModifier]:
            return
        else:
            if not self.__splitter_event_is_paused:
                self.setAllHandlesToPos(pos)

    @staticmethod
    def getAllParrallelWidgets(labelled_input_widget):
        """
        Returns a list of all of the parallel AbstractLabelledInputWidgets

        Args:
            labelled_input_widget (AbstractLabelledInputWidgets)
        """
        #from .ContainerWidgets import FrameInputWidgetContainer
        from cgwidgets.widgets import FrameInputWidgetContainer
        # from ContainerWidgets import FrameInputWidgetContainer
        parent = labelled_input_widget.parent()
        handles_list = []
        if isinstance(parent, FrameInputWidgetContainer):
            widget_list = parent.delegateWidgets()
            for widget in widget_list:
                handles_list.append(widget)

        return handles_list

    def setAllHandlesToPos(self, pos):
        """
        Sets all of the handles to the pos provided

        Args:
            pos (int): value offset of the slider
        Attributes:
            __splitter_event_is_paused (bool): blocks events from updating
        :param pos:
        :return:
        """
        self.__splitter_event_is_paused = True
        widgets_list = AbstractLabelledInputWidget.getAllParrallelWidgets(self)

        for widget in widgets_list:
            widget.moveSplitter(pos, 1)

        self.__splitter_event_is_paused = False
        # todo
        # how to handle ShojiGroups?
        #ShojiInputWidgetContainer

    def getHandlePosition(self):
        """
        Need to figure out how to return the handles position...

        :return:
        """
        return

    """ VIEW WIDGET """
    def viewWidget(self):
        return self._view_widget

    def setViewWidget(self, _view_widget):
        self._view_widget = _view_widget

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
        self.addWidget(_delegate_widget)
        self._delegate_widget.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding
        )

    def delegateWidget(self):
        return self._delegate_widget

    # def setInputBaseClass(self, _input_widget_base_class):
    #
    #     self._input_widget_base_class = _input_widget_base_class
    #
    #     if self.delegateWidget():
    #         self.delegateWidget().setParent(None)
    #
    #         # create new input widget
    #         self._input_widget = _input_widget_base_class(self)
    #         self._input_widget.setMinimumSize(1, 1)
    #         self._input_widget.setSizePolicy(
    #             QSizePolicy.MinimumExpanding, QSizePolicy.Preferred
    #         )
    #         # reset splitter
    #         self.addWidget(self._input_widget)
    #         self._input_widget.show()
    #         self.resetSliderPositionToDefault()
    #
    # def getInputBaseClass(self):
    #     return self._input_widget_base_class

    """ SIZES """
    def setSeparatorLength(self, length):
        self.setHandleLength(length)
        self._separator_length = length

    def setSeparatorWidth(self, width):
        self.setHandleWidth(width)
        self._separator_width = width

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

        # setup minimum sizes
        font_size = getFontSize(QApplication)
        if direction == Qt.Vertical:
            # hide handle?
            self.setHandleMarginOffset(0)
            self.setIsHandleVisible(False)
            self.setIsHandleStatic(True)
            self.setMinimumSize(font_size*4, font_size*6)
        elif direction == Qt.Horizontal:
            self.setHandleMarginOffset(15)
            self.setIsHandleVisible(True)
            self.setIsHandleStatic(False)
            self.setMinimumSize(font_size*12, int(font_size*2.5))

        # update defaults
        if update_defaults:
            if direction == Qt.Horizontal:
                self.setDefaultLabelLength(50)
                self.setSeparatorWidth(0)
            elif direction == Qt.Vertical:
                self.setDefaultLabelLength(30)
            self.resetSliderPositionToDefault()

        # update label
        return AbstractShojiLayout.setOrientation(self, direction)

    def defaultLabelLength(self):
        return self._default_label_length

    def setDefaultLabelLength(self, length):
        self._default_label_length = length

    """ EVENTS """
    def resetSliderPositionToDefault(self):
        #print(self.defaultLabelLength())
        self.moveSplitter(self.defaultLabelLength(), 1)

    def setUserFinishedEditingEvent(self, function):
        self.delegateWidget().setUserFinishedEditingEvent(function)

    def showEvent(self, event):
        super(AbstractLabelledInputWidget, self).showEvent(event)
        self.resetSliderPositionToDefault()
        return AbstractShojiLayout.showEvent(self, event)

    def resizeEvent(self, event):
        super(AbstractLabelledInputWidget, self).resizeEvent(event)
        self.resetSliderPositionToDefault()
        return AbstractShojiLayout.resizeEvent(self, event)


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication, QWidget, QVBoxLayout
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


    test_labelled_embed = AbstractLabelledInputWidget(name="embed")
    #labelled_input = LabelledInputWidget(name="test", widget_type=test_labelled_embed)

    test_labelled_embed.move(QCursor.pos())
    test_labelled_embed.show()
    #test_labelled_embed.resize(256, 256)
    test_labelled_embed.resize(500, 500)
    test_labelled_embed.show()
    #w.move(QCursor.pos())
    sys.exit(app.exec_())

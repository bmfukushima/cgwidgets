
from qtpy.QtWidgets import (QLabel, QStackedWidget)

from cgwidgets.settings.hover_display import installHoverDisplaySS, removeHoverDisplay
from cgwidgets.widgets.AbstractWidgets.AbstractInputInterface import iAbstractInputWidget

class AbstractOverlayInputWidget(QStackedWidget, iAbstractInputWidget):
    """
    Input widget with a display delegate overlaid.  This delegate will disappear
    when the user first hover enters.

    Args:
        display_mode (AbstractOverlayInputWidget.DISPLAYMODE): Trigger that will
            determine if/when the editor is displayed to the user.
        delegate_widget (QWidget): Widget for user to input values into
        image (str): path on disk to image
        title (string): Text to display when the widget is shown
            for the first time.

    Attributes:
        delegate_widget (QWidget): Editor widget that will be displayed when the user
            triggers it with the DisplayMode
        view_widget (AbstractLabelInputWidget): Label to be displayed when the user
            is not hovered over the widget

    Virtual Events:
        hide_delegate_event (Virtual Event): runs when the editor is being closed
        show_delegate_event (Virtual Event): runs when the editor is being opened

        Note: These events both take one arg, which is the current instance of the AbstractOverlayInputWidget
    """
    # Display Modes
    DISABLED = 1
    ENTER = 2
    RELEASE = 4
    def __init__(
            self,
            parent=None,
            delegate_widget=None,
            image=None,
            title="",
            display_mode=4
    ):
        super(AbstractOverlayInputWidget, self).__init__(parent)
        # import widgets (avoid circular imports...)
        from cgwidgets.widgets import AbstractLabelWidget, AbstractStringInputWidget

        # create widgets
        class ViewWidget(AbstractLabelWidget):
            def __init__(self, parent=None, title=""):
                super(ViewWidget, self).__init__(parent, title)

            """ EVENTS """

            def mouseReleaseEvent(self, event):
                # enable editor
                if self.parent().displayMode() == AbstractOverlayInputWidget.RELEASE:
                    if self.parent().currentIndex() == 0:
                        self.parent().showDelegate()
                        self.parent().delegateWidget().setFocus()

                return AbstractLabelWidget.mouseReleaseEvent(self, event)

            def enterEvent(self, event):
                # enable editor
                if self.parent().displayMode() == AbstractOverlayInputWidget.ENTER:
                    self.parent().showDelegate()
                    AbstractLabelWidget.enterEvent(self, event)
                    self.parent().delegateWidget().setFocus()
                return AbstractLabelWidget.enterEvent(self, event)

        view_widget = ViewWidget(self, title)
        self.setViewWidget(view_widget)

        if not delegate_widget:
            delegate_widget = AbstractStringInputWidget(self)
        self.setDelegateWidget(delegate_widget)

        # setup style
        self.setDisplayMode(display_mode)

        if image:
            self.setImage(image)

        # style_sheet = removeHoverDisplay(self.styleSheet(), "INPUT WIDGETS")
        # self.setStyleSheet(style_sheet)
        # self.viewWidget().updateStyleSheet()

    """ WIDGETS """
    def delegateWidget(self):

        return self._delegate_widget

    def setDelegateWidget(self, widget):
        # remove old input widget
        if hasattr(self, "_delegate_widget"):
            self._delegate_widget.setParent(None)

        # add new input widget
        self.addWidget(widget)

        # setup attr
        self._delegate_widget = widget

        style_sheet = removeHoverDisplay(widget.styleSheet(), "INPUT WIDGETS")
        widget.setStyleSheet(style_sheet)

    def viewWidget(self):
        return self._view_widget

    def setViewWidget(self, view_widget):
        if hasattr(self, "_view_widget"):
            self._view_widget.setParent(None)
        self._view_widget = view_widget
        self.insertWidget(0, self._view_widget)
        # self._view_widget.installEventFilter(self)

    """ DELEGATE DISPLAY """
    def displayMode(self):
        return self._display_mode

    def setDisplayMode(self, display_mode):
        """
        Sets when the editor will be displayed to the user

        Args:
            display_mode (AbstractOverlayInputWidget.DISPLAYMODE): Trigger that will
                determine if/when the editor is displayed to the user.
        """
        self._display_mode = display_mode

        if display_mode == AbstractOverlayInputWidget.DISABLED:
            style_sheet = removeHoverDisplay(self.styleSheet(), "INPUT WIDGETS")
            self.setStyleSheet(style_sheet)

        else:
            self.updateStyleSheet()

    def showDelegate(self):
        self.setCurrentIndex(1)
        self.releaseMouse()

        # run user event
        self.showDelegateEvent()

    def hideDelegate(self):
        self.setCurrentIndex(0)

        # run user event
        self.hideDelegateEvent()

    """ VIRTUAL FUNCTIONS """
    def title(self):
        return self.viewWidget().text()

    def setTitle(self, title):
        self.viewWidget().setText(title)

    def setImage(self, image_path):
        self.viewWidget().setImage(image_path)

    def removeImage(self):
        self.viewWidget().removeImage()

    """ VIRTUAL EVENTS """
    def _show_delegate_event(self):
        pass

    def setShowDelegateEvent(self, event):
        self._show_delegate_event = event

    def showDelegateEvent(self):
        self._show_delegate_event(self)

    def _hide_delegate_event(self):
        pass

    def setHideDelegateEvent(self, event):
        self._hide_delegate_event = event

    def hideDelegateEvent(self):
        self._hide_delegate_event(self)

    """ EVENTS """
    def leaveEvent(self, event):
        if self.currentIndex() == 1:
            self.hideDelegate()
        return QStackedWidget.leaveEvent(self, event)


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication, QWidget, QVBoxLayout
    from qtpy.QtGui import QCursor
    from cgwidgets.widgets import AbstractBooleanInputWidget

    import sys, inspect

    app = QApplication(sys.argv)


    class CustomDynamicWidgetExample(AbstractOverlayInputWidget):
        """
        Custom dynamic widget example.  This is a base example of the OverlayInputWidget
        as well.
        """

        def __init__(self, parent=None):
            super(CustomDynamicWidgetExample, self).__init__(parent, title="Hello")

    # Construct
    delegate_widget = AbstractBooleanInputWidget(text="yolo")
    overlay_widget = AbstractOverlayInputWidget(
        title="title",
        display_mode=AbstractOverlayInputWidget.RELEASE,
        delegate_widget=delegate_widget,
        image="/home/brian/Pictures/test.png")

    # main_widget = CustomDynamicWidgetExample()
    #overlay_widget.setDisplayMode(AbstractOverlayInputWidget.DISABLED)
    #overlay_widget.setDisplayMode(AbstractOverlayInputWidget.ENTER)
    main_widget = QWidget()
    main_layout = QVBoxLayout(main_widget)
    main_layout.addWidget(overlay_widget)
    main_layout.addWidget(QLabel("klajdflasjkjfklasfjsl"))

    main_widget.move(QCursor.pos())
    main_widget.show()
    main_widget.resize(500, 500)
    main_widget.show()
    #print ('\n\n========================\n\n')
    #print(main_widget.styleSheet())
    #w.move(QCursor.pos())
    sys.exit(app.exec_())
    #
    # def print_classes():
    #     for name, obj in inspect.getmembers(sys.modules[__name__]):
    #         if inspect.isclass(obj):
    #             print(obj)
    #
    # print(__name__)
    # print_classes()
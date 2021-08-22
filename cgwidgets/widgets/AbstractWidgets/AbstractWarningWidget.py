from qtpy.QtWidgets import QWidget, QHBoxLayout, QSizePolicy
from qtpy.QtCore import Qt

from cgwidgets.settings import iColor
from cgwidgets.settings import icons
from cgwidgets.settings.hover_display import installHoverDisplaySS

from cgwidgets.utils import setAsWindow, centerWidgetOnScreen, setAsAlwaysOnTop
from cgwidgets.widgets import AbstractLabelWidget, AbstractButtonInputWidget
from cgwidgets.widgets.AbstractWidgets.AbstractGIFWidget import AbstractGIFWidget


class AbstractWarningWidget(QWidget):
    """
    Abstract widget that will require user input of
    Accepting / Canceling the current event that
    is proposed to them.

    The event can be accepted/denied with the buttons
    to the left/right of the widget, or with the esc / enter/return keys.

    Args:
        width (int): of widget, only valid if resize TRUE
        height (int): of widget, only valid if resize TRUE
        resize_on_show (bool): if True will resize the widget to the height/width dimensions provided
        display_widget (QWidget): Central widget to be displayed
            to the user.  Can also be set with setCentralWidget.
        button_width (int): The width of the accept/cancel buttons.
        widget (QWidget): Widget that is calling the WarningWidget

    Attributes:
        closing (bool): if the widget is currently in a cancel event

    Widgets:
        accept_button (QPushButton): When pressed, accepts the
            current event registered with setAcceptEvent.
        cancel_button (QPushButton): When pressed, cancels the
            current event registered with setCancelEvent.
        display_widget (QWidget): The central widget to be displayed
            to the user.
        widget (QWidget): Widget that called this WarningWidget

    Hierarchy:
        |- QHBoxLayout
            |- cancelButton --> (AbstractGIFWidget)
            |- displayWidget --> (QWidget)
            |- acceptButton --> (AbstractGIFWidget)

    Notes:
        The button_width attribute really doesn't make sense... and isn't setup correctly
    """

    def __init__(self, parent=None, display_widget=None, button_width=150, width=1080, height=512, resize_on_show=True, widget=None):
        super(AbstractWarningWidget, self).__init__(parent)
        #self.main_widget = getMainWidget(self)

        # Create main layout
        QHBoxLayout(self)
        setAsWindow(self)

        # setup default attrs
        self.display_height = height
        self.display_width = width
        self.resize_on_show = resize_on_show
        self._widget = widget
        self._closing = False

        # create text layout
        if not display_widget:
            text = "Provide display_widget kwarg to constructor \n or \n use setCentralWidget to display a widget here..."
            display_widget = AbstractLabelWidget(parent=self, text=text)
        self._display_widget = display_widget

        # create widgets
        accept_gif = icons["ACCEPT_GIF"]
        cancel_gif = icons["CANCEL_GIF"]
        self._accept_button = AbstractGIFWidget(accept_gif)
        self._cancel_button = AbstractGIFWidget(cancel_gif)

        # install hover displays
        installHoverDisplaySS(self.acceptButton(), hover_color=iColor["rgba_accept"])
        installHoverDisplaySS(self.cancelButton(), hover_color=iColor["rgba_cancel"])

        # setup style
        if not button_width:
            self.setButtonWidth(150)
        self.acceptButton().setResolution(button_width, height-4)
        self.cancelButton().setResolution(button_width, height-4)
        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.acceptButton().setSizePolicy(size_policy)
        self.cancelButton().setSizePolicy(size_policy)

        # setup spacing
        self.acceptButton().layout().setContentsMargins(0, 0, 0, 0)
        self.cancelButton().layout().setContentsMargins(0, 0, 0, 0)
        self.displayWidget().setContentsMargins(0, 0, 0, 0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        # setup events
        self.acceptButton().setMousePressEvent(self.acceptEvent)
        self.cancelButton().setMousePressEvent(self.cancelEvent)

        # setup helpful tips
        self.setupButtonTooltips()

        # set up main layout
        self.layout().addWidget(self.cancelButton(), 1)
        self.layout().addWidget(self._display_widget)
        self.layout().addWidget(self.acceptButton(), 1)
        self.layout().setAlignment(Qt.AlignTop)

    def setupButtonTooltips(self):
        """
        Creates the tooltips for the user on how to use these buttons
        when they hover over the widget.
        """
        self.acceptButton().setToolTip("""
The happy af dog bouncing around that has a massive
green border around it when you hover over it means to continue.

FYI:
You can also hit <ENTER> and <RETURN> to continue...
        """)
        self.cancelButton().setToolTip("""
The super sad dog who looks really sad with the massive red border
around it when you hover over it means to go back...

FYI:
You can also hit <ESCAPE> to go back...
        """)
        self.setStyleSheet("""
            QToolTip {
                background-color: black;
                color: white;
                border: black solid 1px
            }"""
        )

    def setButtonWidth(self, width):
        """
        Sets the accept/cancel buttons to a fixed width...
        """
        self.acceptButton().setFixedWidth(width)
        self.cancelButton().setFixedWidth(width)

    """ UTILS """
    def updateStyleSheet(self):
        style_sheet = """
{type}{{
    background-color: rgba{rgba_background_00};
}}
        """.format(
            type=type(self).__name__,
            rgba_background_00=iColor["rgba_background_00"]
        )

        self.setStyleSheet(style_sheet)

    """ PROPERTIES """
    def cancelButton(self):
        return self._cancel_button

    def acceptButton(self):
        return self._accept_button

    def widget(self):
        return self._widget

    def setWidget(self, widget):
        self._widget = widget

    def displayWidget(self):
        return self._display_widget

    def setDisplayWidget(self, display_widget):
        self.layout().itemAt(1).widget().setParent(None)
        self.layout().insertWidget(1, display_widget)
        self._display_widget = display_widget

    """ EVENTS (VIRTUAL) """
    def _accept_event(self, widget):
        pass

    def acceptEvent(self):
        self._accept_event(self.widget())
        self._closing = True
        self.close()

    def setAcceptEvent(self, accept_event):
        self._accept_event = accept_event

    def _cancel_event(self, widget):
        pass

    def cancelEvent(self):
        self._cancel_event(self.widget())
        self._closing = True
        self.close()

    def setCancelEvent(self, cancel_event):
        self._cancel_event = cancel_event

    """ EVENTS """
    def leaveEvent(self, event):
        if not self._closing:
            self.cancelEvent()
        QWidget.leaveEvent(self, event)

    def showEvent(self, event):
        centerWidgetOnScreen(self, height=self.display_height, width=self.display_width, resize=self.resize_on_show)
        self.updateStyleSheet()
        return QWidget.showEvent(self, event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.cancelEvent()
        elif event.key() in [Qt.Key_Enter, Qt.Key_Return]:
            self.acceptEvent()
        return QWidget.keyPressEvent(self, event)


if __name__ == '__main__':
    import sys
    from qtpy.QtWidgets import QApplication, QVBoxLayout, QPushButton
    from cgwidgets.utils import centerWidgetOnCursor, showWarningDialogue
    app = QApplication(sys.argv)

    def accept(widget):
        print('accept')

    def cancel(widget):
        print("cancel")

    def showWarningDialogueA(widget):
        display_widget = AbstractLabelWidget(text="SINE.")
        showWarningDialogue(widget, display_widget, accept, cancel)

    show_warning_button = AbstractButtonInputWidget()
    show_warning_button.setUserClickedEvent(showWarningDialogueA)

    #show_warning_button.clicked.connect(showWarningDialogue)
    test_label = AbstractLabelWidget(text="test")
    main_widget = QWidget()
    main_layout = QVBoxLayout(main_widget)
    main_layout.addWidget(show_warning_button)
    main_layout.addWidget(test_label)

    main_widget.show()
    centerWidgetOnCursor(main_widget)

    main_widget.resize(512, 512)

    sys.exit(app.exec_())
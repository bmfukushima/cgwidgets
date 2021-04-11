from qtpy.QtWidgets import QWidget, QHBoxLayout, QSizePolicy
from qtpy.QtCore import Qt

from cgwidgets.settings.colors import iColor
from cgwidgets.settings.icons import icons
from cgwidgets.utils import setAsTool, centerWidgetOnScreen
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

    Widgets:
        accept_button (QPushButton): When pressed, accepts the
            current event registered with setAcceptEvent.
        cancel_button (QPushButton): When pressed, cancels the
            current event registered with setCancelEvent.
        display_widget (QWidget): The central widget to be displayed
            to the user.
    """

    def __init__(self, parent=None, display_widget=None, button_width=100, width=1080, height=512, resize_on_show=True, widget=None):
        super(AbstractWarningWidget, self).__init__(parent)
        #self.main_widget = getMainWidget(self)

        # Create main layout
        QHBoxLayout(self)
        setAsTool(self)

        # setup default attrs
        if not button_width:
            self.setButtonWidth(100)

        self.display_height = height
        self.display_width = width
        self.resize_on_show = resize_on_show
        self._widget = widget

        # create text layout
        if not display_widget:
            text = "Provide display_widget kwarg to constructor \n or \n use setCentralWidget to display a widget here..."
            display_widget = AbstractLabelWidget(parent=self, text=text)
        self._display_widget = display_widget

        # create widgets
        accept_gif = icons["ACCEPT_GIF"]
        cancel_gif = icons["CANCEL_GIF"]
        self.accept_button = AbstractGIFWidget(accept_gif, hover_color=iColor["rgba_accept"])
        self.cancel_button = AbstractGIFWidget(cancel_gif, hover_color=iColor["rgba_cancel"])

        # setup style
        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.accept_button.setSizePolicy(size_policy)
        self.cancel_button.setSizePolicy(size_policy)

        self.accept_button.layout().setContentsMargins(0, 0, 0, 0)
        self.cancel_button.layout().setContentsMargins(0, 0, 0, 0)
        self.displayWidget().setContentsMargins(0, 0, 0, 0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        # setup events
        self.accept_button.setMousePressEvent(self.acceptEvent)
        self.cancel_button.setMousePressEvent(self.cancelEvent)

        # setup helpful tips
        self.setupButtonTooltips()

        # set up main layout
        self.layout().addWidget(self.cancel_button, 1)
        self.layout().addWidget(self._display_widget)
        self.layout().addWidget(self.accept_button, 1)
        self.layout().setAlignment(Qt.AlignTop)

    def setupButtonTooltips(self):
        """
        Creates the tooltips for the user on how to use these buttons
        when they hover over the widget.
        """
        self.accept_button.setToolTip("""
The happy af dog bouncing around that has a massive
green border around it when you hover over it means to continue.

FYI:
You can also hit <ENTER> and <RETURN> to continue...
        """)
        self.cancel_button.setToolTip("""
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
        self.accept_button.setFixedWidth(width)
        self.cancel_button.setFixedWidth(width)

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
        self.close()

    def setAcceptEvent(self, accept_event):
        self._accept_event = accept_event

    def _cancel_event(self, widget):
        pass

    def cancelEvent(self):
        self._cancel_event(self.widget())
        self.close()

    def setCancelEvent(self, cancel_event):
        self._cancel_event = cancel_event

    """ EVENTS """
    def showEvent(self, event):
        centerWidgetOnScreen(self, height=self.display_height, width=self.display_width, resize=self.resize_on_show)
        self.setFocus()
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
    from cgwidgets.utils import centerWidgetOnCursor
    app = QApplication(sys.argv)

    class warningShowButton(AbstractButtonInputWidget):
        def __init__(self, parent=None):
            super(warningShowButton, self).__init__(parent)
            self.setUserClickedEvent(self.showWarningDialogue)

        def showWarningDialogue(self, widget):
            from cgwidgets.utils import showWarningDialogue, centerCursorOnWidget
            display_widget = AbstractLabelWidget(text="SINE.")
            warning_widget = showWarningDialogue(self, display_widget, self.acceptEvent, self.cancelEvent)

        def acceptEvent(self, widget):
            print("accepted!", widget)

        def cancelEvent(self, widget):
            print("Firefly!!", widget)

    show_warning_button = warningShowButton()
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
from qtpy.QtWidgets import QWidget, QHBoxLayout, QSizePolicy
from qtpy.QtCore import Qt

from cgwidgets.settings.colors import iColor
from cgwidgets.settings.icons import icons
from cgwidgets.utils import setAsTool, centerWidgetOnScreen
from cgwidgets.widgets import AbstractLabelWidget
from cgwidgets.widgets.AbstractWidgets.AbstractGIFWidget import AbstractGIFWidget

class AbstractWarningWidget(QWidget):
    """
    Abstract widget that will require user input of
    Accepting / Canceling the current event that
    is proposed to them.

    The event can be accepted/denied with the buttons
    to the left/right of the widget, or with the esc / enter/return keys.

    Args:
        central_widget (QWidget): Central widget to be displayed
            to the user.  Can also be set with setCentralWidget.
        button_width (int): The width of the accept/cancel buttons.
        widget (QWidget): Widget that is calling the WarningWidget

    Widgets:
        accept_button (QPushButton): When pressed, accepts the
            current event registered with setAcceptEvent.
        cancel_button (QPushButton): When pressed, cancels the
            current event registered with setCancelEvent.
        central_widget (QWidget): The central widget to be displayed
            to the user.
    """

    def __init__(self, parent=None, central_widget=None, button_width=None, widget=None):
        super(AbstractWarningWidget, self).__init__(parent)
        #self.main_widget = getMainWidget(self)

        # Create main layout
        QHBoxLayout(self)
        setAsTool(self)

        # set widget
        self._widget = widget

        # create text layout
        if not central_widget:
            text = "Provide central_widget kwarg to constructor \n or \n use setCentralWidget to display a widget here..."
            self.central_widget = AbstractLabelWidget(parent=self, text=text)

        # create accept / cancel widgets
        """
        self.accept_button = QPushButton('=>')
        self.cancel_button = QPushButton('<=')
        self.accept_button.clicked.connect(self.acceptPressed)
        self.cancel_button.clicked.connect(self.cancelPressed)
        """
        accept_gif = icons["ACCEPT_GIF"]
        cancel_gif = icons["CANCEL_GIF"]
        self.accept_button = AbstractGIFWidget(accept_gif, hover_color=iColor["rgba_accept"])
        self.cancel_button = AbstractGIFWidget(cancel_gif, hover_color=iColor["rgba_cancel"])

        # setup accept / cancel widgets
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.accept_button.setSizePolicy(size_policy)
        self.cancel_button.setSizePolicy(size_policy)

        self.accept_button.setMousePressEvent(self.acceptEvent)
        self.cancel_button.setMousePressEvent(self.cancelEvent)

        self.setupButtonTooltips()

        # set up main layout
        self.layout().addWidget(self.cancel_button, 1)
        self.layout().addWidget(self.central_widget)
        self.layout().addWidget(self.accept_button, 1)

        self.layout().setAlignment(Qt.AlignTop)

        # set default button size
        if not button_width:
            self.setButtonWidth(100)

        self.updateStyleSheet()

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
    background-color: rgba{rgba_background_00}
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

    def setCentralWidget(self, central_widget):
        self.layout().itemAt(1).widget().setParent(None)
        self.layout().insertWidget(1, central_widget)
        self.central_widget = central_widget

    def getCentralWidget(self):
        return self.central_widget

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
        centerWidgetOnScreen(self)
        self.setFocus()
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

    warning_widget = AbstractWarningWidget()

    def acceptEvent(widget):
        print("accepted!")

    def cancelEvent(widget):
        print("Firefly!!")

    warning_widget.setAcceptEvent(acceptEvent)
    warning_widget.setCancelEvent(cancelEvent)


    """ Setup Main Display """
    def showPushButton():
        warning_widget = AbstractWarningWidget()

        def acceptEvent(widget):
            print("accepted!")

        def cancelEvent(widget):
            print("Firefly!!")

        warning_widget.setAcceptEvent(acceptEvent)
        warning_widget.setCancelEvent(cancelEvent)

        warning_widget.show()

    show_warning_button = QPushButton("show warning")
    show_warning_button.clicked.connect(showPushButton)
    test_label = AbstractLabelWidget(text="test")
    main_widget = QWidget()
    main_layout = QVBoxLayout(main_widget)
    main_layout.addWidget(show_warning_button)
    main_layout.addWidget(test_label)

    main_widget.show()
    centerWidgetOnCursor(main_widget)
    main_widget.resize(512, 512)

    sys.exit(app.exec_())
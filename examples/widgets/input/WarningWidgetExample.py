import sys
from qtpy.QtWidgets import QApplication, QVBoxLayout, QWidget
from cgwidgets.utils import centerWidgetOnCursor, showWarningDialogue

from cgwidgets.widgets import LabelWidget, ButtonInputWidget

app = QApplication(sys.argv)

# create warning button events
def accept(widget):
    """
    When the user accepts the event

    Args:
        widget (QWidget): original widget that caused the warning box to pop up
    """
    print('accept')

def cancel(widget):
    """
    When the user CANCELS the event

    Args:
        widget (QWidget): original widget that caused the warning box to pop up
    """
    print("cancel")

def showWarningDialogueA(widget):
    """
    Shows the actual warning widget

    Args:
        widget:

    Returns:

    """
    display_widget = LabelWidget(text="SINE.")
    showWarningDialogue(widget, display_widget, accept, cancel)

# create warning button
show_warning_button = ButtonInputWidget()
show_warning_button.setUserClickedEvent(showWarningDialogueA)

# create main widget
main_widget = QWidget()
main_layout = QVBoxLayout(main_widget)
main_layout.addWidget(show_warning_button)

# display widget
main_widget.show()
centerWidgetOnCursor(main_widget)
main_widget.resize(512, 512)

# exit
sys.exit(app.exec_())
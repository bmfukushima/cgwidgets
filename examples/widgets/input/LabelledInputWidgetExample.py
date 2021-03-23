import sys
from qtpy.QtWidgets import QApplication, QWidget, QVBoxLayout
from qtpy.QtGui import QCursor

from cgwidgets.widgets import LabelledInputWidget, FloatInputWidget
from cgwidgets.utils import getWidgetAncestor

app = QApplication(sys.argv)


def userInputEvent(widget, value):
    print('---- TOGGLE EVENT ----')
    print(widget, value)

class DynamicArgsInputWidget(LabelledInputWidget):
    """
    One individual arg

    TODO:
        Connect the signal changes in the line edit to where I'm going
        to store this JSON date type container thingy...

    """
    def __init__(self, parent=None, name='', note='', widget_type=FloatInputWidget):
        super(DynamicArgsInputWidget, self).__init__(parent, name=name, widget_type=FloatInputWidget)
        # setup args
        self.arg = name
        self.setToolTip(note)
        #self.setUserFinishedEditingEvent(self.userInputEvent)

    def setText(self, text):
        self.getInputWidget().setText(text)

    def text(self):
        return self.getInputWidget().text()

    def userInputEvent(self, widget, value):
        """
        When the user inputs something into the arg, this event is triggered
        updating the model item
        """
        print(widget, value)
        #main_widget = getWidgetAncestor(self, UserInputMainWidget)
        #main_widget.item().setArg(self.arg, value)

    @property
    def arg(self):
        return self._arg

    @arg.setter
    def arg(self, arg):
        self._arg = arg

test_labelled_embed = LabelledInputWidget(name="embed", widget_type=FloatInputWidget)
main_widget = DynamicArgsInputWidget(name="test", note="note")
#labelled_input = LabelledInputWidget(name="test", widget_type=test_labelled_embed)

main_widget.move(QCursor.pos())
main_widget.show()
main_widget.resize(500, 500)

sys.exit(app.exec_())
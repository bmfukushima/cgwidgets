from .AbstractInputWidgets import (
    AbstractInputGroup,
    AbstractFloatInputWidget,
    AbstractIntInputWidget,
    AbstractStringInputWidget,
    AbstractBooleanInputWidget
)


class InputGroup(AbstractInputGroup):
    def __init__(self, parent=None):
        super(InputGroup, self).__init__(parent)


class FloatInputWidget(AbstractFloatInputWidget):
    def __init__(self, parent=None):
        super(FloatInputWidget, self).__init__(parent)


class IntInputWidget(AbstractIntInputWidget):
    def __init__(self, parent=None):
        super(IntInputWidget, self).__init__(parent)


class StringInputWidget(AbstractStringInputWidget):
    def __init__(self, parent=None):
        super(StringInputWidget, self).__init__(parent)


class BooleanInputWidget(AbstractBooleanInputWidget):
    def __init__(self, parent=None):
        super(BooleanInputWidget, self).__init__(parent)


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication, QWidget, QVBoxLayout
    from qtpy.QtGui import QCursor
    app = QApplication(sys.argv)
    w = QWidget()
    l = QVBoxLayout(w)
    input_widget = AbstractFloatInputWidget()
    gw = AbstractInputGroup('cool stuff', input_widget)
    gw.getInputWidget().setUseLadder(True)
    gw.display_background = False
    l.addWidget(gw)

    w.resize(500, 500)
    w.show()
    w.move(QCursor.pos())
    sys.exit(app.exec_())

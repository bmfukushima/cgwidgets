from qtpy.QtWidgets import (
    QComboBox, QLineEdit, QCompleter, QSizePolicy
)

from qtpy.QtGui import(
    QStandardItem, QStandardItemModel
)
from qtpy.QtCore import (
    QEvent, Qt, QSortFilterProxyModel
)

from qtpy.QtWidgets import QSplitter, QLabel, QFrame, QBoxLayout, QLineEdit
from qtpy.QtCore import Qt

from cgwidgets.widgets import (
    FloatInputWidget,
    IntInputWidget,
    StringInputWidget,
    BooleanInputWidget,
    GroupInputWidget,
    ListInputWidget,
    FrameInputWidget
)


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication, QWidget, QVBoxLayout
    from qtpy.QtGui import QCursor
    app = QApplication(sys.argv)
    w = QWidget()
    l = QVBoxLayout(w)
    testwidget = QLabel()
    testwidget.setText('init')
    l.addWidget(testwidget)

    def test(widget, value):
        print(widget, value)
        #widget.setText(str(value))

    """ group insert """
    gw = GroupInputWidget(parent=None, title='cool stuff')

    # add user inputs
    gw.insertInputWidget(0, FloatInputWidget, 'Float', test, data={'name':'Float'})
    gw.insertInputWidget(0, IntInputWidget, 'Int', test, data={'name':'Int'})
    gw.insertInputWidget(0, BooleanInputWidget, 'Boolean', test, data={'name':'Boolean'})
    gw.insertInputWidget(0, StringInputWidget, 'String', test, data={'name':'String'})
    gw.insertInputWidget(0, ListInputWidget, 'List', test, data={'items_list':['a','b','c','d']})

    gw.display_background = False
    l.addWidget(gw)

    """ normal widgets """
    float_input_widget = FloatInputWidget()
    float_input_widget.setUseLadder(True)
    int_input_widget = IntInputWidget()
    boolean_input_widget = BooleanInputWidget()
    string_input_widget = StringInputWidget()
    list_input_widget = ListInputWidget()

    l.addWidget(float_input_widget)
    l.addWidget(int_input_widget)
    l.addWidget(boolean_input_widget)
    l.addWidget(string_input_widget)
    l.addWidget(list_input_widget)

    float_input_widget.setUserFinishedEditingEvent(test)
    int_input_widget.setUserFinishedEditingEvent(test)
    boolean_input_widget.setUserFinishedEditingEvent(test)
    string_input_widget.setUserFinishedEditingEvent(test)
    list_input_widget.setUserFinishedEditingEvent(test)

    """ Label widgets """
    u_float_input_widget = FrameInputWidget(name="float", widget_type=FloatInputWidget)
    u_int_input_widget = FrameInputWidget(name="int", widget_type=IntInputWidget)
    u_boolean_input_widget = FrameInputWidget(name="bool", widget_type=BooleanInputWidget)
    u_string_input_widget = FrameInputWidget(name='str', widget_type=StringInputWidget)
    u_list_input_widget = FrameInputWidget(name='list', widget_type=ListInputWidget)

    l.addWidget(u_float_input_widget)
    l.addWidget(u_int_input_widget)
    l.addWidget(u_boolean_input_widget)
    l.addWidget(u_string_input_widget)
    l.addWidget(u_list_input_widget)

    u_float_input_widget.setUserFinishedEditingEvent(test)
    u_int_input_widget.setUserFinishedEditingEvent(test)
    u_boolean_input_widget.setUserFinishedEditingEvent(test)
    u_string_input_widget.setUserFinishedEditingEvent(test)
    u_list_input_widget.setUserFinishedEditingEvent(test)

    w.resize(500, 500)
    w.show()
    w.move(QCursor.pos())

    sys.exit(app.exec_())

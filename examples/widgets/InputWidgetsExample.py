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
    from qtpy.QtWidgets import (
        QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox)
    from qtpy.QtGui import QCursor
    app = QApplication(sys.argv)

    # testwidget = QLabel()
    # testwidget.setText('init')
    # l.addWidget(testwidget)
    list_of_crap = [
        ['a', (0, 0, 0, 255)], ['b', (0, 0, 0, 255)], ['c', (0, 0, 0, 255)], ['d', (0, 0, 0, 255)], ['e', (0, 0, 0, 255)],
        ['aa', (255, 0, 0, 255)], ['bb', (0, 255, 0, 255)], ['cc', (0, 0, 255, 255)], ['dd'], ['ee'],
        ['aba'], ['bcb'], ['cdc'], ['ded'], ['efe']
    ]
    l2 = [['a', (255, 0, 0, 255)], ['b'], ['c'], ['aa'], ['bb'], ['cc']]

    def test(widget, value):
        print(widget, value)
        #widget.setText(str(value))

    """ group insert """
    group_widget_layout = QVBoxLayout()
    gw = GroupInputWidget(parent=None, title='cool stuff')

    # add user inputs
    gw.insertInputWidget(0, FloatInputWidget, 'Float', test)
    gw.insertInputWidget(0, IntInputWidget, 'Int', test)
    gw.insertInputWidget(0, BooleanInputWidget, 'Boolean', test)
    gw.insertInputWidget(0, StringInputWidget, 'String', test)
    gw.insertInputWidget(0, ListInputWidget, 'List', test, data={'items_list':list_of_crap})

    gw.display_background = False
    group_widget_layout.addWidget(gw)

    """ normal widgets """
    normal_widget = QGroupBox()
    normal_widget.setTitle("Normal Widgets")
    normal_widget_layout = QVBoxLayout(normal_widget)

    float_input_widget = FloatInputWidget()
    float_input_widget.setUseLadder(True)
    int_input_widget = IntInputWidget()
    boolean_input_widget = BooleanInputWidget()
    string_input_widget = StringInputWidget()
    list_input_widget = ListInputWidget(item_list=list_of_crap)

    normal_widget_layout.addWidget(float_input_widget)
    normal_widget_layout.addWidget(int_input_widget)
    normal_widget_layout.addWidget(boolean_input_widget)
    normal_widget_layout.addWidget(string_input_widget)
    normal_widget_layout.addWidget(list_input_widget)

    float_input_widget.setUserFinishedEditingEvent(test)
    int_input_widget.setUserFinishedEditingEvent(test)
    boolean_input_widget.setUserFinishedEditingEvent(test)
    string_input_widget.setUserFinishedEditingEvent(test)
    list_input_widget.setUserFinishedEditingEvent(test)

    """ Label widgets """
    horizontal_label_widget = QGroupBox()
    horizontal_label_widget.setTitle("Frame Widgets (Horizontal)")
    horizontal_label_widget_layout = QVBoxLayout(horizontal_label_widget)

    u_float_input_widget = FrameInputWidget(name="float", widget_type=FloatInputWidget)
    u_int_input_widget = FrameInputWidget(name="int", widget_type=IntInputWidget)
    u_boolean_input_widget = FrameInputWidget(name="bool", widget_type=BooleanInputWidget)
    u_string_input_widget = FrameInputWidget(name='str', widget_type=StringInputWidget)
    u_list_input_widget = FrameInputWidget(name='list', widget_type=ListInputWidget)
    u_list_input_widget.getInputWidget().populate(list_of_crap)
    u_list_input_widget.getInputWidget().display_item_colors = True

    horizontal_label_widget_layout.addWidget(u_float_input_widget)
    horizontal_label_widget_layout.addWidget(u_int_input_widget)
    horizontal_label_widget_layout.addWidget(u_boolean_input_widget)
    horizontal_label_widget_layout.addWidget(u_string_input_widget)
    horizontal_label_widget_layout.addWidget(u_list_input_widget)

    u_float_input_widget.setUserFinishedEditingEvent(test)
    u_int_input_widget.setUserFinishedEditingEvent(test)
    u_boolean_input_widget.setUserFinishedEditingEvent(test)
    u_string_input_widget.setUserFinishedEditingEvent(test)
    u_list_input_widget.setUserFinishedEditingEvent(test)

    """ FRAME INPUT WIDGETS"""
    q = FrameInputWidget(name="Float", widget_type=FloatInputWidget)
    q.setDirection(Qt.Vertical)
    e = FrameInputWidget(name="List", widget_type=ListInputWidget)
    e.getInputWidget().populate(list_of_crap)
    e.setDirection(Qt.Vertical)
    t = FrameInputWidget(name="Bool", widget_type=BooleanInputWidget)
    t.setDirection(Qt.Vertical)
    # l.addWidget(q)
    # l.addWidget(t)
    # l.addWidget(e)
    # main_widget = ListInputWidget()
    # main_widget.populate(['a','b','c','d'])
    #main_widget.setInputBaseClass(ListInputWidget)

    """ Main Widget"""
    main_widget = QWidget()
    main_layout = QHBoxLayout(main_widget)
    main_layout.addLayout(group_widget_layout)
    main_layout.addWidget(normal_widget)
    main_layout.addWidget(horizontal_label_widget)

    main_widget.resize(500, 500)
    main_widget.show()
    main_widget.move(QCursor.pos())

    sys.exit(app.exec_())


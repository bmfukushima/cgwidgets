
from cgwidgets.widgets import FloatInputWidget, IntInputWidget
from qtpy.QtWidgets import QLabel, QApplication


from cgwidgets.widgets.LadderWidget import LadderWidget


if __name__ == '__main__':
    import sys
    from qtpy.QtWidgets import QApplication
    from qtpy.QtCore import QEvent
    from qtpy.QtGui import QCursor
    app = QApplication(sys.argv)

    def finishedEditing(widget, value):
        print('------ FINISHED EDITING --------')
        print(widget, value)

    def liveEditing(widget, value):
        print('------ LIVE EDITING --------')
        print(widget, value)

    # create main widget
    main_widget = FloatInputWidget()
    main_widget.setUseLadder(
        True,
        user_input=QEvent.MouseButtonRelease,
        value_list=[0.01, 5, 1.0, 10],)
    main_widget.setValue(92.0)
    # main_widget.setLiveInputEvent(liveEditing)
    main_widget.setUserFinishedEditingEvent(finishedEditing)
    main_widget.setRange(True, 0.0, 100.0)
    main_widget.setAllowNegative(True)

    # show widget
    main_widget.show()
    main_widget.move(QCursor.pos())
    sys.exit(app.exec_())
from qtpy.QtWidgets import QLabel, QWidget, QHBoxLayout
from qtpy.QtCore import Qt

from cgwidgets.settings.colors import iColor
from cgwidgets.settings import stylesheets
from cgwidgets.widgets import LabelledInputWidget, FloatInputWidget, TansuGroupInputWidget
from cgwidgets.views import TansuView
from cgwidgets.utils import getWidgetAncestor

if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication
    from qtpy.QtGui import QCursor
    app = QApplication(sys.argv)


    class FloatLadderInputWidget(FloatInputWidget):
        def __init__(self, parent=None):
            super(FloatLadderInputWidget, self).__init__(parent)
            self.setUseLadder(True)

    # add user inputs
    class RadialGradientInputWidget(TansuGroupInputWidget):
        def __init__(self,
            parent=None,
            name="None",
            note="None",
            direction=Qt.Vertical
        ):
            super(RadialGradientInputWidget, self).__init__(parent, name, note, direction)
            self.insertInputWidget(0, FloatLadderInputWidget, 'radius', self.updateStyleSheet,
                                          user_live_update_event=self.liveEdit)

            self.setIsHeaderShown(False)

        @staticmethod
        def updateStyleSheet(widget, value):
            print('finished editing??!??!?')
            print(widget, value)
            # style_sheet = stylesheets.createRadialGradientSS(value, (0.5, 0.5), (0.75, 0.75), stops)
            # style_sheet = style_sheet.format(**iColor.style_sheet_args)
            # main_widget = getWidgetAncestor(widget, RadialGradientInputWidget)
            # main_widget.parent().widget(2).setStyleSheet(style_sheet)
            #return style_sheet

        @staticmethod
        def liveEdit(widget, value):
            print("LIVE?!??!?")
            print(widget, value)


    radial_gradient_wigdet = RadialGradientInputWidget()

    # setup view
    stops = [
        [0.5, "rgba_selected_hover"],
        [0.75, "rgba_gray_0"],
        [0.95, "rgba_red_3"]
    ]
    style_sheet = stylesheets.createRadialGradientSS(0.5, (0.5, 0.5), (0.75, 0.75), stops)
    style_sheet = style_sheet.format(**iColor.style_sheet_args)

    view_widget = QLabel()

    test_widget = LabelledInputWidget(widget_type=FloatLadderInputWidget)
    #view_widget.setStyleSheet(style_sheet)


    # create main widget
    main_widget = TansuView()
    main_widget.addWidget(test_widget)
    main_widget.addWidget(radial_gradient_wigdet)
    # main_widget.addWidget(view_widget)

    # show widget
    main_widget.show()
    main_widget.move(QCursor.pos())
    sys.exit(app.exec_())

# a = """ {{{test}}}""".format(test="yolo")
#
# b = a.format(yolo='penis')
# print(b)
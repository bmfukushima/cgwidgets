from qtpy.QtWidgets import QLabel, QWidget, QHBoxLayout
from qtpy.QtCore import Qt

from cgwidgets.settings.colors import iColor
from cgwidgets.settings import stylesheets, hover_display
from cgwidgets.widgets import LabelledInputWidget, FloatInputWidget, ShojiGroupInputWidget, FrameGroupInputWidget
from cgwidgets.views import ShojiView
from cgwidgets.utils import getWidgetAncestor

if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication, QSplitter, QLineEdit
    from qtpy.QtGui import QCursor
    app = QApplication(sys.argv)


    class FloatLadderInputWidget(FloatInputWidget):
        def __init__(self, parent=None):
            super(FloatLadderInputWidget, self).__init__(parent)
            self.setUseLadder(True, value_list=[0.0001, 0.001, 0.01, 0.1])

    # add user inputs
    class RadialGradientInputWidget(ShojiGroupInputWidget):
        def __init__(self,
            parent=None,
            direction=Qt.Vertical
        ):
            name = "Radial Gradient"
            super(RadialGradientInputWidget, self).__init__(parent, name, direction=direction)
            self.cx = 0.5
            self.cy = 0.5
            self.fx = 0.5
            self.fy = 0.5
            self.radius = 0.5
            self.stops = [
                [0.5, "rgba_selected_hover"],
                [0.75, "rgba_gray_0"],
                [0.95, "rgba_red_3"]
            ]
            inputs = ["cx", "cy", "fx", "fy", "radius"] #, stops"""

            for i in inputs:
                self.insertInputWidget(0, FloatLadderInputWidget, i, self.asdf,
                                          user_live_update_event=self.liveEdit, default_value=0.5)

            tansu_view = self.getInputWidget().delegateWidget()
            tansu_view.setIsSoloViewEnabled(False)
            tansu_view.setIsHandleStatic(True)
            tansu_view.setHandleWidth(0)
            tansu_view.setHandleLength(-1)
            tansu_view.setHandleMarginOffset(0)
            tansu_view.updateStyleSheet()

            for index, child in enumerate(tansu_view.children()):
                tansu_view.setStretchFactor(index, 0)
            tansu_view.setStretchFactor(index, 1)

        @staticmethod
        def asdf(item, widget, value):
            return
            #print('finished editing??!??!?')
            #print(widget, value)
            # style_sheet = stylesheets.createRadialGradientSS(value, (0.5, 0.5), (0.75, 0.75), stops)
            # style_sheet = style_sheet.format(**iColor.style_sheet_args)
            # main_widget = getWidgetAncestor(widget, RadialGradientInputWidget)
            # main_widget.parent().widget(2).setStyleSheet(style_sheet)
            #return style_sheet

        @staticmethod
        def liveEdit(item, widget, value):
            this_widget = getWidgetAncestor(widget, RadialGradientInputWidget)

            name = item.columnData()['name']

            # update style sheet values
            if name == 'radius':
                this_widget.radius = value
            if name == 'cx':
                this_widget.cx = value
            if name == 'cy':
                this_widget.cy = value
            if name == 'fx':
                this_widget.fx = value
            if name == 'fy':
                this_widget.fy = value

            style_sheet = stylesheets.createRadialGradientSS(
                this_widget.radius,
                (this_widget.cx, this_widget.cy),
                (this_widget.fx, this_widget.fy),
                this_widget.stops
            )
            style_sheet = style_sheet.format(**iColor.style_sheet_args)

            this_widget.parent().widget(1).setStyleSheet(style_sheet)


    radial_gradient_wigdet = RadialGradientInputWidget()

    # setup view
    view_widget = QLabel()
    style_sheet = stylesheets.createRadialGradientSS(
        radial_gradient_wigdet.radius,
        (radial_gradient_wigdet.cx, radial_gradient_wigdet.cy),
        (radial_gradient_wigdet.fx, radial_gradient_wigdet.fy),
        radial_gradient_wigdet.stops
    )
    style_sheet = style_sheet.format(**iColor.style_sheet_args)
    view_widget.setStyleSheet(style_sheet)

    # # create main widget
    main_widget = ShojiView()
    main_widget.addWidget(radial_gradient_wigdet)
    main_widget.addWidget(view_widget)

    # main_widget = radial_gradient_wigdet
    # # show widget
    proxy_widget = QWidget()
    proxy_layout = QHBoxLayout(proxy_widget)
    proxy_layout.addWidget(main_widget)

    proxy_widget.resize(500, 500)
    proxy_widget.show()
    proxy_widget.move(QCursor.pos())


    # widget = QLineEdit("Test")
    # hover_display.installHoverDisplaySS(
    #     widget,
    #     hover_type=hover_display.TEST,
    #     focus_type=hover_display.TEST,
    #     hover_focus_type=hover_display.TEST,
    #     focus=True,
    #     hover=True,
    #     hover_focus=True,
    #     hover_type_flags={'focus':{}, 'hover_focus':{}, 'hover':{}})
    #
    # widget.show()
    sys.exit(app.exec_())

# a = """ {{{test}}}""".format(test="yolo")
#
# b = a.format(yolo='penis')
# print(b)
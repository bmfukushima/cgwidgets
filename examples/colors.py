from cgwidgets.settings.colors import iColor
from cgwidgets.widgets import AbstractListInputWidget
from cgwidgets.widgets.AbstractWidgets.AbstractListInputWidget import CompleterPopup
if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication
    from qtpy.QtGui import QCursor
    app = QApplication(sys.argv)

    # create colors list
    item_list = []
    for name, color in iColor.items():
        name = "{name} {color}".format(name=name, color=color)
        item_list.append([name, color])
    r = AbstractListInputWidget(item_list=item_list)
    r.display_item_colors = True

    # setup main widget
    main_widget = CompleterPopup()
    main_widget.setModel(r.proxy_model)

    # show widget
    main_widget.show()
    main_widget.move(QCursor.pos())
    sys.exit(app.exec_())
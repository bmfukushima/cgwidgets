from cgwidgets.widgets import AbstractPiPWidget


class PiPWidget(AbstractPiPWidget):
    """
    The PiPWidget is designed to display multiple widgets simultaneously to the user.

    Similar to the function that was provided to TV's in the mid 1970's.  This widget is
    designed to allow the user to create multiple hot swappable widgets inside of the same
    widget.

    Args:

    Attributes:
        current_widget (QWidget): the widget that is currently set as the main display
        direction (attrs.DIRECTION): what side the mini viewer will be displayed on.
        pip_scale ((float, float)):  fractional percentage of the amount of space that
            the mini viewer will take up in relation to the overall size of the widget.
        swap_key (Qt.KEY): this key will trigger the popup
        widgets (list): of widgets

    Hierarchy:
        |- PiPMainWidget --> QWidget
        |    |- QVBoxLayout
        |    |    |- PiPMainViewer --> QWidget
        |    |    |- PiPPanelCreatorWidget --> AbstractListInputWidget
        |    |- MiniViewer (QWidget)
        |        |- QBoxLayout
        |            |-* PiPMiniViewerWidget --> QWidget
        |                    |- QVBoxLayout
        |                    |- AbstractLabelledInputWidget
        |- LocalOrganizerWidget --> AbstractModelViewWidget
        |- CreatorWidget (Extended...)
        |- GlobalOrganizerWidget --> AbstractModelViewWidget
        |- SettingsWidget --> FrameInputWidgetContainer

    Signals:
        Swap (Enter):
            Upon user cursor entering a widget, that widget becomes the main widget

            PiPMiniViewer --> EventFilter --> EnterEvent
                - swap widget
                - freeze swapping (avoid recursion)
            PiPMiniViewer --> LeaveEvent
                - unfreeze swapping
        Swap (Key Press):
            Upon user key press on widget, that widget becomces the main widget
            PiPMainWidget --> keyPressEvent --> setCurrentWidget
        Swap Previous (Key Press)
            Press ~, main widget is swapped with previous main widget
            PiPMainWidget --> keyPressEvent --> setCurrentWidget
        Quick Drag ( Drag Enter ):
            Upon user drag enter, the mini widget becomes large to allow easier dropping
            PiPMiniViewer --> EventFilter --> Drag Enter
                                          --> Enter
                                          --> Drop
                                          --> Drag Leave
                                          --> Leave
        HotSwap (Key Press 1-5):
            PiPMainWidget --> keyPressEvent --> setCurrentWidget
        Toggle previous widget
            PiPMainWidget --> keyPressEvent --> swapWidgets
        Toggle Organizer Widget (Q):
            keyPressEvent --> toggleLocalOrganizerVisibility
        Create New Widget -->
        Delete Widget -->
        TempWidgets
            Temp widgets will be created and destroyed when the total number of widgets is
            less than the minimum number needed to properly displayed the PiPWidget (2).
            These widgets will then act as place holders for the display, which cannot
            be removed.
                createTempWidget()
                tempWidgets()
                removeTempWidget()

        PanelCreatorWidget:
            show (c):
                keyPressEvent --> toggleCreatorVisibility --> show
            hide (esc)
    """

    def __init__(self, parent=None, widget_types=None, save_data=None):
        super(PiPWidget, self).__init__(parent, widget_types=widget_types, save_data=save_data)
        #, widget_types=widget_types


if __name__ == '__main__':
    import sys
    import os

    os.environ['QT_API'] = 'pyside2'
    from qtpy import API_NAME

    from qtpy.QtWidgets import (QWidget, QHBoxLayout, QApplication, QListWidget, QAbstractItemView, QPushButton)
    from cgwidgets.utils import centerWidgetOnCursor
    from cgwidgets.utils import attrs

    app = QApplication(sys.argv)

    # PiP Widget
    widget_types = {
        "QLabel": """
from qtpy.QtWidgets import QLabel
widget = QLabel(\"TEST\") """,
        "QPushButton":"""
from qtpy.QtWidgets import QPushButton
widget = QPushButton(\"TESTBUTTON\") """
    }
    pip_widget = PiPWidget(widget_types=widget_types)

    pip_widget.setPiPScale((0.25, 0.25))
    pip_widget.setEnlargedScale(0.75)
    pip_widget.setDirection(attrs.WEST)
    pip_widget.showWidgetDisplayNames(False)

    # Main Widget
    main_widget = QWidget()

    main_layout = QHBoxLayout(main_widget)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.addWidget(pip_widget)
    #main_layout.addWidget(drag_drop_widget)

    main_widget.show()
    centerWidgetOnCursor(main_widget)
    main_widget.resize(512, 512)

    sys.exit(app.exec_())
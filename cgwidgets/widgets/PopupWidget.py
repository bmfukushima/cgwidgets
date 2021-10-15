from qtpy.QtCore import Qt

from cgwidgets.widgets import (
    AbstractPiPOrganizerWidget,
    AbstractPiPDisplayWidget,
    AbstractPopupBarWidget,
    AbstractPopupBarItemWidget,
    AbstractPopupBarDisplayWidget)
from cgwidgets.settings import attrs


class PiPDisplayWidget(AbstractPiPDisplayWidget):
    """The PiPWidget is designed to display multiple widgets simultaneously to the user.

    Similar to the function that was provided to TV's in the mid 1970's.  This widget is
    designed to allow the user to create multiple hot swappable widgets inside of the same
    widget.

    Attributes:
        current_widget (QWidget): the widget that is currently set as the main display
        direction (attrs.DIRECTION): what side the mini viewer will be displayed on.
        hotkey_swap_key (list): of Qt.Key that will swap to the corresponding widget in the popupBarWidget().

            The index of the Key in the list, is the index of the widget that will be swapped to.
        is_popup_bar_widget (bool): determines if this is a child of a PopupBarWidget.
        is_popup_bar_shown (bool): if the mini viewer is currently visible.
            This is normally toggled with the "Q" key
        is_standalone (bool): determines if this is a child of the PiPAbstractOrganizer.
            If True, this means that this display is a standalone..
        pip_scale ((float, float)):  fractional percentage of the amount of space that
            the mini viewer will take up in relation to the overall size of the widget.
        swap_key (Qt.KEY): this key will trigger the popup
        widgets (list): of widgets
    """

    def __init__(self, parent=None, is_popup_bar_widget=False):
        super(PiPDisplayWidget, self).__init__(parent)


class PiPOrganizerWidget(AbstractPiPOrganizerWidget):
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
        |    |    |- PiPPopupBarWidgetCreator --> AbstractListInputWidget
        |    |- PopupBar (QWidget)
        |        |- QBoxLayout
        |            |-* PiPPopupBarWidget --> QWidget
        |                    |- QVBoxLayout
        |                    |- AbstractLabelledInputWidget
        |- LocalOrganizerWidget --> AbstractModelViewWidget
        |- CreatorWidget (Extended...)
        |- GlobalOrganizerWidget --> AbstractModelViewWidget
        |- SettingsWidget --> FrameInputWidgetContainer

    Signals:
        Swap (Enter):
            Upon user cursor entering a widget, that widget becomes the main widget

            PiPPopupBar --> EventFilter --> EnterEvent
                - swap widget
                - freeze swapping (avoid recursion)
            PiPPopupBar --> LeaveEvent
                - unfreeze swapping
        Swap (Key Press):
            Upon user key press on widget, that widget becomces the main widget
            PiPMainWidget --> keyPressEvent --> setCurrentWidget
        Swap Previous (Key Press)
            Press ~, main widget is swapped with previous main widget
            PiPMainWidget --> keyPressEvent --> setCurrentWidget
        Quick Drag ( Drag Enter ):
            Upon user drag enter, the mini widget becomes large to allow easier dropping
            PiPPopupBar --> EventFilter --> Drag Enter
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
        super(PiPOrganizerWidget, self).__init__(parent, widget_types=widget_types, save_data=save_data)
        #, widget_types=widget_types


class PopupBarDisplayWidget(AbstractPopupBarDisplayWidget):
    def __init__(self, parent=None):
        super(PopupBarDisplayWidget, self).__init__(parent)


class PopupBarWidget(AbstractPopupBarWidget):
    """
    Widget that contains all of the PiPWidgets.

    This widget is an overlay of the MainWidget, and sits at a parallel hierarchy to the PiPMainViewer

    Attributes:
        direction (attrs.DIRECTION): direction that the popup will be displayed on
        display_mode (PopupBarWidget.TYPE): Determines what type of widget this should be displayed as
            valid options are
                PIP | PIPTASKBAR | TASKBAR
            The PIP mode will be displayed over an existing widget.  While the TASKBAR mode will be displayed
            as a standalone widget.
        is_dragging (bool): determines if this widget is currently in a drag/drop operation
        is_enlarged (bool): If there is currently an widget enlarged.
            Widgets are enlarged by the user hovering over them.  And closed
            be pressing "esc" or having the mouse exit the boundries of the widget.
        if_frozen (bool): Determines if events should be handled or not.

        enlarged_widget (QWidget): The widget that is currently enlarged
        overlay_widget (QWidget): Widget that the popup will be overlaid on.  If none is specified,
            then this will return the main window.
        popup_widget (QWidget): The widget that is displayed if the enlarged widget
            has opened a subwidget (popup) menu.
        spacer_widget (QLabel): Widget that holds the space in the QSplitter where
            the currently enlarged widget normally lives.
        __temp_sizes (list): of ints, that are the sizes of the individual widgets.
            This is normally gotten through the "sizes()" call, but needs a temp one,
            for swapping the spacer widget in/out.
        __last_object_entered (PopupBarItemWidget): placeholder to determine the last object
            that was entered.  This is mainly used when enlarging widgets to ensure that the
            enlarged widget can be entered, as if the bounds are not great enough, you can enter
            the Main Viewer, thus closing the enlarged widget.
        widgets (list): Of PopupBarWidget widgets that are currently displayed.
            This does not include the currently enlarged widget
    """
    def __init__(self, parent=None, direction=attrs.EAST, orientation=Qt.Vertical, overlay_widget=None):
        super(PopupBarWidget, self).__init__(parent=parent, direction=direction, orientation=orientation, overlay_widget=overlay_widget)


class PopupBarItemWidget(AbstractPopupBarItemWidget):
    """
    One PiP Widget that is displayed in the PopupBarWidget

    Attributes:
        index (int): current index in model
        item (PopupBarWidgetOrganizerItem)
    """

    def __init__(
            self,
            parent=None,
            name="None",
            direction=Qt.Horizontal,
            delegate_widget=None,
            is_pip_widget=False
    ):
        super(PopupBarItemWidget, self).__init__(
            parent=parent,
            name=name,
            direction=direction,
            delegate_widget=delegate_widget,
            is_pip_widget=is_pip_widget)


if __name__ == '__main__':
    import sys
    import os

    os.environ['QT_API'] = 'pyside2'
    from qtpy import API_NAME

    from qtpy.QtWidgets import (QWidget, QHBoxLayout, QApplication, QListWidget, QAbstractItemView, QPushButton)
    from cgwidgets.utils import centerWidgetOnCursor
    from cgwidgets.settings import attrs

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
    pip_widget = PiPOrganizerWidget(widget_types=widget_types)

    pip_widget.setPiPScale((0.25, 0.25))
    pip_widget.setEnlargedScale(0.75)
    pip_widget.setDirection(attrs.WEST)
    pip_widget.setIsDisplayNamesShown(False)

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
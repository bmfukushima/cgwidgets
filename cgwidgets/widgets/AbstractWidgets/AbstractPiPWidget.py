"""
Todo:
    * keyPressEvent... does not register until 2 widgets or so??
        in general shitty registry...
    * show organizer...
        - exit mini view... somehow swaps?
            registry is wrong?
        - west calculation also fucked on that...
    * Overall cleanup / organization
        mainWidget --> AbstractPiPWidget?
    * Expose settings to user?
    * Organizer...
        - Settup API
        - Save/Load JSON's
            - how does this even work...
    * PiPMiniViewerWidget --> Borders... styles not working???
        - base style sheet added to ShojiLayout...
            in general the shoji layout needs to be more flexible

"""
import json

from qtpy.QtWidgets import (
    QStackedLayout, QWidget, QBoxLayout, QVBoxLayout, QLabel, QSizePolicy, QSplitter, QHBoxLayout)
from qtpy.QtCore import QEvent, Qt, QPoint
from qtpy.QtGui import QCursor

from cgwidgets.views import AbstractDragDropModelItem
from cgwidgets.utils import attrs, getWidgetUnderCursor, isWidgetDescendantOf, getWidgetAncestor, getDefaultSavePath
from cgwidgets.settings.hover_display import installHoverDisplaySS, removeHoverDisplay
from cgwidgets.settings.colors import iColor

from cgwidgets.widgets.AbstractWidgets.AbstractLabelledInputWidget import AbstractLabelledInputWidget
from cgwidgets.widgets.AbstractWidgets.AbstractOverlayInputWidget import AbstractOverlayInputWidget
from cgwidgets.widgets.AbstractWidgets.AbstractModelViewWidget import AbstractModelViewWidget
from cgwidgets.widgets import AbstractListInputWidget, AbstractButtonInputWidget, AbstractStringInputWidget, AbstractLabelWidget


class AbstractPiPWidget(QSplitter):
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
        |    |- QHBoxLayout
        |    |    |- PiPMainViewer --> QWidget
        |    |- MiniViewer (QWidget)
        |        |- QBoxLayout
        |            |-* PiPMiniViewerWidget --> QWidget
        |                    |- QVBoxLayout
        |                    |- AbstractLabelledInputWidget
        |- OrganizerWidget --> ModelViewWidget

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
            keyPressEvent --> toggleOrganizerVisibility
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
    """
    def __init__(self, parent=None, widget_types=None):
        super(AbstractPiPWidget, self).__init__(parent)
        # setup default attrs
        self.setOrientation(Qt.Horizontal)
        self._temp_widgets = []
        if not widget_types:
            widget_types = []

        # create widgets
        # create main pip widget
        self._main_widget = PiPMainWidget(self, widget_types)

        # setup organizer widget
        self._organizer_widget = PiPOrganizerWidget(self)
        self._is_organizer_visible = False
        self._organizer_widget.hide()

        # setup creator widget visibility
        self._is_panel_creator_visible = False

        # add widgets
        self.addWidget(self._main_widget)
        self.addWidget(self._organizer_widget)

        # create temp widget
        self.createTempWidget()
        self.createTempWidget()

    """ UTILS """
    def numWidgets(self):
        return len(self.widgets())

    def widgets(self):
        return [index.internalPointer().widget() for index in self.organizerWidget().model().getAllIndexes() if hasattr(index.internalPointer(), "_widget")]

    def items(self):
        return [index.internalPointer() for index in self.organizerWidget().model().getAllIndexes() if hasattr(index.internalPointer(), "_widget")]

    """ WIDGETS (DISPLAY)"""
    def mainWidget(self):
        return self._main_widget

    def miniViewerWidget(self):
        return self.mainWidget().mini_viewer

    def mainViewerWidget(self):
        return self.mainWidget().main_viewer

    def organizerWidget(self):
        return self._organizer_widget

    def panelCreatorWidget(self):
        return self.mainWidget().panel_creator_widget

    """ WIDGETS """
    def createNewWidget(self, widget, constructor_code, name=""):
        """

        Args:
            widget:
            name:

        Returns:

        """
        if 0 < self.numWidgets():
            mini_widget = self.miniViewerWidget().createNewWidget(widget, name=name)
        else:
            mini_widget = PiPMiniViewerWidget(self, direction=Qt.Vertical, delegate_widget=widget, name=name)
            self.mainWidget().setCurrentWidget(mini_widget)

        # create new index
        # if create_index:
        index = self.organizerWidget().model().insertNewIndex(0, name=name)
        mini_widget.setIndex(0)
        item = index.internalPointer()
        item.setWidget(mini_widget)
        item.setConstructorCode(constructor_code)
        # update indexes
        self.updateWidgetIndexes()

        # # destroy temp widgets
        if 2 < self.numWidgets():
            if name != "":
                self.removeTempWidget()
        #
        # print (self.tempWidgets())

        self.mainWidget().resizeMiniViewer()
        return index

    def updateWidgetIndexes(self):
        """
        Runs through all of the widgets and resets their indexes.

        This will need to be done every time a new widget is added
        """
        for index in self.organizerWidget().model().getAllIndexes():
            item = index.internalPointer()
            if hasattr(item, "_widget"):
                item.widget().setIndex(index.row())

    # """ WIDGETS (TEMP)"""
    def createTempWidget(self):
        constructor_code = """
        from qtpy.QtWidgets import QLabel
        constructor = QLabel """
        text = """
        (A): Open widget organizer, to create new widgets, save widgets, etc """
        index = self.createNewWidget(AbstractLabelWidget(self, text), constructor_code, "")
        item = index.internalPointer()
        item.setIsSelectable(False)
        item.setIsDragEnabled(False)
        item.setIsEnabled(False)

    def removeTempWidget(self):
        """
        Removes the first temp widget from the tempWidgets list
        """
        model = self.organizerWidget().model()
        indexes = model.findItems("", match_type=Qt.MatchExactly)
        if 0 < len(indexes):
            model.deleteItem(indexes[0].internalPointer(), event_update=True)

    """ SAVE (VIRTUAL) """
    def setSavePath(self, file_path):
        self.organizerWidget().saveWidget().setSaveFilePath(file_path)

    """ VIRTUAL FUNCTIONS (MAIN WIDGET)"""
    def direction(self):
        return self.mainWidget().direction()

    def setDirection(self, direction):
        self.mainWidget().setDirection(direction)

    def swapKey(self):
        return self.mainWidget().swapKey()

    def setSwapKey(self, key):
        self.mainWidget().setSwapKey(key)

    def pipScale(self):
        return self.mainWidget().pipScale()

    def setPiPScale(self, pip_scale):
        self.mainWidget().setPiPScale(pip_scale)

    def enlargedScale(self):
        return self.mainWidget().enlargedScale()

    def setEnlargedScale(self, _enlarged_scale):
        self.mainWidget().setEnlargedScale(_enlarged_scale)

    def showWidgetNames(self, enabled):
        self.mainWidget().showWidgetNames(enabled)

    def currentWidget(self):
        return self.mainWidget().currentWidget()

    def setCurrentWidget(self, current_widget):
        self.mainWidget().setCurrentWidget(current_widget)

    def previousWidget(self):
        return self.mainWidget().previousWidget()

    def setPreviousWidget(self, previous_widget):
        self.mainWidget().setPreviousWidget(previous_widget)

    """ ORGANIZER / CREATOR """
    def isOrganizerVisible(self):
        return self._is_organizer_visible

    def setIsOrganizerVisible(self, visible):
        self._is_organizer_visible = visible

    def toggleOrganizerVisibility(self):
        """
        Toggles whether or not the organizer widget is visible to the user

        Note: This is currently hard coded to "Q"
        """

        # if self.miniViewerWidget()._is_frozen:
        if self.miniViewerWidget().isEnlarged():
            obj = getWidgetUnderCursor(QCursor.pos())
            widget = getWidgetAncestor(obj, PiPMiniViewerWidget)
            self.miniViewerWidget().closeEnlargedView(widget)

        self._is_organizer_visible = not self.isOrganizerVisible()
        if self.isOrganizerVisible():
            self.organizerWidget().show()
        else:
            self.organizerWidget().hide()

    def isPanelCreatorVisible(self):
        return self._is_panel_creator_visible

    def setIsPanelCreatorVisible(self, visible):
        self._is_panel_creator_visible = visible

    def toggleCreatorVisibility(self):
        """
        Toggles whether or not the organizer widget is visible to the user

        Note: This is currently hard coded to "Q"
        """

        # if self.miniViewerWidget()._is_frozen:
        if not self.isPanelCreatorVisible():
            if self.miniViewerWidget().isEnlarged():
                obj = getWidgetUnderCursor(QCursor.pos())
                widget = getWidgetAncestor(obj, PiPMiniViewerWidget)
                self.miniViewerWidget().closeEnlargedView(widget)

            self._is_panel_creator_visible = not self.isPanelCreatorVisible()
            if self.isPanelCreatorVisible():
                self.panelCreatorWidget().show()
                self.panelCreatorWidget().setFocus()
        # else:
        #     #self.panelCreatorWidget().clearFocus()
        #     self.panelCreatorWidget().hide()
        #     self.setFocus()

    """ EVENTS """
    def keyPressEvent(self, event):
        print('abstract')
        if event.key() == Qt.Key_A:
            self.toggleOrganizerVisibility()

        if event.key() == Qt.Key_C:
            self.toggleCreatorVisibility()

        return QSplitter.keyPressEvent(self, event)


class PiPMainWidget(QWidget):
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

    """

    def __init__(self, parent=None, widget_types=None):
        super(PiPMainWidget, self).__init__(parent)

        # setup attrs
        self._widgets = []
        if not widget_types:
            widget_types = []
        self._current_widget = None
        self._previous_widget = None
        self._pip_scale = (0.35, 0.35)
        self._enlarged_scale = 0.55
        self._direction = attrs.SOUTH
        self._swap_key = 96

        # create widgets
        self.main_viewer = PiPMainViewer(self)
        self.mini_viewer = PiPMiniViewer(self)
        self.panel_creator_widget = PiPCreateNewPanelWidget(self, widget_types=widget_types)
        self.panel_creator_widget.hide()

        # create layout
        """
        Not using a stacked layout as the enter/leave events get borked
        """
        #QStackedLayout(self)
        QVBoxLayout(self)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        #self.layout().addWidget(self.mini_viewer)
        self.layout().addWidget(self.main_viewer)
        self.layout().addWidget(self.panel_creator_widget)

        self.setStyleSheet("background-color:rgba(255,0,255,255);")

    """ UTILS (SWAP) """
    def swapWidgets(self):
        """
        Swaps the previous widget with the current widget.

        This allows the user to quickly swap between two widgets.
        """
        if self.previousWidget():
            self.setCurrentWidget(self.previousWidget())

    def swapKey(self):
        return self._swap_key

    def setSwapKey(self, key):
        self._swap_key = key

    """ UTILS """
    def pipScale(self):
        return self._pip_scale

    def setPiPScale(self, pip_scale):
        if isinstance(pip_scale, float):
            pip_scale = (pip_scale, pip_scale)

        self._pip_scale = pip_scale
        self.resizeMiniViewer()

    def enlargedScale(self):
        return self._enlarged_scale

    def setEnlargedScale(self, _enlarged_scale):
        self._enlarged_scale = _enlarged_scale

    def resizeMiniViewer(self):
        """
        Main function for resizing the mini viewer
        """
        w = self.main_viewer.width()
        h = self.main_viewer.height()
        num_widgets = self.mini_viewer.layout().count()

        if num_widgets == 0:
            self.mini_viewer.hide()
            return
        else:
            self.mini_viewer.show()
            # xpos = 0
            # ypos = 0
            # height = h
            # width = w

        if num_widgets == 1:
            height = h * self.pipScale()[1]
            width = w * self.pipScale()[0]
            if self.direction() in [attrs.EAST, attrs.WEST]:
                if self.direction() == attrs.EAST:
                    ypos = 0
                    xpos = w * (1 - self.pipScale()[0])
                if self.direction() == attrs.WEST:
                    ypos = h * (1 - self.pipScale()[1])
                    xpos = 0

            if self.direction() in [attrs.NORTH, attrs.SOUTH]:
                if self.direction() == attrs.SOUTH:
                    xpos = w * (1 - self.pipScale()[0])
                    ypos = h * (1 - self.pipScale()[1])
                if self.direction() == attrs.NORTH:
                    xpos = 0
                    ypos = 0

        if 1 < num_widgets:
            pip_offset = 1 - self.pipScale()[0]
            # set position
            if self.direction() in [attrs.EAST, attrs.WEST]:
                height = h
                width = w * self.pipScale()[0]
                if self.direction() == attrs.EAST:
                    ypos = 0
                    xpos = w * pip_offset
                if self.direction() == attrs.WEST:
                    ypos = 0
                    xpos = 0

            if self.direction() in [attrs.NORTH, attrs.SOUTH]:
                height = h * self.pipScale()[1]
                width = w
                if self.direction() == attrs.NORTH:
                    xpos = 0
                    ypos = 0
                if self.direction() == attrs.SOUTH:
                    xpos = 0
                    ypos = h * pip_offset

        # move/resize mini viewer
        self.mini_viewer.move(int(xpos), int(ypos))
        self.mini_viewer.setFixedSize(int(width), int(height))
        self.mini_viewer.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def areWidgetNamesShown(self):
        return self._are_widget_names_shown

    def showWidgetNames(self, enabled):
        self._are_widget_names_shown = enabled
        for widget in self.parent().widgets():
            if enabled:
                widget.main_widget.viewWidget().show()
            else:
                widget.main_widget.viewWidget().hide()

    """ WIDGETS """
    def removeWidget(self, widget):
        #self.widgets().remove(widget)
        widget.setParent(None)
        widget.deleteLater()

    def currentWidget(self):
        return self._current_widget

    def setCurrentWidget(self, widget):
        """
        Sets the current full screen widget

        Args:
            widget (QWidget): widget to be set as full screen
        """
        # reset current widget
        if self._current_widget:
            self._current_widget.setParent(None)
            self.mini_viewer.addWidget(self._current_widget)
            self.setPreviousWidget(self._current_widget)

        # set widget as current
        self._current_widget = widget
        self.mini_viewer.removeWidget(widget)
        self.main_viewer.setWidget(widget)

    def previousWidget(self):
        return self._previous_widget

    def setPreviousWidget(self, widget):
        self._previous_widget = widget

    """ DIRECTION """
    def direction(self):
        return self._direction

    def setDirection(self, direction):
        self._direction = direction
        if direction in [attrs.EAST, attrs.WEST]:
            self.mini_viewer.setDirection(QBoxLayout.TopToBottom)
        elif direction in [attrs.NORTH, attrs.SOUTH]:
            self.mini_viewer.setDirection(QBoxLayout.LeftToRight)

    """ EVENTS """
    def resizeEvent(self, event):
        self.resizeMiniViewer()

        return QWidget.resizeEvent(self, event)

    def keyPressEvent(self, event):
        print('main')
        # swap between this and previous
        if event.key() == 96:
            # pre flight
            widget = getWidgetUnderCursor()
            if widget == self.mini_viewer: return

            # swap previous widget widgets
            is_descendant_of_main_viewer = isWidgetDescendantOf(widget, self.currentWidget())
            if widget == self or is_descendant_of_main_viewer:
                self.swapWidgets()
                return QWidget.keyPressEvent(self, event)

            # set widget under cursor as current
            is_descendant_of_main_widget = isWidgetDescendantOf(widget, self)
            if is_descendant_of_main_widget:
                swap_widget = getWidgetAncestor(widget, PiPMiniViewerWidget)
                self.setCurrentWidget(swap_widget)
                self.mini_viewer.setIsEnlarged(False)
                return QWidget.keyPressEvent(self, event)

        # hotkey swapping
        if event.key() in [Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4, Qt.Key_5]:
            try:
                if event.key() == Qt.Key_1:
                    widget = self.mini_viewer.layout().itemAt(0).widget()
                if event.key() == Qt.Key_2:
                    widget = self.mini_viewer.layout().itemAt(1).widget()
                if event.key() == Qt.Key_3:
                    widget = self.mini_viewer.layout().itemAt(2).widget()
                if event.key() == Qt.Key_4:
                    widget = self.mini_viewer.layout().itemAt(3).widget()
                if event.key() == Qt.Key_5:
                    widget = self.mini_viewer.layout().itemAt(4).widget()
                self.setCurrentWidget(widget)

            except AttributeError:
                # not enough widgets
                pass

        # hide PiP
        if event.key() == Qt.Key_Space:
            self.mini_viewer.hide()
            return

        # escape
        if event.key() == Qt.Key_Escape:
            if self.mini_viewer.isEnlarged():
                obj = getWidgetUnderCursor(QCursor.pos())
                widget = getWidgetAncestor(obj, PiPMiniViewerWidget)
                self.mini_viewer.closeEnlargedView(widget)
                # self.mini_viewer.setIsEnlarged(False)

        return QWidget.keyPressEvent(self, event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.mini_viewer.show()
            return
        return QWidget.keyReleaseEvent(self, event)


class PiPMainViewer(QWidget):
    def __init__(self, parent=None):
        super(PiPMainViewer, self).__init__(parent)
        QVBoxLayout(self)
        self.layout().setContentsMargins(0, 0, 0, 0)

    def setWidget(self, widget):
        self.layout().addWidget(widget)
        widget.layout().setContentsMargins(0, 0, 0, 0)


class PiPMiniViewer(QWidget):
    def __init__(self, parent=None):
        super(PiPMiniViewer, self).__init__(parent)
        #QBoxLayout(QBoxLayout.LeftToRight, self)
        QVBoxLayout(self)
        # self.layout().setContentsMargins(0, 0, 0, 0)

        self._widgets = []
        self._is_frozen = False
        self._is_exiting = False
        self._is_enlarged = False
        self._temp = False

    def isEnlarged(self):
        return self._is_enlarged

    def setIsEnlarged(self, enabled):
        self._is_enlarged = enabled

    """ EVENTS """
    def eventFilter(self, obj, event):
        """

        Args:
            obj:
            event:

        Returns:

        Note:
            _is_frozen (bool): flag to determine if the UI should be frozen for updates
            _temp (bool): flag to determine if this is exiting into a widget that will be moved,
                and then another widget will be in its place.
            _enlarged_object (PiPMiniViewerWidget): when exiting, this is the current object that has
                been enlarged for use.
            _entered_object (PiPMiniViewerWidget): when exiting, this is the object that is under the cursor
                if the user exits into the MiniViewerWidget

        """
        if event.type() in [QEvent.DragEnter, QEvent.Enter]:
            # catch a double exit.
            """
            If the user exits on the first widget, or a widget that will be the enlarged widget,
            it will recurse back and enlarge itself.  This will block that recursion
            """
            if hasattr(self, "_temp") and hasattr(self, "_enlarged_object"):
                if self._enlarged_object == obj:
                    self._is_exiting = True
                    return True
            # enlarge widget
            if not self._is_frozen:
                main_widget = getWidgetAncestor(self, PiPMainWidget)
                self.setIsEnlarged(True)
                # freeze
                self._is_frozen = True

                # set/get attrs
                scale = main_widget.enlargedScale()
                negative_space = 1 - scale
                half_neg_space = negative_space * 0.5
                num_widgets = main_widget.parent().numWidgets()
                # self.hide()

                # reparent widget
                obj.setParent(main_widget)

                # get widget position / size
                if main_widget.direction() == attrs.EAST:
                    xpos = int(main_widget.width() * (negative_space - half_neg_space))
                    ypos = int(main_widget.height() * half_neg_space)
                if main_widget.direction() == attrs.WEST:
                    xpos = 0
                    ypos = int(main_widget.height() * half_neg_space)
                if main_widget.direction() == attrs.NORTH:
                    xpos = int(main_widget.width() * half_neg_space)
                    ypos = 0
                if main_widget.direction() == attrs.SOUTH:
                    xpos = int(main_widget.width() * half_neg_space)
                    ypos = int(main_widget.height() * (negative_space - half_neg_space))
                # show widget
                obj.show()

                # move / resize
                obj.move(xpos, ypos)
                if main_widget.direction() in [attrs.SOUTH, attrs.NORTH]:
                    obj.resize(int(main_widget.width() * scale), int(main_widget.height() * (scale + half_neg_space)))
                if main_widget.direction() in [attrs.EAST, attrs.WEST]:
                    obj.resize(int(main_widget.width() * (scale + half_neg_space)), int(main_widget.height() * scale))

                # move cursor
                if main_widget.direction() in [attrs.NORTH, attrs.WEST]:
                    if num_widgets == 2 and main_widget.direction() == attrs.WEST:
                        QCursor.setPos(self.mapToGlobal(
                            QPoint(
                                xpos + int(main_widget.width() * scale * 0.5),
                                ypos - int(main_widget.height() * scale * 0.5))))
                    if 2 < num_widgets:
                        QCursor.setPos(self.mapToGlobal(
                            QPoint(
                                xpos + int(main_widget.width() * scale * 0.5),
                                ypos + int(main_widget.height() * scale * 0.5))))

                if main_widget.direction() == attrs.SOUTH:
                    # if only one mini viewer widget
                    if num_widgets == 2:
                        QCursor.setPos(self.mapToGlobal(
                            QPoint(
                                xpos - int(main_widget.width() * scale * 0.5),
                                ypos - int(main_widget.height() * scale * 0.5))))
                    # if more than one mini viewer widget
                    if 2 < num_widgets:
                        QCursor.setPos(self.mapToGlobal(
                            QPoint(
                                xpos + int(main_widget.width() * scale * 0.5),
                                ypos - int(main_widget.height() * scale * 0.5))))

                if main_widget.direction() == attrs.EAST:
                    QCursor.setPos(self.mapToGlobal(
                        QPoint(
                            xpos - int(main_widget.width() * scale * 0.5),
                            ypos + int(main_widget.height() * scale * 0.5))))

                # unfreeze
                self._is_frozen = False

                # # drag enter
                if event.type() == QEvent.DragEnter:
                    event.accept()

        elif event.type() in [QEvent.Drop, QEvent.DragLeave, QEvent.Leave]:
            self.closeEnlargedView(obj)
        return False

    def closeEnlargedView(self, obj):
        """
        Closes the enlarged viewer, and returns it back to normal PiP mode

        Args:
            obj:

        Returns:
        """
        widget_under_cursor = getWidgetUnderCursor(QCursor.pos())
        under_mini_viewer = isWidgetDescendantOf(widget_under_cursor, self)
        # avoid exit recursion when exiting over existing widgets
        if self._is_exiting:
            if hasattr(self, "_entered_object") and hasattr(self, "_temp"):
                if self._enlarged_object == obj:
                    self._is_frozen = False
                    self._is_exiting = False
                    delattr(self, "_temp")
                    return True
                if self._entered_object == obj:
                    self._is_frozen = False
                    self._is_exiting = False
                    self._temp = True
                    return True

        # exiting
        if not self._is_frozen:
            self._is_frozen = True
            self.addWidget(obj)

            if under_mini_viewer:
                self._is_exiting = True
                self._enlarged_object = obj
                self._entered_object = getWidgetAncestor(widget_under_cursor, PiPMiniViewerWidget)
            else:
                self._is_frozen = False

            self.setIsEnlarged(False)

    """ DIRECTION """
    def setDirection(self, direction):
        self.layout().setDirection(direction)

    """ WIDGETS """
    def addWidget(self, widget):
        self.layout().insertWidget(widget.index(), widget)
        widget.installEventFilter(self)

        # installHoverDisplaySS(
        #     widget,
        #     name="PIP")

    def createNewWidget(self, widget, name=""):
        """
        Creates a new widget in the mini widget.  This is only when a new widget needs to be instantiated.

        Args:
            widget:
            name:

        Returns (PiPMiniViewerWidget):
        """
        mini_widget = PiPMiniViewerWidget(self, direction=Qt.Vertical, delegate_widget=widget, name=name)
        self.layout().insertWidget(0, mini_widget)
        mini_widget.installEventFilter(self)
        return mini_widget

    def removeWidget(self, widget):
        self.layout().removeWidget(widget)
        widget.removeEventFilter(self)


class PiPMiniViewerWidget(QWidget):
    """
    One PiP Widget that is displayed in the PiPMiniViewer

    Attributes:
        index (int): current index in model
    """
    def __init__(
        self,
        parent=None,
        name="None",
        direction=Qt.Horizontal,
        delegate_widget=None,
    ):
        super(PiPMiniViewerWidget, self).__init__(parent)
        QVBoxLayout(self)
        self._index = 0

        self.main_widget = AbstractLabelledInputWidget(self, name=name, direction=direction, delegate_widget=delegate_widget)
        self.layout().addWidget(self.main_widget)
        # self.layout().setContentsMargins(0, 0, 0, 0)
        base_style_sheet = """
        {type}{{
            background-color: rgba{rgba_background};
            color: rgba{rgba_text};
            border: 2px solid rgba{rgba_border};
        }}""".format(
            rgba_background=repr(self.main_widget.rgba_background),
            rgba_border=iColor["rgba_background_01"],
            rgba_text=repr(self.main_widget.rgba_text),
            type=type(self.main_widget).__name__,
        )
        self.main_widget.setBaseStyleSheet(base_style_sheet)

        self.setAcceptDrops(True)
        # installHoverDisplaySS(self, "TEST")

    def index(self):
        return self._index

    def setIndex(self, index):
        self._index = index

""" Create Widgets"""
class PiPModelItem(AbstractDragDropModelItem):
    def __init__(self, parent=None):
        super(PiPModelItem, self).__init__(parent)

    def widget(self):
        return self._widget

    def setWidget(self, widget):
        self._widget = widget

    def constructorCode(self):
        return self._constructor_code

    def setConstructorCode(self, constructor_code):
        self._constructor_code = constructor_code


class PiPOrganizerWidget(AbstractModelViewWidget):
    """
    This widget is in charge of creating/destroying PiP items, along with
    holding the order that the items should be displayed in.

    Attributes:
        widget_types (dict): of widget names / constructors
            {"name": constructor,
            "QLabel": QLabel,
            "QPushButton":QPushButton}

    Signals:
        Create New Widget -->
        Delete Widget -->
    """
    def __init__(self, parent=None, widget_types=None):
        super(PiPOrganizerWidget, self).__init__(parent=parent)
        # setup default attrs
        self._widget_types = widget_types

        # setup model
        # model = PiPOrganizerModel(self)
        # self.setModel(model)
        self.model().setItemType(PiPModelItem)

        # create save widget
        self._save_widget = PiPOrganizerSaveWidget(self)
        self.addDelegate([Qt.Key_S], self._save_widget)
        self._save_widget.show()

        # install events
        self.setItemDeleteEvent(self.deleteWidget)
        self.setTextChangedEvent(self.editWidget)
        self.setDropEvent(self.itemReordered)

    def proxyModel(self):
        return self._proxy_model

    def setProxyModel(self, proxy_model):
        self._proxy_model = proxy_model

    def sourceModel(self):
        return self._source_model

    def setSourceModel(self, source_model):
        self._source_model = source_model

    def saveWidget(self):
        return self._save_widget

    """ EVENTS """
    def itemReordered(self, data, items, model, row, parent):
        """
        When an item is drag/dropped, this will update the widget indexes, and reinsert
        the widget into the mini viewer if it is not currently the active widget.
        """
        # get default attrs
        main_widget = getWidgetAncestor(self, AbstractPiPWidget)
        mini_viewer = main_widget.miniViewerWidget()
        widget = items[0].widget()

        # if in mini viewer
        # reset parent and insert back into mini viewer
        if widget.parent() == mini_viewer:
            widget.setParent(None)
            widget.setIndex(row)
            mini_viewer.addWidget(widget)

        # update all widget indexes
        main_widget.updateWidgetIndexes()

    def editWidget(self, item, old_value, new_value):
        item.widget().main_widget.setName(new_value)

    def deleteWidget(self, item):
        """
        When an item is deleted, the corresponding widget is removed from the PiPViewer.

        If the item deleted is the currently viewed item, the previously viewed item will
        automatically be set as the currently viewed item, and if that doesn't exist,
        it will set it to the first widget it can find.

        Args:
            item (to be deleted):
        """
        # get widget
        widget = item.widget()

        # get current widget
        main_widget = getWidgetAncestor(self, AbstractPiPWidget)

        # if current widget
        current_widget = main_widget.currentWidget()
        if widget == current_widget:
            # get first useable widget
            first_widget = main_widget.widgets()[0]
            if first_widget == widget:
                first_widget = main_widget.widgets()[1]

            # set current widget
            if main_widget.previousWidget():
                main_widget.setCurrentWidget(main_widget.previousWidget())
            else:
                main_widget.setCurrentWidget(first_widget)

            # remove previous widget
            main_widget.setPreviousWidget(None)

        # create temp widget
        if main_widget.numWidgets() < 3:
            main_widget.createTempWidget()

        # delete widget
        item.widget().setParent(None)
        item.widget().deleteLater()
        # resize
        main_widget.mainWidget().resizeMiniViewer()

    """ EVENTS """
    def showEvent(self, event):
        main_widget = getWidgetAncestor(self, AbstractPiPWidget)
        main_widget.setIsOrganizerVisible(True)
        self.setFocus()
        AbstractModelViewWidget.showEvent(self, event)

    def hideEvent(self, event):
        main_widget = getWidgetAncestor(self, AbstractPiPWidget)
        main_widget.setIsOrganizerVisible(False)
        main_widget.setFocus()
        AbstractModelViewWidget.hideEvent(self, event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.hide()
        return AbstractModelViewWidget.keyPressEvent(self, event)


class PiPOrganizerSaveWidget(QWidget):
    """
    constructor is a required arg in the constructor code
    {PiPName: [
        {"widget name": "constructor code"},
        {"widget name": "constructor code"},
        {"widget name": "constructor code"},]
    }
    """
    def __init__(self, parent=None):
        super(PiPOrganizerSaveWidget, self).__init__(parent)
        QVBoxLayout(self)
        # todo name needs to be a list delegate and load all of the current names
        name_list = AbstractListInputWidget(self)
        name_list.dynamic_update = True
        name_list.setCleanItemsFunction(self.getAllPiPWidgetsNames)
        self._name_widget = AbstractLabelledInputWidget(name="Name", delegate_widget=name_list)
        self._save_button = AbstractButtonInputWidget(self, title="Save")

        self.layout().addWidget(self._name_widget)
        self.layout().addWidget(self._save_button)

        self._file_path = getDefaultSavePath() + '/.PiPWidgets.json'
        # dcc name
        # pip name
        self._save_button.setUserClickedEvent(self.savePiPWidget)

    def getAllPiPWidgetsNames(self):
        widgets_list = [[name] for name in list(self.loadPiPWidgets().keys())]

        return widgets_list

    def loadPiPWidgets(self):
        from cgwidgets.utils import getJSONData
        return getJSONData(self.saveFilePath())

    def savePiPWidget(self, this):
        """
        When the "Save" button is pressed, this will save the current PiPWidget to the master
        PiPDictionary located at self.saveFilePath()

        Args:
            this (AbstractButtonInputWidget): being pressed

        Returns:

        """
        main_widget = getWidgetAncestor(self, AbstractPiPWidget)
        main_widget.items()
        name = self._name_widget.delegateWidget().text()
        pip_widgets = self.loadPiPWidgets()

        # create pip save dict
        #pip_save_file = {}
        from collections import OrderedDict
        pip_widgets[name] = OrderedDict()
        for item in main_widget.items():
            item_name = item.columnData()['name']
            item_code = item.constructorCode()
            pip_widgets[name][item_name] = item_code

        # save pip file
        if self.saveFilePath():
            # Writing JSON data
            with open(self.saveFilePath(), 'w') as f:
                json.dump(pip_widgets, f)

        print('saving to... ', self.saveFilePath())
        print(pip_widgets)

    def saveFilePath(self):
        return self._file_path

    def setSaveFilePath(self, file_path):
        self._file_path = file_path


class PiPCreateNewPanelWidget(AbstractListInputWidget):
    def __init__(self, parent=None, widget_types=None):
        super(PiPCreateNewPanelWidget, self).__init__(parent)

        self._widget_types = widget_types
        self.populate([[key] for key in widget_types.keys()])
        #self.setUserFinishedEditingEvent(self.createNewWidget)

    def widgetTypes(self):
        return self._widget_types

    def setWidgetTypes(self, widget_types):
        self._widget_types = widget_types

    def createNewWidget(self):
        # preflight
        value = self.text()

        if value not in self.widgetTypes().keys(): return
        main_widget = getWidgetAncestor(self, AbstractPiPWidget)

        # get constructor
        loc = {}
        exec(self.widgetTypes()[value], globals(), loc)
        constructor = loc['constructor']

        widget_type = constructor(self)
        main_widget.createNewWidget(widget_type, self.widgetTypes()[value], name=str(value))
        # widget = index.internalPointer().widget()

        # reset widget
        self.setText('')
        self.hide()
        self.clearFocus()

    """ EVENTS """
    def showEvent(self, event):
        main_widget = getWidgetAncestor(self, AbstractPiPWidget)
        main_widget.setIsPanelCreatorVisible(True)
        self.setFocus()
        AbstractListInputWidget.showEvent(self, event)

    def hideEvent(self, event):
        main_widget = getWidgetAncestor(self, AbstractPiPWidget)
        main_widget.setIsPanelCreatorVisible(False)
        main_widget.setFocus()
        AbstractListInputWidget.hideEvent(self, event)

    def keyPressEvent(self, event):
        from cgwidgets.settings import keylist
        if event.key() in keylist.ACCEPT_KEYS:
            self.createNewWidget()
        if event.key() == Qt.Key_Escape:
            self.hide()
        return AbstractListInputWidget.keyPressEvent(self, event)


if __name__ == '__main__':
    import sys
    from qtpy.QtWidgets import (QApplication, QListWidget, QAbstractItemView, QPushButton)
    from cgwidgets.utils import centerWidgetOnCursor
    app = QApplication(sys.argv)

    # PiP Widget
    widget_types = {
        "QLabel": """
from qtpy.QtWidgets import QLabel
constructor = QLabel""",
        "QPushButton":"""
from qtpy.QtWidgets import QPushButton
constructor = QPushButton"""
    }
    pip_widget = AbstractPiPWidget(widget_types=widget_types)

#     for x in ("SINE"):
#         child = QLabel(str(x))
#         child.setAlignment(Qt.AlignCenter)
#         child.setStyleSheet("color: rgba(255,255,255,255);")
#         pip_widget.createNewWidget(child, """
# from qtpy.QtWidgets import QLabel
# constructor = QLabel""", name=str(x))

    pip_widget.setPiPScale((0.2, 0.2))
    pip_widget.setEnlargedScale(0.75)
    pip_widget.setDirection(attrs.WEST)
    #pip_widget.showWidgetNames(False)

    #

    # Drag/Drop Widget
    # drag_drop_widget = QListWidget()
    # drag_drop_widget.setDragDropMode(QAbstractItemView.DragDrop)
    # drag_drop_widget.addItems(['a', 'b', 'c', 'd'])
    # drag_drop_widget.setFixedWidth(100)

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
"""
TODO
    Move this into custom LineEdit with model/completer.  Similair to the
    AbstractFileBrowser currently located in KatanaBebop
    * FilterCompletionResults
        tf is this doing... supposed to suppress the results.  So that if it's set to false, it will
        always show all of the options... this seems like a stupid idea
"""
from qtpy.QtWidgets import (
    QComboBox, QSizePolicy, QLineEdit, QCompleter, QStyledItemDelegate, QApplication)
from qtpy.QtGui import(
    QStandardItem, QStandardItemModel, QPixmap, QIcon, QColor)
from qtpy.QtCore import (QEvent, QAbstractListModel, Qt, QSortFilterProxyModel, QRegExp)

from cgwidgets.widgets.AbstractWidgets import AbstractStringInputWidget
from cgwidgets.utils import getBottomLeftPos, getFontSize
from cgwidgets.settings import iColor
from cgwidgets.views.CompleterView import CompleterPopup


class AbstractListInputWidget(AbstractStringInputWidget):
    """
    Signals:
    QLineEdit
        QCompleter
            | -- QSortFilterProxyModel --> QAbstractListModel (Custom Model)
            | -- Popup
                    | -- QListView (CompleterPopup)
    Attributes:
        dynamic_update (bool): Determines if the model should be repopulated
            every time the user requests the popup to be displayed
        filter_results (bool): Determines if the returned results in the popup
            should be filtered based off of the current input.
        display_item_colors (bool): Determines if the item colors should be displayed
            or not.  By default this is set to off.  Item colors will need to be put as the
            second index for each item in the model provided to the list.
        item_list (list): string list of all of the items in the list.  Updating this
            will auto update the default settings for blank setups
        previous_text (str): the previous items text.  This is stored for cancel events
            and allowing the user to return to the previous item after cancelling.
        cleanItems (virtual function): returns a list of items to populate the
            model with.  Not sure if I still need this...
    """
    TYPE = 'list'

    def __init__(self, parent=None, item_list=None):
        super(AbstractListInputWidget, self).__init__(parent)
        # setup default attrs
        if not item_list:
            item_list = ['']
        self._item_list = item_list
        self._previous_text = ''
        self._dynamic_update = False
        self._filter_results = True
        self._display_item_colors = False
        self.proxy_model = QSortFilterProxyModel()

        # setup custom completer
        self.setupCustomModelCompleter(item_list)

        # setup style
        self.updateStyleSheet()

        # setup signals
        # self.textChanged.connect(self.filterCompletionResults)

    def populate(self, item_list):
        """
        Creates all of the items from the item list and
        appends them to the model.

        item_list (list): list of strings to be displayed to the user
            this should be set with the setCleanItemsFunction.
        """
        self.setItemList(item_list)
        self.setupCustomModelCompleter(item_list)

    def __getCleanItems(self):
        return []

    def setCleanItemsFunction(self, function):
        """
        Sets the function to get the list of strings to populate the model

        function (function): function to return a list of strings to be shown
            to the user
        """
        self.__getCleanItems = function

    def getCleanItems(self):
        """
        Returns a list of strings based off of the function set with
        setCleanItemsFunction
        """
        return self.__getCleanItems()

    """ COMPLETER """
    def _updateModel(self, item_list=None):
        # get item list
        if not item_list:
            item_list = self.getCleanItems()

        # update model items
        self.setItemList(item_list)
        self._model = CustomModel(item_list=item_list)
        self._model.display_item_colors = self.display_item_colors

        #self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self._model)

        # set models
        self.completer().setModel(self.proxy_model)

        # set item for popup
        # this makes it so that the stylesheet can be attached...
        # https://forum.qt.io/topic/26703/solved-stylize-using-css-and-editable-qcombobox-s-completions-list-view/7
        delegate = QStyledItemDelegate()
        self.completer().popup().setItemDelegate(delegate)

    #     self.completer().activated.connect(self.test)
    #     self.completer().highlighted.connect(self.test2)
    #
    # def test(self, string):
    #     print('testing', string)
    #
    # def test2(self, string):
    #     print('higlights', string)

    def setupCustomModelCompleter(self, item_list):
        """
        Creates a new completely custom completer

        Args:
            item_list (list): of strings to be the list of things
                that is displayed to the user
        """
        # create completer/models
        completer = CustomModelCompleter()
        self.setCompleter(completer)
        self._updateModel(item_list)

    # seems to force it to only options that are currently in the list?
    def filterCompletionResults(self):
        """
        Filter the current proxy model based off of the text in the input string

        This will filter AS the user types... rather than filtering AFTER the user
        finishes typing...
        """
        # preflight
        if self.filter_results:
            regExp = QRegExp("({text})".format(text=self.text()))
            self.proxy_model.setFilterRegExp(regExp)
        else:
            self.completer().setCompletionMode(QCompleter.UnfilteredPopupCompletion)

    """ EVENTS """
    def mouseReleaseEvent(self, event, *args, **kwargs):

        self.showCompleter()
        return AbstractStringInputWidget.mouseReleaseEvent(self, event, *args, **kwargs)

    def keyPressEvent(self, event):
        """
        Suppress enter keypress event when the pop up is visible.  This will allow the user to press enter,
        without it registering the setting of the text event...
        """

        #
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            if self.completer().popup().isVisible():
                self.setIsFrozen(True)
                QLineEdit.keyPressEvent(self, event)
                self.setIsFrozen(False)
                return

        # resolve
        super(AbstractStringInputWidget, self).keyPressEvent(event)

        #
        self.filterCompletionResults()

        # show ALL items when deleting to empty
        if event.key() == Qt.Key_Delete or event.key() == Qt.Key_Backspace:
            if self.text() == "":
                self.completer().setCompletionMode(QCompleter.UnfilteredPopupCompletion)
                self.completer().complete()

    def showCompleter(self):
        """
        Displays the popup completer to the user
        Args:
            filter_results (bool): determines if the results should be filtered
                based off of the users current input. The default value for this is True
        """
        # update model (if enabled)
        if self.dynamic_update:
            self._updateModel()

        # filter completion results
        # if self.filter_results:
        self.filterCompletionResults()

        if self.text() == "":
            item_list = self.itemList()
            self.setupCustomModelCompleter(item_list)

        self.completer().complete()

    """ UTILS """
    def next_completion(self):
        row = self.completer().currentRow()

        # if does not exist reset
        if not self.completer().setCurrentRow(row + 1):
            self.completer().setCurrentRow(0)

        # if initializing
        if self.completer().popup().currentIndex().row() == -1:
            self.completer().setCurrentRow(0)

        index = self.completer().currentIndex()
        self.completer().popup().setCurrentIndex(index)

    def previous_completion(self):
        row = self.completer().currentRow()
        numRows = self.completer().completionCount()

        # if wrapping
        if not self.completer().setCurrentRow(row - 1):
            self.completer().setCurrentRow(numRows - 1)
        # if initializing
        if self.completer().popup().currentIndex().row() == -1:
            self.completer().setCurrentRow(numRows - 1)

        index = self.completer().currentIndex()
        self.completer().popup().setCurrentIndex(index)

    def event(self, event, *args, **kwargs):
        # tab
        if (event.type() == QEvent.KeyPress) and (event.key() == Qt.Key_Tab):
            if self.text() == '':
                self.completer().complete()
            else:
                self.next_completion()
            return True

        # shift tab
        if (event.type() == QEvent.KeyPress) and (event.key() == 16777218):
            self.previous_completion()
            return True

        return AbstractStringInputWidget.event(self, event, *args, **kwargs)

    """ PROPERTIES """
    @property
    def display_item_colors(self):
        return self._display_item_colors

    @display_item_colors.setter
    def display_item_colors(self, display_item_colors):
        self._display_item_colors = display_item_colors
        self.model().display_item_colors = display_item_colors

    @property
    def dynamic_update(self):
        return self._dynamic_update

    @dynamic_update.setter
    def dynamic_update(self, dynamic_update):
        self._dynamic_update = dynamic_update

    @property
    def filter_results(self):
        return self._filter_results

    @filter_results.setter
    def filter_results(self, filter_results):
        self._filter_results = filter_results

    def itemList(self):
        return self._item_list

    def setItemList(self, item_list):
        # if self.previous_text == '':
        #     item_list.insert(0, '')
        self._item_list = item_list

    @property
    def previous_text(self):
        return self._previous_text

    @previous_text.setter
    def previous_text(self, previous_text):
        self._previous_text = previous_text

    def model(self):
        return self._model

    def setModel(self, _model):
        self._model = _model


class CustomModelCompleter(QCompleter):
    def __init__(self, parent=None):
        super(CustomModelCompleter, self).__init__(parent)
        popup = CompleterPopup()
        self.setPopup(popup)

    # def activated(self, text):
    #     print("activated === ", text)
    #     #return QCompleter.activated(self, text)
    #
    # def splitPath(self, path):
    #     print("splitPath === ", path)
    #     return QCompleter.splitPath(self, 'yolo')


class CustomModel(QAbstractListModel):
    """
    The main item list expects two indexes
        0: Display/Edit Role
        1: Decoration Role (R, G, B, A)
    """
    def __init__(self, parent=None, item_list=[['Display Role', (64, 64, 128, 255)]]):
        super(CustomModel, self).__init__(parent)
        self._display_item_colors = False
        self.item_list = item_list

    def rowCount(self, parent):
        return len(self.item_list)

    def data(self, index, role):
        if role in (Qt.DisplayRole, Qt.EditRole):
            try:
                return self.item_list[index.row()][0]
            except IndexError:
                return None

        elif role == Qt.DecorationRole:
            # preflight
            if not self.display_item_colors: return

            # get display color
            try:
                color = QColor(*self.item_list[index.row()][1])
            except IndexError:
                color = QColor(*iColor["rgba_background_00"])

            # create pixmap/icon
            pixmap = QPixmap(int(getFontSize(QApplication) * 2), int(getFontSize(QApplication) * 0.5))
            pixmap.fill(color)
            icon = QIcon(pixmap)
            return icon

    @property
    def item_list(self):
        return self._item_list

    @item_list.setter
    def item_list(self, item_list):
        self._item_list = item_list

    @property
    def display_item_colors(self):
        return self._display_item_colors

    @display_item_colors.setter
    def display_item_colors(self, display_item_colors):
        self._display_item_colors = display_item_colors


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication, QWidget, QVBoxLayout
    from qtpy.QtGui import QCursor

    app = QApplication(sys.argv)
    def userFinishedEditing(widget, value):
        print('---- FINISH EVENT ----')
        print(widget, value)

        #qApp.processEvents()
        QApplication.instance().processEvents()
        # widget.setText('')

    def getItems():
        print('getting items??')
        items = [['a', (255, 0, 0, 255)], ['b'], ['c'], ['aa'], ['bb'], ['cc'], ['b1'], ['c1'], ['aaa'], ['bbb'], ['ccc']]
        return items


    w = QWidget()
    l = QVBoxLayout(w)
    # list_widget = AbstractListInputWidget()
    # list_widget.setCleanItemsFunction(getItems)
    list_widget = AbstractListInputWidget(item_list=[
        ['a', (255, 0, 0, 255)], ['b'], ['c'], ['aa'], ['bb'], ['cc'], ['b1'], ['c1'], ['aaa'], ['bbb'], ['ccc']]
    )
    list_widget.setUserFinishedEditingEvent(userFinishedEditing)
    #list_widget.filter_results = False
    list_widget.display_item_colors = True
    e = CompleterPopup()
    l.addWidget(list_widget)
    l.addWidget(e)
    e.setModel(list_widget.proxy_model)

    # item_list = ['a', 'b', 'c', 'aa', 'bb', 'cc']
    # w=QListView()
    # w.setStyleSheet("""
    #     QListView::item:selected{background-color: rgba(255,0,0,255);}
    # """)
    # model = CustomModel(item_list=item_list)
    # w.setModel(model)
    w.show()
    w.move(QCursor.pos())
    sys.exit(app.exec_())
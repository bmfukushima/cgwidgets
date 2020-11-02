"""
TODO
    Move this into custom LineEdit with model/completer.  Similair to the
    AbstractFileBrowser currently located in KatanaBebop
"""
from qtpy.QtWidgets import (
    QComboBox, QLineEdit, QCompleter, QSizePolicy, QVBoxLayout
)

from qtpy.QtGui import(
    QStandardItem, QStandardItemModel, QPixmap, QIcon, QColor
)
from qtpy.QtCore import (
    QEvent, Qt, QSortFilterProxyModel
)


from qtpy.QtCore import (
    QAbstractListModel, Qt, QRegExp, QSortFilterProxyModel)
from qtpy.QtWidgets import (
    QLineEdit, QCompleter, QListView, QStyledItemDelegate, QApplication)

from cgwidgets.widgets.AbstractWidgets import AbstractStringInputWidget
from cgwidgets.utils import getBottomLeftPos, getFontSize
from cgwidgets.settings.colors import iColor
from cgwidgets.views import CompleterPopup


class AbstractComboListInputWidget(QComboBox):
    """
    A custom QComboBox with a completer / model.  This is
    designed to be an abstract class that will be inherited by the
    the GSV and Node ComboBoxes

    Attributes:
        exists (bool) flag used to determine whether or not the popup menu
            for the menu change should register or not (specific to copy/paste
            of a node.

            In plain english... this flag is toggled to hide the Warning PopUp Box
            from displaying to the user in some events.
        item_list (list): string list of all of the items in the list.  Updating this
            will auto update the default settings for blank setups
        previous_text (str): the previous items text.  This is stored for cancel events
            and allowing the user to return to the previous item after cancelling.
    """
    TYPE = 'list'
    def __init__(self, parent=None):
        super(AbstractComboListInputWidget, self).__init__(parent)
        self.main_widget = self.parent()
        self.previous_text = ''
        self.setExistsFlag(True)

        # setup line edit
        #self.line_edit = QLineEdit("Select & Focus", self)
        self.line_edit = QLineEdit(self)
        self.line_edit.editingFinished.connect(self.userFinishedEditing)
        self.setLineEdit(self.line_edit)

        self.setEditable(True)

        # setup completer
        self.completer = QCompleter(self)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setPopup(self.view())
        self.setCompleter(self.completer)
        self.pFilterModel = QSortFilterProxyModel(self)

        # set size policy ( this will ignore the weird resizing effects)
        size_policy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self.setSizePolicy(size_policy)

        # initialize model...
        model = QStandardItemModel()
        self.setModel(model)
        self.setModelColumn(0)

    def populate(self, item_list):
        """
        Creates all of the items from the item list and
        appends them to the model.

        item_list (list): list of strings to be displayed to the user
            this should be set with the setCleanItemsFunction.
        """
        self.setItemList(item_list)
        for i, item_name in enumerate(self.getItemList()):
            item = QStandardItem(item_name)
            self.model().setItem(i, 0, item)
            self.setExistsFlag(False)

    def update(self):
        """
        Updates the model items with all of the graph state variables.

        This is very similar to the populate call, except that with this, it
        will remove all of the items except for the current one.  Which
        will ensure that an indexChanged event is not registered thus
        updating the UI.
        """
        self.setExistsFlag(False)

        self.model().clear()
        self.populate(self.getCleanItems())
        self.setCurrentIndexToText(self.previous_text)

        self.setExistsFlag(True)

    def setModel(self, model):
        # somehow this super makes the node type not resize...
        super(AbstractListInputWidget, self).setModel(model)
        self.pFilterModel.setSourceModel(model)
        self.completer.setModel(self.pFilterModel)

    def setModelColumn(self, column):
        self.completer.setCompletionColumn(column)
        self.pFilterModel.setFilterKeyColumn(column)
        super(AbstractListInputWidget, self).setModelColumn(column)

    def view(self):
        return self.completer.popup()

    """ UTILS """
    def next_completion(self):
        row = self.completer.currentRow()

        # if does not exist reset
        if not self.completer.setCurrentRow(row + 1):
            self.completer.setCurrentRow(0)

        # if initializing
        if self.completer.popup().currentIndex().row() == -1:
            self.completer.setCurrentRow(0)

        index = self.completer.currentIndex()
        self.completer.popup().setCurrentIndex(index)

    def previous_completion(self):
        row = self.completer.currentRow()
        numRows = self.completer.completionCount()

        # if wrapping
        if not self.completer.setCurrentRow(row - 1):
            self.completer.setCurrentRow(numRows - 1)
        # if initializing
        if self.completer.popup().currentIndex().row() == -1:
            self.completer.setCurrentRow(numRows - 1)

        index = self.completer.currentIndex()
        self.completer.popup().setCurrentIndex(index)

    def setCurrentIndexToText(self, text):
        """
        Sets the current index to the text provided.  If no
        match can be found, this will default back to the
        first index.

        If no first index... create '' ?
        """
        self.setExistsFlag(False)

        # get all matches
        items = self.model().findItems(text, Qt.MatchExactly)

        # set to index of match
        if len(items) > 0:
            index = self.model().indexFromItem(items[0]).row()
            self.setCurrentIndex(index)
        else:
            self.setCurrentIndex(0)
        self.previous_text = self.currentText()
        self.setExistsFlag(True)

    def isUserInputValid(self):
        """
        Determines if the new user input is currently
        in the model.

        Returns True if this is an existing item, Returns
        false if it is not.
        """
        items = self.model().findItems(self.currentText(), Qt.MatchExactly)
        if len(items) > 0:
            return True
        else:
            return False

    def setupStyleSheet(self):
        width = self.width()
        dropdown_width = int(width * 0.35)
        style_sheet_args = iColor.style_sheet_args
        style_sheet_args['width'] = dropdown_width
        # QComboBox {{
        #     border: None;
        #     background-color: rgba{rgba_gray_0}
        # }}
        style_sheet = """
            QComboBox{{
                border: None;
                background-color: rgba{rgba_gray_0};
                color: rgba{rgba_text};
            }}
            QComboBox::drop-down {{
                width: {width}px;
            }}
            QLineEdit{{
                border: None;
                background-color: rgba{rgba_gray_0};
                color: rgba{rgba_text};
            }}
            QListView{{
                border: None;
                background-color: rgba{rgba_gray_0};
                color: rgba{rgba_text};
            }}
            QListView::item:hover{{
                background-color: rgba(255,0,0,255);
            }}
        """.format(**style_sheet_args)

        self.completer.popup().setStyleSheet("""
            QListView{{
                border: None;
                background-color: rgba{rgba_gray_0};
                color: rgba{rgba_text};
            }}
            QListView::item:hover{{
                background-color: rgba(255,0,0,255);
            }}
        """.format(**style_sheet_args))

        self.setStyleSheet(style_sheet)

    """ API """
    def __selectionChangedEmit(self):
        pass

    def setSelectionChangedEmitEvent(self, method):
        """
        sets the method for the selection changed emit call
        this will be called everytime the user hits enter/return
        inside of the line edits as a way of sending an emit
        signal from the current text changed (finalized) before
        input changed event...
        """
        self.__selectionChangedEmit = method

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

    """ EVENTS """
    def userFinishedEditing(self):
        is_input_valid = self.isUserInputValid()
        if is_input_valid:
            self.__selectionChangedEmit()
            self.previous_text = self.currentText()
            #self.userFinishedEditingEvent(self.currentText())
        else:
            self.setCurrentIndexToText(self.previous_text)

    def resizeEvent(self, event):
        self.setupStyleSheet()
        return QComboBox.resizeEvent(self, event)

    def event(self, event, *args, **kwargs):
        """
        Registering key presses in here as for some reason
        they don't work in the keyPressEvent method...
        """
        if event.type() == QEvent.KeyPress:
            # tab
            if event.key() == Qt.Key_Tab:
                self.next_completion()
                return True

            # shift tab
            elif event.key() == Qt.Key_Tab + 1:
                self.previous_completion()
                return True

            # enter pressed
            elif event.key() in [
                Qt.Key_Return,
                Qt.Key_Enter,
                Qt.Key_Down
            ]:
                self.__selectionChangedEmit()

        elif event.type() == QEvent.MouseButtonRelease:
            self.completer.setPopup(self.view())

        return QComboBox.event(self, event, *args, **kwargs)

    """ PROPERTIES """
    def getExistsFlag(self):
        return self._exists

    def setExistsFlag(self, exists):
        self._exists = exists

    def getItemList(self):
        return self._item_list

    def setItemList(self, item_list):
        if self.previous_text == '':
            item_list.insert(0, '')
        self._item_list = item_list

    @property
    def previous_text(self):
        return self._previous_text

    @previous_text.setter
    def previous_text(self, previous_text):
        self._previous_text = previous_text


class AbstractListInputWidget(AbstractStringInputWidget):
    """
    TODO:
        *   as soon as you type it breaks?
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

    def __init__(self, parent=None, item_list=[]):
        super(AbstractListInputWidget, self).__init__(parent)
        # setup default attrs
        self._item_list = []
        self._previous_text = ''
        self._dynamic_update = False
        self._filter_results = True
        self._display_item_colors = False

        # setup custom completer
        self.setupCustomModelCompleter(item_list)

        # setup style
        self.updateStyleSheet()

        # setup signals
        self.textChanged.connect(self.filterCompletionResults)

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

    """ Style Sheet"""
    def updateStyleSheet(self):
        style_sheet_args = iColor.style_sheet_args
        style_sheet_args.update({
            'type': type(self).__name__
        })

        style_sheet = """
        {type}{{
            border:None;
            background-color: rgba{rgba_gray_0};
            selection-background-color: rgba{rgba_selected};
            color: rgba{rgba_text}
        }}

        """.format(**style_sheet_args)

        self.setStyleSheet(style_sheet)

    """ COMPLETER """
    def _updateModel(self, item_list=None):
        # get item list
        if not item_list:
            item_list = self.getCleanItems()

        # completer = CustomModelCompleter()
        # self.setCompleter(completer)
        # update model items
        self._model = CustomModel(item_list=item_list)
        self._model.display_item_colors = self.display_item_colors
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self._model)

        # set models
        self.completer().setModel(self.proxy_model)

        # set item for popup
        # this makes it so that the stylesheet can be attached...
        # https://forum.qt.io/topic/26703/solved-stylize-using-css-and-editable-qcombobox-s-completions-list-view/7
        delegate = QStyledItemDelegate()
        self.completer().popup().setItemDelegate(delegate)

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
        self.proxy_model = QSortFilterProxyModel()
        self._updateModel(item_list)

    def filterCompletionResults(self):
        """
        Filter the current proxy model based off of the text in the input string
        """
        # preflight
        if not self.filter_results: return

        # filter results
        if self.text() != '':
            self.completer().setCompletionMode(QCompleter.PopupCompletion)

        else:
            self.completer().setCompletionMode(QCompleter.UnfilteredPopupCompletion)

    """ EVENTS """
    def mouseReleaseEvent(self, event, *args, **kwargs):
        # update model (if enabled)
        if self.dynamic_update:
            self._updateModel()

        # update the current proxy model based off the current text
        self.filterCompletionResults()

        # show completer
        self.completer().complete()

        return QLineEdit.mouseReleaseEvent(self, event, *args, **kwargs)

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
        if (event.type() == QEvent.KeyPress) and (event.key() == Qt.Key_Tab):
            if self.text() == '':
                self.completer().complete()
            else:
                self.next_completion()
            return True

        if (event.type() == QEvent.KeyPress) and (event.key() == 16777218):
            self.previous_completion()
            return True

        return AbstractStringInputWidget.event(self, event, *args, **kwargs)

    """ PROPERTIES """
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

    @property
    def display_item_colors(self):
        return self._display_item_colors

    @display_item_colors.setter
    def display_item_colors(self, display_item_colors):
        self._display_item_colors = display_item_colors
        self.model().display_item_colors = display_item_colors

    def getItemList(self):
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
    #     return QCompleter.activated(self, text)
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
                color = QColor(*iColor["rgba_gray_0"])

            # create pixmap/icon
            pixmap = QPixmap(getFontSize(QApplication) * 2, getFontSize(QApplication) * 0.5)
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
    w = QWidget()
    l = QVBoxLayout(w)
    r = AbstractListInputWidget(item_list=[['a', (255,0,0, 255)], ['b'], ['c'], ['aa'], ['bb'], ['cc']])
    r.display_item_colors = True
    e = CompleterPopup()
    l.addWidget(r)
    l.addWidget(e)
    e.setModel(r.proxy_model)

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
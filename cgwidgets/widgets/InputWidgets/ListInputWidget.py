from qtpy.QtWidgets import (
    QComboBox, QLineEdit, QCompleter, QSizePolicy, QVBoxLayout
)

from qtpy.QtGui import(
    QStandardItem, QStandardItemModel
)
from qtpy.QtCore import (
    QEvent, Qt, QSortFilterProxyModel
)


class ListInputWidget(QComboBox):
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
        super(ListInputWidget, self).__init__(parent)
        self.main_widget = self.parent()
        self.previous_text = ''
        self.setExistsFlag(True)

        # setup line edit
        self.line_edit = QLineEdit("Select & Focus", self)
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
        super(ListInputWidget, self).setModel(model)
        self.pFilterModel.setSourceModel(model)
        self.completer.setModel(self.pFilterModel)

    def setModelColumn(self, column):
        self.completer.setCompletionColumn(column)
        self.pFilterModel.setFilterKeyColumn(column)
        super(ListInputWidget, self).setModelColumn(column)

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
        else:
            self.setCurrentIndexToText(self.previous_text)

    def resizeEvent(self, event):
        width = self.width()
        dropdown_width = int(width * 0.35)
        style_sheet = """
        QComboBox {
            border: 1px solid;
            border-color: rgba(0,0,0,0);
            }
            QComboBox::drop-down {
                width: %spx;
            }
        """ % (dropdown_width)
        self.setStyleSheet(style_sheet)
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


from qtpy.QtCore import QAbstractListModel, Qt, QRegExp
from qtpy.QtWidgets import QLineEdit, QCompleter, QListView
from qtpy.QtGui import QStandardItem, QStandardItemModel

from cgwidgets.settings.colors import iColor
from cgwidgets.utils import getBottomLeftPos, installCompleterPopup


class LineEdit(QLineEdit):
    """
    Signals:
    QLineEdit
        QCompleter
            | -- QSortFilterProxyModel --> QAbstractListModel (Custom Model)
            | -- Popup
                    | -- QListView (CompleterPopup)


    """
    def __init__(self, parent=None, item_list=[]):
        super(LineEdit, self).__init__(parent)
        # setup custom completer
        self.setupCustomModelCompleter(item_list)

        # setup style
        self.updateStyleSheet()

        # setup signals
        self.textChanged.connect(self.filterCompletionResults)

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
    def setupCustomModelCompleter(self, item_list):
        """
        Creates a new completely custom completer

        Args:
            item_list (list): of strings to be the list of things
                that is displayed to the user
        """
        # create completer/models
        completer = CustomModelCompleter()
        self.source_model = CustomModel(item_list=item_list)
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.source_model)

        # set models
        completer.setModel(self.proxy_model)
        completer.popup().setModel(self.proxy_model)

        # set item for popup
        # this makes it so that the stylesheet can be attached...
        # https://forum.qt.io/topic/26703/solved-stylize-using-css-and-editable-qcombobox-s-completions-list-view/7
        delegate = QStyledItemDelegate()
        completer.popup().setItemDelegate(delegate)

        # set completer
        installCompleterPopup(completer)
        self.setCompleter(completer)

    def filterCompletionResults(self):
        """
        Filter the current proxy model based off of the text in the input string
        """
        pattern = QRegExp(
            str(self.text()),
            Qt.CaseInsensitive,
            QRegExp.FixedString
        )
        self.proxy_model.setFilterRegExp(pattern)

    def mouseReleaseEvent(self, event):
        # update the current proxy model based off the current text
        self.filterCompletionResults()

        # show the pop completer
        view = self.completer().popup()
        view.show()
        pos = getBottomLeftPos(self)
        view.move(pos)

        #delegate = QStyledItemDelegate()
        #view.setItemDelegate(delegate)
        # return
        return QLineEdit.mouseReleaseEvent(self, event)


# class CompleterPopup(QListView):
#     def __init__(self, parent=None):
#         super(CompleterPopup, self).__init__(parent)
#         style_sheet_args = iColor.style_sheet_args
#
#         style_sheet = """
#         CompleterPopup{{
#             border: 1px solid rgba{rgba_outline};
#             background-color: rgba{rgba_gray_0};
#             color: rgba{rgba_text};
#         }}
#         CompleterPopup::item:selected{{
#             color: rgba{rgba_hover};
#             background-color: rgba{rgba_gray_2};
#         }}
#         CompleterPopup::item:hover{{color: rgba{rgba_hover}}}
#         CompleterPopup::item{{
#             border: None ;
#             background-color: rgba{rgba_gray_0};
#             color: rgba{rgba_text};
#         }}
#
#         """.format(**style_sheet_args)
#
#         self.setStyleSheet(style_sheet)


class CustomModelCompleter(QCompleter):
    def __init__(self, parent=None):
        super(CustomModelCompleter, self).__init__(parent)

        #popup = CompleterPopup()
        #self.setPopup(popup)


class CustomModel(QAbstractListModel):
    def __init__(self, parent=None, item_list=[]):
        super(CustomModel, self).__init__(parent)

        self.item_list = item_list

    def rowCount(self, parent):
        return len(self.item_list)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # displays this when the custom view is shown
            return self.item_list[index.row()]
        elif role == Qt.EditRole:
            # returns this when an item is selected
            return self.item_list[index.row()]

    @property
    def item_list(self):
        return self._item_list

    @item_list.setter
    def item_list(self, item_list):
        self._item_list = item_list


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication, QListView, QWidget, QLabel, QStyledItemDelegate
    from qtpy.QtGui import QCursor

    app = QApplication(sys.argv)
    w = QWidget()
    l = QVBoxLayout(w)
    r = LineEdit(item_list=['a', 'b', 'c', 'aa', 'bb', 'cc'])
    #e = CompleterPopup()
    l.addWidget(r)
    #l.addWidget(e)
    #e.setModel(r.proxy_model)

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
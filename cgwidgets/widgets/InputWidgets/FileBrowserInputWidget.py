import sys
import os

from qtpy.QtWidgets import (
    QLineEdit, QFileSystemModel, QApplication, QCompleter, QListView, QStyledItemDelegate)
from qtpy.QtCore import Qt, QEvent, QDir

from cgwidgets.widgets import AbstractStringInputWidget
from cgwidgets.utils import installCompleterPopup

class AbstractFileBrowser(AbstractStringInputWidget):
    def __init__(self, parent=None):
        super(AbstractFileBrowser, self).__init__(parent=parent)

        # setup model
        self.model = QFileSystemModel()
        self.model.setRootPath('/home/')
        filters = self.model.filter()
        self.model.setFilter(filters | QDir.Hidden)

        # setup completer
        self.completer = QCompleter(self.model, self)

        installCompleterPopup(self.completer)

        self.setCompleter(self.completer)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)

        self.autoCompleteList = []

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

    def checkDirectory(self):
        directory = str(self.text())
        if os.path.isdir(directory):
            self.model.setRootPath(str(self.text()))

    def event(self, event, *args, **kwargs):
        if (event.type() == QEvent.KeyPress) and (event.key() == Qt.Key_Tab):
            self.next_completion()
            return True

        if (event.type() == QEvent.KeyPress) and (event.key() == 16777218):
            self.previous_completion()
            return True

        # I think this is the / key... lol
        if (event.type() == QEvent.KeyRelease) and event.key() == 47:
            self.checkDirectory()
            self.completer.popup().show()

        return QLineEdit.event(self, event, *args, **kwargs)


if __name__ == '__main__':
    from qtpy.QtGui import QCursor
    app = QApplication(sys.argv)
    widget = AbstractFileBrowser()
    widget.show()
    widget.move(QCursor.pos())
    sys.exit(app.exec_())
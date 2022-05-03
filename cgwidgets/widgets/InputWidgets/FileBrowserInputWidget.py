import sys
import os

from qtpy.QtWidgets import (
    QLineEdit, QFileSystemModel, QApplication, QCompleter, QListView, QStyledItemDelegate)
from qtpy.QtCore import Qt, QEvent, QDir

from cgwidgets.widgets import AbstractListInputWidget
from cgwidgets.utils import installCompleterPopup, getDefaultSavePath

class FileBrowserInputWidget(AbstractListInputWidget):
    def __init__(self, parent=None):
        super(FileBrowserInputWidget, self).__init__(parent=parent)

        # setup model
        self.model = QFileSystemModel()
        import os
        self.model.setRootPath(getDefaultSavePath())
        filters = self.model.filter()
        self.model.setFilter(filters | QDir.Hidden)

        # setup completer
        completer = QCompleter(self.model, self)
        self.setCompleter(completer)
        installCompleterPopup(completer)

        self.setCompleter(completer)
        completer.setCaseSensitivity(Qt.CaseInsensitive)

        self.autoCompleteList = []

    def checkDirectory(self):
        directory = str(self.text())
        if os.path.isdir(directory):
            self.model.setRootPath(str(self.text()))

    def event(self, event, *args, **kwargs):
        # I think this is the / key... lol
        if (event.type() == QEvent.KeyRelease) and event.key() == 47:
            self.checkDirectory()
            #self.completer().popup().show()
            self.completer().complete()

        return AbstractListInputWidget.event(self, event, *args, **kwargs)


if __name__ == '__main__':
    from qtpy.QtGui import QCursor
    app = QApplication(sys.argv)
    widget = FileBrowserInputWidget()
    widget.show()
    widget.move(QCursor.pos())
    sys.exit(app.exec_())
import os
import sys

from qtpy.QtWidgets import QApplication

from cgwidgets.widgets import LibraryWidget

if __name__ == '__main__':

    app = QApplication(sys.argv)
    os.environ['LIBRARY_DIR'] = '/media/ssd01/library/library:/media/ssd01/library/library'
    main_widget = LibraryWidget()
    main_widget.show()
    sys.exit(app.exec_())

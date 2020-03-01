import sys
import os

from qtpy.QtWidgets import *

from . import LibraryWidget
from . import ColorWidget

''' UNIT TESTS '''
app = QApplication(sys.argv)

# Library Widget
os.environ['LIBRARY_DIR'] = '/media/ssd01/library/library:/media/ssd01/library/library'
library = LibraryWidget()
library.show()

# Color Widget
color_widget = ColorWidget()
color_widget.show()
sys.exit(app.exec_())

    



    

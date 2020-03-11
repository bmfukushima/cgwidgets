import sys
import os

os.environ['QT_API'] = "pyside2"


from qtpy.QtWidgets import *

from . import LibraryWidget
from . import ColorWidget
from . import LadderWidget

'''
pyqt5
pyqt4
pyside
pyside2
'''
#print(os.environ['QT_API'])
''' UNIT TESTS '''
app = QApplication(sys.argv)

# Library Widget
os.environ['LIBRARY_DIR'] = '/media/ssd01/library/library:/media/ssd01/library/library'
library = LibraryWidget()
library.show()
#library.close()

# Color Widget
color_widget = ColorWidget()
color_widget.show()
#color_widget.close()
sys.exit(app.exec_())

    



    
